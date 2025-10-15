# Security Architect MCP Server - Setup Guide

This guide will help you set up and run the Security Architect MCP Server with Claude Desktop.

## Prerequisites

- Python 3.10+ (tested with Python 3.12.3)
- Claude Desktop installed
- Git (optional, for cloning the repository)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/flying-coyote/security-architect-mcp-server.git
cd security-architect-mcp-server
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -e ".[dev]"
```

This installs:
- Core dependencies: mcp, pydantic, httpx
- Dev dependencies: pytest, black, ruff, mypy

### 4. Verify Installation

Run the test suite to verify everything is working:

```bash
pytest -v
```

You should see all 10 tests passing with ~93% code coverage.

### 5. Configure Claude Desktop

Add the MCP server to your Claude Desktop configuration:

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

**Configuration**:

```json
{
  "mcpServers": {
    "security-architect": {
      "command": "/absolute/path/to/security-architect-mcp-server/venv/bin/python",
      "args": [
        "-m",
        "src.server"
      ],
      "cwd": "/absolute/path/to/security-architect-mcp-server"
    }
  }
}
```

**Important**: Replace `/absolute/path/to/security-architect-mcp-server` with the actual absolute path to your cloned repository.

### 6. Restart Claude Desktop

After updating the configuration, restart Claude Desktop to load the MCP server.

## Testing the Integration

Once Claude Desktop restarts, test the integration:

1. **Check Resources**: Ask Claude to "list available resources"
   - You should see "Vendor Database Statistics"

2. **Read Resource**: Ask Claude to "read the vendor database statistics resource"
   - You should see mock statistics showing 10 vendors

3. **Use Tool**: Ask Claude to "list vendors" or "list SIEM vendors"
   - You should see a list of mock vendors (Dremio, Athena, Splunk)

4. **Try Prompt**: Ask Claude to "use the start_decision prompt"
   - You should see the welcome message for the decision interview

## Current Phase: Hello World (Phase 1 Week 1-2)

The current implementation is a **hello world** version demonstrating basic MCP functionality:

### Available Resources
- `vendor://database/stats` - Mock vendor database statistics

### Available Tools
- `list_vendors` - List mock vendors (optionally filtered by category)

### Available Prompts
- `start_decision` - Welcome message for decision interview

### Coming Soon (Phase 1 Week 3-8)
- Real vendor database with 80+ platforms
- 12-step decision interview
- Tier 1 filtering (team, budget, sovereignty)
- Tier 2 scoring (preferred capabilities)
- Architecture report generation
- Journey persona matching (Jennifer/Marcus/Priya)

## Development Workflow

### Running Tests

```bash
# Run all tests with coverage
pytest -v

# Run specific test file
pytest tests/test_server.py -v

# Run with coverage report
pytest --cov=src --cov-report=html
```

### Code Formatting

```bash
# Format code with Black
black src/ tests/

# Check code with Ruff
ruff check src/ tests/

# Type checking with mypy
mypy src/
```

### Running the Server Standalone

For development/debugging, you can run the server standalone:

```bash
python -m src.server
```

The server will start and wait for MCP messages on stdin/stdout. This is primarily useful for debugging the MCP protocol itself.

## Troubleshooting

### Claude Desktop doesn't see the MCP server

1. **Check configuration path**: Ensure `claude_desktop_config.json` is in the correct location
2. **Verify absolute paths**: All paths in the config must be absolute, not relative
3. **Check Python path**: Ensure the Python path points to your virtual environment
4. **Restart Claude Desktop**: Configuration changes require a restart
5. **Check Claude Desktop logs**: Look for error messages in Claude Desktop's console/logs

### Tests failing

1. **Virtual environment**: Ensure you've activated the virtual environment
2. **Dependencies**: Run `pip install -e ".[dev]"` to ensure all dependencies are installed
3. **Python version**: Ensure Python 3.10+ is being used

### Import errors

If you see import errors like "cannot import name 'handle_list_resources'", ensure you've installed the package in editable mode:

```bash
pip install -e ".[dev]"
```

## Project Structure

```
security-architect-mcp-server/
├── src/
│   ├── server.py           # Main MCP server entry point
│   ├── resources/          # Resource handlers (TBD)
│   ├── tools/              # Tool handlers (TBD)
│   ├── prompts/            # Prompt templates (TBD)
│   └── utils/              # Utility functions (TBD)
├── data/
│   ├── vendor_database.json      # Vendor data (TBD)
│   ├── decision_states/          # Session persistence (TBD)
│   └── chapter_framework/        # Decision logic (TBD)
├── tests/
│   └── test_server.py      # MCP server tests
├── docs/
│   └── SETUP.md            # This file
├── pyproject.toml          # Python project configuration
└── README.md               # Project overview
```

## Next Steps

After verifying the hello world installation:

1. **Week 3-4**: Implement Vendor Pydantic schema and enter initial 10-80 vendors
2. **Week 5-6**: Implement decision interview prompt and filtering logic
3. **Week 7-8**: Implement scoring logic and architecture report generation

## License

- **MCP Server**: Apache 2.0
- **Vendor Database**: CC BY-SA 4.0

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/flying-coyote/security-architect-mcp-server/issues
- Book Repository: https://github.com/flying-coyote/modern-data-stack-for-cybersecurity-book

## References

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Claude Desktop Integration](https://docs.anthropic.com/claude/docs)
- [Modern Data Stack for Cybersecurity Book](https://github.com/flying-coyote/modern-data-stack-for-cybersecurity-book)
