# MCP-Literature Review Integration Schema

**Purpose**: Define the integrated vendor database schema that connects MCP server to literature review evidence base
**Status**: Design Phase
**Last Updated**: 2025-10-22

---

## Overview

The MCP server vendor database becomes a **generated artifact** from the literature review repository. The literature review is the single source of truth for:
- Vendor capability scores with evidence tiers
- Technology decision tree logic
- Cost modeling data
- Performance benchmarks
- Bibliography references

---

## Master Data Location

**Authoritative Source**: `~/security-data-literature-review/vendor-landscape/vendor-database.json`

**Generated Artifact**: `~/security-architect-mcp-server/data/vendor_database.json`

**DO NOT EDIT**: The MCP `vendor_database.json` is auto-generated. All edits must go to the literature review repository.

---

## Integrated Vendor Entry Schema

```json
{
  "id": "clickhouse",
  "name": "ClickHouse",
  "category": "OLAP/Analytics Engine",
  "description": "Open-source columnar OLAP database optimized for real-time analytics with security-specific advantages (native IP types, 50-100× CIDR query speedup).",
  "website": "https://clickhouse.com",

  "capabilities": {
    "query_performance": {
      "score": 5,
      "evidence": {
        "tier": "A",
        "confidence": 5,
        "sources": [
          {
            "id": "cloudflare-clickhouse-2024",
            "description": "Cloudflare production: 96% queries <1s, 6M req/sec",
            "url": "https://blog.cloudflare.com/http-analytics-for-6m-requests-per-second-using-clickhouse/",
            "evidence_tier": "A",
            "type": "production_deployment",
            "lit_review_ref": "MASTER-BIBLIOGRAPHY.md#cloudflare-clickhouse-2024"
          },
          {
            "id": "shell-clickhouse-2024",
            "description": "Shell security telemetry: 57TB/day production scale",
            "url": "https://altinity.com/blog/2024-shell-clickhouse-security-telemetry",
            "evidence_tier": "A",
            "type": "production_deployment",
            "lit_review_ref": "MASTER-BIBLIOGRAPHY.md#shell-clickhouse-2024"
          }
        ],
        "validation_notes": "2 production deployments at scale. Cloudflare (96% <1s) and Shell (57TB/day) validate sub-second performance for security workloads.",
        "last_validated": "2025-10-22"
      }
    },

    "compression_efficiency": {
      "score": 5,
      "evidence": {
        "tier": "A",
        "confidence": 5,
        "sources": [
          {
            "id": "altinity-clickhouse-compression-2024",
            "description": "10-12× compression typical, 75-85% storage reduction vs Elasticsearch",
            "url": "https://altinity.com/blog/clickhouse-compression-security-logs",
            "evidence_tier": "A",
            "type": "benchmark",
            "lit_review_ref": "analysis-bundles/performance-benchmarks-table.md#clickhouse-compression"
          }
        ],
        "validation_notes": "Validated across multiple security log deployments. Range: 10-12× compression ratio.",
        "last_validated": "2025-10-22"
      }
    },

    "security_specific_advantages": {
      "score": 5,
      "evidence": {
        "tier": "A",
        "confidence": 5,
        "sources": [
          {
            "id": "clickhouse-native-ip-types",
            "description": "Native IPv4/IPv6 types enable 50-100× faster CIDR queries",
            "url": "https://clickhouse.com/docs/en/sql-reference/data-types/ipv4",
            "evidence_tier": "B",
            "type": "vendor_documentation",
            "lit_review_ref": "analysis-bundles/security-performance-advantages.md#native-ip-types"
          }
        ],
        "validation_notes": "Native IP types are documented feature with production validation from security deployments.",
        "last_validated": "2025-10-22"
      }
    },

    "operational_complexity": "medium",
    "team_size_required": "standard",
    "sql_interface": true,
    "deployment_models": ["cloud", "on-prem", "hybrid"],
    "cost_model": "hybrid",
    "maturity": "production"
  },

  "cost_modeling": {
    "typical_annual_cost_range": "$50K-300K annually",
    "cost_notes": "OSS self-hosted free. ClickHouse Cloud: consumption-based. Enterprise support: $50K-150K/year. TCO varies with scale.",
    "tco_analysis_ref": "analysis-bundles/cost-reality-reference.md#clickhouse-tco",
    "evidence": {
      "tier": "B",
      "confidence": 4,
      "sources": [
        {
          "id": "clickhouse-cloud-pricing-2025",
          "url": "https://clickhouse.com/pricing",
          "evidence_tier": "B",
          "type": "vendor_pricing"
        }
      ]
    }
  },

  "architecture_patterns": ["liger_stack", "batch_olap", "hybrid"],
  "liger_role": "E",
  "decision_tree_fit": {
    "streaming_path": false,
    "batch_path": true,
    "hybrid_path": true,
    "volume_threshold": "1TB+/day",
    "use_cases": ["high_volume_olap", "security_specific_queries", "real_time_dashboards"],
    "decision_tree_ref": "analysis-bundles/technology-decision-tree.md#recommendation-4-batch-clickhouse-iceberg"
  },

  "journey_persona_fit": {
    "jennifer": "low",
    "marcus": "high",
    "priya": "medium",
    "rationale": "Marcus (data engineering background) best fit for ClickHouse ops complexity. Jennifer (no data engineers) needs managed service. Priya (growing team) could adopt with training.",
    "decision_tree_mapping": "Question 4, Option A: High-volume OLAP (TB+/day, ad-hoc queries)"
  },

  "evidence_summary": {
    "total_sources": 5,
    "tier_a_sources": 3,
    "tier_b_sources": 2,
    "tier_c_sources": 0,
    "tier_d_sources": 0,
    "overall_evidence_quality": "A",
    "last_validated": "2025-10-22",
    "validated_by": "Jeremy Wiley"
  },

  "tags": [
    "oss",
    "columnar",
    "olap",
    "security-optimized",
    "native-ip-types",
    "high-compression",
    "liger-stack",
    "production-validated"
  ],

  "last_updated": "2025-10-22T00:00:00",
  "source_repository": "security-data-literature-review",
  "sync_version": "2025-Q4"
}
```

---

## Evidence Tier Classification

Following blog Post #05 promise and literature review methodology:

### Evidence Tier Definitions

| Tier | Definition | Examples | Confidence Weighting |
|------|------------|----------|---------------------|
| **A** | Peer-reviewed research, production data | Production deployments (Cloudflare, Shell, Netflix), Academic research (DORA, MIT), Government (CISA, MITRE) | High (4-5) |
| **B** | Vendor documentation, deployment examples | Official docs, case studies, benchmark reports | Medium (3-4) |
| **C** | Expert interviews, conference presentations | Expert network validation, RSA presentations, practitioner blog posts | Medium (2-3) |
| **D** | Blog posts, marketing claims | Vendor marketing, unverified claims, speculation | Low (1-2) |

### Confidence Levels (1-5 Scale)

| Level | Meaning | Criteria |
|-------|---------|----------|
| **5** | Very High | 3+ Tier A sources, production validated, no contradictions |
| **4** | High | 2+ Tier A/B sources, validated, minor contradictions resolved |
| **3** | Medium | 1-2 Tier B/C sources, plausible but limited validation |
| **2** | Low | Single Tier C/D source, or contradictory evidence |
| **1** | Very Low | Tier D only, speculative, or significant contradictions |

---

## Technology Decision Tree Integration

### Journey Persona Mapping

Each vendor includes `journey_persona_fit` linking to Chapter 4 personas:

**Jennifer** (No data engineers, needs simplicity):
- Managed services preferred
- Low operational complexity
- Team size: 0-1 data engineers

**Marcus** (Data engineering background, wants control):
- Self-managed acceptable
- High technical capability
- Team size: 2-5+ data engineers

**Priya** (Growing team, building capability):
- Hybrid approaches
- Medium complexity tolerance
- Team size: 1-3 data engineers, growing

### Decision Tree Reference

Each vendor includes `decision_tree_fit` mapping to specific decision tree nodes:

```json
"decision_tree_fit": {
  "decision_tree_ref": "analysis-bundles/technology-decision-tree.md#recommendation-4-batch-clickhouse-iceberg",
  "decision_path": "Question 1C → Question 4A",
  "volume_threshold": "1TB+/day",
  "latency_acceptable": "15-60 minutes",
  "use_cases": ["high_volume_olap", "security_specific_queries"]
}
```

---

## Bibliography Integration

### Master Bibliography Reference

All evidence sources link to `MASTER-BIBLIOGRAPHY.md`:

```json
"lit_review_ref": "MASTER-BIBLIOGRAPHY.md#cloudflare-clickhouse-2024"
```

### Citation Format

When generating architecture reports, cite sources:

> "ClickHouse achieves sub-second query performance for 96% of queries (Cloudflare production deployment, 6M req/sec) [1] and handles 57TB/day security telemetry (Shell case study) [2]."
>
> **References**:
> [1] Cloudflare. "HTTP Analytics for 6M Requests/Second Using ClickHouse." 2024. https://blog.cloudflare.com/...
> [2] Altinity. "Shell ClickHouse Security Telemetry: 57TB/day Production Scale." 2024. https://altinity.com/blog/...

---

## Sync Metadata

### .last_sync File

Track synchronization state:

```json
{
  "sync_timestamp": "2025-10-22T15:30:00Z",
  "source_version": "2025-Q4",
  "vendors_synced": 64,
  "evidence_sources_total": 327,
  "tier_a_percentage": 79,
  "tier_b_percentage": 21,
  "tier_c_percentage": 0,
  "tier_d_percentage": 0,
  "sync_status": "success",
  "warnings": [],
  "errors": []
}
```

---

## Quarterly Update Workflow

1. **Literature Review Updates** (Month 1):
   - IT Harvest data refresh
   - New vendor additions
   - Evidence source validation
   - Update `vendor-landscape/vendor-database.json`

2. **Sync to MCP** (Month 1, Day 28):
   - Run `scripts/sync_from_literature_review.py`
   - Generate `INTEGRATION_STATUS.md` report
   - Validate evidence tiers
   - Run MCP test suite

3. **Blog Post Generation** (Month 2):
   - Anonymized case studies from MCP conversations
   - Reference updated vendor database
   - Cite new evidence sources

4. **Version Control**:
   - Literature review: `2025-Q4-update.md`
   - MCP server: `sync_version: "2025-Q4"`
   - Blog: "Based on 2025-Q4 vendor landscape"

---

## Quality Assurance

### Validation Rules

1. **Evidence Tier Quality**:
   - ❌ FAIL if Tier D sources used for capability scores 4-5
   - ⚠️ WARN if Tier C only for capability score 4+
   - ✅ PASS if Tier A/B for all high scores

2. **Confidence Level Alignment**:
   - Confidence 5 requires 3+ Tier A sources
   - Confidence 4 requires 2+ Tier A/B sources
   - Confidence 3 requires 1-2 Tier B/C sources

3. **Citation Completeness**:
   - All scores 4-5 must have `evidence.sources`
   - All sources must have `lit_review_ref`
   - All `lit_review_ref` must resolve to valid bibliography entries

### Validation Script

`scripts/validate_evidence_tiers.py` runs on every sync:
- Check evidence tier distribution (target: 70%+ Tier A)
- Validate citation links
- Detect contradictory sources
- Flag outdated evidence (>12 months old)

---

## Migration Path

### Current State (MCP Vendor Database)
- 64 vendors with basic `evidence_source` field
- No evidence tier classification
- No literature review linkage

### Target State (Integrated Database)
- 64+ vendors with full evidence metadata
- Evidence tier classification on all capability scores
- Bibliography citations for all claims
- Technology decision tree integration

### Migration Steps
1. Create `vendor-landscape/vendor-database.json` in lit review
2. Migrate 64 existing vendors with evidence annotation
3. Build sync script
4. Test integration workflow
5. Document "DO NOT EDIT" in MCP vendor database

---

**Status**: Design Complete - Ready for Implementation
**Next**: Create literature review vendor landscape structure
