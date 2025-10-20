# MCP Hybrid Architecture - Decision Approved

**Date**: October 19, 2025
**Decision**: Option A - Hybrid Approach APPROVED
**Status**: Implementation Phase (3 weeks, November 2025)

---

## Decision Summary

**Recommendation Approved**: MCP Resources (data layer) + Claude Skills (workflow layer)

**Rationale**:
- Keep MCP Resources (vendor_database, decision_state) for protocol-level data standardization
- Convert 8 MCP Tools + 2 Prompts → 4 Claude Skills for workflow simplicity
- Apply Memory Prompts + Fabric patterns to Skills (40-60% efficiency gain target)
- Best of both worlds: Standardized data (MCP) + flexible workflows (Skills)

**Timeline**: 3 weeks (November 2025), 20-30 hours effort

**Expected Outcomes**:
- Simpler deployment (Claude Skills auto-discovery)
- Memory Prompts + Fabric integration (40-60% efficiency)
- Reduced maintenance burden (<180 hours/year vs 200 hours/year)
- Increased architect adoption (30-50 target vs <20 MCP-only)

---

## Implementation Plan

### Week 1 (Nov 2-8): MCP Server Simplification

**Objective**: Remove Tools/Prompts, keep Resources only

**Tasks**:
1. Remove 8 MCP Tools from server code:
   - list_vendors
   - filter_tier1
   - score_tier2
   - generate_report
   - match_journey
   - calculate_tco
   - compare_tco
   - generate_poc_suite

2. Remove 2 MCP Prompts:
   - decision_interview
   - journey_matching

3. Keep 2 MCP Resources:
   - vendor_database (vendors.json)
   - decision_state (decision_state.json)

4. Test: MCP server loads with Resources only (no errors)

**Deliverable**: Simplified MCP server (data layer only)

**Estimated Time**: 8-10 hours

---

### Week 2 (Nov 9-15): Claude Skills Creation

**Objective**: Create 4 skills with 10-section standardized template

**Skills to Create**:

#### 1. security-vendor-filter

**Purpose**: Apply Tier 1 mandatory filters + Tier 2 preferred scoring
**Input**: Architect requirements (team, budget, sovereignty, vendor tolerance, preferred capabilities)
**Output**: 3-5 finalist vendors with scores

**10-Section Template**:
1. IDENTITY: Vendor filtering specialist for security data platforms
2. GOAL: Filter 80+ platforms → 3-5 finalists matching requirements
3. CONTEXT RETRIEVAL:
   - Automatic: vendor_database.json (MCP Resource), architect requirements
   - On-Demand: Similar past decisions, vendor reviews
4. TRIGGER CONDITIONS: User asks to evaluate vendors, compare platforms, filter by capabilities
5. STEPS:
   - Tier 1: Apply mandatory filters (team capacity, budget, sovereignty, vendor tolerance)
   - Tier 2: Score preferred capabilities (3× weight multiplier)
   - Rank finalists by total score
6. OUTPUT FORMAT: Markdown table (vendor, score, strengths, weaknesses)
7. VERIFICATION: Facts (vendor capabilities from database) vs Assumptions (user-provided requirements)
8. EXAMPLES: Healthcare SOC evaluation, FinTech compliance scenario
9. INTEGRATION: Works with tco-calculator, journey-persona-matcher, architecture-report-generator
10. ANTI-PATTERNS: Don't recommend vendors without verification, don't ignore budget constraints

---

#### 2. tco-calculator

**Purpose**: 5-year TCO projection (platform + ops + hidden costs)
**Input**: Vendor selection, data volume, growth rate
**Output**: Cost breakdown table, 5-year total

**10-Section Template**:
1. IDENTITY: TCO analysis specialist for security data platforms
2. GOAL: Project 5-year total cost of ownership with growth modeling
3. CONTEXT RETRIEVAL:
   - Automatic: vendor_database.json cost models, industry benchmarks
   - On-Demand: Similar deployment sizes, cost trends
4. TRIGGER CONDITIONS: User asks about costs, budget planning, vendor comparison by price
5. STEPS:
   - Calculate platform costs (licensing, compute, storage)
   - Calculate operational costs (FTE, training, support)
   - Calculate hidden costs (migrations, integrations, maintenance)
   - Project 5-year total with growth rate modeling
6. OUTPUT FORMAT: Markdown table (cost category, year 1-5, total), chart-ready data
7. VERIFICATION: Facts (vendor pricing from database) vs Assumptions (growth rate, FTE costs)
8. EXAMPLES: 10K employee SOC, 100K employee enterprise deployment
9. INTEGRATION: Works with security-vendor-filter (post-filtering), architecture-report-generator
10. ANTI-PATTERNS: Don't ignore hidden costs, don't use outdated pricing

---

#### 3. journey-persona-matcher

**Purpose**: Match architect to Jennifer/Marcus/Priya journey (Book Chapter 4)
**Input**: Organization context (industry, size, constraints)
**Output**: Persona match + narrative guidance

**10-Section Template**:
1. IDENTITY: Journey persona matching specialist
2. GOAL: Map organization to persona-specific architecture journey
3. CONTEXT RETRIEVAL:
   - Automatic: Book Chapter 4 persona narratives
   - On-Demand: Industry patterns, similar organization profiles
4. TRIGGER CONDITIONS: User describes organization constraints, asks about architecture approach
5. STEPS:
   - Identify organization profile (industry, size, maturity, constraints)
   - Match to persona: Jennifer (healthcare, compliance-first), Marcus (FinTech, cost-sensitive), Priya (multi-national, sovereignty)
   - Provide persona-specific guidance
6. OUTPUT FORMAT: Markdown (persona match, key priorities, recommended vendors, journey narrative)
7. VERIFICATION: Facts (organization details) vs Assumptions (persona fit accuracy)
8. EXAMPLES: Healthcare 10K employees → Jennifer, FinTech startup → Marcus
9. INTEGRATION: Works with security-vendor-filter (persona-specific scoring), architecture-report-generator
10. ANTI-PATTERNS: Don't force-fit personas, acknowledge hybrid scenarios

---

#### 4. architecture-report-generator

**Purpose**: Generate 8-12 page architecture recommendation
**Input**: Finalists, TCO, persona, trade-offs
**Output**: Architecture-Recommendation-YYYY-MM-DD.md

**10-Section Template**:
1. IDENTITY: Architecture documentation specialist
2. GOAL: Create comprehensive decision artifact for stakeholder communication
3. CONTEXT RETRIEVAL:
   - Automatic: All prior skill outputs (finalists, TCO, persona, decision_state.json)
   - On-Demand: Vendor reviews, production deployment examples
4. TRIGGER CONDITIONS: User ready to finalize decision, requests formal recommendation
5. STEPS:
   - Executive summary (3-5 finalists, recommendation)
   - Detailed analysis (vendor capabilities, trade-offs, TCO)
   - Persona journey guidance (implementation roadmap)
   - POC evaluation criteria (vendor-specific test plans)
   - Risk assessment (deployment complexity, vendor lock-in, support)
6. OUTPUT FORMAT: Markdown report (8-12 pages, executive summary, detailed sections, appendices)
7. VERIFICATION: Facts (vendor data, TCO projections) vs Assumptions (implementation timeline, risk severity)
8. EXAMPLES: Healthcare SIEM selection, FinTech lakehouse architecture
9. INTEGRATION: Final step after security-vendor-filter, tco-calculator, journey-persona-matcher
10. ANTI-PATTERNS: Don't oversimplify trade-offs, don't hide vendor weaknesses

---

**Deliverable**: 4 Claude Skills with 10-section template

**Estimated Time**: 12-15 hours (3-4 hours per skill)

---

### Week 3 (Nov 16-22): Testing Migration + Documentation

**Objective**: Migrate 178 tests, update documentation

**Tasks**:
1. Adapt 178 tests to skill-aware wrappers:
   - Business logic tests reuse (filtering, scoring, reporting)
   - Skill invocation tests (trigger conditions, context retrieval)
   - Integration tests (skill-to-skill workflows)

2. Achieve 80%+ coverage (target: 85-90%)

3. Update documentation:
   - PROJECT-BRIEF.md (hybrid architecture section)
   - README.md (setup instructions, architecture diagram)
   - CLAUDE.md (Claude Skills section expanded)
   - Create MIGRATION-GUIDE.md (rationale, before/after comparison)

**Deliverable**: 178 tests passing, 80%+ coverage, documentation complete

**Estimated Time**: 6-8 hours testing + 4-5 hours documentation = 10-13 hours total

---

## Architecture Diagrams

### Before (Pure MCP)

```
[Architect] ↔ [Claude Desktop] ↔ [MCP Server Process]
                                       ↓
                            [8 MCP Tools]
                            [2 MCP Prompts]
                            [2 MCP Resources]
                                       ↓
                        [vendor_database.json]
                        [decision_state.json]
                                       ↓
                         [Architecture Report.md]
```

**Deployment**:
- Separate MCP server process required
- Claude Desktop config.json setup
- 8 Tools + 2 Prompts + 2 Resources

---

### After (Hybrid)

```
[Architect] ↔ [Claude Code] ↔ [Claude Skills (auto-discovered)] + [MCP Server (data only)]
                                       ↓                                ↓
                    [4 Claude Skills handle workflow]    [2 MCP Resources provide data]
                    - security-vendor-filter              - vendor_database (Resource)
                    - tco-calculator                      - decision_state (Resource)
                    - journey-persona-matcher
                    - architecture-report-generator
                                       ↓
                        [Architecture Report.md]
```

**Deployment**:
- Claude Skills: Auto-discovery in `.claude/skills/` (zero config)
- MCP Server: Simplified (Resources only, no Tools/Prompts)
- Skills access MCP Resources via protocol

---

## Success Metrics

### Week 1 Success
- ✅ MCP server simplified (Tools/Prompts removed, Resources kept)
- ✅ MCP server loads without errors
- ✅ vendor_database.json, decision_state.json accessible via Resources

### Week 2 Success
- ✅ 4 Claude Skills operational (security-vendor-filter, tco-calculator, journey-persona-matcher, architecture-report-generator)
- ✅ 10-section template applied to all skills
- ✅ Memory Prompts CONTEXT RETRIEVAL integrated

### Week 3 Success
- ✅ 178 tests migrated, 80%+ coverage restored
- ✅ Documentation updated (PROJECT-BRIEF, README, CLAUDE, MIGRATION-GUIDE)
- ✅ Hybrid architecture functional (end-to-end workflow validated)

---

## Risk Mitigation

### Risk 1: Conversion Takes Longer Than Expected
**Mitigation**: Week 1 prototype validates time estimates (3-4 hours per skill)
**Fallback**: Reduce scope to 3 skills if timeline slips (defer journey-persona-matcher)

### Risk 2: MCP Resources + Claude Skills Integration Issues
**Mitigation**: Test MCP Resource access from Claude Skills in Week 1
**Fallback**: Revert to file-based vendor_database.json if MCP Resource access fails

### Risk 3: Testing Migration Complexity
**Mitigation**: Reuse business logic tests (filtering, scoring unchanged)
**Fallback**: Accept 70% coverage if 80% unreachable, document gaps

---

## Timeline

**Start Date**: November 2, 2025 (Week 1)
**End Date**: November 22, 2025 (Week 3)
**Total Duration**: 3 weeks, 20-30 hours

**Milestones**:
- Nov 8: Week 1 complete (MCP server simplified)
- Nov 15: Week 2 complete (4 Claude Skills operational)
- Nov 22: Week 3 complete (testing + documentation)

---

## Next Actions

### Immediate (Week 4 - Oct 21-25)
- [ ] Notify team: Hybrid architecture approved, November implementation
- [ ] Schedule Week 1 kickoff (Nov 2)
- [ ] Prepare development environment (Claude Code, MCP server setup)

### Week 1 (Nov 2-8)
- [ ] Remove 8 MCP Tools, 2 MCP Prompts from server code
- [ ] Test MCP server with Resources only
- [ ] Prototype first skill (security-vendor-filter) to validate time estimate
- [ ] Document MCP server simplification changes

### Week 2 (Nov 9-15)
- [ ] Create remaining 3 Claude Skills (tco-calculator, journey-persona-matcher, architecture-report-generator)
- [ ] Apply 10-section template to all skills
- [ ] Integrate Memory Prompts CONTEXT RETRIEVAL
- [ ] Test skill-to-skill workflows

### Week 3 (Nov 16-22)
- [ ] Migrate 178 tests to skill-aware wrappers
- [ ] Achieve 80%+ coverage
- [ ] Update documentation (PROJECT-BRIEF, README, CLAUDE, MIGRATION-GUIDE)
- [ ] Beta test hybrid architecture (3-5 testers)

---

**Decision Status**: APPROVED
**Implementation Status**: READY TO START (November 2, 2025)
**Expected Completion**: November 22, 2025
