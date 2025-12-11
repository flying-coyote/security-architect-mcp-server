# Security Architect MCP Server - Project Context

## Project Purpose
AI-powered interactive decision support tool transforming the "Modern Data Stack for Cybersecurity" book's decision framework into a conversational assistant that helps cybersecurity architects filter 80+ security data platforms to 3-5 personalized finalists in 30 minutes.

## Key Documentation Files

### PROJECT-BRIEF.md
**Purpose**: Complete project context using Memory Prompts Prompt 3 format - confirmed facts vs. assumptions, scope, constraints, risks
**Update Trigger**: Monthly at phase transitions (Phase 2 → Phase 3), quarterly vendor updates, major milestones
**Lifecycle**: PROJECT-SCOPED (5-6 months active development + ongoing maintenance)
**Note**: Separates canonical facts from assumptions requiring verification - critical for AI context

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
**Phase**: Phase 2 Complete → Phase 3 Ready (Web Tool Primary Focus)
**Last Updated**: December 11, 2025 (Progressive filtering + 82 vendors)
**Current Branch**: main
**Strategic Pivot**: Shifted from MCP server to interactive web tool as primary delivery mechanism

**Recent Achievement - Progressive Filtering + Vendor Expansion** (December 11, 2025):
✅ **Progressive Filtering Display** - Major UX enhancement showing filter impact
   - **Live Vendor Counts**: Each question displays how many vendors match after that filter
   - **Color-Coded Indicators**: Green (no change), Orange (1-19 eliminated), Red (20+ eliminated)
   - **Visual Feedback**: Users see which questions have biggest filtering impact
   - **Real-time Updates**: Counts update dynamically as user answers questions
   - **Technical**: Added `updateQuestionVendorCounts()`, CSS styling for 3 impact levels

✅ **Vendor Database Expansion** - 79 → 82 vendors with observability & detection focus
   - **Grafana Cloud** (new): Full observability + Cloud SIEM platform
     - 25M+ users, FedRAMP High, SOC2, ISO27001
     - Loki (logs) + Tempo (traces) + Mimir (metrics)
     - $25K-500K for 1-5TB/day
   - **Datadog** (updated): Enhanced with 2025 Cloud SIEM capabilities
     - 1000+ detection rules, MITRE ATT&CK mapping, 15-month retention
     - Gartner Leader (Observability 2024, 4th consecutive year)
     - Cloud SIEM $5/M events, CSM Pro $10/host/month
   - **Velociraptor** (new): Open-source endpoint visibility & DFIR
     - Rapid threat hunting, forensic artifact collection
     - Windows/Mac/Linux agents, Rapid7 support
     - $10K-100K for 1000 endpoints
   - **Zeek** (new): Network security monitoring (NSM) framework
     - 50+ log types, application-layer decoding, Corelight support
     - Microsoft Windows integration, industry standard NSM
     - $30K-300K for 10-100Gbps

   - **Live URL**: https://flying-coyote.github.io/security-architect-mcp-server/

**Previous Achievement - Web Tool Enhancements** (December 6, 2025):
✅ **Web Tool Expanded & Enhanced** - 79 vendors + interactive features
   - **Vendor Expansion**: 71 → 79 vendors (+8 from MCP database sync)
   - **Clickable Vendor List Modal**: Click vendor count to see all matching vendors
   - **Volume Context Added**: All costs show data volume capacity
   - Examples: "$100K-500K for 5TB/day", "$50K-300K for 1-5TB/day"

**Previous Achievement - MCP V3 Sync** (November 26, 2025):
✅ **Web Decision Tool V3 Production Deployed** - Sizing-first architecture + enhanced UX
   - **Live URL**: https://flying-coyote.github.io/security-architect-mcp-server/
   - **Sizing Constraints First** (S1-S4): Data volume (1 GB-100 TB), growth rate (0-300%), source count (1-500), retention (1d-7yr)
   - **Multi-Select Support**: Query engine (F4) and cloud environment (Q3) now allow multiple selections
   - **Budget Slider**: Replaced radio buttons with $50K-$50M logarithmic slider (Q2)
   - **Enhanced UX**: Deselectable radio buttons, real-time vendor filtering, slider markers
   - **Architecture-First Ordering**: S1-S4 sizing → F0-F4 foundational → Q1-Q4 constraints → Q5 use cases
   - **State Management**: Separated state buckets (sizingConstraints, foundationalAnswers, queryEngineCharacteristics, cloudEnvironments, useCases)
   - **Filtering Logic**: Multi-select questions now SCORE vendors instead of hard filtering (better UX for multi-cloud, multi-engine needs)
   - **Production Ready**: 75 vendors, 110 evidence sources, full report generation with TCO projections

**Previous Achievements - Sessions 2 & 3** (October 23, 2025):
1. ✅ **Evidence Backfill Complete** - Strategic correction over quantity inflation
   - Corrected evidence_summary metadata: 79 vendor-level sources (vs 184 aspirational counts)
   - Extracted 25 capability-level sources to vendor-level evidence_sources
   - Result: 110 total evidence sources (79 vendor + ~31 capability-level)
   - 84% Tier A quality (92/110 sources) - exceeds 60% target by 40%
2. ✅ **Vendor Expansion** - 6 high-quality additions (65 → 75 vendors)
   - Gurucul Next-Gen SIEM (Gartner MQ Leader 2025): UEBA + XDR + Identity Analytics
   - Palo Alto XSIAM (Forrester Strong Performer 2025): AI-driven, Cortex XDL lakehouse
   - SentinelOne Singularity (Gartner Endpoint Leader 2025): OCSF native SIEM + EDR
   - Apache Impala (Query Engine): NYSE, Quest Diagnostics production
   - Apache Paimon (Data Lakehouse): China Unicom 700 streaming tasks, 3× write, 7× query
   - Starburst Enterprise (Data Virtualization): 61% TCO savings
3. ✅ **Production Readiness Verified** - 0 blockers, database ready for MCP server
   - 75 vendors, 110 evidence sources, 84% Tier A quality
   - 46.5% analyst coverage (33/75 vendors with Gartner MQ/Forrester Wave)
   - 35.2% production validation (25/71 OSS vendors with Fortune 500 deployments)
   - Comprehensive quality review: Grade A (Excellent) - 92.7/100
4. ✅ **Blog Recommendations Updated** - Corrected metrics + new content opportunities
   - Updated vendor count 65 → 71, evidence 52 → 92 Tier A sources
   - Added 6 new vendors to evidence footnotes
   - Created Apache Paimon vs Iceberg comparison content
5. ✅ **Automation Operational** - Maintenance burden reduced 75-90%
   - Weekly refresh: Validates analyst URLs, checks for new publications
   - Monthly GitHub metrics: Tracks 24 OSS repos (stars, forks, contributors)
6. ✅ **MCP Server Production Deployment** (Session 3) - User verified working in Claude Desktop
   - Fixed schema validation error (maturity: "emerging" → "production")
   - All 7 tools, 1 resource, 2 prompts operational and accessible via Claude Desktop
   - User tested and confirmed: resources, tools, and prompts working
   - Ready for beta testing with security architects

**Previous Achievements - Session 1** (October 23, 2025):
1. Vendor Database Enrichment Complete - 52 Tier A evidence sources (100% enrichment quality)
2. TCO Calculator, vendor expansion 54 → 65, hidden cost modeling
3. 144 tests passing, 87% coverage, 7 MCP tools operational

**Previous Achievements** (October 16, 2025):
- TCO Calculator, vendor expansion to 64, cost modeling

**Next Immediate Work** (Web Tool Beta Testing Focus):
1. **Beta Testing Launch** (Priority: HIGH)
   - Recruit 3-5 security architects to test the 82-vendor web tool
   - Collect feedback on progressive filtering UX and vendor selection
   - Validate that progressive filtering helps decision-making
   - Assess if volume context and filter impact indicators are useful
2. **Usage Analytics** (Priority: MEDIUM)
   - Track which questions eliminate the most vendors
   - Identify common filtering paths (e.g., isolation pattern → table format → budget)
   - Document vendor combinations that emerge frequently
   - Measure time-to-decision (target: <30 minutes)
3. **Blog Content Generation** (Priority: MEDIUM)
   - Write case studies from beta tester decisions
   - Document common architect journeys (matches to Jennifer/Marcus/Priya personas)
   - Create vendor comparison content (e.g., "Grafana vs Datadog for SOC monitoring")
4. **Documentation Polish** (Priority: LOW)
   - Create SETUP.md for local development
   - Enhance USAGE.md with progressive filtering examples
   - Add FAQ section based on beta tester questions

## Project Architecture

### MCP Components

**Resources** (Data exposed to Claude):
1. Vendor Database - 82 security data platforms with capability matrix (9 categories)
   - 112+ evidence sources (84%+ Tier A quality)
   - 46.5% analyst coverage (33 vendors with Gartner MQ, Forrester Wave)
   - 35.2% production validation (25 OSS vendors with Fortune 500 deployments)
   - Enterprise-grade quality for CIO/CISO procurement decisions
   - Automated weekly refresh + monthly GitHub metrics tracking
2. Decision State - Current architect's conversation progress
3. Chapter Framework - Chapter 3-4 decision tree logic from book

**Tools** (Functions callable by Claude):
1. `list_vendors()` - Browse 82 vendors by category
2. `filter_vendors_tier1()` - Applies mandatory filters (team, budget, sovereignty)
3. `score_vendors_tier2()` - Scores vendors on preferred capabilities (3× weight)
4. `generate_architecture_report()` - Produces 8-12 page recommendation report
5. `match_journey_persona()` - Identifies Chapter 4 journey match (Jennifer/Marcus/Priya)
6. `calculate_tco()` - Projects 5-year Total Cost of Ownership with growth modeling
7. `compare_vendors_tco()` - Compare TCO across multiple vendors (ranked by total cost)

**Prompts** (Pre-written templates):
1. Decision Interview - 12-step guided questionnaire
2. Journey Matching - Explains persona match and architecture pattern

### Web Tool Architecture (PRIMARY DELIVERY)

**Deployment**: GitHub Pages at https://flying-coyote.github.io/security-architect-mcp-server/

**Technology Stack**:
- Vanilla JavaScript (no frameworks for simplicity)
- CSS Grid + Flexbox for responsive layout
- GitHub Pages for zero-infrastructure hosting
- Auto-deploy on git push to main branch

**Core Components**:

1. **index.html** - Main interface structure
   - Single-page application layout
   - Two-column design (questions + recommendations)
   - Modal overlay for vendor list
   - Responsive down to mobile

2. **decision-tree-v2.js** - Business logic (1,176 lines)
   - State management with separated buckets
   - Real-time filtering as questions answered
   - Modal interactions (open/close/populate)
   - Report generation functionality

3. **styles-v2.css** - UI styling (845 lines)
   - Modern gradient headers
   - Smooth animations and transitions
   - Hover effects and clickable indicators
   - Mobile-responsive breakpoints

4. **vendor_database.json** - Data source (82 vendors)
   - Synchronized with MCP server database
   - Volume context for all costs
   - 9 capability categories scored
   - Evidence sources tracked
   - Progressive filtering display integration

**Decision Flow Architecture**:
```
Phase 0: Sizing (S1-S4 sliders)
  ├─ Data volume: Eliminates vendors that can't handle scale
  ├─ Growth rate: Scores serverless/elastic higher
  ├─ Source count: Triggers ETL requirements
  └─ Retention: Drives storage tier choices

Phase 1: Foundational (F0-F4)
  ├─ Isolation pattern: Hard filter (shared vs dedicated vs BYOC)
  ├─ Table format: Establishes ecosystem (Iceberg vs Delta)
  ├─ Catalog: Locks in vendor bias (Unity, Polaris, etc)
  ├─ Transformation: dbt vs Spark vs vendor-specific
  └─ Query engine: Multi-select SCORES (not filters)

Phase 2: Organizational (Q1-Q4)
  ├─ Team size: 0-1 engineers → managed only
  ├─ Budget slider: $50K-$50M logarithmic
  ├─ Cloud environment: Multi-select SCORES
  └─ Vendor tolerance: OSS vs commercial preference

Phase 3: Use Cases (Q5)
  └─ Multi-select SCORES on specific needs
```

**Filtering Strategy**:
- **Hard Filters**: S1-S4, F0-F3, Q1-Q2, Q4 (eliminate vendors)
- **Scoring**: F4, Q3, Q5 (rank vendors with 1-3× weights)
- **Result**: 82 vendors → 3-5 finalists with ranked scores

**Interactive Features**:

1. **Progressive Filtering Display** (NEW - Dec 11, 2025)
   - Live vendor count at each question showing filter impact
   - Color-coded indicators: Green (no change), Orange (moderate), Red (high impact)
   - Helps users prioritize which questions to answer
   - Real-time feedback on filtering effectiveness

2. **Clickable Vendor List Modal**
   - Click "82 Vendors Match" to see full list
   - Filter summary explains why vendors match
   - Responsive grid with vendor cards
   - Click vendors to visit their websites
   - Close with X, ESC, or click outside

3. **Volume Context Display**
   - All costs show data capacity
   - Category-specific metrics (TB/day, tables, events)
   - Helps users understand value proposition
   - Examples: "$100K-500K for 5TB/day"

4. **Real-time Vendor Count**
   - Updates as each question answered
   - Shows filtering impact visually
   - Hover shows "Click to view all" hint

5. **Report Download**
   - Markdown format recommendation
   - Top 5 vendors with trade-offs
   - TCO projections included
   - Production examples cited

**State Management**:
```javascript
state = {
  sizingConstraints: {},      // S1-S4 slider values
  foundationalAnswers: {},    // F0-F3 architectural choices
  queryEngineCharacteristics: [], // F4 multi-select
  constraintAnswers: {},      // Q1, Q2, Q4
  cloudEnvironments: [],      // Q3 multi-select
  useCases: [],               // Q5 multi-select
  filteredVendors: [],        // Current matches
  vendorCount: 82,            // Live count
  vendorCountsByQuestion: {}  // Progressive filtering tracking
}
```

**Why Web Tool vs MCP Server**:
- **Accessibility**: No Claude Desktop required
- **Visual Feedback**: See vendors filter in real-time
- **Progressive Disclosure**: Build understanding step-by-step
- **Shareability**: Send URL to colleagues
- **Zero Installation**: Works in any browser
- **Mobile Support**: Responsive design works on phones

**Deployment Process**:
1. Edit files in docs/
2. `git add docs/ && git commit -m "Update web tool"`
3. `git push origin main`
4. GitHub Pages auto-deploys in 2-5 minutes

### Directory Structure

```
security-architect-mcp-server/
├── README.md (project overview)
├── ULTRATHINK-MCP-SERVER-DESIGN.md (comprehensive design doc)
├── pyproject.toml (Python dependencies)
├── src/
│   ├── server.py (✅ Main MCP server entry point)
│   ├── resources/ (✅ vendor_database.py, decision_state.py)
│   ├── tools/ (✅ filter, score, report, cost, journey)
│   ├── prompts/ (✅ decision_interview.py, journey_personas.py)
│   └── utils/ (✅ filters, scoring, report_generator)
├── data/
│   ├── vendor_database.json (✅ 82 vendors operational)
│   ├── decision_states/ (session persistence)
│   └── chapter_framework/ (decision tree logic)
├── tests/ (✅ 236 tests passing, 81% coverage)
├── docs/ (Web Tool - PRIMARY DELIVERY)
│   ├── index.html (✅ Main web interface)
│   ├── decision-tree-v2.js (✅ Filtering logic + progressive display)
│   ├── styles-v2.css (✅ UI styling + filter indicators)
│   ├── vendor_database.json (✅ 82 vendors)
│   ├── README.md (✅ Web tool documentation)
│   └── SETUP.md, USAGE.md (⏳ To be created)
├── scripts/
│   ├── add_volume_context.py (✅ Volume tier mapping)
│   └── sync scripts (✅ Literature review integration)
└── .claude/
    ├── CLAUDE.md (✅ This file)
    ├── sessions/ (✅ Work archives)
    └── skills/ (✅ 8 project skills)
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

### Phase 1: Core Decision Tree (Month 1-2) - **✅ COMPLETE**

**Deliverables**:
- ✅ MCP server basic structure (Python 3.10+, MCP SDK 1.2.0+)
- ✅ Vendor database (64 vendors across 9 categories, evidence-based)
- ✅ Decision interview prompt (12-step guided conversation)
- ✅ Filter/score tools (Tier 1-2 logic from Chapter 3)
- ✅ Architecture report generator (8-12 page Markdown output)
- ✅ Journey matching tool (Jennifer/Marcus/Priya personas)

**Completed**: October 16, 2025

**Success Criteria**:
- ✅ Vendor landscape filtered (64 → 3-5 finalists in <30 min)
- ✅ Architecture reports generated with honest trade-offs
- ✅ Journey personas matched with high accuracy
- ✅ 144 tests passing, 87% coverage

### Phase 2: Living Literature Review Integration (Month 3-4) - **✅ COMPLETE**

**Deliverables**:
- ✅ Cost calculator tool (5-year TCO projections with growth modeling)
- ✅ Vendor database expansion (54 → 79 vendors) - **8 vendors added Dec 6**
- ✅ **Analyst Evidence Enrichment + Evidence Backfill** (110 sources, 84% Tier A)
  - Phase 1: 18 commercial leaders (Gartner MQ, Forrester Wave)
  - Phase 2: 10 medium-priority commercial vendors
  - Phase 3: 24 OSS vendors (production deployments, adoption metrics)
  - Session 2: 6 vendor additions + evidence backfill (79 vendor-level sources corrected)
  - Result: 46.5% analyst coverage, 35.2% production validation, 84% Tier A quality
- ✅ **Automation Pipeline** - Weekly refresh + monthly GitHub metrics tracking
- ⏳ POC test suite generator (NEXT)
- ⏳ Quarterly vendor database update pipeline (automated refresh operational)
- ⏳ Hypothesis validation pipeline

**Progress**: 4/6 deliverables complete

**Timeline**: 5-7 weeks (90-130 hours total)

### Phase 3: Blog Integration & Content Generation (Month 5-6)

**Deliverables**:
- Blog post generator (decision conversation → anonymized case study)
- Use Case Library integration (detection requirements mapping)
- Expert interview synthesizer

**Timeline**: 4-5 weeks (75-105 hours total)

## Claude Skills

### Project-Specific Skills (2 skills)
This project has 2 specialized Claude Skills that activate automatically during MCP server development:

**mcp-schema-validator**:
- **Activates**: When validating schemas, adding tools/resources, or testing MCP server functionality
- **Validates**: JSON schema structure compliance, tool input schema validation (all properties have "type", enum non-empty), implementation consistency (tool code matches schema declarations), resource/tool/prompt schemas correct
- **Purpose**: Catches schema errors before runtime failures during Claude interactions
- **Location**: `.claude/skills/mcp-schema-validator/SKILL.md`

**vendor-data-quality-checker**:
- **Activates**: When adding/updating vendors, scoring capabilities, or maintaining vendor database
- **Validates**: No marketing hype in descriptions, capability scores (0-5) require Tier 1-3 evidence, all 9 capability categories scored, cost models accurate, production deployments documented, cross-referenced with book Chapter 5
- **Purpose**: Maintains evidence-based quality for 75-vendor database (expanding to 80), prevents marketing claims
- **Location**: `.claude/skills/vendor-data-quality-checker/SKILL.md`

### Personal Skills (6 universal skills)
All personal skills from `~/.claude/skills/` are available:
- **systematic-debugger**: 4-phase debugging for MCP runtime errors
- **tdd-enforcer**: RED-GREEN-REFACTOR for tool implementation
- **git-workflow-helper**: Conventional commits for MCP development
- **ultrathink-analyst**: Deep analysis of MCP architecture decisions
- **academic-citation-manager**: Evidence tier classification for vendor capabilities
- **voice-consistency-enforcer**: Maintains quality in documentation (no marketing hype)

### Workflow Integration

**Adding New Tool**:
1. **tdd-enforcer** → Write test for tool FIRST
2. Implement tool in src/tools/
3. **mcp-schema-validator** → Validate JSON schema
4. Run tests (tdd-enforcer enforces test-first)
5. **git-workflow-helper** → Commit with conventional message

**Adding/Updating Vendor**:
1. Research vendor capabilities (gather evidence)
2. **vendor-data-quality-checker** → Validate quality standards (evidence tier, no hype, all 9 capabilities scored)
3. **mcp-schema-validator** → Validate JSON structure
4. Cross-reference with book Chapter 5
5. **git-workflow-helper** → Commit vendor database update

**Schema Validation**:
1. Modify server.py, resources/, tools/, or prompts/
2. **mcp-schema-validator** → Run compliance check
3. Fix any issues flagged
4. **tdd-enforcer** → Ensure tests exist
5. Test with Claude desktop app

**Documentation**: See `.claude/skills/README.md` for complete skill descriptions and workflow patterns.

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
- **Vendor Database Sync**: Book Appendix D (Vendor Comparison Matrix) ↔ MCP vendors.json
- **Skills Coordination**:
  - **vendor-data-quality-checker** (MCP) validates evidence tiers for vendor scores
  - **appendix-content-generator** (Book) updates Appendix D when Chapter 5 changes
  - Both enforce same evidence requirements: Tier 1-3 for scores 5-4-3
- **Value**: Transforms static book content into interactive AI assistant with synchronized data

### Literature Review Integration
- **Repository**: https://github.com/flying-coyote/security-data-literature-review
- **Integration**: Vendor database sourced from 75+ validated sources (Phase 2)
- **Enrichment Status**: 110 evidence sources (84% Tier A quality = 92 Tier A sources)
  - Phase 1-3: 85 enrichment sources added (analyst reports + production deployments)
  - Evidence backfill: 25 capability-level sources extracted to vendor-level
  - 33 vendors with Gartner MQ/Forrester Wave, 25 OSS with Fortune 500 production
- **Sync Mechanism**: `scripts/sync_from_literature_review.py` - bidirectional sync with evidence validation
- **Automation**: Weekly refresh validates URLs, monthly GitHub metrics tracking (24 OSS repos)
- **Value**: Evidence-based vendor capabilities, validated cost models, enterprise-grade credibility

### Blog Integration
- **Repository**: https://github.com/flying-coyote/security-data-commons-blog
- **Blog URL**: https://securitydatacommons.substack.com
- **Status**: 43 posts (10 published, 33 drafted #11-43), 3x/week cadence (Mon/Wed/Fri)
- **MCP Featured**: Post #10 "Introducing the Security Architecture Decision Tool" (Oct 23, 2025)
- **Content Structure**: 7 waves optimized for narrative flow
  - Wave 1 (#11-16): Critical architecture decisions (Iceberg vs Delta, catalog, dbt, governance) - **Foundational decisions FIRST**
  - Wave 2 (#17-21): LIGER engine implementation (Netflix ClickHouse, Kafka-Iceberg, query engines, routing)
  - Waves 3-7 (#22-43): Detection maturity, OCSF strategy, anti-patterns, MLOps, federated enterprises
- **Strategic Insight**: Blog renumbering (Oct 30, 2025) revealed that foundational architecture decisions (table format, catalog choice) must precede implementation details (query engine, routing). This discovery should inform MCP decision interview flow redesign - ask foundational questions before constraint filtering completes vendor selection.
- **Integration** (Phase 3): Anonymized architect decisions → blog posts, validate blog frameworks with real MCP conversations
- **Value**: Real-world case studies, community engagement, hypothesis validation, content generation from MCP data

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
1. **Literature Review Integration** - Quarterly vendor database updates (automation operational)
2. **Cost Calculator** - TCO projection tool
3. **Blog Content Generator** - Anonymized case studies
4. **Use Case Library** - Detection requirements mapping

## Performance Optimization Insights

### Code Execution Pattern (December 2025)
**Source**: Second Brain intelligence capture - Anthropic's November 2025 engineering blog
**Impact**: 98.7% token reduction for bulk operations

**The Pattern**:
Instead of making sequential tool calls (80 vendors × 4 checks = 320 round trips), let the agent write code that processes all data in a single execution:

```python
# Old way: 150,000 tokens, 45-60 seconds, $2.25 per query
for vendor in range(80):
    result = mcp.call_tool("get_vendor", id=vendor)
    # ... multiple tool calls per vendor

# New way: 2,000 tokens, 2-3 seconds, $0.03 per query
code = """
finalists = [v for v in vendors
             if v.has_ocsf and v.cost < 500000]
return finalists[:10]
"""
result = mcp.execute_code(code)
```

**Security Implementation Required**:
1. AST validation (no dangerous operations)
2. Sandboxed namespace (limited access)
3. No builtins (no open, eval, etc.)
4. Timeout protection (30 second max)
5. Memory limits (256MB max)

**When to Apply**:
- Bulk filtering operations (all 75 vendors)
- Aggregate calculations (TCO for multiple vendors)
- Complex multi-condition queries
- Report generation across dataset

**Implementation Priority**: HIGH - Critical for production scale

### Other Intelligence from Second Brain (Dec 2025)

**NANDA (MIT Media Lab)**:
- DNS for AI agents - decentralized discovery/authentication
- 1,000+ agents registered, Databricks MLflow integration
- Relevance: Future MCP servers could register with NANDA for cross-vendor interoperability

**Governance Maturity Correlation**:
- 70% of AI projects fail due to data governance issues
- Level 3+ maturity required for >40% success rate
- Relevance: MCP server could assess organization's governance maturity before vendor selection

**RAPTOR Pattern (Gadi Evron)**:
- "Duct tape AI" - simple infrastructure that works
- 60-80% success rate acceptable for production
- Relevance: MCP server doesn't need perfection, just practical value

## Next Session Priorities

When resuming work on this project, focus on:

1. **Code Execution Implementation** (CRITICAL) - Add code execution pattern for 98.7% token reduction
2. **Vendor Database Expansion** (75 → 80 vendors) - Add remaining 5 vendors
3. **Beta Testing Launch** - Recruit 3-5 security architects
4. **Blog Content Generation** - Convert MCP decisions to case studies
5. **Documentation** (ongoing) - Update SETUP.md, USAGE.md, ARCHITECTURE.md

## License

- **MCP Server**: Apache 2.0 (open source, permissive)
- **Vendor Database**: CC BY-SA 4.0 (Creative Commons Attribution-ShareAlike)
- **Book Integration**: Proprietary (book copyright retained, MCP server references only)

---

**Usage**: This file is loaded in every Claude Code conversation to provide consistent project context. Update when phase transitions occur, major milestones are completed, or implementation architecture changes.

**Last Updated**: December 11, 2025 (Progressive filtering + 82 vendors)

**Recent Session**: Progressive Filtering + Vendor Expansion (Dec 11, 2025) - Implemented major UX enhancement with progressive filtering display showing live vendor counts at each question with color-coded impact indicators (green/orange/red). Added 3 new vendors: Grafana Cloud (observability + SIEM), Velociraptor (endpoint DFIR), Zeek (network monitoring). Updated Datadog with 2025 Cloud SIEM capabilities. Total vendor count: 79 → 82. All changes deployed to GitHub Pages. Web tool now provides real-time feedback on filtering effectiveness, helping users understand which questions have the biggest impact on vendor selection. Ready for beta testing with architects.
