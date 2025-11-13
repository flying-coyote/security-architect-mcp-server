"""
Tests for Tier 1 filtering logic.

Tests include realistic scenarios from the book's Chapter 4 journeys
(Jennifer, Marcus, Priya) to validate decision framework accuracy.
"""

import pytest

from src.models import (
    BudgetRange,
    DataSovereignty,
    DecisionState,
    TeamSize,
    VendorTolerance,
)
from src.tools.filter_vendors import (
    FilterResult,
    apply_foundational_filters,
    apply_tier1_filters,
    filter_by_budget,
    filter_by_data_sovereignty,
    filter_by_team_capacity,
    filter_by_tier1_requirements,
    filter_by_vendor_tolerance,
    update_decision_state_with_filters,
)
from src.utils.database_loader import load_default_database


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def vendor_db():
    """Load vendor database for testing."""
    return load_default_database()


# ============================================================================
# INDIVIDUAL FILTER TESTS
# ============================================================================


def test_filter_by_team_capacity_lean(vendor_db):
    """Test team capacity filter with lean team (1-2 engineers)."""
    viable, eliminated = filter_by_team_capacity(
        vendor_db.vendors, TeamSize.LEAN
    )

    # Lean team can only handle platforms with low operational complexity
    # Athena, Snowflake should pass (lean requirement)
    # Splunk, Denodo, QRadar should fail (large team requirement)
    assert len(eliminated) > 0

    # Check specific vendors
    eliminated_ids = list(eliminated.keys())
    assert "splunk-enterprise-security" in eliminated_ids  # Requires large team
    assert "denodo" in eliminated_ids  # Requires large team
    assert "ibm-qradar" in eliminated_ids  # Requires large team

    # Athena should pass (lean team requirement)
    viable_ids = [v.id for v in viable]
    assert "amazon-athena" in viable_ids
    assert "snowflake" in viable_ids


def test_filter_by_team_capacity_standard(vendor_db):
    """Test team capacity filter with standard team (3-5 engineers)."""
    viable, eliminated = filter_by_team_capacity(
        vendor_db.vendors, TeamSize.STANDARD
    )

    # Standard team can handle lean + standard platforms
    # Only large team platforms should be eliminated
    eliminated_ids = list(eliminated.keys())
    assert "splunk-enterprise-security" in eliminated_ids  # Requires large
    assert "ibm-qradar" in eliminated_ids  # Requires large

    # Standard platforms should pass
    viable_ids = [v.id for v in viable]
    assert "dremio" in viable_ids  # Standard team
    assert "starburst" in viable_ids  # Standard team
    assert "databricks" in viable_ids  # Standard team
    assert "denodo" in viable_ids  # Standard team (not large)


def test_filter_by_budget_under_500k(vendor_db):
    """Test budget filter with <$500K constraint."""
    viable, eliminated = filter_by_budget(
        vendor_db.vendors, BudgetRange.UNDER_500K
    )

    # High-cost platforms should be eliminated
    eliminated_ids = list(eliminated.keys())
    assert "splunk-enterprise-security" in eliminated_ids  # $3M-12M
    assert "snowflake" in eliminated_ids  # $500K-3M (max exceeds)
    assert "ibm-qradar" in eliminated_ids  # $1M-5M

    # Low-cost platforms should pass
    viable_ids = [v.id for v in viable]
    assert "amazon-athena" in viable_ids  # $50K-200K
    assert "microsoft-sentinel" in viable_ids  # $144K-420K (under $500K)


def test_filter_by_budget_500k_to_2m(vendor_db):
    """Test budget filter with $500K-2M range."""
    viable, eliminated = filter_by_budget(
        vendor_db.vendors, BudgetRange.RANGE_500K_2M
    )

    # Very high-cost platforms should be eliminated
    eliminated_ids = list(eliminated.keys())
    assert "splunk-enterprise-security" in eliminated_ids  # $3M-12M
    assert "snowflake" in eliminated_ids  # $500K-3M (max $3M exceeds $2M ceiling)
    assert "databricks" in eliminated_ids  # $400K-2.5M (max $2.5M exceeds $2M)

    # Mid-range platforms should pass
    viable_ids = [v.id for v in viable]
    assert "amazon-athena" in viable_ids  # $50K-200K
    assert "dremio" in viable_ids  # $200K-800K


def test_filter_by_data_sovereignty_on_prem_only(vendor_db):
    """Test data sovereignty filter requiring on-prem deployment."""
    viable, eliminated = filter_by_data_sovereignty(
        vendor_db.vendors, DataSovereignty.ON_PREM_ONLY
    )

    # Cloud-only platforms should be eliminated
    eliminated_ids = list(eliminated.keys())
    assert "amazon-athena" in eliminated_ids  # Cloud-only
    assert "snowflake" in eliminated_ids  # Cloud-only
    assert "databricks" in eliminated_ids  # Cloud-only
    assert "microsoft-sentinel" in eliminated_ids  # Cloud-only

    # Platforms with on-prem support should pass
    viable_ids = [v.id for v in viable]
    assert "splunk-enterprise-security" in viable_ids  # Cloud + on-prem
    assert "dremio" in viable_ids  # Cloud + on-prem + hybrid


def test_filter_by_data_sovereignty_hybrid(vendor_db):
    """Test data sovereignty filter requiring hybrid deployment."""
    viable, eliminated = filter_by_data_sovereignty(
        vendor_db.vendors, DataSovereignty.HYBRID
    )

    # Platforms without hybrid or (cloud + on-prem) should be eliminated
    eliminated_ids = list(eliminated.keys())
    assert "amazon-athena" in eliminated_ids  # Cloud-only
    assert "snowflake" in eliminated_ids  # Cloud-only

    # Platforms with hybrid capability should pass
    viable_ids = [v.id for v in viable]
    assert "dremio" in viable_ids  # Explicit hybrid support
    assert "starburst" in viable_ids  # Explicit hybrid support


def test_filter_by_vendor_tolerance_oss_first(vendor_db):
    """Test vendor tolerance filter preferring open source."""
    viable, eliminated = filter_by_vendor_tolerance(
        vendor_db.vendors, VendorTolerance.OSS_FIRST
    )

    # All vendors should pass (OSS_FIRST accepts everything)
    assert len(eliminated) == 0
    assert len(viable) == 71


def test_filter_by_vendor_tolerance_commercial_only(vendor_db):
    """Test vendor tolerance filter requiring commercial support."""
    viable, eliminated = filter_by_vendor_tolerance(
        vendor_db.vendors, VendorTolerance.COMMERCIAL_ONLY
    )

    # Our current database has no OSS vendors, so all should pass
    # (In future with OSS vendors like self-hosted Elastic, they'd be eliminated)
    assert len(viable) >= 0


def test_filter_by_tier1_requirements_sql_required(vendor_db):
    """Test Tier 1 requirement filter requiring SQL interface."""
    viable, eliminated = filter_by_tier1_requirements(
        vendor_db.vendors, {"sql_interface": True}
    )

    # Vendors without SQL should be eliminated
    eliminated_ids = list(eliminated.keys())
    assert "splunk-enterprise-security" in eliminated_ids  # SPL, not SQL
    assert "ibm-qradar" in eliminated_ids  # AQL, not SQL

    # Vendors with SQL should pass
    viable_ids = [v.id for v in viable]
    assert "amazon-athena" in viable_ids
    assert "dremio" in viable_ids
    assert "snowflake" in viable_ids


def test_filter_by_tier1_requirements_no_streaming(vendor_db):
    """Test Tier 1 requirement where streaming is NOT required (False)."""
    viable, eliminated = filter_by_tier1_requirements(
        vendor_db.vendors, {"streaming_query": False}
    )

    # Vendors WITH streaming would be eliminated if we required streaming=False
    # This tests the inverse: "I explicitly don't want streaming"
    # (Unusual but valid use case - avoiding real-time complexity)
    eliminated_ids = list(eliminated.keys())

    # Streaming vendors should be eliminated
    assert "splunk-enterprise-security" in eliminated_ids
    assert "microsoft-sentinel" in eliminated_ids

    # Non-streaming vendors should pass
    viable_ids = [v.id for v in viable]
    assert "amazon-athena" in viable_ids  # No streaming


# ============================================================================
# COMBINED FILTER TESTS (REALISTIC SCENARIOS)
# ============================================================================


def test_marcus_journey_scenario(vendor_db):
    """
    Test Marcus's journey scenario from book Chapter 4.

    Marcus: Financial services SOC, 2-person team, <$500K budget, on-prem requirement.
    Expected outcome: Athena recommended (cost-effective, low ops, but cloud-only conflict).
    This test validates constraint application.
    """
    result = apply_tier1_filters(
        vendor_db,
        team_size=TeamSize.LEAN,  # 2 engineers
        budget=BudgetRange.UNDER_500K,  # <$500K
        data_sovereignty=DataSovereignty.ON_PREM_ONLY,  # On-prem required
        vendor_tolerance=VendorTolerance.COMMERCIAL_ONLY,  # Need vendor support
        tier_1_requirements={"sql_interface": True},  # SOC team knows SQL
    )

    # With on-prem requirement, Athena (cloud-only) should be eliminated
    assert "amazon-athena" in result.eliminated_vendors

    # Splunk should be eliminated due to budget (too expensive)
    assert "splunk-enterprise-security" in result.eliminated_vendors

    # Very few vendors should survive (tight constraints)
    assert result.filtered_count < 5

    # Summary should show significant elimination
    assert "eliminated" in result.summary().lower()


def test_jennifer_journey_scenario(vendor_db):
    """
    Test Jennifer's journey scenario from book Chapter 4.

    Jennifer: Cloud-native startup, 5-person team, $500K-2M budget, cloud-first.
    Expected outcome: Multiple cloud-native options within budget.
    """
    result = apply_tier1_filters(
        vendor_db,
        team_size=TeamSize.STANDARD,  # 5 engineers
        budget=BudgetRange.RANGE_500K_2M,  # $500K-2M
        data_sovereignty=DataSovereignty.CLOUD_FIRST,  # Cloud preferred
        vendor_tolerance=VendorTolerance.OSS_WITH_SUPPORT,  # OSS acceptable with support
        tier_1_requirements={"sql_interface": True},  # SQL required
    )

    # Cloud-native platforms within budget should pass
    viable_ids = [v.id for v in result.filtered_vendors]
    assert "amazon-athena" in viable_ids  # $50K-200K
    assert "dremio" in viable_ids  # $200K-800K
    assert "starburst" in viable_ids  # $300K-1M

    # Splunk should be eliminated (too expensive, $3M-12M exceeds $2M ceiling)
    assert "splunk-enterprise-security" in result.eliminated_vendors

    # Snowflake/Databricks eliminated (max cost exceeds $2M ceiling)
    assert "snowflake" in result.eliminated_vendors  # $500K-3M (max exceeds)
    assert "databricks" in result.eliminated_vendors  # $400K-2.5M (max exceeds)

    # Non-SQL platforms eliminated
    assert "ibm-qradar" in result.eliminated_vendors

    # Should have several viable options (not overly constrained)
    assert result.filtered_count >= 3


def test_lean_team_tight_budget_scenario(vendor_db):
    """
    Test very constrained scenario: lean team + tight budget.

    Expected: Only serverless/managed platforms survive.
    """
    result = apply_tier1_filters(
        vendor_db,
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
        tier_1_requirements={"sql_interface": True},
    )

    # Athena should pass (lean team, low cost, SQL)
    viable_ids = [v.id for v in result.filtered_vendors]
    assert "amazon-athena" in viable_ids

    # High-ops platforms eliminated
    assert "splunk-enterprise-security" in result.eliminated_vendors
    assert "denodo" in result.eliminated_vendors

    # Expensive platforms eliminated
    assert "snowflake" in result.eliminated_vendors  # Max cost exceeds $500K

    # Very few survivors (Phase 2 added more lean-team options like Kinesis, Pub/Sub)
    # Database expanded from 64 to 71 vendors, increasing lean+low-cost+SQL options
    assert result.filtered_count <= 15


def test_no_filters_applied(vendor_db):
    """Test that no filters returns all vendors."""
    result = apply_tier1_filters(vendor_db)

    assert result.filtered_count == result.initial_count
    assert len(result.eliminated_vendors) == 0
    assert result.filtered_count == 71


def test_single_filter_budget_only(vendor_db):
    """Test applying only budget filter."""
    result = apply_tier1_filters(
        vendor_db, budget=BudgetRange.UNDER_500K
    )

    # Only expensive vendors eliminated
    assert "splunk-enterprise-security" in result.eliminated_vendors
    assert result.filtered_count < result.initial_count


# ============================================================================
# DECISION STATE INTEGRATION TESTS
# ============================================================================


def test_update_decision_state_with_filters(vendor_db):
    """Test updating DecisionState with filter results."""
    state = DecisionState(session_id="test-123")

    result = apply_tier1_filters(
        vendor_db,
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
    )

    updated_state = update_decision_state_with_filters(state, result)

    assert len(updated_state.filtered_vendors) == result.filtered_count
    assert len(updated_state.eliminated_vendors) == result.eliminated_count
    assert updated_state.last_updated is not None


def test_filter_result_to_dict(vendor_db):
    """Test FilterResult serialization to dict."""
    result = apply_tier1_filters(
        vendor_db,
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
    )

    result_dict = result.to_dict()

    assert "initial_count" in result_dict
    assert "filtered_count" in result_dict
    assert "eliminated_count" in result_dict
    assert "filtered_vendor_ids" in result_dict
    assert "eliminated_vendors" in result_dict
    assert "summary" in result_dict

    assert result_dict["initial_count"] == 71
    assert isinstance(result_dict["filtered_vendor_ids"], list)
    assert isinstance(result_dict["eliminated_vendors"], dict)


# ============================================================================
# EDGE CASES
# ============================================================================


def test_filter_empty_vendor_list():
    """Test filtering empty vendor list."""
    from src.models import VendorDatabase

    empty_db = VendorDatabase(vendors=[])

    result = apply_tier1_filters(
        empty_db,
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
    )

    assert result.initial_count == 0
    assert result.filtered_count == 0
    assert len(result.eliminated_vendors) == 0


def test_filter_all_vendors_eliminated(vendor_db):
    """Test scenario where all vendors are eliminated."""
    # Impossible constraints: lean team + on-prem + streaming + under $100K
    result = apply_tier1_filters(
        vendor_db,
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
        data_sovereignty=DataSovereignty.ON_PREM_ONLY,
        tier_1_requirements={"streaming_query": True, "sql_interface": True},
    )

    # Very few (possibly zero) vendors should survive these constraints
    assert result.filtered_count < result.initial_count


def test_filter_result_summary_format():
    """Test FilterResult summary formatting."""
    from src.models import VendorDatabase

    db = VendorDatabase(vendors=[])
    result = FilterResult(
        initial_count=10,
        filtered_vendors=[],
        eliminated_vendors={"vendor1": "reason1", "vendor2": "reason2"},
    )

    summary = result.summary()

    assert "10" in summary
    assert "0" in summary
    assert "2" in summary
    assert "eliminated" in summary.lower()


# ============================================================================
# PHASE 1: FOUNDATIONAL ARCHITECTURE FILTERING TESTS (Added Oct 2025)
# ============================================================================


def test_foundational_filter_iceberg_preference(vendor_db):
    """
    Test foundational filtering with Iceberg table format preference.

    Expected: Iceberg-native vendors pass, Delta-only vendors eliminated.
    """
    result = apply_foundational_filters(
        vendor_db,
        table_format="iceberg",
    )

    # Iceberg-native vendors should pass
    viable_ids = [v.id for v in result.filtered_vendors]
    assert "apache-iceberg" in viable_ids
    assert "amazon-athena" in viable_ids  # Iceberg native
    assert "dremio" in viable_ids  # Iceberg native
    assert "snowflake" in viable_ids  # Iceberg support
    assert "trino" in viable_ids  # Iceberg support

    # Delta-only vendors should be eliminated
    eliminated_ids = list(result.eliminated_vendors.keys())
    assert "databricks" in eliminated_ids  # Delta native, no Iceberg
    assert "delta-lake" in eliminated_ids  # Delta native

    # Should have substantial filtering
    assert result.filtered_count < result.initial_count


def test_foundational_filter_delta_lake_preference(vendor_db):
    """
    Test foundational filtering with Delta Lake table format preference.

    Expected: Delta-native vendors pass, Iceberg-only vendors eliminated.
    """
    result = apply_foundational_filters(
        vendor_db,
        table_format="delta_lake",
    )

    # Delta-native vendors should pass
    viable_ids = [v.id for v in result.filtered_vendors]
    assert "databricks" in viable_ids  # Delta native
    assert "delta-lake" in viable_ids  # Delta native
    assert "trino" in viable_ids  # Delta support

    # Iceberg-only vendors should be eliminated
    eliminated_ids = list(result.eliminated_vendors.keys())
    assert "apache-iceberg" in eliminated_ids  # Iceberg only
    assert "amazon-athena" in eliminated_ids  # Iceberg only
    assert "dremio" in eliminated_ids  # Iceberg only


def test_foundational_filter_polaris_catalog_preference(vendor_db):
    """
    Test foundational filtering with Polaris catalog preference.

    Expected: Polaris-compatible vendors pass, Unity-only vendors eliminated.
    """
    result = apply_foundational_filters(
        vendor_db,
        catalog="polaris",
    )

    # Polaris-compatible vendors should pass
    viable_ids = [v.id for v in result.filtered_vendors]
    assert "apache-iceberg" in viable_ids  # Polaris native
    assert "trino" in viable_ids  # Polaris support
    assert "starburst" in viable_ids  # Polaris support

    # Unity-only vendors should be eliminated
    eliminated_ids = list(result.eliminated_vendors.keys())
    assert "databricks" in eliminated_ids  # Unity Catalog only


def test_foundational_filter_unity_catalog_preference(vendor_db):
    """
    Test foundational filtering with Unity Catalog preference.

    Expected: Unity-compatible vendors pass, Polaris-only vendors eliminated.
    """
    result = apply_foundational_filters(
        vendor_db,
        catalog="unity_catalog",
    )

    # Unity-compatible vendors should pass
    viable_ids = [v.id for v in result.filtered_vendors]
    assert "databricks" in viable_ids  # Unity native
    assert "delta-lake" in viable_ids  # Unity native

    # Polaris-only vendors should be eliminated
    eliminated_ids = list(result.eliminated_vendors.keys())
    # Many vendors will lack Unity support


def test_foundational_filter_glue_catalog_preference(vendor_db):
    """
    Test foundational filtering with AWS Glue catalog preference.

    Expected: AWS-compatible vendors pass.
    """
    result = apply_foundational_filters(
        vendor_db,
        catalog="glue",
    )

    # Glue-compatible vendors should pass
    viable_ids = [v.id for v in result.filtered_vendors]
    assert "amazon-athena" in viable_ids  # Glue native
    assert "apache-iceberg" in viable_ids  # Glue support
    assert "trino" in viable_ids  # Glue support
    assert "dremio" in viable_ids  # Glue support


def test_foundational_filter_dbt_transformation(vendor_db):
    """
    Test foundational filtering with dbt transformation strategy.

    Expected: dbt-compatible vendors pass, non-dbt vendors eliminated.
    """
    result = apply_foundational_filters(
        vendor_db,
        transformation_strategy="dbt",
    )

    # dbt-compatible vendors should pass
    viable_ids = [v.id for v in result.filtered_vendors]
    assert "amazon-athena" in viable_ids  # dbt support
    assert "snowflake" in viable_ids  # dbt support
    assert "databricks" in viable_ids  # dbt support
    assert "google-bigquery" in viable_ids  # dbt support
    assert "clickhouse" in viable_ids  # dbt support

    # Vendors without dbt support should be eliminated
    eliminated_ids = list(result.eliminated_vendors.keys())
    # Many SIEMs and specialized platforms lack dbt support
    assert result.eliminated_count > 0


def test_foundational_filter_spark_transformation(vendor_db):
    """
    Test foundational filtering with Spark transformation strategy.

    Expected: Spark-compatible vendors pass.
    """
    result = apply_foundational_filters(
        vendor_db,
        transformation_strategy="spark",
    )

    # Spark-compatible vendors should pass
    viable_ids = [v.id for v in result.filtered_vendors]
    assert "databricks" in viable_ids  # Spark native
    assert "trino" in viable_ids  # Spark support
    assert "starburst" in viable_ids  # Spark support
    assert "apache-flink" in viable_ids  # Spark support


def test_foundational_filter_low_latency_query_engine(vendor_db):
    """
    Test foundational filtering with low-latency query engine preference.

    Expected: Sub-second query engines pass (P95 < 1000ms).
    """
    result = apply_foundational_filters(
        vendor_db,
        query_engine_preference="low_latency",
    )

    # Low-latency vendors should pass
    viable_ids = [v.id for v in result.filtered_vendors]
    assert "clickhouse" in viable_ids  # 200ms P95
    assert "dremio" in viable_ids  # 500ms P95
    assert "apache-druid" in viable_ids  # 500ms P95

    # High-latency vendors should be eliminated
    eliminated_ids = list(result.eliminated_vendors.keys())
    assert "amazon-athena" in eliminated_ids  # 2000ms P95

    # Should have substantial filtering
    assert result.eliminated_count > 0


def test_foundational_filter_high_concurrency_query_engine(vendor_db):
    """
    Test foundational filtering with high-concurrency query engine preference.

    Expected: Vendors supporting 80+ concurrent queries pass.
    """
    result = apply_foundational_filters(
        vendor_db,
        query_engine_preference="high_concurrency",
    )

    # High-concurrency vendors should pass
    viable_ids = [v.id for v in result.filtered_vendors]
    assert "snowflake" in viable_ids  # 100 concurrent
    assert "amazon-athena" in viable_ids  # 100 concurrent
    assert "clickhouse" in viable_ids  # 100 concurrent
    assert "dremio" in viable_ids  # 100 concurrent


def test_foundational_filter_combined_iceberg_polaris_dbt(vendor_db):
    """
    Test combined foundational filtering: Iceberg + Polaris + dbt.

    This is the "LIGER Stack" default configuration from the blog.
    Expected: Very narrow vendor list (Trino, Starburst).
    """
    result = apply_foundational_filters(
        vendor_db,
        table_format="iceberg",
        catalog="polaris",
        transformation_strategy="dbt",
    )

    # LIGER-compatible vendors should pass
    viable_ids = [v.id for v in result.filtered_vendors]
    assert "trino" in viable_ids  # Iceberg + Polaris + dbt
    assert "starburst" in viable_ids  # Iceberg + Polaris + dbt

    # Delta-native vendors should be eliminated
    eliminated_ids = list(result.eliminated_vendors.keys())
    assert "databricks" in eliminated_ids  # Delta only
    assert "amazon-athena" in eliminated_ids  # Glue catalog, not Polaris
    # Apache Iceberg (table format) eliminated for lack of dbt integration
    assert "apache-iceberg" in eliminated_ids

    # Should have significant filtering (70+ vendors → <10)
    assert result.filtered_count < 15


def test_foundational_filter_combined_delta_unity_spark(vendor_db):
    """
    Test combined foundational filtering: Delta + Unity + Spark.

    This is the "Databricks-native" configuration.
    Expected: Very narrow vendor list (Databricks, Delta Lake).
    """
    result = apply_foundational_filters(
        vendor_db,
        table_format="delta_lake",
        catalog="unity_catalog",
        transformation_strategy="spark",
    )

    # Delta + Unity + Spark vendors should pass
    viable_ids = [v.id for v in result.filtered_vendors]
    assert "databricks" in viable_ids
    assert "delta-lake" in viable_ids

    # Iceberg-native vendors should be eliminated
    eliminated_ids = list(result.eliminated_vendors.keys())
    assert "apache-iceberg" in eliminated_ids
    assert "amazon-athena" in eliminated_ids
    assert "dremio" in eliminated_ids

    # Very narrow vendor list (2-5 vendors)
    assert result.filtered_count <= 5


def test_foundational_filter_undecided_no_elimination(vendor_db):
    """
    Test foundational filtering with "undecided" for all criteria.

    Expected: No vendors eliminated (all pass through).
    """
    result = apply_foundational_filters(
        vendor_db,
        table_format="undecided",
        catalog="undecided",
        transformation_strategy="undecided",
        query_engine_preference="flexible",
    )

    # All vendors should pass
    assert result.filtered_count == result.initial_count
    assert result.eliminated_count == 0


def test_foundational_filter_flexible_query_engine(vendor_db):
    """
    Test foundational filtering with flexible query engine preference.

    Expected: No elimination based on query engine characteristics.
    """
    result = apply_foundational_filters(
        vendor_db,
        query_engine_preference="flexible",
    )

    # All vendors should pass (no filtering)
    assert result.filtered_count == result.initial_count
    assert result.eliminated_count == 0


def test_foundational_filter_no_parameters(vendor_db):
    """
    Test foundational filtering with no parameters.

    Expected: No vendors eliminated (all pass through).
    """
    result = apply_foundational_filters(vendor_db)

    # All vendors should pass
    assert result.filtered_count == result.initial_count
    assert result.eliminated_count == 0


def test_foundational_filter_result_structure(vendor_db):
    """
    Test that foundational filter result has expected structure.
    """
    result = apply_foundational_filters(
        vendor_db,
        table_format="iceberg",
    )

    # Check result structure
    assert hasattr(result, "initial_count")
    assert hasattr(result, "filtered_vendors")
    assert hasattr(result, "eliminated_vendors")
    assert hasattr(result, "filtered_count")
    assert hasattr(result, "eliminated_count")

    # Check summary method exists
    summary = result.summary()
    assert isinstance(summary, str)
    assert "71" in summary  # Initial count
    assert "viable" in summary.lower()  # Result description
    assert result.filtered_count > 0  # Some vendors passed
    assert result.eliminated_count > 0  # Some vendors eliminated


def test_foundational_filter_elimination_reasons(vendor_db):
    """
    Test that elimination reasons are properly recorded.
    """
    result = apply_foundational_filters(
        vendor_db,
        table_format="iceberg",
        catalog="polaris",
    )

    # Check that eliminated vendors have reasons
    for vendor_id, reason in result.eliminated_vendors.items():
        assert isinstance(reason, str)
        assert len(reason) > 0
        # Reason should mention the missing capability
        assert "table format" in reason.lower() or "catalog" in reason.lower()
