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
    assert stats["total_vendors"] == 64
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

    # Should have 8 tools (list, filter, score, report, journey, calculate_tco, compare_vendors_tco, generate_poc_test_suite)
    assert len(tools) == 8
    tool_names = [t.name for t in tools]
    assert "list_vendors" in tool_names
    assert "filter_vendors_tier1" in tool_names
    assert "score_vendors_tier2" in tool_names
    assert "generate_architecture_report" in tool_names
    assert "match_journey_persona" in tool_names
    assert "calculate_tco" in tool_names
    assert "compare_vendors_tco" in tool_names
    assert "generate_poc_test_suite" in tool_names
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
    assert data["total"] == 64  # Real database has 54 vendors


@pytest.mark.asyncio
async def test_call_tool_list_vendors_with_category():
    """Test calling list_vendors tool with category filter."""
    result = await handle_call_tool("list_vendors", {"category": "SIEM"})

    data = json.loads(result[0].text)
    assert data["category_filter"] == "SIEM"
    assert data["total"] == 15  # 15 SIEM platforms in database (11 original + 4 new)


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
    assert data["initial_count"] == 64

    # Lean team + tight budget should filter most vendors
    assert data["filtered_count"] < data["initial_count"]


@pytest.mark.asyncio
async def test_call_tool_score_vendors_tier2():
    """Test calling score_vendors_tier2 tool."""
    result = await handle_call_tool("score_vendors_tier2", {
        "vendor_ids": ["amazon-athena", "snowflake", "databricks"],
        "preferences": {
            "sql_interface": 3,
            "open_table_format": 3,
            "cloud_native": 2
        }
    })

    assert len(result) == 1
    assert result[0].type == "text"

    data = json.loads(result[0].text)
    assert "summary" in data
    assert "preferences" in data
    assert "scored_vendors" in data
    assert "top_5" in data
    assert data["vendor_count"] == 3
    assert data["max_possible_score"] == 8  # 3+3+2

    # Check that vendors are ranked
    scores = [v["score"] for v in data["scored_vendors"]]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_call_tool_score_vendors_tier2_invalid_vendor():
    """Test that invalid vendor ID returns error."""
    result = await handle_call_tool("score_vendors_tier2", {
        "vendor_ids": ["invalid-vendor-id"],
        "preferences": {"sql_interface": 3}
    })

    data = json.loads(result[0].text)
    assert "error" in data


@pytest.mark.asyncio
async def test_call_tool_score_vendors_tier2_missing_params():
    """Test that missing parameters returns error."""
    result = await handle_call_tool("score_vendors_tier2", {
        "vendor_ids": []
    })

    data = json.loads(result[0].text)
    assert "error" in data


@pytest.mark.asyncio
async def test_call_tool_invalid_tool():
    """Test that calling invalid tool raises error."""
    with pytest.raises(ValueError, match="Unknown tool"):
        await handle_call_tool("invalid_tool", {})


@pytest.mark.asyncio
async def test_list_prompts():
    """Test that prompts are listed correctly."""
    prompts = await handle_list_prompts()

    assert len(prompts) == 2
    prompt_names = [p.name for p in prompts]
    assert "start_decision" in prompt_names
    assert "decision_interview" in prompt_names
    assert len(prompts[0].arguments) == 0


@pytest.mark.asyncio
async def test_get_prompt():
    """Test getting start_decision prompt."""
    prompt = await handle_get_prompt("start_decision")

    assert prompt.role == "user"
    assert prompt.content.type == "text"
    assert "Welcome to the Security Architect Decision Support Tool" in prompt.content.text
    assert "Tier 1 Filtering" in prompt.content.text
    assert "Tier 2 Scoring" in prompt.content.text
    assert "filter_vendors_tier1" in prompt.content.text
    assert "score_vendors_tier2" in prompt.content.text


@pytest.mark.asyncio
async def test_get_prompt_decision_interview():
    """Test getting decision_interview prompt."""
    prompt = await handle_get_prompt("decision_interview")

    assert prompt.role == "user"
    assert prompt.content.type == "text"
    assert "Security Architecture Decision Interview" in prompt.content.text
    assert "12-step interview" in prompt.content.text
    assert "Section 1: Team Capacity" in prompt.content.text
    assert "Section 2: Budget Constraints" in prompt.content.text
    assert "Section 3: Data Sovereignty" in prompt.content.text
    assert "Section 4: Vendor Relationships" in prompt.content.text
    assert "Section 5: Tier 1 Mandatory Requirements" in prompt.content.text
    assert "Section 6: Tier 2 Strongly Preferred" in prompt.content.text
    assert "filter_vendors_tier1" in prompt.content.text
    assert "score_vendors_tier2" in prompt.content.text


@pytest.mark.asyncio
async def test_get_prompt_invalid_name():
    """Test that getting invalid prompt raises error."""
    with pytest.raises(ValueError, match="Unknown prompt"):
        await handle_get_prompt("invalid_prompt")
