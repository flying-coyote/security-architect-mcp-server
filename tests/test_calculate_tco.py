"""
Tests for TCO (Total Cost of Ownership) calculator.

Validates cost projections, growth calculations, and hidden cost estimates.
"""

import pytest

from src.models import BudgetRange, CostModel, TeamSize
from src.tools.calculate_tco import (
    calculate_hidden_costs,
    calculate_operational_cost,
    calculate_tco,
    compare_vendors_tco,
    estimate_cost_from_model,
    get_team_fte,
    parse_cost_range,
)
from src.utils.database_loader import load_default_database


@pytest.fixture
def vendor_db():
    """Load vendor database for testing."""
    return load_default_database()


# ============================================================================
# COST PARSING TESTS
# ============================================================================


def test_parse_cost_range_k_format():
    """Test parsing cost ranges with K suffix."""
    min_cost, max_cost = parse_cost_range("$50K-200K/year")

    assert min_cost == 50000
    assert max_cost == 200000


def test_parse_cost_range_m_format():
    """Test parsing cost ranges with M suffix."""
    min_cost, max_cost = parse_cost_range("$3M-12M/year")

    assert min_cost == 3000000
    assert max_cost == 12000000


def test_parse_cost_range_mixed_format():
    """Test parsing cost ranges with mixed K/M suffixes."""
    min_cost, max_cost = parse_cost_range("$500K-2M/year")

    assert min_cost == 500000
    assert max_cost == 2000000


def test_parse_cost_range_invalid():
    """Test parsing invalid cost range returns zeros."""
    min_cost, max_cost = parse_cost_range("invalid")

    assert min_cost == 0
    assert max_cost == 0


def test_parse_cost_range_empty():
    """Test parsing empty cost range."""
    min_cost, max_cost = parse_cost_range("")

    assert min_cost == 0
    assert max_cost == 0


# ============================================================================
# OPERATIONAL COST TESTS
# ============================================================================


def test_calculate_operational_cost_low_complexity(vendor_db):
    """Test operational cost for low complexity vendor."""
    athena = vendor_db.get_by_id("amazon-athena")  # Low complexity

    ops_cost = calculate_operational_cost(athena, TeamSize.LEAN)

    # Low complexity = 0.25 FTE * $150K/year = $37,500
    assert 30000 < ops_cost < 50000


def test_calculate_operational_cost_high_complexity(vendor_db):
    """Test operational cost for high complexity vendor."""
    splunk = vendor_db.get_by_id("splunk-enterprise-security")  # High complexity

    ops_cost = calculate_operational_cost(splunk, TeamSize.LARGE)

    # High complexity = 1.0 FTE * $150K/year = $150,000
    assert 140000 < ops_cost < 160000


def test_get_team_fte():
    """Test FTE mapping for team sizes."""
    assert get_team_fte(TeamSize.LEAN) == 1.5
    assert get_team_fte(TeamSize.STANDARD) == 4.0
    assert get_team_fte(TeamSize.LARGE) == 8.0


# ============================================================================
# HIDDEN COST TESTS
# ============================================================================


def test_calculate_hidden_costs_year1(vendor_db):
    """Test hidden costs for Year 1 (includes migration)."""
    athena = vendor_db.get_by_id("amazon-athena")
    platform_cost = 100000

    hidden = calculate_hidden_costs(athena, platform_cost, year=1)

    # Egress (15%) + Support (12%) + Migration ($50K) = $77K
    assert 70000 < hidden < 85000


def test_calculate_hidden_costs_year2(vendor_db):
    """Test hidden costs for Year 2+ (no migration)."""
    athena = vendor_db.get_by_id("amazon-athena")
    platform_cost = 100000

    hidden = calculate_hidden_costs(athena, platform_cost, year=2)

    # Egress (15%) + Support (12%) = $27K (no migration)
    assert 25000 < hidden < 30000


# ============================================================================
# COST ESTIMATION TESTS
# ============================================================================


def test_estimate_cost_from_model_per_gb():
    """Test cost estimation for per-GB model."""
    from src.models import Vendor, VendorCapabilities, VendorCategory

    vendor = Vendor(
        id="test-vendor",
        name="Test Vendor",
        category=VendorCategory.SIEM,
        description="Test vendor",
        capabilities=VendorCapabilities(
            sql_interface=False,
            streaming_query=True,
            open_table_format="proprietary",
            deployment_models=["cloud"],
            cloud_native=True,
            operational_complexity="medium",
            team_size_required=TeamSize.STANDARD,
            cost_model=CostModel.PER_GB,
            cost_predictability="low",
            maturity="production",
        ),
        evidence_source="test",
    )

    cost = estimate_cost_from_model(vendor, data_volume_tb_day=1.0)

    # 1 TB/day = 30 TB/month * $175/TB * 12 months = $63K
    assert 60000 < cost < 70000


def test_estimate_cost_from_model_consumption():
    """Test cost estimation for consumption model."""
    from src.models import Vendor, VendorCapabilities, VendorCategory

    vendor = Vendor(
        id="test-vendor",
        name="Test Vendor",
        category=VendorCategory.QUERY_ENGINE,
        description="Test vendor",
        capabilities=VendorCapabilities(
            sql_interface=True,
            open_table_format="iceberg-native",
            deployment_models=["cloud"],
            cloud_native=True,
            operational_complexity="low",
            team_size_required=TeamSize.LEAN,
            cost_model=CostModel.CONSUMPTION,
            cost_predictability="high",
            maturity="production",
        ),
        evidence_source="test",
    )

    cost = estimate_cost_from_model(vendor, data_volume_tb_day=1.0)

    # 1 TB/day = 30 TB/month * $75/TB * 12 months = $27K
    assert 25000 < cost < 30000


# ============================================================================
# TCO CALCULATION TESTS
# ============================================================================


def test_calculate_tco_basic(vendor_db):
    """Test basic TCO calculation."""
    athena = vendor_db.get_by_id("amazon-athena")

    tco = calculate_tco(
        vendor=athena,
        data_volume_tb_day=1.0,
        team_size=TeamSize.LEAN,
        growth_rate=0.20,
    )

    # Basic assertions
    assert tco.vendor == athena
    assert tco.year1_cost > 0
    assert tco.year5_total > tco.year1_cost
    assert len(tco.annual_costs) == 5
    assert len(tco.assumptions) > 0


def test_calculate_tco_growth(vendor_db):
    """Test that costs grow with data volume."""
    splunk = vendor_db.get_by_id("splunk-enterprise-security")  # Per-GB pricing

    tco = calculate_tco(
        vendor=splunk,
        data_volume_tb_day=1.0,
        team_size=TeamSize.STANDARD,
        growth_rate=0.20,  # 20% annual growth
    )

    # Costs should increase each year for per-GB models
    for i in range(4):
        assert tco.annual_costs[i + 1] > tco.annual_costs[i]


def test_calculate_tco_subscription_flat(vendor_db):
    """Test that subscription models don't scale with data volume."""
    dremio = vendor_db.get_by_id("dremio")  # Subscription pricing

    tco = calculate_tco(
        vendor=dremio,
        data_volume_tb_day=1.0,
        team_size=TeamSize.STANDARD,
        growth_rate=0.20,
    )

    # Subscription costs should be relatively flat (small ops cost growth only)
    year1 = tco.annual_costs[0]
    year5 = tco.annual_costs[4]

    # Year 5 should be within 20% of Year 1 (ops costs may grow slightly)
    assert year5 < year1 * 1.2


def test_calculate_tco_warnings(vendor_db):
    """Test that warnings are generated appropriately."""
    splunk = vendor_db.get_by_id("splunk-enterprise-security")

    tco = calculate_tco(
        vendor=splunk,
        data_volume_tb_day=1.0,
        team_size=TeamSize.LARGE,
    )

    # Splunk should have warnings (per-GB pricing, low predictability, high complexity)
    assert len(tco.warnings) > 0
    assert any("Per-GB" in w for w in tco.warnings)


def test_calculate_tco_assumptions(vendor_db):
    """Test that assumptions are documented."""
    athena = vendor_db.get_by_id("amazon-athena")

    tco = calculate_tco(
        vendor=athena,
        data_volume_tb_day=2.5,
        team_size=TeamSize.LEAN,
        growth_rate=0.15,
    )

    # Check assumptions are documented
    assumptions_text = " ".join(tco.assumptions)
    assert "2.5 TB/day" in assumptions_text
    assert "15%" in assumptions_text or "0.15" in assumptions_text
    assert "lean" in assumptions_text.lower()


# ============================================================================
# SERIALIZATION TESTS
# ============================================================================


def test_tco_to_dict(vendor_db):
    """Test TCO serialization to dictionary."""
    athena = vendor_db.get_by_id("amazon-athena")

    tco = calculate_tco(
        vendor=athena,
        data_volume_tb_day=1.0,
        team_size=TeamSize.LEAN,
    )

    tco_dict = tco.to_dict()

    assert "vendor_id" in tco_dict
    assert "vendor_name" in tco_dict
    assert "year1_cost" in tco_dict
    assert "year5_total" in tco_dict
    assert "annual_costs" in tco_dict
    assert "breakdown" in tco_dict
    assert "assumptions" in tco_dict
    assert "warnings" in tco_dict

    assert tco_dict["vendor_id"] == "amazon-athena"
    assert len(tco_dict["annual_costs"]) == 5


def test_tco_summary(vendor_db):
    """Test TCO summary generation."""
    athena = vendor_db.get_by_id("amazon-athena")

    tco = calculate_tco(
        vendor=athena,
        data_volume_tb_day=1.0,
        team_size=TeamSize.LEAN,
    )

    summary = tco.summary()

    assert "Amazon Athena" in summary
    assert "K" in summary or "M" in summary  # Has cost figures
    assert "5-year" in summary


# ============================================================================
# VENDOR COMPARISON TESTS
# ============================================================================


def test_compare_vendors_tco(vendor_db):
    """Test comparing TCO across multiple vendors."""
    vendors = [
        vendor_db.get_by_id("amazon-athena"),
        vendor_db.get_by_id("splunk-enterprise-security"),
        vendor_db.get_by_id("dremio"),
    ]

    tco_comparison = compare_vendors_tco(
        vendors=vendors,
        data_volume_tb_day=1.0,
        team_size=TeamSize.LEAN,
    )

    # Should return 3 TCO projections
    assert len(tco_comparison) == 3

    # Should be sorted by 5-year total cost (lowest first)
    for i in range(2):
        assert tco_comparison[i].year5_total <= tco_comparison[i + 1].year5_total


def test_compare_vendors_tco_athena_cheapest(vendor_db):
    """Test that Athena is typically cheapest for lean teams."""
    vendors = [
        vendor_db.get_by_id("amazon-athena"),
        vendor_db.get_by_id("splunk-enterprise-security"),
        vendor_db.get_by_id("snowflake"),
    ]

    tco_comparison = compare_vendors_tco(
        vendors=vendors,
        data_volume_tb_day=1.0,
        team_size=TeamSize.LEAN,
        growth_rate=0.20,
    )

    # Athena should be cheapest (low ops, consumption pricing)
    cheapest = tco_comparison[0]
    assert cheapest.vendor.id == "amazon-athena"


# ============================================================================
# REALISTIC SCENARIO TESTS
# ============================================================================


def test_tco_jennifer_scenario(vendor_db):
    """Test TCO for Jennifer's cloud-native startup scenario."""
    athena = vendor_db.get_by_id("amazon-athena")

    tco = calculate_tco(
        vendor=athena,
        data_volume_tb_day=1.0,  # Small startup
        team_size=TeamSize.STANDARD,
        growth_rate=0.30,  # High growth startup
    )

    # Should be within Jennifer's $500K-2M budget for Year 1
    assert 100000 < tco.year1_cost < 600000


def test_tco_marcus_scenario(vendor_db):
    """Test TCO for Marcus's lean team scenario."""
    athena = vendor_db.get_by_id("amazon-athena")

    tco = calculate_tco(
        vendor=athena,
        data_volume_tb_day=0.5,  # Small regional bank
        team_size=TeamSize.LEAN,
        growth_rate=0.10,  # Conservative growth
    )

    # Should be within Marcus's <$500K budget for Year 1
    # Athena with consumption pricing scales down for low volumes
    assert tco.year1_cost < 500000


def test_tco_priya_enterprise_scenario(vendor_db):
    """Test TCO for Priya's enterprise scenario."""
    databricks = vendor_db.get_by_id("databricks")

    tco = calculate_tco(
        vendor=databricks,
        data_volume_tb_day=10.0,  # Enterprise scale
        team_size=TeamSize.LARGE,
        growth_rate=0.15,  # Moderate enterprise growth
    )

    # Enterprise should have high costs but within $2M-10M budget
    assert 1000000 < tco.year1_cost < 5000000


def test_tco_cost_predictability_warning(vendor_db):
    """Test that low predictability vendors generate warnings."""
    splunk = vendor_db.get_by_id("splunk-enterprise-security")

    tco = calculate_tco(
        vendor=splunk,
        data_volume_tb_day=1.0,
        team_size=TeamSize.STANDARD,
    )

    # Splunk has low cost predictability
    warnings_text = " ".join(tco.warnings)
    assert "predictability" in warnings_text.lower()


def test_tco_operational_complexity_warning(vendor_db):
    """Test that high complexity vendors generate warnings."""
    denodo = vendor_db.get_by_id("denodo")  # High complexity

    tco = calculate_tco(
        vendor=denodo,
        data_volume_tb_day=1.0,
        team_size=TeamSize.STANDARD,
    )

    # Denodo has high operational complexity
    warnings_text = " ".join(tco.warnings)
    assert "complexity" in warnings_text.lower()
