"""
Tests for Tier 2 scoring logic.

Tests include realistic scenarios validating preference-based vendor ranking.
"""

import pytest

from src.tools.score_vendors import (
    ScoreResult,
    ScoredVendor,
    apply_combined_filtering_and_scoring,
    calculate_max_possible_score,
    score_vendor_on_preferences,
    score_vendors_tier2,
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
# SCORING CALCULATION TESTS
# ============================================================================


def test_calculate_max_possible_score():
    """Test max score calculation."""
    preferences = {
        "sql_interface": 3,
        "streaming_query": 2,
        "ocsf_support": 1,
    }

    max_score = calculate_max_possible_score(preferences)
    assert max_score == 6  # 3 + 2 + 1


def test_score_vendor_on_preferences_all_match(vendor_db):
    """Test scoring vendor that matches all preferences."""
    athena = vendor_db.get_by_id("amazon-athena")

    preferences = {
        "sql_interface": 3,  # Athena has SQL
        "cloud_native": 2,   # Athena is cloud-native
    }

    score, breakdown = score_vendor_on_preferences(athena, preferences)

    assert score == 5  # 3 + 2
    assert breakdown["sql_interface"] == 3
    assert breakdown["cloud_native"] == 2


def test_score_vendor_on_preferences_partial_match(vendor_db):
    """Test scoring vendor with partial preference match."""
    athena = vendor_db.get_by_id("amazon-athena")

    preferences = {
        "sql_interface": 3,      # Athena has SQL (3 points)
        "streaming_query": 2,    # Athena does NOT have streaming (0 points)
        "cloud_native": 1,       # Athena is cloud-native (1 point)
    }

    score, breakdown = score_vendor_on_preferences(athena, preferences)

    assert score == 4  # 3 + 0 + 1
    assert breakdown["sql_interface"] == 3
    assert breakdown["streaming_query"] == 0
    assert breakdown["cloud_native"] == 1


def test_score_vendor_on_preferences_open_table_format(vendor_db):
    """Test scoring open table format preference."""
    athena = vendor_db.get_by_id("amazon-athena")  # iceberg-native
    splunk = vendor_db.get_by_id("splunk-enterprise-security")  # proprietary

    preferences = {"open_table_format": 3}

    # Athena (iceberg-native) should get full points
    athena_score, athena_breakdown = score_vendor_on_preferences(athena, preferences)
    assert athena_score == 3
    assert athena_breakdown["open_table_format"] == 3

    # Splunk (proprietary) should get 0 points
    splunk_score, splunk_breakdown = score_vendor_on_preferences(splunk, preferences)
    assert splunk_score == 0
    assert splunk_breakdown["open_table_format"] == 0


def test_score_vendor_on_preferences_invalid_weight(vendor_db):
    """Test that invalid weight raises error."""
    athena = vendor_db.get_by_id("amazon-athena")

    preferences = {"sql_interface": 5}  # Invalid weight (must be 1-3)

    with pytest.raises(ValueError, match="Weight must be 1-3"):
        score_vendor_on_preferences(athena, preferences)


# ============================================================================
# VENDOR SCORING TESTS
# ============================================================================


def test_score_vendors_tier2_basic(vendor_db):
    """Test basic Tier 2 scoring."""
    vendors = [
        vendor_db.get_by_id("amazon-athena"),
        vendor_db.get_by_id("splunk-enterprise-security"),
    ]

    preferences = {
        "sql_interface": 3,
        "cloud_native": 2,
    }

    result = score_vendors_tier2(vendors, preferences)

    assert isinstance(result, ScoreResult)
    assert result.vendor_count == 2
    assert result.max_possible_score == 5

    # Athena should score higher (has SQL + cloud-native)
    # Splunk should score lower (no SQL, not cloud-native)
    top_vendor = result.scored_vendors[0]
    assert top_vendor.vendor.id == "amazon-athena"


def test_score_vendors_tier2_ranking(vendor_db):
    """Test that vendors are ranked by score."""
    vendors = vendor_db.vendors

    preferences = {
        "sql_interface": 3,
        "open_table_format": 3,
        "cloud_native": 2,
    }

    result = score_vendors_tier2(vendors, preferences)

    # Scores should be descending
    scores = [sv.score for sv in result.scored_vendors]
    assert scores == sorted(scores, reverse=True)

    # Top vendors should have high scores
    top_3 = result.get_top_n(3)
    assert len(top_3) == 3
    assert all(sv.score > 0 for sv in top_3)


def test_score_vendors_tier2_empty_preferences():
    """Test that empty preferences raises error."""
    with pytest.raises(ValueError, match="Preferences cannot be empty"):
        score_vendors_tier2([], {})


def test_scored_vendor_percentage(vendor_db):
    """Test score percentage calculation."""
    athena = vendor_db.get_by_id("amazon-athena")

    preferences = {
        "sql_interface": 3,
        "streaming_query": 2,  # Athena doesn't have this
    }

    score, breakdown = score_vendor_on_preferences(athena, preferences)
    scored = ScoredVendor(athena, score, 5, breakdown)

    # Athena gets 3/5 = 60%
    assert scored.score_percentage == 60.0


# ============================================================================
# SCORE RESULT TESTS
# ============================================================================


def test_score_result_get_top_n(vendor_db):
    """Test getting top N vendors."""
    vendors = vendor_db.vendors

    preferences = {"sql_interface": 3, "cloud_native": 2}

    result = score_vendors_tier2(vendors, preferences)

    top_3 = result.get_top_n(3)
    assert len(top_3) == 3

    top_10 = result.get_top_n(10)
    assert len(top_10) == 10  # Top 10 from 24 vendors returned


def test_score_result_get_finalists(vendor_db):
    """Test getting finalists by minimum score threshold."""
    vendors = vendor_db.vendors

    preferences = {
        "sql_interface": 3,
        "cloud_native": 2,
        "open_table_format": 3,
    }

    result = score_vendors_tier2(vendors, preferences)

    # Get finalists with at least 50% score
    finalists = result.get_finalists(min_score_percentage=50.0)

    assert len(finalists) > 0
    assert all(f.score_percentage >= 50.0 for f in finalists)


def test_score_result_to_dict(vendor_db):
    """Test ScoreResult serialization."""
    vendors = [vendor_db.get_by_id("amazon-athena")]
    preferences = {"sql_interface": 3}

    result = score_vendors_tier2(vendors, preferences)
    result_dict = result.to_dict()

    assert "vendor_count" in result_dict
    assert "max_possible_score" in result_dict
    assert "preferences" in result_dict
    assert "scored_vendors" in result_dict
    assert "summary" in result_dict

    assert result_dict["vendor_count"] == 1
    assert result_dict["max_possible_score"] == 3
    assert len(result_dict["scored_vendors"]) == 1


def test_score_result_summary(vendor_db):
    """Test ScoreResult summary formatting."""
    vendors = [vendor_db.get_by_id("amazon-athena")]
    preferences = {"sql_interface": 3}

    result = score_vendors_tier2(vendors, preferences)
    summary = result.summary()

    assert "1 vendors scored" in summary
    assert "Amazon Athena" in summary
    assert "3/3" in summary or "100.0%" in summary


# ============================================================================
# REALISTIC SCENARIOS
# ============================================================================


def test_cloud_native_lakehouse_preferences(vendor_db):
    """
    Test scoring for cloud-native lakehouse preferences.

    Scenario: Architect wants SQL, open format, cloud-native, multi-cloud.
    Expected: Athena, Snowflake, Databricks score high.
    """
    vendors = vendor_db.vendors

    preferences = {
        "sql_interface": 3,
        "open_table_format": 3,
        "cloud_native": 2,
        "multi_cloud": 2,
    }

    result = score_vendors_tier2(vendors, preferences)

    top_5 = result.get_top_n(5)
    top_ids = [sv.vendor.id for sv in top_5]

    # Cloud-native platforms with open formats should rank high
    assert "amazon-athena" in top_ids or "databricks" in top_ids or "starburst" in top_ids


def test_real_time_siem_preferences(vendor_db):
    """
    Test scoring for real-time SIEM preferences.

    Scenario: Architect wants streaming, ML analytics, SIEM integration.
    Expected: Splunk, Elastic, Sentinel score high.
    """
    vendors = vendor_db.vendors

    preferences = {
        "streaming_query": 3,
        "ml_analytics": 2,
        "siem_integration": 2,
    }

    result = score_vendors_tier2(vendors, preferences)

    top_5 = result.get_top_n(5)
    top_ids = [sv.vendor.id for sv in top_5]

    # SIEM platforms with streaming should rank high
    # (Though Splunk/QRadar lack SQL, they have streaming)
    assert any(vendor_id in top_ids for vendor_id in [
        "splunk-enterprise-security",
        "elastic-security",
        "microsoft-sentinel"
    ])


def test_cost_conscious_open_source_preferences(vendor_db):
    """
    Test scoring for cost-conscious, open-format preferences.

    Scenario: Architect wants SQL, open format, low operational complexity.
    Expected: Athena ranks highest (serverless, Iceberg, low-ops).
    """
    vendors = vendor_db.vendors

    preferences = {
        "sql_interface": 3,
        "open_table_format": 3,
        "managed_service_available": 2,
    }

    result = score_vendors_tier2(vendors, preferences)

    top_vendor = result.scored_vendors[0]

    # Athena should rank very high (SQL + iceberg-native + managed)
    assert top_vendor.vendor.id in ["amazon-athena", "snowflake", "starburst"]
    assert top_vendor.score >= 6  # At least 6/8 points


# ============================================================================
# COMBINED FILTERING + SCORING TESTS
# ============================================================================


def test_apply_combined_filtering_and_scoring(vendor_db):
    """Test combined Tier 1 filtering + Tier 2 scoring."""
    from src.models import BudgetRange, TeamSize

    filter_result, score_result = apply_combined_filtering_and_scoring(
        vendor_db,
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
        tier_1_requirements={"sql_interface": True},
        tier_2_preferences={
            "open_table_format": 3,
            "cloud_native": 2,
        }
    )

    # Tier 1 should eliminate expensive vendors
    assert filter_result.filtered_count < filter_result.initial_count

    # Tier 2 should rank remaining vendors
    assert score_result is not None
    assert score_result.vendor_count == filter_result.filtered_count

    # Top vendor should be Athena (lean, cheap, SQL, open format, cloud)
    top_vendor = score_result.scored_vendors[0]
    assert top_vendor.vendor.id == "amazon-athena"


def test_combined_no_tier2_preferences(vendor_db):
    """Test combined operation without Tier 2 preferences."""
    from src.models import BudgetRange

    filter_result, score_result = apply_combined_filtering_and_scoring(
        vendor_db,
        budget=BudgetRange.UNDER_500K,
    )

    assert filter_result is not None
    assert score_result is None  # No scoring without preferences


def test_combined_all_vendors_eliminated(vendor_db):
    """Test combined operation when all vendors eliminated."""
    from src.models import BudgetRange, DataSovereignty, TeamSize

    filter_result, score_result = apply_combined_filtering_and_scoring(
        vendor_db,
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
        data_sovereignty=DataSovereignty.ON_PREM_ONLY,  # Conflicts with cheap cloud
        tier_1_requirements={"streaming_query": True},  # Further restrict
        tier_2_preferences={"sql_interface": 3}
    )

    # Very few (possibly zero) vendors survive
    assert filter_result.filtered_count < filter_result.initial_count

    # If no vendors, no scoring
    if filter_result.filtered_count == 0:
        assert score_result is None
