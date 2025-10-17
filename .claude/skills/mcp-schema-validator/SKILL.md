---
name: MCP Schema Validator
description: Validate Model Context Protocol (MCP) server schemas against Anthropic's official specification when user develops or modifies MCP resources, tools, or prompts. Trigger when user mentions "MCP", "schema", "validate server", "add tool", "add resource", "test MCP", or modifies server implementation. Ensure compliance with MCP spec, proper JSON schema format, tool descriptions match implementations, error handling patterns correct, and resource/tool/prompt schemas consistent. Prevent runtime errors from schema mismatches.
allowed-tools: Read, Grep, Bash
---

# MCP Schema Validator

## Purpose
Ensure Security Architect MCP Server complies with Anthropic's Model Context Protocol specification, catching schema errors before they cause runtime failures during Claude interactions.

## Trigger Conditions

**ACTIVATE when user:**
- Modifies MCP server implementation files (`server.py`, `resources/`, `tools/`, `prompts/`)
- Adds new MCP tools, resources, or prompts
- Says "validate schema", "check MCP compliance", "test server", "validate MCP"
- Mentions "schema error", "MCP not working", "tool failing"
- Prepares to test server with Claude desktop
- Updates vendor database structure or decision state schema

**DO NOT ACTIVATE when:**
- Writing non-MCP Python code (data models, utilities, tests)
- User is brainstorming MCP design (not implementing)
- Running general pytest tests (not MCP-specific)
- User explicitly says "skip validation" or "rough draft"

## MCP Specification Compliance Protocol

### Step 1: Schema Structure Validation

**Check MCP components exist and are properly structured:**

```bash
# Verify server entry point
Read: src/server.py

# Check for required MCP components
Grep: src/ for "list_resources", "read_resource", "list_tools", "call_tool", "list_prompts", "get_prompt"
```

**Required MCP Patterns (from Anthropic spec):**

**Resources** (read-only data exposed to Claude):
```python
@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="vendor://database",
            name="Vendor Database",
            description="64+ security data platform vendors with capability matrix",
            mimeType="application/json"
        )
    ]

@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content"""
    if uri == "vendor://database":
        return json.dumps(vendor_data)
    raise ValueError(f"Unknown resource: {uri}")
```

**Tools** (functions callable by Claude):
```python
@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="filter_vendors_tier1",
            description="Apply mandatory filters (budget, team size, data sovereignty)",
            inputSchema={
                "type": "object",
                "properties": {
                    "budget": {"type": "number", "description": "Annual budget in USD"},
                    "team_size": {"type": "string", "enum": ["small", "medium", "large"]}
                },
                "required": ["budget", "team_size"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute tool"""
    if name == "filter_vendors_tier1":
        # Implementation
        return [TextContent(type="text", text=result)]
    raise ValueError(f"Unknown tool: {name}")
```

**Prompts** (pre-written templates):
```python
@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List available prompts"""
    return [
        Prompt(
            name="decision_interview",
            description="12-step guided questionnaire for architect requirements",
            arguments=[
                PromptArgument(
                    name="architect_name",
                    description="Security architect's name",
                    required=False
                )
            ]
        )
    ]

@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    """Get prompt content"""
    if name == "decision_interview":
        messages = [PromptMessage(role="user", content=TextContent(type="text", text=prompt_text))]
        return GetPromptResult(messages=messages)
    raise ValueError(f"Unknown prompt: {name}")
```

### Step 2: JSON Schema Validation

**For each tool, validate inputSchema compliance:**

**✓ VALID Schema Patterns:**
```json
{
  "type": "object",
  "properties": {
    "budget": {
      "type": "number",
      "description": "Annual budget in USD",
      "minimum": 0
    },
    "team_size": {
      "type": "string",
      "enum": ["small", "medium", "large"],
      "description": "Team size category"
    },
    "data_sovereignty": {
      "type": "boolean",
      "description": "Requires on-premises deployment"
    }
  },
  "required": ["budget", "team_size"]
}
```

**✗ INVALID Schema Patterns:**
```json
{
  // ❌ Missing "type": "object"
  "properties": { ... }
}

{
  "type": "object",
  "properties": {
    "budget": {
      // ❌ Missing "type"
      "description": "Annual budget"
    }
  }
}

{
  "type": "object",
  "properties": {
    "team_size": {
      "type": "string",
      // ❌ Empty enum
      "enum": []
    }
  }
}
```

**Validation Checklist:**
- [ ] Top-level `"type": "object"` present
- [ ] Each property has `"type"` specified
- [ ] Each property has descriptive `"description"`
- [ ] Enums are non-empty and valid values
- [ ] Required fields listed in `"required"` array
- [ ] Numeric constraints (`minimum`, `maximum`) are valid
- [ ] No Python-specific types (use JSON types: `string`, `number`, `boolean`, `object`, `array`)

### Step 3: Tool Description Quality

**Tool descriptions are CRITICAL for Claude's tool selection.**

**✓ GOOD Tool Descriptions (specific, actionable):**
```python
Tool(
    name="filter_vendors_tier1",
    description="Apply mandatory filters to vendor database based on budget, team size, and data sovereignty requirements. Returns filtered list of vendors meeting all specified constraints. Use this first to eliminate vendors that don't meet hard requirements before scoring remaining vendors on preferred capabilities.",
    inputSchema={...}
)
```

**✗ BAD Tool Descriptions (vague, unhelpful):**
```python
Tool(
    name="filter_vendors_tier1",
    description="Filters vendors",  # ❌ Too vague, doesn't explain purpose
    inputSchema={...}
)
```

**Description Quality Standards:**
- ✅ Explains WHAT the tool does (specific action)
- ✅ Explains WHEN to use it (context/workflow)
- ✅ Explains WHAT it returns (expected output)
- ✅ Max 1-2 sentences (Claude scans many tools)
- ✅ Uses domain terminology (budget, team size, data sovereignty)
- ❌ Generic verbs without specifics ("processes data", "handles requests")
- ❌ Overly long explanations (>200 chars)

### Step 4: Implementation Consistency Check

**Verify tool implementation matches schema:**

```bash
# For each tool, check implementation
Read: src/tools/[tool_name].py

# Verify:
# 1. Function signature matches inputSchema parameters
# 2. Required parameters are enforced
# 3. Return type matches MCP spec (list[TextContent])
# 4. Error handling for invalid inputs
```

**Example Consistency Check:**

**Schema declares:**
```python
inputSchema={
    "type": "object",
    "properties": {
        "budget": {"type": "number"},
        "team_size": {"type": "string", "enum": ["small", "medium", "large"]}
    },
    "required": ["budget", "team_size"]
}
```

**Implementation MUST validate:**
```python
async def filter_vendors_tier1(budget: float, team_size: str) -> list[TextContent]:
    # ✅ Validate required parameters
    if budget is None or team_size is None:
        raise ValueError("budget and team_size are required")

    # ✅ Validate enum values
    if team_size not in ["small", "medium", "large"]:
        raise ValueError(f"Invalid team_size: {team_size}")

    # ✅ Validate numeric constraints
    if budget < 0:
        raise ValueError("budget must be non-negative")

    # Implementation...
    result = filter_logic(budget, team_size)

    # ✅ Return correct type
    return [TextContent(type="text", text=json.dumps(result))]
```

**Common Consistency Errors:**
- ❌ Schema says parameter required, implementation doesn't validate
- ❌ Schema defines enum, implementation accepts any string
- ❌ Schema says number, implementation doesn't validate type
- ❌ Return type doesn't match MCP spec (should be `list[TextContent]`)

### Step 5: Resource Schema Validation

**Vendor Database Schema:**

```bash
# Check vendor database structure
Read: data/vendor_database.json

# Verify each vendor has required fields:
# - id (unique identifier)
# - name (vendor name)
# - category (query_engine, catalog, lakehouse, etc.)
# - cost_model (per_gb, consumption, subscription, oss, hybrid)
# - capabilities (9 categories scored 0-5)
# - description (evidence-based, no marketing hype)
```

**Required Vendor Schema:**
```json
{
  "id": "vendor_001",
  "name": "Dremio",
  "category": "query_engine",
  "cost_model": "subscription",
  "tier1_filters": {
    "min_budget": 100000,
    "min_team_size": "small",
    "supports_on_prem": true,
    "supports_cloud": true
  },
  "tier2_capabilities": {
    "query_performance": 5,
    "schema_flexibility": 5,
    "security_integration": 4,
    "data_lake_support": 5,
    "real_time_capability": 3,
    "cost_efficiency": 3,
    "ease_of_use": 4,
    "ecosystem_maturity": 4,
    "vendor_support": 5
  },
  "description": "Dremio provides SQL query engine with Iceberg catalog integration...",
  "evidence_tier": 1,
  "production_deployments": ["Okta (Jake Thomas)", "..."]
}
```

**Schema Validation Checks:**
- [ ] All 64+ vendors have complete schemas
- [ ] No missing required fields
- [ ] Capability scores are 0-5 (not out of range)
- [ ] Cost models are valid enums
- [ ] Evidence tiers are 1-5
- [ ] Descriptions are evidence-based (no marketing hype)

### Step 6: Error Handling Validation

**MCP servers MUST handle errors gracefully:**

**✓ GOOD Error Handling:**
```python
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "filter_vendors_tier1":
            # Validate inputs
            if "budget" not in arguments:
                raise ValueError("Missing required parameter: budget")

            # Execute
            result = filter_vendors_tier1(**arguments)
            return [TextContent(type="text", text=json.dumps(result))]

        # Unknown tool
        raise ValueError(f"Unknown tool: {name}")

    except ValueError as e:
        # ✅ Return error as TextContent (Claude can read it)
        return [TextContent(type="text", text=f"Error: {str(e)}")]

    except Exception as e:
        # ✅ Catch unexpected errors
        return [TextContent(type="text", text=f"Unexpected error: {str(e)}")]
```

**✗ BAD Error Handling:**
```python
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    # ❌ No try/except - errors crash server
    result = filter_vendors_tier1(**arguments)
    return [TextContent(type="text", text=json.dumps(result))]
```

**Error Handling Checklist:**
- [ ] All tool calls wrapped in try/except
- [ ] ValueError for invalid inputs (with helpful messages)
- [ ] Unknown tool/resource names raise clear errors
- [ ] Errors returned as TextContent (not raised to crash server)
- [ ] Error messages are helpful for debugging

### Step 7: Testing Recommendations

**After schema validation, recommend tests:**

```python
# tests/test_mcp_schema.py
import pytest
from src.server import app

@pytest.mark.asyncio
async def test_list_resources():
    """Verify resources are properly declared"""
    resources = await app.list_resources()
    assert len(resources) > 0
    for resource in resources:
        assert resource.uri
        assert resource.name
        assert resource.description
        assert resource.mimeType

@pytest.mark.asyncio
async def test_list_tools():
    """Verify tools have valid schemas"""
    tools = await app.list_tools()
    assert len(tools) > 0
    for tool in tools:
        assert tool.name
        assert tool.description
        assert tool.inputSchema
        assert "type" in tool.inputSchema
        assert tool.inputSchema["type"] == "object"
        assert "properties" in tool.inputSchema

@pytest.mark.asyncio
async def test_tool_input_validation():
    """Verify tools validate inputs correctly"""
    # Test missing required parameter
    result = await app.call_tool("filter_vendors_tier1", {})
    assert "Error" in result[0].text or "required" in result[0].text.lower()

    # Test invalid enum value
    result = await app.call_tool("filter_vendors_tier1", {
        "budget": 500000,
        "team_size": "invalid"
    })
    assert "Error" in result[0].text or "Invalid" in result[0].text
```

## Validation Response Structure

Provide schema validation results in this format:

```
MCP Schema Validation Report
============================

SERVER: security-architect-mcp-server
VALIDATION DATE: [Date]

COMPONENT STRUCTURE:
✅ Resources: [count] defined
✅ Tools: [count] defined
✅ Prompts: [count] defined

SCHEMA COMPLIANCE:

Resources:
✅ vendor://database - Valid schema
✅ decision://state - Valid schema

Tools:
✅ filter_vendors_tier1 - Valid schema, good description
✅ score_vendors_tier2 - Valid schema, good description
⚠️ calculate_tco - Schema valid, description could be more specific
❌ generate_report - Invalid schema: missing "type" on properties.format

Prompts:
✅ decision_interview - Valid schema
✅ journey_matching - Valid schema

INPUT SCHEMA ISSUES:

Tool: generate_report
File: src/tools/report.py
Issue: inputSchema["properties"]["format"] missing "type" field
Fix: Add "type": "string" to format property

IMPLEMENTATION CONSISTENCY:

Tool: filter_vendors_tier1
✅ Implementation validates required parameters
✅ Implementation validates enum values
✅ Return type matches MCP spec

Tool: calculate_tco
⚠️ Implementation doesn't validate budget >= 0
Fix: Add validation: if budget < 0: raise ValueError(...)

ERROR HANDLING:

✅ All tools wrapped in try/except
✅ Errors returned as TextContent
✅ Error messages are descriptive

VENDOR DATABASE SCHEMA:

Total Vendors: 64
✅ All vendors have complete schemas
⚠️ 3 vendors missing production_deployments field
❌ Vendor vendor_042 has capability score 6 (max is 5)

RECOMMENDED ACTIONS:

Priority 1 (Blocks MCP functionality):
1. Fix generate_report schema: Add missing "type" fields
2. Fix vendor_042 capability score: Change from 6 to 5

Priority 2 (Quality improvements):
1. Add budget validation in calculate_tco implementation
2. Improve calculate_tco tool description (be more specific)
3. Add production_deployments to 3 vendors

Priority 3 (Nice to have):
1. Add integration tests for all tools
2. Add schema validation tests to CI/CD

OVERALL STATUS: ⚠️ NEEDS FIXES (2 blocking issues)

NEXT STEPS:
1. Fix Priority 1 issues
2. Re-run validation
3. Test server with Claude desktop app
```

## Integration with Other Skills

**Works WITH:**
- **systematic-debugger** (personal): Debug MCP runtime errors
- **tdd-enforcer** (personal): Write tests for MCP tools
- **vendor-data-quality-checker** (MCP project): Validate vendor database content

**Sequence:**
1. User modifies MCP server code
2. **mcp-schema-validator** → Validate schema compliance
3. **tdd-enforcer** → Ensure tests exist for new tools
4. **systematic-debugger** → Debug if runtime errors occur

## MCP Project Context

**Current Status** (as of Oct 17, 2025):
- Phase 2 in progress
- 7 tools operational
- 64 vendors (expanding to 80)
- 144 tests passing, 87% coverage

**Key Files:**
- `src/server.py` - MCP server entry point
- `data/vendor_database.json` - 64+ vendor schemas
- `src/resources/` - Resource implementations
- `src/tools/` - Tool implementations
- `src/prompts/` - Prompt implementations

**Official MCP Spec:**
- https://modelcontextprotocol.io/docs
- https://github.com/anthropics/anthropic-sdk-python

## Quick Reference: Common Schema Errors

**Error 1: Missing "type" in schema**
```python
# ❌ WRONG
{"properties": {"budget": {"description": "Budget"}}}

# ✅ CORRECT
{"properties": {"budget": {"type": "number", "description": "Budget"}}}
```

**Error 2: Empty enum**
```python
# ❌ WRONG
{"type": "string", "enum": []}

# ✅ CORRECT
{"type": "string", "enum": ["small", "medium", "large"]}
```

**Error 3: Tool doesn't validate required parameters**
```python
# ❌ WRONG
async def filter_vendors(budget: float, team_size: str):
    return filter_logic(budget, team_size)  # No validation

# ✅ CORRECT
async def filter_vendors(budget: float, team_size: str):
    if budget is None:
        raise ValueError("budget is required")
    if team_size not in ["small", "medium", "large"]:
        raise ValueError(f"Invalid team_size: {team_size}")
    return filter_logic(budget, team_size)
```

**Error 4: Wrong return type**
```python
# ❌ WRONG
async def call_tool(name: str, arguments: dict) -> str:
    return json.dumps(result)

# ✅ CORRECT
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(result))]
```

## References

- **MCP Specification**: https://modelcontextprotocol.io/docs/specification
- **Anthropic MCP SDK**: https://github.com/anthropics/anthropic-sdk-python
- **Project Design**: `/home/jerem/security-architect-mcp-server/ULTRATHINK-MCP-SERVER-DESIGN.md`
- **README**: `/home/jerem/security-architect-mcp-server/README.md`

---

**Version**: 1.0
**Created**: 2025-10-17
**Scope**: security-architect-mcp-server project
**Purpose**: Catch MCP schema errors before runtime failures
