#!/usr/bin/env python3
"""
Security Architect MCP Server - Main Entry Point

This MCP server helps cybersecurity architects filter 80+ security data platforms
to 3-5 personalized finalists using the decision framework from
"Modern Data Stack for Cybersecurity" book.

Phase 1 Hello World: Basic resource, tool, and prompt to verify MCP functionality.
"""

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource, Prompt, PromptMessage


# Initialize MCP server
app = Server("security-architect-mcp-server")


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
        # Hello world: Return mock statistics
        # In Phase 1 Week 3+, this will query the real vendor database
        stats = {
            "total_vendors": 10,
            "categories": ["Data Virtualization", "Data Lake", "SIEM"],
            "last_updated": "2025-10-15",
            "status": "Phase 1 Week 1-2: Hello World Mode"
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
                        "description": "Optional: Filter vendors by category (e.g., 'SIEM', 'Data Lake', 'Data Virtualization')",
                    }
                },
            }
        )
    ]


async def handle_call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute a tool by name with given arguments."""
    if name == "list_vendors":
        category = arguments.get("category")

        # Hello world: Return mock vendor list
        # In Phase 1 Week 3+, this will query the real vendor database
        vendors = [
            {"name": "Dremio", "category": "Data Virtualization", "description": "Data lakehouse platform"},
            {"name": "Amazon Athena", "category": "Data Lake", "description": "Serverless interactive query service"},
            {"name": "Splunk", "category": "SIEM", "description": "Security information and event management"},
        ]

        # Filter by category if specified
        if category:
            vendors = [v for v in vendors if v["category"] == category]

        result = {
            "total": len(vendors),
            "category_filter": category,
            "vendors": vendors
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
        # Hello world: Return basic decision interview starter
        # In Phase 1 Week 3+, this will be the full 12-step interview
        return PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text="""Welcome to the Security Architect Decision Support Tool!

This interactive assistant helps you filter 80+ security data platforms to 3-5 personalized finalists in about 30 minutes.

The decision framework is based on Chapters 3-4 of "Modern Data Stack for Cybersecurity" book.

**Phase 1 Week 1-2 Status**: Hello World Mode
- Currently demonstrating basic MCP functionality
- Full decision interview coming in Week 3-8

**Current Capabilities**:
- View vendor database statistics (use resource: vendor://database/stats)
- List vendors (use tool: list_vendors)

**Coming Soon**:
- 12-step decision interview
- Tier 1 filtering (team, budget, sovereignty)
- Tier 2 scoring (preferred capabilities)
- Architecture report generation
- Journey persona matching (Jennifer/Marcus/Priya)

How would you like to explore the current capabilities?"""
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
