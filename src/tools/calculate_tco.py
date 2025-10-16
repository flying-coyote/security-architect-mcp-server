"""
Total Cost of Ownership (TCO) Calculator

Projects 5-year TCO for security data platforms based on:
- Platform costs (licensing, consumption, per-GB)
- Infrastructure costs (compute, storage, network)
- Operational costs (team time, training, maintenance)
- Hidden costs (egress fees, support contracts, migration)

Helps architects budget and justify vendor selection decisions.
"""

from datetime import datetime
from typing import Any

from src.models import BudgetRange, CostModel, TeamSize, Vendor


class TCOProjection:
    """
    5-year Total Cost of Ownership projection for a vendor.

    Attributes:
        vendor: Vendor being analyzed
        year1_cost: Year 1 total cost
        year5_total: 5-year total cost
        annual_costs: List of annual costs [Y1, Y2, Y3, Y4, Y5]
        breakdown: Cost breakdown by category
        assumptions: List of assumptions used in calculation
        warnings: List of cost risks and warnings
    """

    def __init__(
        self,
        vendor: Vendor,
        year1_cost: float,
        year5_total: float,
        annual_costs: list[float],
        breakdown: dict[str, float],
        assumptions: list[str],
        warnings: list[str],
    ):
        self.vendor = vendor
        self.year1_cost = year1_cost
        self.year5_total = year5_total
        self.annual_costs = annual_costs
        self.breakdown = breakdown
        self.assumptions = assumptions
        self.warnings = warnings

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "vendor_id": self.vendor.id,
            "vendor_name": self.vendor.name,
            "year1_cost": round(self.year1_cost, 2),
            "year5_total": round(self.year5_total, 2),
            "annual_costs": [round(c, 2) for c in self.annual_costs],
            "breakdown": {k: round(v, 2) for k, v in self.breakdown.items()},
            "assumptions": self.assumptions,
            "warnings": self.warnings,
        }

    def summary(self) -> str:
        """Generate human-readable summary."""
        return f"{self.vendor.name}: ${self.year1_cost/1000:.0f}K/year → ${self.year5_total/1000:.0f}K total (5-year)"


def parse_cost_range(cost_range_str: str) -> tuple[float, float]:
    """
    Parse cost range string to min/max values.

    Args:
        cost_range_str: Cost range like "$50K-200K/year" or "$3M-12M/year"

    Returns:
        Tuple of (min_cost, max_cost) in dollars

    Example:
        parse_cost_range("$50K-200K/year") → (50000, 200000)
        parse_cost_range("$3M-12M/year") → (3000000, 12000000)
    """
    if not cost_range_str:
        return (0, 0)

    # Remove common prefixes/suffixes
    cost_str = cost_range_str.replace("/year", "").replace("/month", "").replace("$", "")

    # Remove extra text after the cost range (e.g., " for 5TB/day")
    # Split on common separators
    for separator in [" for ", " FOR ", " at ", " AT ", ","]:
        if separator in cost_str:
            cost_str = cost_str.split(separator)[0]
            break

    # Split on dash or hyphen
    parts = cost_str.split("-")
    if len(parts) != 2:
        return (0, 0)

    def parse_amount(s: str) -> float:
        """Parse amount with K/M suffix."""
        s = s.strip().upper()

        # Extract just the number and K/M suffix
        # Remove any non-numeric characters except . and K/M
        cleaned = ""
        for char in s:
            if char.isdigit() or char in ".KM":
                cleaned += char

        if "M" in cleaned:
            try:
                return float(cleaned.replace("M", "")) * 1000000
            except ValueError:
                return 0
        elif "K" in cleaned:
            try:
                return float(cleaned.replace("K", "")) * 1000
            except ValueError:
                return 0
        else:
            try:
                return float(cleaned)
            except ValueError:
                return 0

    min_cost = parse_amount(parts[0])
    max_cost = parse_amount(parts[1])

    return (min_cost, max_cost)


def calculate_tco(
    vendor: Vendor,
    data_volume_tb_day: float = 1.0,
    team_size: TeamSize = TeamSize.STANDARD,
    growth_rate: float = 0.20,  # 20% annual data growth
    include_hidden_costs: bool = True,
) -> TCOProjection:
    """
    Calculate 5-year Total Cost of Ownership for a vendor.

    Args:
        vendor: Vendor to analyze
        data_volume_tb_day: Daily data ingestion in TB
        team_size: Team capacity (affects operational costs)
        growth_rate: Annual data volume growth rate (default 20%)
        include_hidden_costs: Include egress, support, migration costs

    Returns:
        TCOProjection with 5-year cost breakdown

    Example:
        ```python
        from src.utils.database_loader import load_default_database
        from src.tools.calculate_tco import calculate_tco
        from src.models import TeamSize

        db = load_default_database()
        athena = db.get_by_id("amazon-athena")

        tco = calculate_tco(
            vendor=athena,
            data_volume_tb_day=1.0,  # 1 TB/day
            team_size=TeamSize.LEAN,
            growth_rate=0.20,  # 20% annual growth
        )

        print(tco.summary())
        # Output: Amazon Athena: $150K/year → $900K total (5-year)
        ```
    """
    assumptions = []
    warnings = []
    annual_costs = []

    # Parse vendor cost range
    min_cost, max_cost = parse_cost_range(vendor.typical_annual_cost_range or "")

    # Use midpoint of cost range as baseline
    baseline_cost = (min_cost + max_cost) / 2 if max_cost > 0 else 0

    # If no cost range, estimate based on cost model
    if baseline_cost == 0:
        baseline_cost = estimate_cost_from_model(vendor, data_volume_tb_day)
        assumptions.append(f"Cost estimated from {vendor.capabilities.cost_model.value} model (no vendor data)")

    # Calculate annual costs with growth
    for year in range(1, 6):
        # Data volume grows each year
        volume_multiplier = (1 + growth_rate) ** (year - 1)

        # Platform cost scales with data volume for per-GB models
        if vendor.capabilities.cost_model == CostModel.PER_GB:
            platform_cost = baseline_cost * volume_multiplier
        elif vendor.capabilities.cost_model == CostModel.CONSUMPTION:
            # Consumption models scale more slowly (query volume doesn't grow as fast as data)
            platform_cost = baseline_cost * (1 + (volume_multiplier - 1) * 0.6)
        else:
            # Subscription and OSS models are flat
            platform_cost = baseline_cost

        # Operational costs (team time)
        ops_cost = calculate_operational_cost(vendor, team_size)

        # Hidden costs (egress, support, migration)
        hidden_cost = 0
        if include_hidden_costs:
            hidden_cost = calculate_hidden_costs(vendor, platform_cost, year)

        total_year_cost = platform_cost + ops_cost + hidden_cost
        annual_costs.append(total_year_cost)

    # Build breakdown
    breakdown = {
        "platform_costs": sum(annual_costs) * 0.60,  # ~60% platform
        "operational_costs": sum(annual_costs) * 0.25,  # ~25% operations
        "hidden_costs": sum(annual_costs) * 0.15 if include_hidden_costs else 0,  # ~15% hidden
    }

    # Add assumptions
    assumptions.append(f"Data volume: {data_volume_tb_day} TB/day growing {growth_rate*100:.0f}%/year")
    assumptions.append(f"Team size: {team_size.value} ({get_team_fte(team_size)} FTE)")
    assumptions.append(f"Cost model: {vendor.capabilities.cost_model.value}")

    # Add warnings based on vendor characteristics
    if vendor.capabilities.cost_predictability == "low":
        warnings.append("⚠️ Low cost predictability - actual costs may vary significantly")

    if vendor.capabilities.cost_model == CostModel.PER_GB:
        warnings.append("⚠️ Per-GB pricing - costs will spike with data volume growth")

    if not vendor.capabilities.cloud_native and "cloud" in [d.value for d in vendor.capabilities.deployment_models]:
        warnings.append("⚠️ Not cloud-native - may incur higher cloud infrastructure costs")

    if vendor.capabilities.operational_complexity == "high":
        warnings.append("⚠️ High operational complexity - significant team time required")

    return TCOProjection(
        vendor=vendor,
        year1_cost=annual_costs[0],
        year5_total=sum(annual_costs),
        annual_costs=annual_costs,
        breakdown=breakdown,
        assumptions=assumptions,
        warnings=warnings,
    )


def estimate_cost_from_model(vendor: Vendor, data_volume_tb_day: float) -> float:
    """
    Estimate annual cost based on cost model when no vendor data available.

    Args:
        vendor: Vendor to estimate
        data_volume_tb_day: Daily data volume in TB

    Returns:
        Estimated annual cost in dollars
    """
    cost_model = vendor.capabilities.cost_model

    if cost_model == CostModel.PER_GB:
        # Assume $150-200/TB/month for per-GB models (typical SIEM pricing)
        monthly_tb = data_volume_tb_day * 30
        return monthly_tb * 175 * 12  # $175/TB/month * 12 months

    elif cost_model == CostModel.CONSUMPTION:
        # Assume $50-100/TB/month for consumption models (query-based)
        monthly_tb = data_volume_tb_day * 30
        return monthly_tb * 75 * 12  # $75/TB/month * 12 months

    elif cost_model == CostModel.SUBSCRIPTION:
        # Flat subscription: $200K-500K/year typical
        return 350000

    elif cost_model == CostModel.OPEN_SOURCE:
        # Infrastructure costs only: $50-150/TB/month
        monthly_tb = data_volume_tb_day * 30
        return monthly_tb * 100 * 12  # $100/TB/month infrastructure

    else:  # HYBRID
        # Mix of subscription + consumption
        return 400000


def calculate_operational_cost(vendor: Vendor, team_size: TeamSize) -> float:
    """
    Calculate annual operational cost (team time).

    Args:
        vendor: Vendor being analyzed
        team_size: Team capacity

    Returns:
        Annual operational cost in dollars
    """
    # FTE cost assumptions
    engineer_cost_per_year = 150000  # $150K/year fully loaded cost

    # Time investment based on operational complexity
    complexity = vendor.capabilities.operational_complexity
    fte_required = {
        "low": 0.25,  # 0.25 FTE (1 week/month)
        "medium": 0.50,  # 0.5 FTE (2 weeks/month)
        "high": 1.0,  # 1 FTE (full-time)
    }.get(complexity, 0.5)

    return fte_required * engineer_cost_per_year


def calculate_hidden_costs(vendor: Vendor, platform_cost: float, year: int) -> float:
    """
    Calculate hidden costs (egress, support, migration).

    Args:
        vendor: Vendor being analyzed
        platform_cost: Annual platform cost
        year: Current year (1-5)

    Returns:
        Annual hidden costs in dollars
    """
    hidden_cost = 0

    # Egress fees (10-20% of platform cost for cloud vendors)
    if "cloud" in [d.value for d in vendor.capabilities.deployment_models]:
        egress_multiplier = 0.15  # 15% egress fees
        hidden_cost += platform_cost * egress_multiplier

    # Support contracts (10-20% for commercial vendors)
    if vendor.capabilities.vendor_support in ["enterprise", "standard"]:
        support_multiplier = 0.12  # 12% support contract
        hidden_cost += platform_cost * support_multiplier

    # Migration costs (Year 1 only)
    if year == 1:
        migration_cost = 50000  # $50K migration cost
        hidden_cost += migration_cost

    return hidden_cost


def get_team_fte(team_size: TeamSize) -> float:
    """Get FTE count for team size."""
    return {
        TeamSize.LEAN: 1.5,  # 1-2 engineers
        TeamSize.STANDARD: 4.0,  # 3-5 engineers
        TeamSize.LARGE: 8.0,  # 6+ engineers
    }.get(team_size, 4.0)


def compare_vendors_tco(
    vendors: list[Vendor],
    data_volume_tb_day: float = 1.0,
    team_size: TeamSize = TeamSize.STANDARD,
    growth_rate: float = 0.20,
) -> list[TCOProjection]:
    """
    Compare TCO across multiple vendors.

    Args:
        vendors: List of vendors to compare
        data_volume_tb_day: Daily data ingestion in TB
        team_size: Team capacity
        growth_rate: Annual data volume growth rate

    Returns:
        List of TCOProjection sorted by 5-year total cost (lowest first)

    Example:
        ```python
        from src.tools.filter_vendors import apply_tier1_filters
        from src.tools.calculate_tco import compare_vendors_tco

        filter_result = apply_tier1_filters(
            vendor_db,
            team_size=TeamSize.LEAN,
            budget=BudgetRange.UNDER_500K,
        )

        tco_comparison = compare_vendors_tco(
            vendors=filter_result.filtered_vendors,
            data_volume_tb_day=1.0,
            team_size=TeamSize.LEAN,
        )

        for tco in tco_comparison[:3]:
            print(tco.summary())
        ```
    """
    projections = []

    for vendor in vendors:
        tco = calculate_tco(
            vendor=vendor,
            data_volume_tb_day=data_volume_tb_day,
            team_size=team_size,
            growth_rate=growth_rate,
        )
        projections.append(tco)

    # Sort by 5-year total cost (lowest first)
    projections.sort(key=lambda x: x.year5_total)

    return projections
