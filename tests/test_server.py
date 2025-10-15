"""
Basic tests for MCP server functionality - Phase 1 Hello World
"""

import pytest
from src.server import (
    handle_list_resources,
    handle_read_resource,
    handle_list_tools,
    handle_call_tool,
    handle_list_prompts,
    handle_get_prompt,
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
    import json

    content = await handle_read_resource("vendor://database/stats")
    stats = json.loads(content)

    assert "total_vendors" in stats
    assert "categories" in stats
    assert "last_updated" in stats
    assert stats["status"] == "Phase 1 Week 1-2: Hello World Mode"


@pytest.mark.asyncio
async def test_read_resource_invalid_uri():
    """Test that invalid resource URI raises error."""
    with pytest.raises(ValueError, match="Unknown resource URI"):
        await handle_read_resource("invalid://uri")


@pytest.mark.asyncio
async def test_list_tools():
    """Test that tools are listed correctly."""
    tools = await handle_list_tools()

    assert len(tools) == 1
    assert tools[0].name == "list_vendors"
    assert "inputSchema" in tools[0].model_dump()


@pytest.mark.asyncio
async def test_call_tool_list_vendors():
    """Test calling list_vendors tool without filters."""
    import json

    result = await handle_call_tool("list_vendors", {})

    assert len(result) == 1
    assert result[0].type == "text"

    data = json.loads(result[0].text)
    assert "total" in data
    assert "vendors" in data
    assert data["total"] == 3  # Hello world has 3 mock vendors


@pytest.mark.asyncio
async def test_call_tool_list_vendors_with_category():
    """Test calling list_vendors tool with category filter."""
    import json

    result = await handle_call_tool("list_vendors", {"category": "SIEM"})

    data = json.loads(result[0].text)
    assert data["category_filter"] == "SIEM"
    assert data["total"] == 1
    assert data["vendors"][0]["name"] == "Splunk"


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


@pytest.mark.asyncio
async def test_get_prompt_invalid_name():
    """Test that getting invalid prompt raises error."""
    with pytest.raises(ValueError, match="Unknown prompt"):
        await handle_get_prompt("invalid_prompt")
