"""
Pydantic models for Security Architect MCP Server

This module defines the data models for vendors, capabilities, decision state,
and filtering logic based on the Chapter 3 decision framework from
"Modern Data Stack for Cybersecurity" book.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# ENUMS - Controlled vocabularies
# ============================================================================

class VendorCategory(str, Enum):
    """Vendor platform categories (aligned with book taxonomy)."""
    SIEM = "SIEM"
    QUERY_ENGINE = "Query Engine"
    DATA_LAKEHOUSE = "Data Lakehouse"
    STREAMING = "Streaming Platform"
    VIRTUALIZATION = "Data Virtualization"
    OBSERVABILITY = "Observability Platform"
    OBJECT_STORAGE = "Object Storage"
    DATA_CATALOG = "Data Catalog & Governance"
    ETL_ELT = "ETL/ELT Platform"
    OTHER = "Other"


class DeploymentModel(str, Enum):
    """Deployment options."""
    CLOUD = "cloud"
    ON_PREM = "on-prem"
    HYBRID = "hybrid"
    EDGE = "edge"


class CostModel(str, Enum):
    """Pricing models."""
    PER_GB = "per-gb"  # Per-GB ingestion (e.g., Splunk, Elastic)
    CONSUMPTION = "consumption"  # Consumption-based (e.g., Athena, Snowflake)
    SUBSCRIPTION = "subscription"  # Flat subscription (e.g., Dremio)
    OPEN_SOURCE = "open-source"  # Open source (infrastructure costs only)
    HYBRID = "hybrid"  # Mixed model


class Maturity(str, Enum):
    """Product maturity level."""
    PRODUCTION = "production"
    BETA = "beta"
    EXPERIMENTAL = "experimental"


class OpenTableFormat(str, Enum):
    """Open table format support."""
    ICEBERG_NATIVE = "iceberg-native"  # Native Iceberg support
    ICEBERG_SUPPORT = "iceberg-support"  # Supports Iceberg via plugin
    DELTA = "delta"  # Delta Lake native
    HUDI = "hudi"  # Apache Hudi
    PROPRIETARY = "proprietary"  # Proprietary format only
    MULTIPLE = "multiple"  # Multiple formats supported


class DataSovereignty(str, Enum):
    """Data sovereignty requirements."""
    CLOUD_FIRST = "cloud-first"
    HYBRID = "hybrid"
    ON_PREM_ONLY = "on-prem-only"
    MULTI_REGION = "multi-region"


class VendorTolerance(str, Enum):
    """Vendor relationship tolerance."""
    OSS_FIRST = "oss-first"  # Open source preferred
    OSS_WITH_SUPPORT = "oss-with-support"  # OSS acceptable if vendor provides support
    COMMERCIAL_ONLY = "commercial-only"  # Require vendor SLA, 24/7 support


class BudgetRange(str, Enum):
    """Annual budget ranges."""
    UNDER_500K = "<500K"
    RANGE_500K_2M = "500K-2M"
    RANGE_2M_10M = "2M-10M"
    OVER_10M = "10M+"


class TeamSize(str, Enum):
    """Team capacity levels."""
    LEAN = "lean"  # 1-2 engineers
    STANDARD = "standard"  # 3-5 engineers
    LARGE = "large"  # 6+ engineers


# ============================================================================
# VENDOR CAPABILITIES
# ============================================================================

class VendorCapabilities(BaseModel):
    """
    Vendor platform capabilities used for filtering and scoring.

    Based on Chapter 3 decision framework Tier 1-2-3 requirements.
    """

    # Core query capabilities
    sql_interface: bool = Field(
        description="Supports SQL queries (vs proprietary query language)"
    )
    streaming_query: bool = Field(
        default=False,
        description="Real-time/streaming query capability"
    )
    multi_engine_query: bool = Field(
        default=False,
        description="Can query data across multiple engines"
    )

    # Data format and interoperability
    open_table_format: OpenTableFormat = Field(
        description="Open table format support (Iceberg, Delta, Hudi, proprietary)"
    )
    schema_evolution: bool = Field(
        default=False,
        description="Supports schema evolution without data migration"
    )

    # Deployment and infrastructure
    deployment_models: list[DeploymentModel] = Field(
        description="Supported deployment models (cloud, on-prem, hybrid)"
    )
    cloud_native: bool = Field(
        description="Built cloud-native (vs retrofitted for cloud)"
    )
    multi_cloud: bool = Field(
        default=False,
        description="Supports multi-cloud deployments (AWS + Azure + GCP)"
    )

    # Operational complexity
    operational_complexity: str = Field(
        description="Operational overhead: 'low', 'medium', 'high'"
    )
    managed_service_available: bool = Field(
        default=False,
        description="Fully managed service available (reduces operational burden)"
    )
    team_size_required: TeamSize = Field(
        description="Minimum team size to operate effectively"
    )

    # Cost and licensing
    cost_model: CostModel = Field(
        description="Pricing model (per-gb, consumption, subscription, open-source)"
    )
    cost_predictability: str = Field(
        description="Cost predictability: 'high', 'medium', 'low'"
    )

    # Security-specific capabilities
    siem_integration: bool = Field(
        default=False,
        description="Integrates with SIEM platforms"
    )
    compliance_certifications: list[str] = Field(
        default_factory=list,
        description="Compliance certifications (SOC2, FedRAMP, ISO27001, etc.)"
    )
    data_governance: bool = Field(
        default=False,
        description="Built-in data governance and access control"
    )

    # Maturity and support
    maturity: Maturity = Field(
        description="Product maturity level (production, beta, experimental)"
    )
    vendor_support: str | None = Field(
        default=None,
        description="Vendor support tier (enterprise, standard, community, none)"
    )
    community_size: str = Field(
        default="unknown",
        description="Community size for OSS projects: 'large', 'medium', 'small', 'unknown'"
    )

    # Advanced capabilities (Tier 2-3)
    ocsf_support: bool = Field(
        default=False,
        description="Supports Open Cybersecurity Schema Framework (OCSF)"
    )
    ml_analytics: bool = Field(
        default=False,
        description="Built-in ML/analytics capabilities"
    )
    api_extensibility: bool = Field(
        default=False,
        description="Rich API for extensibility and automation"
    )

    @field_validator("operational_complexity", "cost_predictability")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate level is low/medium/high."""
        if v not in ["low", "medium", "high"]:
            raise ValueError("Must be 'low', 'medium', or 'high'")
        return v


# ============================================================================
# VENDOR MODEL
# ============================================================================

class Vendor(BaseModel):
    """
    Security data platform vendor.

    Represents a single vendor in the database with capabilities, cost model,
    and evidence sources for validation.
    """

    id: str = Field(
        description="Unique vendor identifier (lowercase-hyphenated, e.g., 'amazon-athena')"
    )
    name: str = Field(
        description="Display name (e.g., 'Amazon Athena')"
    )
    category: VendorCategory = Field(
        description="Primary platform category"
    )
    description: str = Field(
        description="Brief description of platform (1-2 sentences)"
    )
    website: str | None = Field(
        default=None,
        description="Vendor website URL"
    )

    capabilities: VendorCapabilities = Field(
        description="Platform capabilities for filtering and scoring"
    )

    # Cost information
    typical_annual_cost_range: str | None = Field(
        default=None,
        description="Typical annual cost range (e.g., '$100K-500K for 5TB/day')"
    )
    cost_notes: str | None = Field(
        default=None,
        description="Additional cost model notes and assumptions"
    )

    # Evidence and validation
    evidence_source: str = Field(
        description="Source of vendor data (book, expert interview, vendor docs, IT Harvest)"
    )
    last_updated: datetime = Field(
        default_factory=datetime.now,
        description="Last time vendor data was updated"
    )
    validated_by: str | None = Field(
        default=None,
        description="Expert who validated this vendor data (optional)"
    )

    # Tags for additional filtering
    tags: list[str] = Field(
        default_factory=list,
        description="Additional tags for flexible filtering (e.g., 'mentioned-in-book', 'practitioner-recommended')"
    )

    @field_validator("id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Ensure ID is lowercase-hyphenated."""
        if not v.islower() or " " in v:
            raise ValueError("ID must be lowercase with hyphens (e.g., 'amazon-athena')")
        return v


# ============================================================================
# VENDOR DATABASE
# ============================================================================

class VendorDatabase(BaseModel):
    """
    Complete vendor database with metadata.

    Represents the full set of vendors available for filtering.
    """

    vendors: list[Vendor] = Field(
        description="List of all vendors in database"
    )
    update_cadence: str = Field(
        default="quarterly",
        description="How often the database is updated"
    )
    last_full_update: datetime = Field(
        default_factory=datetime.now,
        description="Last time full database was refreshed"
    )
    total_vendors: int = Field(
        default=0,
        description="Total number of vendors in database"
    )

    def model_post_init(self, __context: Any) -> None:
        """Auto-populate total_vendors after initialization."""
        self.total_vendors = len(self.vendors)

    def get_by_id(self, vendor_id: str) -> Vendor | None:
        """Get vendor by ID."""
        return next((v for v in self.vendors if v.id == vendor_id), None)

    def get_by_category(self, category: VendorCategory) -> list[Vendor]:
        """Get all vendors in a category."""
        return [v for v in self.vendors if v.category == category]

    def filter_by_tags(self, tags: list[str]) -> list[Vendor]:
        """Get vendors matching any of the given tags."""
        return [v for v in self.vendors if any(tag in v.tags for tag in tags)]


# ============================================================================
# DECISION STATE
# ============================================================================

class DecisionState(BaseModel):
    """
    Architect's decision conversation state.

    Tracks constraints, requirements, and filtering progress through the
    Chapter 3 decision framework.
    """

    session_id: str = Field(
        description="Unique session identifier"
    )

    # Organizational context
    architect_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Organization profile (industry, size, maturity)"
    )

    # Tier 1 constraints (mandatory filters)
    team_size: TeamSize | None = None
    budget: BudgetRange | None = None
    data_sovereignty: DataSovereignty | None = None
    vendor_tolerance: VendorTolerance | None = None

    # Tier 1 mandatory requirements
    tier_1_requirements: dict[str, bool] = Field(
        default_factory=dict,
        description="Mandatory capabilities (missing = disqualified)"
    )

    # Tier 2 preferences (scoring weights 1-3)
    tier_2_preferences: dict[str, int] = Field(
        default_factory=dict,
        description="Preferred capabilities with weights (1=nice, 2=preferred, 3=strongly preferred)"
    )

    # Filtering state
    filtered_vendors: list[str] = Field(
        default_factory=list,
        description="Current viable vendor IDs (after Tier 1 filters)"
    )
    eliminated_vendors: dict[str, str] = Field(
        default_factory=dict,
        description="Vendor ID → elimination reason"
    )
    finalist_vendors: list[str] = Field(
        default_factory=list,
        description="Top 3-5 finalists after Tier 2 scoring"
    )

    # Journey matching (Chapter 4)
    journey_match: str | None = Field(
        default=None,
        description="Matched journey persona: 'jennifer', 'marcus', 'priya', 'hybrid'"
    )

    # Interview progress
    interview_progress: int = Field(
        default=0,
        description="Current step in 12-step decision interview (0-12)"
    )
    interview_complete: bool = Field(
        default=False,
        description="Whether decision interview is complete"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Session creation time"
    )
    last_updated: datetime = Field(
        default_factory=datetime.now,
        description="Last update time"
    )

    def mark_vendor_eliminated(self, vendor_id: str, reason: str) -> None:
        """Mark a vendor as eliminated with reason."""
        self.eliminated_vendors[vendor_id] = reason
        if vendor_id in self.filtered_vendors:
            self.filtered_vendors.remove(vendor_id)

    def update_progress(self, step: int) -> None:
        """Update interview progress."""
        self.interview_progress = step
        self.last_updated = datetime.now()
        if step >= 12:
            self.interview_complete = True
