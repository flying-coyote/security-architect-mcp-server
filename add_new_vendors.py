#!/usr/bin/env python3
"""
Add new vendors to the Security Architect MCP Server vendor database.
Based on LinkedIn intelligence from December 2025.
"""

import json
from datetime import datetime

def add_new_vendors():
    # Load existing database
    with open('data/vendor_database.json', 'r') as f:
        data = json.load(f)

    # New vendors to add based on LinkedIn intelligence
    new_vendors = [
        {
            "id": "tenzir",
            "name": "Tenzir",
            "category": "ETL/Ingestion",
            "description": "Open-source security data pipeline with MCP-enabled AI parser generation for automated OCSF mapping. AWS-native deployment for Security Lake.",
            "website": "https://tenzir.com",
            "capabilities": {
                "sql_interface": False,
                "streaming_query": True,
                "multi_engine_query": False,
                "open_table_format": "native",
                "schema_evolution": True,
                "deployment_models": ["cloud", "on-prem", "hybrid"],
                "cloud_native": True,
                "multi_cloud": True,
                "operational_complexity": "low",
                "managed_service_available": True,
                "team_size_required": "small",
                "cost_model": "open-source",
                "cost_predictability": "high",
                "siem_integration": True,
                "compliance_certifications": [],
                "data_governance": True,
                "maturity": "production",
                "vendor_support": "community",
                "community_size": "growing",
                "ocsf_support": True,  # Native OCSF support
                "ml_analytics": True,  # AI-generated parsers
                "api_extensibility": True,
                "iceberg_support": True,
                "delta_lake_support": False,
                "hudi_support": False,
                "polaris_catalog_support": False,
                "unity_catalog_support": False,
                "nessie_catalog_support": False,
                "glue_catalog_support": True,  # AWS-native
                "hive_metastore_support": False,
                "dbt_integration": False,
                "spark_transformation_support": False,
                "query_latency_p95": None,
                "query_concurrency": None,
                "mcp_enabled": True,  # MCP Server for AI parser generation
                "ai_parser_generation": True  # Unique capability
            },
            "typical_annual_cost_range": "OSS free, Enterprise $50K-200K",
            "cost_notes": "Open source execution engine. Enterprise support and cloud deployment extra.",
            "evidence_level": "B",
            "evidence_source": "Tenzir LinkedIn announcement at AWS re:Invent 2025",
            "analyst_coverage": None,
            "production_deployments": ["AWS Security Lake customers"],
            "github_url": "https://github.com/tenzir",
            "documentation_quality": "good",
            "adoption_trend": "growing",
            "strengths": [
                "AI-generated OCSF parsers",
                "MCP server integration",
                "True open source",
                "AWS Security Lake native"
            ],
            "weaknesses": [
                "ETL-only (not full platform)",
                "Early stage adoption",
                "Limited enterprise references"
            ],
            "best_for": [
                "Security data lake ETL",
                "OCSF transformation",
                "AWS Security Lake ingestion"
            ],
            "avoid_if": [
                "Need full SIEM platform",
                "Want established vendor"
            ],
            "tco_factors": {
                "platform_cost": 0,
                "operational_cost": "low",
                "hidden_costs": ["Training on MCP patterns"]
            },
            "validated": "2025-12-06",
            "validated_by": "LinkedIn Intelligence Dec 2025",
            "tags": ["open-source", "mcp-enabled", "etl", "ocsf-native", "ai-parsers", "aws"]
        },
        {
            "id": "estuary",
            "name": "Estuary",
            "category": "ETL/Ingestion",
            "description": "Real-time data pipeline platform with CDC and streaming capabilities. Cost-effective alternative for terabyte-scale workloads.",
            "website": "https://estuary.dev",
            "capabilities": {
                "sql_interface": False,
                "streaming_query": True,
                "multi_engine_query": False,
                "open_table_format": "proprietary",
                "schema_evolution": True,
                "deployment_models": ["cloud"],
                "cloud_native": True,
                "multi_cloud": True,
                "operational_complexity": "low",
                "managed_service_available": True,
                "team_size_required": "small",
                "cost_model": "consumption",
                "cost_predictability": "medium",
                "siem_integration": False,
                "compliance_certifications": ["SOC2"],
                "data_governance": True,
                "maturity": "production",
                "vendor_support": "commercial",
                "community_size": "small",
                "ocsf_support": False,
                "ml_analytics": False,
                "api_extensibility": True,
                "iceberg_support": True,
                "delta_lake_support": True,
                "hudi_support": False,
                "polaris_catalog_support": False,
                "unity_catalog_support": False,
                "nessie_catalog_support": False,
                "glue_catalog_support": True,
                "hive_metastore_support": False,
                "dbt_integration": True,
                "spark_transformation_support": False,
                "query_latency_p95": None,
                "query_concurrency": None,
                "real_time_cdc": True  # Key differentiator
            },
            "typical_annual_cost_range": "<$200K for TB-scale",
            "cost_notes": "Significantly cheaper than $200K/year incumbent for terabyte monthly workloads",
            "evidence_level": "C",
            "evidence_source": "Seattle Data Guy LinkedIn post Dec 3, 2025",
            "analyst_coverage": None,
            "production_deployments": ["2+ year production use cases"],
            "github_url": "https://github.com/estuary",
            "documentation_quality": "good",
            "adoption_trend": "growing",
            "strengths": [
                "Real-time CDC",
                "Cost-effective at scale",
                "It just works reliability",
                "Terabyte-scale proven"
            ],
            "weaknesses": [
                "Small community",
                "Limited security features",
                "ETL-only solution"
            ],
            "best_for": [
                "Real-time data pipelines",
                "CDC workloads",
                "Cost-sensitive teams"
            ],
            "avoid_if": [
                "Need full analytics platform",
                "Require on-prem deployment"
            ],
            "tco_factors": {
                "platform_cost": "low",
                "operational_cost": "low",
                "hidden_costs": ["Limited ecosystem"]
            },
            "validated": "2025-12-06",
            "validated_by": "LinkedIn Intelligence Dec 2025",
            "tags": ["commercial", "real-time", "cdc", "cost-effective", "etl"]
        },
        {
            "id": "databricks-lakebase",
            "name": "Databricks Lakebase",
            "category": "Lakehouse Platform",
            "description": "OLTP capabilities inside Databricks lakehouse. Enables transactional workloads alongside analytics in unified platform.",
            "website": "https://databricks.com/lakebase",
            "capabilities": {
                "sql_interface": True,
                "streaming_query": True,
                "multi_engine_query": True,
                "open_table_format": "delta_lake",
                "schema_evolution": True,
                "deployment_models": ["cloud"],
                "cloud_native": True,
                "multi_cloud": True,
                "operational_complexity": "medium",
                "managed_service_available": True,
                "team_size_required": "standard",
                "cost_model": "consumption",
                "cost_predictability": "low",
                "siem_integration": False,
                "compliance_certifications": ["SOC2", "ISO27001", "HIPAA"],
                "data_governance": True,
                "maturity": "production",
                "vendor_support": "commercial",
                "community_size": "large",
                "ocsf_support": False,
                "ml_analytics": True,
                "api_extensibility": True,
                "iceberg_support": False,
                "delta_lake_support": True,  # Native
                "hudi_support": False,
                "polaris_catalog_support": False,
                "unity_catalog_support": True,  # Native
                "nessie_catalog_support": False,
                "glue_catalog_support": True,
                "hive_metastore_support": True,
                "dbt_integration": True,
                "spark_transformation_support": True,
                "query_latency_p95": 100,  # OLTP performance
                "query_concurrency": 1000,
                "oltp_support": True,  # Key differentiator
                "acid_transactions": True
            },
            "typical_annual_cost_range": "$200K-2M+",
            "cost_notes": "Part of Databricks platform. OLTP adds to compute costs.",
            "evidence_level": "A",
            "evidence_source": "Reynold Xin (Databricks co-founder) interview Nov 29, 2025",
            "analyst_coverage": "Gartner MQ Leader",
            "production_deployments": ["Netflix", "Rivian", "Block"],
            "github_url": None,
            "documentation_quality": "excellent",
            "adoption_trend": "accelerating",
            "strengths": [
                "OLTP + OLAP unified",
                "Unity Catalog governance",
                "Enterprise maturity",
                "AI/ML integration"
            ],
            "weaknesses": [
                "High cost at scale",
                "Vendor lock-in risk",
                "Complex pricing"
            ],
            "best_for": [
                "Unified analytics + transactions",
                "Real-time security events",
                "Enterprise data platforms"
            ],
            "avoid_if": [
                "Cost-sensitive",
                "Simple ETL needs",
                "Prefer open source"
            ],
            "tco_factors": {
                "platform_cost": "high",
                "operational_cost": "medium",
                "hidden_costs": ["DBU consumption", "Unity Catalog costs"]
            },
            "validated": "2025-12-06",
            "validated_by": "LinkedIn Intelligence Dec 2025",
            "tags": ["commercial", "lakehouse", "oltp", "enterprise", "unity-catalog"]
        },
        {
            "id": "knostic",
            "name": "Knostic",
            "category": "Security Tools",
            "description": "Security defense platform for AI agents and MCP servers. Protects against prompt injection and agent attacks.",
            "website": "https://knostic.com",
            "capabilities": {
                "sql_interface": False,
                "streaming_query": False,
                "multi_engine_query": False,
                "open_table_format": "none",
                "schema_evolution": False,
                "deployment_models": ["cloud", "on-prem"],
                "cloud_native": True,
                "multi_cloud": True,
                "operational_complexity": "low",
                "managed_service_available": True,
                "team_size_required": "small",
                "cost_model": "subscription",
                "cost_predictability": "high",
                "siem_integration": True,
                "compliance_certifications": [],
                "data_governance": False,
                "maturity": "emerging",
                "vendor_support": "commercial",
                "community_size": "small",
                "ocsf_support": False,
                "ml_analytics": False,
                "api_extensibility": True,
                "iceberg_support": False,
                "delta_lake_support": False,
                "hudi_support": False,
                "polaris_catalog_support": False,
                "unity_catalog_support": False,
                "nessie_catalog_support": False,
                "glue_catalog_support": False,
                "hive_metastore_support": False,
                "dbt_integration": False,
                "spark_transformation_support": False,
                "query_latency_p95": None,
                "query_concurrency": None,
                "mcp_security": True,  # Key differentiator
                "agent_defense": True,
                "prompt_injection_protection": True
            },
            "typical_annual_cost_range": "Unknown",
            "cost_notes": "Early stage product, pricing not public",
            "evidence_level": "D",
            "evidence_source": "Gadi Evron LinkedIn announcement Dec 2, 2025",
            "analyst_coverage": None,
            "production_deployments": [],
            "github_url": None,
            "documentation_quality": "unknown",
            "adoption_trend": "emerging",
            "strengths": [
                "MCP-specific security",
                "Agent attack defense",
                "Industry veterans (Gadi Evron)"
            ],
            "weaknesses": [
                "Early stage",
                "Unproven at scale",
                "Limited documentation"
            ],
            "best_for": [
                "MCP server protection",
                "AI agent security",
                "Prompt injection defense"
            ],
            "avoid_if": [
                "Need data platform",
                "Want mature solution"
            ],
            "tco_factors": {
                "platform_cost": "unknown",
                "operational_cost": "low",
                "hidden_costs": ["Early adopter risk"]
            },
            "validated": "2025-12-06",
            "validated_by": "LinkedIn Intelligence Dec 2025",
            "tags": ["security", "mcp-defense", "ai-security", "emerging"]
        }
    ]

    # Add new vendors to the list
    data['vendors'].extend(new_vendors)

    # Update metadata
    data['total_vendors'] = len(data['vendors'])
    data['last_full_update'] = datetime.now().isoformat()

    # Save updated database
    with open('data/vendor_database.json', 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Successfully added {len(new_vendors)} new vendors:")
    for vendor in new_vendors:
        print(f"  - {vendor['name']} ({vendor['id']}): {vendor['category']}")
    print(f"\nTotal vendors now: {data['total_vendors']}")

if __name__ == "__main__":
    add_new_vendors()