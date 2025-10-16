# Vendor Database Expansion Plan

**Current Status**: 10 vendors across 4 categories
**Target**: 80+ vendors across 8-10 categories
**Estimated Effort**: 30-40 hours
**Priority**: High (Phase 1 deliverable)

---

## Current Database (10 Vendors)

### Query Engines (2)
- Amazon Athena
- Starburst Enterprise

### Data Virtualization (2)
- Dremio
- Denodo Platform

### Data Lakehouses (2)
- Snowflake Data Cloud
- Databricks Lakehouse Platform

### SIEM (4)
- Splunk Enterprise Security
- Elastic Security (SIEM)
- IBM QRadar SIEM
- Microsoft Sentinel

---

## Expansion Strategy

### Phase 1: Expand Existing Categories (+15 vendors)
**Estimated Effort**: 10-12 hours
**Priority**: Immediate

#### Query Engines (+3 vendors)
- [ ] Trino (formerly Presto SQL)
- [ ] Apache Drill
- [ ] Google BigQuery

**Rationale**: Core category for security data query, multiple OSS + commercial options

#### Data Virtualization (+2 vendors)
- [ ] Starburst (also does virtualization, not just query)
- [ ] Apache Calcite (OSS foundation)

**Rationale**: Important for hybrid on-prem/cloud architectures

#### Data Lakehouses (+3 vendors)
- [ ] Delta Lake (Databricks)
- [ ] Apache Hudi
- [ ] Apache Iceberg

**Rationale**: Open table formats often deployed standalone, not just as part of lakehouse

#### SIEM (+7 vendors)
- [ ] CrowdStrike Falcon LogScale (formerly Humio)
- [ ] Sumo Logic
- [ ] Chronicle Security (Google)
- [ ] Securonix
- [ ] Exabeam
- [ ] Rapid7 InsightIDR
- [ ] Devo Platform

**Rationale**: SIEM is most crowded category, critical to have comprehensive coverage

### Phase 2: Add New Categories (+30 vendors)
**Estimated Effort**: 15-20 hours
**Priority**: After Phase 1 complete

#### Streaming Platforms (10 vendors)
- [ ] Apache Kafka
- [ ] Confluent Platform
- [ ] Amazon Kinesis
- [ ] Apache Flink
- [ ] Apache Pulsar
- [ ] Redpanda
- [ ] Azure Event Hubs
- [ ] Google Cloud Pub/Sub
- [ ] Apache Storm
- [ ] RabbitMQ

**Rationale**: Real-time detection requires streaming ingestion

#### Data Observability (5 vendors)
- [ ] Splunk Observability Cloud
- [ ] Datadog
- [ ] New Relic
- [ ] Dynatrace
- [ ] Honeycomb

**Rationale**: Overlap with security monitoring, important for DevSecOps

#### Object Storage (5 vendors)
- [ ] Amazon S3
- [ ] Azure Blob Storage
- [ ] Google Cloud Storage
- [ ] MinIO
- [ ] Ceph

**Rationale**: Foundation of modern data lakes

#### Data Catalog & Governance (5 vendors)
- [ ] Apache Atlas
- [ ] Collibra
- [ ] Alation
- [ ] AWS Glue Data Catalog
- [ ] Purview (Microsoft)

**Rationale**: Important for data lineage, compliance, discovery

#### ETL/ELT Platforms (5 vendors)
- [ ] Apache NiFi
- [ ] Airbyte
- [ ] Fivetran
- [ ] Talend
- [ ] Matillion

**Rationale**: Critical for data ingestion pipelines

### Phase 3: Long Tail (+35 vendors)
**Estimated Effort**: 10-15 hours
**Priority**: After Phase 2 complete

#### Specialized Security Data Platforms
- XDR vendors (Palo Alto Cortex, Trend Micro, etc.)
- SOAR platforms (Splunk SOAR, Palo Alto XSOAR, etc.)
- Threat Intelligence (Anomali, ThreatConnect, etc.)
- NDR platforms (Darktrace, Vectra, ExtraHop, etc.)
- UEBA (Gurucul, Exabeam, etc.)

#### Cloud-Native Security
- Cloud security posture management (CSPM)
- Cloud workload protection platforms (CWPP)
- Kubernetes security (Falco, etc.)

---

## Data Quality Standards

Each vendor entry requires:

### Required Fields
1. **id** (slug format: vendor-name-product)
2. **name** (Official product name)
3. **category** (From VendorCategory enum)
4. **description** (1-2 sentence summary)
5. **website** (Vendor homepage or product page)
6. **capabilities** (25+ capability dimensions)
   - team_size_required (lean/standard/large)
   - operational_complexity (1-10)
   - deployment_models (list)
   - cost_model (per-gb/consumption/subscription/oss-support)
   - sql_interface (bool)
   - streaming_query (bool)
   - open_table_format (iceberg-native/delta/hudi/proprietary)
   - cloud_native (bool)
   - multi_cloud (bool)
   - managed_service_available (bool)
   - siem_integration (bool)
   - ml_analytics (bool)
   - api_extensibility (bool)
   - ocsf_support (bool)
   - multi_source_integration (bool)
   - time_series_partitioning (bool)
   - long_term_retention (bool)
   - data_sovereignty_options (list)
   - maturity (emerging/production/mature/legacy)
7. **typical_annual_cost_range** (e.g., "$50K-200K")
8. **evidence_source** (Book chapter, vendor docs, practitioner)
9. **tags** (e.g., mentioned-in-book, oss, commercial, cloud-only)

### Evidence Requirements
- All capability claims must be sourced from:
  - "Modern Data Stack for Cybersecurity" book chapters
  - Vendor documentation
  - Practitioner recommendations (with attribution)
  - Literature review validated sources

### Validation Process
1. Research vendor capabilities from public documentation
2. Cross-reference with book mentions (if applicable)
3. Validate cost ranges from pricing pages or Gartner/Forrester
4. Add evidence_source citations
5. Tag appropriately (oss, cloud-only, enterprise-only, etc.)

---

## Incremental Expansion Workflow

### Week 1: Query Engines & Data Virtualization (+5 vendors)
1. Research Trino, Apache Drill, Google BigQuery
2. Research Starburst virtualization, Apache Calcite
3. Create vendor JSON entries
4. Update tests
5. Commit: "📊 Vendor database: Query engines expanded (13 → 15 vendors)"

### Week 2: Data Lakehouses & SIEM Part 1 (+10 vendors)
1. Research Delta Lake, Hudi, Iceberg
2. Research CrowdStrike Falcon LogScale, Sumo Logic, Chronicle, Securonix
3. Create vendor JSON entries
4. Update tests
5. Commit: "📊 Vendor database: Lakehouses + SIEM expanded (15 → 25 vendors)"

### Week 3: SIEM Part 2 & Streaming Platforms Part 1 (+10 vendors)
1. Research Exabeam, Rapid7, Devo
2. Research Kafka, Confluent, Kinesis, Flink, Pulsar
3. Create vendor JSON entries
4. Update tests
5. Commit: "📊 Vendor database: SIEM + Streaming expanded (25 → 35 vendors)"

### Week 4: Streaming Part 2 & Observability (+10 vendors)
1. Research Redpanda, Event Hubs, Pub/Sub, Storm, RabbitMQ
2. Research Splunk O11y, Datadog, New Relic, Dynatrace, Honeycomb
3. Create vendor JSON entries
4. Update tests
5. Commit: "📊 Vendor database: Streaming + Observability (35 → 45 vendors)"

### Week 5: Object Storage, Catalog, ETL (+15 vendors)
1. Research S3, Blob, GCS, MinIO, Ceph
2. Research Atlas, Collibra, Alation, Glue, Purview
3. Research NiFi, Airbyte, Fivetran, Talend, Matillion
4. Create vendor JSON entries
5. Update tests
6. Commit: "📊 Vendor database: Storage + Catalog + ETL (45 → 60 vendors)"

### Week 6-7: Specialized Security Platforms (+20+ vendors)
1. Research XDR vendors
2. Research SOAR platforms
3. Research Threat Intelligence
4. Research NDR platforms
5. Create vendor JSON entries
6. Update tests
7. Commit: "📊 Vendor database: Specialized security platforms (60 → 80+ vendors)"

---

## Testing Strategy

### Tests to Update
- `test_database_loader.py`: Update total vendor count assertions
- `test_filter_vendors.py`: Add scenarios for new categories
- `test_score_vendors.py`: Validate scoring across expanded database
- `test_server.py`: Update resource stats assertions

### New Test Scenarios
- Streaming platform filtering (real-time detection requirement)
- Observability platform scoring (DevSecOps use case)
- Multi-category filtering (e.g., SIEM + Streaming + Lakehouse)

---

## Risks & Mitigations

### Risk 1: Data Quality Degradation
**Mitigation**: Enforce evidence_source requirement, manual review each batch

### Risk 2: Capability Matrix Inconsistency
**Mitigation**: Use capability validation checklist, compare similar vendors

### Risk 3: Cost Data Accuracy
**Mitigation**: Mark cost ranges as estimates, cite pricing page dates

### Risk 4: Category Taxonomy Explosion
**Mitigation**: Limit to 8-10 categories, resist over-segmentation

### Risk 5: Time Overrun
**Mitigation**: Incremental commits, ship 20-30 vendors initially if time constrained

---

## Success Criteria

### Phase 1 Success (15 vendors)
- [ ] All existing categories have 3-5 vendors minimum
- [ ] SIEM category has 10+ vendors (most critical)
- [ ] Tests passing with expanded database
- [ ] Coverage maintained at 90%+

### Phase 2 Success (45 vendors)
- [ ] 5 new categories added
- [ ] Each new category has 5+ vendors
- [ ] Book journey scenarios still passing
- [ ] New test scenarios for streaming/observability

### Phase 3 Success (80+ vendors)
- [ ] All major security data platform categories covered
- [ ] 80+ vendors total
- [ ] Evidence-based capability data for all
- [ ] Ready for beta testing

---

## Next Steps (Immediate)

1. **Research vendors for Phase 1 expansion** (2-3 hours)
   - Trino, Apache Drill, Google BigQuery
   - CrowdStrike Falcon LogScale, Sumo Logic, Chronicle
   - Delta Lake, Hudi, Iceberg (as standalone platforms)

2. **Create vendor JSON entries** (5-6 hours)
   - Complete capability matrices
   - Validate cost ranges
   - Add evidence sources

3. **Update tests** (1-2 hours)
   - Adjust vendor count assertions
   - Add new filtering scenarios

4. **Commit Phase 1 expansion** (15 → 25 vendors)

**Estimated Time**: 8-11 hours for Phase 1 expansion
**Target Completion**: Within 1-2 weeks

---

**Last Updated**: October 15, 2025
**Status**: Planning complete, ready to begin Phase 1 expansion
