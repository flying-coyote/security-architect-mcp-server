"""
Tests for Pydantic models (vendors, capabilities, decision state)
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.models import (
    BudgetRange,
    CostModel,
    DataSovereignty,
    DecisionState,
    DeploymentModel,
    Maturity,
    OpenTableFormat,
    TeamSize,
    Vendor,
    VendorCapabilities,
    VendorCategory,
    VendorDatabase,
    VendorTolerance,
)


# ============================================================================
# VENDOR CAPABILITIES TESTS
# ============================================================================


def test_vendor_capabilities_minimal():
    """Test creating minimal vendor capabilities."""
    caps = VendorCapabilities(
        sql_interface=True,
        open_table_format=OpenTableFormat.ICEBERG_NATIVE,
        deployment_models=[DeploymentModel.CLOUD],
        cloud_native=True,
        operational_complexity="low",
        team_size_required=TeamSize.LEAN,
        cost_model=CostModel.CONSUMPTION,
        cost_predictability="high",
        maturity=Maturity.PRODUCTION,
    )

    assert caps.sql_interface is True
    assert caps.open_table_format == OpenTableFormat.ICEBERG_NATIVE
    assert DeploymentModel.CLOUD in caps.deployment_models
    assert caps.streaming_query is False  # Default


def test_vendor_capabilities_full():
    """Test creating fully populated vendor capabilities."""
    caps = VendorCapabilities(
        sql_interface=True,
        streaming_query=True,
        multi_engine_query=True,
        open_table_format=OpenTableFormat.ICEBERG_NATIVE,
        schema_evolution=True,
        deployment_models=[DeploymentModel.CLOUD, DeploymentModel.HYBRID],
        cloud_native=True,
        multi_cloud=True,
        operational_complexity="low",
        managed_service_available=True,
        team_size_required=TeamSize.LEAN,
        cost_model=CostModel.CONSUMPTION,
        cost_predictability="high",
        siem_integration=True,
        compliance_certifications=["SOC2", "FedRAMP"],
        data_governance=True,
        maturity=Maturity.PRODUCTION,
        vendor_support="enterprise",
        community_size="large",
        ocsf_support=True,
        ml_analytics=True,
        api_extensibility=True,
    )

    assert caps.streaming_query is True
    assert caps.multi_cloud is True
    assert len(caps.compliance_certifications) == 2
    assert caps.ocsf_support is True


def test_vendor_capabilities_invalid_complexity():
    """Test that invalid operational complexity raises error."""
    with pytest.raises(ValidationError):
        VendorCapabilities(
            sql_interface=True,
            open_table_format=OpenTableFormat.ICEBERG_NATIVE,
            deployment_models=[DeploymentModel.CLOUD],
            cloud_native=True,
            operational_complexity="invalid",  # Should be low/medium/high
            team_size_required=TeamSize.LEAN,
            cost_model=CostModel.CONSUMPTION,
            cost_predictability="high",
            maturity=Maturity.PRODUCTION,
        )


# ============================================================================
# VENDOR TESTS
# ============================================================================


def test_vendor_minimal():
    """Test creating minimal vendor."""
    caps = VendorCapabilities(
        sql_interface=True,
        open_table_format=OpenTableFormat.ICEBERG_NATIVE,
        deployment_models=[DeploymentModel.CLOUD],
        cloud_native=True,
        operational_complexity="low",
        team_size_required=TeamSize.LEAN,
        cost_model=CostModel.CONSUMPTION,
        cost_predictability="high",
        maturity=Maturity.PRODUCTION,
    )

    vendor = Vendor(
        id="amazon-athena",
        name="Amazon Athena",
        category=VendorCategory.QUERY_ENGINE,
        description="Serverless interactive query service for S3",
        capabilities=caps,
        evidence_source="book-chapter-3",
    )

    assert vendor.id == "amazon-athena"
    assert vendor.name == "Amazon Athena"
    assert vendor.category == VendorCategory.QUERY_ENGINE
    assert vendor.capabilities.sql_interface is True


def test_vendor_full():
    """Test creating fully populated vendor."""
    caps = VendorCapabilities(
        sql_interface=True,
        open_table_format=OpenTableFormat.ICEBERG_NATIVE,
        deployment_models=[DeploymentModel.CLOUD],
        cloud_native=True,
        operational_complexity="low",
        team_size_required=TeamSize.LEAN,
        cost_model=CostModel.CONSUMPTION,
        cost_predictability="high",
        maturity=Maturity.PRODUCTION,
        vendor_support="enterprise",
    )

    vendor = Vendor(
        id="amazon-athena",
        name="Amazon Athena",
        category=VendorCategory.QUERY_ENGINE,
        description="Serverless interactive query service for S3",
        website="https://aws.amazon.com/athena",
        capabilities=caps,
        typical_annual_cost_range="$50K-200K for 5TB/day",
        cost_notes="Pay per query, $5/TB scanned",
        evidence_source="book-chapter-3",
        validated_by="Jeremy Wiley",
        tags=["mentioned-in-book", "practitioner-recommended"],
    )

    assert vendor.website == "https://aws.amazon.com/athena"
    assert "mentioned-in-book" in vendor.tags
    assert vendor.validated_by == "Jeremy Wiley"


def test_vendor_invalid_id():
    """Test that uppercase or spaced ID raises error."""
    caps = VendorCapabilities(
        sql_interface=True,
        open_table_format=OpenTableFormat.ICEBERG_NATIVE,
        deployment_models=[DeploymentModel.CLOUD],
        cloud_native=True,
        operational_complexity="low",
        team_size_required=TeamSize.LEAN,
        cost_model=CostModel.CONSUMPTION,
        cost_predictability="high",
        maturity=Maturity.PRODUCTION,
    )

    with pytest.raises(ValidationError):
        Vendor(
            id="Amazon Athena",  # Should be lowercase-hyphenated
            name="Amazon Athena",
            category=VendorCategory.QUERY_ENGINE,
            description="Serverless query service",
            capabilities=caps,
            evidence_source="book",
        )


# ============================================================================
# VENDOR DATABASE TESTS
# ============================================================================


def test_vendor_database_empty():
    """Test creating empty vendor database."""
    db = VendorDatabase(vendors=[])

    assert len(db.vendors) == 0
    assert db.total_vendors == 0
    assert db.update_cadence == "quarterly"


def test_vendor_database_with_vendors():
    """Test vendor database with multiple vendors."""
    caps1 = VendorCapabilities(
        sql_interface=True,
        open_table_format=OpenTableFormat.ICEBERG_NATIVE,
        deployment_models=[DeploymentModel.CLOUD],
        cloud_native=True,
        operational_complexity="low",
        team_size_required=TeamSize.LEAN,
        cost_model=CostModel.CONSUMPTION,
        cost_predictability="high",
        maturity=Maturity.PRODUCTION,
    )

    caps2 = VendorCapabilities(
        sql_interface=True,
        open_table_format=OpenTableFormat.PROPRIETARY,
        deployment_models=[DeploymentModel.CLOUD, DeploymentModel.ON_PREM],
        cloud_native=False,
        operational_complexity="high",
        team_size_required=TeamSize.LARGE,
        cost_model=CostModel.PER_GB,
        cost_predictability="medium",
        maturity=Maturity.PRODUCTION,
    )

    vendor1 = Vendor(
        id="amazon-athena",
        name="Amazon Athena",
        category=VendorCategory.QUERY_ENGINE,
        description="Serverless query service",
        capabilities=caps1,
        evidence_source="book",
        tags=["mentioned-in-book"],
    )

    vendor2 = Vendor(
        id="splunk",
        name="Splunk Enterprise Security",
        category=VendorCategory.SIEM,
        description="Security information and event management",
        capabilities=caps2,
        evidence_source="book",
        tags=["mentioned-in-book", "incumbent"],
    )

    db = VendorDatabase(vendors=[vendor1, vendor2])

    assert db.total_vendors == 2
    assert len(db.vendors) == 2


def test_vendor_database_get_by_id():
    """Test retrieving vendor by ID."""
    caps = VendorCapabilities(
        sql_interface=True,
        open_table_format=OpenTableFormat.ICEBERG_NATIVE,
        deployment_models=[DeploymentModel.CLOUD],
        cloud_native=True,
        operational_complexity="low",
        team_size_required=TeamSize.LEAN,
        cost_model=CostModel.CONSUMPTION,
        cost_predictability="high",
        maturity=Maturity.PRODUCTION,
    )

    vendor = Vendor(
        id="amazon-athena",
        name="Amazon Athena",
        category=VendorCategory.QUERY_ENGINE,
        description="Serverless query service",
        capabilities=caps,
        evidence_source="book",
    )

    db = VendorDatabase(vendors=[vendor])

    found = db.get_by_id("amazon-athena")
    assert found is not None
    assert found.name == "Amazon Athena"

    not_found = db.get_by_id("non-existent")
    assert not_found is None


def test_vendor_database_get_by_category():
    """Test retrieving vendors by category."""
    caps = VendorCapabilities(
        sql_interface=True,
        open_table_format=OpenTableFormat.ICEBERG_NATIVE,
        deployment_models=[DeploymentModel.CLOUD],
        cloud_native=True,
        operational_complexity="low",
        team_size_required=TeamSize.LEAN,
        cost_model=CostModel.CONSUMPTION,
        cost_predictability="high",
        maturity=Maturity.PRODUCTION,
    )

    athena = Vendor(
        id="amazon-athena",
        name="Amazon Athena",
        category=VendorCategory.QUERY_ENGINE,
        description="Serverless query service",
        capabilities=caps,
        evidence_source="book",
    )

    splunk = Vendor(
        id="splunk",
        name="Splunk",
        category=VendorCategory.SIEM,
        description="SIEM platform",
        capabilities=caps,
        evidence_source="book",
    )

    db = VendorDatabase(vendors=[athena, splunk])

    query_engines = db.get_by_category(VendorCategory.QUERY_ENGINE)
    assert len(query_engines) == 1
    assert query_engines[0].id == "amazon-athena"

    siems = db.get_by_category(VendorCategory.SIEM)
    assert len(siems) == 1
    assert siems[0].id == "splunk"


def test_vendor_database_filter_by_tags():
    """Test filtering vendors by tags."""
    caps = VendorCapabilities(
        sql_interface=True,
        open_table_format=OpenTableFormat.ICEBERG_NATIVE,
        deployment_models=[DeploymentModel.CLOUD],
        cloud_native=True,
        operational_complexity="low",
        team_size_required=TeamSize.LEAN,
        cost_model=CostModel.CONSUMPTION,
        cost_predictability="high",
        maturity=Maturity.PRODUCTION,
    )

    vendor1 = Vendor(
        id="vendor1",
        name="Vendor 1",
        category=VendorCategory.QUERY_ENGINE,
        description="Test vendor 1",
        capabilities=caps,
        evidence_source="test",
        tags=["mentioned-in-book", "practitioner-recommended"],
    )

    vendor2 = Vendor(
        id="vendor2",
        name="Vendor 2",
        category=VendorCategory.SIEM,
        description="Test vendor 2",
        capabilities=caps,
        evidence_source="test",
        tags=["emerging"],
    )

    db = VendorDatabase(vendors=[vendor1, vendor2])

    book_mentioned = db.filter_by_tags(["mentioned-in-book"])
    assert len(book_mentioned) == 1
    assert book_mentioned[0].id == "vendor1"

    emerging = db.filter_by_tags(["emerging"])
    assert len(emerging) == 1
    assert emerging[0].id == "vendor2"


# ============================================================================
# DECISION STATE TESTS
# ============================================================================


def test_decision_state_minimal():
    """Test creating minimal decision state."""
    state = DecisionState(session_id="test-session-123")

    assert state.session_id == "test-session-123"
    assert state.interview_progress == 0
    assert state.interview_complete is False
    assert len(state.filtered_vendors) == 0


def test_decision_state_full():
    """Test creating fully populated decision state."""
    state = DecisionState(
        session_id="test-session-123",
        architect_context={"org": "ACME Corp", "industry": "finance"},
        team_size=TeamSize.LEAN,
        budget=BudgetRange.UNDER_500K,
        data_sovereignty=DataSovereignty.ON_PREM_ONLY,
        vendor_tolerance=VendorTolerance.OSS_WITH_SUPPORT,
        tier_1_requirements={"sql_interface": True, "streaming_query": False},
        tier_2_preferences={"open_format": 3, "streaming": 2, "ocsf": 1},
        filtered_vendors=["vendor1", "vendor2", "vendor3"],
        journey_match="jennifer",
        interview_progress=5,
    )

    assert state.team_size == TeamSize.LEAN
    assert state.budget == BudgetRange.UNDER_500K
    assert state.tier_1_requirements["sql_interface"] is True
    assert state.tier_2_preferences["open_format"] == 3
    assert len(state.filtered_vendors) == 3
    assert state.journey_match == "jennifer"


def test_decision_state_mark_vendor_eliminated():
    """Test marking vendor as eliminated."""
    state = DecisionState(
        session_id="test-session-123", filtered_vendors=["vendor1", "vendor2"]
    )

    state.mark_vendor_eliminated("vendor1", "Missing SQL interface (Tier 1 requirement)")

    assert "vendor1" in state.eliminated_vendors
    assert state.eliminated_vendors["vendor1"] == "Missing SQL interface (Tier 1 requirement)"
    assert "vendor1" not in state.filtered_vendors
    assert "vendor2" in state.filtered_vendors


def test_decision_state_update_progress():
    """Test updating interview progress."""
    state = DecisionState(session_id="test-session-123")

    assert state.interview_progress == 0
    assert state.interview_complete is False

    state.update_progress(5)
    assert state.interview_progress == 5
    assert state.interview_complete is False

    state.update_progress(12)
    assert state.interview_progress == 12
    assert state.interview_complete is True
