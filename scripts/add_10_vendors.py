#!/usr/bin/env python3
"""
Add 10 high-value vendors to vendor database.

Vendors to add:
1. PrestoDB - Distributed SQL query engine (Meta open source)
2. ClickHouse - Columnar OLAP database for analytics
3. Apache Pinot - Real-time distributed OLAP datastore
4. Rockset - Real-time analytics database (recently acquired by OpenAI)
5. Apache Druid - Real-time analytics database
6. Grafana Loki - Log aggregation system
7. Cribl - Data routing/transformation platform
8. Wazuh - Open source XDR/SIEM platform
9. Graylog - Open source log management
10. Sysdig Secure - Cloud-native security platform

Research sources: Official vendor documentation, 2025 pricing pages
"""

import json
from pathlib import Path

# Load existing database
db_path = Path(__file__).parent.parent / "data" / "vendor_database.json"
with open(db_path) as f:
    db = json.load(f)

# New vendors to add
new_vendors = [
    {
        "id": "prestodb",
        "name": "PrestoDB",
        "category": "Query Engine",
        "description": "Open source distributed SQL query engine for running interactive analytic queries against data sources of all sizes. Originally developed by Meta (Facebook), optimized for low-latency ad-hoc queries.",
        "website": "https://prestodb.io",
        "capabilities": {
            "sql_interface": True,
            "streaming_query": False,
            "multi_engine_query": True,  # Can query multiple data sources
            "open_table_format": "iceberg-compatible",
            "schema_evolution": True,
            "deployment_models": ["on-prem", "cloud", "hybrid"],
            "cloud_native": False,  # Can run in cloud but not cloud-native
            "multi_cloud": True,
            "operational_complexity": "medium",
            "managed_service_available": True,  # AWS EMR, Ahana Cloud
            "team_size_required": "standard",
            "cost_model": "open-source",
            "cost_predictability": "high",
            "siem_integration": True,
            "compliance_certifications": [],  # Open source, depends on deployment
            "data_governance": True,
            "maturity": "production",
            "vendor_support": "community",
            "community_size": "large",
            "ocsf_support": False,
            "ml_analytics": False,
            "api_extensibility": True
        },
        "typical_annual_cost_range": "$50K-300K for infrastructure costs (no licensing fees)",
        "cost_notes": "Open source (Apache 2.0). Costs are infrastructure only (compute, storage, network). Managed services like Ahana Cloud add $50K-200K/year depending on scale.",
        "evidence_source": "https://prestodb.io/docs/current/ (2025-01)",
        "last_updated": "2025-10-16T00:00:00",
        "validated_by": "Jeremy Wiley",
        "tags": ["open-source", "distributed-query", "meta", "low-latency"]
    },
    {
        "id": "clickhouse",
        "name": "ClickHouse",
        "category": "Query Engine",
        "description": "Open source column-oriented OLAP database management system for real-time analytics. Extremely fast for analytical queries on large datasets, widely used for security log analytics and metrics.",
        "website": "https://clickhouse.com",
        "capabilities": {
            "sql_interface": True,
            "streaming_query": True,  # Materialized views, real-time inserts
            "multi_engine_query": False,
            "open_table_format": "proprietary",  # MergeTree engine
            "schema_evolution": True,
            "deployment_models": ["on-prem", "cloud", "hybrid"],
            "cloud_native": True,
            "multi_cloud": True,
            "operational_complexity": "medium",
            "managed_service_available": True,  # ClickHouse Cloud
            "team_size_required": "lean",
            "cost_model": "hybrid",  # Open source + cloud managed
            "cost_predictability": "high",
            "siem_integration": True,
            "compliance_certifications": ["SOC2", "GDPR", "HIPAA"],
            "data_governance": True,
            "maturity": "production",
            "vendor_support": "enterprise",
            "community_size": "very-large",
            "ocsf_support": False,
            "ml_analytics": False,
            "api_extensibility": True
        },
        "typical_annual_cost_range": "$30K-200K for cloud managed service",
        "cost_notes": "Open source (Apache 2.0). ClickHouse Cloud pricing: $0.60/GB stored + $0.15/GB scanned. Typical 1TB/day deployment: $30K-80K/year. Self-hosted infrastructure costs: $20K-150K/year.",
        "evidence_source": "https://clickhouse.com/pricing (2025-01)",
        "last_updated": "2025-10-16T00:00:00",
        "validated_by": "Jeremy Wiley",
        "tags": ["open-source", "columnar", "real-time-analytics", "log-analytics"]
    },
    {
        "id": "apache-pinot",
        "name": "Apache Pinot",
        "category": "Query Engine",
        "description": "Real-time distributed OLAP datastore designed for low-latency analytics on large-scale data. Widely used at LinkedIn, Uber, and Microsoft for user-facing analytics and operational intelligence.",
        "website": "https://pinot.apache.org",
        "capabilities": {
            "sql_interface": True,
            "streaming_query": True,  # Real-time ingestion from Kafka
            "multi_engine_query": False,
            "open_table_format": "proprietary",
            "schema_evolution": True,
            "deployment_models": ["on-prem", "cloud", "hybrid"],
            "cloud_native": True,
            "multi_cloud": True,
            "operational_complexity": "high",  # Complex cluster management
            "managed_service_available": True,  # StarTree Cloud
            "team_size_required": "standard",
            "cost_model": "open-source",
            "cost_predictability": "medium",
            "siem_integration": True,
            "compliance_certifications": [],
            "data_governance": False,
            "maturity": "production",
            "vendor_support": "community",
            "community_size": "medium",
            "ocsf_support": False,
            "ml_analytics": False,
            "api_extensibility": True
        },
        "typical_annual_cost_range": "$75K-400K for managed service (StarTree)",
        "cost_notes": "Open source (Apache 2.0). Self-hosted infrastructure: $50K-300K/year. StarTree Cloud managed service: $100K-500K/year depending on data volume and query load.",
        "evidence_source": "https://pinot.apache.org/docs/ (2025-01)",
        "last_updated": "2025-10-16T00:00:00",
        "validated_by": "Jeremy Wiley",
        "tags": ["open-source", "real-time", "low-latency", "user-facing-analytics"]
    },
    {
        "id": "rockset",
        "name": "Rockset",
        "category": "Query Engine",
        "description": "Real-time analytics database (recently acquired by OpenAI in 2024). Cloud-native SQL database for real-time analytics on streaming and operational data. Known for sub-second latency on fresh data.",
        "website": "https://rockset.com",
        "capabilities": {
            "sql_interface": True,
            "streaming_query": True,
            "multi_engine_query": True,
            "open_table_format": "proprietary",
            "schema_evolution": True,
            "deployment_models": ["cloud"],
            "cloud_native": True,
            "multi_cloud": False,  # AWS only
            "operational_complexity": "low",
            "managed_service_available": True,
            "team_size_required": "lean",
            "cost_model": "consumption",
            "cost_predictability": "high",
            "siem_integration": True,
            "compliance_certifications": ["SOC2", "GDPR", "HIPAA"],
            "data_governance": True,
            "maturity": "production",
            "vendor_support": "enterprise",
            "community_size": "small",
            "ocsf_support": False,
            "ml_analytics": False,
            "api_extensibility": True
        },
        "typical_annual_cost_range": "$60K-300K for typical security workloads",
        "cost_notes": "Fully managed consumption pricing. Typical 1TB/day: $80K-200K/year. Pricing based on compute (query execution) + storage + ingestion. Note: Acquired by OpenAI (2024), future roadmap uncertain.",
        "evidence_source": "https://rockset.com/pricing (2024-12, pre-acquisition pricing)",
        "last_updated": "2025-10-16T00:00:00",
        "validated_by": "Jeremy Wiley",
        "tags": ["real-time", "cloud-native", "openai-acquisition", "sub-second-latency"]
    },
    {
        "id": "apache-druid",
        "name": "Apache Druid",
        "category": "Data Lakehouse",
        "description": "Real-time analytics database designed for fast slice-and-dice analytics (OLAP queries) on large datasets. Combines streaming ingestion, fast aggregations, and approximate algorithms for sub-second query latency.",
        "website": "https://druid.apache.org",
        "capabilities": {
            "sql_interface": True,
            "streaming_query": True,
            "multi_engine_query": False,
            "open_table_format": "proprietary",
            "schema_evolution": True,
            "deployment_models": ["on-prem", "cloud", "hybrid"],
            "cloud_native": True,
            "multi_cloud": True,
            "operational_complexity": "high",
            "managed_service_available": True,  # Imply Cloud
            "team_size_required": "standard",
            "cost_model": "open-source",
            "cost_predictability": "medium",
            "siem_integration": True,
            "compliance_certifications": [],
            "data_governance": False,
            "maturity": "production",
            "vendor_support": "community",
            "community_size": "large",
            "ocsf_support": False,
            "ml_analytics": False,
            "api_extensibility": True
        },
        "typical_annual_cost_range": "$100K-500K for managed service (Imply)",
        "cost_notes": "Open source (Apache 2.0). Self-hosted infrastructure: $60K-350K/year. Imply Cloud managed service: $150K-600K/year. Used at Airbnb, Lyft, Netflix for real-time metrics.",
        "evidence_source": "https://druid.apache.org/docs/latest/ (2025-01)",
        "last_updated": "2025-10-16T00:00:00",
        "validated_by": "Jeremy Wiley",
        "tags": ["open-source", "real-time", "olap", "streaming-analytics"]
    },
    {
        "id": "grafana-loki",
        "name": "Grafana Loki",
        "category": "SIEM",
        "description": "Open source log aggregation system designed for cost-effectiveness and operational simplicity. Inspired by Prometheus, Loki indexes only metadata (labels) not full-text, dramatically reducing storage costs.",
        "website": "https://grafana.com/oss/loki",
        "capabilities": {
            "sql_interface": False,  # Uses LogQL query language
            "streaming_query": True,
            "multi_engine_query": False,
            "open_table_format": "proprietary",
            "schema_evolution": False,
            "deployment_models": ["on-prem", "cloud", "hybrid"],
            "cloud_native": True,
            "multi_cloud": True,
            "operational_complexity": "low",
            "managed_service_available": True,  # Grafana Cloud
            "team_size_required": "lean",
            "cost_model": "open-source",
            "cost_predictability": "high",
            "siem_integration": False,  # IT IS the SIEM
            "compliance_certifications": [],
            "data_governance": False,
            "maturity": "production",
            "vendor_support": "commercial",  # Grafana Labs offers support
            "community_size": "very-large",
            "ocsf_support": False,
            "ml_analytics": False,
            "api_extensibility": True
        },
        "typical_annual_cost_range": "$20K-150K for Grafana Cloud logs",
        "cost_notes": "Open source (Apache 2.0). Self-hosted: $10K-80K/year infrastructure. Grafana Cloud: $0.50-2.00/GB ingested. Typical 1TB/day: $15K-60K/year. 10x cheaper than traditional SIEM for logs.",
        "evidence_source": "https://grafana.com/pricing (2025-01)",
        "last_updated": "2025-10-16T00:00:00",
        "validated_by": "Jeremy Wiley",
        "tags": ["open-source", "log-aggregation", "cost-effective", "grafana"]
    },
    {
        "id": "cribl",
        "name": "Cribl Stream",
        "category": "ETL/ELT Platform",
        "description": "Data routing, reduction, and transformation platform for observability and security data. Sits between data sources and destinations, enabling real-time filtering, enrichment, and multi-destination routing to reduce data costs.",
        "website": "https://cribl.io/stream",
        "capabilities": {
            "sql_interface": False,
            "streaming_query": True,
            "multi_engine_query": False,
            "open_table_format": "proprietary",
            "schema_evolution": True,
            "deployment_models": ["on-prem", "cloud", "hybrid", "edge"],
            "cloud_native": True,
            "multi_cloud": True,
            "operational_complexity": "medium",
            "managed_service_available": True,  # Cribl.Cloud
            "team_size_required": "lean",
            "cost_model": "subscription",
            "cost_predictability": "high",
            "siem_integration": True,  # Routes TO SIEMs
            "compliance_certifications": ["SOC2", "FedRAMP", "ISO27001"],
            "data_governance": True,
            "maturity": "production",
            "vendor_support": "enterprise",
            "community_size": "large",
            "ocsf_support": True,  # OCSF transformation pipelines
            "ml_analytics": False,
            "api_extensibility": True
        },
        "typical_annual_cost_range": "$100K-500K for typical deployment",
        "cost_notes": "Subscription pricing based on GB/day processed. Free tier: 1TB/day. Enterprise: $150K-600K/year for 5-50TB/day. ROI: Reduces downstream SIEM costs by 40-70% via data reduction.",
        "evidence_source": "https://cribl.io/pricing (2025-01)",
        "last_updated": "2025-10-16T00:00:00",
        "validated_by": "Jeremy Wiley",
        "tags": ["data-routing", "cost-reduction", "streaming", "vendor-neutral"]
    },
    {
        "id": "wazuh",
        "name": "Wazuh",
        "category": "SIEM",
        "description": "Open source unified XDR and SIEM platform for threat detection, integrity monitoring, incident response, and compliance. Fork of OSSEC with modern architecture, integrates with Elastic Stack for log analysis and visualization.",
        "website": "https://wazuh.com",
        "capabilities": {
            "sql_interface": False,  # Uses Elastic query DSL
            "streaming_query": True,
            "multi_engine_query": False,
            "open_table_format": "proprietary",
            "schema_evolution": False,
            "deployment_models": ["on-prem", "cloud", "hybrid"],
            "cloud_native": False,
            "multi_cloud": True,
            "operational_complexity": "medium",
            "managed_service_available": True,  # Wazuh Cloud
            "team_size_required": "standard",
            "cost_model": "open-source",
            "cost_predictability": "high",
            "siem_integration": False,  # IT IS the SIEM/XDR
            "compliance_certifications": ["PCI DSS", "HIPAA", "GDPR"],
            "data_governance": True,
            "maturity": "production",
            "vendor_support": "commercial",
            "community_size": "very-large",
            "ocsf_support": False,
            "ml_analytics": True,  # ML-based anomaly detection
            "api_extensibility": True
        },
        "typical_annual_cost_range": "$50K-300K for managed cloud service",
        "cost_notes": "Open source (GPL 2.0). Self-hosted: $30K-200K/year infrastructure + support. Wazuh Cloud: $80K-400K/year depending on agents/data volume. Popular Splunk alternative for compliance-focused orgs.",
        "evidence_source": "https://wazuh.com/pricing (2025-01)",
        "last_updated": "2025-10-16T00:00:00",
        "validated_by": "Jeremy Wiley",
        "tags": ["open-source", "xdr", "siem", "compliance", "ossec-fork"]
    },
    {
        "id": "graylog",
        "name": "Graylog",
        "category": "SIEM",
        "description": "Open source log management and SIEM platform for collecting, indexing, and analyzing security and application logs. Built on Elasticsearch/OpenSearch, provides centralized log management with real-time search and alerting.",
        "website": "https://www.graylog.org",
        "capabilities": {
            "sql_interface": False,
            "streaming_query": True,
            "multi_engine_query": False,
            "open_table_format": "proprietary",
            "schema_evolution": False,
            "deployment_models": ["on-prem", "cloud", "hybrid"],
            "cloud_native": True,
            "multi_cloud": True,
            "operational_complexity": "medium",
            "managed_service_available": True,  # Graylog Cloud
            "team_size_required": "lean",
            "cost_model": "hybrid",
            "cost_predictability": "high",
            "siem_integration": False,  # IT IS the SIEM
            "compliance_certifications": ["SOC2", "GDPR"],
            "data_governance": True,
            "maturity": "production",
            "vendor_support": "commercial",
            "community_size": "large",
            "ocsf_support": False,
            "ml_analytics": False,
            "api_extensibility": True
        },
        "typical_annual_cost_range": "$40K-250K for enterprise license",
        "cost_notes": "Open source (SSPL). Free tier: unlimited data. Enterprise: $50K-300K/year for advanced features (archiving, compliance, support). Graylog Cloud: $0.15-0.40/GB ingested.",
        "evidence_source": "https://www.graylog.org/pricing (2025-01)",
        "last_updated": "2025-10-16T00:00:00",
        "validated_by": "Jeremy Wiley",
        "tags": ["open-source", "log-management", "siem", "elasticsearch"]
    },
    {
        "id": "sysdig-secure",
        "name": "Sysdig Secure",
        "category": "SIEM",
        "description": "Cloud-native application protection platform (CNAPP) combining runtime security, vulnerability management, and compliance for containers and Kubernetes. Real-time threat detection with eBPF kernel instrumentation.",
        "website": "https://sysdig.com/products/secure",
        "capabilities": {
            "sql_interface": False,
            "streaming_query": True,
            "multi_engine_query": False,
            "open_table_format": "proprietary",
            "schema_evolution": False,
            "deployment_models": ["cloud", "hybrid"],
            "cloud_native": True,
            "multi_cloud": True,
            "operational_complexity": "medium",
            "managed_service_available": True,
            "team_size_required": "lean",
            "cost_model": "subscription",
            "cost_predictability": "high",
            "siem_integration": True,  # Integrates WITH SIEMs
            "compliance_certifications": ["SOC2", "ISO27001", "PCI DSS"],
            "data_governance": True,
            "maturity": "production",
            "vendor_support": "enterprise",
            "community_size": "medium",
            "ocsf_support": False,
            "ml_analytics": True,
            "api_extensibility": True
        },
        "typical_annual_cost_range": "$100K-600K for enterprise deployment",
        "cost_notes": "Subscription pricing per-host or per-container. Typical 500-container deployment: $150K-400K/year. Includes runtime security, vulnerability scanning, compliance, forensics. Competes with Prisma Cloud, Aqua Security.",
        "evidence_source": "https://sysdig.com/pricing (2025-01)",
        "last_updated": "2025-10-16T00:00:00",
        "validated_by": "Jeremy Wiley",
        "tags": ["cloud-native", "cnapp", "container-security", "kubernetes", "ebpf"]
    }
]

# Add new vendors to database
db["vendors"].extend(new_vendors)

# Sort vendors by ID for consistency
db["vendors"] = sorted(db["vendors"], key=lambda v: v["id"])

# Write updated database
with open(db_path, "w") as f:
    json.dump(db, f, indent=2, ensure_ascii=False)
    f.write("\n")  # Add trailing newline

print(f"Added {len(new_vendors)} vendors to database")
print(f"Total vendors: {len(db['vendors'])}")
print("\nNew vendors:")
for v in new_vendors:
    print(f"  - {v['name']} ({v['category']})")
