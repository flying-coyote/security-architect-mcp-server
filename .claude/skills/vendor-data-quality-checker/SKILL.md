---
name: Vendor Data Quality Checker
description: Maintain evidence-based quality standards for security data platform vendor database (64+ vendors expanding to 80+) when user adds or updates vendor entries. Trigger when user mentions "add vendor", "update vendor", "vendor database", "capability score", or modifies vendor_database.json. Ensure no marketing hype in descriptions, capability scores evidence-based with Tier 1-3 validation, cost models accurate, all 9 capability categories scored, and vendor claims cross-referenced with book Chapter 5. Prevent vendor bias from entering database.
allowed-tools: Read, Grep, Edit
---

# Vendor Data Quality Checker

## Purpose
Maintain evidence-based, bias-free quality standards for the 64+ vendor database (expanding to 80+) that powers the Security Architect MCP Server's decision support tool. Prevent marketing hype and ensure all vendor claims are validated against evidence tiers.

## Trigger Conditions

**ACTIVATE when user:**
- Adds new vendors to database (`vendor_database.json`)
- Updates existing vendor entries (capabilities, costs, descriptions)
- Says "add vendor", "update vendor database", "vendor entry", "capability score"
- Reviews vendor information for accuracy
- Mentions "check vendor data", "validate vendor claims"
- Prepares vendor database expansion (64 → 80 vendors)

**DO NOT ACTIVATE when:**
- User is researching vendors (not adding to database)
- Reading book Chapter 5 for reference (not database work)
- Discussing vendors in blog posts (different context)
- User explicitly says "rough draft" or "placeholder data"

## Vendor Quality Standards Protocol

### Step 1: Required Fields Validation

**Every vendor entry MUST have complete schema:**

```json
{
  "id": "vendor_XXX",
  "name": "[Vendor Name]",
  "category": "[query_engine|catalog|lakehouse|siem|streaming|storage|observability|governance|integration]",
  "cost_model": "[per_gb|consumption|subscription|oss|hybrid]",
  "tier1_filters": {
    "min_budget": [number],
    "min_team_size": "[small|medium|large]",
    "supports_on_prem": [boolean],
    "supports_cloud": [boolean],
    "data_sovereignty_compliant": [boolean]
  },
  "tier2_capabilities": {
    "query_performance": [0-5],
    "schema_flexibility": [0-5],
    "security_integration": [0-5],
    "data_lake_support": [0-5],
    "real_time_capability": [0-5],
    "cost_efficiency": [0-5],
    "ease_of_use": [0-5],
    "ecosystem_maturity": [0-5],
    "vendor_support": [0-5]
  },
  "description": "[Evidence-based, no marketing hype]",
  "evidence_tier": [1-5],
  "production_deployments": ["[Company (Contact)] if Tier 1", "..."],
  "book_chapter5_reference": "[Page number or section]",
  "last_validated": "[YYYY-MM-DD]"
}
```

**Validation Checklist:**
- [ ] All required fields present (id, name, category, cost_model, etc.)
- [ ] ID follows `vendor_XXX` format (sequential numbering)
- [ ] Category is valid enum value
- [ ] Cost model is valid enum value
- [ ] All 9 tier2_capabilities scored (0-5 scale)
- [ ] Evidence tier assigned (1-5)
- [ ] Description exists and is non-empty
- [ ] Last_validated is recent (<6 months old)

### Step 2: Evidence-Based Capability Scoring

**Capability scores MUST be evidence-based, not vendor claims.**

**Evidence Tier Requirements by Score:**

**Score 5 (Exceptional):**
- ✅ Tier 1 evidence: Production deployments with measured outcomes
- ✅ Specific metrics documented: "Production environment sustains 100K QPS"
- ✅ Multiple independent confirmations
- ❌ Cannot be based solely on vendor marketing

**Score 4 (Strong):**
- ✅ Tier 2 evidence: Peer-reviewed research or industry benchmarks
- ✅ Expert consensus from multiple sources
- ✅ Documented production use (even without specific metrics)

**Score 3 (Adequate):**
- ✅ Tier 3 evidence: Expert opinion or framework inclusion (NIST, MITRE)
- ✅ Vendor documentation with plausible claims
- ✅ Community adoption visible (GitHub stars, conference talks)

**Score 2 (Limited):**
- ✅ Tier 4 evidence: Vendor claims only
- ⚠️ Must be marked as unvalidated in description
- ⚠️ Cannot be primary recommendation

**Score 1 (Weak):**
- ✅ Tier 5 evidence: Theoretical capability
- ⚠️ Feature exists but no production validation
- ⚠️ Must note "unvalidated in production" in description

**Score 0 (Not Applicable / Not Supported):**
- ✅ Feature explicitly not supported
- ✅ Use case not applicable to this vendor

**Scoring Validation Process:**

```bash
# For each capability score >= 4, verify evidence
Grep: Book Chapter 5 for vendor production deployments
Grep: MASTER-BIBLIOGRAPHY.md for peer-reviewed sources
Grep: Vendor descriptions for specific metrics

# Example checks:
# - query_performance: 5 requires production benchmark data
# - security_integration: 4 requires documented SIEM integrations
# - ecosystem_maturity: 5 requires broad adoption evidence
```

**Common Scoring Errors:**

❌ **Over-scoring based on vendor marketing:**
```json
// WRONG: Vendor claims "best-in-class performance" without evidence
{"query_performance": 5}  // No production metrics documented

// CORRECT: Vendor claims not validated
{"query_performance": 2}  // Note in description: "Vendor claims high performance (unvalidated)"
```

❌ **Under-scoring proven capabilities:**
```json
// WRONG: Platform has documented Iceberg support (production validated)
{"data_lake_support": 3}  // Should be 5

// CORRECT: Tier 1 evidence exists
{"data_lake_support": 5}  // Production deployment documented
```

### Step 3: Marketing Hype Detection

**Vendor descriptions MUST be evidence-based, not marketing material.**

**✓ GOOD Descriptions (evidence-based):**
```json
{
  "name": "DuckDB",
  "description": "Embedded columnar database optimized for analytical queries. Sustains 100K QPS with sub-second latency in production deployments (2024 validation). Open source (MIT license), no infrastructure overhead. Limited: No native distributed processing, single-node only. Best for: Edge processing, embedded analytics, cost-sensitive deployments."
}
```

**✗ BAD Descriptions (marketing hype):**
```json
{
  "name": "Vendor X",
  "description": "Revolutionary AI-powered platform that transforms security operations. Industry-leading performance with game-changing capabilities. Best-in-class solution for modern SOCs."
  // ❌ No specific metrics, pure marketing language
}
```

**Hype Detection Patterns:**

**RED FLAGS (Remove or require evidence):**
- ❌ "Revolutionary", "game-changing", "transformative"
- ❌ "Best-in-class", "industry-leading", "world-class"
- ❌ "Unmatched", "unparalleled", "unprecedented"
- ❌ "Complete solution", "solves all problems", "handles everything"
- ❌ Superlatives without specific comparison ("fastest", "cheapest", "easiest")
- ❌ Vague benefits ("increases efficiency", "reduces costs") without numbers

**REQUIRED SPECIFICS (Must include):**
- ✅ Specific capabilities with evidence tier
- ✅ Production deployment examples (if Tier 1 evidence)
- ✅ Quantitative metrics (QPS, latency, cost, throughput)
- ✅ Known limitations documented
- ✅ Scope boundaries ("Best for: X use case, Not suitable for: Y use case")
- ✅ Cost model clearly stated
- ✅ Trade-offs acknowledged

**Description Template:**
```
[Vendor Name] provides [specific capability]. [Evidence: production deployment/peer-reviewed/expert consensus].
[Quantitative metric if available]. [Known limitation].
Best for: [specific use case].
Not suitable for: [specific use case where it fails].
```

### Step 4: Cost Model Validation

**Cost models MUST accurately reflect actual pricing structures.**

**Valid Cost Models:**

**per_gb (Per-GB Storage/Query):**
```json
{
  "cost_model": "per_gb",
  "tier1_filters": {
    "min_budget": 50000  // Typical starting cost
  },
  "description": "... Pricing: $X per GB stored, $Y per GB scanned. Cost scales with data volume and query frequency."
}
```

**consumption (Pay-per-query):**
```json
{
  "cost_model": "consumption",
  "tier1_filters": {
    "min_budget": 25000  // Can start smaller, scales with usage
  },
  "description": "... Pricing: Pay per query execution. Cost scales with query complexity and frequency. Typical: $X per 1M queries."
}
```

**subscription (Fixed annual/monthly):**
```json
{
  "cost_model": "subscription",
  "tier1_filters": {
    "min_budget": 100000  // Typical enterprise minimum
  },
  "description": "... Pricing: Fixed annual subscription starting at $X. Includes Y TB of data, Z queries/day. Overage: $A per GB."
}
```

**oss (Open source, infrastructure costs only):**
```json
{
  "cost_model": "oss",
  "tier1_filters": {
    "min_budget": 10000  // Infrastructure + staffing minimum
  },
  "description": "... Pricing: Open source (Apache/MIT license). Costs: Infrastructure ($X/month for Y TB), staffing (0.5-1 FTE for operations). No licensing fees."
}
```

**hybrid (Mix of subscription + consumption):**
```json
{
  "cost_model": "hybrid",
  "tier1_filters": {
    "min_budget": 75000  // Base subscription + consumption buffer
  },
  "description": "... Pricing: Base subscription $X/year + consumption fees $Y per GB scanned. Cost model optimized for: [specific workload]."
}
```

**Cost Model Validation:**
- [ ] Cost model matches actual vendor pricing structure
- [ ] Min_budget is realistic for this vendor (not placeholder)
- [ ] Description includes cost guidance (even if approximate)
- [ ] Cost model is consistent with vendor category
- [ ] Hidden costs documented (egress, support, migration)

### Step 5: Cross-Reference with Book Chapter 5

**Vendor data MUST be consistent with book's vendor landscape analysis.**

```bash
# Check book reference
Read: /home/jerem/modern-data-stack-for-cybersecurity-book/chapters/05-vendor-landscape.md

# Verify consistency:
# - Vendor categorization matches book
# - Capability assessments align with book's analysis
# - Production deployments cited in book are in database
# - Cost guidance matches book's TCO analysis
```

**Consistency Checks:**
- [ ] Vendor category matches book Chapter 5 classification
- [ ] Capability scores align with book's assessment
- [ ] Production deployments cited in book are in `production_deployments` field
- [ ] Cost model matches book's TCO discussion
- [ ] Limitations noted in book are in database description
- [ ] Book_chapter5_reference points to correct section

**If inconsistency found:**
```
Inconsistency Detected:

Vendor: [Name]
Field: [capability_score / description / cost_model]

Database says: [Database value]
Book Chapter 5 says: [Book value]

Resolution needed:
- [ ] Update database to match book (if book is more recent/accurate)
- [ ] Update book to match database (if database has new validation)
- [ ] Add note explaining difference (if both are valid in different contexts)
```

### Step 6: Production Deployment Validation

**Tier 1 evidence requires documented production deployments.**

**✓ VALID Production Deployment Documentation:**
```json
{
  "evidence_tier": 1,
  "production_deployments": [
    "Enterprise A - 100K QPS, sub-second latency (2024)",
    "Enterprise B - 10TB/day, 85% cost reduction (2024)"
  ],
  "description": "... Production-validated: 100K QPS with sub-second latency (2024 validation)."
}
```

**✗ INVALID Production Deployment Claims:**
```json
{
  "evidence_tier": 1,  // ❌ Claims Tier 1 but no production deployments
  "production_deployments": [],
  "description": "Used by many Fortune 500 companies."  // ❌ Vague, no specific contacts
}
```

**Production Deployment Standards:**
- ✅ Organization type or anonymized reference
- ✅ Specific metrics (QPS, latency, volume, cost reduction)
- ✅ Validation date (within 24 months)
- ✅ Evidence tier 1 ONLY if production deployments documented
- ❌ Generic claims ("many customers", "Fortune 500 companies")
- ❌ Vendor-provided case studies without independent validation
- ❌ Theoretical deployments ("could handle...", "designed for...")

### Step 7: Capability Category Completeness

**All 9 categories MUST be scored (0-5) with rationale.**

**Required Capability Categories:**

1. **query_performance**: Query execution speed, latency, throughput
   - Evidence: Benchmarks, production QPS data, query latency measurements

2. **schema_flexibility**: Schema evolution, schema-on-read, flexible data models
   - Evidence: Production schema changes, Iceberg/Delta support, documented migrations

3. **security_integration**: SIEM/SOAR integration, auth/authz, compliance
   - Evidence: Native integrations, SSO support, compliance certifications

4. **data_lake_support**: Iceberg/Delta/Hudi, object storage, catalog integration
   - Evidence: Native table format support, catalog integrations (Gravitino, etc.)

5. **real_time_capability**: Streaming ingestion, real-time queries, low-latency detection
   - Evidence: Streaming benchmarks, production latency data, streaming frameworks

6. **cost_efficiency**: Price/performance ratio, cost predictability, hidden costs
   - Evidence: TCO calculations, production cost data, pricing transparency

7. **ease_of_use**: Learning curve, SQL compatibility, UI/UX quality
   - Evidence: User surveys, training time, SQL standards compliance

8. **ecosystem_maturity**: Community size, integration availability, documentation quality
   - Evidence: GitHub activity, connector count, Stack Overflow questions

9. **vendor_support**: SLA availability, support quality, professional services
   - Evidence: Published SLAs, support tier pricing, documented response times

**Scoring Validation:**
```bash
# For each vendor, verify all 9 categories scored
Grep: vendor_database.json for vendor entry
# Check: All keys in tier2_capabilities present
# Check: All scores are 0-5 (not missing, not out of range)
```

**Common Completeness Errors:**
- ❌ Missing capability category (only 8 of 9 scored)
- ❌ Score out of range (6, -1, null)
- ❌ Placeholder scores (all 3s without evidence)
- ❌ Inconsistent scoring across similar vendors

## Quality Check Response Structure

Provide vendor data quality assessment in this format:

```
Vendor Data Quality Check
=========================

VENDOR: [Name]
VENDOR ID: vendor_XXX
CATEGORY: [Category]
EVIDENCE TIER: [1-5]

REQUIRED FIELDS:
✅ All required fields present
⚠️ Missing: production_deployments (required for Tier 1)
✅ book_chapter5_reference: Page 127

CAPABILITY SCORING:

query_performance: 5
Evidence: ✅ Tier 1 - Production deployment: 100K QPS (2024 validation)
Status: ✅ VALIDATED

schema_flexibility: 4
Evidence: ⚠️ Tier 3 - Expert consensus only, no production metrics
Status: ⚠️ NEEDS VALIDATION - Consider downgrading to 3

security_integration: 2
Evidence: ✅ Tier 4 - Vendor claims only
Status: ✅ CORRECTLY SCORED (marked as unvalidated in description)

[... all 9 categories ...]

MARKETING HYPE DETECTION:

Description: "DuckDB provides embedded columnar database..."
✅ No marketing hype detected
✅ Specific metrics provided (100K QPS)
✅ Limitations documented (single-node only)
✅ Scope boundaries clear (best for edge processing)

Alternative vendor description: "Revolutionary AI-powered platform..."
❌ MARKETING HYPE: "Revolutionary" (no evidence)
❌ MARKETING HYPE: "AI-powered" (not relevant to capabilities)
❌ VAGUE CLAIMS: No specific metrics
❌ MISSING LIMITATIONS: No documented constraints

Suggested revision: "Vendor X provides [specific capability]. [Evidence]. Best for: [use case]. Limited: [constraint]."

COST MODEL VALIDATION:

Cost Model: subscription
Min Budget: $100,000
Status: ✅ REALISTIC for enterprise subscription
Description includes: ✅ Base subscription pricing, ✅ overage fees
Missing: ⚠️ Support tier costs not mentioned

PRODUCTION DEPLOYMENT VALIDATION:

Evidence Tier: 1 (Production)
Production Deployments:
✅ "Enterprise A - 100K QPS, sub-second latency (2024)"
✅ Metrics specific, validation documented
✅ Validation date: 2024 (within 24 months)

Status: ✅ TIER 1 EVIDENCE VALIDATED

BOOK CHAPTER 5 CROSS-REFERENCE:

Database capability scores: query_performance=5, schema_flexibility=4
Book Chapter 5 assessment: "High performance (5/5), Good flexibility (4/5)"
Status: ✅ CONSISTENT

OVERALL QUALITY: ✅ PASS / ⚠️ NEEDS IMPROVEMENT / ❌ FAILS STANDARDS

REQUIRED ACTIONS:
Priority 1 (Blocking):
1. [Fix critical issue]

Priority 2 (Quality):
1. Downgrade schema_flexibility from 4 to 3 (no production metrics)
2. Add support tier costs to description

Priority 3 (Enhancement):
1. Add second production deployment reference (increase confidence)

PUBLICATION READINESS: [Ready / Needs fixes / Major revision]
```

## Integration with Other Skills

**Works WITH:**
- **mcp-schema-validator** (MCP project): Validates vendor database JSON schema
- **academic-citation-manager** (personal): Evidence tier classification
- **evidence-tier-classifier** (lit-review): Same tier 1-5 system
- **publication-quality-checker** (project1): Evidence-based standards

**Sequence:**
1. User adds/updates vendor in database
2. **mcp-schema-validator** → Validates JSON schema structure
3. **vendor-data-quality-checker** → Validates content quality, evidence, no hype
4. **systematic-debugger** → Debug if MCP server fails to load vendor data

## MCP Project Context

**Current Status:**
- 64 vendors in database (expanding to 80)
- 9 capability categories
- Evidence tier system (Tier 1-5)
- Book Chapter 5 serves as authoritative vendor landscape

**Quality Standards:**
- 70%+ vendors should have Tier 1-3 evidence (production, peer-reviewed, expert consensus)
- 0% marketing hype tolerance in descriptions
- All capability scores >= 4 require Tier 1-2 evidence
- Production deployments required for Tier 1 classification

**Files:**
- `/home/jerem/security-architect-mcp-server/data/vendor_database.json`
- `/home/jerem/modern-data-stack-for-cybersecurity-book/chapters/05-vendor-landscape.md`

## Quick Reference: Capability Scoring Guide

```
5 (Exceptional): Tier 1 evidence (production with metrics)
4 (Strong): Tier 2 evidence (peer-reviewed, expert consensus)
3 (Adequate): Tier 3 evidence (expert opinion, framework inclusion)
2 (Limited): Tier 4 evidence (vendor claims only - mark as unvalidated)
1 (Weak): Tier 5 evidence (theoretical - note "unvalidated in production")
0 (N/A): Not applicable or explicitly not supported
```

## References

- **Evidence Tier System**: Same as academic-citation-manager (Tier 1-5)
- **Book Chapter 5**: `/home/jerem/modern-data-stack-for-cybersecurity-book/chapters/05-vendor-landscape.md`
- **Vendor Database**: `/home/jerem/security-architect-mcp-server/data/vendor_database.json`
- **MCP Project README**: `/home/jerem/security-architect-mcp-server/README.md`

---

**Version**: 1.0
**Created**: 2025-10-17
**Scope**: security-architect-mcp-server project
**Purpose**: Maintain evidence-based vendor database quality (64→80 vendors)

## SECURITY: Source Validation

**Risk Level**: LOW RISK

**Context**: This skill validates structured data against known schemas/standards.

**Trusted sources**: Git-controlled project files, known specifications (Anthropic MCP spec, vendor database schema)
**No external document processing**: Only validates against whitelisted schemas
**Input validation**: Validates expected JSON/schema format, rejects malformed data

**This skill operates on trusted structured data only. Standard validation provides sufficient security.**
