"""
Tests for database loader utility functions.
"""

import json
from pathlib import Path

import pytest

from src.models import VendorCategory, VendorDatabase
from src.utils.database_loader import (
    get_default_database_path,
    load_default_database,
    load_vendor_database,
    save_vendor_database,
)


def test_get_default_database_path():
    """Test that default database path is correct."""
    path = get_default_database_path()

    assert path.name == "vendor_database.json"
    assert path.parent.name == "data"
    assert path.exists()


def test_load_vendor_database():
    """Test loading vendor database from file."""
    db_path = get_default_database_path()
    db = load_vendor_database(db_path)

    assert isinstance(db, VendorDatabase)
    assert db.total_vendors == 54
    assert len(db.vendors) == 54
    assert db.update_cadence == "quarterly"


def test_load_default_database():
    """Test loading vendor database from default location."""
    db = load_default_database()

    assert isinstance(db, VendorDatabase)
    assert db.total_vendors == 54
    assert len(db.vendors) == 54


def test_load_vendor_database_not_found():
    """Test that loading non-existent database raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_vendor_database("nonexistent.json")


def test_all_vendors_have_required_fields():
    """Test that all vendors in database have required fields."""
    db = load_default_database()

    for vendor in db.vendors:
        # Check required fields
        assert vendor.id
        assert vendor.name
        assert vendor.category
        assert vendor.description
        assert vendor.capabilities
        assert vendor.evidence_source

        # Check ID format (lowercase-hyphenated)
        assert vendor.id.islower()
        assert " " not in vendor.id

        # Check capabilities
        assert vendor.capabilities.sql_interface is not None
        assert vendor.capabilities.open_table_format
        assert len(vendor.capabilities.deployment_models) > 0
        assert vendor.capabilities.cloud_native is not None
        assert vendor.capabilities.operational_complexity in ["low", "medium", "high"]
        assert vendor.capabilities.team_size_required
        assert vendor.capabilities.cost_model
        assert vendor.capabilities.cost_predictability in ["low", "medium", "high"]
        assert vendor.capabilities.maturity


def test_vendor_categories_distribution():
    """Test that we have vendors across multiple categories."""
    db = load_default_database()

    categories = {vendor.category for vendor in db.vendors}

    # We should have at least 3 different categories
    assert len(categories) >= 3

    # Check specific categories exist
    assert VendorCategory.SIEM in categories
    assert VendorCategory.QUERY_ENGINE in categories


def test_specific_vendors_exist():
    """Test that core 10 initial vendors exist in database."""
    db = load_default_database()

    # Check that original 10 vendors are present
    expected_vendors = {
        "amazon-athena",
        "dremio",
        "splunk-enterprise-security",
        "starburst",
        "denodo",
        "snowflake",
        "databricks",
        "elastic-security",
        "ibm-qradar",
        "microsoft-sentinel",
    }

    actual_vendors = {vendor.id for vendor in db.vendors}

    # Original 10 should be subset of all 24
    assert expected_vendors.issubset(actual_vendors)
    assert len(actual_vendors) == 54


def test_amazon_athena_details():
    """Test Amazon Athena vendor has correct details."""
    db = load_default_database()
    athena = db.get_by_id("amazon-athena")

    assert athena is not None
    assert athena.name == "Amazon Athena"
    assert athena.category == VendorCategory.QUERY_ENGINE
    assert athena.capabilities.sql_interface is True
    assert athena.capabilities.open_table_format.value == "iceberg-native"
    assert athena.capabilities.cloud_native is True
    assert athena.capabilities.operational_complexity == "low"
    assert athena.capabilities.team_size_required.value == "lean"
    assert athena.capabilities.cost_model.value == "consumption"
    assert "mentioned-in-book" in athena.tags


def test_splunk_details():
    """Test Splunk vendor has correct details."""
    db = load_default_database()
    splunk = db.get_by_id("splunk-enterprise-security")

    assert splunk is not None
    assert splunk.name == "Splunk Enterprise Security"
    assert splunk.category == VendorCategory.SIEM
    assert splunk.capabilities.sql_interface is False  # Splunk uses SPL, not SQL
    assert splunk.capabilities.streaming_query is True
    assert splunk.capabilities.operational_complexity == "high"
    assert splunk.capabilities.team_size_required.value == "large"
    assert splunk.capabilities.cost_model.value == "per-gb"
    assert "incumbent" in splunk.tags


def test_save_and_load_roundtrip(tmp_path):
    """Test saving and loading database preserves data."""
    # Load original database
    db_original = load_default_database()

    # Save to temp file
    temp_db_path = tmp_path / "test_vendor_database.json"
    save_vendor_database(db_original, temp_db_path)

    # Load from temp file
    db_loaded = load_vendor_database(temp_db_path)

    # Compare
    assert db_loaded.total_vendors == db_original.total_vendors
    assert len(db_loaded.vendors) == len(db_original.vendors)

    # Check first vendor matches
    assert db_loaded.vendors[0].id == db_original.vendors[0].id
    assert db_loaded.vendors[0].name == db_original.vendors[0].name


def test_database_json_is_valid():
    """Test that the database JSON file is well-formed."""
    db_path = get_default_database_path()

    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check top-level structure
    assert "vendors" in data
    assert "update_cadence" in data
    assert "last_full_update" in data
    assert "total_vendors" in data

    # Check vendor structure
    assert isinstance(data["vendors"], list)
    assert len(data["vendors"]) == 54

    # Check first vendor has expected fields
    vendor = data["vendors"][0]
    assert "id" in vendor
    assert "name" in vendor
    assert "category" in vendor
    assert "capabilities" in vendor
