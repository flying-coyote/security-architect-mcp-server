"""
Recommendation Logic with Isolation Pattern Awareness

Provides catalog, query engine, and table format recommendations based on
infrastructure isolation patterns. Integrates findings from
ARCHITECTURE-PATTERNS-SECURITY-DATA.md (security-data-commons-blog).

Isolation patterns affect technology recommendations:
- **Isolated dedicated**: Table-level RBAC sufficient, performance-first selection
- **Shared corporate**: Fine-grained access control required (RLS, column masking)
- **Multi-tenant MSSP**: Row-level security essential for tenant isolation
"""

from typing import Dict, List


class CatalogRecommendation:
    """Catalog recommendation with rationale."""

    def __init__(
        self,
        primary: str,
        score: int,
        rationale: str,
        alternatives: List[str],
        performance_overhead: str,
        tco: str,
        production_examples: List[str]
    ):
        self.primary = primary
        self.score = score
        self.rationale = rationale
        self.alternatives = alternatives
        self.performance_overhead = performance_overhead
        self.tco = tco
        self.production_examples = production_examples


class QueryEngineRecommendation:
    """Query engine recommendation with rationale."""

    def __init__(
        self,
        primary: str,
        rationale: str,
        alternatives: List[str],
        performance_overhead: str,
        architecture_pattern: str
    ):
        self.primary = primary
        self.rationale = rationale
        self.alternatives = alternatives
        self.performance_overhead = performance_overhead
        self.architecture_pattern = architecture_pattern


class TableFormatRecommendation:
    """Table format recommendation with rationale."""

    def __init__(
        self,
        primary: str,
        rationale: str,
        alternatives: List[str],
        performance_considerations: str,
        catalog_compatibility: str
    ):
        self.primary = primary
        self.rationale = rationale
        self.alternatives = alternatives
        self.performance_considerations = performance_considerations
        self.catalog_compatibility = catalog_compatibility


def recommend_catalog_with_isolation(
    isolation_pattern: str,
    requirements: Dict[str, bool] = None
) -> CatalogRecommendation:
    """
    Recommend catalog based on isolation pattern.

    Isolated platforms: Polaris (vendor-neutral) or Nessie (Git workflows) preferred
    Shared platforms: Unity Catalog (fine-grained access) essential
    Multi-tenant MSSP: Unity Catalog (row-level security) required

    Args:
        isolation_pattern: Infrastructure isolation pattern
        requirements: Additional requirements (git_workflows, ai_ml_governance, etc.)

    Returns:
        CatalogRecommendation with primary choice and rationale
    """
    requirements = requirements or {}

    if isolation_pattern == "multi_tenant_mssp":
        return CatalogRecommendation(
            primary="Unity Catalog",
            score=9,
            rationale="Multi-tenant MSSP requires row-level security (Customer A analysts only see Customer A logs). Unity Catalog provides tenant-level row filters essential for compliance.",
            alternatives=[],
            performance_overhead="5-30% (RLS evaluation per query)",
            tco="High (Unity Catalog licensing), but worth cost for multi-tenant isolation",
            production_examples=["Arctic Wolf (hypothesized)", "Expel (hypothesized)", "Red Canary (hypothesized)"]
        )

    elif isolation_pattern == "shared_corporate":
        return CatalogRecommendation(
            primary="Unity Catalog",
            score=8,
            rationale="Shared corporate data platform (PII + security logs) requires fine-grained access control. Unity Catalog provides row-level security and column masking for compliance.",
            alternatives=["Polaris + Trino row filters (if avoiding Databricks lock-in)"],
            performance_overhead="15-50% (RLS + column masking + metadata encryption)",
            tco="High (Unity Catalog licensing + compute overhead)",
            production_examples=["Multi-tenant MSSPs", "Federated global security teams"]
        )

    elif isolation_pattern == "isolated_dedicated":
        # Isolated platform: table-level RBAC sufficient, choose based on features
        if requirements.get("git_workflows") or requirements.get("multi_table_transactions"):
            return CatalogRecommendation(
                primary="Nessie",
                score=9,
                rationale="Isolated security infrastructure (table-level RBAC sufficient) + need for Git-like version control and multi-table transactions (OCSF normalization). Nessie provides branch-level isolation for testing detection rules.",
                alternatives=["Polaris (if vendor neutrality > Git workflows)"],
                performance_overhead="0% (no RLS/masking overhead)",
                tco="Low (open-source, no licensing costs)",
                production_examples=["Netflix", "Huntress"]
            )

        elif requirements.get("ai_ml_governance") or requirements.get("delta_sharing"):
            return CatalogRecommendation(
                primary="Unity Catalog",
                score=7,
                rationale="Isolated infrastructure simplifies Unity Catalog deployment (no RLS needed), but still benefits from AI/ML governance or Delta Sharing for external data sharing.",
                alternatives=["Polaris (if avoiding Unity Catalog cost)"],
                performance_overhead="0% (no RLS/masking needed for isolated platform)",
                tco="Medium (Unity Catalog licensing, but avoid RLS compute overhead)",
                production_examples=["Isolated security platforms with AI/ML workloads"]
            )

        else:
            # Default for isolated platforms: Polaris (vendor-neutral)
            return CatalogRecommendation(
                primary="Polaris",
                score=8,
                rationale="Isolated security infrastructure (table-level RBAC sufficient) + vendor neutrality priority. Polaris provides pure Iceberg catalog with cloud-agnostic deployment.",
                alternatives=["Nessie (if Git workflows needed)", "Unity Catalog (if AI/ML governance needed)"],
                performance_overhead="0% (no RLS/masking overhead)",
                tco="Low (open-source, no licensing costs)",
                production_examples=["Netflix", "Huntress"]
            )

    else:
        # Fallback: default to Polaris for unknown patterns
        return CatalogRecommendation(
            primary="Polaris",
            score=7,
            rationale="Vendor-neutral Iceberg catalog with table-level RBAC. Assess isolation pattern for performance optimization.",
            alternatives=["Unity Catalog (if fine-grained access needed)"],
            performance_overhead="0% (table-level RBAC)",
            tco="Low (open-source)",
            production_examples=["Netflix"]
        )


def recommend_query_engine_with_isolation(
    isolation_pattern: str,
    requirements: Dict[str, bool] = None
) -> QueryEngineRecommendation:
    """
    Recommend query engine based on isolation pattern.

    Isolated platform: performance-first engine selection
    Shared platform or MSSP: row-level security required

    Args:
        isolation_pattern: Infrastructure isolation pattern
        requirements: Additional requirements (real_time_dashboards, ad_hoc_analysis, etc.)

    Returns:
        QueryEngineRecommendation with primary choice and rationale
    """
    requirements = requirements or {}

    if isolation_pattern == "isolated_dedicated":
        # Isolated platform: performance-first engine selection
        if requirements.get("real_time_dashboards"):
            return QueryEngineRecommendation(
                primary="ClickHouse (hot tier, 1-3 second queries)",
                rationale="Isolated infrastructure enables ClickHouse MergeTree hot tier (7-day retention) + Iceberg cold tier (90+ days) without RBAC conflicts. No row-level security overhead in ClickHouse queries.",
                alternatives=["Trino (if multi-cloud federation needed)"],
                performance_overhead="0% (no RLS/masking overhead)",
                architecture_pattern="Netflix (ClickHouse hot + Iceberg cold, isolated VPC)"
            )

        elif requirements.get("ad_hoc_analysis"):
            return QueryEngineRecommendation(
                primary="DuckDB (laptop-based, S3 Direct Query via HTTPFS)",
                rationale="Isolated infrastructure simplifies DuckDB security (table-level S3 IAM permissions). Single-process queries ideal for security analysts (no multi-user access control needed).",
                alternatives=["Trino (if team-wide shared query engine needed)"],
                performance_overhead="0% (no access control overhead)",
                architecture_pattern="Okta security analytics (Jake Thomas validation, DuckDB + Iceberg)"
            )

        else:
            return QueryEngineRecommendation(
                primary="Trino (federated queries, Iceberg-native)",
                rationale="Isolated infrastructure eliminates Trino row filter configuration overhead. Direct table queries without access control complexity.",
                alternatives=["Dremio (if semantic layer + Reflections needed)"],
                performance_overhead="0% (no row filter evaluation)",
                architecture_pattern="Standard isolated security platform (Trino + Iceberg + Polaris)"
            )

    elif isolation_pattern in ["shared_corporate", "multi_tenant_mssp"]:
        # Shared platform or MSSP: row-level security required
        if requirements.get("databricks_ecosystem"):
            return QueryEngineRecommendation(
                primary="Databricks SQL (Unity Catalog native)",
                rationale="Shared platform or multi-tenant MSSP requires fine-grained access. Databricks SQL natively supports Unity Catalog row-level security and column masking.",
                alternatives=["Trino (if avoiding Databricks lock-in, configure row filters)"],
                performance_overhead="15-30% (Unity Catalog RLS evaluation)",
                architecture_pattern="Multi-tenant MSSP (customer-level row filters)"
            )
        else:
            return QueryEngineRecommendation(
                primary="Trino (with row filter configuration)",
                rationale="Shared platform requires row-level security. Trino supports row filters per table (configure via SQL or system tables).",
                alternatives=["Dremio (column masking + row filters)"],
                performance_overhead="5-30% (row filter evaluation per query)",
                architecture_pattern="Shared corporate data platform (Trino + Polaris + row filters)"
            )

    else:
        # Fallback: default to Trino
        return QueryEngineRecommendation(
            primary="Trino (federated queries)",
            rationale="Flexible SQL query engine with broad ecosystem support. Assess isolation pattern for performance optimization.",
            alternatives=["ClickHouse (if low-latency required)", "DuckDB (if ad-hoc analysis)"],
            performance_overhead="Depends on access control configuration",
            architecture_pattern="Standard security platform"
        )


def recommend_table_format_with_isolation(
    isolation_pattern: str,
    requirements: Dict[str, bool] = None
) -> TableFormatRecommendation:
    """
    Recommend table format based on isolation pattern.

    Isolated platform: open format choice without RLS constraints
    Shared platform or MSSP: table format must support Unity Catalog RLS

    Args:
        isolation_pattern: Infrastructure isolation pattern
        requirements: Additional requirements (databricks_ecosystem, etc.)

    Returns:
        TableFormatRecommendation with primary choice and rationale
    """
    requirements = requirements or {}

    if isolation_pattern == "isolated_dedicated":
        return TableFormatRecommendation(
            primary="Iceberg",
            rationale="Isolated security infrastructure enables open format choice without RLS constraints. Iceberg provides broad query engine support (Trino, Dremio, ClickHouse, DuckDB), vendor neutrality, and mature metadata architecture.",
            alternatives=["Delta Lake (if already on Databricks)"],
            performance_considerations="No metadata encryption overhead needed (network isolation + IAM sufficient)",
            catalog_compatibility="Polaris (pure Iceberg), Nessie (Iceberg-native), Unity Catalog (multi-format)"
        )

    elif isolation_pattern in ["shared_corporate", "multi_tenant_mssp"]:
        return TableFormatRecommendation(
            primary="Delta Lake or Iceberg (both support Unity Catalog RLS)",
            rationale="Shared platform or multi-tenant MSSP requires Unity Catalog for fine-grained access. Both Delta Lake and Iceberg support Unity Catalog row-level security and column masking.",
            alternatives=[],
            performance_considerations="Metadata encryption overhead 10-20% (shared platform security requirement)",
            catalog_compatibility="Unity Catalog (primary), Polaris (if Iceberg + avoiding Databricks)"
        )

    else:
        # Fallback: default to Iceberg
        return TableFormatRecommendation(
            primary="Iceberg",
            rationale="Open format with broad query engine support and vendor neutrality. Assess isolation pattern for performance optimization.",
            alternatives=["Delta Lake (if Databricks ecosystem)"],
            performance_considerations="Depends on security requirements",
            catalog_compatibility="Polaris, Nessie, Unity Catalog, AWS Glue"
        )


def get_isolation_pattern_recommendations(
    isolation_pattern: str,
    additional_requirements: Dict[str, bool] = None
) -> Dict[str, any]:
    """
    Get comprehensive recommendations for catalog, query engine, and table format
    based on isolation pattern.

    Args:
        isolation_pattern: Infrastructure isolation pattern
        additional_requirements: Additional requirements

    Returns:
        Dictionary with recommendations for catalog, query_engine, and table_format
    """
    catalog_rec = recommend_catalog_with_isolation(isolation_pattern, additional_requirements)
    query_engine_rec = recommend_query_engine_with_isolation(isolation_pattern, additional_requirements)
    table_format_rec = recommend_table_format_with_isolation(isolation_pattern, additional_requirements)

    return {
        "catalog": {
            "primary": catalog_rec.primary,
            "score": catalog_rec.score,
            "rationale": catalog_rec.rationale,
            "alternatives": catalog_rec.alternatives,
            "performance_overhead": catalog_rec.performance_overhead,
            "tco": catalog_rec.tco,
            "production_examples": catalog_rec.production_examples
        },
        "query_engine": {
            "primary": query_engine_rec.primary,
            "rationale": query_engine_rec.rationale,
            "alternatives": query_engine_rec.alternatives,
            "performance_overhead": query_engine_rec.rationale,
            "architecture_pattern": query_engine_rec.architecture_pattern
        },
        "table_format": {
            "primary": table_format_rec.primary,
            "rationale": table_format_rec.rationale,
            "alternatives": table_format_rec.alternatives,
            "performance_considerations": table_format_rec.performance_considerations,
            "catalog_compatibility": table_format_rec.catalog_compatibility
        },
        "isolation_pattern": isolation_pattern,
        "summary": _generate_summary(isolation_pattern, catalog_rec, query_engine_rec, table_format_rec)
    }


def _generate_summary(
    isolation_pattern: str,
    catalog_rec: CatalogRecommendation,
    query_engine_rec: QueryEngineRecommendation,
    table_format_rec: TableFormatRecommendation
) -> str:
    """Generate a concise summary of recommendations."""

    if isolation_pattern == "isolated_dedicated":
        return f"""
**Recommended Stack (Isolation-First Security Pattern)**:
- **Table Format**: {table_format_rec.primary}
- **Catalog**: {catalog_rec.primary}
- **Query Engine**: {query_engine_rec.primary}

**Key Benefits**:
- 0% row-level security overhead (table-level RBAC only)
- 0% column masking overhead (security team authorized for all fields)
- 0% metadata encryption overhead (network isolation + IAM sufficient)
- **Total**: 15-50% faster queries vs shared platform with Unity Catalog RLS

**Production Validation**: {', '.join(catalog_rec.production_examples[:2])}
        """.strip()

    elif isolation_pattern == "shared_corporate":
        return f"""
**Recommended Stack (Shared Corporate Platform)**:
- **Table Format**: {table_format_rec.primary}
- **Catalog**: {catalog_rec.primary}
- **Query Engine**: {query_engine_rec.primary}

**Requirements**:
- Fine-grained access control (row-level security, column masking)
- Compliance with data co-location (PII + security logs)

**Performance Overhead**: {catalog_rec.performance_overhead}
**TCO**: {catalog_rec.tco}
        """.strip()

    elif isolation_pattern == "multi_tenant_mssp":
        return f"""
**Recommended Stack (Multi-Tenant MSSP)**:
- **Table Format**: {table_format_rec.primary}
- **Catalog**: {catalog_rec.primary}
- **Query Engine**: {query_engine_rec.primary}

**Requirements**:
- Row-level security essential for tenant isolation
- Customer A analysts only see Customer A logs

**Performance Overhead**: {catalog_rec.performance_overhead}
**TCO**: {catalog_rec.tco} (worth cost for multi-tenant isolation)
        """.strip()

    else:
        return f"Recommended: {table_format_rec.primary} + {catalog_rec.primary} + {query_engine_rec.primary}"
