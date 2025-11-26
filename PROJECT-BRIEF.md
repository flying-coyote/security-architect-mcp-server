# Security Architect MCP Server - Project Brief

**Created**: 2025-10-19
**Last Updated**: 2025-11-13
**Lifecycle**: PROJECT-SCOPED (duration: 5-6 months active development + ongoing maintenance)
**Methodology**: Memory Prompts Prompt 3 (Project Brief Compiler - 26 questions)
**Status**: PRODUCTION READY - Phase 2 Complete ✅ (237 tests passing, 100% pass rate, 87% coverage, Nov 13, 2025)

---

## Project Goal & Audience

### Objective
Transform "Modern Data Stack for Cybersecurity" book's Chapter 3-4 decision framework from static content into an interactive AI-powered MCP server that guides cybersecurity architects through a 30-minute conversation to filter 80+ security data platforms to 3-5 personalized finalists, producing comprehensive architecture recommendation reports with honest trade-offs, TCO projections, and POC evaluation criteria.

### Beneficiary
**Primary**: Cybersecurity architects evaluating security data platforms (mid-to-senior, 5-15 years experience, SOC leaders, security engineers)
**Secondary**: Book readers seeking to apply decision framework interactively (not manually over 2-4 weeks)
**Tertiary**: Research portfolio for hypothesis validation (29 hypotheses) and constraint discovery at scale (50-100 architect decisions/year)

### Success Criteria
**Phase 1 Complete** (✅ October 16, 2025):
- ✅ Architect completes decision interview in <30 minutes
- ✅ Vendor landscape filtered from 64 → 3-5 finalists
- ✅ Architecture reports generated with honest trade-offs (8-12 pages Markdown)
- ✅ Journey persona matched (Jennifer/Marcus/Priya) with high accuracy
- ✅ 178 tests passing, 88% code coverage

**Phase 2 Complete** (✅ November 13, 2025):
- ✅ Test suite 100% passing (237 tests, 87% coverage, 1.5s execution time)
- ✅ 2025 MCP best practices implemented (98.7% token reduction via code execution pattern, 90% context reduction via progressive discovery)
- ✅ Security hardening complete (5-layer security defense with AST-based code validation)
- ✅ TCO calculator operational (5-year projections with growth modeling)
- ✅ Vendor database expanded (54 → 75 vendors)
- ✅ 9 MCP tools operational (all production ready)
- ✅ **Production ready for beta testing**

**Phase 3 Goals** (Next priorities):
- ⏳ POC test suite generator (vendor-specific evaluation plans)
- ⏳ Vendor database reaches 80+ platforms (9 more vendors needed)
- ⏳ Automated vendor update pipeline (web scraping or community contributions)
- ⏳ Hypothesis validation pipeline (capture decisions → update confidence levels)

**12-Month Goals** (Year 1):
- 50-100 architects use MCP server
- Book sales driven by MCP funnel (30%+ conversion rate)
- 10-20 blog posts/year generated from anonymized MCP decisions
- 5-10 new hypotheses discovered from real architectural decisions

### Deliverable
**Primary**: Python MCP server (Model Context Protocol) for Claude Desktop integration
- 9 MCP tools: list_vendors, filter_tier1, score_tier2, generate_report, match_journey, calculate_tco, compare_tco, generate_poc_suite, execute_code
- 2 MCP resources: vendor_database (75 vendors), decision_state (session persistence)
- 2 MCP prompts: decision_interview (12-step), journey_matching (persona narratives)

**Secondary**: Vendor database (vendors.json) with 80+ security data platforms (capability matrix, cost models, evidence-based)

**Tertiary**: Architecture recommendation reports (8-12 pages Markdown, personalized finalists, TCO analysis, POC criteria, honest trade-offs)

---

## Scope & Boundaries

### In Scope
**Core Functionality**:
- MCP server implementation (Python 3.10+, Anthropic MCP SDK 1.2.0+)
- Vendor database (80+ platforms across 9 categories: SIEM, Query Engines, Lakehouses, Streaming, Virtualization, Catalogs, Ingestion, Observability, Security-Specific)
- Decision interview workflow (12-step guided conversation matching Chapter 3 framework)
- Filtering logic (Tier 1 mandatory: team capacity, budget, sovereignty, vendor tolerance)
- Scoring logic (Tier 2 preferred: 3× weight multiplier for preferred capabilities)
- Architecture report generation (finalists, rationale, trade-offs, TCO, POC criteria)
- Journey persona matching (Jennifer/Marcus/Priya patterns from Chapter 4)
- TCO calculator (5-year projections with growth modeling, platform/ops/hidden costs)
- POC test suite generator (vendor-specific evaluation plans with success criteria)

**Phase 2-3 Extensions**:
- Living Literature Review integration (automated vendor updates)
- Quarterly vendor database update pipeline
- Hypothesis validation pipeline (anonymized decisions → confidence updates)
- Blog post generator (decision conversations → anonymized case studies)
- Use Case Library integration (detection requirements → platform capability gaps)

### Out of Scope
**Excluded Functionality**:
- ❌ SaaS product (not commercial, research/book companion only)
- ❌ User authentication or multi-tenancy
- ❌ Web UI (Claude Desktop MCP client only)
- ❌ Real-time vendor data sync (quarterly updates sufficient)
- ❌ Advanced analytics dashboard (simple metrics only)
- ❌ Vendor advocacy or paid placements (vendor-neutral only)
- ❌ Production-grade scalability (private use, not public service)

**Strategic Boundaries**:
- NOT a vendor comparison site (Gartner/Forrester competitor)
- NOT a commercial product (open source, Apache 2.0)
- NOT vendor-funded (no sponsorships, pure research tool)
- NOT generic RFP automation (security data platforms only)

### Edge Cases & Boundary Conditions
**Vendor Database Staleness**:
- If >6 months stale → Display warning in reports, prompt quarterly update
- If vendor acquisition/sunset → Flag vendor as deprecated, suggest alternatives
- If automated updates unavailable → Fallback to manual quarterly updates
- Community contributions via GitHub PRs (vendor updates submitted by users)

**Architect Abandons Interview Mid-Stream**:
- Save decision_state.json after each question (session persistence)
- Resume prompt: "I see you were on question 8/12, let's continue..."

**Vendor Ties in Scoring**:
- If multiple vendors score identically → Include all ties in finalists (3-5 range elastic)
- Report explains tie-breaking considerations (cost, maturity, team expertise fit)

---

## Canonical Facts (Confirmed, Sources Required)

### Development Status
✅ **CONFIRMED**: Phase 1 complete (October 16, 2025)
- 178 tests passing, 88% code coverage
- 8 MCP tools operational
- Source: README.md line 120, .claude/CLAUDE.md line 28-34

✅ **CONFIRMED**: Phase 2 complete (November 13, 2025)
- 237 tests passing (100% pass rate), 87% code coverage
- 9 MCP tools operational (added execute_code with 2025 best practices)
- 2025 MCP patterns implemented (98.7% token reduction, 90% context reduction)
- Security hardening complete (5-layer defense with AST validation)
- Vendor database expanded (54 → 75 vendors, targeting 80)
- Production ready for beta testing
- Source: README.md, LAUNCH-PLAN.md, November 13, 2025 milestone

✅ **CONFIRMED**: 75 vendors in database across 9 categories (expanded from 64)
- Query Engines: 9 platforms (ClickHouse, Pinot, Rockset, PrestoDB, DuckDB, Dremio, Starburst, Snowflake, Athena)
- SIEM Platforms: 15 platforms (Splunk, Elastic, Sentinel, QRadar, Wazuh, Loki, Graylog, Sysdig, etc.)
- Open Source: 17+ platforms (24%)
- Cloud-Native: 47+ platforms (66%)
- Source: README.md, data/vendor_database.json, November 13, 2025 update

✅ **CONFIRMED**: Comprehensive design document exists (18,000 words)
- ULTRATHINK-MCP-SERVER-DESIGN.md with FRAME-ANALYZE-SYNTHESIZE methodology
- Complete architecture, implementation roadmap, success metrics
- Source: README.md line 297, ULTRATHINK-MCP-SERVER-DESIGN.md full document

### Book Integration
✅ **CONFIRMED**: Chapter 3-4 decision framework extracted from 115,500-word manuscript
- Three-tier hierarchy (Mandatory/Preferred/Nice-to-Have)
- Organizational constraints (Team/Budget/Sovereignty/Vendor)
- Filtering mechanism (80 → 10-15 → 3-5 → 1)
- Source: ULTRATHINK design doc lines 346-387, book manuscript

✅ **CONFIRMED**: Three journey personas defined (Chapter 4 patterns)
- Jennifer (Healthcare): HIPAA + 0-1 engineers + <$500K budget → Dremio hybrid recommendation
- Marcus (Financial Services): Cloud-first + 3 engineers + $2M-$4M budget → AWS Athena + Starburst recommendation
- Priya (Multi-national): Multi-cloud + GDPR/China + federated model → Denodo virtualization recommendation
- Source: ULTRATHINK design doc lines 358-385, Chapter 4 manuscript

✅ **CONFIRMED**: Book Appendix C integration planned
- "Interactive Decision Support Tool" setup guide for Claude Desktop
- Source: ULTRATHINK design doc lines 1514-1553

### Evidence-Based Requirements
✅ **CONFIRMED**: Vendor database sourced from validated evidence
- All entries cite 2025 sources (production deployments, expert interviews, vendor docs)
- Evidence tier system enforced (vendor-data-quality-checker skill)
- Cost models verified from public pricing pages
- Source: README.md line 223, .claude/CLAUDE.md lines 189-192

✅ **CONFIRMED**: Claude Skills infrastructure active
- 2 project-specific skills: mcp-schema-validator, vendor-data-quality-checker
- 6 personal skills: systematic-debugger, tdd-enforcer, git-workflow-helper, ultrathink-analyst, academic-citation-manager, voice-consistency-enforcer
- Source: .claude/CLAUDE.md lines 178-226

✅ **CONFIRMED**: Technology stack operational
- Python 3.10+, Anthropic MCP SDK 1.2.0+
- Pydantic 2.0+ for schema validation
- pytest with 237 tests passing (100%), 87% coverage, 1.5s execution time
- Source: .claude/CLAUDE.md, pyproject.toml, November 13, 2025 milestone

### Related Projects Integration
✅ **CONFIRMED**: Integration points defined
- Book manuscript (GitHub: modern-data-stack-for-cybersecurity-book) - Chapter 3-4 source, Appendix D vendor sync
- Blog (GitHub: security-data-commons-blog) - anonymized case studies (Phase 3)
- Literature Review (GitHub: security-data-literature-review) - vendor data validation (75+ sources)
- Source: .claude/CLAUDE.md lines 249-273

---

## Assumptions Requiring Verification

### Automated Vendor Database Updates
⚠️ **ASSUMPTION**: Automated vendor updates achievable through web scraping or APIs
- No confirmed automation approach as of October 19, 2025
- Assumption basis: Quarterly updates feasible with open-source tools
- **Verification needed**: Implement web scraping prototype by Month 4
- **Impact if false**: Manual quarterly updates required (increased maintenance burden 30-50%)

### Architect Adoption Targets
⚠️ **ASSUMPTION**: 50-100 architects will use MCP server in Year 1
- No baseline adoption data (new product launch)
- Assumption basis: Book readers (estimated 500-1,000), blog community (500 subscribers target)
- **Verification needed**: Track actual adoption Month 1-6, recalibrate if <10 users by Month 6
- **Impact if false**: Research hypothesis validation pipeline insufficient (need 50+ decisions for statistical significance)

⚠️ **ASSUMPTION**: 30%+ MCP users convert to book purchase
- No historical funnel data
- Assumption basis: MCP provides substantial value (30 min decision support), likely drives book interest
- **Verification needed**: Track conversion Month 1-12, survey MCP users about book purchase intent
- **Impact if false**: Book sales goal missed, recalibrate marketing strategy (focus blog over MCP)

### Content Generation Targets
⚠️ **ASSUMPTION**: 10-20 blog posts/year generated from anonymized MCP decisions
- Depends on: (1) Architect adoption (50-100/year), (2) Permission rate (20-30% grant anonymized case study rights)
- Assumption basis: 50 architects × 20% permission = 10 blog posts minimum
- **Verification needed**: Track permission rate Month 1-6, if <10% recalibrate target to 5-10 posts/year
- **Impact if false**: Blog content pipeline insufficient, more manual content creation required

### Vendor Database Maintenance Sustainability
⚠️ **ASSUMPTION**: 160-200 hours/year maintenance effort sustainable long-term
- Depends on: (1) Automation success (50% reduction if achieved), (2) Community contributions (30-50% reduction if materialize)
- Assumption basis: Quarterly updates (10-12 hours/quarter) + annual audit (68 hours) + user support (48-96 hours) = 160-200 hours
- **Verification needed**: Track actual maintenance time Year 1, if >300 hours recalibrate (reduce vendor count to top 30, increase update interval to bi-annual)
- **Impact if false**: Unsustainable maintenance burden, project abandonment risk

### Cost Projection Accuracy
⚠️ **ASSUMPTION**: TCO projections accurate within ±20%
- No validation against real deployments yet (need beta tester feedback)
- Assumption basis: Vendor pricing pages (public data), conservative estimates, ±20% disclaimer in reports
- **Verification needed**: Collect actual TCO data from 5-10 MCP users by Month 6, calibrate cost models
- **Impact if false**: Decision confidence undermined, architects distrust recommendations

### Journey Persona Match Accuracy
⚠️ **ASSUMPTION**: Journey matching (Jennifer/Marcus/Priya) achieves 80%+ accuracy
- No beta testing data yet (Phase 1 just completed October 16)
- Assumption basis: Decision tree logic validated against Chapter 4 journey narratives
- **Verification needed**: Beta test with 3 architects (healthcare, financial, multi-national contexts) by Month 3
- **Impact if false**: Persona matching unhelpful, remove from reports or redesign decision tree

---

## Prior Decisions & Rationale

### Decision 1: MCP Server (Not SaaS Web App)
**Decision**: Build as MCP server for Claude Desktop (not web-based SaaS)
**Rationale**:
- Research/book companion tool, not commercial product
- Avoid scalability/authentication/multi-tenancy complexity
- Claude Desktop handles UI, MCP handles business logic (simpler architecture)
- Open source model (Apache 2.0), anyone can self-host
- No operational burden (SaaS requires 24/7 uptime, support, billing)
**Made by**: Jeremy + ULTRATHINK analysis (October 14, 2025)
**Date**: October 14, 2025 (design phase)
**Reversible?**: Partially (could add web UI later, but MCP-first design validated)
**Source**: ULTRATHINK design doc lines 141-149

### Decision 2: Python (Not TypeScript) for Implementation
**Decision**: Python 3.10+ as primary language (not TypeScript)
**Rationale**:
- Faster development (rich libraries: Pydantic, pytest, Jinja2)
- Better data science libraries (if analytics needed later)
- Easier integration with existing knowledge base (all markdown, Python automation scripts)
- MCP SDK supports both, Python preferred for research tool
**Made by**: Jeremy
**Date**: October 14, 2025 (design phase)
**Reversible?**: No (rewrite cost too high mid-project, 178 tests already passing)
**Source**: ULTRATHINK design doc lines 613-623

### Decision 3: Evidence-Based Vendor Database (No Marketing Hype)
**Decision**: All vendor capabilities require Tier A/B/C evidence (documented sources, not marketing claims)
**Rationale**:
- Credibility depends on honest vendor assessment
- Vendor neutrality requires equal treatment (no sponsorships)
- vendor-data-quality-checker skill enforces standards automatically
- Aligns with book's intellectual honesty brand (profile-and-preferences.md)
**Made by**: Jeremy (evidence tier system from Second Brain project)
**Date**: Pre-October 2025 (inherited from book quality standards)
**Reversible?**: No (core to project credibility, compromising = project failure)
**Source**: .claude/CLAUDE.md lines 189-192, vendor-data-quality-checker skill

### Decision 4: Quarterly Vendor Database Updates (Not Monthly)
**Decision**: Update vendor database quarterly (Jan/Apr/Jul/Oct), not monthly or continuous
**Rationale**:
- Vendor capabilities change slowly (quarterly cadence sufficient)
- Monthly updates unsustainable (4× maintenance burden)
- Continuous updates infeasible (no real-time API access currently available)
- Timestamp displayed in reports (users aware of staleness)
**Made by**: Jeremy
**Date**: October 14, 2025 (ULTRATHINK analysis sustainability section)
**Reversible?**: Yes (if automation achieves better than expected results, could move to monthly)
**Source**: ULTRATHINK design doc lines 1743-1781

### Decision 5: Three-Tier Requirement Hierarchy (Mandatory/Preferred/Nice-to-Have)
**Decision**: Implement Chapter 3's three-tier filtering logic (Tier 1 mandatory eliminates vendors, Tier 2 preferred scores with 3× weight, Tier 3 nice-to-have informational only)
**Rationale**:
- Validated by book research (tested across 3 journey personas)
- Avoids "all requirements equal" problem (80 vendors all score identically)
- Prevents feature-creep prioritization (architects forced to choose mandatory vs preferred)
- 3× weight multiplier gives preferred capabilities meaningful impact without overwhelming mandatory filters
**Made by**: Book manuscript (Chapter 3), extracted to MCP design
**Date**: Book manuscript 2024-2025, MCP extraction October 2025
**Reversible?**: No (foundational to filtering logic, changing breaks Chapter 3 alignment)
**Source**: ULTRATHINK design doc lines 346-387, book Chapter 3

### Decision 6: Journey Persona Matching (Jennifer/Marcus/Priya, Not Generic)
**Decision**: Match architects to specific Chapter 4 journey personas (Jennifer/Marcus/Priya) rather than generic recommendations
**Rationale**:
- Personalization requires context-specific guidance (healthcare ≠ financial ≠ multi-national)
- Chapter 4 already documents three validated journeys (real deployments)
- Persona matching builds narrative continuity (book readers recognize their journey)
- Generic recommendations lack actionable specificity ("it depends" unhelpful)
**Made by**: Book manuscript (Chapter 4), extracted to MCP design
**Date**: Book manuscript 2024-2025, MCP extraction October 2025
**Reversible?**: Partially (could add more personas, but Jennifer/Marcus/Priya core set validated)
**Source**: ULTRATHINK design doc lines 358-385, book Chapter 4

### Decision 7: Honest Trade-Offs Documented (Not Just Benefits)
**Decision**: Architecture reports MUST document what each platform does NOT solve (limitations, trade-offs)
**Rationale**:
- Prevents buyer's remorse (architects aware of limitations before POC)
- Differentiation from vendor marketing (honest assessment)
- Intellectual honesty brand alignment (profile-and-preferences.md standards)
- Multi-path validation (Dremio, Athena, Splunk, Denodo all valid in correct context)
**Made by**: Jeremy (Second Brain quality standards)
**Date**: Pre-October 2025 (inherited from evidence-based reasoning standards)
**Reversible?**: No (core to credibility, omitting = vendor advocacy perception)
**Source**: ULTRATHINK design doc lines 996-1003, profile-and-preferences.md

---

## Pending Decisions

### Decision 1: Vendor Database Update Automation Approach
**Question**: What automation approach should be used for vendor database updates?
**Options**:
- Option A: Build web scraping automation (vendor websites → capability updates, 30-40 hours development)
- Option B: Reduce vendor scope (80 → top 30 most common platforms, focus depth over breadth)
- Option C: Community contribution model (GitHub PRs for vendor updates, minimal automation)
**Trade-offs**:
- Option A: Higher development cost, ongoing scraping maintenance, legal/ethical concerns (terms of service violations?)
- Option B: Reduced value (missing niche vendors), faster maintenance (30 vendors = 50% effort reduction)
- Option C: Unpredictable quality (community may not materialize), low cost
**Decision needed by**: Month 4 (December 2025)
**Blocking**: Phase 2 completion (quarterly update pipeline depends on data source)

### Decision 2: POC Test Suite Generator - Vendor-Specific or Generic?
**Question**: Generate vendor-specific POC scripts (Dremio/Athena/Starburst each unique) or generic evaluation template?
**Options**:
- Option A: Vendor-specific scripts (SQL queries tailored to platform syntax, load tests, operational tasks)
- Option B: Generic template (architect fills in vendor-specific details manually)
- Option C: Hybrid (generic template with vendor-specific examples/guidance)
**Trade-offs**:
- Option A: Higher value (directly executable), 80+ vendor scripts to maintain, high development cost
- Option B: Lower value (more work for architect), minimal maintenance, fast development
- Option C: Balanced value/cost, 30-40 hours development, moderate maintenance
**Decision needed by**: Month 3 (November 2025) - POC generator is Phase 2 next deliverable
**Blocking**: No (can start with Option B, enhance to Option C later)

### Decision 3: Beta Testing - Approach and Recruitment
**Question**: What approach should be used for beta testing with security architects?
**Options**:
- Option A: Recruit from professional network (3-5 beta testers from existing relationships)
- Option B: External recruitment (blog readers, LinkedIn community, 5-10 testers)
- Option C: Hybrid (1-2 from network + 3-5 external)
**Trade-offs**:
- Option A: High-quality feedback (detailed critiques), limited diversity (similar backgrounds)
- Option B: Diverse perspectives (healthcare/financial/multi-national validated), lower quality feedback (may not complete interview)
- Option C: Balanced quality/diversity, coordination overhead
**Decision needed by**: Month 2 (end of Phase 1, October 2025) - beta testing starts after Phase 1 complete
**Blocking**: No (Phase 1 already complete October 16, can beta test now)

### Decision 4: Hypothesis Validation Pipeline - Manual or Automated?
**Question**: Extract hypothesis validation from MCP decisions manually (human review each decision) or automate (decision_state.json → hypothesis confidence updates)?
**Options**:
- Option A: Manual extraction (human reviews each decision, updates MASTER-HYPOTHESIS-TRACKER.md)
- Option B: Automated pipeline (decision_state.json parsed, confidence levels updated algorithmically)
- Option C: Semi-automated (algorithm suggests updates, human approves)
**Trade-offs**:
- Option A: Higher quality (human judgment), unsustainable at 50-100 decisions/year (2-4 hours/decision = 100-400 hours/year)
- Option B: Scalable, lower quality (algorithm may miss nuance), 40-50 hours development
- Option C: Balanced quality/scalability, 50-60 hours development + 50-100 hours/year review
**Decision needed by**: Month 5 (January 2026) - Phase 2 deliverable
**Blocking**: No (hypothesis validation nice-to-have, not core functionality)

---

## Constraints & Non-Negotiables

### Technical Constraints
**Non-Negotiable**: Python 3.10+ (no downgrade to 3.8/3.9)
- Rationale: Type hints, pattern matching, structural pattern matching require 3.10+
- Consequences if violated: Code refactor (50+ hours), lose modern Python features
- No exceptions: Already 178 tests passing on Python 3.10

**Non-Negotiable**: MCP SDK 1.2.0+ compatibility
- Rationale: Claude Desktop integration requires current MCP protocol
- Consequences if violated: MCP server won't load in Claude Desktop
- Mitigation: Track Anthropic MCP SDK releases, upgrade as needed

**Non-Negotiable**: 80%+ test coverage minimum
- Rationale: Decision logic must be validated (architect decisions depend on correctness)
- Consequences if violated: Production bugs undermine credibility
- Current status: 88% coverage (exceeds minimum)
- No exceptions: All new tools require tests before merge

### Quality Standards (Non-Negotiable)
**Vendor Neutrality**: No vendor sponsorships accepted
- Rationale: Credibility depends on honest assessment (vendor-funded = biased)
- Consequences if violated: Loss of trust, project abandonment by community
- No exceptions: Vendor updates via GitHub PRs acceptable, but cannot influence scoring logic

**Evidence-Based Claims**: All vendor capabilities require documented sources (Tier A/B/C evidence)
- Rationale: vendor-data-quality-checker skill enforces automatically
- Consequences if violated: Marketing hype perception, loss of credibility
- No exceptions: Tier D/5 (speculation/personal experience) not acceptable for vendor database

**Honest Trade-Offs**: Architecture reports MUST document limitations (what platform does NOT solve)
- Rationale: Prevents buyer's remorse, differentiates from vendor marketing
- Consequences if violated: Architect dissatisfaction, negative reviews
- No exceptions: Every vendor recommendation includes "What This Architecture Does NOT Solve" section

### Project Scope Constraints
**Non-Negotiable**: Research tool only (NOT SaaS product)
- Rationale: Avoid commercial product complexity (authentication, billing, scalability, 24/7 uptime)
- Consequences if violated: Scope creep, unsustainable operational burden
- No exceptions: If demand overwhelming, license to third-party (book receives royalty, no operational burden)

**Non-Negotiable**: Open source (Apache 2.0 license)
- Rationale: Transparency (scoring algorithms auditable), community contributions, vendor neutrality
- Consequences if violated: Proprietary perception, vendor advocacy suspicion
- No exceptions: Vendor database CC BY-SA 4.0 (share-alike prevents proprietary forks)

### Maintenance Constraints
**Non-Negotiable**: 200 hours/year maximum maintenance effort (sustainable at 20% FTE)
- Rationale: Solo practitioner with concurrent projects (book, blog, MCP server, Claude Skills, expert interviews)
- Consequences if violated: Project abandonment, vendor database stale (credibility loss)
- Mitigation: If exceeds 200 hours, reduce vendor scope (80 → top 30), increase update interval (quarterly → bi-annual)

---

## Acceptance Criteria & Quality Bar

### Phase 1 Completion Criteria (✅ Achieved October 16, 2025)
**Minimum Success**:
- ✅ Architect completes decision interview in <30 minutes
- ✅ Vendor landscape filtered from 64 → 3-5 finalists
- ✅ Architecture reports generated (8-12 pages Markdown)
- ✅ Journey persona matched (Jennifer/Marcus/Priya)
- ✅ 150+ tests passing, 80%+ coverage

**Achieved** (Exceeded minimum):
- ✅ 178 tests passing (vs 150 minimum)
- ✅ 88% coverage (vs 80% minimum)
- ✅ 8 MCP tools operational (vs 5 planned)
- ✅ TCO calculator functional (Phase 2 deliverable completed early)

### Phase 2 Completion Criteria (✅ Complete, November 13, 2025)
**Achieved** (Core infrastructure complete):
1. ✅ Test suite 100% passing (237 tests, 87% coverage, 1.5s execution)
2. ✅ 2025 MCP best practices implemented (98.7% token reduction, 90% context reduction)
3. ✅ Security hardening complete (5-layer defense, AST validation)
4. ✅ Cost calculator tool (5-year TCO projections with growth modeling)
5. ✅ Vendor database expansion (54 → 75 vendors)
6. ✅ 9 MCP tools operational (all production ready)
7. ✅ **Production ready for beta testing**

**Phase 3 Priorities** (Next development cycle):
- ⏳ POC test suite generator (vendor-specific evaluation plans)
- ⏳ Vendor database reaches 80 platforms (9 more vendors)
- ⏳ Automated vendor update pipeline (web scraping or community contributions)
- ⏳ Hypothesis validation pipeline (capture decisions → update confidence)

### 12-Month Completion Criteria (All Phases)
**Minimum Success** (3/5 criteria required):
1. ✅ 30+ architects use MCP in Year 1 (60% of target)
2. ✅ 15%+ book sales conversion from MCP users (50% of target)
3. ✅ 5-10 blog posts/year from MCP decisions (50% of target)
4. ✅ 2-3 new hypotheses discovered (40% of target)
5. ✅ Maintenance burden <250 hours/year (125% of target, acceptable)

**Excellent Success** (5/5 criteria met):
- 50-100 architects, 30%+ conversion, 10-20 blog posts, 5-10 hypotheses, <200 hours/year

### Quality Bar: Good Enough vs. Excellent

**Good Enough** (shippable):
- MCP server loads in Claude Desktop without errors
- Vendor database has 64+ vendors with complete capability matrix
- Decision interview completes in 30 minutes average
- Architecture reports generate in <10 seconds
- Test coverage 80%+ (current: 88%)
- Documentation (README, SETUP, USAGE) complete

**Excellent** (aspirational):
- Vendor database 80+ vendors (comprehensive coverage)
- Decision interview feels conversational (not rigid form)
- Architecture reports include personalized journey guidance (not generic)
- POC test suites directly executable (not just templates)
- Test coverage 90%+ (current: 88%, close)
- Validation from production deployments and beta testers

**Critical Defects** (block release):
- ❌ MCP server crashes during interview (unrecoverable errors)
- ❌ Vendor filtering logic incorrect (violates Chapter 3 decision tree)
- ❌ Cost projections >50% inaccurate (undermines decision confidence)
- ❌ Journey persona matching <50% accurate (unhelpful guidance)
- ❌ Architecture reports missing trade-offs section (vendor advocacy perception)

---

## Risks, Unknowns & Blockers

### High-Probability Risks

**Risk 1: Automated Vendor Updates Not Achieved (Likelihood: MEDIUM, 50%)**
- **Impact**: Manual quarterly updates required (increased maintenance 30-50%)
- **Indicators**: Web scraping proves infeasible, community contributions insufficient
- **Mitigation**: Community contribution model (GitHub PRs), reduce vendor scope (80 → top 30)
- **Contingency**: If >250 hours/year maintenance, reduce update frequency (quarterly → bi-annual) or vendor count (80 → 50 → 30)

**Risk 2: Architect Adoption Lower Than Projected (Likelihood: MEDIUM)**
- **Impact**: Hypothesis validation pipeline insufficient (<50 decisions = no statistical significance), blog content pipeline insufficient (<5 posts/year)
- **Indicators**: <10 architects by Month 6, <30 by Month 12
- **Mitigation**: Increase marketing (blog posts, conference speaking), simplify setup (one-click Claude Desktop install)
- **Contingency**: Recalibrate targets (50-100 → 20-50 architects), extend timeline (Year 1 → Year 2)

**Risk 3: Vendor Database Staleness (Likelihood: HIGH)**
- **Impact**: Stale recommendations (vendor capabilities changed), decision confidence undermined
- **Indicators**: >6 months since last vendor update, community reports outdated data
- **Mitigation**: Timestamp prominently displayed in reports ("Data current as of [date]"), blog posts announcing major vendor changes between quarterly updates
- **Contingency**: If unsustainable, reduce update frequency (quarterly → bi-annual), focus top 30 vendors only

### Medium-Probability Risks

**Risk 4: Cost Projection Inaccuracy (Likelihood: MEDIUM)**
- **Impact**: TCO projections >±30% off (architects distrust recommendations)
- **Indicators**: Beta testers report actual costs differ significantly, vendor pricing changes not captured
- **Mitigation**: ±20% accuracy disclaimer in reports, link to vendor pricing pages, validate with 5-10 real deployments
- **Contingency**: If >50% inaccurate, remove TCO calculator entirely (better no data than bad data)

**Risk 5: Vendor Advocacy Perception (Likelihood: LOW-MEDIUM)**
- **Impact**: Community perceives MCP as biased toward certain vendors (trust erosion)
- **Indicators**: Reddit/LinkedIn comments alleging bias, vendor-specific complaints
- **Mitigation**: Multi-path validation (Dremio, Athena, Splunk, Denodo all valid in correct context), honest trade-offs (what each does NOT solve), transparent scoring (open source algorithms), vendor neutrality policy (no sponsorships)
- **Contingency**: Publish transparency report (vendor update changelog, scoring algorithm explanation, evidence sources)

### Unknowns Requiring Research

**Unknown 1: Beta Tester Conversion Rate (Architects → Users)**
- **Why it matters**: Determines adoption targets feasibility (50-100 architects/year achievable?)
- **Research needed**: Recruit 5-10 beta testers by Month 3, track completion rate (start interview → complete report)
- **Decision impact**: If <50% completion rate, simplify interview (12 steps → 6 steps), improve UX (clearer progress indicators)

**Unknown 2: Journey Persona Match Accuracy (Real-World)**
- **Why it matters**: If <60% accurate, persona matching unhelpful (remove from reports or redesign)
- **Research needed**: Beta test with 3 architects (healthcare, financial, multi-national), validate Jennifer/Marcus/Priya match accuracy
- **Decision impact**: If inaccurate, redesign decision tree or add 4th persona (hybrid journey)

**Unknown 3: Actual Maintenance Burden (Quarterly Updates)**
- **Why it matters**: 200 hours/year sustainable? Or exceeds capacity?
- **Research needed**: Track actual hours Quarter 1-2 (Jan-Jun 2026), measure vendor update time, bug fix time, user support time
- **Decision impact**: If >250 hours/year, reduce vendor scope (80 → 50 → 30) or increase update interval (quarterly → bi-annual)

**Unknown 4: Community Contribution Viability**
- **Why it matters**: Can community sustain vendor updates (GitHub PRs), or requires full-time maintainer?
- **Research needed**: Monitor GitHub PR activity Month 6-12, measure community engagement (stars, forks, issues, PRs)
- **Decision impact**: If no community contributions by Month 12, maintenance unsustainable (recalibrate scope or abandon)

### Potential Blockers

**Blocker 1: MCP SDK Breaking Changes**
- **Scenario**: Anthropic releases MCP SDK 2.0 with incompatible protocol changes
- **Probability**: LOW (SDK 1.2.0 stable)
- **Impact**: MCP server broken, 20-40 hours refactor required
- **Mitigation**: Pin MCP SDK version (mcp>=1.2.0,<2.0.0), monitor Anthropic releases, upgrade incrementally
- **Escalation**: If breaking change unavoidable, pause Phase 2-3 development (refactor takes priority)

**Blocker 2: Vendor Database Legal Challenge**
- **Scenario**: Vendor claims copyright infringement (vendor database violates terms of service)
- **Probability**: LOW (public data, fair use research)
- **Impact**: Vendor data removal, capability matrix gaps
- **Mitigation**: CC BY-SA 4.0 license (share-alike), document public sources, fair use research exemption
- **Escalation**: Remove challenged vendor from database, legal consultation if multiple vendors challenge

**Blocker 3: Beta Tester Unavailability**
- **Scenario**: Cannot recruit 3 beta testers (healthcare, financial, multi-national contexts)
- **Probability**: LOW-MEDIUM (professional network available, but availability uncertain)
- **Impact**: Phase 1 validation incomplete, journey persona matching unvalidated
- **Mitigation**: Recruit from blog community (LinkedIn promotion), offer value proposition (free architecture report), extend timeline (Month 2 → Month 4)
- **Escalation**: If no beta testers by Month 4, self-test with synthetic personas (lower confidence)

---

## Context for AI

### Help Needed (What AI Should Assist With)

**Development Support**:
- MCP server implementation (tool definitions, resource management, prompt templates)
- Vendor database JSON schema validation (Pydantic models, type safety)
- Test-driven development (pytest fixtures, async test patterns)
- Architecture report generation (Jinja2 templates, Markdown formatting)
- TCO calculation algorithms (growth modeling, cost model-aware scaling)

**Data Management**:
- Vendor database expansion (research 16 more vendors to reach 80 target)
- Capability matrix validation (cross-reference with book Chapter 5, expert interviews)
- Evidence tier classification (Tier A/B/C sources for vendor capabilities)
- Cost model accuracy (verify vendor pricing pages, update quarterly)

**Quality Assurance**:
- mcp-schema-validator skill enforcement (JSON schema compliance, tool/resource/prompt validation)
- vendor-data-quality-checker skill enforcement (evidence tier, no marketing hype, all 9 capabilities scored)
- Test coverage maintenance (80%+ required, currently 88%)
- Honest trade-offs documentation (every vendor recommendation includes limitations section)

**Integration Work**:
- Book Appendix D vendor sync (MCP vendors.json ↔ book Appendix D)
- Blog content generation (anonymized case study templates from decision_state.json)
- Hypothesis validation pipeline (decision patterns → confidence level updates)

### Domain Background AI Needs

**MCP Protocol Context**:
- Model Context Protocol (MCP) = Anthropic's standard for AI-accessible data/tools
- MCP server exposes: Resources (file-like data), Tools (callable functions), Prompts (pre-written templates)
- Claude Desktop = MCP client (architect interacts with Claude, Claude calls MCP server)
- Session persistence via decision_state.json (MCP itself stateless)

**Book Decision Framework Context**:
- Chapter 3: Three-tier requirement hierarchy (Mandatory filters → Preferred scoring → Nice-to-have informational)
- Chapter 4: Three journey personas (Jennifer/Healthcare, Marcus/Financial, Priya/Multi-national)
- Organizational constraints: Team capacity (0-1, 2-3, 3-5, 5+ engineers), Budget (<$500K, $500K-$2M, $2M-$10M, $10M+), Data sovereignty (cloud-first, hybrid, on-prem-only, multi-region), Vendor tolerance (OSS-first, OSS-with-support, commercial-only)
- Filtering mechanism: 80 vendors → Tier 1 filters (mandatory) → 10-15 viable → Tier 2 scoring (3× weight) → 3-5 finalists

**Evidence Tier System** (from Second Brain):
- Tier A: Academic peer-reviewed, official standards (NIST, ISO, OCSF spec)
- Tier B: Industry practitioners (production deployments, expert interviews, conference talks)
- Tier C: Blog posts, vendor marketing, unvalidated claims
- Tier D: Speculation, hypotheses (not acceptable for vendor database)
- Tier 5: Personal experience (must be labeled "I observed...", not generalizable)

**Vendor Database Structure**:
- 64 vendors (expanding to 80+) across 9 categories
- Capability matrix: SQL interface, open table format, deployment models, operational complexity, cost model, maturity, vendor support
- Tier 1 mandatory: SQL support, multi-source integration, time-series partitioning
- Tier 2 preferred: Iceberg-native, multi-engine query, OCSF support, streaming ingestion
- Cost estimates: Per-TB/month, per-query, subscription, open-source (free), hybrid
- Evidence sources: Book hypotheses, production deployments, peer-reviewed research

**Related Projects Context**:
- **Book** (modern-data-stack-for-cybersecurity-book): 115,500 words, Chapter 3-4 decision framework source, Appendix D vendor comparison matrix
- **Blog** (security-data-commons-blog): 3x/week publication, anonymized case studies target (10-20 posts/year from MCP)
- **Literature Review** (security-data-literature-review): 75+ validated sources, vendor capability validation
- **Second Brain** (project1): Quality standards source (evidence tier, intellectual honesty, voice consistency)

**Claude Skills Context**:
- **mcp-schema-validator**: Catches JSON schema errors (tool input schema validation, resource/tool/prompt compliance)
- **vendor-data-quality-checker**: Enforces evidence-based quality (no marketing hype, capability scores require Tier 1-3 evidence, all 9 categories scored)
- **tdd-enforcer**: RED-GREEN-REFACTOR cycle (write test FIRST, then implement tool)
- **systematic-debugger**: 4-phase debugging (reproduce → isolate → identify → resolve) for MCP runtime errors

**Phase Status**:
- Phase 1 ✅ COMPLETE (October 16, 2025): 178 tests passing, 88% coverage, 8 tools operational
- Phase 2 ✅ COMPLETE (November 13, 2025): 237 tests passing (100%), 87% coverage, 9 tools operational, 2025 best practices implemented, security hardening complete, production ready
- Phase 3 ⏳ NEXT: POC generator, vendor expansion to 80, automated updates, hypothesis validation, blog integration

---

## Token Count & Format Optimization

**Estimated Token Count**: ~10,000 tokens (this document)
**Reusability**: PROJECT-SCOPED (applicable for 5-6 months active development + ongoing maintenance years)
**Update Frequency**: Monthly at phase transitions (Phase 2 → Phase 3 transition, quarterly vendor updates)

**Optimization Notes**:
- Canonical Facts section comprehensive (13 confirmed items with sources)
- Assumptions section extensive (7 items flagged for verification with decision impact)
- Prior Decisions include detailed rationale (7 major decisions documented)
- Pending Decisions explicit (4 decisions with trade-offs and timelines)
- Risks section thorough (5 high/medium risks, 4 unknowns, 3 blockers)

---

## Verification Checklist (Pre-Use)

Before using this project brief, verify:
- [ ] Phase 2 status updated (check README.md for deliverable count)
- [ ] Test coverage current (run pytest, confirm 80%+)
- [ ] Vendor count accurate (check data/vendor_database.json)
- [ ] Automation approach status updated (check if web scraping or community model selected)
- [ ] Beta tester recruitment status (if Phase 1 complete, recruit 3-5 testers)
- [ ] POC test suite generator scope decided (vendor-specific vs generic template)

**Last Verified**: 2025-10-19 (project brief creation)
**Next Verification**: 2025-11-19 (Month 3, Phase 2 completion check)

---

## Changelog

**2025-11-13**: Phase 2 Complete - Production Ready Milestone
- Updated status: Phase 2 ✅ COMPLETE (test suite 100% passing, 237 tests, 87% coverage)
- Updated deliverables: 9 MCP tools operational (added execute_code with 2025 best practices)
- Updated vendor count: 75 vendors (expanded from 64)
- Added 2025 MCP patterns: 98.7% token reduction (code execution), 90% context reduction (progressive discovery)
- Added security hardening: 5-layer defense with AST-based code validation
- Updated canonical facts: Phase 2 complete with production-ready status
- Updated acceptance criteria: Phase 2 achievements documented, Phase 3 priorities defined
- Updated phase status: Phase 2 → complete, Phase 3 → next priorities

**2025-10-19**: Initial creation using Memory Prompts Prompt 3 (26-question methodology)
- Separated confirmed facts (13 items) from assumptions (7 items)
- Documented 7 prior decisions with rationale (MCP-not-SaaS, Python-not-TypeScript, evidence-based-vendors, quarterly-updates, three-tier-hierarchy, journey-personas, honest-trade-offs)
- Identified 4 pending decisions with trade-offs (automation approach, POC generator scope, beta testing approach, hypothesis validation automation)
- Mapped 6 non-negotiable constraints (Python 3.10+, MCP SDK 1.2.0+, 80%+ test coverage, vendor neutrality, evidence-based claims, honest trade-offs, research tool only, open source, 200 hours/year max maintenance)
- Defined 3-tier acceptance criteria (Phase 1 complete ✅, Phase 2 in progress 2/6, 12-month goals 3/5 required)
- Assessed 5 high/medium-probability risks + 4 unknowns + 3 blockers
- Provided comprehensive AI context (MCP protocol, book framework, evidence tier system, vendor database structure, related projects, Claude Skills, phase status)

**Next Update**: 2025-12-19 (Phase 3 progress check or major milestone)
