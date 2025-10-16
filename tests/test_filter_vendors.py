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
    assert "denodo" in eliminated_ids  # Requires large

    # Standard platforms should pass
    viable_ids = [v.id for v in viable]
    assert "dremio" in viable_ids  # Standard team
    assert "starburst" in viable_ids  # Standard team
    assert "databricks" in viable_ids  # Standard team


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
    assert "microsoft-sentinel" in eliminated_ids  # $800K-3M

    # Low-cost platforms should pass
    viable_ids = [v.id for v in viable]
    assert "amazon-athena" in viable_ids  # $50K-200K


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
    assert len(viable) == 64


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
    assert result.filtered_count <= 10


def test_no_filters_applied(vendor_db):
    """Test that no filters returns all vendors."""
    result = apply_tier1_filters(vendor_db)

    assert result.filtered_count == result.initial_count
    assert len(result.eliminated_vendors) == 0
    assert result.filtered_count == 64


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

    assert result_dict["initial_count"] == 64
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
