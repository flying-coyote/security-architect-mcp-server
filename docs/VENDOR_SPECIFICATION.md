# Vendor Database Specification

**Purpose**: Reference document for adding and maintaining vendors in the Security Architect MCP Server database.

**Status**: Phase 2 complete (54 vendors across 9 categories)

**Last Updated**: October 16, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Vendor Categories](#vendor-categories)
3. [Capability Matrix](#capability-matrix)
4. [Data Quality Standards](#data-quality-standards)
5. [Research Process](#research-process)
6. [Adding New Vendors](#adding-new-vendors)
7. [Cost Model Guidelines](#cost-model-guidelines)
8. [Evidence Sources](#evidence-sources)

---

## Overview

The vendor database is the core data asset for the Security Architect MCP Server. It contains **54 security data platforms** across **9 categories**, with **25+ capability dimensions** per vendor.

### Current Database Status

- **Total Vendors**: 54
- **Categories**: 9 (SIEM, Query Engine, Data Lakehouse, Streaming Platform, Virtualization, Observability, Object Storage, Data Catalog, ETL/ELT)
- **Coverage**: 94% test coverage maintained
- **Evidence**: All vendors validated from official documentation, pricing pages, analyst reports (2025 data)

### Database Philosophy

1. **Evidence-Based**: Every capability and cost range sourced from verifiable documentation
2. **Practitioner-Focused**: Real-world accuracy over theoretical features
3. **Vendor-Neutral**: Equal treatment regardless of commercial/OSS status
4. **Honest Trade-offs**: No "perfect" vendor - document limitations clearly

---

## Vendor Categories

### 1. SIEM (Security Information and Event Management)

**Purpose**: Real-time security monitoring, threat detection, incident response

**Examples**: Splunk Enterprise Security, Elastic Security, Microsoft Sentinel, CrowdStrike Falcon LogScale, Sumo Logic, Chronicle Security, Securonix, Exabeam, Rapid7 InsightIDR, Devo Platform, IBM QRadar

**Key Characteristics**:
- `streaming_query: true` (real-time detection)
- `ml_analytics: true` (anomaly detection, UEBA)
- `siem_integration: false` (they ARE the SIEM, not exporting to one)
- `operational_complexity: medium-high` (require SOC team expertise)
- `cost_model: per-gb` or `subscription`

**Target Use Case**: Security operations centers (SOCs), compliance monitoring, threat hunting

---

### 2. Query Engine

**Purpose**: Federated SQL queries across multiple data sources without data movement

**Examples**: Amazon Athena, Starburst, Trino, Apache Drill, Google BigQuery, Dremio (also Virtualization)

**Key Characteristics**:
- `sql_interface: true` (standard SQL)
- `multi_engine_query: true` (query federation)
- `open_table_format: iceberg-native` or `iceberg-support` (preferred)
- `operational_complexity: low-medium`
- `cost_model: consumption` or `subscription`

**Target Use Case**: Ad-hoc security analytics, cost-effective data lake queries, cross-source investigations

---

### 3. Data Lakehouse

**Purpose**: Unified platform combining data lake flexibility with data warehouse performance

**Examples**: Snowflake, Databricks, Delta Lake, Apache Hudi, Apache Iceberg

**Key Characteristics**:
- `sql_interface: true`
- `open_table_format: iceberg-native`, `delta`, or `hudi`
- `schema_evolution: true` (handle evolving security schemas)
- `ml_analytics: true` (ML/AI capabilities for threat detection)
- `streaming_query: true` (real-time ingestion)

**Target Use Case**: Unified security data platform, ML-powered threat detection, long-term retention

---

### 4. Streaming Platform

**Purpose**: Real-time event streaming and processing for security data pipelines

**Examples**: Apache Kafka, Confluent, Amazon Kinesis, Apache Flink, Apache Pulsar, Redpanda, Azure Event Hubs, Google Pub/Sub, Apache Storm, RabbitMQ

**Key Characteristics**:
- `streaming_query: true` (real-time processing)
- `sql_interface: false-true` (varies - Confluent has ksqlDB, Flink has SQL)
- `siem_integration: true` (export to SIEMs)
- `operational_complexity: medium-high` (requires streaming expertise)
- `cost_model: open-source`, `consumption`, or `hybrid`

**Target Use Case**: Real-time log ingestion, event-driven architectures, high-throughput security pipelines

---

### 5. Data Virtualization

**Purpose**: Logical data layer providing unified view across disparate sources without data replication

**Examples**: Dremio, Denodo Platform

**Key Characteristics**:
- `multi_engine_query: true` (cross-source federation)
- `sql_interface: true`
- `operational_complexity: medium-high` (requires data modeling expertise)
- `cost_model: subscription`

**Target Use Case**: Multi-source security analytics, legacy system integration, data mesh architectures

---

### 6. Observability Platform

**Purpose**: Application performance monitoring (APM), infrastructure monitoring, log analytics

**Examples**: Datadog, New Relic, Dynatrace, Splunk Observability, Honeycomb

**Key Characteristics**:
- `streaming_query: true` (real-time metrics)
- `ml_analytics: true` (anomaly detection)
- `siem_integration: true` (export security-relevant events to SIEMs)
- `operational_complexity: low-medium` (managed services)
- `cost_model: subscription` or `per-gb`

**Target Use Case**: Application security monitoring, DevSecOps, infrastructure threat detection

---

### 7. Object Storage

**Purpose**: Scalable storage for raw logs, PCAP files, forensic data

**Examples**: Amazon S3, Azure Blob Storage, Google Cloud Storage, MinIO, Ceph

**Key Characteristics**:
- `sql_interface: false` (storage only, query with Athena/Presto/Trino)
- `streaming_query: false`
- `siem_integration: true` (SIEMs ingest from object storage)
- `operational_complexity: low` (managed) or `medium` (self-hosted)
- `cost_model: consumption` (per-GB storage + API calls)

**Target Use Case**: Long-term log retention, cost-effective archival, data lake foundation

---

### 8. Data Catalog & Governance

**Purpose**: Metadata management, data lineage, access control, compliance

**Examples**: Apache Atlas, Collibra, Alation, AWS Glue, Microsoft Purview

**Key Characteristics**:
- `sql_interface: false` (metadata layer, not query engine)
- `data_governance: true` (access control, lineage tracking)
- `compliance_certifications: [...]` (regulatory compliance)
- `operational_complexity: medium`
- `cost_model: subscription` or `open-source`

**Target Use Case**: Security data governance, compliance reporting, data lineage for investigations

---

### 9. ETL/ELT Platform

**Purpose**: Data pipeline orchestration, log normalization, schema transformation

**Examples**: Apache NiFi, Airbyte, Fivetran, Talend, Matillion

**Key Characteristics**:
- `sql_interface: false` (pipeline tool, not query engine)
- `streaming_query: true-false` (varies - NiFi/Flink are streaming, Airbyte is batch)
- `siem_integration: true` (prepare data for SIEM ingestion)
- `api_extensibility: true` (custom connectors)
- `operational_complexity: medium`

**Target Use Case**: Log normalization, OCSF transformation, multi-source data integration

---

## Capability Matrix

Each vendor has **25+ capability dimensions** defined in the `VendorCapabilities` Pydantic model:

### Core Query Capabilities

| Field | Type | Description | Examples |
|-------|------|-------------|----------|
| `sql_interface` | `bool` | Supports SQL queries (vs proprietary query language) | `true` for Athena/Snowflake, `false` for Splunk (SPL) |
| `streaming_query` | `bool` | Real-time/streaming query capability | `true` for SIEMs, Streaming Platforms |
| `multi_engine_query` | `bool` | Can query data across multiple engines | `true` for Trino, Dremio, Starburst |

### Data Format and Interoperability

| Field | Type | Description | Examples |
|-------|------|-------------|----------|
| `open_table_format` | `enum` | Open table format support | `iceberg-native`, `iceberg-support`, `delta`, `hudi`, `proprietary`, `multiple` |
| `schema_evolution` | `bool` | Supports schema evolution without data migration | `true` for Iceberg/Delta/Hudi |

### Deployment and Infrastructure

| Field | Type | Description | Examples |
|-------|------|-------------|----------|
| `deployment_models` | `list[enum]` | Supported deployment models | `["cloud", "on-prem", "hybrid", "edge"]` |
| `cloud_native` | `bool` | Built cloud-native (vs retrofitted for cloud) | `true` for Athena, `false` for Splunk |
| `multi_cloud` | `bool` | Supports multi-cloud deployments (AWS + Azure + GCP) | `true` for Snowflake, Databricks |

### Operational Complexity

| Field | Type | Description | Examples |
|-------|------|-------------|----------|
| `operational_complexity` | `enum` | Operational overhead | `low`, `medium`, `high` |
| `managed_service_available` | `bool` | Fully managed service available | `true` for Athena, Snowflake, Sentinel |
| `team_size_required` | `enum` | Minimum team size to operate effectively | `lean` (1-2), `standard` (3-5), `large` (6+) |

### Cost and Licensing

| Field | Type | Description | Examples |
|-------|------|-------------|----------|
| `cost_model` | `enum` | Pricing model | `per-gb`, `consumption`, `subscription`, `open-source`, `hybrid` |
| `cost_predictability` | `enum` | Cost predictability | `low`, `medium`, `high` |

### Security-Specific Capabilities

| Field | Type | Description | Examples |
|-------|------|-------------|----------|
| `siem_integration` | `bool` | Integrates with SIEM platforms (exports data TO SIEMs) | `true` for non-SIEM platforms, `false` for SIEMs |
| `compliance_certifications` | `list[str]` | Compliance certifications | `["SOC2", "FedRAMP", "ISO27001", "HIPAA", "PCI-DSS"]` |
| `data_governance` | `bool` | Built-in data governance and access control | `true` for Enterprise platforms |

### Maturity and Support

| Field | Type | Description | Examples |
|-------|------|-------------|----------|
| `maturity` | `enum` | Product maturity level | `production`, `beta`, `experimental` |
| `vendor_support` | `str` | Vendor support tier | `enterprise`, `standard`, `community`, `none` |
| `community_size` | `enum` | Community size for OSS projects | `large`, `medium`, `small`, `unknown` |

### Advanced Capabilities

| Field | Type | Description | Examples |
|-------|------|-------------|----------|
| `ocsf_support` | `bool` | Supports Open Cybersecurity Schema Framework (OCSF) | `false` for most vendors (future Phase 3 feature) |
| `ml_analytics` | `bool` | Built-in ML/analytics capabilities | `true` for SIEMs, Databricks, BigQuery |
| `api_extensibility` | `bool` | Rich API for extensibility and automation | `true` for modern platforms |

---

## Data Quality Standards

### Evidence Sources (Priority Order)

1. **Official Vendor Documentation** (pricing pages, feature docs)
2. **Analyst Reports** (Gartner Magic Quadrant, Forrester Wave)
3. **Third-Party Pricing Databases** (Vendr, IT Central Station, PeerSpot)
4. **Practitioner Reviews** (Reddit r/AskNetsec, r/sysadmin, Security StackExchange)
5. **Book Research** (Modern Data Stack for Cybersecurity - for incumbents)

### Validation Requirements

- **Pricing**: Must cite source from 2024-2025 (no older than 18 months)
- **Capabilities**: Verified from official documentation or analyst reports
- **Cost Ranges**: 80th percentile range (e.g., $100K-500K excludes outliers)
- **Maturity**: Only `production` status for customer-facing vendors

### Quality Checklist

Before adding a vendor, verify:

- [ ] Vendor ID is lowercase-hyphenated (e.g., `amazon-athena`)
- [ ] All 25 capability fields populated (no `null` for core fields)
- [ ] Cost range cites specific source (e.g., "vendor.com/pricing, accessed 2025-10-16")
- [ ] Description is 1-2 sentences (concise, jargon-free)
- [ ] Tags include relevant keywords (e.g., `oss`, `cloud-native`, `mentioned-in-book`)
- [ ] Compliance certifications accurate (check official compliance pages)

---

## Research Process

### Phase 2 Research Workflow (October 2025)

**Objective**: Add 30 vendors across 5 new categories (Streaming, Observability, Storage, Catalog, ETL/ELT)

**Tools Used**:
- Claude Code WebSearch tool (30+ searches)
- Official vendor documentation
- Pricing comparison sites (Vendr, SelectHub, Comparitech)
- Analyst reports (Gartner, Forrester)

**Process**:

1. **Category Definition** (30 min)
   - Define purpose, key characteristics, target use cases
   - Identify 8-12 candidate vendors per category

2. **Vendor Research** (2-3 hours per category)
   - Search: `{vendor name} security use cases 2025`
   - Search: `{vendor name} pricing 2025 cost`
   - Search: `{vendor name} vs competitors siem integration`
   - Verify: Deployment models, SQL support, streaming capabilities

3. **Capability Matrix Population** (30 min per vendor)
   - Extract capabilities from feature comparison pages
   - Validate against official documentation
   - Cross-check with analyst reports (Gartner, Forrester)

4. **Cost Research** (15 min per vendor)
   - Find pricing page or request quote ranges
   - Cite: "$100K-500K/year based on {source}, accessed {date}"
   - Note: Cost assumptions (e.g., "5TB/day ingestion, 50 users")

5. **Quality Assurance** (1 hour total)
   - Run pytest suite (ensure all tests pass)
   - Validate JSON syntax
   - Check for duplicate IDs
   - Verify all 25 capability fields populated

**Time Investment**: ~25 hours for 30 vendors (50 min/vendor average)

---

## Adding New Vendors

### Step-by-Step Guide

#### 1. Research Phase

**Vendor Selection Criteria**:
- [ ] Production-ready (not beta/experimental)
- [ ] Documented pricing (or cost model is clear)
- [ ] Security use cases documented (not general-purpose only)
- [ ] Meets minimum adoption threshold (>100 known customers OR active OSS community)

**Research Checklist**:
- [ ] Official website URL
- [ ] Category classification (SIEM, Query Engine, etc.)
- [ ] Description (1-2 sentences, no marketing fluff)
- [ ] SQL support (SQL vs proprietary query language)
- [ ] Streaming capabilities (real-time vs batch)
- [ ] Deployment models (cloud, on-prem, hybrid, edge)
- [ ] Cost model (per-gb, consumption, subscription, OSS)
- [ ] Compliance certifications (SOC2, FedRAMP, ISO27001, etc.)

#### 2. JSON Entry Creation

**Template**:
```json
{
  "id": "vendor-name-lowercase",
  "name": "Vendor Display Name",
  "category": "SIEM" | "Query Engine" | "Data Lakehouse" | ...,
  "description": "1-2 sentence description of platform purpose and key differentiator.",
  "website": "https://vendor.com",
  "capabilities": {
    "sql_interface": true | false,
    "streaming_query": true | false,
    "multi_engine_query": true | false,
    "open_table_format": "iceberg-native" | "iceberg-support" | "delta" | "hudi" | "proprietary" | "multiple",
    "schema_evolution": true | false,
    "deployment_models": ["cloud", "on-prem", "hybrid", "edge"],
    "cloud_native": true | false,
    "multi_cloud": true | false,
    "operational_complexity": "low" | "medium" | "high",
    "managed_service_available": true | false,
    "team_size_required": "lean" | "standard" | "large",
    "cost_model": "per-gb" | "consumption" | "subscription" | "open-source" | "hybrid",
    "cost_predictability": "low" | "medium" | "high",
    "siem_integration": true | false,
    "compliance_certifications": ["SOC2", "FedRAMP", ...],
    "data_governance": true | false,
    "maturity": "production" | "beta" | "experimental",
    "vendor_support": "enterprise" | "standard" | "community" | "none",
    "community_size": "large" | "medium" | "small" | "unknown",
    "ocsf_support": false,
    "ml_analytics": true | false,
    "api_extensibility": true | false
  },
  "typical_annual_cost_range": "$100K-500K for 5TB/day ingestion, 50 users",
  "cost_notes": "Additional context about pricing model, assumptions, caveats.",
  "evidence_source": "vendor.com/pricing, Gartner MQ 2025, accessed 2025-10-16",
  "last_updated": "2025-10-16T00:00:00",
  "validated_by": "Your Name",
  "tags": ["relevant", "keywords", "for", "filtering"]
}
```

#### 3. Validation

**Run tests**:
```bash
source venv/bin/activate
pytest tests/ -v
```

**Check coverage**:
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

**Expected**: 80+ tests passing, 90%+ coverage maintained

#### 4. Commit

**Commit message format**:
```
📊 Add {N} vendors to {category} category

Added: {vendor1}, {vendor2}, {vendor3}

Evidence: {sources}
Cost ranges: {date}
Tests: {pass/fail status}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Cost Model Guidelines

### Cost Model Types

| Cost Model | Description | Examples | Predictability |
|------------|-------------|----------|----------------|
| `per-gb` | Charged per GB ingested | Splunk, Elastic, Sentinel | **Low** (unpredictable spikes) |
| `consumption` | Charged per query/compute | Athena, Snowflake, BigQuery | **Medium** (query volume varies) |
| `subscription` | Flat annual subscription | Dremio, QRadar, Chronicle | **High** (fixed cost) |
| `open-source` | Infrastructure costs only | Kafka, Trino, Iceberg | **High** (self-managed) |
| `hybrid` | Mixed model (e.g., base + usage) | Databricks, Exabeam | **Medium** |

### Cost Range Format

**Template**: `$XXK-YYYK for [assumptions]`

**Examples**:
- `$50K-200K/year for 1TB/day queries, serverless` (Athena)
- `$3M-12M/year for 10TB/day ingestion, 100 users` (Splunk)
- `$100K-500K infrastructure costs for 5TB/day, self-managed` (Kafka)

**Key Requirements**:
1. **Cite source**: "Based on vendor.com/pricing, accessed 2025-10-16"
2. **State assumptions**: Ingestion volume, user count, retention period
3. **Use 80th percentile range**: Exclude extreme outliers (very small/large deployments)
4. **Update annually**: Cost data expires after 18 months

### Cost Predictability

- **High**: Fixed subscription, no usage-based charges (e.g., QRadar, Chronicle)
- **Medium**: Consumption-based but volume is predictable (e.g., Snowflake, BigQuery)
- **Low**: Per-GB ingestion with unpredictable spikes (e.g., Splunk, Sentinel)

---

## Evidence Sources

### Primary Sources (Highest Priority)

1. **Official Vendor Documentation**
   - Pricing pages: `vendor.com/pricing`
   - Feature comparison: `vendor.com/features`
   - Deployment guides: `vendor.com/docs`

2. **Analyst Reports**
   - Gartner Magic Quadrant (SIEM, Cloud Databases, Observability)
   - Forrester Wave (Security Analytics, Data Platforms)
   - IDC MarketScape

3. **Compliance and Certifications**
   - Vendor trust pages: `vendor.com/trust`, `vendor.com/compliance`
   - Third-party attestations: SOC2 reports, FedRAMP listing

### Secondary Sources

4. **Pricing Comparison Sites**
   - Vendr: `vendr.com` (SaaS pricing data)
   - IT Central Station / PeerSpot: `peerspot.com`
   - G2: `g2.com` (user reviews, pricing estimates)

5. **Practitioner Communities**
   - Reddit: r/AskNetsec, r/sysadmin, r/dataengineering
   - Security StackExchange: `security.stackexchange.com`
   - Slack communities: OWASP Slack, DevSecOps Slack

6. **Book Research**
   - "Modern Data Stack for Cybersecurity" (Jeremy Wiley, 2025)
   - Referenced in Chapters 3-4 for incumbent vendors

### Citation Format

**Format**: `{source type}, {URL or publication}, accessed {date}`

**Examples**:
- `Splunk pricing page, splunk.com/pricing, accessed 2025-10-16`
- `Gartner Magic Quadrant for SIEM 2025, gartner.com, Q2 2025`
- `"Modern Data Stack for Cybersecurity", Chapter 4 Marcus journey, 2025`
- `Chronicle Security documentation, chronicle.security/docs, accessed 2025-10-16`

---

## Maintenance and Updates

### Quarterly Update Cadence

**Target**: Refresh vendor database every **3 months** (Q1, Q2, Q3, Q4)

**Update Checklist**:
- [ ] Review pricing pages for cost model changes
- [ ] Check for new compliance certifications (FedRAMP, ISO27001)
- [ ] Verify feature updates (new capabilities, SQL support, streaming)
- [ ] Add new vendors (5-10 per quarter)
- [ ] Archive deprecated vendors (mark as `maturity: experimental` if sunsetted)

### Versioning

**Format**: `YYYY-QN` (e.g., `2025-Q4` for Q4 2025 update)

**Tracking**:
- Update `last_full_update` field in `vendor_database.json`
- Commit message: `📊 Quarterly vendor update: 2025-Q4`
- Archive old version: `data/archive/vendor_database_2025-Q3.json`

---

## Appendix A: Phase 2 Vendor List (24 → 54)

### Original 24 Vendors (Phase 1)

**SIEM** (4): Splunk, Elastic, QRadar, Sentinel
**Query Engine** (5): Athena, Starburst, Trino, Apache Drill, BigQuery
**Data Lakehouse** (5): Snowflake, Databricks, Delta Lake, Apache Hudi, Apache Iceberg
**Virtualization** (2): Dremio, Denodo
**Other** (1): Apache Calcite (query framework)

### New 30 Vendors (Phase 2)

**SIEM** (7): CrowdStrike Falcon LogScale, Sumo Logic, Chronicle Security, Securonix, Exabeam, Rapid7 InsightIDR, Devo Platform

**Streaming Platform** (10): Apache Kafka, Confluent, Amazon Kinesis, Apache Flink, Apache Pulsar, Redpanda, Azure Event Hubs, Google Pub/Sub, Apache Storm, RabbitMQ

**Observability** (5): Datadog, New Relic, Dynatrace, Splunk Observability, Honeycomb

**Object Storage** (5): Amazon S3, Azure Blob Storage, Google Cloud Storage, MinIO, Ceph

**Data Catalog** (5): Apache Atlas, Collibra, Alation, AWS Glue, Microsoft Purview

**ETL/ELT** (5): Apache NiFi, Airbyte, Fivetran, Talend, Matillion

---

## Appendix B: Pydantic Schema Reference

See `src/models.py` for complete schema definitions:

- `VendorCapabilities`: 25+ capability fields
- `Vendor`: Vendor entry with capabilities, cost, evidence
- `VendorDatabase`: Collection of vendors with metadata
- `DecisionState`: Architect's filtering progress

**Key Enums**:
- `VendorCategory`: SIEM, Query Engine, Data Lakehouse, Streaming, Virtualization, Observability, Object Storage, Data Catalog, ETL/ELT
- `DeploymentModel`: cloud, on-prem, hybrid, edge
- `CostModel`: per-gb, consumption, subscription, open-source, hybrid
- `OpenTableFormat`: iceberg-native, iceberg-support, delta, hudi, proprietary, multiple
- `Maturity`: production, beta, experimental
- `TeamSize`: lean (1-2), standard (3-5), large (6+)

---

## Contributing

To contribute vendor data:

1. Follow research process (see [Research Process](#research-process))
2. Add vendor JSON entry to `data/vendor_database.json`
3. Run test suite: `pytest tests/`
4. Submit pull request with evidence sources cited
5. Tag: @flying-coyote for review

**Quality Bar**: All PRs must maintain 90%+ test coverage and pass all tests.

---

**Document Version**: 1.0 (Phase 2 Complete)
**Author**: Jeremy Wiley
**License**: Apache 2.0 (code), CC BY-SA 4.0 (documentation)
