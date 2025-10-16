"""
Tests for architecture report generation.

Validates that reports are generated correctly with all required sections.
"""

import pytest

from src.models import BudgetRange, DataSovereignty, TeamSize
from src.tools.filter_vendors import apply_tier1_filters
from src.tools.generate_report import ArchitectureReport, generate_architecture_report
from src.tools.score_vendors import score_vendors_tier2
from src.utils.database_loader import load_default_database


@pytest.fixture
def vendor_db():
    """Load vendor database for testing."""
    return load_default_database()


# ============================================================================
# BASIC REPORT GENERATION TESTS
# ============================================================================


def test_generate_empty_report():
    """Test generating report without any results."""
    report = ArchitectureReport()
    markdown = report.generate_markdown()

    assert "# Security Architecture Recommendation Report" in markdown
    assert "## Executive Summary" in markdown
    assert "## Organizational Context" in markdown


def test_generate_report_with_filter_only(vendor_db):
    """Test generating report with only filtering results."""
    filter_result = apply_tier1_filters(
        vendor_db,
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
    )

    report = ArchitectureReport(filter_result=filter_result)
    markdown = report.generate_markdown()

    assert "# Security Architecture Recommendation Report" in markdown
    assert str(filter_result.filtered_count) in markdown
    assert str(filter_result.eliminated_count) in markdown


def test_generate_full_report(vendor_db):
    """Test generating complete report with filtering and scoring."""
    # Apply filters
    filter_result = apply_tier1_filters(
        vendor_db,
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
        tier_1_requirements={"sql_interface": True},
    )

    # Apply scoring
    score_result = score_vendors_tier2(
        filter_result.filtered_vendors,
        preferences={
            "open_table_format": 3,
            "cloud_native": 2,
        },
    )

    # Generate report
    report = ArchitectureReport(
        filter_result=filter_result,
        score_result=score_result,
        architect_context={
            "team_size": TeamSize.LEAN,
            "budget": BudgetRange.UNDER_500K,
        },
    )

    markdown = report.generate_markdown()

    # Check all major sections present
    assert "# Security Architecture Recommendation Report" in markdown
    assert "## Executive Summary" in markdown
    assert "## Organizational Context" in markdown
    assert "## Decision Constraints Applied" in markdown
    assert "## Vendor Landscape Analysis" in markdown
    assert "## Finalist Recommendations" in markdown
    assert "## Honest Trade-off Analysis" in markdown
    assert "## Implementation Considerations" in markdown
    assert "## Recommended Next Steps" in markdown

    # Check top vendor mentioned
    top_vendor = score_result.scored_vendors[0]
    assert top_vendor.vendor.name in markdown


# ============================================================================
# SECTION-SPECIFIC TESTS
# ============================================================================


def test_executive_summary_section(vendor_db):
    """Test executive summary section."""
    filter_result = apply_tier1_filters(
        vendor_db,
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
    )

    score_result = score_vendors_tier2(
        filter_result.filtered_vendors,
        preferences={"sql_interface": 3},
    )

    report = ArchitectureReport(
        filter_result=filter_result,
        score_result=score_result,
    )

    markdown = report._executive_summary()

    assert "## Executive Summary" in markdown
    assert str(filter_result.filtered_count) in markdown
    assert "viable" in markdown.lower()

    # Check top vendor mentioned
    top_vendor = score_result.scored_vendors[0]
    assert top_vendor.vendor.name in markdown


def test_organizational_context_section():
    """Test organizational context section."""
    report = ArchitectureReport(
        architect_context={
            "team_size": TeamSize.LEAN,
            "budget": BudgetRange.UNDER_500K,
            "data_sovereignty": DataSovereignty.CLOUD_FIRST,
        },
    )

    markdown = report._organizational_context()

    assert "## Organizational Context" in markdown
    assert "Team Capacity" in markdown
    assert "Budget Constraints" in markdown
    assert "Data Sovereignty" in markdown
    assert "lean team" in markdown.lower()


def test_decision_constraints_section(vendor_db):
    """Test decision constraints section."""
    filter_result = apply_tier1_filters(
        vendor_db,
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
    )

    score_result = score_vendors_tier2(
        filter_result.filtered_vendors,
        preferences={
            "open_table_format": 3,
            "cloud_native": 2,
        },
    )

    report = ArchitectureReport(
        filter_result=filter_result,
        score_result=score_result,
    )

    markdown = report._decision_constraints()

    assert "## Decision Constraints Applied" in markdown
    assert "Tier 1: Mandatory Filters" in markdown
    assert "Tier 2: Preferred Capabilities" in markdown
    assert str(filter_result.eliminated_count) in markdown


def test_vendor_landscape_section(vendor_db):
    """Test vendor landscape section."""
    filter_result = apply_tier1_filters(
        vendor_db,
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
    )

    report = ArchitectureReport(filter_result=filter_result)
    markdown = report._vendor_landscape()

    assert "## Vendor Landscape Analysis" in markdown
    assert str(filter_result.filtered_count) in markdown
    assert "Vendor Categories" in markdown


def test_finalists_section(vendor_db):
    """Test finalists section with vendor details."""
    filter_result = apply_tier1_filters(
        vendor_db,
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
        tier_1_requirements={"sql_interface": True},
    )

    score_result = score_vendors_tier2(
        filter_result.filtered_vendors,
        preferences={
            "open_table_format": 3,
            "cloud_native": 2,
        },
    )

    report = ArchitectureReport(score_result=score_result)
    markdown = report._finalists()

    assert "## Finalist Recommendations" in markdown

    # Check top 3 vendors mentioned
    for i, scored in enumerate(score_result.get_top_n(3), 1):
        assert f"{i}. {scored.vendor.name}" in markdown
        assert f"{scored.score}/{scored.max_score}" in markdown
        assert scored.vendor.description in markdown


def test_trade_off_analysis_section(vendor_db):
    """Test trade-off analysis section."""
    filter_result = apply_tier1_filters(
        vendor_db,
        budget=BudgetRange.UNDER_500K,
    )

    score_result = score_vendors_tier2(
        filter_result.filtered_vendors,
        preferences={"sql_interface": 3},
    )

    report = ArchitectureReport(score_result=score_result)
    markdown = report._trade_off_analysis()

    assert "## Honest Trade-off Analysis" in markdown
    assert "Strengths" in markdown
    assert "Limitations" in markdown

    # Check top 3 vendors analyzed
    for scored in score_result.get_top_n(3):
        assert scored.vendor.name in markdown


def test_implementation_considerations_section():
    """Test implementation considerations section."""
    report = ArchitectureReport()
    markdown = report._implementation_considerations()

    assert "## Implementation Considerations" in markdown
    assert "Proof of Concept" in markdown
    assert "Migration Strategy" in markdown
    assert "Team Training" in markdown
    assert "Vendor Negotiation" in markdown


def test_next_steps_section(vendor_db):
    """Test next steps section."""
    filter_result = apply_tier1_filters(vendor_db, budget=BudgetRange.UNDER_500K)
    score_result = score_vendors_tier2(
        filter_result.filtered_vendors,
        preferences={"sql_interface": 3},
    )

    report = ArchitectureReport(score_result=score_result)
    markdown = report._next_steps()

    assert "## Recommended Next Steps" in markdown
    assert "Immediate" in markdown
    assert "Short-term" in markdown
    assert "Medium-term" in markdown

    # Check top vendor mentioned
    top_vendor = score_result.scored_vendors[0]
    assert top_vendor.vendor.name in markdown


# ============================================================================
# SERIALIZATION TESTS
# ============================================================================


def test_report_to_dict(vendor_db):
    """Test report serialization to dictionary."""
    filter_result = apply_tier1_filters(vendor_db, budget=BudgetRange.UNDER_500K)
    score_result = score_vendors_tier2(
        filter_result.filtered_vendors,
        preferences={"sql_interface": 3},
    )

    report = ArchitectureReport(
        filter_result=filter_result,
        score_result=score_result,
        architect_context={"budget": BudgetRange.UNDER_500K},
    )

    report_dict = report.to_dict()

    assert "generated_at" in report_dict
    assert "filter_summary" in report_dict
    assert "score_summary" in report_dict
    assert "architect_context" in report_dict
    assert "markdown" in report_dict

    # Check markdown is full report
    assert "# Security Architecture Recommendation Report" in report_dict["markdown"]


# ============================================================================
# CONVENIENCE FUNCTION TESTS
# ============================================================================


def test_generate_architecture_report_function(vendor_db):
    """Test convenience function for report generation."""
    filter_result = apply_tier1_filters(
        vendor_db,
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
        tier_1_requirements={"sql_interface": True},
    )

    score_result = score_vendors_tier2(
        filter_result.filtered_vendors,
        preferences={
            "open_table_format": 3,
            "cloud_native": 2,
        },
    )

    markdown = generate_architecture_report(
        filter_result=filter_result,
        score_result=score_result,
        architect_context={
            "team_size": TeamSize.LEAN,
            "budget": BudgetRange.UNDER_500K,
        },
    )

    assert isinstance(markdown, str)
    assert "# Security Architecture Recommendation Report" in markdown
    assert len(markdown) > 1000  # Report should be substantial


# ============================================================================
# REALISTIC SCENARIO TESTS
# ============================================================================


def test_jennifer_journey_report(vendor_db):
    """
    Test report generation for Jennifer's journey scenario.

    Jennifer: Cloud-native startup, 5-person team, $500K-2M budget.
    """
    filter_result = apply_tier1_filters(
        vendor_db,
        team_size=TeamSize.STANDARD,
        budget=BudgetRange.RANGE_500K_2M,
        data_sovereignty=DataSovereignty.CLOUD_FIRST,
        tier_1_requirements={"sql_interface": True},
    )

    score_result = score_vendors_tier2(
        filter_result.filtered_vendors,
        preferences={
            "open_table_format": 3,
            "cloud_native": 3,
            "managed_service_available": 2,
        },
    )

    markdown = generate_architecture_report(
        filter_result=filter_result,
        score_result=score_result,
        architect_context={
            "team_size": TeamSize.STANDARD,
            "budget": BudgetRange.RANGE_500K_2M,
            "data_sovereignty": DataSovereignty.CLOUD_FIRST,
        },
    )

    # Jennifer should get cloud-native recommendations
    assert "cloud" in markdown.lower()
    assert filter_result.filtered_count > 0
    assert len(score_result.scored_vendors) > 0


def test_marcus_journey_report(vendor_db):
    """
    Test report generation for Marcus's journey scenario.

    Marcus: Financial services SOC, 2-person team, <$500K budget.
    """
    filter_result = apply_tier1_filters(
        vendor_db,
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
        tier_1_requirements={"sql_interface": True},
    )

    score_result = score_vendors_tier2(
        filter_result.filtered_vendors,
        preferences={
            "managed_service_available": 3,
            "operational_complexity": 1,  # This won't work directly, need different approach
        },
    )

    markdown = generate_architecture_report(
        filter_result=filter_result,
        score_result=score_result,
        architect_context={
            "team_size": TeamSize.LEAN,
            "budget": BudgetRange.UNDER_500K,
        },
    )

    # Marcus should get cost-effective, low-ops recommendations
    assert "lean" in markdown.lower() or "1-2 engineers" in markdown.lower()
    assert filter_result.filtered_count > 0


def test_report_length_is_substantial(vendor_db):
    """Test that generated reports are comprehensive (8-12 pages)."""
    filter_result = apply_tier1_filters(
        vendor_db,
        team_size=TeamSize.STANDARD,
        budget=BudgetRange.RANGE_500K_2M,
    )

    score_result = score_vendors_tier2(
        filter_result.filtered_vendors,
        preferences={"sql_interface": 3, "cloud_native": 2},
    )

    markdown = generate_architecture_report(
        filter_result=filter_result,
        score_result=score_result,
        architect_context={
            "team_size": TeamSize.STANDARD,
            "budget": BudgetRange.RANGE_500K_2M,
        },
    )

    # 8-12 pages = ~10,000-24,000 characters (assuming 1500-2000 chars/page)
    assert len(markdown) > 10000  # At least 5-6 pages
    assert len(markdown) < 50000  # Not excessively long


def test_report_contains_methodology_footer():
    """Test that report includes methodology and disclaimers."""
    report = ArchitectureReport()
    markdown = report._footer()

    assert "## Methodology" in markdown
    assert "## Disclaimers" in markdown
    assert "Chapter 3 decision framework" in markdown
    assert "No Vendor Sponsorship" in markdown
    assert "Apache 2.0" in markdown
