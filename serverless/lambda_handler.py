#!/usr/bin/env python3
"""
AWS Lambda Handler for Security Architect MCP Server
Implements Streamable HTTP transport for serverless deployment (2025 pattern)

Benefits:
- Scale to zero when idle (no cost when not in use)
- Pay-per-request pricing model
- Automatic scaling for concurrent requests
- No infrastructure management
"""

import json
import os
import sys
from typing import Any, Dict
import traceback
import time

# Add src to path for imports
sys.path.insert(0, '/opt/python')  # Lambda layer path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import MCP server components
from src.utils.database_loader import load_default_database
from src.tools.filter_vendors import apply_tier1_filters, apply_foundational_filters
from src.tools.score_vendors import score_vendors_tier2
from src.tools.calculate_tco import calculate_tco, compare_vendors_tco
from src.tools.code_execution import CodeExecutor, ExecutionContext, create_code_execution_tool
from src.tools.progressive_discovery import ProgressiveToolLoader, create_discovery_tool

# Initialize resources (cached between invocations for warm starts)
VENDOR_DB = None
DECISION_STATE = None
PROGRESSIVE_LOADER = None
CODE_EXECUTOR = None


def initialize_resources():
    """Initialize resources once for Lambda container reuse."""
    global VENDOR_DB, DECISION_STATE, PROGRESSIVE_LOADER, CODE_EXECUTOR

    if VENDOR_DB is None:
        print("Initializing vendor database...")
        VENDOR_DB = load_default_database()

    if DECISION_STATE is None:
        print("Loading decision state...")
        # In Lambda, this would come from S3 or DynamoDB
        DECISION_STATE = {}

    if PROGRESSIVE_LOADER is None:
        print("Initializing progressive discovery...")
        PROGRESSIVE_LOADER = ProgressiveToolLoader(VENDOR_DB)

    if CODE_EXECUTOR is None:
        print("Initializing code executor...")
        context = ExecutionContext(
            allowed_functions={
                'filter_vendors': apply_tier1_filters,
                'score_vendors': score_vendors_tier2,
                'calculate_tco': calculate_tco
            },
            vendor_database=VENDOR_DB,
            decision_state=DECISION_STATE,
            max_execution_time=25.0,  # Lambda timeout buffer
            max_memory_mb=256
        )
        CODE_EXECUTOR = CodeExecutor(context)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for MCP server requests.

    Supports Streamable HTTP transport (2025 standard) for serverless.

    Args:
        event: API Gateway event with MCP request
        context: Lambda context with runtime information

    Returns:
        API Gateway response with MCP result
    """
    start_time = time.time()

    # Initialize resources (cached for warm starts)
    initialize_resources()

    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        method = body.get('method')
        params = body.get('params', {})

        # Route to appropriate handler
        result = route_request(method, params)

        # Calculate execution metrics
        execution_time = time.time() - start_time
        remaining_time = context.get_remaining_time_in_millis() / 1000 if context else 30

        # Add Lambda metadata to response
        result['_metadata'] = {
            'execution_time': execution_time,
            'remaining_time': remaining_time,
            'memory_used_mb': get_memory_usage_mb(),
            'cold_start': execution_time > 2.0,  # Heuristic for cold start
            'request_id': context.aws_request_id if context else 'local'
        }

        # Return successful response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'X-MCP-Version': '2025-11',
                'X-MCP-Transport': 'streamable-http',
                'Access-Control-Allow-Origin': '*'  # Configure for production
            },
            'body': json.dumps(result)
        }

    except Exception as e:
        # Error response
        error_trace = traceback.format_exc()
        print(f"Error in Lambda handler: {error_trace}")

        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'X-MCP-Version': '2025-11'
            },
            'body': json.dumps({
                'error': str(e),
                'trace': error_trace if os.environ.get('DEBUG') == 'true' else None
            })
        }


def route_request(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Route MCP request to appropriate handler."""

    # Progressive discovery endpoints (2025 pattern)
    if method == 'search_tools':
        return PROGRESSIVE_LOADER.search_tools(
            query=params.get('query'),
            category=params.get('category'),
            requirements=params.get('requirements'),
            limit=params.get('limit', 10)
        )

    elif method == 'load_tool':
        tool = PROGRESSIVE_LOADER.load_tool(params.get('tool_name'))
        return tool if tool else {'error': 'Tool not found'}

    elif method == 'get_discovery_stats':
        return PROGRESSIVE_LOADER.get_discovery_stats()

    # Code execution endpoint (98.7% token reduction)
    elif method == 'execute_vendor_analysis':
        result = CODE_EXECUTOR.execute(params.get('code', ''))
        return result

    # Traditional tool endpoints (backward compatibility)
    elif method == 'list_vendors':
        from src.server import handle_call_tool
        return handle_call_tool('list_vendors', params)

    elif method == 'filter_vendors_tier1':
        from src.server import handle_call_tool
        return handle_call_tool('filter_vendors_tier1', params)

    elif method == 'score_vendors_tier2':
        from src.server import handle_call_tool
        return handle_call_tool('score_vendors_tier2', params)

    elif method == 'calculate_tco':
        vendor_id = params.get('vendor_id')
        vendor = VENDOR_DB.get_by_id(vendor_id)
        if not vendor:
            return {'error': f'Vendor not found: {vendor_id}'}

        tco = calculate_tco(
            vendor=vendor,
            data_volume_tb_day=params.get('data_volume_tb_day', 1.0),
            team_size=params.get('team_size', 'standard'),
            growth_rate=params.get('growth_rate', 0.20)
        )
        return tco.to_dict()

    # Health check
    elif method == 'health':
        return {
            'status': 'healthy',
            'vendor_count': VENDOR_DB.total_vendors if VENDOR_DB else 0,
            'progressive_discovery': True,
            'code_execution': True,
            'transport': 'streamable-http'
        }

    else:
        return {'error': f'Unknown method: {method}'}


def get_memory_usage_mb() -> int:
    """Get current memory usage in MB."""
    try:
        import resource
        usage = resource.getrusage(resource.RUSAGE_SELF)
        return int(usage.ru_maxrss / 1024)  # Convert KB to MB
    except:
        return 0


# Warm-up handler for Lambda provisioned concurrency
def warmup_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Lambda warm-up pings to keep container warm."""
    if event.get('source') == 'serverless-plugin-warmup':
        initialize_resources()
        return {'statusCode': 200, 'body': 'Warm'}
    return lambda_handler(event, context)


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        'body': json.dumps({
            'method': 'search_tools',
            'params': {
                'query': 'SIEM alternatives',
                'requirements': {'budget': '<500K'},
                'limit': 5
            }
        })
    }

    # Mock context
    class MockContext:
        aws_request_id = 'test-123'

        def get_remaining_time_in_millis(self):
            return 30000

    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))