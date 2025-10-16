"""
Tier 2 Scoring Logic - Preferred Capability Scoring

Implements Chapter 3 decision framework from "Modern Data Stack for Cybersecurity" book.

Tier 2 preferences are WEIGHTED - vendors are scored based on how well they match
preferred capabilities. These are "nice-to-have" requirements that improve the
solution but aren't mandatory.

Scoring:
- Weight 3: Strongly preferred (critical for success)
- Weight 2: Preferred (important but not critical)
- Weight 1: Nice-to-have (marginal benefit)

The 3× weight multiplier ensures strongly preferred capabilities have significant
impact on final vendor ranking.
"""

from typing import Any

from src.models import Vendor


class ScoredVendor:
    """Vendor with Tier 2 preference score."""

    def __init__(self, vendor: Vendor, score: int, max_score: int, score_breakdown: dict[str, int]):
        self.vendor = vendor
        self.score = score
        self.max_score = max_score
        self.score_breakdown = score_breakdown
        self.score_percentage = (score / max_score * 100) if max_score > 0 else 0

    def __repr__(self) -> str:
        return f"ScoredVendor({self.vendor.id}, score={self.score}/{self.max_score}, {self.score_percentage:.1f}%)"


class ScoreResult:
    """Result of applying Tier 2 scoring to vendors."""

    def __init__(
        self,
        scored_vendors: list[ScoredVendor],
        preferences: dict[str, int],
        max_possible_score: int,
    ):
        self.scored_vendors = sorted(scored_vendors, key=lambda x: x.score, reverse=True)
        self.preferences = preferences
        self.max_possible_score = max_possible_score
        self.vendor_count = len(scored_vendors)

    def get_top_n(self, n: int = 5) -> list[ScoredVendor]:
        """Get top N vendors by score."""
        return self.scored_vendors[:n]

    def get_finalists(self, min_score_percentage: float = 50.0) -> list[ScoredVendor]:
        """Get finalists meeting minimum score threshold."""
        return [v for v in self.scored_vendors if v.score_percentage >= min_score_percentage]

    def summary(self) -> str:
        """Generate human-readable summary of scoring results."""
        if not self.scored_vendors:
            return "No vendors scored"

        top_vendor = self.scored_vendors[0]
        return (
            f"{self.vendor_count} vendors scored, "
            f"top: {top_vendor.vendor.name} ({top_vendor.score}/{self.max_possible_score}, "
            f"{top_vendor.score_percentage:.1f}%)"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "vendor_count": self.vendor_count,
            "max_possible_score": self.max_possible_score,
            "preferences": self.preferences,
            "scored_vendors": [
                {
                    "vendor_id": sv.vendor.id,
                    "vendor_name": sv.vendor.name,
                    "score": sv.score,
                    "max_score": sv.max_score,
                    "score_percentage": round(sv.score_percentage, 1),
                    "score_breakdown": sv.score_breakdown,
                }
                for sv in self.scored_vendors
            ],
            "summary": self.summary(),
        }


def score_vendor_on_preferences(
    vendor: Vendor, preferences: dict[str, int]
) -> tuple[int, dict[str, int]]:
    """
    Score a single vendor against Tier 2 preferences.

    Args:
        vendor: Vendor to score
        preferences: Dict of {capability_name: weight} where weight is 1-3

    Returns:
        Tuple of (total_score, score_breakdown)

    Example:
        preferences = {
            "open_table_format": 3,  # Strongly preferred
            "streaming_query": 2,     # Preferred
            "ocsf_support": 1         # Nice-to-have
        }
    """
    score = 0
    breakdown = {}

    for capability, weight in preferences.items():
        # Validate weight
        if weight not in [1, 2, 3]:
            raise ValueError(f"Weight must be 1-3, got {weight} for {capability}")

        # Get capability value from vendor
        cap_value = getattr(vendor.capabilities, capability, None)

        if cap_value is None:
            # Capability not found, skip
            breakdown[capability] = 0
            continue

        # Score based on capability type
        if isinstance(cap_value, bool):
            # Boolean capability: full weight if True, 0 if False
            if cap_value:
                points = weight
                score += points
                breakdown[capability] = points
            else:
                breakdown[capability] = 0

        elif isinstance(cap_value, str):
            # String capability: check for specific values
            # For open_table_format: iceberg-native = full points, proprietary = 0
            if capability == "open_table_format":
                if "iceberg" in cap_value.lower():
                    points = weight  # Iceberg support = full points
                elif "delta" in cap_value.lower() or "hudi" in cap_value.lower():
                    points = weight // 2  # Delta/Hudi = half points
                elif "proprietary" in cap_value.lower():
                    points = 0  # Proprietary = 0 points
                else:
                    points = weight // 2  # Unknown = half points

                score += points
                breakdown[capability] = points
            else:
                # Generic string: assume any non-empty value = full points
                points = weight if cap_value else 0
                score += points
                breakdown[capability] = points

        elif isinstance(cap_value, list):
            # List capability (e.g., deployment_models): full points if non-empty
            points = weight if cap_value else 0
            score += points
            breakdown[capability] = points

        else:
            # Unknown type, skip
            breakdown[capability] = 0

    return score, breakdown


def calculate_max_possible_score(preferences: dict[str, int]) -> int:
    """
    Calculate maximum possible score given preferences.

    Args:
        preferences: Dict of {capability_name: weight}

    Returns:
        Maximum possible score (sum of all weights)
    """
    return sum(preferences.values())


def score_vendors_tier2(
    vendors: list[Vendor], preferences: dict[str, int]
) -> ScoreResult:
    """
    Score vendors on Tier 2 preferred capabilities.

    Vendors are ranked by how well they match preferred capabilities.
    Higher scores indicate better fit.

    Args:
        vendors: List of vendors to score (typically output of Tier 1 filtering)
        preferences: Dict of {capability_name: weight (1-3)}

    Returns:
        ScoreResult with scored and ranked vendors

    Example:
        preferences = {
            "open_table_format": 3,  # Critical: vendor-neutral data format
            "streaming_query": 2,     # Important: real-time detection
            "multi_cloud": 2,         # Important: cloud flexibility
            "ocsf_support": 1         # Nice: standardized schema
        }

        result = score_vendors_tier2(viable_vendors, preferences)
        top_5 = result.get_top_n(5)
    """
    if not preferences:
        raise ValueError("Preferences cannot be empty")

    max_possible = calculate_max_possible_score(preferences)
    scored_vendors = []

    for vendor in vendors:
        score, breakdown = score_vendor_on_preferences(vendor, preferences)
        scored_vendor = ScoredVendor(
            vendor=vendor,
            score=score,
            max_score=max_possible,
            score_breakdown=breakdown,
        )
        scored_vendors.append(scored_vendor)

    return ScoreResult(
        scored_vendors=scored_vendors,
        preferences=preferences,
        max_possible_score=max_possible,
    )


def apply_combined_filtering_and_scoring(
    database,  # VendorDatabase
    team_size=None,
    budget=None,
    data_sovereignty=None,
    vendor_tolerance=None,
    tier_1_requirements=None,
    tier_2_preferences=None,
):
    """
    Apply both Tier 1 filtering and Tier 2 scoring in one operation.

    This is a convenience function that combines filtering and scoring
    to produce ranked finalists in a single step.

    Args:
        database: VendorDatabase to process
        team_size: Tier 1 team capacity filter
        budget: Tier 1 budget filter
        data_sovereignty: Tier 1 sovereignty filter
        vendor_tolerance: Tier 1 vendor tolerance filter
        tier_1_requirements: Tier 1 custom requirements
        tier_2_preferences: Tier 2 scoring preferences

    Returns:
        Tuple of (FilterResult, ScoreResult or None)
    """
    from src.tools.filter_vendors import apply_tier1_filters

    # Apply Tier 1 filters
    filter_result = apply_tier1_filters(
        database,
        team_size=team_size,
        budget=budget,
        data_sovereignty=data_sovereignty,
        vendor_tolerance=vendor_tolerance,
        tier_1_requirements=tier_1_requirements,
    )

    # Apply Tier 2 scoring if preferences provided
    score_result = None
    if tier_2_preferences and filter_result.filtered_vendors:
        score_result = score_vendors_tier2(
            filter_result.filtered_vendors, tier_2_preferences
        )

    return filter_result, score_result
