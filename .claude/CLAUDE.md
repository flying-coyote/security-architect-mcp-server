# Security Architect MCP Server - Project Context

## Project Purpose
AI-powered interactive decision support tool transforming the "Modern Data Stack for Cybersecurity" book's decision framework into a conversational assistant that helps cybersecurity architects filter 80+ security data platforms to 3-5 personalized finalists in 30 minutes.

## Key Documentation Files

### README.md
**Purpose**: Project vision, strategic value, implementation roadmap, success metrics
**Update Trigger**: Phase transitions, milestone completions, strategic pivots
**Status**: Complete - comprehensive overview

### ULTRATHINK-MCP-SERVER-DESIGN.md
**Purpose**: 18,000-word comprehensive design document with FRAME-ANALYZE-SYNTHESIZE methodology
**Update Trigger**: Major design decisions, architecture changes
**Status**: Complete - design phase finished

### pyproject.toml
**Purpose**: Python project configuration, dependencies, dev tools
**Update Trigger**: Dependency changes, version updates
**Status**: Complete - ready for Phase 1 implementation

## Current Status
**Phase**: Design Complete - Ready for Phase 1 Implementation
**Last Updated**: October 14, 2025
**Current Branch**: main

**Phase 1 Week 1-2 Actions** (NEXT IMMEDIATE WORK):
1. Setup Python project structure (src/, data/, tests/, docs/)
2. MCP server hello-world (basic resource, tool, prompt)
3. Define Vendor Pydantic schema
4. Enter 10 vendors manually (Dremio, Athena, Splunk, Starburst, Denodo, Snowflake, Databricks, Elastic, QRadar, Sentinel)

**Estimated Effort**: 20-30 hours

## Project Architecture

### MCP Components

**Resources** (Data exposed to Claude):
1. Vendor Database - 80+ security data platforms with capability matrix
2. Decision State - Current architect's conversation progress
3. Chapter Framework - Chapter 3-4 decision tree logic from book

**Tools** (Functions callable by Claude):
1. `filter_vendors_tier_1()` - Applies mandatory filters (team, budget, sovereignty)
2. `score_vendors_tier_2()` - Scores vendors on preferred capabilities (3× weight)
3. `generate_architecture_report()` - Produces 12-15 page recommendation report
4. `calculate_tco()` - Projects 5-year Total Cost of Ownership
5. `match_journey_persona()` - Identifies Chapter 4 journey match (Jennifer/Marcus/Priya)

**Prompts** (Pre-written templates):
1. Decision Interview - 12-step guided questionnaire
2. Journey Matching - Explains persona match and architecture pattern

### Directory Structure

```
security-architect-mcp-server/
├── README.md (project overview)
├── ULTRATHINK-MCP-SERVER-DESIGN.md (comprehensive design doc)
├── pyproject.toml (Python dependencies)
├── src/
│   ├── server.py (Main MCP server entry point - TBD)
│   ├── resources/ (vendor_database.py, decision_state.py - TBD)
│   ├── tools/ (filter, score, report, cost, journey - TBD)
│   ├── prompts/ (decision_interview.py, journey_personas.py - TBD)
│   └── utils/ (filters, scoring, report_generator - TBD)
├── data/
│   ├── vendor_database.json (80+ vendors - TBD)
│   ├── decision_states/ (session persistence - TBD)
│   └── chapter_framework/ (decision tree logic - TBD)
├── tests/ (test_filtering, test_journey_matching, test_report - TBD)
└── docs/ (SETUP.md, USAGE.md, ARCHITECTURE.md - TBD)
```

## Quality Standards

### From Second Brain Project
This project inherits quality standards from [second-brain](https://github.com/flying-coyote/second-brain):

**Evidence-Based Reasoning**:
- Decision framework validated by book research (115,500 words)
- Vendor capabilities sourced from production deployments
- TCO projections based on documented cost models
- Hypothesis validation through real architect decisions

**Professional Objectivity**:
- Navigation, not prescription - multiple valid architecture paths
- Honest trade-off documentation (no "perfect" vendor)
- Balanced vendor assessment (open source + commercial)
- Acknowledge limitations and alternatives

**Systematic Documentation**:
- ULTRATHINK methodology applied throughout design
- Type-safe implementation (Pydantic schemas, mypy)
- Test-driven development (pytest, 80%+ coverage target)
- Session archival for major milestones

**Code Quality**:
- Python 3.10+ type hints throughout
- Black formatting (100 char line length)
- Ruff linting (pycodestyle, pyflakes, isort)
- Pytest with async support

### MCP Server-Specific Standards

**Conversational Design**:
- Natural language questions (not technical jargon)
- Progressive disclosure (start simple, add complexity)
- Context persistence across conversation
- Honest uncertainty communication

**Vendor Neutrality**:
- No vendor sponsorships accepted
- Equal treatment in filtering logic
- Capability matrix based on documented features
- Cost data verified from public sources

**Privacy & Transparency**:
- No architect data uploaded without explicit permission
- Clear documentation of what MCP server accesses
- Open source (Apache 2.0 license)
- Anonymized case studies opt-in only

## Implementation Roadmap

### Phase 1: Core Decision Tree (Month 1-2) - **CURRENT PHASE**

**Deliverables**:
- [ ] MCP server basic structure (Python 3.10+, MCP SDK 1.2.0+)
- [ ] Vendor database (80+ vendors, manual JSON file)
- [ ] Decision interview prompt (12-step guided conversation)
- [ ] Filter/score tools (Tier 1-2 logic from Chapter 3)
- [ ] Architecture report generator (Markdown output)
- [ ] Journey matching tool (Jennifer/Marcus/Priya personas)

**Timeline**: 6-8 weeks at 20 hours/week (110-150 hours total)

**Success Criteria**:
- 3 beta testers complete decision interview successfully
- Vendor landscape filtered 80 → 3-5 finalists
- Architecture reports generated with honest trade-offs

### Phase 2: Living Literature Review Integration (Month 3-4)

**Deliverables**:
- IT Harvest API integration (if partnership succeeds) OR web scraping fallback
- Quarterly vendor database update pipeline
- Cost calculator tool (TCO projections)
- Hypothesis validation pipeline

**Timeline**: 5-7 weeks (90-130 hours total)

### Phase 3: Blog Integration & Content Generation (Month 5-6)

**Deliverables**:
- Blog post generator (decision conversation → anonymized case study)
- POC test suite generator
- Use Case Library integration (detection requirements mapping)
- Expert interview synthesizer

**Timeline**: 4-5 weeks (75-105 hours total)

## Git Workflow

### Commit Message Conventions
```
🎯 Phase milestones and major deliverables
🏗️ Infrastructure and project setup
📊 Data additions (vendor database, decision framework)
🔧 Tool implementations (filter, score, report, cost, journey)
📝 Documentation updates
✅ Tests and validation
🐛 Bug fixes
```

### Branch Strategy
- `main` - stable releases
- `dev` - active development
- `feature/*` - specific features (e.g., `feature/vendor-filtering`)
- `docs/*` - documentation improvements

## Integration Points

### Book Manuscript Integration
- **Repository**: https://github.com/flying-coyote/modern-data-stack-for-cybersecurity-book
- **Integration**: Chapter 3-4 decision framework logic extracted to MCP tools
- **Appendix C**: "Interactive Decision Support Tool" - setup guide for Claude Desktop
- **Value**: Transforms static book content into interactive AI assistant

### Literature Review Integration
- **Repository**: https://github.com/flying-coyote/security-data-literature-review
- **Integration**: Vendor database sourced from 75+ validated sources (Phase 2)
- **Value**: Evidence-based vendor capabilities, validated cost models

### Blog Integration
- **Repository**: https://github.com/flying-coyote/security-data-commons
- **Integration**: Anonymized architect decisions → blog posts (Phase 3)
- **Value**: Real-world case studies, community engagement, hypothesis validation

### Expert Network
- **Source**: second-brain expert network (1,444 thought leaders)
- **Integration**: Expert interviews validate vendor assessments
- **Value**: Practitioner feedback ensures real-world accuracy

## Related Projects

### Core Projects
- **[second-brain](https://github.com/flying-coyote/second-brain)**: Source of quality standards and methodology
- **[modern-data-stack-for-cybersecurity-book](https://github.com/flying-coyote/modern-data-stack-for-cybersecurity-book)**: Decision framework source (115,500 words)
- **[security-data-literature-review](https://github.com/flying-coyote/security-data-literature-review)**: Vendor data validation (75+ sources)
- **[security-data-commons-blog](https://github.com/flying-coyote/security-data-commons)**: Content generation target (3x/week)

## Technical Details

### Technology Stack
- **Language**: Python 3.10+
- **MCP SDK**: Anthropic MCP SDK 1.2.0+
- **Schema Validation**: Pydantic 2.0+
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Code Quality**: black, ruff, mypy
- **Deployment**: Claude Desktop (local MCP server)

### Development Dependencies
```bash
# Core dependencies
mcp>=1.2.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
httpx>=0.24.0
python-dotenv>=1.0.0

# Dev dependencies
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
black>=23.0.0
ruff>=0.1.0
mypy>=1.0.0
```

### Environment Setup
```bash
# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
ruff check src/ tests/
mypy src/
```

## Success Metrics

### Phase 1 Success (Immediate)
- [ ] 3 beta testers complete decision interview successfully
- [ ] Vendor landscape filtered 80 → 3-5 finalists
- [ ] Architecture reports generated with honest trade-offs
- [ ] Journey personas matched with 80%+ accuracy

### 12-Month Success (All Phases)
- [ ] 50-100 architects use MCP in Year 1
- [ ] Book sales driven by MCP funnel (30%+ conversion)
- [ ] 10-20 blog posts/year generated from MCP decisions
- [ ] Research portfolio enriched (5-10 new hypotheses discovered)

## Strategic Value

### For Architects
- **Time Savings**: 30 minutes vs. 2-4 weeks manual vendor evaluation
- **Decision Confidence**: Evidence-based filtering, validated by book research
- **Personalization**: Tailored to YOUR constraints, not generic best practices
- **Risk Mitigation**: Honest trade-off documentation prevents buyer's remorse

### For Book Project
- **Living Validation**: Captures real architectural decisions, validates hypotheses
- **Content Generation**: Decision conversations → blog posts, case studies
- **Community Engagement**: Interactive tool builds book community
- **Differentiation**: "First security architecture book with AI decision support companion"

### For Research Portfolio
- **Constraint Discovery**: What organizational constraints matter most?
- **Vendor Landscape Evolution**: Track which vendors gain/lose traction
- **Hypothesis Refinement**: Real-world validation of book's 29 hypotheses

## Current Priorities

### Immediate (Phase 1 Week 1-2)
1. **Project Setup** - Create src/, data/, tests/, docs/ structure
2. **MCP Hello World** - Basic server with one resource, tool, prompt
3. **Vendor Schema** - Pydantic model for vendor capabilities
4. **Initial Data** - 10 vendors entered manually (Dremio, Athena, Splunk, etc.)

### Short-term (Phase 1 Week 3-8)
1. **Filtering Logic** - Implement Tier 1 mandatory filters
2. **Scoring Logic** - Implement Tier 2 preferred capabilities (3× weight)
3. **Report Generator** - 12-15 page architecture recommendation (Markdown)
4. **Journey Matching** - Match to Jennifer/Marcus/Priya personas
5. **Decision Interview** - 12-step guided conversation prompt

### Medium-term (Phase 2-3, Month 3-6)
1. **Literature Review Integration** - IT Harvest API or web scraping
2. **Cost Calculator** - TCO projection tool
3. **Blog Content Generator** - Anonymized case studies
4. **Use Case Library** - Detection requirements mapping

## Next Session Priorities

When resuming work on this project, focus on:

1. **Project Setup** (if Phase 1 Week 1-2) - Create directory structure, MCP hello world
2. **Vendor Data Entry** (if setup complete) - Enter 10-80 vendors to database
3. **Tool Development** (if data ready) - Implement filtering and scoring logic
4. **Testing** (ongoing) - Write pytest tests for all tools
5. **Documentation** (ongoing) - Update SETUP.md, USAGE.md, ARCHITECTURE.md

## License

- **MCP Server**: Apache 2.0 (open source, permissive)
- **Vendor Database**: CC BY-SA 4.0 (Creative Commons Attribution-ShareAlike)
- **Book Integration**: Proprietary (book copyright retained, MCP server references only)

---

**Usage**: This file is loaded in every Claude Code conversation to provide consistent project context. Update when phase transitions occur, major milestones are completed, or implementation architecture changes.

**Last Updated**: October 15, 2025 (initialization with second-brain quality standards)
