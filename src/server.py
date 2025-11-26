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
from src.tools.filter_vendors import apply_foundational_filters, apply_tier1_filters
from src.tools.score_vendors import score_vendors_tier2
from src.tools.calculate_tco import calculate_tco, compare_vendors_tco
from src.tools.generate_poc_test_suite import generate_poc_test_suite
from src.utils.database_loader import load_default_database


# Initialize MCP server
app = Server("security-architect-mcp-server")

# Load vendor database at startup
VENDOR_DB = load_default_database()

# Load decision state at startup
import os
DECISION_STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "decision_state.json")
with open(DECISION_STATE_PATH, "r") as f:
    DECISION_STATE = json.load(f)


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
        ),
        Resource(
            uri="decision://state",
            name="Decision State History",
            mimeType="application/json",
            description="Past architecture decisions made using this MCP server for similar decision matching and learning from previous choices"
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

    elif uri == "decision://state":
        # Return decision state history
        return json.dumps(DECISION_STATE, indent=2)

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
            name="apply_foundational_filters",
            description="""Apply Phase 1 foundational architecture filters (table format, catalog, transformation, query engine, isolation pattern).

            **NEW (October 2025)**: Foundational filters establish architectural commitments BEFORE organizational constraints.
            This prevents vendor lock-in by deciding table format, catalog, transformation strategy, and query engine
            characteristics first, then filtering vendors within that architecture.

            **NEW (November 2025)**: Isolation pattern parameter guides catalog and query engine recommendations.
            Isolated platforms enable performance-first selection (0% RLS overhead). Shared platforms require
            fine-grained access control (Unity Catalog + RLS-aware query engines).

            Filters available:
            - isolation_pattern: Isolated dedicated (security VPC), shared corporate (PII+security), multi-tenant MSSP, undecided
            - table_format: Apache Iceberg, Delta Lake, Hudi, proprietary, undecided
            - catalog: Polaris, Unity Catalog, Nessie, AWS Glue, Hive Metastore, undecided
            - transformation_strategy: dbt, Spark, vendor built-in, custom Python, undecided
            - query_engine_preference: low-latency (<1s P95), high-concurrency (100+ queries), serverless, cost-optimized, flexible

            Returns viable vendors matching architecture + elimination reasons for filtered vendors.

            **Decision Flow**: Phase 1 (foundational) → Phase 2 (constraints via filter_vendors_tier1) → Phase 3 (features via score_vendors_tier2)""",
            inputSchema={
                "type": "object",
                "properties": {
                    "isolation_pattern": {
                        "type": "string",
                        "enum": ["isolated_dedicated", "shared_corporate", "multi_tenant_mssp", "undecided"],
                        "description": "Infrastructure isolation pattern (isolated_dedicated = security VPC 0% RLS overhead, shared_corporate = PII+security co-located 15-50% overhead, multi_tenant_mssp = customer tenants 5-30% overhead, undecided = no preference)"
                    },
                    "table_format": {
                        "type": "string",
                        "enum": ["iceberg", "delta_lake", "hudi", "proprietary", "undecided"],
                        "description": "Table format preference (iceberg = Netflix/Polaris, delta_lake = Databricks/Unity, hudi = Uber, proprietary = Snowflake, undecided = no preference)"
                    },
                    "catalog": {
                        "type": "string",
                        "enum": ["polaris", "unity_catalog", "nessie", "glue", "hive_metastore", "undecided"],
                        "description": "Catalog for metadata management (polaris = Iceberg-native, unity_catalog = Delta-native, nessie = OSS Git-like, glue = AWS serverless, hive_metastore = legacy)"
                    },
                    "transformation_strategy": {
                        "type": "string",
                        "enum": ["dbt", "spark", "vendor_builtin", "custom_python", "undecided"],
                        "description": "Transformation approach (dbt = SQL-based, spark = PySpark/Scala, vendor_builtin = SPL/KQL, custom_python = Pandas/Polars, undecided = no preference)"
                    },
                    "query_engine_preference": {
                        "type": "string",
                        "enum": ["low_latency", "high_concurrency", "serverless", "cost_optimized", "flexible"],
                        "description": "Query engine characteristics (low_latency = ClickHouse <1s P95, high_concurrency = Trino 100+ queries, serverless = Athena no-ops, cost_optimized = DuckDB efficiency, flexible = any SQL engine)"
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
        ),
        Tool(
            name="generate_architecture_report",
            description="""Generate comprehensive architecture recommendation report (Markdown format).

            Produces 8-12 page report with:
            - Executive summary with top recommendations
            - Organizational context (team, budget, sovereignty)
            - Decision constraints applied (Tier 1-2)
            - Vendor landscape analysis
            - Top 3-5 finalist recommendations with detailed capability analysis
            - Honest trade-off analysis (strengths + limitations)
            - Implementation considerations (POC testing, migration strategy, training)
            - Next steps with timeline

            Requires both filter_vendors_tier1 and score_vendors_tier2 results.
            Returns Markdown report ready for review.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_result": {
                        "type": "object",
                        "description": "Output from filter_vendors_tier1 tool"
                    },
                    "score_result": {
                        "type": "object",
                        "description": "Output from score_vendors_tier2 tool"
                    },
                    "architect_context": {
                        "type": "object",
                        "description": "Organization profile (team_size, budget, data_sovereignty, vendor_tolerance)",
                        "properties": {
                            "team_size": {"type": "string", "enum": ["lean", "standard", "large"]},
                            "budget": {"type": "string", "enum": ["<500K", "500K-2M", "2M-10M", "10M+"]},
                            "data_sovereignty": {"type": "string", "enum": ["cloud-first", "hybrid", "on-prem-only", "multi-region"]},
                            "vendor_tolerance": {"type": "string", "enum": ["oss-first", "oss-with-support", "commercial-only"]}
                        }
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="match_journey_persona",
            description="""Match architect's context to Chapter 4 journey persona (Jennifer/Marcus/Priya).

            Identifies which real-world case study from the book best matches your organization:
            - **Jennifer**: Cloud-native startup, 5-person team, $500K-2M, serverless architecture
            - **Marcus**: Financial services SOC, 2-person lean team, <$500K, on-prem compliance
            - **Priya**: Enterprise security architect, 8+ team, $2M+, hybrid multi-cloud

            Returns:
            - Matched persona with confidence score
            - Architecture pattern recommendation
            - Reasoning explaining why this persona matched
            - Recommended vendors from that journey

            Use this to understand relevant case studies and proven architecture patterns.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_size": {
                        "type": "string",
                        "enum": ["lean", "standard", "large"],
                        "description": "Team capacity: lean (1-2), standard (3-5), large (6+)"
                    },
                    "budget": {
                        "type": "string",
                        "enum": ["<500K", "500K-2M", "2M-10M", "10M+"],
                        "description": "Annual budget range"
                    },
                    "data_sovereignty": {
                        "type": "string",
                        "enum": ["cloud-first", "hybrid", "on-prem-only", "multi-region"],
                        "description": "Data sovereignty requirement"
                    },
                    "vendor_tolerance": {
                        "type": "string",
                        "enum": ["oss-first", "oss-with-support", "commercial-only"],
                        "description": "Vendor relationship tolerance"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="calculate_tco",
            description="""Calculate 5-year Total Cost of Ownership (TCO) for a vendor.

            Projects comprehensive TCO including:
            - Platform costs (licensing, consumption, per-GB fees)
            - Operational costs (team time based on complexity)
            - Hidden costs (egress fees, support contracts, migration)
            - Growth modeling (data volume increases over time)

            Returns:
            - Year 1 cost and 5-year total
            - Annual cost breakdown for each year
            - Cost category breakdown (platform/ops/hidden)
            - Key assumptions documented
            - Cost warnings (predictability, scaling risks)

            Use this to budget and compare vendors on true total cost, not just sticker price.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "vendor_id": {
                        "type": "string",
                        "description": "Vendor ID to analyze (e.g., 'amazon-athena', 'splunk-enterprise-security')"
                    },
                    "data_volume_tb_day": {
                        "type": "number",
                        "description": "Daily data ingestion volume in TB (default: 1.0)",
                        "default": 1.0
                    },
                    "team_size": {
                        "type": "string",
                        "enum": ["lean", "standard", "large"],
                        "description": "Team capacity for operational costs (default: standard)"
                    },
                    "growth_rate": {
                        "type": "number",
                        "description": "Annual data volume growth rate as decimal (default: 0.20 = 20%)",
                        "default": 0.20
                    },
                    "include_hidden_costs": {
                        "type": "boolean",
                        "description": "Include egress, support, migration costs (default: true)",
                        "default": True
                    }
                },
                "required": ["vendor_id"]
            }
        ),
        Tool(
            name="compare_vendors_tco",
            description="""Compare 5-year TCO across multiple vendors.

            Calculates TCO for each vendor and ranks them by total 5-year cost (lowest first).

            Returns ranked list of TCO projections with:
            - Each vendor's Year 1 and 5-year total costs
            - Cost breakdowns and assumptions
            - Warnings about cost predictability and scaling

            Use this to compare finalists on total cost, not just platform pricing.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "vendor_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of vendor IDs to compare (e.g., ['amazon-athena', 'dremio'])"
                    },
                    "data_volume_tb_day": {
                        "type": "number",
                        "description": "Daily data ingestion volume in TB (default: 1.0)",
                        "default": 1.0
                    },
                    "team_size": {
                        "type": "string",
                        "enum": ["lean", "standard", "large"],
                        "description": "Team capacity (default: standard)"
                    },
                    "growth_rate": {
                        "type": "number",
                        "description": "Annual data volume growth rate (default: 0.20)",
                        "default": 0.20
                    }
                },
                "required": ["vendor_ids"]
            }
        ),
        Tool(
            name="generate_poc_test_suite",
            description="""Generate vendor-specific proof-of-concept (POC) test plan.

            Creates comprehensive POC test suite with:
            - Test scenarios by use case (threat hunting, compliance, incident response, etc.)
            - Success criteria (measurable outcomes)
            - Infrastructure requirements (deployment, compute, storage)
            - Estimated POC duration (days)
            - Sample queries/dashboards to build
            - Evaluation rubric (scoring criteria)

            Use this to plan hands-on evaluation of finalist vendors with realistic scenarios.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "vendor_id": {
                        "type": "string",
                        "description": "Vendor ID to generate POC for (e.g., 'amazon-athena')"
                    },
                    "use_cases": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Use cases to test (e.g., ['threat_hunting', 'compliance_reporting', 'incident_response'])"
                    },
                    "data_sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Available data sources (e.g., ['cloudtrail', 'vpc_flow_logs', 'windows_events'])"
                    },
                    "team_skillset": {
                        "type": "string",
                        "enum": ["lean", "standard", "large"],
                        "description": "Team capacity (affects POC complexity and duration)"
                    }
                },
                "required": ["vendor_id"]
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

    elif name == "apply_foundational_filters":
        # Parse foundational filter parameters
        isolation_pattern = arguments.get("isolation_pattern")
        table_format = arguments.get("table_format")
        catalog = arguments.get("catalog")
        transformation_strategy = arguments.get("transformation_strategy")
        query_engine_preference = arguments.get("query_engine_preference")

        # Apply foundational filters
        filter_result = apply_foundational_filters(
            VENDOR_DB,
            table_format=table_format,
            catalog=catalog,
            transformation_strategy=transformation_strategy,
            query_engine_preference=query_engine_preference,
            isolation_pattern=isolation_pattern,
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
                "iceberg_support": v.capabilities.iceberg_support,
                "delta_lake_support": v.capabilities.delta_lake_support,
                "dbt_integration": v.capabilities.dbt_integration,
                "query_latency_p95": v.capabilities.query_latency_p95,
                "tags": v.tags
            }
            for v in filter_result.filtered_vendors
        ]

        # Build result
        result = {
            "summary": filter_result.summary(),
            "filters_applied": {
                "isolation_pattern": isolation_pattern,
                "table_format": table_format,
                "catalog": catalog,
                "transformation_strategy": transformation_strategy,
                "query_engine_preference": query_engine_preference,
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

    elif name == "generate_architecture_report":
        # Import report generator
        from src.tools.generate_report import generate_architecture_report
        from src.tools.filter_vendors import FilterResult

        # Parse arguments
        filter_data = arguments.get("filter_result")
        score_data = arguments.get("score_result")
        context = arguments.get("architect_context", {})

        # Reconstruct FilterResult if provided
        filter_result = None
        if filter_data and "filtered_vendor_ids" in filter_data:
            # Get vendors by IDs
            filtered_vendors = [
                VENDOR_DB.get_by_id(vid) for vid in filter_data["filtered_vendor_ids"]
            ]
            filtered_vendors = [v for v in filtered_vendors if v is not None]

            filter_result = FilterResult(
                initial_count=filter_data.get("initial_count", 54),
                filtered_vendors=filtered_vendors,
                eliminated_vendors=filter_data.get("eliminated_vendors", {}),
            )

        # Reconstruct ScoreResult if provided
        score_result = None
        if score_data and "scored_vendors" in score_data:
            # Get scored vendors
            vendor_ids = [sv["vendor_id"] for sv in score_data["scored_vendors"]]
            vendors = [VENDOR_DB.get_by_id(vid) for vid in vendor_ids]
            vendors = [v for v in vendors if v is not None]

            # Score them with preferences
            preferences = score_data.get("preferences", {})
            if vendors and preferences:
                score_result = score_vendors_tier2(vendors, preferences)

        # Parse architect context enums
        architect_context = {}
        if "team_size" in context:
            architect_context["team_size"] = TeamSize(context["team_size"])
        if "budget" in context:
            architect_context["budget"] = BudgetRange(context["budget"])
        if "data_sovereignty" in context:
            architect_context["data_sovereignty"] = DataSovereignty(context["data_sovereignty"])
        if "vendor_tolerance" in context:
            architect_context["vendor_tolerance"] = VendorTolerance(context["vendor_tolerance"])

        # Generate report
        report_markdown = generate_architecture_report(
            filter_result=filter_result,
            score_result=score_result,
            architect_context=architect_context,
        )

        # Return Markdown report
        return [TextContent(
            type="text",
            text=report_markdown
        )]

    elif name == "match_journey_persona":
        # Import journey matcher
        from src.tools.match_journey import match_journey_persona

        # Parse arguments
        team_size_str = arguments.get("team_size")
        budget_str = arguments.get("budget")
        sovereignty_str = arguments.get("data_sovereignty")
        tolerance_str = arguments.get("vendor_tolerance")

        # Convert to enums
        team_size = TeamSize(team_size_str) if team_size_str else None
        budget = BudgetRange(budget_str) if budget_str else None
        sovereignty = DataSovereignty(sovereignty_str) if sovereignty_str else None
        tolerance = VendorTolerance(tolerance_str) if tolerance_str else None

        # Match journey
        match = match_journey_persona(
            team_size=team_size,
            budget=budget,
            data_sovereignty=sovereignty,
            vendor_tolerance=tolerance,
        )

        # Build result
        result = {
            "persona": match.persona,
            "confidence": round(match.confidence, 1),
            "architecture_pattern": match.architecture_pattern,
            "reasoning": match.reasoning,
            "key_constraints": match.key_constraints,
            "summary": match.summary(),
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    elif name == "calculate_tco":
        # Parse arguments
        vendor_id = arguments.get("vendor_id")
        data_volume = arguments.get("data_volume_tb_day", 1.0)
        team_size_str = arguments.get("team_size", "standard")
        growth_rate = arguments.get("growth_rate", 0.20)
        include_hidden = arguments.get("include_hidden_costs", True)

        # Get vendor
        vendor = VENDOR_DB.get_by_id(vendor_id)
        if not vendor:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Vendor not found: {vendor_id}"}, indent=2)
            )]

        # Parse team size
        team_size = TeamSize(team_size_str)

        # Calculate TCO
        tco = calculate_tco(
            vendor=vendor,
            data_volume_tb_day=data_volume,
            team_size=team_size,
            growth_rate=growth_rate,
            include_hidden_costs=include_hidden,
        )

        # Return serialized result
        return [TextContent(
            type="text",
            text=json.dumps(tco.to_dict(), indent=2)
        )]

    elif name == "compare_vendors_tco":
        # Parse arguments
        vendor_ids = arguments.get("vendor_ids", [])
        data_volume = arguments.get("data_volume_tb_day", 1.0)
        team_size_str = arguments.get("team_size", "standard")
        growth_rate = arguments.get("growth_rate", 0.20)

        # Get vendors
        vendors = [VENDOR_DB.get_by_id(vid) for vid in vendor_ids]
        vendors = [v for v in vendors if v is not None]

        if not vendors:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "No valid vendors found"}, indent=2)
            )]

        # Parse team size
        team_size = TeamSize(team_size_str)

        # Compare TCO
        tco_projections = compare_vendors_tco(
            vendors=vendors,
            data_volume_tb_day=data_volume,
            team_size=team_size,
            growth_rate=growth_rate,
        )

        # Serialize results
        results = [tco.to_dict() for tco in tco_projections]

        return [TextContent(
            type="text",
            text=json.dumps({
                "comparisons": results,
                "count": len(results),
                "cheapest": results[0] if results else None,
            }, indent=2)
        )]

    elif name == "generate_poc_test_suite":
        # Parse arguments
        vendor_id = arguments.get("vendor_id")
        use_cases = arguments.get("use_cases")
        data_sources = arguments.get("data_sources")
        team_skillset_str = arguments.get("team_skillset", "standard")

        # Get vendor
        vendor = VENDOR_DB.get_by_id(vendor_id)
        if not vendor:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Vendor not found: {vendor_id}"}, indent=2)
            )]

        # Parse team size
        team_skillset = TeamSize(team_skillset_str)

        # Generate POC test suite
        poc = generate_poc_test_suite(
            vendor=vendor,
            use_cases=use_cases,
            data_sources=data_sources,
            team_skillset=team_skillset,
        )

        # Return Markdown test plan
        return [TextContent(
            type="text",
            text=poc.to_markdown()
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
        ),
        Prompt(
            name="decision_interview",
            description="Complete 12-step decision interview to filter 80+ vendors to 3-5 finalists (15-30 minutes)",
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

    elif name == "decision_interview":
        return PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"""# Security Architecture Decision Interview

Welcome to the Security Architecture Decision Framework!

I'll guide you through a systematic interview to identify the right security data platform for YOUR organization. This replaces the 40-page RFP with a personalized conversation.

**Updated Flow** (November 2025 - V3): We now start with **SIZING CONSTRAINTS FIRST** to eliminate vendors by scale, then foundational architecture decisions, then organizational constraints. This mirrors the V3 web tool question ordering.

**Time**: 15-30 minutes
**Goal**: Filter {VENDOR_DB.total_vendors} platforms → 3-5 finalists tailored to your sizing + architecture + constraints

Let's begin.

---

## Phase 0: Sizing Constraints (Questions S1-S4)

*These questions establish your data scale and growth trajectory BEFORE architectural decisions. Sizing constraints eliminate vendors that can't handle your scale or are overkill for your volume.*

---

**Question S1: Current Data Ingestion Volume**

How much security log data do you ingest daily?

*Context: This determines vendor viability by scale. DuckDB maxes at ~1 TB/day (single-process limit). Splunk economical at 10+ TB/day. AWS CloudTrail typical: 50-500 GB/day. 100 endpoints ≈ 1 GB/day baseline.*

Options (specify range or exact value):
- **0-10 GB/day** (eliminates Splunk - $100K+ minimum, overkill)
- **10-100 GB/day** (sweet spot for most vendors)
- **100 GB - 1 TB/day** (eliminates DuckDB single-process max ~500 GB/day)
- **1-10 TB/day** (requires distributed query engines, eliminates small-scale vendors)
- **10+ TB/day** (hyperscale workloads, Netflix/Uber tier)

Enter value: ___ GB/day OR ___ TB/day

---

**Question S2: Expected Data Growth Rate**

How much will your log volume increase annually?

*Context: Common drivers: cloud migration (+30-50%), M&A (+100%+), compliance expansion (+20-40%), EDR rollout (+50-100%). High growth (100%+) favors elastic/serverless architectures.*

Options:
- **0-20% annually** (stable, fixed-capacity platforms viable)
- **20-50% annually** (moderate growth, hybrid architectures needed)
- **50-100% annually** (high growth, elastic architectures preferred)
- **100-300% annually** (explosive growth, serverless/elastic REQUIRED - Athena, Databricks, Snowflake)
- **300%+ annually** (hyperscale, Netflix-tier autoscaling)

Enter value: ___% annually

---

**Question S3: Number of Data Sources**

How many unique log sources send data to your platform?

*Context: Count EDR, firewalls, cloud providers (AWS/Azure/GCP), SaaS apps, network devices, identity providers. Example: AWS (1), Okta (1), CrowdStrike (1) = 3 sources. 100+ sources may require ETL/normalization layer (Cribl, Tenzir).*

Options:
- **1-10 sources** (simple architecture, direct ingestion viable)
- **10-50 sources** (standard ETL, schema management needed)
- **50-100 sources** (consider ETL layer - Cribl, Logstash)
- **100-500 sources** (ETL/normalization REQUIRED - Cribl Stream, Tenzir)
- **500+ sources** (MSSP-scale normalization - OCSF, Cribl enterprise)

Enter value: ___ sources

---

**Question S4: Retention Requirements**

How long must logs remain queryable?

*Context: Hot retention (fast queries, expensive) vs cold archival (slow queries, cheap). Real-time detection: 1-7 days. Compliance: GDPR 90-365 days, PCI-DSS 1 year, HIPAA 6 years, finance 7 years. 2+ years requires hot/warm/cold tiering.*

Options:
- **1-30 days** (real-time detection only, simple hot tier)
- **30-90 days** (standard SOC, single tier acceptable)
- **90-365 days** (hot/warm tiering recommended - 30d hot, rest warm)
- **1-2 years** (compliance, hot/warm/cold tiering REQUIRED)
- **2-7 years** (long-term compliance, multi-tier archival - Iceberg time-travel beneficial)

Enter value: ___ days OR ___ years

---

## Phase 1: Foundational Architecture Decisions (Questions F0-F4)

*These questions establish your architectural commitments before filtering by organizational constraints. Think of these as multi-year decisions that shape your entire security data platform.*

---

**Question F0: Infrastructure Isolation Pattern** *(NEW - November 2025)*

Is your security data isolated on dedicated infrastructure (separate VPC/VNet from corporate data platforms)?

*Context: **This is THE most important architectural decision for catalog and query engine selection**. Isolation pattern determines whether you need fine-grained access control (row-level security, column masking) or can use simpler table-level RBAC. Isolated platforms achieve 15-50% faster queries by avoiding RLS overhead. Netflix, Huntress, and Okta use isolated security infrastructure.*

*Production Examples:*
- **Isolated (Netflix)**: Security logs on separate VPC from corporate data → ClickHouse + Iceberg + Polaris → 0% RLS overhead, table-level RBAC sufficient
- **Shared (Multi-tenant MSSP)**: Security logs + customer data co-located → Databricks + Unity Catalog → Row-level security essential for tenant isolation

Options:
- **Isolated dedicated infrastructure** - Security data on separate VPC/VNet (isolated from PII/financial data), security team-only access → *Table-level RBAC sufficient, 0% RLS overhead, performance-first query engine selection (ClickHouse, DuckDB, Trino)*
- **Shared corporate platform** - Security logs + PII + financial data co-located on same platform → *Fine-grained access control required (Unity Catalog + RLS + column masking), 15-50% performance overhead*
- **Multi-tenant MSSP** - Multiple customer tenants on shared infrastructure → *Row-level security essential (Customer A analysts only see Customer A logs), Unity Catalog required, 5-30% performance overhead*
- **Undecided** - I need guidance on isolation vs. shared architecture

Enter: `isolated_dedicated` | `shared_corporate` | `multi_tenant_mssp` | `undecided`

**Why F0 comes first**: Your isolation pattern determines which catalogs are viable (Polaris/Nessie for isolated, Unity Catalog for shared/MSSP) and which query engines are optimal (ClickHouse/DuckDB for isolated, Databricks SQL for shared). This decision informs F1-F4 answers.

---

**Question F1: Table Format Decision**

Which table format do you prefer for your security data lakehouse?

*Context: This is a multi-year architectural commitment. Table format affects vendor lock-in, query engine compatibility, operational complexity, and catalog choice. Netflix uses Iceberg for their security data platform. Databricks primarily uses Delta Lake.*

Options:
- **Apache Iceberg** (Netflix production-validated, strong community, Polaris catalog native, query engine flexibility)
- **Delta Lake** (Databricks native, Unity Catalog integration, strong ACID guarantees, less vendor flexibility)
- **Apache Hudi** (Uber origins, strong CDC support, less security community adoption)
- **Proprietary format** (Snowflake, vendor lock-in but simplicity)
- **Undecided** - I need guidance on table format choice

Enter: `iceberg` | `delta_lake` | `hudi` | `proprietary` | `undecided`

---

**Question F2: Catalog Decision**

Which catalog for metadata management?

*Context: Catalog choice affects governance (row-level security, column masking), RBAC, multi-engine query support, and operational complexity. Your table format choice (F1) influences catalog compatibility.*

Options:
- **Polaris** (Snowflake open source, Iceberg-native, production-ready, multi-engine)
- **Unity Catalog** (Databricks, Delta Lake native, strong governance, some Iceberg support)
- **Nessie** (OSS, Git-like versioning, flexible but emerging maturity)
- **AWS Glue** (AWS native, serverless, Athena/EMR integration, limited non-AWS support)
- **Hive Metastore** (Legacy, widely supported, operational complexity, no modern governance)
- **Undecided** - I need catalog guidance

Enter: `polaris` | `unity_catalog` | `nessie` | `glue` | `hive_metastore` | `undecided`

---

**Question F3: Transformation Strategy**

How will you transform security data?

*Context: Transformation strategy affects team skillset requirements, operational complexity, and vendor lock-in risk. dbt enables SQL-based transformations familiar to security analysts. Spark requires data engineering expertise but offers more flexibility.*

Options:
- **dbt** (SQL-based, analytics engineer friendly, strong testing framework, growing security community)
- **Spark** (PySpark/Scala, data engineering required, flexible but complex, mature ecosystem)
- **Vendor built-in** (Splunk SPL, Sentinel KQL, proprietary query languages, vendor lock-in)
- **Custom Python** (Pandas, Polars, flexible but maintenance burden, team-dependent)
- **Undecided** - I need transformation strategy guidance

Enter: `dbt` | `spark` | `vendor_builtin` | `custom_python` | `undecided`

---

**Question F4: Query Engine Characteristics (SELECT ALL THAT APPLY)**

Which query engine characteristics do you need? **MULTI-SELECT** - most architectures need multiple characteristics.

*Context: Query engine choice affects latency (dashboards, real-time detection), concurrency (many analysts querying), operational complexity, and cost. **You can select MULTIPLE characteristics** - we'll recommend architectures that handle them. ClickHouse offers low-latency for interactive dashboards. Trino handles high concurrency. Athena provides serverless simplicity.*

*Example: Real-time dashboards (<1s P95) + ad-hoc hunting (high concurrency) → ClickHouse hot tier + Trino cold tier*

Options (select all that apply):
- **Low-latency interactive queries** (ClickHouse, Pinot - <1 second P95, SOC dashboard use case, operational complexity)
- **High concurrency** (Trino, Presto - many analysts querying simultaneously, 100+ concurrent queries)
- **Serverless simplicity** (AWS Athena - no infrastructure management, pay-per-query, 2-10 second latency acceptable)
- **Cost-optimized** (DuckDB - single-process, in-memory efficiency, <50 analysts, ~1GB/s query throughput)
- **Flexible** - any SQL engine acceptable, no strong preference

Enter (comma-separated): `low_latency, high_concurrency` OR `serverless` OR `low_latency, cost_optimized` etc.

---

## Phase 2: Organizational Constraints (Questions 1-7)

*Now that you've established your architectural preferences, let's apply organizational constraints to filter vendors within that architecture.*

---

## Section 1: Team Capacity (Questions 1-3)

**Question 1**: How many data engineers or platform engineers are dedicated to your security team?

*Context: This determines operational complexity tolerance. 0-1 engineers means we'll prioritize managed services. 5+ engineers means fully composable architectures are viable.*

Options:
- 0 data engineers (security-focused team only)
- 1-2 engineers (small platform team) → **lean**
- 3-5 engineers (moderate team, hybrid architectures viable) → **standard**
- 6+ engineers (large team, fully composable stack) → **large**

---

**Question 2**: What's their primary expertise?

Options:
- Security/SOC background (strong domain knowledge, limited data platform experience)
- Data engineering background (strong platform skills, learning security)
- Cloud infrastructure background (excellent with managed services)
- Mixed team (diverse skills)

---

**Question 3**: Can you hire specialized talent (data engineers, $150K-$180K annually)?

Options:
- Yes, with budget (can recruit)
- Yes, but 6-12 month timeline acceptable
- No (hiring freeze, budget constraints)

---

## Section 2: Budget Constraints (Question Q2)

**Question Q2**: What's your annual security data platform budget? (SLIDER: $50K - $50M)

*Context: This determines cost model viability. <$500K eliminates enterprise SIEM per-GB pricing and Unity Catalog. $500K-$2M enables balanced OSS + managed services. $10M+ means cost is secondary to capability.*

*Note: In the V3 web tool, this is a logarithmic slider. For the MCP interview, provide your budget range or specific value.*

Options:
- <$500K (cost-sensitive, OSS-first stack required - DuckDB, Athena, Trino, Iceberg, Polaris)
- $500K-$2M (moderate budget, balanced OSS + managed services)
- $2M-$10M (enterprise budget, full vendor landscape available)
- $10M+ (large enterprise, best-in-class vendors - Databricks, Snowflake, Splunk)

Enter value: $___K annually OR specify range (e.g., "$500K-$1M")

---

**Question 5**: Is your CFO cost-sensitive or capability-focused?

*Context: This determines justification approach. Cost-sensitive requires quantified business case. Capability-focused prioritizes security outcomes over cost.*

Options:
- Cost-sensitive ("How much does it cost?" leads every conversation)
- Capability-focused ("Will it solve our problem?" leads, cost discussed after)
- Balanced (cost and capability weighted equally)

---

## Section 3: Data Sovereignty & Compliance (Questions 6-7)

**Question 6**: Any data residency requirements?

Options:
- GDPR (EU) - data must remain in EU data centers
- HIPAA (US Healthcare) - on-prem or certified cloud
- Chinese data localization laws
- Multi-region (GDPR + US + China) → **multi-region**
- None (no geographic restrictions)

---

**Question Q3**: Cloud Environment (SELECT ALL THAT APPLY - MULTI-SELECT)

Where will security data be stored? **Multi-cloud architectures are common** (AWS + Azure, AWS + on-prem).

*Context: On-prem requirement eliminates 50% of cloud-only vendors. Multi-cloud requires cloud-agnostic vendors (Trino, Iceberg, Polaris). Select ALL environments you need to support.*

Options (select all that apply):
- **AWS** - AWS-first architecture (Athena, Glue, EMR, S3)
- **Azure** - Azure-first architecture (Synapse, Fabric, ADLS)
- **GCP** - GCP-first architecture (BigQuery, GCS)
- **Multi-cloud** - AWS + Azure + GCP unified query (requires cloud-agnostic vendors)
- **On-premises** - Compliance requirement, data cannot leave data centers (eliminates 35 cloud-only vendors)

Enter (comma-separated): `aws, azure` OR `aws, on_prem` OR `multi_cloud` etc.

---

## Section 4: Vendor Relationships (Questions 8-9)

**Question 8**: Existing vendor relationships influencing decision?

Options:
- Splunk incumbent (5+ years deployment, institutional knowledge)
- AWS commitment (Enterprise Support, heavy AWS investment)
- Microsoft E5 licensing (Office 365 E5 includes Sentinel)
- None (greenfield, vendor-agnostic)

---

**Question Q4 (formerly 9)**: Risk tolerance for open source?

Options:
- High / OSS-first (comfortable with Apache projects, community support) → **oss-first**
- Medium / OSS with commercial support (OSS acceptable if vendor provides support) → **oss-with-support**
- Low / Commercial only (require vendor SLA, 24/7 support, legal accountability) → **commercial-only**

---

## Phase 3: Use Cases & Features (Questions Q5, 10-12)

**Question Q5**: Primary Use Cases (SELECT ALL THAT APPLY - MULTI-SELECT)

Which security analytics workloads do you need to support? **Most teams have multiple use cases** - select all that apply.

*Context: We'll recommend architectures that handle ALL selected use cases. Real-time dashboards require low-latency engines (ClickHouse <1s P95). Ad-hoc hunting benefits from flexible SQL engines (DuckDB, Trino). Compliance reporting works well with serverless (Athena). Detection rules need streaming (Kafka + Flink).*

Options (select all that apply):
- **Real-time dashboards** (<1s queries) - SOC dashboards, live threat monitoring → Requires: ClickHouse (1-3s P95) or Pinot
- **Ad-hoc threat hunting** - Security analysts exploring logs, iterative queries → Recommended: DuckDB (laptop-based) or Trino (team-wide)
- **Compliance reporting** (scheduled queries) - Regular reports, batch processing acceptable → Recommended: Athena (serverless) or Trino (scheduled)
- **Detection rules** (streaming + batch) - Real-time detection, streaming ingestion → Requires: Kafka + Flink or Cribl Stream + Iceberg

Enter (comma-separated): `real_time_dashboards, ad_hoc_hunting` OR `compliance_reporting` etc.

---

## Section 5: Tier 1 Mandatory Features (Questions 10-11)

*Within your chosen architecture, which specific features are mandatory vs. preferred?*

---

## Section 5: Tier 1 Mandatory Features (Questions 10-11)

**Question 10**: Which capabilities are MANDATORY (missing = immediately disqualified)?

*Note: Table format and catalog were decided in Phase 1 (F1-F2). These are feature requirements within your architecture.*

Select all that apply:
- [ ] SQL query interface (SOC analysts know SQL, not proprietary languages) → `sql_interface: true`
- [ ] 90-day+ hot retention (threat hunting workload requirement) → `long_term_retention: true`
- [ ] Multi-source integration (Zeek, Sysmon, CloudTrail, EDR telemetry) → `multi_source_integration: true`
- [ ] Time-series partitioning (prevent 20-45 minute query timeouts) → `time_series_partitioning: true`
- [ ] Real-time streaming (<30 second detection latency) → `streaming_query: true`
- [ ] On-premises deployment (compliance requirement) → Filter by `data_sovereignty: on-prem-only`
- [ ] Multi-cloud support (AWS + Azure + GCP unified query) → `multi_cloud: true`

---

**Question 11**: Any other mandatory requirements?

*Free text - I'll map these to capability fields if possible.*

---

## Section 6: Tier 2 Preferred Features (Question 12)

**Question 12**: Rate these capabilities by importance (1 = nice-to-have, 3 = strongly preferred):

*Note: These are preferences WITHIN your architecture. Table format and query engine characteristics were decided in Phase 1.*

- [ ] OCSF normalization support: Weight ___ (1-3)
- [ ] Real-time streaming ingestion: Weight ___ (1-3)
- [ ] Built-in ML anomaly detection: Weight ___ (1-3)
- [ ] Cloud-native architecture: Weight ___ (1-3)
- [ ] Multi-cloud support: Weight ___ (1-3)
- [ ] Managed service available: Weight ___ (1-3)
- [ ] SIEM integration: Weight ___ (1-3)
- [ ] API extensibility: Weight ___ (1-3)

---

## Interview Complete - Next Steps

Thank you! I have all the information needed to filter the vendor landscape.

**Please provide your answers**, and I'll:

1. **Apply Phase 1 foundational filters** (eliminate vendors not supporting your architecture: isolation pattern F0, table format F1, catalog F2, transformation strategy F3, query engine F4)
2. **Apply Phase 2 constraint filters** (eliminate vendors not matching team size, budget, sovereignty, vendor tolerance)
3. **Apply Phase 3 feature filters** (eliminate vendors missing mandatory capabilities from Q10)
4. **Score remaining vendors on Phase 3 preferences** (Q12 preferences with 3× weight multiplier)
5. **Identify 3-5 finalists** matching YOUR architecture + constraints
6. **Calculate TCO** for top finalists (5-year projections) with isolation pattern performance benefits
7. **(Future)** Match you to a Chapter 4 journey pattern (Jennifer/Marcus/Priya)
8. **(Future)** Generate comprehensive architecture recommendation report

**To execute the filtering workflow (V3 - Sizing First)**:

```
# NOTE: V3 uses sizing constraints to guide architecture decisions
# Phase 0: Sizing guides what's viable
# Phase 1: Architecture determines catalog/query engine
# Phase 2: Constraints filter within architecture
# Phase 3: Use cases score remaining vendors

# Step 1: Apply foundational filters (Phase 1 - Architecture-First)
apply_foundational_filters(
    isolation_pattern="YOUR_F0_ANSWER",   # isolated_dedicated, shared_corporate, multi_tenant_mssp
    table_format="YOUR_F1_ANSWER",        # iceberg, delta_lake, hudi, proprietary
    catalog="YOUR_F2_ANSWER",             # polaris, unity_catalog, nessie, glue, hive_metastore
    transformation="YOUR_F3_ANSWER",      # dbt, spark, vendor_builtin, custom_python
    query_engine_pref="YOUR_F4_ANSWER"    # Comma-separated for multi-select: "low_latency,high_concurrency"
)

# Step 2: Apply organizational constraints (Phase 2)
filter_vendors_tier1(
    team_size="YOUR_Q1_ANSWER",          # lean, standard, large
    budget="YOUR_Q2_ANSWER",             # <500K, 500K-2M, 2M-10M, 10M+ (or specific value like "750")
    data_sovereignty="YOUR_Q3_ANSWER",   # Comma-separated for multi-select: "aws,azure" or "aws,on_prem"
    vendor_tolerance="YOUR_Q4_ANSWER",   # oss-first, oss-with-support, commercial-only
    tier_1_requirements={{               # Phase 3 mandatory features (Q10)
        "sql_interface": true,
        # ... other mandatory requirements from Q10
    }}
)

# Step 3: Score finalists on use cases + preferences (Phase 3)
score_vendors_tier2(
    vendor_ids=[...],  # From filter_vendors_tier1 output
    preferences={{     # Phase 3 use cases (Q5) + preferred features (Q12)
        # Use cases from Q5 (multi-select)
        "real_time_dashboards": 3,
        "ad_hoc_hunting": 2,
        # Preferred features from Q12
        "ocsf_support": 3,
        "streaming_query": 2,
        # ... other preferences from Q12
    }}
)
```

**Ready to answer? Start with Phase 0, Question S1 (Current Data Ingestion Volume).**"""
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
