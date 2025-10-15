"""
Basic tests for MCP server functionality - Phase 1 with Tier 1 Filtering
"""

import json

import pytest

from src.server import (
    handle_call_tool,
    handle_get_prompt,
    handle_list_prompts,
    handle_list_resources,
    handle_list_tools,
    handle_read_resource,
)


@pytest.mark.asyncio
async def test_list_resources():
    """Test that resources are listed correctly."""
    resources = await handle_list_resources()

    assert len(resources) == 1
    assert str(resources[0].uri) == "vendor://database/stats"
    assert resources[0].name == "Vendor Database Statistics"
    assert resources[0].mimeType == "application/json"


@pytest.mark.asyncio
async def test_read_resource():
    """Test reading vendor database statistics resource."""
    content = await handle_read_resource("vendor://database/stats")
    stats = json.loads(content)

    assert "total_vendors" in stats
    assert "categories" in stats
    assert "last_updated" in stats
    assert "update_cadence" in stats
    assert stats["total_vendors"] == 10
    assert stats["status"] == "Phase 1 Week 3-8: Tier 1 Filtering Active"


@pytest.mark.asyncio
async def test_read_resource_invalid_uri():
    """Test that invalid resource URI raises error."""
    with pytest.raises(ValueError, match="Unknown resource URI"):
        await handle_read_resource("invalid://uri")


@pytest.mark.asyncio
async def test_list_tools():
    """Test that tools are listed correctly."""
    tools = await handle_list_tools()

    assert len(tools) == 2
    tool_names = [t.name for t in tools]
    assert "list_vendors" in tool_names
    assert "filter_vendors_tier1" in tool_names
    assert "inputSchema" in tools[0].model_dump()


@pytest.mark.asyncio
async def test_call_tool_list_vendors():
    """Test calling list_vendors tool without filters."""
    result = await handle_call_tool("list_vendors", {})

    assert len(result) == 1
    assert result[0].type == "text"

    data = json.loads(result[0].text)
    assert "total" in data
    assert "vendors" in data
    assert data["total"] == 10  # Real database has 10 vendors


@pytest.mark.asyncio
async def test_call_tool_list_vendors_with_category():
    """Test calling list_vendors tool with category filter."""
    result = await handle_call_tool("list_vendors", {"category": "SIEM"})

    data = json.loads(result[0].text)
    assert data["category_filter"] == "SIEM"
    assert data["total"] == 4  # 4 SIEM platforms in database


@pytest.mark.asyncio
async def test_call_tool_filter_vendors_tier1():
    """Test calling filter_vendors_tier1 tool."""
    result = await handle_call_tool("filter_vendors_tier1", {
        "team_size": "lean",
        "budget": "<500K",
        "tier_1_requirements": {"sql_interface": True}
    })

    assert len(result) == 1
    assert result[0].type == "text"

    data = json.loads(result[0].text)
    assert "summary" in data
    assert "filters_applied" in data
    assert "viable_vendors" in data
    assert "eliminated_vendors" in data
    assert data["initial_count"] == 10

    # Lean team + tight budget should filter most vendors
    assert data["filtered_count"] < data["initial_count"]


@pytest.mark.asyncio
async def test_call_tool_invalid_tool():
    """Test that calling invalid tool raises error."""
    with pytest.raises(ValueError, match="Unknown tool"):
        await handle_call_tool("invalid_tool", {})


@pytest.mark.asyncio
async def test_list_prompts():
    """Test that prompts are listed correctly."""
    prompts = await handle_list_prompts()

    assert len(prompts) == 1
    assert prompts[0].name == "start_decision"
    assert len(prompts[0].arguments) == 0


@pytest.mark.asyncio
async def test_get_prompt():
    """Test getting start_decision prompt."""
    prompt = await handle_get_prompt("start_decision")

    assert prompt.role == "user"
    assert prompt.content.type == "text"
    assert "Welcome to the Security Architect Decision Support Tool" in prompt.content.text
    assert "Tier 1 Filtering" in prompt.content.text
    assert "filter_vendors_tier1" in prompt.content.text


@pytest.mark.asyncio
async def test_get_prompt_invalid_name():
    """Test that getting invalid prompt raises error."""
    with pytest.raises(ValueError, match="Unknown prompt"):
        await handle_get_prompt("invalid_prompt")
