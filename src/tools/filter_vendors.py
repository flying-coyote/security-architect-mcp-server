"""
Foundational + Tier 1 Filtering Logic - Mandatory Requirement Filters

Implements Chapter 3 decision framework from "Modern Data Stack for Cybersecurity" book
with Phase 1 foundational architecture decisions added (October 2025).

PHASE 1: FOUNDATIONAL ARCHITECTURE FILTERING (NEW - Oct 2025)
Applied BEFORE organizational constraints. Establishes architectural approach.
1. Table format - Iceberg vs Delta Lake vs Hudi vs Proprietary
2. Catalog - Polaris vs Unity Catalog vs Nessie vs Glue vs Hive Metastore
3. Transformation - dbt vs Spark vs Vendor built-in vs Custom Python
4. Query engine - Low-latency vs High-concurrency vs Serverless vs Cost-optimized

PHASE 2: ORGANIZATIONAL CONSTRAINT FILTERING (Tier 1)
Applied AFTER foundational filtering. Filters vendors within chosen architecture.
1. Team capacity - Eliminates platforms requiring more engineers than available
2. Budget - Eliminates platforms exceeding budget ceiling
3. Data sovereignty - Eliminates platforms violating compliance requirements
4. Vendor tolerance - Eliminates OSS/commercial based on support needs
5. Custom mandatory requirements - Architect-specific must-haves
"""

from typing import Any

from src.models import (
    BudgetRange,
    DataSovereignty,
    DecisionState,
    DeploymentModel,
    TeamSize,
    Vendor,
    VendorDatabase,
    VendorTolerance,
)


class FilterResult:
    """Result of applying Tier 1 filters to vendor database."""

    def __init__(
        self,
        initial_count: int,
        filtered_vendors: list[Vendor],
        eliminated_vendors: dict[str, str],
    ):
        self.initial_count = initial_count
        self.filtered_vendors = filtered_vendors
        self.eliminated_vendors = eliminated_vendors
        self.filtered_count = len(filtered_vendors)
        self.eliminated_count = len(eliminated_vendors)

    def summary(self) -> str:
        """Generate human-readable summary of filtering results."""
        return (
            f"{self.initial_count} vendors → {self.filtered_count} viable "
            f"({self.eliminated_count} eliminated)"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "initial_count": self.initial_count,
            "filtered_count": self.filtered_count,
            "eliminated_count": self.eliminated_count,
            "filtered_vendor_ids": [v.id for v in self.filtered_vendors],
            "eliminated_vendors": self.eliminated_vendors,
            "summary": self.summary(),
        }


def filter_by_team_capacity(
    vendors: list[Vendor], team_size: TeamSize
) -> tuple[list[Vendor], dict[str, str]]:
    """
    Filter vendors by team capacity requirements.

    Eliminates platforms requiring more engineering resources than available.

    Args:
        vendors: List of vendors to filter
        team_size: Available team capacity (lean, standard, large)

    Returns:
        Tuple of (viable_vendors, eliminated_vendors_with_reasons)
    """
    viable = []
    eliminated = {}

    # Team size hierarchy: lean < standard < large
    team_hierarchy = {TeamSize.LEAN: 0, TeamSize.STANDARD: 1, TeamSize.LARGE: 2}
    available_capacity = team_hierarchy[team_size]

    for vendor in vendors:
        required_capacity = team_hierarchy[vendor.capabilities.team_size_required]

        if required_capacity > available_capacity:
            eliminated[vendor.id] = (
                f"Requires {vendor.capabilities.team_size_required.value} team "
                f"(you have {team_size.value}). "
                f"Operational complexity: {vendor.capabilities.operational_complexity}."
            )
        else:
            viable.append(vendor)

    return viable, eliminated


def filter_by_budget(
    vendors: list[Vendor], budget: BudgetRange
) -> tuple[list[Vendor], dict[str, str]]:
    """
    Filter vendors by budget constraints.

    Eliminates platforms whose typical annual costs exceed budget ceiling.

    Args:
        vendors: List of vendors to filter
        budget: Annual budget range

    Returns:
        Tuple of (viable_vendors, eliminated_vendors_with_reasons)
    """
    viable = []
    eliminated = {}

    # Budget ceiling thresholds (in thousands)
    budget_ceilings = {
        BudgetRange.UNDER_500K: 500,
        BudgetRange.RANGE_500K_2M: 2000,
        BudgetRange.RANGE_2M_10M: 10000,
        BudgetRange.OVER_10M: float("inf"),
    }
    ceiling = budget_ceilings[budget]

    for vendor in vendors:
        # Parse cost range to extract maximum
        # Format: "$XXK-YYK for ZTB/day" or "$XM-YM for ZTB/day"
        cost_range = vendor.typical_annual_cost_range
        if not cost_range:
            # No cost data, assume viable (conservative approach)
            viable.append(vendor)
            continue

        # Extract maximum cost from range
        try:
            # Look for patterns like "$3M-12M" or "$50K-200K"
            parts = cost_range.split("-")
            if len(parts) >= 2:
                # Get the high end (before " for")
                high_end = parts[1].split()[0]  # e.g., "12M" or "200K"

                # Convert to thousands
                if "M" in high_end:
                    max_cost = float(high_end.replace("$", "").replace("M", "")) * 1000
                elif "K" in high_end:
                    max_cost = float(high_end.replace("$", "").replace("K", ""))
                else:
                    # Can't parse, assume viable
                    viable.append(vendor)
                    continue

                if max_cost > ceiling:
                    eliminated[vendor.id] = (
                        f"Typical cost {cost_range} exceeds budget ceiling "
                        f"${ceiling}K/year. Cost model: {vendor.capabilities.cost_model.value}."
                    )
                else:
                    viable.append(vendor)
            else:
                # Can't parse, assume viable
                viable.append(vendor)
        except (ValueError, IndexError):
            # Parsing error, assume viable (conservative)
            viable.append(vendor)

    return viable, eliminated


def filter_by_data_sovereignty(
    vendors: list[Vendor], sovereignty: DataSovereignty
) -> tuple[list[Vendor], dict[str, str]]:
    """
    Filter vendors by data sovereignty requirements.

    Eliminates platforms that don't meet compliance/deployment constraints.

    Args:
        vendors: List of vendors to filter
        sovereignty: Data sovereignty requirement

    Returns:
        Tuple of (viable_vendors, eliminated_vendors_with_reasons)
    """
    viable = []
    eliminated = {}

    for vendor in vendors:
        deployment_models = vendor.capabilities.deployment_models

        # ON_PREM_ONLY: Must support on-premises deployment
        if sovereignty == DataSovereignty.ON_PREM_ONLY:
            if DeploymentModel.ON_PREM not in deployment_models:
                eliminated[vendor.id] = (
                    f"Cloud-only platform, violates on-prem requirement. "
                    f"Deployment models: {[d.value for d in deployment_models]}."
                )
                continue

        # CLOUD_FIRST: Prefer cloud but no hard requirement
        # (all vendors pass this filter)

        # HYBRID: Must support hybrid deployment
        if sovereignty == DataSovereignty.HYBRID:
            if DeploymentModel.HYBRID not in deployment_models:
                # Check if supports both cloud and on-prem (implies hybrid capability)
                has_cloud = DeploymentModel.CLOUD in deployment_models
                has_onprem = DeploymentModel.ON_PREM in deployment_models

                if not (has_cloud and has_onprem):
                    eliminated[vendor.id] = (
                        f"Does not support hybrid deployment. "
                        f"Deployment models: {[d.value for d in deployment_models]}."
                    )
                    continue

        # MULTI_REGION: Must support multi-cloud for data residency
        if sovereignty == DataSovereignty.MULTI_REGION:
            if not vendor.capabilities.multi_cloud:
                eliminated[vendor.id] = (
                    f"Does not support multi-cloud (required for multi-region data residency). "
                    f"Multi-cloud: {vendor.capabilities.multi_cloud}."
                )
                continue

        viable.append(vendor)

    return viable, eliminated


def filter_by_vendor_tolerance(
    vendors: list[Vendor], tolerance: VendorTolerance
) -> tuple[list[Vendor], dict[str, str]]:
    """
    Filter vendors by organization's vendor relationship tolerance.

    Determines whether open-source or commercial support is required.

    Args:
        vendors: List of vendors to filter
        tolerance: Vendor relationship tolerance level

    Returns:
        Tuple of (viable_vendors, eliminated_vendors_with_reasons)
    """
    viable = []
    eliminated = {}

    for vendor in vendors:
        is_open_source = vendor.capabilities.cost_model.value == "open-source"
        has_vendor_support = vendor.capabilities.vendor_support is not None

        # OSS_FIRST: Prefer open source, commercial OK
        if tolerance == VendorTolerance.OSS_FIRST:
            # All vendors acceptable, but prefer OSS
            viable.append(vendor)

        # OSS_WITH_SUPPORT: OSS acceptable only if vendor provides support
        elif tolerance == VendorTolerance.OSS_WITH_SUPPORT:
            if is_open_source and not has_vendor_support:
                eliminated[vendor.id] = (
                    f"Open-source without vendor support, violates support requirement. "
                    f"Vendor support: {vendor.capabilities.vendor_support}."
                )
            else:
                viable.append(vendor)

        # COMMERCIAL_ONLY: Require vendor SLA, 24/7 support, legal accountability
        elif tolerance == VendorTolerance.COMMERCIAL_ONLY:
            if is_open_source:
                eliminated[vendor.id] = (
                    f"Open-source platform, violates commercial-only requirement. "
                    f"Cost model: {vendor.capabilities.cost_model.value}."
                )
            elif vendor.capabilities.vendor_support not in ["enterprise", "standard"]:
                eliminated[vendor.id] = (
                    f"Insufficient vendor support (requires enterprise/standard SLA). "
                    f"Vendor support: {vendor.capabilities.vendor_support}."
                )
            else:
                viable.append(vendor)

    return viable, eliminated


def filter_by_tier1_requirements(
    vendors: list[Vendor], requirements: dict[str, bool]
) -> tuple[list[Vendor], dict[str, str]]:
    """
    Filter vendors by custom Tier 1 mandatory requirements.

    These are architect-specific must-haves that eliminate vendors immediately
    if not met (e.g., SQL interface, streaming, open format).

    Args:
        vendors: List of vendors to filter
        requirements: Dict of {capability_name: required_value}

    Returns:
        Tuple of (viable_vendors, eliminated_vendors_with_reasons)

    Example:
        requirements = {
            "sql_interface": True,
            "streaming_query": False,  # Don't need streaming
        }
    """
    viable = []
    eliminated = {}

    for vendor in vendors:
        failed_requirements = []

        for capability, required_value in requirements.items():
            # Get capability value from vendor (handle nested attributes)
            actual_value = getattr(vendor.capabilities, capability, None)

            # For boolean requirements, check if actual matches required
            if isinstance(required_value, bool):
                if actual_value != required_value:
                    failed_requirements.append(
                        f"{capability}={actual_value} (required={required_value})"
                    )

        if failed_requirements:
            eliminated[vendor.id] = (
                f"Missing Tier 1 mandatory requirements: {', '.join(failed_requirements)}."
            )
        else:
            viable.append(vendor)

    return viable, eliminated


# ============================================================================
# PHASE 1: FOUNDATIONAL ARCHITECTURE FILTERING (Added Oct 2025)
# ============================================================================

def apply_foundational_filters(
    database: VendorDatabase,
    table_format: str | None = None,
    catalog: str | None = None,
    transformation_strategy: str | None = None,
    query_engine_preference: str | None = None,
    isolation_pattern: str | None = None,
) -> FilterResult:
    """
    Apply Phase 1 foundational architecture filters to vendor database.

    These filters establish architectural commitments BEFORE organizational
    constraints. Filters vendors based on architecture decisions (table format,
    catalog, transformation, query engine, isolation pattern).

    **NEW (November 2025)**: Isolation pattern parameter guides catalog and query
    engine recommendations without eliminating vendors. Isolated platforms enable
    performance-first selection (0% RLS overhead). Shared platforms require
    fine-grained access control.

    Args:
        database: VendorDatabase to filter
        table_format: Preferred table format (iceberg, delta_lake, hudi, proprietary, undecided)
        catalog: Preferred catalog (polaris, unity_catalog, nessie, glue, hive_metastore, undecided)
        transformation_strategy: Preferred transformation (dbt, spark, vendor_builtin, custom_python, undecided)
        query_engine_preference: Query engine characteristics (low_latency, high_concurrency, serverless, cost_optimized, flexible)
        isolation_pattern: Infrastructure isolation (isolated_dedicated, shared_corporate, multi_tenant_mssp, undecided)

    Returns:
        FilterResult with viable vendors and elimination reasons
    """
    initial_count = len(database.vendors)
    viable = database.vendors.copy()
    all_eliminated = {}

    # Note on Isolation Pattern (November 2025):
    # Isolation pattern guides catalog/query engine recommendations rather than
    # eliminating vendors. The filtering logic remains based on table format,
    # catalog, transformation, and query engine preferences, but isolation pattern
    # informs which choices are optimal:
    #
    # - isolated_dedicated: Polaris/Nessie catalogs preferred (0% RLS overhead),
    #   performance-first query engine selection (ClickHouse, DuckDB, Trino)
    # - shared_corporate: Unity Catalog required (fine-grained access control),
    #   RLS-aware query engines (Databricks SQL, Trino with row filters)
    # - multi_tenant_mssp: Unity Catalog required (row-level security essential),
    #   tenant isolation enforcement
    #
    # Recommendations are provided via src.utils.recommendations module.
    # This function focuses on hard architectural filtering.

    # Filter 1: Table format preference
    if table_format and table_format != "undecided":
        eliminated_vendors = {}
        filtered_vendors = []

        for vendor in viable:
            caps = vendor.capabilities

            if table_format == "iceberg":
                if not caps.iceberg_support:
                    eliminated_vendors[vendor.id] = (
                        f"Does not support Apache Iceberg table format (architectural requirement). "
                        f"Table format: {caps.open_table_format.value}."
                    )
                else:
                    filtered_vendors.append(vendor)

            elif table_format == "delta_lake":
                if not caps.delta_lake_support:
                    eliminated_vendors[vendor.id] = (
                        f"Does not support Delta Lake table format (architectural requirement). "
                        f"Table format: {caps.open_table_format.value}."
                    )
                else:
                    filtered_vendors.append(vendor)

            elif table_format == "hudi":
                if not caps.hudi_support:
                    eliminated_vendors[vendor.id] = (
                        f"Does not support Apache Hudi table format (architectural requirement). "
                        f"Table format: {caps.open_table_format.value}."
                    )
                else:
                    filtered_vendors.append(vendor)

            elif table_format == "proprietary":
                if caps.open_table_format not in ["proprietary"]:
                    eliminated_vendors[vendor.id] = (
                        f"Does not use proprietary table format (architectural requirement). "
                        f"Table format: {caps.open_table_format.value}."
                    )
                else:
                    filtered_vendors.append(vendor)

            else:
                # Unknown format, assume viable
                filtered_vendors.append(vendor)

        viable = filtered_vendors
        all_eliminated.update(eliminated_vendors)

    # Filter 2: Catalog preference
    if catalog and catalog != "undecided":
        eliminated_vendors = {}
        filtered_vendors = []

        for vendor in viable:
            caps = vendor.capabilities

            if catalog == "polaris" and not caps.polaris_catalog_support:
                eliminated_vendors[vendor.id] = (
                    f"Does not support Polaris catalog (architectural requirement)."
                )
            elif catalog == "unity_catalog" and not caps.unity_catalog_support:
                eliminated_vendors[vendor.id] = (
                    f"Does not support Unity Catalog (architectural requirement)."
                )
            elif catalog == "nessie" and not caps.nessie_catalog_support:
                eliminated_vendors[vendor.id] = (
                    f"Does not support Nessie catalog (architectural requirement)."
                )
            elif catalog == "glue" and not caps.glue_catalog_support:
                eliminated_vendors[vendor.id] = (
                    f"Does not support AWS Glue catalog (architectural requirement)."
                )
            elif catalog == "hive_metastore" and not caps.hive_metastore_support:
                eliminated_vendors[vendor.id] = (
                    f"Does not support Hive Metastore catalog (architectural requirement)."
                )
            else:
                filtered_vendors.append(vendor)

        viable = filtered_vendors
        all_eliminated.update(eliminated_vendors)

    # Filter 3: Transformation strategy preference
    if transformation_strategy and transformation_strategy != "undecided":
        eliminated_vendors = {}
        filtered_vendors = []

        for vendor in viable:
            caps = vendor.capabilities

            if transformation_strategy == "dbt" and not caps.dbt_integration:
                eliminated_vendors[vendor.id] = (
                    f"Does not integrate with dbt (architectural requirement)."
                )
            elif transformation_strategy == "spark" and not caps.spark_transformation_support:
                eliminated_vendors[vendor.id] = (
                    f"Does not support Apache Spark transformations (architectural requirement)."
                )
            elif transformation_strategy in ["vendor_builtin", "custom_python", "flexible"]:
                # These strategies are vendor-agnostic, all vendors viable
                filtered_vendors.append(vendor)
            else:
                filtered_vendors.append(vendor)

        viable = filtered_vendors
        all_eliminated.update(eliminated_vendors)

    # Filter 4: Query engine characteristics preference
    if query_engine_preference and query_engine_preference != "flexible":
        eliminated_vendors = {}
        filtered_vendors = []

        for vendor in viable:
            caps = vendor.capabilities

            if query_engine_preference == "low_latency":
                # Require P95 latency < 1000ms (1 second)
                if caps.query_latency_p95 is not None and caps.query_latency_p95 >= 1000:
                    eliminated_vendors[vendor.id] = (
                        f"Query latency P95 {caps.query_latency_p95}ms exceeds low-latency requirement (<1 second). "
                        f"Consider high_concurrency or serverless preference."
                    )
                else:
                    filtered_vendors.append(vendor)

            elif query_engine_preference == "high_concurrency":
                # Require concurrency >= 50 concurrent queries
                if caps.query_concurrency is not None and caps.query_concurrency < 50:
                    eliminated_vendors[vendor.id] = (
                        f"Query concurrency {caps.query_concurrency} below high-concurrency requirement (≥50). "
                        f"Consider low_latency or serverless preference."
                    )
                else:
                    filtered_vendors.append(vendor)

            elif query_engine_preference == "serverless":
                # Require managed service available
                if not caps.managed_service_available:
                    eliminated_vendors[vendor.id] = (
                        f"No managed/serverless service available (architectural requirement). "
                        f"Consider low_latency or cost_optimized preference."
                    )
                else:
                    filtered_vendors.append(vendor)

            elif query_engine_preference == "cost_optimized":
                # Require open-source or consumption-based pricing
                if caps.cost_model.value not in ["open-source", "consumption"]:
                    eliminated_vendors[vendor.id] = (
                        f"Cost model {caps.cost_model.value} not cost-optimized (require open-source or consumption). "
                        f"Consider serverless preference."
                    )
                else:
                    filtered_vendors.append(vendor)

            else:
                # Unknown preference, assume viable
                filtered_vendors.append(vendor)

        viable = filtered_vendors
        all_eliminated.update(eliminated_vendors)

    return FilterResult(
        initial_count=initial_count,
        filtered_vendors=viable,
        eliminated_vendors=all_eliminated,
    )


# ============================================================================
# PHASE 2: ORGANIZATIONAL CONSTRAINT FILTERING (Tier 1)
# ============================================================================

def apply_tier1_filters(
    database: VendorDatabase,
    team_size: TeamSize | None = None,
    budget: BudgetRange | None = None,
    data_sovereignty: DataSovereignty | None = None,
    vendor_tolerance: VendorTolerance | None = None,
    tier_1_requirements: dict[str, bool] | None = None,
) -> FilterResult:
    """
    Apply all Tier 1 mandatory filters to vendor database.

    Filters are applied sequentially. Order matters: each filter operates on
    the output of the previous filter.

    Args:
        database: VendorDatabase to filter
        team_size: Team capacity constraint (optional)
        budget: Budget ceiling (optional)
        data_sovereignty: Deployment/compliance requirement (optional)
        vendor_tolerance: OSS vs commercial preference (optional)
        tier_1_requirements: Custom mandatory capabilities (optional)

    Returns:
        FilterResult with viable vendors and elimination reasons
    """
    initial_count = len(database.vendors)
    viable = database.vendors.copy()
    all_eliminated = {}

    # Filter 1: Team capacity
    if team_size:
        viable, eliminated = filter_by_team_capacity(viable, team_size)
        all_eliminated.update(eliminated)

    # Filter 2: Budget
    if budget:
        viable, eliminated = filter_by_budget(viable, budget)
        all_eliminated.update(eliminated)

    # Filter 3: Data sovereignty
    if data_sovereignty:
        viable, eliminated = filter_by_data_sovereignty(viable, data_sovereignty)
        all_eliminated.update(eliminated)

    # Filter 4: Vendor tolerance
    if vendor_tolerance:
        viable, eliminated = filter_by_vendor_tolerance(viable, vendor_tolerance)
        all_eliminated.update(eliminated)

    # Filter 5: Custom Tier 1 requirements
    if tier_1_requirements:
        viable, eliminated = filter_by_tier1_requirements(viable, tier_1_requirements)
        all_eliminated.update(eliminated)

    return FilterResult(
        initial_count=initial_count,
        filtered_vendors=viable,
        eliminated_vendors=all_eliminated,
    )


def update_decision_state_with_filters(
    state: DecisionState, result: FilterResult
) -> DecisionState:
    """
    Update DecisionState with filtering results.

    Args:
        state: DecisionState to update
        result: FilterResult from apply_tier1_filters()

    Returns:
        Updated DecisionState
    """
    state.filtered_vendors = [v.id for v in result.filtered_vendors]
    state.eliminated_vendors = result.eliminated_vendors
    state.last_updated = __import__("datetime").datetime.now()

    return state
