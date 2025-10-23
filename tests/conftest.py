"""
Pytest configuration and fixtures for MCP Server tests.

Provides dynamic vendor count detection to support both:
- Integrated database (3 vendors from literature review)
- Standalone database (64 vendors)
"""

import pytest
from src.utils.database_loader import load_default_database


@pytest.fixture(scope="session")
def vendor_db():
    """Load vendor database once per test session."""
    return load_default_database()


@pytest.fixture(scope="session")
def expected_vendor_count(vendor_db):
    """
    Get expected vendor count from actual database.

    This allows tests to work with both:
    - Integrated database (3 vendors from literature review)
    - Standalone database (64 vendors)
    """
    return vendor_db.total_vendors


@pytest.fixture(scope="session")
def is_integrated_database(vendor_db):
    """Check if using integrated literature review database."""
    if not vendor_db.vendors:
        return False
    # Integrated database has evidence_source="literature-review"
    return vendor_db.vendors[0].evidence_source == "literature-review"


@pytest.fixture(scope="session")
def available_vendor_ids(vendor_db):
    """Get list of all vendor IDs in database."""
    return [v.id for v in vendor_db.vendors]
