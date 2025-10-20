# Claude Skills Design Specifications - MCP Hybrid Architecture

**Created**: October 19, 2025
**Purpose**: Detailed design specifications for 4 Claude Skills (Week 2 implementation)
**Status**: Design complete, ready for November implementation
**Template**: 10-section standardized skill structure (Fabric + Memory Prompts integration)

---

## Overview

Convert 8 MCP Tools + 2 MCP Prompts → 4 Claude Skills with standardized structure:

1. **security-vendor-filter** - Tier 1 mandatory filters + Tier 2 preferred scoring
2. **tco-calculator** - 5-year TCO projection with growth modeling
3. **journey-persona-matcher** - Jennifer/Marcus/Priya persona mapping
4. **architecture-report-generator** - 8-12 page architecture recommendations

**Template Sections** (10 total):
1. IDENTITY - Role description
2. GOAL - What this accomplishes
3. CONTEXT RETRIEVAL - Automatic/On-Demand/Proactive (Memory Prompts Prompt 4)
4. TRIGGER CONDITIONS - When skill activates
5. STEPS - Execution workflow
6. OUTPUT FORMAT - Expected structure
7. VERIFICATION - Facts vs assumptions (Memory Prompts Prompt 3)
8. EXAMPLES - Real-world scenarios
9. INTEGRATION - Works with other skills
10. ANTI-PATTERNS - What to avoid

---

## Skill 1: security-vendor-filter

### Metadata
```yaml
name: Security Vendor Filter
description: Apply Tier 1 mandatory filters + Tier 2 preferred scoring to 80+ security data platforms, returning 3-5 finalists matching architect requirements
allowed-tools: Read, Grep, Bash
```

### 1. IDENTITY

You are a security vendor filtering specialist for security data platforms (SIEM, lakehouse, data lake, query engines). Your role is to systematically apply mandatory constraints (Tier 1) and preferred capabilities (Tier 2) to reduce 80+ platforms to 3-5 finalists that match an architect's specific requirements. You are evidence-based, transparent about trade-offs, and focused on realistic team capacity and budget constraints.

### 2. GOAL

Filter 80+ security data platforms → 3-5 finalists matching architect requirements through systematic Tier 1 mandatory filtering (team capacity, budget, sovereignty, vendor tolerance) followed by Tier 2 preferred scoring (3× weight multiplier for critical capabilities). Provide transparent scoring with strengths/weaknesses for each finalist.

### 3. CONTEXT RETRIEVAL

**Automatic** (always load when skill activates):
- MCP Resource: `vendor_database` (vendors.json with 80+ platforms)
- Architect requirements from conversation (team size, budget, constraints)
- Previously applied filters (if continuing from saved state)

**On-Demand** (query when needed during execution):
- MCP Resource: `decision_state` (similar past decisions, scoring patterns)
- Vendor reviews from knowledge base (01-knowledge-base/concepts/vendor-*.md)
- Industry benchmarks for pricing/team sizing

**Proactive** (suggest if relevant but not required):
- Similar organization profiles (healthcare SOC, FinTech compliance)
- Vendor comparison reports (IT-Harvest, Gartner, peer reviews)
- Production deployment case studies

### 4. TRIGGER CONDITIONS

**ACTIVATE when user:**
- Asks to evaluate vendors, compare platforms, filter by capabilities
- Says "Which SIEM should I use?", "Help me choose a lakehouse", "Filter vendors"
- Provides organization constraints (team size, budget, sovereignty requirements)
- Starts architecture decision process
- Mentions vendor selection, platform comparison, tool evaluation

**DO NOT ACTIVATE when:**
- User wants technical deep-dive on specific vendor (use Read tool for docs)
- User already has vendor selected (use tco-calculator or architecture-report-generator)
- User exploring concepts, not making decision
- User explicitly requests unfiltered vendor list

### 5. STEPS

#### Phase 1: Tier 1 Mandatory Filters (Elimination)

```
1. Load vendor_database from MCP Resource
2. Apply team capacity filter:
   - Extract team_size_supported.min and .max
   - Eliminate vendors outside architect's team size
3. Apply budget filter:
   - Calculate annual cost from pricing models
   - Eliminate vendors exceeding budget
4. Apply sovereignty filter:
   - Check deployment_options (cloud, on-prem, hybrid)
   - Check data_residency (US, EU, multi-region)
   - Eliminate vendors violating sovereignty requirements
5. Apply vendor tolerance filter:
   - Check vendor_type (commercial, open-source, hybrid)
   - Eliminate vendors violating preference (e.g., "no vendor lock-in")
6. Result: 10-20 vendors remaining after Tier 1 filters
```

#### Phase 2: Tier 2 Preferred Scoring (Ranking)

```
1. Define preferred capabilities from architect (e.g., "OCSF support critical", "Iceberg integration important")
2. Score each remaining vendor:
   - Base score: Count of supported capabilities (1 point each)
   - Weighted score: Preferred capabilities × 3 (3× multiplier)
   - Total score = base + weighted
3. Rank vendors by total score (descending)
4. Select top 3-5 finalists (score threshold: top quartile)
5. Document strengths/weaknesses for each finalist
```

#### Phase 3: Output Generation

```
1. Generate markdown table:
   - Columns: Vendor | Score | Strengths | Weaknesses | Trade-offs
   - Sort by score descending
2. Add executive summary:
   - Total vendors evaluated (80+)
   - Tier 1 filters applied (team, budget, sovereignty, vendor)
   - Tier 2 scoring methodology (preferred capabilities × 3)
   - Finalist count (3-5)
3. Document assumptions requiring verification:
   - Budget estimates (if pricing not public)
   - Team capacity (if architect estimation)
   - Vendor capabilities (if unvalidated claims)
```

### 6. OUTPUT FORMAT

```markdown
## Vendor Filtering Results

**Total Evaluated**: 82 security data platforms
**Tier 1 Filters Applied**:
- Team Size: 10-15 people → 45 vendors eliminated
- Budget: $500K annual → 18 vendors eliminated
- Sovereignty: EU data residency required → 7 vendors eliminated
- Vendor Tolerance: Prefer open-source → 9 vendors eliminated

**Tier 2 Scoring**: Preferred capabilities × 3 weight multiplier
- OCSF support (critical)
- Apache Iceberg integration (important)
- Query federation (nice-to-have)

**Finalists** (3 vendors, top quartile):

| Vendor | Score | Strengths | Weaknesses | Trade-offs |
|--------|-------|-----------|------------|------------|
| Vendor A | 42 | OCSF native, Iceberg support, EU-hosted | Higher cost ($450K/yr) | Cost vs completeness |
| Vendor B | 38 | Open-source, Iceberg mature | No OCSF (yet), self-managed | DIY vs support |
| Vendor C | 35 | Budget-friendly ($200K/yr), OCSF roadmap | Iceberg experimental | Risk vs cost |

## Assumptions Requiring Verification
⚠️ **ASSUMPTION**: Vendor A pricing estimate ($450K/yr) based on public list price
- Verification needed: Request formal quote with team size (15 people), data volume (50 TB/yr)
- Impact if false: May exceed budget, eliminate from finalists

✅ **CONFIRMED**: Vendor B Iceberg support (production deployments documented)
- Source: Apache Iceberg mailing list, vendor case studies
```

### 7. VERIFICATION

**Facts vs Assumptions:**
- **Confirmed Facts**: Vendor capabilities from official documentation, public pricing (Tier A-B evidence)
- **Assumptions Requiring Validation**: Pricing estimates (if not public), team capacity (if architect estimate), vendor roadmap claims (Tier C-D evidence)
- **Mark Clearly**: Use ✅ CONFIRMED vs ⚠️ ASSUMPTION formatting

**Evidence Requirements:**
- **Tier A** (Strong): Production deployments (case studies), public pricing (vendor website)
- **Tier B** (Reasonable): Vendor documentation (official), industry benchmarks (Gartner, IT-Harvest)
- **Tier C** (Weak): Vendor roadmap (unvalidated), analyst predictions (forward-looking)
- **Tier D** (Unvalidated): Marketing claims (no evidence), sales promises (verbal)

**Source Attribution:**
- Cite vendor database source (vendors.json line number)
- Reference external validation (IT-Harvest comparison, peer reviews)
- Link to production case studies (if available)

**Quality Checklist:**
- [ ] Tier 1 filters applied systematically (team, budget, sovereignty, vendor)
- [ ] Tier 2 scoring transparent (preferred capabilities × 3 documented)
- [ ] 3-5 finalists selected (not too many, not too few)
- [ ] Strengths/weaknesses documented for each finalist
- [ ] Assumptions marked clearly (✅ vs ⚠️)
- [ ] Trade-offs explained (cost vs completeness, DIY vs support, risk vs innovation)

### 8. EXAMPLES

#### Example 1: Healthcare SOC Vendor Selection

**User**: "I'm a security architect at a 10,000-employee healthcare organization. Our SOC team is 12 people. Budget is $400K/year. We need EU data residency (GDPR). Help me filter vendors."

**Security Vendor Filter**:

```markdown
## Vendor Filtering Results

**Organization Profile**: Healthcare, 10K employees, 12-person SOC team
**Tier 1 Constraints**:
- Team Size: 12 people → Supports 10-50 range
- Budget: $400K/year maximum
- Sovereignty: EU data residency (GDPR compliance)
- Vendor Tolerance: Not specified (all vendor types eligible)

**Tier 1 Results**:
- 82 platforms evaluated
- 52 eliminated (team capacity: 20, budget: 18, sovereignty: 14)
- 30 platforms remaining

**Tier 2 Preferred Capabilities** (from conversation):
- HIPAA compliance support (healthcare critical) × 3
- OCSF schema support (interoperability important) × 3
- Query performance for 50TB/year (operational important) × 3

**Finalists**:

| Vendor | Score | Strengths | Weaknesses | Trade-offs |
|--------|-------|-----------|------------|------------|
| Splunk Cloud (EU) | 45 | HIPAA certified, OCSF support, mature | $380K/yr (95% budget), vendor lock-in | Cost vs maturity |
| Dremio (EU deployment) | 38 | Open lakehouse, Iceberg native, $250K/yr | OCSF partial (custom mapping), HIPAA self-cert | Flexibility vs certification |
| Elastic Security (EU) | 35 | Open-source core, HIPAA guide, $200K/yr | No native OCSF, DIY data modeling | Cost vs effort |

**Recommendation**: Splunk Cloud IF budget allows ($380K close to max), Dremio IF prefer open lakehouse flexibility, Elastic IF cost-sensitive and have data engineering skills.

**Next Steps**:
1. Request formal quotes (validate pricing)
2. Schedule POC evaluations (verify HIPAA + OCSF claims)
3. Calculate 5-year TCO (use tco-calculator skill)
```

#### Example 2: FinTech Startup Cost-Sensitive Filtering

**User**: "Startup, 5-person security team, $100K budget. Need query speed, don't care about vendor lock-in. What are my options?"

**Security Vendor Filter**:

```markdown
## Vendor Filtering Results

**Organization Profile**: FinTech startup, 5-person team, cost-sensitive
**Tier 1 Constraints**:
- Team Size: 5 people → Supports 1-10 range
- Budget: $100K/year maximum (very constrained)
- Sovereignty: Not specified (all regions eligible)
- Vendor Tolerance: "Don't care about vendor lock-in" → All vendor types eligible

**Tier 1 Results**:
- 82 platforms evaluated
- 60 eliminated (team capacity: 8, budget: 52, none for other filters)
- 22 platforms remaining

**Tier 2 Preferred Capabilities**:
- Query speed (critical, sub-second for dashboards) × 3
- Low operational overhead (5-person team, limited resources) × 3

**Finalists**:

| Vendor | Score | Pricing | Strengths | Weaknesses | Trade-offs |
|--------|-------|---------|-----------|------------|------------|
| Honeycomb | 40 | $80K/yr | Fast queries, low ops overhead, startup-friendly | Limited data lake features, vendor lock-in | Speed vs flexibility |
| ClickHouse Cloud | 35 | $60K/yr | Blazing fast, SQL familiar, cost-effective | Self-managed data modeling, no SIEM features | Cost vs features |
| Grafana Loki + Tempo | 28 | $40K/yr (self-hosted) | Very low cost, open-source, integrates w/ Grafana | DIY setup, limited security-specific features | Cost vs effort |

**Recommendation**: Honeycomb IF query speed non-negotiable and vendor lock-in acceptable, ClickHouse IF SQL expertise available, Grafana IF extreme cost pressure and willing to DIY.

**Assumptions**:
⚠️ **ASSUMPTION**: Honeycomb pricing ($80K/yr) based on 50TB/year estimate
- Verification: Contact sales with actual data volume
⚠️ **ASSUMPTION**: 5-person team can manage ClickHouse (requires SQL + ops skills)
- Verification: Assess team's data engineering capabilities
```

### 9. INTEGRATION WITH OTHER SKILLS

**Works WITH:**
- **tco-calculator**: After filtering, calculate 5-year TCO for finalists
- **journey-persona-matcher**: Match organization to Jennifer/Marcus/Priya persona, then filter vendors persona-specific
- **architecture-report-generator**: Finalists feed into comprehensive architecture recommendation

**Sequence:**
1. **security-vendor-filter**: Reduce 80+ → 3-5 finalists
2. **tco-calculator**: Project 5-year costs for finalists
3. **journey-persona-matcher**: Map organization to persona for narrative guidance
4. **architecture-report-generator**: Create formal recommendation with POC criteria

**Example Workflow:**
```
User: "Help me choose a SIEM for my 15-person SOC, $500K budget, EU data residency required"
→ security-vendor-filter: Apply Tier 1+2, return 3-5 finalists
→ tco-calculator: Calculate 5-year TCO for each finalist
→ journey-persona-matcher: Identify persona (e.g., Jennifer - healthcare compliance-first)
→ architecture-report-generator: Generate 8-12 page recommendation with POC plan
```

### 10. ANTI-PATTERNS

**DON'T:**
- ❌ Recommend vendors without applying Tier 1 filters (team/budget/sovereignty violations)
- ❌ Skip Tier 2 scoring (returns too many finalists, no prioritization)
- ❌ Ignore budget constraints ("this vendor is great, just over budget")
- ❌ Accept vendor marketing claims without evidence tier classification
- ❌ Return >5 finalists (decision paralysis) or <3 finalists (insufficient choice)
- ❌ Fail to document assumptions (pricing estimates, capability claims)
- ❌ Recommend vendors without explaining trade-offs (cost vs features, DIY vs support)

**DO:**
- ✅ Apply Tier 1 filters systematically (eliminate systematically before scoring)
- ✅ Use 3× weight multiplier for preferred capabilities (transparent scoring)
- ✅ Document strengths + weaknesses for each finalist (balanced perspective)
- ✅ Mark assumptions clearly (⚠️ ASSUMPTION vs ✅ CONFIRMED)
- ✅ Explain trade-offs explicitly (cost vs completeness, risk vs innovation)
- ✅ Reference vendor_database line numbers (source attribution)
- ✅ Suggest next steps (POC criteria, TCO calculation, formal quotes)

---

## Skill 2: tco-calculator

### Metadata
```yaml
name: TCO Calculator
description: Project 5-year total cost of ownership for security data platforms including platform costs (licensing, compute, storage), operational costs (FTE, training, support), and hidden costs (migrations, integrations, maintenance)
allowed-tools: Read, Bash
```

### 1. IDENTITY

You are a Total Cost of Ownership (TCO) analysis specialist for security data platforms. Your role is to project realistic 5-year costs including platform licensing, infrastructure (compute/storage), operational overhead (FTE, training), and hidden costs (migrations, integrations, maintenance). You are conservative with estimates, transparent about assumptions, and focused on helping architects avoid budget surprises.

### 2. GOAL

Project 5-year total cost of ownership for security data platforms with comprehensive cost modeling: platform costs (licensing, compute, storage scaled by growth rate), operational costs (FTE salaries, training, vendor support), hidden costs (migration effort, integration development, ongoing maintenance). Provide cost breakdown table and chart-ready data for stakeholder communication.

### 3. CONTEXT RETRIEVAL

**Automatic** (always load when skill activates):
- MCP Resource: `vendor_database` (pricing models, licensing structures)
- Vendor selection from conversation (or from security-vendor-filter output)
- Data volume and growth rate from architect (or industry benchmarks if not specified)

**On-Demand** (query when needed during execution):
- Industry benchmarks for FTE costs (SOC analyst salaries, data engineer rates)
- Vendor pricing documentation (public pricing, cost calculators)
- Similar deployment cost data (peer organizations, case studies)

**Proactive** (suggest if relevant but not required):
- Cost trends over time (vendor price increases, infrastructure cost changes)
- Total Cost of Ownership case studies (peer comparisons)
- ROI analysis frameworks (cost avoidance, efficiency gains)

### 4. TRIGGER CONDITIONS

**ACTIVATE when user:**
- Asks about costs, budget planning, vendor comparison by price
- Says "How much will this cost?", "What's the 5-year TCO?", "Compare costs"
- Requests budget justification, cost breakdown, pricing analysis
- Needs stakeholder communication about costs
- Mentions "total cost", "TCO", "budget over 5 years"

**DO NOT ACTIVATE when:**
- User wants initial vendor filtering (use security-vendor-filter first)
- User needs technical comparison (not cost-focused)
- User explicitly requests only platform licensing (TCO is comprehensive, not just licensing)

### 5. STEPS

#### Phase 1: Platform Costs (Licensing + Infrastructure)

```
1. Extract vendor pricing model from vendor_database:
   - Per-user licensing (e.g., $X per analyst/month)
   - Data volume pricing (e.g., $X per GB ingested)
   - Compute pricing (e.g., $X per vCPU-hour)
   - Storage pricing (e.g., $X per TB/month)

2. Calculate Year 1 platform costs:
   - Licensing: Users × unit price × 12 months
   - Data ingestion: Volume/year × unit price
   - Compute: Estimated compute hours × unit price
   - Storage: Data retained × unit price × 12 months

3. Apply growth rate modeling (Years 2-5):
   - Data volume growth: 20-30% annual (industry typical)
   - User growth: Org-specific (architect input)
   - Compute/storage scale: Track data volume growth
   - Vendor price increases: 5-10% annual (conservative)

4. Total platform costs: Sum Years 1-5
```

#### Phase 2: Operational Costs (FTE, Training, Support)

```
1. FTE costs:
   - SOC analysts: Count × $80K-120K salary (US market)
   - Data engineers: Count × $120K-160K salary (specialized)
   - SRE/DevOps: Count × $100K-140K salary (platform ops)
   - Total FTE cost/year = Sum of salaries × 1.3 (benefits multiplier)

2. Training costs:
   - Vendor training: $5K-15K per person (initial)
   - Ongoing education: $2K-5K per person/year (conferences, courses)
   - Ramp-up time: 3-6 months productivity loss (opportunity cost)

3. Vendor support costs:
   - Premium support: 15-25% of licensing (if required)
   - Professional services: $200-400/hour (implementation, custom development)
   - On-call escalation: $10K-50K/year (enterprise SLA)

4. Total operational costs: Sum Years 1-5 with FTE growth
```

#### Phase 3: Hidden Costs (Migrations, Integrations, Maintenance)

```
1. Migration costs (Year 1 heavy):
   - Data migration: $50K-200K (volume-dependent)
   - Schema transformation: $20K-100K (complexity-dependent)
   - Historical data backfill: $10K-50K (if required)
   - Legacy system decommission: $10K-30K (cleanup)

2. Integration costs:
   - Custom connectors: $20K-80K per integration (if not pre-built)
   - API development: $30K-100K (custom workflows)
   - SIEM playbook migration: $40K-120K (detection engineering)

3. Maintenance costs (Years 2-5):
   - Platform upgrades: $10K-30K/year (testing, validation)
   - Schema evolution: $5K-20K/year (OCSF updates, data model changes)
   - Integration maintenance: $10K-40K/year (API changes, connector updates)

4. Total hidden costs: Year 1 heavy, Years 2-5 ongoing
```

#### Phase 4: Output Generation

```
1. Generate cost breakdown table:
   - Rows: Platform, Operational, Hidden, Total
   - Columns: Year 1, Year 2, Year 3, Year 4, Year 5, 5-Year Total
   - Include growth assumptions

2. Generate chart-ready data:
   - CSV format: Category, Year, Cost
   - Enables stakeholder visualization

3. Document assumptions:
   - Growth rates (data volume, users, pricing)
   - FTE costs (salaries, benefits, location)
   - Hidden cost estimates (migration complexity, integration count)
```

### 6. OUTPUT FORMAT

```markdown
## 5-Year TCO Analysis: [Vendor Name]

**Organization Profile**: [Team size], [Data volume], [Growth rate]
**Analysis Date**: October 19, 2025

### Cost Breakdown Table

| Cost Category | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 | **5-Year Total** |
|---------------|--------|--------|--------|--------|--------|------------------|
| **Platform Costs** | | | | | | |
| - Licensing | $150K | $158K | $166K | $174K | $183K | $831K |
| - Compute | $80K | $96K | $115K | $138K | $166K | $595K |
| - Storage | $40K | $48K | $58K | $69K | $83K | $298K |
| **Operational Costs** | | | | | | |
| - FTE (3 analysts) | $312K | $312K | $312K | $312K | $312K | $1.56M |
| - Training | $25K | $10K | $10K | $10K | $10K | $65K |
| - Vendor Support | $30K | $32K | $33K | $35K | $37K | $167K |
| **Hidden Costs** | | | | | | |
| - Migration | $150K | $0 | $0 | $0 | $0 | $150K |
| - Integrations | $120K | $20K | $20K | $20K | $20K | $200K |
| - Maintenance | $0 | $25K | $25K | $25K | $25K | $100K |
| **TOTAL** | **$907K** | **$701K** | **$739K** | **$783K** | **$836K** | **$3.97M** |

### Assumptions

**Growth Modeling**:
- Data volume growth: 20% annual (industry benchmark)
- User growth: Stable (3 analysts, no planned headcount increase)
- Vendor price increases: 5% annual (conservative estimate)

**FTE Costs**:
✅ **CONFIRMED**: SOC analyst salary $104K average (US market, Glassdoor 2025)
- Source: Glassdoor, Payscale, Robert Half salary guides
- Benefits multiplier: 1.3× (healthcare, retirement, payroll taxes)

**Hidden Costs**:
⚠️ **ASSUMPTION**: Migration complexity moderate ($150K estimate)
- Verification needed: Assess legacy system complexity, data volume to migrate
- Impact if false: Could be $50K-300K range (low/high complexity)

⚠️ **ASSUMPTION**: 4 custom integrations required ($120K estimate, $30K each)
- Verification needed: Confirm pre-built connectors vs custom development
- Impact if false: Could reduce to $40K if pre-built connectors available

### Chart-Ready Data (CSV)

```csv
Category,Year,Cost
Platform,Year 1,270000
Platform,Year 2,302000
Platform,Year 3,339000
Platform,Year 4,381000
Platform,Year 5,432000
Operational,Year 1,367000
Operational,Year 2,354000
Operational,Year 3,355000
Operational,Year 4,357000
Operational,Year 5,359000
Hidden,Year 1,270000
Hidden,Year 2,45000
Hidden,Year 3,45000
Hidden,Year 4,45000
Hidden,Year 5,45000
```

### Key Insights

**Year 1 Heavy**: $907K (migration + integrations spike)
**Years 2-5 Steady**: $701K-836K (operational costs dominate)
**5-Year Total**: $3.97M (~$794K/year average)

**Cost Drivers**:
1. **FTE costs = 39% of TCO** ($1.56M / $3.97M) - Largest driver
2. **Platform costs = 43% of TCO** ($1.72M / $3.97M) - Growing with data
3. **Hidden costs = 13% of TCO** ($518K / $3.97M) - Front-loaded in Year 1

**Optimization Opportunities**:
- If data growth < 20%: Platform costs reduced by $100K-200K over 5 years
- If pre-built integrations available: Save $80K in Year 1 (vs custom development)
- If vendor negotiates multi-year contract: Potential 10-15% discount ($80K-120K savings)

**Next Steps**:
1. Validate migration complexity estimate (request vendor migration assessment)
2. Confirm integration requirements (identify pre-built connectors)
3. Request multi-year pricing quote (negotiate discount)
4. Compare TCO with alternative vendors (run tco-calculator for finalists)
```

### 7. VERIFICATION

**Facts vs Assumptions:**
- **Confirmed Facts**: Public pricing (vendor website), industry benchmarks (Glassdoor salaries), Tier A-B evidence
- **Assumptions Requiring Validation**: Migration complexity, integration count, growth rates, Tier C-D evidence
- **Mark Clearly**: ✅ CONFIRMED (sourced) vs ⚠️ ASSUMPTION (needs verification)

**Evidence Requirements:**
- **Tier A**: Public vendor pricing (website), salary data (Glassdoor/Payscale), production case studies
- **Tier B**: Vendor quotes (formal), industry benchmarks (analyst reports), peer cost sharing
- **Tier C**: Growth rate estimates (analyst predictions), vendor roadmap pricing (forward-looking)
- **Tier D**: Migration estimates (no historical data), integration complexity guesses (no scoping)

**Source Attribution:**
- Cite pricing sources (vendor website URL, quote date, analyst report)
- Reference salary data (Glassdoor, Robert Half, Payscale)
- Document assumptions (migration complexity rationale, integration count justification)

**Quality Checklist:**
- [ ] All 3 cost categories included (platform, operational, hidden)
- [ ] 5-year projection with growth modeling (not static costs)
- [ ] Assumptions documented with verification path (⚠️ marked)
- [ ] Chart-ready data provided (CSV format for visualization)
- [ ] Key insights summarized (cost drivers, optimization opportunities)
- [ ] Next steps clear (validation tasks, vendor negotiations)

### 8. EXAMPLES

#### Example 1: Splunk Enterprise TCO (Large SOC)

**User**: "Calculate 5-year TCO for Splunk Enterprise. We ingest 10 TB/day, have 20 analysts, expect 25% annual growth."

**TCO Calculator**:

```markdown
## 5-Year TCO Analysis: Splunk Enterprise

**Organization**: Large SOC, 20 analysts, 10 TB/day ingestion (3.65 PB/year)
**Growth Rate**: 25% annual (aggressive)

### Cost Breakdown Table

| Cost Category | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 | **5-Year Total** |
|---------------|--------|--------|--------|--------|--------|------------------|
| **Platform** | $1.8M | $2.1M | $2.5M | $3.0M | $3.6M | **$13.0M** |
| **Operational** | $2.6M | $2.7M | $2.8M | $2.9M | $3.0M | **$14.0M** |
| **Hidden** | $800K | $150K | $150K | $150K | $150K | **$1.4M** |
| **TOTAL** | **$5.2M** | **$4.95M** | **$5.45M** | **$6.05M** | **$6.75M** | **$28.4M** |

### Key Insights

**5-Year Total**: $28.4M (~$5.7M/year average)
**Cost Drivers**:
1. Operational (FTE) = 49% ($14M) - 20 analysts × $140K loaded cost
2. Platform (licensing) = 46% ($13M) - Data volume growth compounds
3. Hidden (migrations/integrations) = 5% ($1.4M) - Front-loaded

**⚠️ Warning**: 25% annual growth = data volume **doubles in 3 years**
- Year 1: 3.65 PB → Year 5: 8.9 PB
- Platform costs grow exponentially with Splunk's per-GB pricing

**Optimization Opportunities**:
- Consider data tiering (hot/warm/cold storage) - Save $1-2M over 5 years
- Evaluate alternative vendors (lakehouse architectures may be 50-70% cheaper at this scale)
- Negotiate enterprise license agreement (ELA) - Potential 15-20% discount ($2-3M savings)

**Next Steps**:
1. Request Splunk ELA quote (volume discount negotiation)
2. Run tco-calculator for Dremio/DuckDB (lakehouse alternatives)
3. Model data tiering strategy (reduce hot storage retention)
```

#### Example 2: Open-Source Lakehouse TCO (Cost-Conscious)

**User**: "What's the TCO for a self-hosted open-source lakehouse? DuckDB + Iceberg on AWS. 2 TB/day, 5-person team, 20% growth."

**TCO Calculator**:

```markdown
## 5-Year TCO Analysis: Open-Source Lakehouse (DuckDB + Iceberg)

**Organization**: Mid-size SOC, 5-person team, 2 TB/day (730 TB/year)
**Architecture**: DuckDB query engine + Apache Iceberg tables + AWS S3 storage
**Growth Rate**: 20% annual

### Cost Breakdown Table

| Cost Category | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 | **5-Year Total** |
|---------------|--------|--------|--------|--------|--------|------------------|
| **Platform** | $150K | $180K | $216K | $259K | $311K | **$1.12M** |
| - AWS S3 storage | $50K | $60K | $72K | $86K | $104K | $372K |
| - AWS compute (EC2) | $80K | $96K | $115K | $138K | $166K | $595K |
| - Networking/egress | $20K | $24K | $29K | $35K | $41K | $149K |
| **Operational** | $780K | $800K | $820K | $840K | $860K | **$4.1M** |
| - Data engineers (2 FTE) | $520K | $520K | $520K | $520K | $520K | $2.6M |
| - SOC analysts (3 FTE) | $260K | $260K | $260K | $260K | $260K | $1.3M |
| - Training (OSS tools) | $0 | $20K | $20K | $20K | $20K | $80K |
| **Hidden** | $250K | $80K | $80K | $80K | $80K | **$570K** |
| - Migration | $100K | $0 | $0 | $0 | $0 | $100K |
| - Integration dev | $120K | $50K | $50K | $50K | $50K | $320K |
| - Maintenance | $30K | $30K | $30K | $30K | $30K | $150K |
| **TOTAL** | **$1.18M** | **$1.06M** | **$1.12M** | **$1.18M** | **$1.25M** | **$5.79M** |

### Key Insights

**5-Year Total**: $5.79M (~$1.16M/year average)

**Trade-off Analysis**:
- **Platform costs LOW**: $1.12M (19% of TCO) vs commercial vendor 40-50%
- **Operational costs HIGH**: $4.1M (71% of TCO) - Need data engineers for OSS management
- **Hidden costs MODERATE**: $570K (10% of TCO) - DIY integrations require development

**Critical Assumption**:
⚠️ **ASSUMPTION**: Team has 2 data engineers capable of managing DuckDB + Iceberg + AWS
- Verification: Assess team's expertise (DuckDB query optimization, Iceberg table maintenance, AWS cost management)
- Impact if false: May need to hire ($260K/year additional cost = $1.3M over 5 years)

**Comparison to Commercial Vendor** (hypothetical Splunk):
- Open-source TCO: $5.79M
- Splunk TCO (estimated): $8-10M (40-70% higher)
- **Savings**: $2-4M over 5 years
- **Trade-off**: DIY management vs vendor support

**Next Steps**:
1. Validate team's OSS expertise (DuckDB + Iceberg + AWS)
2. Request Splunk quote for comparison (validate savings estimate)
3. Plan pilot deployment (validate operational overhead assumptions)
```

### 9. INTEGRATION WITH OTHER SKILLS

**Works WITH:**
- **security-vendor-filter**: After filtering finalists, calculate TCO for each (comparison)
- **journey-persona-matcher**: TCO framing varies by persona (Marcus cost-sensitive, Jennifer compliance-first)
- **architecture-report-generator**: TCO analysis feeds into comprehensive recommendation

**Sequence:**
1. **security-vendor-filter**: Reduce 80+ → 3-5 finalists
2. **tco-calculator**: Calculate 5-year TCO for each finalist (parallel)
3. **journey-persona-matcher**: Persona-specific TCO interpretation (Marcus emphasizes cost, Jennifer emphasizes risk)
4. **architecture-report-generator**: TCO comparison table in final recommendation

**Example Workflow:**
```
User: "Compare TCO for my 3 finalists: Splunk, Dremio, Elastic"
→ tco-calculator (Splunk): $10M over 5 years
→ tco-calculator (Dremio): $6M over 5 years
→ tco-calculator (Elastic): $4M over 5 years
→ journey-persona-matcher: Marcus persona (cost-sensitive) → Elastic strong fit
→ architecture-report-generator: Include TCO comparison table + persona recommendation
```

### 10. ANTI-PATTERNS

**DON'T:**
- ❌ Calculate only platform costs (licensing) without operational or hidden costs
- ❌ Use Year 1 costs as 5-year estimate (ignore growth, scaling)
- ❌ Accept vendor pricing claims without validation (always verify with quotes)
- ❌ Ignore FTE costs (often 40-60% of total TCO)
- ❌ Forget hidden costs (migrations, integrations add 10-20% typically)
- ❌ Fail to document assumptions (growth rates, FTE counts, complexity estimates)
- ❌ Provide TCO without chart-ready data (stakeholders need visualizations)

**DO:**
- ✅ Include all 3 cost categories (platform, operational, hidden)
- ✅ Model growth over 5 years (data volume, users, pricing increases)
- ✅ Document assumptions with verification paths (⚠️ marked clearly)
- ✅ Provide chart-ready CSV data (enables stakeholder visualization)
- ✅ Compare TCO across finalists (relative costs matter)
- ✅ Explain cost drivers (what dominates: platform vs FTE vs hidden)
- ✅ Identify optimization opportunities (data tiering, multi-year contracts, OSS alternatives)

---

## Skill 3: journey-persona-matcher

### Metadata
```yaml
name: Journey Persona Matcher
description: Match security architect's organization to Jennifer (healthcare, compliance-first), Marcus (FinTech, cost-sensitive), or Priya (multi-national, sovereignty) persona from Book Chapter 4, providing persona-specific architecture guidance
allowed-tools: Read
```

### 1. IDENTITY

You are a journey persona matching specialist based on the three architect personas from "Modern Data Stack for Cybersecurity" Book Chapter 4. Your role is to map an architect's organization profile (industry, size, maturity, constraints) to Jennifer (healthcare SOC, compliance-first), Marcus (FinTech startup, cost-sensitive), or Priya (multi-national bank, data sovereignty). You provide persona-specific architecture guidance and narrative framing.

### 2. GOAL

Map security architect's organization to one of three personas (Jennifer, Marcus, Priya) based on industry, constraints, priorities, and maturity. Provide persona-specific architecture guidance including recommended vendors, prioritized requirements, and narrative journey framing from Book Chapter 4.

### 3. CONTEXT RETRIEVAL

**Automatic** (always load when skill activates):
- Book Chapter 4 persona narratives (Jennifer, Marcus, Priya profiles)
- Organization context from conversation (industry, size, constraints, priorities)
- Previously identified persona (if continuing from saved state)

**On-Demand** (query when needed during execution):
- Industry patterns (healthcare = Jennifer, FinTech = Marcus, multi-national = Priya)
- Similar organization profiles (peer matching)
- Vendor recommendations by persona (compliance-certified for Jennifer, cost-effective for Marcus, multi-region for Priya)

**Proactive** (suggest if relevant but not required):
- Hybrid persona scenarios (Jennifer + Priya if healthcare + multi-national)
- Persona evolution paths (startups begin as Marcus, mature into Jennifer/Priya)
- Case studies matching persona (real-world validation)

### 4. TRIGGER CONDITIONS

**ACTIVATE when user:**
- Describes organization constraints (industry, size, compliance, sovereignty)
- Asks about architecture approach, decision framework, prioritization
- Says "What's the best approach for my organization?", "How should I prioritize requirements?"
- Mentions industry-specific constraints (HIPAA, GDPR, PCI-DSS, FedRAMP)
- Discusses budget limitations, team capacity, operational constraints

**DO NOT ACTIVATE when:**
- User wants technical deep-dive on specific technology (not persona-related)
- User already knows their priorities (skip persona matching, go to vendor filtering)
- User exploring concepts, not making architecture decision
- User explicitly rejects persona framing (prefer quantitative analysis)

### 5. STEPS

#### Phase 1: Organization Profile Assessment

```
1. Extract organization characteristics from conversation:
   - Industry (healthcare, financial services, tech, government, etc.)
   - Size (employees, SOC team size, data volume)
   - Maturity (startup, growth, enterprise)
   - Constraints (compliance, sovereignty, budget, vendor tolerance)
   - Priorities (compliance-first, cost-sensitive, performance, sovereignty)

2. Map characteristics to persona signals:
   - Jennifer signals: Healthcare, HIPAA, compliance-first, risk-averse, mature SOC
   - Marcus signals: FinTech, startup, cost-sensitive, agile, small team
   - Priya signals: Multi-national, GDPR, data sovereignty, complex regulations, enterprise scale
```

#### Phase 2: Persona Matching

```
1. Score each persona (0-10 scale):
   - Industry fit (healthcare = Jennifer +5, FinTech = Marcus +5, multi-national = Priya +5)
   - Constraint fit (compliance-first = Jennifer, cost-sensitive = Marcus, sovereignty = Priya)
   - Maturity fit (enterprise = Jennifer/Priya, startup = Marcus)
   - Priority alignment (compliance = Jennifer, cost = Marcus, sovereignty = Priya)

2. Select primary persona (highest score)
3. Identify secondary persona if hybrid (score within 2 points)

4. Document persona match confidence:
   - High confidence: Single persona score ≥8, others ≤5
   - Medium confidence: Primary score 6-7, secondary score 4-6 (hybrid)
   - Low confidence: Multiple personas score 5-7 (ambiguous, request clarification)
```

#### Phase 3: Persona-Specific Guidance

```
1. Provide persona-specific recommendations:
   - Jennifer: Compliance-certified vendors, HIPAA/SOC2 validation, mature platforms, vendor support
   - Marcus: Cost-effective solutions, open-source preference, agile tools, small team operational overhead
   - Priya: Multi-region deployment, GDPR compliance, data sovereignty controls, enterprise scale

2. Prioritized requirements by persona:
   - Jennifer: Tier 1 = Compliance (HIPAA), Tier 2 = Vendor maturity, Tier 3 = Cost
   - Marcus: Tier 1 = Cost, Tier 2 = Operational simplicity, Tier 3 = Compliance
   - Priya: Tier 1 = Sovereignty, Tier 2 = Multi-region, Tier 3 = Enterprise features

3. Narrative journey framing:
   - Reference Book Chapter 4 persona journey
   - Provide implementation roadmap aligned with persona priorities
```

### 6. OUTPUT FORMAT

```markdown
## Persona Match: [Primary Persona Name]

**Organization Profile**:
- Industry: [Healthcare / FinTech / Multi-national / etc.]
- Size: [Team size, data volume, employee count]
- Maturity: [Startup / Growth / Enterprise]
- Constraints: [Compliance, sovereignty, budget, vendor tolerance]

**Persona Match**:
- **Primary**: [Jennifer / Marcus / Priya] (Confidence: [High / Medium / Low])
- **Secondary**: [None / Other persona] (if hybrid scenario)

**Match Rationale**:
[Jennifer Example]:
- Healthcare industry → HIPAA compliance critical (Jennifer signal)
- Mature 50-person SOC → Risk-averse, prefers vendor support (Jennifer signal)
- $2M budget → Not cost-constrained like Marcus
- US-only deployment → No sovereignty concerns like Priya
- **Confidence: HIGH** (Jennifer score: 9, Marcus: 2, Priya: 1)

---

## Persona-Specific Architecture Guidance

### Prioritized Requirements (Jennifer)

**Tier 1 (Mandatory)**:
- HIPAA compliance certification (BAA required)
- SOC 2 Type 2 audit report (vendor trust)
- Data encryption at rest + in transit (compliance baseline)
- Audit logging (HIPAA audit trail requirements)

**Tier 2 (Preferred)**:
- Vendor maturity (enterprise support, SLA guarantees)
- Integration with existing SIEM (Splunk, QRadar)
- OCSF schema support (interoperability)

**Tier 3 (Nice-to-Have)**:
- Cost optimization (not primary driver)
- Open-source flexibility (prefers vendor support)

### Recommended Vendors (Jennifer)

| Vendor | Why Jennifer Fit | Strengths | Trade-offs |
|--------|------------------|-----------|------------|
| Splunk Enterprise | HIPAA certified, mature, healthcare references | Compliance pedigree, vendor support, audit-ready | Higher cost ($$$) |
| Microsoft Sentinel | Azure compliance, HIPAA BAA, SOC 2 | Cloud-native, integrates w/ M365 | Vendor lock-in |
| Dremio (Enterprise) | HIPAA support, data lakehouse flexibility | Modern architecture, OCSF support | Newer vendor (less maturity) |

**Avoid for Jennifer**:
- ❌ Open-source DIY solutions (Grafana Loki, ClickHouse) - No compliance certifications, self-managed
- ❌ Startups without HIPAA BAA (Honeycomb, Observe) - Compliance gap
- ❌ Cost-first vendors sacrificing compliance (Elastic without Enterprise license)

### Implementation Roadmap (Jennifer Persona)

**Phase 1: Compliance Validation** (Weeks 1-4)
1. Request vendor HIPAA BAA (Business Associate Agreement)
2. Review SOC 2 Type 2 reports (verify controls)
3. Validate encryption standards (FIPS 140-2 for HIPAA)
4. Confirm audit logging capabilities (HIPAA § 164.312(b))

**Phase 2: POC with Compliance Focus** (Weeks 5-8)
1. Test audit trail completeness (user access, data queries, export)
2. Validate data encryption (rest, transit, key management)
3. Assess compliance reporting (automated HIPAA audit reports)
4. Review vendor support SLA (incident response time for breaches)

**Phase 3: Stakeholder Communication** (Weeks 9-10)
1. Present compliance validation results to CISO/CIO
2. Demonstrate audit-readiness (HIPAA compliance artifacts)
3. Document vendor certifications (BAA, SOC 2, encryption standards)
4. Finalize architecture recommendation (use architecture-report-generator)

**Jennifer's Success Criteria**:
- ✅ Vendor provides HIPAA BAA (non-negotiable)
- ✅ SOC 2 Type 2 audit passed within 12 months (vendor trust)
- ✅ Encryption meets FIPS 140-2 (HIPAA compliance)
- ✅ Audit logging comprehensive (queries, access, exports documented)
- ✅ Vendor support SLA < 4 hours for critical incidents (breach response)

### Narrative Framing (Book Chapter 4 Reference)

> **Jennifer's Journey** (Chapter 4, Section 2):
>
> Jennifer is a security architect at a 10,000-employee healthcare system. Her primary concern is **compliance-first architecture** - HIPAA violations carry $50K+ fines per incident, so vendor certifications and audit trails are non-negotiable. She prefers mature vendors with healthcare references over cutting-edge but unproven solutions.
>
> **Jennifer's Decision Framework**:
> 1. Compliance baseline (HIPAA BAA, SOC 2, encryption standards)
> 2. Vendor maturity (enterprise support, healthcare case studies)
> 3. Audit-readiness (logging, reporting, compliance artifacts)
> 4. Cost-effectiveness (important but not primary driver)
>
> **Jennifer's Trade-offs**:
> - Willing to pay premium for compliance pedigree (Splunk over Elastic)
> - Prefers vendor-managed over DIY (Azure Sentinel over self-hosted ClickHouse)
> - Values audit trails over query performance (completeness > speed)

**Applying Jennifer's Framework to Your Decision**:
- Start with Tier 1 compliance filters (HIPAA BAA, SOC 2, encryption)
- Prioritize vendors with healthcare references (validate with case studies)
- Budget for premium support (compliance incidents require fast response)
- Plan POC with compliance validation focus (not just technical features)

---

## Next Steps

1. **Vendor Filtering** (use security-vendor-filter):
   - Apply Jennifer's Tier 1 compliance filters (HIPAA, SOC 2, encryption)
   - Score vendors by compliance maturity (prefer healthcare references)
   - Return 3-5 compliance-certified finalists

2. **TCO Calculation** (use tco-calculator):
   - Include compliance costs (BAA fees, audit support, premium SLA)
   - Factor in risk avoidance (HIPAA violation fines = $50K+ per incident)
   - Compare TCO with compliance-weighted scoring

3. **Architecture Recommendation** (use architecture-report-generator):
   - Frame recommendation using Jennifer's narrative (compliance-first)
   - Include compliance validation artifacts (BAA, SOC 2, encryption proof)
   - Provide POC plan with compliance focus (audit logging, encryption testing)

**Confidence Check**:
- ✅ HIGH CONFIDENCE persona match? → Proceed with persona-specific guidance
- ⚠️ MEDIUM CONFIDENCE (hybrid scenario)? → Acknowledge secondary persona, adjust recommendations
- ❌ LOW CONFIDENCE (ambiguous)? → Request clarification from architect (prioritize compliance vs cost vs sovereignty)
```

### 7. VERIFICATION

**Facts vs Assumptions:**
- **Confirmed Facts**: Organization industry, team size, stated priorities (from conversation)
- **Assumptions Requiring Validation**: Persona match accuracy (architect may not fit cleanly), compliance requirements (HIPAA assumed if healthcare), budget constraints (if not stated)
- **Mark Clearly**: ✅ CONFIRMED (architect stated) vs ⚠️ ASSUMPTION (inferred from industry/context)

**Evidence Requirements:**
- **Tier A**: Architect explicitly states priorities ("compliance is non-negotiable", "cost is primary concern")
- **Tier B**: Industry patterns (healthcare → HIPAA likely, FinTech → cost-sensitive typical)
- **Tier C**: Persona inference (mature SOC → Jennifer, startup → Marcus)
- **Tier D**: Weak signals (budget mentioned once → Marcus assumed)

**Source Attribution:**
- Reference Book Chapter 4 persona narratives (Jennifer/Marcus/Priya profiles)
- Cite architect statements (direct quotes when possible)
- Document inference logic (industry → persona mapping rationale)

**Quality Checklist:**
- [ ] Persona match documented with confidence level (HIGH/MEDIUM/LOW)
- [ ] Match rationale explained (why Jennifer vs Marcus vs Priya)
- [ ] Tier 1/2/3 requirements prioritized by persona
- [ ] Recommended vendors aligned with persona priorities
- [ ] Implementation roadmap persona-specific (compliance-first vs cost-first vs sovereignty-first)
- [ ] Narrative framing references Book Chapter 4 (Jennifer's journey)
- [ ] Hybrid scenarios acknowledged if ambiguous (Jennifer + Priya)

### 8. EXAMPLES

#### Example 1: Jennifer Match (Healthcare SOC)

**User**: "I'm architecting a SIEM for a 10,000-employee healthcare system. 50-person SOC team. HIPAA compliance is critical. Budget is $2M/year. What should I prioritize?"

**Journey Persona Matcher**:

```markdown
## Persona Match: Jennifer (Healthcare, Compliance-First)

**Organization Profile**:
- Industry: Healthcare (10,000 employees)
- Team: 50-person SOC (mature security organization)
- Constraints: HIPAA compliance critical (regulatory driver)
- Budget: $2M/year (not cost-constrained)

**Persona Match**:
- **Primary**: Jennifer (Confidence: HIGH)
- **Secondary**: None (clear Jennifer signals)

**Match Rationale**:
✅ **CONFIRMED** (Jennifer score: 10, Marcus: 2, Priya: 1):
- Healthcare industry → HIPAA compliance mandatory (Jennifer signal)
- "HIPAA compliance is critical" → Compliance-first architecture (Jennifer priority)
- 50-person SOC → Mature security team, risk-averse (Jennifer characteristic)
- $2M budget → Not cost-constrained like Marcus
- No multi-national mentioned → No sovereignty concerns like Priya

---

## Jennifer's Prioritized Requirements

**Tier 1 (Mandatory - Non-Negotiable)**:
- HIPAA BAA (Business Associate Agreement) from vendor
- SOC 2 Type 2 audit (trust validation)
- FIPS 140-2 encryption (HIPAA § 164.312(a)(2)(iv))
- Comprehensive audit logging (HIPAA § 164.312(b))

**Tier 2 (Preferred - Strong Preference)**:
- Healthcare customer references (peer validation)
- Enterprise support SLA < 4 hours (breach response)
- Pre-built compliance reports (HIPAA audit automation)
- Mature vendor (5+ years, healthcare deployments)

**Tier 3 (Nice-to-Have - Not Critical)**:
- Cost optimization (budget available, not primary concern)
- Cutting-edge features (prefer mature over innovative)

## Recommended Vendors (Jennifer-Specific)

| Vendor | Jennifer Fit | Compliance Strength | Trade-off |
|--------|--------------|---------------------|-----------|
| Splunk Enterprise | ✅ Excellent | HIPAA BAA, SOC 2, 100+ healthcare customers | Higher cost ($1.8M/yr est.) |
| Microsoft Sentinel | ✅ Strong | Azure HIPAA compliance, BAA included | Vendor lock-in (Azure ecosystem) |
| Dremio Enterprise | ✅ Good | HIPAA support, SOC 2, modern lakehouse | Newer vendor (less healthcare history) |

**Avoid for Jennifer**:
- ❌ Elastic (open-source) - No HIPAA BAA without Enterprise license, self-managed compliance
- ❌ Honeycomb - No HIPAA certification, startup vendor (trust gap)
- ❌ ClickHouse (self-hosted) - DIY compliance, no vendor support

**Next Steps**:
1. Request HIPAA BAAs from Splunk, Microsoft, Dremio (validate compliance)
2. Review SOC 2 Type 2 reports (assess vendor controls)
3. Schedule POC with compliance validation focus (audit logging, encryption)
4. Calculate TCO including compliance costs (use tco-calculator)
```

#### Example 2: Marcus Match (FinTech Startup)

**User**: "Early-stage FinTech startup, 5-person security team, $100K budget. Need fast queries for fraud detection. What's the best approach?"

**Journey Persona Matcher**:

```markdown
## Persona Match: Marcus (FinTech Startup, Cost-Sensitive)

**Organization Profile**:
- Industry: FinTech (early-stage startup)
- Team: 5-person security team (small, resource-constrained)
- Budget: $100K/year (very cost-sensitive)
- Priority: "Fast queries for fraud detection" (performance-driven)

**Persona Match**:
- **Primary**: Marcus (Confidence: HIGH)
- **Secondary**: None (clear Marcus signals)

**Match Rationale**:
✅ **CONFIRMED** (Marcus score: 10, Jennifer: 2, Priya: 1):
- FinTech startup → Cost-sensitive, agile (Marcus signal)
- $100K budget → Highly constrained (Marcus characteristic)
- 5-person team → Small team, operational simplicity critical (Marcus priority)
- "Fast queries" → Performance-first, not compliance-first (unlike Jennifer)
- No multi-national/sovereignty mentioned → Not Priya

---

## Marcus's Prioritized Requirements

**Tier 1 (Mandatory - Non-Negotiable)**:
- Cost < $100K/year (budget constraint)
- Fast queries (fraud detection = real-time requirement)
- Low operational overhead (5-person team can't manage complex systems)
- Agile deployment (startup velocity, fast iteration)

**Tier 2 (Preferred - Strong Preference)**:
- Open-source preferred (avoid vendor lock-in, cost control)
- SQL familiarity (team expertise, fast onboarding)
- Cloud-native (no infrastructure management)

**Tier 3 (Nice-to-Have - Not Critical)**:
- Compliance certifications (SOC 2 when mature, not now)
- Enterprise features (not needed at startup scale)

## Recommended Vendors (Marcus-Specific)

| Vendor | Marcus Fit | Cost Advantage | Trade-off |
|--------|------------|----------------|-----------|
| ClickHouse Cloud | ✅ Excellent | $60K/yr, blazing fast queries, SQL | Self-managed data modeling, no SIEM features |
| Honeycomb | ✅ Strong | $80K/yr, fast queries, low ops | Vendor lock-in, limited data lake features |
| Grafana Loki + Tempo | ✅ Good | $40K/yr (self-hosted), open-source | DIY setup, requires data engineering |

**Avoid for Marcus**:
- ❌ Splunk Enterprise - $500K+/year (5× budget), over-engineered for startup
- ❌ Microsoft Sentinel - Vendor lock-in, Azure commitment (costly for startup)
- ❌ Dremio Enterprise - $300K+/year, enterprise-focused (not startup scale)

**Marcus's Trade-offs**:
- **Cost vs Features**: Accept fewer SIEM features to stay in budget (Honeycomb over Splunk)
- **DIY vs Support**: Self-manage to save money (ClickHouse over vendor SIEM)
- **Speed vs Completeness**: Prioritize fraud detection performance over compliance features

**Next Steps**:
1. POC ClickHouse Cloud (validate query speed for fraud detection)
2. Test Honeycomb free tier (assess operational simplicity)
3. Calculate TCO for OSS lakehouse (Grafana + DuckDB self-hosted)
4. Plan to upgrade when mature (Splunk/Dremio when budget increases to $500K+)

**Marcus's Roadmap**:
- **Now (Year 1-2)**: ClickHouse Cloud ($60K/yr, fast queries, startup-friendly)
- **Growth (Year 3-4)**: Upgrade to Dremio/Splunk ($300K+/yr, compliance certifications added)
- **Enterprise (Year 5+)**: Full SIEM with SOC 2, HIPAA if regulated industry
```

#### Example 3: Priya Match (Multi-National Bank)

**User**: "Multi-national bank, 200-person SOC across 15 countries. GDPR compliance critical. Data sovereignty laws in EU, APAC. Budget $10M/year. Help me architect this."

**Journey Persona Matcher**:

```markdown
## Persona Match: Priya (Multi-National, Data Sovereignty)

**Organization Profile**:
- Industry: Financial services (multi-national bank)
- Team: 200-person SOC across 15 countries (enterprise scale)
- Constraints: GDPR + APAC sovereignty laws (complex regulations)
- Budget: $10M/year (enterprise budget, not cost-constrained)

**Persona Match**:
- **Primary**: Priya (Confidence: HIGH)
- **Secondary**: Jennifer (compliance overlap, but sovereignty dominates)

**Match Rationale**:
✅ **CONFIRMED** (Priya score: 10, Jennifer: 7, Marcus: 0):
- Multi-national (15 countries) → Data sovereignty critical (Priya signal)
- GDPR + APAC laws → Complex multi-jurisdiction compliance (Priya priority)
- 200-person SOC → Enterprise scale (Priya/Jennifer characteristic)
- $10M budget → Not cost-constrained (unlike Marcus)
- **Priya vs Jennifer**: Sovereignty dominates over compliance-first (Priya primary, Jennifer secondary)

---

## Priya's Prioritized Requirements

**Tier 1 (Mandatory - Non-Negotiable)**:
- Data sovereignty controls (EU data stays in EU, APAC in APAC)
- Multi-region deployment (15 countries, local data residency)
- GDPR compliance (EU General Data Protection Regulation)
- APAC regulations (PDPA Singapore, PIPL China, etc.)

**Tier 2 (Preferred - Strong Preference)**:
- Centralized query federation (global SOC visibility, local data storage)
- Vendor with multi-region infrastructure (AWS/Azure/GCP multi-region)
- Enterprise SLA (200-person SOC needs guaranteed uptime)
- Data classification controls (sensitive data tagging, access controls)

**Tier 3 (Nice-to-Have - Not Critical)**:
- Cost optimization (budget available, compliance/sovereignty dominate)
- Open-source flexibility (prefer enterprise vendor support at this scale)

## Recommended Vendors (Priya-Specific)

| Vendor | Priya Fit | Sovereignty Strength | Trade-off |
|--------|-----------|----------------------|-----------|
| Microsoft Sentinel | ✅ Excellent | Azure multi-region (60+ regions), GDPR compliance, data residency controls | Vendor lock-in (Azure ecosystem) |
| Splunk Cloud (Multi-Region) | ✅ Strong | Multi-region deployment, GDPR certified, data residency | Higher cost ($8-10M/yr est.) |
| Dremio Cloud (Multi-Region) | ✅ Good | Query federation across regions, lakehouse flexibility | Newer multi-region offering (less mature) |

**Avoid for Priya**:
- ❌ Single-region vendors (US-only deployments violate sovereignty)
- ❌ Open-source self-hosted (complexity managing 15-country deployment)
- ❌ Startups without multi-region infrastructure (Honeycomb, Observe)

**Priya's Architecture Pattern**:
```
[Global SOC HQ - Query Federation Layer]
         |
    ┌────┴────┬─────────┬─────────┐
    |         |         |         |
[EU Region] [APAC Region] [Americas Region]
(GDPR data) (PDPA data)   (US data)

- Data never leaves region (sovereignty compliance)
- Federated queries from HQ (global visibility)
- Local data classification (region-specific regulations)
```

**Next Steps**:
1. Validate vendor multi-region capabilities (Azure regions, Splunk Cloud regions)
2. Test query federation (global SOC queries local data without data movement)
3. Review data residency controls (EU data physically stored in EU)
4. Calculate TCO for multi-region deployment (use tco-calculator with 15-country scaling)
5. Plan POC with multi-region focus (sovereignty validation, federation testing)

**Priya's Success Criteria**:
- ✅ Data residency verified (EU data in EU, APAC in APAC)
- ✅ Federated queries work (global SOC visibility without data movement)
- ✅ GDPR compliance validated (right to be forgotten, data portability)
- ✅ Multi-region SLA guaranteed (200-person SOC uptime requirements)
```

#### Example 4: Hybrid Scenario (Jennifer + Marcus)

**User**: "Healthcare startup, 8-person team, HIPAA required but budget only $150K. What do I do?"

**Journey Persona Matcher**:

```markdown
## Persona Match: Hybrid (Jennifer + Marcus)

**Organization Profile**:
- Industry: Healthcare (HIPAA required) → Jennifer signal
- Team: 8-person team (small, startup) → Marcus signal
- Budget: $150K/year (constrained) → Marcus signal
- Constraint: HIPAA compliance required → Jennifer signal

**Persona Match**:
- **Primary**: Jennifer (HIPAA non-negotiable)
- **Secondary**: Marcus (cost constraints real)
- **Confidence**: MEDIUM (hybrid scenario, conflicting priorities)

**Match Rationale**:
⚠️ **HYBRID SCENARIO** (Jennifer: 7, Marcus: 8):
- Jennifer signals: Healthcare industry, HIPAA required (regulatory driver)
- Marcus signals: Startup scale, $150K budget (very constrained), 8-person team (small)
- **Conflict**: Jennifer needs compliance pedigree (expensive), Marcus needs cost control

**Challenge**: HIPAA compliance typically requires $300K+ budget (Splunk, Sentinel)
- Jennifer's recommended vendors (Splunk $500K+, Sentinel $300K+) exceed Marcus's budget
- Marcus's recommended vendors (ClickHouse $60K, Honeycomb $80K) lack HIPAA BAA

---

## Hybrid Strategy: Compliance-First with Cost Optimization

**Tier 1 (Non-Negotiable - HIPAA Baseline)**:
- HIPAA BAA (must have, regulatory requirement)
- Encryption at rest + in transit (HIPAA § 164.312(a)(2)(iv))
- Audit logging (HIPAA § 164.312(b))

**Tier 2 (Cost Optimization - Marcus Constraints)**:
- Prefer cloud-native (no infrastructure management for 8-person team)
- Prefer consumption-based pricing (start small, scale with growth)
- Prefer minimal operational overhead (8-person team can't manage complex systems)

**Tier 3 (Nice-to-Have - Deferred for Startups)**:
- Enterprise support SLA (acceptable to use standard support)
- Advanced SIEM features (start with basic, upgrade later)

## Recommended Vendors (Hybrid Jennifer + Marcus)

| Vendor | Hybrid Fit | Compliance + Cost | Trade-off |
|--------|------------|-------------------|-----------|
| Microsoft Sentinel (Consumption) | ✅ Best hybrid fit | HIPAA BAA, pay-per-GB ($~120K/yr at 500GB/day) | Vendor lock-in (Azure) |
| Elastic Cloud (Enterprise) | ✅ Good fit | HIPAA with Enterprise license ($~150K/yr), open-source core | Self-managed compliance (more ops) |
| Dremio Cloud (Starter) | ⚠️ Emerging option | HIPAA support, lakehouse flexibility ($~180K/yr) | Exceeds budget slightly |

**Avoid**:
- ❌ Splunk ($500K+) - Exceeds budget 3×, over-engineered for startup
- ❌ ClickHouse/Honeycomb ($60-80K) - No HIPAA BAA (regulatory gap)

**Hybrid Trade-offs**:
- **Jennifer priority wins**: HIPAA BAA non-negotiable (regulatory requirement)
- **Marcus optimization**: Choose consumption pricing (Sentinel pay-per-GB vs Splunk fixed license)
- **Compromise**: Accept standard support (not premium SLA) to stay in budget

**Startup-Specific Guidance**:
1. **Year 1-2**: Microsoft Sentinel consumption pricing (~$120K/yr, HIPAA BAA included)
   - Start small (500GB/day), scale with growth
   - Leverage Azure's HIPAA infrastructure (no DIY compliance)
2. **Year 3-4**: Upgrade to Dremio/Splunk ($300K+/yr) when budget increases
   - Add advanced SIEM features, enterprise support
3. **Long-term**: Enterprise platform (Splunk $500K+) when mature

**Next Steps**:
1. Request Microsoft Sentinel HIPAA BAA (validate compliance baseline)
2. Calculate consumption pricing ($120K/yr est. at 500GB/day, verify with Azure calculator)
3. POC Sentinel (validate HIPAA audit logging, encryption)
4. Document cost-compliance trade-offs for stakeholders (HIPAA non-negotiable, budget real constraint)

**Confidence Check**:
⚠️ **MEDIUM CONFIDENCE** - Hybrid scenario requires trade-offs
- If budget non-negotiable: Sentinel ($120K) only viable option
- If HIPAA delayed (pre-revenue startup): Could use Marcus vendors temporarily, upgrade before patient data
- **Recommendation**: Consult with architect to confirm priority (compliance vs cost if forced to choose)
```

### 9. INTEGRATION WITH OTHER SKILLS

**Works WITH:**
- **security-vendor-filter**: Persona-specific Tier 1/2 filters (Jennifer = compliance-first, Marcus = cost-first)
- **tco-calculator**: Persona-specific TCO interpretation (Marcus emphasizes cost, Jennifer emphasizes compliance risk)
- **architecture-report-generator**: Persona narrative framing in final recommendation

**Sequence:**
1. **journey-persona-matcher**: Identify persona (Jennifer/Marcus/Priya)
2. **security-vendor-filter**: Apply persona-specific filters (compliance vs cost vs sovereignty)
3. **tco-calculator**: Calculate TCO with persona-weighted factors (Jennifer = compliance costs, Marcus = operational costs)
4. **architecture-report-generator**: Frame recommendation using persona journey narrative

**Example Workflow:**
```
User: "Healthcare startup, HIPAA required, $150K budget"
→ journey-persona-matcher: Jennifer + Marcus hybrid (HIPAA + cost constraints)
→ security-vendor-filter: Apply Jennifer Tier 1 (HIPAA BAA) + Marcus Tier 2 (cost < $150K)
→ tco-calculator: Calculate TCO for Sentinel (consumption pricing), Elastic (Enterprise)
→ architecture-report-generator: Frame as "Startup Compliance Journey" with cost-optimization roadmap
```

### 10. ANTI-PATTERNS

**DON'T:**
- ❌ Force-fit persona when ambiguous (acknowledge hybrid scenarios)
- ❌ Ignore cost constraints for Jennifer (healthcare ≠ unlimited budget)
- ❌ Ignore compliance for Marcus (FinTech may have PCI-DSS, SOC 2 requirements)
- ❌ Skip persona matching when signals clear (healthcare → Jennifer obvious)
- ❌ Recommend vendors misaligned with persona (Splunk for Marcus, ClickHouse for Jennifer)
- ❌ Fail to document persona match confidence (HIGH/MEDIUM/LOW)
- ❌ Assume single persona (many organizations are hybrid Jennifer + Priya)

**DO:**
- ✅ Acknowledge hybrid scenarios (Jennifer + Marcus common for healthcare startups)
- ✅ Document persona match confidence (HIGH when clear, MEDIUM when ambiguous)
- ✅ Prioritize persona requirements (Tier 1 non-negotiable, Tier 2 preferred, Tier 3 nice-to-have)
- ✅ Reference Book Chapter 4 narratives (Jennifer's journey provides context)
- ✅ Explain persona trade-offs (compliance vs cost, vendor support vs DIY)
- ✅ Adapt recommendations to persona (Splunk for Jennifer, ClickHouse for Marcus, Sentinel multi-region for Priya)
- ✅ Suggest persona evolution paths (Marcus → Jennifer as startup matures)

---

## Skill 4: architecture-report-generator

### Metadata
```yaml
name: Architecture Report Generator
description: Generate comprehensive 8-12 page architecture recommendation incorporating finalists (from security-vendor-filter), TCO analysis (from tco-calculator), persona guidance (from journey-persona-matcher), and POC evaluation criteria. Output: Architecture-Recommendation-YYYY-MM-DD.md
allowed-tools: Read, Write
```

### 1. IDENTITY

You are an architecture documentation specialist focused on creating comprehensive, stakeholder-ready architecture recommendations for security data platforms. Your role is to synthesize vendor filtering, TCO analysis, and persona guidance into a cohesive 8-12 page decision artifact that communicates technical analysis, trade-offs, and implementation roadmap to executives, architects, and engineers.

### 2. GOAL

Generate comprehensive 8-12 page architecture recommendation document combining vendor finalists (security-vendor-filter), 5-year TCO (tco-calculator), persona journey (journey-persona-matcher), POC evaluation criteria, risk assessment, and implementation roadmap. Provide stakeholder-ready markdown report (Architecture-Recommendation-YYYY-MM-DD.md) suitable for CISO/CIO communication.

### 3. CONTEXT RETRIEVAL

**Automatic** (always load when skill activates):
- All prior skill outputs:
  - security-vendor-filter finalists (3-5 vendors)
  - tco-calculator results (5-year TCO breakdown)
  - journey-persona-matcher guidance (Jennifer/Marcus/Priya)
- MCP Resource: `decision_state` (save complete analysis for future reference)
- Organization profile from conversation (industry, team, constraints)

**On-Demand** (query when needed during execution):
- Vendor reviews from knowledge base (01-knowledge-base/concepts/vendor-*.md)
- Production deployment case studies (peer validation)
- POC evaluation templates (from MCP server docs)

**Proactive** (suggest if relevant but not required):
- Similar architecture decisions (decision_state historical comparisons)
- Industry benchmarks (Gartner, IT-Harvest comparisons)
- Expert reviews (if available in knowledge base)

### 4. TRIGGER CONDITIONS

**ACTIVATE when user:**
- Ready to finalize decision, requests formal recommendation
- Says "Generate architecture report", "Create recommendation doc", "Prepare for stakeholders"
- Completed vendor filtering + TCO + persona matching (all prior skills done)
- Needs stakeholder communication artifact (CISO presentation, board deck)

**DO NOT ACTIVATE when:**
- Still exploring options (vendor filtering incomplete)
- TCO analysis not yet done (missing cost justification)
- User wants quick summary (not full 8-12 page report)
- User explicitly requests different format (PowerPoint, spreadsheet)

### 5. STEPS

#### Phase 1: Executive Summary (1-2 pages)

```
1. Organization profile summary (industry, team, constraints)
2. Persona match (Jennifer/Marcus/Priya) with rationale
3. Finalist vendors (3-5) with recommendation
4. Top recommendation with justification (1-2 sentences)
5. 5-year TCO summary (total, annual average)
6. Key trade-offs (cost vs completeness, DIY vs support, risk vs innovation)
7. Implementation timeline (POC → production)
```

#### Phase 2: Detailed Analysis (4-6 pages)

```
1. Vendor Comparison Table:
   - Capabilities (OCSF, Iceberg, query performance, etc.)
   - Compliance (HIPAA, SOC 2, GDPR, etc.)
   - Pricing (5-year TCO, annual breakdown)
   - Strengths/Weaknesses/Trade-offs

2. TCO Deep-Dive:
   - Platform costs (licensing, compute, storage)
   - Operational costs (FTE, training, support)
   - Hidden costs (migrations, integrations, maintenance)
   - Chart-ready data (CSV for stakeholder visualization)

3. Persona Journey Guidance:
   - Jennifer/Marcus/Priya-specific priorities
   - Implementation roadmap aligned with persona
   - Compliance/cost/sovereignty framing

4. Risk Assessment:
   - Vendor lock-in risk (commercial vs open-source)
   - Deployment complexity (cloud-native vs self-managed)
   - Support risk (vendor SLA, community support)
   - Technology maturity (proven vs emerging)
```

#### Phase 3: POC Evaluation Criteria (2-3 pages)

```
1. Vendor-Specific Test Plans:
   - Vendor A POC: Test X, Y, Z (detailed steps)
   - Vendor B POC: Test X, Y, Z (detailed steps)
   - Vendor C POC: Test X, Y, Z (detailed steps)

2. Success Criteria:
   - Must-have features (Tier 1 requirements)
   - Nice-to-have features (Tier 2 requirements)
   - Performance benchmarks (query speed, ingestion rate)
   - Operational complexity assessment (FTE effort, training time)

3. POC Timeline:
   - Week 1-2: Setup + data ingestion
   - Week 3-4: Feature validation
   - Week 5-6: Performance testing
   - Week 7-8: Final evaluation + recommendation
```

#### Phase 4: Appendices (1-2 pages)

```
1. Vendor Contact Information:
   - Sales contacts (POC coordination)
   - Technical support (pre-sales engineering)
   - Pricing quotes (formal TCO validation)

2. References:
   - Production case studies (peer validation)
   - Vendor documentation (capability verification)
   - Industry benchmarks (Gartner, IT-Harvest)

3. Decision State:
   - Save complete analysis to decision_state.json (MCP Resource)
   - Enable future reference, similar decision matching
```

#### Phase 5: Document Generation

```
1. Write markdown report: Architecture-Recommendation-YYYY-MM-DD.md
2. Save to appropriate location (project docs directory)
3. Generate summary for user (key highlights, next steps)
```

### 6. OUTPUT FORMAT

```markdown
# Security Data Platform Architecture Recommendation

**Organization**: [Name], [Industry], [Team Size]
**Prepared By**: Security Architect + AI Assistant
**Date**: October 19, 2025
**Status**: DRAFT - For Executive Review

---

## Executive Summary

### Organization Profile
- **Industry**: Healthcare (10,000 employees)
- **Team**: 50-person SOC, mature security organization
- **Constraints**: HIPAA compliance critical, $2M annual budget
- **Persona Match**: Jennifer (Compliance-First Healthcare SOC)

### Recommendation

**Top Recommendation**: **Splunk Enterprise** (Cloud, EU deployment)

**Rationale**:
- HIPAA BAA + SOC 2 Type 2 certified (compliance baseline met)
- 100+ healthcare customer references (peer validation)
- Comprehensive audit logging (HIPAA § 164.312(b) compliance)
- Enterprise SLA < 4 hours (breach response requirement)

**Trade-off**: Higher 5-year TCO ($9.2M) vs alternatives (Dremio $6.5M, Elastic $5.1M), but compliance pedigree justifies premium for Jennifer persona.

### Finalists (3 vendors evaluated)

| Vendor | 5-Year TCO | Compliance Strength | Recommendation |
|--------|------------|---------------------|----------------|
| **Splunk Enterprise** | **$9.2M** | ✅ HIPAA BAA, SOC 2, 100+ healthcare refs | **PRIMARY** |
| Dremio Cloud | $6.5M | ✅ HIPAA support, SOC 2, modern lakehouse | SECONDARY (if cost-conscious) |
| Elastic Cloud (Enterprise) | $5.1M | ⚠️ HIPAA with Enterprise license, self-managed compliance | TERTIARY (higher ops risk) |

### Implementation Timeline

- **Week 1-4**: POC evaluation (3 vendors parallel)
- **Week 5-6**: Final recommendation + stakeholder approval
- **Week 7-12**: Vendor negotiation + contract finalization
- **Month 4-6**: Production deployment + data migration
- **Month 7-12**: Full production rollout + legacy decommission

**Go-Live Target**: Q2 2026 (6 months from decision)

---

## Detailed Vendor Analysis

### Vendor Comparison Table

| Capability | Splunk Enterprise | Dremio Cloud | Elastic Cloud (Enterprise) |
|------------|-------------------|--------------|----------------------------|
| **Compliance** | | | |
| HIPAA BAA | ✅ Included | ✅ Included | ✅ Enterprise license required |
| SOC 2 Type 2 | ✅ Yes | ✅ Yes | ✅ Yes |
| Healthcare References | ✅ 100+ customers | ⚠️ 20+ customers (newer) | ⚠️ 30+ customers |
| **Technical** | | | |
| OCSF Support | ✅ Native | ✅ Native | ⚠️ Custom mapping required |
| Apache Iceberg | ⚠️ Roadmap (2026) | ✅ Native (production) | ⚠️ Experimental |
| Query Performance | ✅ Sub-second (proven) | ✅ Sub-second (lakehouse) | ✅ Sub-second (Elasticsearch) |
| Data Ingestion | ✅ 10 TB/day tested | ✅ 10 TB/day tested | ✅ 10 TB/day tested |
| **Operational** | | | |
| Deployment | ✅ Cloud-managed | ✅ Cloud-managed | ⚠️ Self-managed compliance |
| Support SLA | ✅ <4 hours (enterprise) | ✅ <8 hours (enterprise) | ⚠️ <24 hours (standard) |
| Training Required | ⚠️ Moderate (SPL query language) | ⚠️ Moderate (SQL + lakehouse concepts) | ✅ Low (SQL + Elasticsearch familiar) |
| **Pricing (5-Year TCO)** | | | |
| Platform Costs | $6.2M | $4.1M | $2.8M |
| Operational Costs | $2.5M | $2.0M | $2.0M |
| Hidden Costs | $500K | $400K | $300K |
| **Total TCO** | **$9.2M** | **$6.5M** | **$5.1M** |

### Strengths, Weaknesses, Trade-offs

**Splunk Enterprise**:
- ✅ **Strengths**: Compliance pedigree (HIPAA BAA, 100+ healthcare refs), enterprise support SLA, comprehensive audit logging
- ❌ **Weaknesses**: Highest TCO ($9.2M), proprietary SPL query language (learning curve), no native Iceberg (roadmap 2026)
- ⚖️ **Trade-offs**: Cost vs compliance maturity (Jennifer persona accepts premium for compliance)

**Dremio Cloud**:
- ✅ **Strengths**: Modern lakehouse architecture (Iceberg native), OCSF support, lower TCO ($6.5M), SQL-based queries
- ❌ **Weaknesses**: Fewer healthcare references (20+ vs Splunk 100+), newer vendor (less maturity)
- ⚖️ **Trade-offs**: Innovation vs proven track record (emerging vendor risk)

**Elastic Cloud (Enterprise)**:
- ✅ **Strengths**: Lowest TCO ($5.1M), open-source core (flexibility), familiar SQL + Elasticsearch
- ❌ **Weaknesses**: HIPAA requires Enterprise license (self-managed compliance), OCSF custom mapping (integration effort), lower support SLA
- ⚖️ **Trade-offs**: Cost vs operational complexity (higher ops burden for Jennifer persona)

---

## 5-Year TCO Analysis

### Cost Breakdown (All Vendors)

| Cost Category | Splunk Enterprise | Dremio Cloud | Elastic Cloud (Enterprise) |
|---------------|-------------------|--------------|----------------------------|
| **Year 1** | $2.1M | $1.5M | $1.2M |
| **Year 2** | $1.9M | $1.4M | $1.1M |
| **Year 3** | $1.8M | $1.3M | $1.0M |
| **Year 4** | $1.7M | $1.2M | $950K |
| **Year 5** | $1.7M | $1.1M | $850K |
| **5-Year Total** | **$9.2M** | **$6.5M** | **$5.1M** |

### TCO Assumptions

**Growth Modeling**:
- Data volume growth: 15% annual (healthcare industry benchmark)
- User growth: Stable (50-person SOC, no planned expansion)
- Vendor price increases: 5% annual (conservative)

**FTE Costs** (all vendors):
- SOC analysts (50 FTE): $6.5M over 5 years ($130K loaded cost each)
- Training (vendor-specific):
  - Splunk: $150K over 5 years (SPL learning curve)
  - Dremio: $120K over 5 years (SQL + lakehouse concepts)
  - Elastic: $100K over 5 years (SQL familiar, less training)

**Hidden Costs**:
- Migration (Year 1 heavy):
  - Splunk: $200K (comprehensive migration support)
  - Dremio: $150K (lakehouse transformation)
  - Elastic: $100K (self-managed migration)
- Integrations (Year 1 + ongoing):
  - All vendors: $300K over 5 years (SIEM playbook development, API integrations)

**Cost Drivers**:
1. **Splunk**: Platform licensing dominates (67% of TCO) - Per-GB pricing scales with data growth
2. **Dremio**: Balanced (platform 63%, ops 31%, hidden 6%)
3. **Elastic**: Operational costs dominate (39% of TCO) - Self-managed compliance adds FTE burden

### Chart-Ready Data (CSV)

```csv
Vendor,Year,Platform,Operational,Hidden,Total
Splunk,Year 1,1400000,600000,100000,2100000
Splunk,Year 2,1300000,500000,100000,1900000
Splunk,Year 3,1200000,500000,100000,1800000
Splunk,Year 4,1100000,500000,100000,1700000
Splunk,Year 5,1200000,400000,100000,1700000
Dremio,Year 1,1000000,400000,100000,1500000
Dremio,Year 2,900000,400000,100000,1400000
Dremio,Year 3,800000,400000,100000,1300000
Dremio,Year 4,700000,400000,100000,1200000
Dremio,Year 5,650000,400000,50000,1100000
Elastic,Year 1,700000,400000,100000,1200000
Elastic,Year 2,650000,350000,100000,1100000
Elastic,Year 3,600000,300000,100000,1000000
Elastic,Year 4,550000,300000,100000,950000
Elastic,Year 5,500000,300000,50000,850000
```

---

## Persona Guidance: Jennifer (Compliance-First Healthcare SOC)

### Jennifer's Priorities

**Tier 1 (Non-Negotiable)**:
- HIPAA BAA (Business Associate Agreement) - All 3 finalists provide ✅
- SOC 2 Type 2 audit - All 3 finalists provide ✅
- Comprehensive audit logging (HIPAA § 164.312(b)) - Splunk strongest ✅
- Healthcare customer references - Splunk 100+, Dremio 20+, Elastic 30+ ⚠️

**Tier 2 (Preferred)**:
- Enterprise support SLA - Splunk <4 hours ✅, Dremio <8 hours ⚠️, Elastic <24 hours ❌
- Vendor maturity - Splunk 20+ years ✅, Dremio 8 years ⚠️, Elastic 15 years ✅
- Compliance automation - Splunk pre-built reports ✅, others custom ⚠️

**Tier 3 (Nice-to-Have)**:
- Cost optimization - Splunk highest, Elastic lowest (not primary driver for Jennifer)
- Cutting-edge features (Iceberg) - Dremio strongest, Splunk roadmap (not critical)

### Jennifer's Recommendation: Splunk Enterprise

**Why Splunk Aligns with Jennifer**:
1. **Compliance Pedigree**: 100+ healthcare customers, proven HIPAA compliance track record
2. **Risk Mitigation**: Enterprise SLA <4 hours critical for breach response (HIPAA breach notification = 60 days)
3. **Audit-Readiness**: Pre-built HIPAA compliance reports (saves 40-60 hours/year compliance reporting)
4. **Vendor Trust**: 20+ years in market, Fortune 500 deployments, minimal vendor risk

**Jennifer's Trade-offs**:
- **Accept**: Higher TCO ($9.2M vs Dremio $6.5M) - Compliance premium justified
- **Accept**: Proprietary SPL query language - Training investment ($150K over 5 years) acceptable
- **Accept**: No native Iceberg (roadmap 2026) - Compliance > cutting-edge features

**Jennifer's Implementation Roadmap**:
1. **Phase 1 (Weeks 1-4)**: POC with compliance validation focus
   - Test audit logging completeness (user access, data queries, export)
   - Validate HIPAA BAA terms (data handling, breach notification, audit rights)
   - Review SOC 2 Type 2 report (vendor control effectiveness)
2. **Phase 2 (Weeks 5-8)**: Stakeholder communication
   - Present POC results to CISO/CIO (compliance validation artifacts)
   - Demonstrate audit-readiness (HIPAA compliance reports)
   - Justify TCO premium (compliance risk avoidance = $50K+ per HIPAA violation avoided)
3. **Phase 3 (Weeks 9-24)**: Production deployment
   - Vendor contract negotiation (multi-year ELA for 10-15% discount)
   - Data migration (200K using Splunk professional services)
   - Full production rollout (6-month timeline)

---

## POC Evaluation Criteria

### POC Timeline (8 Weeks, 3 Vendors Parallel)

**Week 1-2**: Setup + Data Ingestion
- Vendor-provided cloud instances (no infrastructure setup)
- Ingest 7 days of production data (test data volume: 70 TB total)
- Validate data parsing (OCSF schema mapping, field extraction)

**Week 3-4**: Feature Validation
- Test Tier 1 requirements (audit logging, encryption, HIPAA compliance)
- Test Tier 2 requirements (query performance, SIEM playbooks, alert correlation)
- Document feature gaps (missing capabilities, workarounds required)

**Week 5-6**: Performance Testing
- Query performance benchmarks (dashboard load times, ad-hoc queries)
- Ingestion rate testing (10 TB/day sustained, peak 15 TB/day)
- Operational complexity assessment (training time, FTE effort)

**Week 7-8**: Final Evaluation + Recommendation
- Score vendors (Tier 1 must-haves, Tier 2 nice-to-haves, performance benchmarks)
- Calculate actual TCO (based on POC resource usage, validate estimates)
- Prepare final recommendation (this document updated with POC results)

### Vendor-Specific Test Plans

#### Splunk Enterprise POC

**Must-Have Tests** (Tier 1):
1. **Audit Logging Completeness**:
   - Test: Query audit logs for user access, data queries, export operations
   - Success Criteria: 100% of user actions logged (HIPAA § 164.312(b) compliance)
   - Validation: Compare audit log vs actual actions (no gaps)

2. **HIPAA BAA Validation**:
   - Test: Review BAA terms (data handling, breach notification, audit rights)
   - Success Criteria: BAA covers all HIPAA requirements (§ 164.308-318)
   - Validation: Legal review by compliance team

3. **Encryption Validation**:
   - Test: Verify data encryption at rest (AES-256) and in transit (TLS 1.2+)
   - Success Criteria: FIPS 140-2 compliant encryption (HIPAA § 164.312(a)(2)(iv))
   - Validation: Request Splunk encryption certificates, test key management

**Nice-to-Have Tests** (Tier 2):
1. **Query Performance**:
   - Test: Dashboard load times (10 concurrent users), ad-hoc query response (1 TB dataset)
   - Success Criteria: <3 seconds for dashboards, <10 seconds for ad-hoc queries
   - Validation: Run 100 queries, measure P50/P95/P99 latencies

2. **SIEM Playbook Migration**:
   - Test: Migrate 10 detection rules from legacy SIEM to Splunk SPL
   - Success Criteria: 80%+ rules migrate with <4 hours effort each
   - Validation: Test migrated rules against historical data (validate detection accuracy)

**Cost Validation**:
- Test: Monitor POC resource usage (compute, storage, ingestion)
- Success Criteria: Actual usage within 20% of TCO estimate
- Validation: Request Splunk invoice for POC period, extrapolate to annual cost

#### Dremio Cloud POC

**Must-Have Tests** (Tier 1):
1. **HIPAA Compliance Validation**:
   - Test: Same as Splunk (audit logging, BAA, encryption)
   - Success Criteria: Same HIPAA compliance baseline
   - Validation: Dremio BAA review, encryption validation

2. **Iceberg Integration**:
   - Test: Ingest data into Apache Iceberg tables, query with Dremio SQL
   - Success Criteria: OCSF schema mapping works (field extraction, data types correct)
   - Validation: Compare Dremio query results vs source data (accuracy check)

**Nice-to-Have Tests** (Tier 2):
1. **Lakehouse Performance**:
   - Test: Query performance on Iceberg tables (10 concurrent users, 1 TB dataset)
   - Success Criteria: <5 seconds for dashboards (slightly slower than Splunk acceptable)
   - Validation: Run 100 queries, compare vs Splunk performance

2. **Operational Complexity**:
   - Test: Train 2 SOC analysts on Dremio SQL + lakehouse concepts
   - Success Criteria: Analysts productive in <2 weeks (vs Splunk SPL 3-4 weeks)
   - Validation: Measure time to write first functional query

#### Elastic Cloud (Enterprise) POC

**Must-Have Tests** (Tier 1):
1. **HIPAA Compliance (Enterprise License)**:
   - Test: Validate Enterprise license includes HIPAA BAA (not open-source core)
   - Success Criteria: BAA provided, audit logging available
   - Validation: Legal review Elastic Enterprise BAA

2. **OCSF Mapping**:
   - Test: Custom OCSF schema mapping (field extraction, data normalization)
   - Success Criteria: 90%+ OCSF fields mapped (some custom development acceptable)
   - Validation: Compare Elastic data vs OCSF schema spec (field completeness)

**Nice-to-Have Tests** (Tier 2):
1. **Self-Managed Compliance Effort**:
   - Test: Assess FTE effort for compliance management (audit logs, encryption validation, reporting)
   - Success Criteria: <10 hours/month FTE effort (acceptable operational overhead)
   - Validation: Document required tasks, estimate time (compare vs Splunk/Dremio managed)

2. **Cost Validation**:
   - Test: Monitor Elastic Cloud usage (compute, storage, support)
   - Success Criteria: Actual cost <$1.2M/year (validate lowest TCO)
   - Validation: Request Elastic invoice for POC, extrapolate annual

### POC Success Criteria Summary

| Criterion | Splunk Enterprise | Dremio Cloud | Elastic Cloud (Enterprise) |
|-----------|-------------------|--------------|----------------------------|
| **Tier 1 (Must-Have)** | | | |
| HIPAA BAA | ✅ Must provide | ✅ Must provide | ✅ Must provide (Enterprise) |
| Audit Logging | ✅ 100% coverage | ✅ 100% coverage | ✅ 100% coverage |
| Encryption (FIPS 140-2) | ✅ Must validate | ✅ Must validate | ✅ Must validate |
| **Tier 2 (Performance)** | | | |
| Query Performance | <3 sec dashboards | <5 sec dashboards | <3 sec dashboards |
| Ingestion Rate | 10 TB/day sustained | 10 TB/day sustained | 10 TB/day sustained |
| **Tier 2 (Operational)** | | | |
| Training Time | <4 weeks (SPL) | <2 weeks (SQL) | <2 weeks (SQL + Elasticsearch) |
| FTE Effort | <5 hours/month (managed) | <5 hours/month (managed) | <10 hours/month (self-managed) |
| **Cost Validation** | | | |
| Year 1 TCO | $2.1M ± 20% | $1.5M ± 20% | $1.2M ± 20% |

---

## Risk Assessment

### Vendor Lock-In Risk

| Vendor | Lock-In Risk | Mitigation |
|--------|--------------|------------|
| Splunk Enterprise | ⚠️ **HIGH** - Proprietary SPL, vendor-specific data format | Plan data export strategy (Iceberg migration roadmap 2026) |
| Dremio Cloud | ✅ **LOW** - Open lakehouse (Iceberg), standard SQL | Iceberg tables portable to other query engines (DuckDB, Trino) |
| Elastic Cloud | ⚠️ **MEDIUM** - Open-source core, but Enterprise features proprietary | Open-source core enables migration, Enterprise features may require rebuild |

### Deployment Complexity Risk

| Vendor | Complexity Risk | Mitigation |
|--------|-----------------|------------|
| Splunk Enterprise | ✅ **LOW** - Cloud-managed, vendor-handled infrastructure | Splunk manages upgrades, patching, scaling (minimal SOC effort) |
| Dremio Cloud | ✅ **LOW** - Cloud-managed lakehouse | Dremio manages Iceberg compaction, query optimization |
| Elastic Cloud | ⚠️ **MEDIUM** - Self-managed compliance, OCSF custom mapping | Budget 10 hours/month FTE for compliance management, OCSF maintenance |

### Support Risk

| Vendor | Support Risk | Mitigation |
|--------|--------------|------------|
| Splunk Enterprise | ✅ **LOW** - Enterprise SLA <4 hours, 24/7 support | Proven track record, healthcare-specific support team |
| Dremio Cloud | ⚠️ **MEDIUM** - Enterprise SLA <8 hours (slower than Splunk) | Acceptable for non-critical incidents, escalate critical to <4 hours |
| Elastic Cloud | ⚠️ **MEDIUM** - Standard SLA <24 hours (Enterprise upgrade available) | Upgrade to Enterprise support ($50K+/year) if <4 hour SLA required |

### Technology Maturity Risk

| Vendor | Maturity Risk | Mitigation |
|--------|---------------|------------|
| Splunk Enterprise | ✅ **LOW** - 20+ years in market, proven at scale | Minimal risk, extensive production deployments |
| Dremio Cloud | ⚠️ **MEDIUM** - 8 years, fewer healthcare references (20+ vs Splunk 100+) | Request healthcare case studies, validate production deployments |
| Elastic Cloud | ✅ **LOW** - 15 years, widely deployed | Open-source core = extensive community validation |

---

## Appendices

### Appendix A: Vendor Contact Information

**Splunk Enterprise**:
- Sales: [splunk-healthcare-sales@splunk.com](mailto:splunk-healthcare-sales@splunk.com)
- Pre-Sales Engineering: [splunk-presales@splunk.com](mailto:splunk-presales@splunk.com)
- POC Coordination: Request via sales (cloud instance provisioning)

**Dremio Cloud**:
- Sales: [sales@dremio.com](mailto:sales@dremio.com)
- Pre-Sales Engineering: [solutions@dremio.com](mailto:solutions@dremio.com)
- POC Coordination: Self-service cloud trial (14-day) or request extended POC

**Elastic Cloud (Enterprise)**:
- Sales: [elastic-enterprise-sales@elastic.co](mailto:elastic-enterprise-sales@elastic.co)
- Pre-Sales Engineering: [elastic-presales@elastic.co](mailto:elastic-presales@elastic.co)
- POC Coordination: Self-service cloud trial (14-day) or request extended POC

### Appendix B: References

**Production Case Studies**:
- Splunk Healthcare: [splunk.com/customers/healthcare](https://www.splunk.com/customers/healthcare) (100+ references)
- Dremio Healthcare: Request from sales (20+ references, not all public)
- Elastic Healthcare: [elastic.co/customers/healthcare](https://www.elastic.co/customers/healthcare) (30+ references)

**Vendor Documentation**:
- Splunk HIPAA Compliance: [docs.splunk.com/Documentation/Splunk/latest/Security/HIPAA](https://docs.splunk.com/Documentation/Splunk/latest/Security/HIPAA)
- Dremio HIPAA: [docs.dremio.com/security/hipaa](https://docs.dremio.com/security/hipaa)
- Elastic HIPAA: [elastic.co/what-is/hipaa](https://www.elastic.co/what-is/hipaa) (Enterprise license required)

**Industry Benchmarks**:
- Gartner Magic Quadrant for SIEM (2025)
- IT-Harvest Security Data Platform Comparison (2025)
- Forrester Wave: Security Analytics Platforms (2024)

### Appendix C: Decision State (Saved to MCP Resource)

This complete analysis saved to `decision_state.json` (MCP Resource) for:
- Future reference (similar decisions, retrospective analysis)
- Similar organization matching (peer comparison)
- Vendor database updates (pricing validation, capability changes)

**Saved Decision State**:
```json
{
  "decision_id": "healthcare-siem-2025-10-19",
  "organization": {
    "industry": "healthcare",
    "team_size": 50,
    "constraints": ["HIPAA", "EU data residency"],
    "budget": 2000000
  },
  "persona": "Jennifer",
  "finalists": ["Splunk Enterprise", "Dremio Cloud", "Elastic Cloud (Enterprise)"],
  "recommendation": "Splunk Enterprise",
  "tco_5yr": {
    "Splunk Enterprise": 9200000,
    "Dremio Cloud": 6500000,
    "Elastic Cloud (Enterprise)": 5100000
  },
  "decision_date": "2025-10-19",
  "poc_status": "pending"
}
```

---

## Next Steps

1. **Week 1 (Oct 21-25)**: Initiate POC coordination
   - Contact Splunk, Dremio, Elastic sales (request cloud instances)
   - Prepare 70 TB production data sample (7 days, anonymized PHI)
   - Schedule POC kickoff meetings (technical scope review)

2. **Week 2-9 (Oct 28 - Dec 20)**: Execute POC (8-week timeline)
   - Follow vendor-specific test plans (documented above)
   - Weekly POC status meetings (track progress, blockers)
   - Document results in POC evaluation spreadsheet

3. **Week 10-11 (Dec 23 - Jan 3)**: Final recommendation update
   - Update this document with POC results (actual vs estimated performance)
   - Validate TCO estimates (actual POC costs vs projections)
   - Prepare stakeholder presentation (CISO/CIO approval)

4. **Week 12+ (Jan 2026)**: Vendor negotiation + deployment
   - Negotiate multi-year contract (target 10-15% discount for ELA)
   - Finalize SOW (professional services, migration support)
   - Begin production deployment (6-month timeline)

**Go-Live Target**: Q2 2026 (July 1, 2026)

---

**Document Status**: DRAFT - Pending POC Validation
**Next Review**: Week 10 (POC completion, final recommendation update)
**Stakeholder Approval Required**: CISO, CIO, CTO, Compliance Officer
**Budget Authority**: CFO sign-off for >$5M 5-year commitment
```

### 7. VERIFICATION

**Facts vs Assumptions:**
- **Confirmed Facts**: All data from prior skills (vendor finalists, TCO, persona) are facts (sourced from systematic analysis)
- **Assumptions Requiring Validation**: POC results (estimated performance), TCO validation (actual vs projected costs), vendor pricing (quote-based vs public pricing)
- **Mark Clearly**: ✅ CONFIRMED (from prior skills) vs ⚠️ ASSUMPTION (requires POC validation)

**Evidence Requirements:**
- **Tier A**: Prior skill outputs (vendor finalists, TCO analysis, persona match) are Tier A evidence (systematic methodology)
- **Tier B**: Vendor documentation (HIPAA BAA, SOC 2 reports) are Tier B evidence (vendor-provided, verifiable)
- **Tier C**: POC estimates (performance projections, TCO assumptions) are Tier C evidence (requires validation)

**Source Attribution:**
- Cite prior skill outputs (security-vendor-filter lines X-Y, tco-calculator table Z)
- Reference vendor documentation (HIPAA compliance guide URL, SOC 2 report date)
- Document POC assumptions (performance benchmarks from vendor claims, TCO from public pricing)

**Quality Checklist:**
- [ ] Executive summary complete (1-2 pages, clear recommendation)
- [ ] Vendor comparison table comprehensive (capabilities, compliance, pricing, trade-offs)
- [ ] TCO analysis detailed (platform + operational + hidden costs, 5-year projection)
- [ ] Persona guidance integrated (Jennifer/Marcus/Priya priorities reflected)
- [ ] POC evaluation criteria specific (vendor-specific test plans, success criteria)
- [ ] Risk assessment thorough (lock-in, complexity, support, maturity)
- [ ] Appendices complete (vendor contacts, references, decision state saved)
- [ ] Next steps clear (POC timeline, stakeholder approval, deployment roadmap)

### 8. EXAMPLES

(Due to length, architecture-report-generator OUTPUT FORMAT section above serves as the primary example. Full 8-12 page report structure demonstrated.)

### 9. INTEGRATION WITH OTHER SKILLS

**Works WITH:**
- **security-vendor-filter**: Finalists feed into report (vendor comparison section)
- **tco-calculator**: TCO analysis feeds into report (cost breakdown section)
- **journey-persona-matcher**: Persona guidance feeds into report (recommendation framing, implementation roadmap)

**Sequence:**
1. **security-vendor-filter**: Reduce 80+ → 3-5 finalists
2. **tco-calculator**: Calculate 5-year TCO for each finalist (parallel)
3. **journey-persona-matcher**: Identify persona (Jennifer/Marcus/Priya)
4. **architecture-report-generator**: FINAL STEP - Synthesize all prior outputs into comprehensive report

**Example Workflow:**
```
User: "Generate architecture recommendation for my healthcare SIEM decision"
→ Validate: security-vendor-filter complete? (3-5 finalists) ✅
→ Validate: tco-calculator complete? (5-year TCO for finalists) ✅
→ Validate: journey-persona-matcher complete? (Jennifer persona identified) ✅
→ architecture-report-generator: Synthesize → Architecture-Recommendation-2025-10-19.md
→ Save decision_state.json (MCP Resource) for future reference
→ Return summary + next steps to user
```

### 10. ANTI-PATTERNS

**DON'T:**
- ❌ Generate report without prior skill outputs (vendor finalists, TCO, persona missing)
- ❌ Skip executive summary (stakeholders need 1-page overview)
- ❌ Omit trade-offs (every vendor has weaknesses, document honestly)
- ❌ Fail to save decision_state (future similar decisions lose context)
- ❌ Provide generic POC criteria (vendor-specific test plans required)
- ❌ Ignore risk assessment (deployment complexity, vendor lock-in matter)
- ❌ Missing next steps (stakeholders need actionable timeline)

**DO:**
- ✅ Validate all prior skills complete before generating report (vendor finalists, TCO, persona)
- ✅ Provide executive summary (1-2 pages, clear recommendation, key trade-offs)
- ✅ Document vendor comparison systematically (capabilities, compliance, pricing, strengths/weaknesses)
- ✅ Include TCO deep-dive (platform + operational + hidden, 5-year projection, chart-ready data)
- ✅ Integrate persona guidance (Jennifer/Marcus/Priya priorities reflected throughout)
- ✅ Provide vendor-specific POC test plans (must-have vs nice-to-have tests, success criteria)
- ✅ Assess risks honestly (lock-in, complexity, support, maturity)
- ✅ Save decision_state.json (MCP Resource) for future reference
- ✅ Provide clear next steps (POC timeline, stakeholder approval, deployment roadmap)

---

**Document Status**: Design specifications complete, ready for November implementation (Week 2: Nov 9-15)
**Next Actions**:
1. Begin Week 1 MCP server simplification (remove Tools/Prompts, keep Resources)
2. Implement 4 skills in Week 2 using these specifications
3. Migrate 178 tests in Week 3 (skill-aware wrappers)

**Estimated Implementation Time**: 12-15 hours (Week 2), 3-4 hours per skill
