"""
Tests for isolation pattern recommendations.

Validates catalog, query engine, and table format recommendations based on
infrastructure isolation patterns (isolated_dedicated, shared_corporate,
multi_tenant_mssp).
"""

import pytest

from src.utils.recommendations import (
    recommend_catalog_with_isolation,
    recommend_query_engine_with_isolation,
    recommend_table_format_with_isolation,
    get_isolation_pattern_recommendations,
)


# ============================================================================
# CATALOG RECOMMENDATION TESTS
# ============================================================================


def test_isolated_dedicated_recommends_polaris_by_default():
    """Isolated dedicated infrastructure should recommend Polaris by default."""
    result = recommend_catalog_with_isolation("isolated_dedicated")

    assert result.primary == "Polaris"
    assert result.score == 8
    assert "0%" in result.performance_overhead
    assert "Low" in result.tco
    assert "Netflix" in result.production_examples


def test_isolated_dedicated_with_git_workflows_recommends_nessie():
    """Isolated dedicated with Git workflows requirement should recommend Nessie."""
    result = recommend_catalog_with_isolation(
        "isolated_dedicated",
        {"git_workflows": True}
    )

    assert result.primary == "Nessie"
    assert result.score == 9
    assert "0%" in result.performance_overhead
    assert "Huntress" in result.production_examples or "Netflix" in result.production_examples


def test_isolated_dedicated_with_ai_ml_governance_recommends_unity():
    """Isolated dedicated with AI/ML governance should recommend Unity Catalog."""
    result = recommend_catalog_with_isolation(
        "isolated_dedicated",
        {"ai_ml_governance": True}
    )

    assert result.primary == "Unity Catalog"
    assert result.score == 7
    assert "0%" in result.performance_overhead  # No RLS needed for isolated
    assert "Medium" in result.tco


def test_shared_corporate_requires_unity_catalog():
    """Shared corporate platform should require Unity Catalog for fine-grained access."""
    result = recommend_catalog_with_isolation("shared_corporate")

    assert result.primary == "Unity Catalog"
    assert result.score == 8
    assert "15-50%" in result.performance_overhead  # RLS + column masking
    assert "High" in result.tco


def test_multi_tenant_mssp_requires_unity_catalog():
    """Multi-tenant MSSP should require Unity Catalog for row-level security."""
    result = recommend_catalog_with_isolation("multi_tenant_mssp")

    assert result.primary == "Unity Catalog"
    assert result.score == 9
    assert "5-30%" in result.performance_overhead  # RLS evaluation
    assert "High" in result.tco


# ============================================================================
# QUERY ENGINE RECOMMENDATION TESTS
# ============================================================================


def test_isolated_dedicated_real_time_recommends_clickhouse():
    """Isolated dedicated with real-time dashboards should recommend ClickHouse."""
    result = recommend_query_engine_with_isolation(
        "isolated_dedicated",
        {"real_time_dashboards": True}
    )

    assert "ClickHouse" in result.primary
    assert "0%" in result.performance_overhead
    assert "Netflix" in result.architecture_pattern


def test_isolated_dedicated_ad_hoc_recommends_duckdb():
    """Isolated dedicated with ad-hoc analysis should recommend DuckDB."""
    result = recommend_query_engine_with_isolation(
        "isolated_dedicated",
        {"ad_hoc_analysis": True}
    )

    assert "DuckDB" in result.primary
    assert "0%" in result.performance_overhead
    assert "Okta" in result.architecture_pattern


def test_isolated_dedicated_default_recommends_trino():
    """Isolated dedicated without specific requirements should recommend Trino."""
    result = recommend_query_engine_with_isolation("isolated_dedicated")

    assert "Trino" in result.primary
    assert "0%" in result.performance_overhead
    assert "Standard isolated security platform" in result.architecture_pattern


def test_shared_corporate_with_databricks_recommends_databricks_sql():
    """Shared corporate with Databricks ecosystem should recommend Databricks SQL."""
    result = recommend_query_engine_with_isolation(
        "shared_corporate",
        {"databricks_ecosystem": True}
    )

    assert "Databricks SQL" in result.primary
    assert "15-30%" in result.performance_overhead  # Unity Catalog RLS
    assert "Multi-tenant MSSP" in result.architecture_pattern


def test_multi_tenant_mssp_recommends_rls_aware_engine():
    """Multi-tenant MSSP should recommend RLS-aware query engine."""
    result = recommend_query_engine_with_isolation("multi_tenant_mssp")

    assert "Trino" in result.primary
    assert "5-30%" in result.performance_overhead
    assert "row filter" in result.rationale.lower()


# ============================================================================
# TABLE FORMAT RECOMMENDATION TESTS
# ============================================================================


def test_isolated_dedicated_recommends_iceberg():
    """Isolated dedicated infrastructure should recommend Iceberg."""
    result = recommend_table_format_with_isolation("isolated_dedicated")

    assert result.primary == "Iceberg"
    assert "No metadata encryption overhead" in result.performance_considerations
    assert "Polaris" in result.catalog_compatibility


def test_shared_corporate_recommends_delta_or_iceberg():
    """Shared corporate should recommend Delta Lake or Iceberg (both support Unity Catalog RLS)."""
    result = recommend_table_format_with_isolation("shared_corporate")

    assert "Delta Lake or Iceberg" in result.primary
    assert "10-20%" in result.performance_considerations  # Metadata encryption
    assert "Unity Catalog" in result.catalog_compatibility


def test_multi_tenant_mssp_recommends_unity_compatible_formats():
    """Multi-tenant MSSP should recommend formats compatible with Unity Catalog."""
    result = recommend_table_format_with_isolation("multi_tenant_mssp")

    assert "Delta Lake or Iceberg" in result.primary
    assert "Unity Catalog" in result.catalog_compatibility


# ============================================================================
# COMPREHENSIVE RECOMMENDATIONS TEST
# ============================================================================


def test_get_isolation_pattern_recommendations_isolated():
    """Test comprehensive recommendations for isolated dedicated infrastructure."""
    result = get_isolation_pattern_recommendations("isolated_dedicated")

    assert result["isolation_pattern"] == "isolated_dedicated"
    assert result["catalog"]["primary"] == "Polaris"
    assert "Iceberg" in result["table_format"]["primary"]
    assert "Trino" in result["query_engine"]["primary"]
    assert "0%" in result["summary"]  # Performance benefits


def test_get_isolation_pattern_recommendations_isolated_with_git():
    """Test recommendations for isolated dedicated with Git workflows."""
    result = get_isolation_pattern_recommendations(
        "isolated_dedicated",
        {"git_workflows": True}
    )

    assert result["catalog"]["primary"] == "Nessie"
    assert "Iceberg" in result["table_format"]["primary"]
    assert "15-50% faster queries" in result["summary"]


def test_get_isolation_pattern_recommendations_shared():
    """Test comprehensive recommendations for shared corporate platform."""
    result = get_isolation_pattern_recommendations("shared_corporate")

    assert result["isolation_pattern"] == "shared_corporate"
    assert result["catalog"]["primary"] == "Unity Catalog"
    assert "Unity Catalog" in result["table_format"]["catalog_compatibility"]
    assert "15-50%" in result["catalog"]["performance_overhead"]


def test_get_isolation_pattern_recommendations_mssp():
    """Test comprehensive recommendations for multi-tenant MSSP."""
    result = get_isolation_pattern_recommendations("multi_tenant_mssp")

    assert result["isolation_pattern"] == "multi_tenant_mssp"
    assert result["catalog"]["primary"] == "Unity Catalog"
    assert "5-30%" in result["catalog"]["performance_overhead"]
    assert "Row-level security" in result["summary"]


# ============================================================================
# EDGE CASES
# ============================================================================


def test_unknown_isolation_pattern_defaults_safely():
    """Unknown isolation pattern should default to safe recommendations."""
    result_catalog = recommend_catalog_with_isolation("unknown_pattern")
    result_query = recommend_query_engine_with_isolation("unknown_pattern")
    result_table = recommend_table_format_with_isolation("unknown_pattern")

    # Should default to Polaris, Trino, Iceberg (safe defaults)
    assert result_catalog.primary == "Polaris"
    assert "Trino" in result_query.primary
    assert result_table.primary == "Iceberg"


def test_isolated_dedicated_with_multiple_requirements():
    """Test isolated dedicated with multiple requirements combines correctly."""
    result = get_isolation_pattern_recommendations(
        "isolated_dedicated",
        {
            "git_workflows": True,
            "real_time_dashboards": True,
            "ad_hoc_analysis": False
        }
    )

    # Git workflows should influence catalog (Nessie)
    assert result["catalog"]["primary"] == "Nessie"

    # Real-time dashboards should influence query engine (ClickHouse)
    assert "ClickHouse" in result["query_engine"]["primary"]

    # Table format should still be Iceberg for isolated platforms
    assert "Iceberg" in result["table_format"]["primary"]
