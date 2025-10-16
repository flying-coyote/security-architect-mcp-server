"""
Tests for journey persona matching.

Validates that architect contexts are correctly matched to Chapter 4 personas.
"""

import pytest

from src.models import BudgetRange, DataSovereignty, DecisionState, TeamSize, VendorTolerance
from src.tools.match_journey import (
    JENNIFER_PROFILE,
    MARCUS_PROFILE,
    PRIYA_PROFILE,
    calculate_match_score,
    get_journey_description,
    match_journey_persona,
)


# ============================================================================
# MATCH SCORE CALCULATION TESTS
# ============================================================================


def test_calculate_perfect_match():
    """Test perfect match score calculation."""
    architect_context = {
        "team_size": TeamSize.STANDARD,
        "budget": BudgetRange.RANGE_500K_2M,
        "data_sovereignty": DataSovereignty.CLOUD_FIRST,
        "vendor_tolerance": VendorTolerance.OSS_WITH_SUPPORT,
    }

    score, constraints = calculate_match_score(architect_context, JENNIFER_PROFILE)

    assert score == 100.0  # Perfect match
    assert len(constraints) == 4  # All 4 constraints match


def test_calculate_partial_match():
    """Test partial match with adjacent values."""
    architect_context = {
        "team_size": TeamSize.LEAN,  # Adjacent to STANDARD
        "budget": BudgetRange.UNDER_500K,  # Adjacent to 500K-2M
        "data_sovereignty": DataSovereignty.CLOUD_FIRST,  # Exact match
        "vendor_tolerance": VendorTolerance.OSS_FIRST,  # Adjacent to OSS_WITH_SUPPORT
    }

    score, constraints = calculate_match_score(architect_context, JENNIFER_PROFILE)

    # Partial credit: 12.5 (team) + 15 (budget) + 25 (sovereignty) + 10 (tolerance) = 62.5
    assert 60 < score < 65
    assert len(constraints) > 0


def test_calculate_no_match():
    """Test no match scenario."""
    architect_context = {
        "team_size": TeamSize.LEAN,  # Opposite of LARGE
        "budget": BudgetRange.UNDER_500K,  # Opposite of 2M-10M
        "data_sovereignty": DataSovereignty.ON_PREM_ONLY,  # Opposite of CLOUD_FIRST
        "vendor_tolerance": VendorTolerance.OSS_FIRST,  # Opposite of COMMERCIAL_ONLY
    }

    score, constraints = calculate_match_score(architect_context, PRIYA_PROFILE)

    # Adjacent matches only: some partial credit
    assert score < 50


# ============================================================================
# JOURNEY MATCHING TESTS
# ============================================================================


def test_match_jennifer_journey():
    """Test matching Jennifer's journey (cloud-native startup)."""
    match = match_journey_persona(
        team_size=TeamSize.STANDARD,
        budget=BudgetRange.RANGE_500K_2M,
        data_sovereignty=DataSovereignty.CLOUD_FIRST,
        vendor_tolerance=VendorTolerance.OSS_WITH_SUPPORT,
    )

    assert match.persona == "jennifer"
    assert match.confidence == 100.0
    assert "Cloud-Native Lakehouse" in match.architecture_pattern
    assert len(match.key_constraints) == 4


def test_match_marcus_journey():
    """Test matching Marcus's journey (financial services SOC)."""
    match = match_journey_persona(
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
        data_sovereignty=DataSovereignty.ON_PREM_ONLY,
        vendor_tolerance=VendorTolerance.COMMERCIAL_ONLY,
    )

    assert match.persona == "marcus"
    assert match.confidence == 100.0
    assert "SIEM" in match.architecture_pattern or "Hybrid" in match.architecture_pattern
    assert len(match.key_constraints) == 4


def test_match_priya_journey():
    """Test matching Priya's journey (enterprise security architect)."""
    match = match_journey_persona(
        team_size=TeamSize.LARGE,
        budget=BudgetRange.RANGE_2M_10M,
        data_sovereignty=DataSovereignty.HYBRID,
        vendor_tolerance=VendorTolerance.COMMERCIAL_ONLY,
    )

    assert match.persona == "priya"
    assert match.confidence == 100.0
    assert "Enterprise" in match.architecture_pattern or "Mesh" in match.architecture_pattern
    assert len(match.key_constraints) == 4


def test_match_hybrid_scenario():
    """Test hybrid scenario with close matches to multiple personas."""
    # Context that could match both Jennifer and Marcus
    match = match_journey_persona(
        team_size=TeamSize.STANDARD,  # Between LEAN (Marcus) and STANDARD (Jennifer)
        budget=BudgetRange.UNDER_500K,  # Marcus budget
        data_sovereignty=DataSovereignty.CLOUD_FIRST,  # Jennifer sovereignty
    )

    # Should detect hybrid or pick strongest match
    assert match.confidence > 0
    assert match.persona in ["jennifer", "marcus", "hybrid-jennifer-marcus", "hybrid-marcus-jennifer"]


def test_match_with_decision_state():
    """Test matching using DecisionState object."""
    state = DecisionState(
        session_id="test-123",
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
        data_sovereignty=DataSovereignty.ON_PREM_ONLY,
        vendor_tolerance=VendorTolerance.COMMERCIAL_ONLY,
    )

    match = match_journey_persona(decision_state=state)

    assert match.persona == "marcus"
    assert match.confidence == 100.0


def test_match_with_no_context():
    """Test matching with no context provided."""
    match = match_journey_persona()

    assert match.persona == "unknown"
    assert match.confidence == 0.0
    assert "No organizational context" in match.reasoning


def test_match_with_partial_context():
    """Test matching with only some context provided."""
    match = match_journey_persona(
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
    )

    # Should still match to a persona (likely Marcus)
    assert match.confidence > 0
    assert match.persona in ["jennifer", "marcus", "priya"]


# ============================================================================
# SERIALIZATION TESTS
# ============================================================================


def test_journey_match_to_dict():
    """Test JourneyMatch serialization."""
    match = match_journey_persona(
        team_size=TeamSize.STANDARD,
        budget=BudgetRange.RANGE_500K_2M,
        data_sovereignty=DataSovereignty.CLOUD_FIRST,
    )

    match_dict = match.to_dict()

    assert "persona" in match_dict
    assert "confidence" in match_dict
    assert "reasoning" in match_dict
    assert "architecture_pattern" in match_dict
    assert "key_constraints" in match_dict

    assert match_dict["persona"] == "jennifer"
    assert match_dict["confidence"] >= 75.0  # High confidence


def test_journey_match_summary():
    """Test JourneyMatch summary generation."""
    match = match_journey_persona(
        team_size=TeamSize.LARGE,
        budget=BudgetRange.RANGE_2M_10M,
    )

    summary = match.summary()

    assert "Journey Match" in summary
    assert match.persona.title() in summary or "Priya" in summary
    assert "confidence" in summary.lower()


# ============================================================================
# JOURNEY DESCRIPTION TESTS
# ============================================================================


def test_get_jennifer_description():
    """Test getting Jennifer journey description."""
    description = get_journey_description("jennifer")

    assert "Jennifer" in description
    assert "Cloud-Native" in description or "cloud-native" in description
    assert "Architecture Pattern" in description
    assert "Athena" in description or "Dremio" in description


def test_get_marcus_description():
    """Test getting Marcus journey description."""
    description = get_journey_description("marcus")

    assert "Marcus" in description
    assert "Financial" in description or "SOC" in description
    assert "Architecture Pattern" in description


def test_get_priya_description():
    """Test getting Priya journey description."""
    description = get_journey_description("priya")

    assert "Priya" in description
    assert "Enterprise" in description
    assert "Architecture Pattern" in description


def test_get_unknown_persona_description():
    """Test getting description for unknown persona."""
    description = get_journey_description("unknown")

    assert "Unknown persona" in description


# ============================================================================
# REALISTIC SCENARIO TESTS
# ============================================================================


def test_cloud_native_startup_matches_jennifer():
    """Test that cloud-native startup profile matches Jennifer."""
    match = match_journey_persona(
        team_size=TeamSize.STANDARD,
        budget=BudgetRange.RANGE_500K_2M,
        data_sovereignty=DataSovereignty.CLOUD_FIRST,
        vendor_tolerance=VendorTolerance.OSS_WITH_SUPPORT,
    )

    assert match.persona == "jennifer"
    assert match.confidence >= 90.0
    assert "Athena" in match.reasoning or "Dremio" in match.reasoning


def test_financial_services_soc_matches_marcus():
    """Test that financial services SOC profile matches Marcus."""
    match = match_journey_persona(
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
        data_sovereignty=DataSovereignty.ON_PREM_ONLY,
        vendor_tolerance=VendorTolerance.COMMERCIAL_ONLY,
    )

    assert match.persona == "marcus"
    assert match.confidence >= 90.0
    assert "on-prem" in match.reasoning.lower() or "regulatory" in match.reasoning.lower()


def test_enterprise_architect_matches_priya():
    """Test that enterprise architect profile matches Priya."""
    match = match_journey_persona(
        team_size=TeamSize.LARGE,
        budget=BudgetRange.RANGE_2M_10M,
        data_sovereignty=DataSovereignty.HYBRID,
        vendor_tolerance=VendorTolerance.COMMERCIAL_ONLY,
    )

    assert match.persona == "priya"
    assert match.confidence >= 90.0
    assert "Enterprise" in match.reasoning or "large" in match.reasoning.lower()


def test_confidence_ordering():
    """Test that matches are properly ordered by confidence."""
    # Test with ambiguous context
    match = match_journey_persona(
        team_size=TeamSize.STANDARD,
        budget=BudgetRange.RANGE_500K_2M,
    )

    # Should match to someone with reasonable confidence
    assert match.confidence > 30.0  # At least some match
    assert match.persona in ["jennifer", "marcus", "priya", "hybrid-jennifer-marcus", "hybrid-marcus-jennifer"]


def test_all_personas_have_valid_profiles():
    """Test that all persona profiles have required fields."""
    profiles = [JENNIFER_PROFILE, MARCUS_PROFILE, PRIYA_PROFILE]

    for profile in profiles:
        assert "name" in profile
        assert "team_size" in profile
        assert "budget" in profile
        assert "data_sovereignty" in profile
        assert "vendor_tolerance" in profile
        assert "architecture_pattern" in profile
        assert "description" in profile
        assert "recommended_vendors" in profile
        assert len(profile["recommended_vendors"]) > 0
