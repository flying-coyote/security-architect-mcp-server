#!/usr/bin/env python3
"""
Security Architect MCP Server - Main Entry Point

This MCP server helps cybersecurity architects filter 80+ security data platforms
to 3-5 personalized finalists using the decision framework from
"Modern Data Stack for Cybersecurity" book.

Phase 1 Week 3-8: Tier 1 filtering with real vendor database.
"""

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Prompt, PromptMessage, Resource, TextContent, Tool

from src.models import BudgetRange, DataSovereignty, TeamSize, VendorCategory, VendorTolerance
from src.tools.filter_vendors import apply_tier1_filters
from src.tools.score_vendors import score_vendors_tier2
from src.utils.database_loader import load_default_database


# Initialize MCP server
app = Server("security-architect-mcp-server")

# Load vendor database at startup
VENDOR_DB = load_default_database()


# ============================================================================
# RESOURCES - Data exposed to Claude
# ============================================================================

async def handle_list_resources() -> list[Resource]:
    """List available resources (data Claude can access)."""
    return [
        Resource(
            uri="vendor://database/stats",
            name="Vendor Database Statistics",
            mimeType="application/json",
            description="Current statistics about the vendor database (count, categories, last updated)"
        )
    ]


async def handle_read_resource(uri: str) -> str:
    """Read resource content by URI."""
    if uri == "vendor://database/stats":
        # Return real database statistics
        categories = list(set(v.category.value for v in VENDOR_DB.vendors))
        stats = {
            "total_vendors": VENDOR_DB.total_vendors,
            "categories": sorted(categories),
            "last_updated": VENDOR_DB.last_full_update.isoformat(),
            "update_cadence": VENDOR_DB.update_cadence,
            "status": "Phase 1 Week 3-8: Tier 1 Filtering Active"
        }
        return json.dumps(stats, indent=2)

    raise ValueError(f"Unknown resource URI: {uri}")


# Register handlers
app.list_resources()(handle_list_resources)
app.read_resource()(handle_read_resource)


# ============================================================================
# TOOLS - Functions Claude can call
# ============================================================================

async def handle_list_tools() -> list[Tool]:
    """List available tools (functions Claude can call)."""
    return [
        Tool(
            name="list_vendors",
            description="List all vendors currently in the database. Returns basic vendor information including name, category, and description.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional: Filter vendors by category (e.g., 'SIEM', 'Query Engine', 'Data Lakehouse', 'Data Virtualization')",
                    }
                },
            }
        ),
        Tool(
            name="filter_vendors_tier1",
            description="""Apply Tier 1 mandatory filters to vendor database (Chapter 3 decision framework).

            Tier 1 filters are MANDATORY - vendors missing these requirements are immediately eliminated.
            Filters available:
            - team_size: Team capacity (lean, standard, large)
            - budget: Annual budget range (<500K, 500K-2M, 2M-10M, 10M+)
            - data_sovereignty: Deployment requirement (cloud-first, hybrid, on-prem-only, multi-region)
            - vendor_tolerance: OSS vs commercial (oss-first, oss-with-support, commercial-only)
            - tier_1_requirements: Custom mandatory capabilities (e.g., {"sql_interface": true})

            Returns viable vendors and elimination reasons for each filtered vendor.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_size": {
                        "type": "string",
                        "enum": ["lean", "standard", "large"],
                        "description": "Team capacity: lean (1-2 engineers), standard (3-5), large (6+)"
                    },
                    "budget": {
                        "type": "string",
                        "enum": ["<500K", "500K-2M", "2M-10M", "10M+"],
                        "description": "Annual budget range"
                    },
                    "data_sovereignty": {
                        "type": "string",
                        "enum": ["cloud-first", "hybrid", "on-prem-only", "multi-region"],
                        "description": "Deployment/compliance requirement"
                    },
                    "vendor_tolerance": {
                        "type": "string",
                        "enum": ["oss-first", "oss-with-support", "commercial-only"],
                        "description": "Open source vs commercial preference"
                    },
                    "tier_1_requirements": {
                        "type": "object",
                        "description": "Custom mandatory requirements (e.g., {\"sql_interface\": true, \"streaming_query\": false})",
                        "additionalProperties": {"type": "boolean"}
                    }
                },
            }
        ),
        Tool(
            name="score_vendors_tier2",
            description="""Score vendors on Tier 2 preferred capabilities (Chapter 3 decision framework).

            Tier 2 preferences are WEIGHTED (1-3) - vendors scored on how well they match preferences:
            - Weight 3: Strongly preferred (critical for success)
            - Weight 2: Preferred (important but not critical)
            - Weight 1: Nice-to-have (marginal benefit)

            Common preferences:
            - open_table_format, sql_interface, streaming_query, cloud_native
            - multi_cloud, managed_service_available, siem_integration
            - ml_analytics, api_extensibility, ocsf_support

            Pass array of vendor IDs from filter_vendors_tier1 output.
            Returns ranked vendors with scores, percentages, and breakdowns.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "vendor_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of vendor IDs to score (from filter_vendors_tier1 output)"
                    },
                    "preferences": {
                        "type": "object",
                        "description": "Preferences with weights 1-3 (e.g., {\"open_table_format\": 3, \"streaming_query\": 2})",
                        "additionalProperties": {"type": "integer", "minimum": 1, "maximum": 3}
                    }
                },
                "required": ["vendor_ids", "preferences"]
            }
        )
    ]


async def handle_call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute a tool by name with given arguments."""

    if name == "list_vendors":
        category_str = arguments.get("category")

        # Get all vendors from database
        vendors_list = VENDOR_DB.vendors

        # Filter by category if specified
        if category_str:
            try:
                category = VendorCategory(category_str)
                vendors_list = VENDOR_DB.get_by_category(category)
            except ValueError:
                # Invalid category, return error
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Invalid category: {category_str}",
                        "valid_categories": [c.value for c in VendorCategory]
                    }, indent=2)
                )]

        # Convert to serializable format
        vendors_data = [
            {
                "id": v.id,
                "name": v.name,
                "category": v.category.value,
                "description": v.description,
                "website": v.website,
                "cost_range": v.typical_annual_cost_range,
                "tags": v.tags
            }
            for v in vendors_list
        ]

        result = {
            "total": len(vendors_data),
            "category_filter": category_str,
            "vendors": vendors_data
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    elif name == "filter_vendors_tier1":
        # Parse filter parameters
        team_size_str = arguments.get("team_size")
        budget_str = arguments.get("budget")
        sovereignty_str = arguments.get("data_sovereignty")
        tolerance_str = arguments.get("vendor_tolerance")
        tier1_reqs = arguments.get("tier_1_requirements")

        # Convert string parameters to enums
        team_size = TeamSize(team_size_str) if team_size_str else None
        budget = BudgetRange(budget_str) if budget_str else None
        sovereignty = DataSovereignty(sovereignty_str) if sovereignty_str else None
        tolerance = VendorTolerance(tolerance_str) if tolerance_str else None

        # Apply filters
        filter_result = apply_tier1_filters(
            VENDOR_DB,
            team_size=team_size,
            budget=budget,
            data_sovereignty=sovereignty,
            vendor_tolerance=tolerance,
            tier_1_requirements=tier1_reqs
        )

        # Convert viable vendors to serializable format
        viable_vendors = [
            {
                "id": v.id,
                "name": v.name,
                "category": v.category.value,
                "description": v.description,
                "cost_range": v.typical_annual_cost_range,
                "team_required": v.capabilities.team_size_required.value,
                "operational_complexity": v.capabilities.operational_complexity,
                "deployment_models": [d.value for d in v.capabilities.deployment_models],
                "sql_interface": v.capabilities.sql_interface,
                "tags": v.tags
            }
            for v in filter_result.filtered_vendors
        ]

        # Build result
        result = {
            "summary": filter_result.summary(),
            "filters_applied": {
                "team_size": team_size.value if team_size else None,
                "budget": budget.value if budget else None,
                "data_sovereignty": sovereignty.value if sovereignty else None,
                "vendor_tolerance": tolerance.value if tolerance else None,
                "tier_1_requirements": tier1_reqs
            },
            "initial_count": filter_result.initial_count,
            "filtered_count": filter_result.filtered_count,
            "eliminated_count": filter_result.eliminated_count,
            "viable_vendors": viable_vendors,
            "eliminated_vendors": filter_result.eliminated_vendors
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    elif name == "score_vendors_tier2":
        # Parse scoring parameters
        vendor_ids = arguments.get("vendor_ids", [])
        preferences = arguments.get("preferences", {})

        if not vendor_ids:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "vendor_ids array is required"}, indent=2)
            )]

        if not preferences:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "preferences object is required"}, indent=2)
            )]

        # Get vendors by IDs
        vendors = [VENDOR_DB.get_by_id(vid) for vid in vendor_ids]
        vendors = [v for v in vendors if v is not None]  # Filter out None

        if not vendors:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "No valid vendors found for given IDs"}, indent=2)
            )]

        # Score vendors
        score_result = score_vendors_tier2(vendors, preferences)

        # Convert to serializable format
        scored_vendors = [
            {
                "vendor_id": sv.vendor.id,
                "vendor_name": sv.vendor.name,
                "category": sv.vendor.category.value,
                "score": sv.score,
                "max_score": sv.max_score,
                "score_percentage": round(sv.score_percentage, 1),
                "score_breakdown": sv.score_breakdown,
                "description": sv.vendor.description,
                "cost_range": sv.vendor.typical_annual_cost_range,
            }
            for sv in score_result.scored_vendors
        ]

        # Build result
        result = {
            "summary": score_result.summary(),
            "preferences": preferences,
            "vendor_count": score_result.vendor_count,
            "max_possible_score": score_result.max_possible_score,
            "scored_vendors": scored_vendors,
            "top_5": scored_vendors[:5]  # Convenience field
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    raise ValueError(f"Unknown tool: {name}")


# Register handlers
app.list_tools()(handle_list_tools)
app.call_tool()(handle_call_tool)


# ============================================================================
# PROMPTS - Pre-written templates for Claude
# ============================================================================

async def handle_list_prompts() -> list[Prompt]:
    """List available prompts (pre-written templates)."""
    return [
        Prompt(
            name="start_decision",
            description="Start the security architecture decision interview (12-step guided conversation)",
            arguments=[]
        )
    ]


async def handle_get_prompt(name: str, arguments: dict[str, str] | None = None) -> PromptMessage:
    """Get prompt content by name."""
    if name == "start_decision":
        return PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"""Welcome to the Security Architect Decision Support Tool!

This interactive assistant helps you filter {VENDOR_DB.total_vendors} security data platforms to 3-5 personalized finalists using the decision framework from "Modern Data Stack for Cybersecurity" book (Chapters 3-4).

**Current Capabilities** (Phase 1 Week 3-8):

1. **Vendor Database** ({VENDOR_DB.total_vendors} platforms):
   - Categories: {', '.join(sorted(set(v.category.value for v in VENDOR_DB.vendors)))}
   - Use resource `vendor://database/stats` for detailed statistics
   - Use tool `list_vendors` to browse all platforms (filter by category optional)

2. **Tier 1 Filtering** (Mandatory Requirements):
   - Use tool `filter_vendors_tier1` to apply organizational constraints:
     - **Team Size**: lean (1-2 engineers), standard (3-5), large (6+)
     - **Budget**: <500K, 500K-2M, 2M-10M, 10M+
     - **Data Sovereignty**: cloud-first, hybrid, on-prem-only, multi-region
     - **Vendor Tolerance**: oss-first, oss-with-support, commercial-only
     - **Custom Requirements**: sql_interface, streaming_query, etc.
   - Returns viable vendors + elimination reasons for each filtered platform

3. **Tier 2 Scoring** (Preferred Capabilities):
   - Use tool `score_vendors_tier2` to rank finalists by preference fit
   - **Weights**: 1 (nice-to-have), 2 (preferred), 3 (strongly preferred)
   - **Common Preferences**:
     - open_table_format, sql_interface, streaming_query, cloud_native
     - multi_cloud, managed_service_available, siem_integration
     - ml_analytics, api_extensibility, ocsf_support
   - Returns ranked vendors with scores, percentages, and breakdowns

**Example Workflow**:
```
# Step 1: Filter for lean team with tight budget
filter_vendors_tier1(team_size="lean", budget="<500K", tier_1_requirements={{"sql_interface": true}})

# Step 2: Score finalists on preferred capabilities
score_vendors_tier2(
  vendor_ids=["amazon-athena", "starburst"],
  preferences={{
    "open_table_format": 3,      # Strongly preferred
    "cloud_native": 2,            # Preferred
    "managed_service_available": 2
  }}
)
```

**Coming Soon**:
- 12-step decision interview (guided conversation)
- Architecture report generation (12-15 page Markdown)
- Journey persona matching (Jennifer/Marcus/Priya from book)

**How to Proceed**:
1. Ask about my team size, budget, and requirements
2. Apply Tier 1 filters to narrow down vendors
3. Review viable platforms and elimination reasons
4. Score finalists on preferred capabilities (Tier 2)
5. Review top-ranked vendors and make decision
6. (Future) Generate architecture recommendation report

Ready to start? Tell me about your organization's constraints, or ask to see all vendors first."""
            )
        )

    raise ValueError(f"Unknown prompt: {name}")


# Register handlers
app.list_prompts()(handle_list_prompts)
app.get_prompt()(handle_get_prompt)


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

async def main():
    """Run the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
