"""
Utility functions for loading and managing the vendor database.
"""

import json
from pathlib import Path
from typing import Any

from src.models import Vendor, VendorDatabase


def load_vendor_database(database_path: str | Path) -> VendorDatabase:
    """
    Load vendor database from JSON file.

    Args:
        database_path: Path to vendor_database.json file

    Returns:
        VendorDatabase instance with all vendors loaded

    Raises:
        FileNotFoundError: If database file doesn't exist
        json.JSONDecodeError: If JSON is malformed
        ValidationError: If vendor data doesn't match schema
    """
    path = Path(database_path)

    if not path.exists():
        raise FileNotFoundError(f"Vendor database not found at {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Pydantic will validate the data structure
    return VendorDatabase(**data)


def save_vendor_database(database: VendorDatabase, output_path: str | Path) -> None:
    """
    Save vendor database to JSON file.

    Args:
        database: VendorDatabase instance to save
        output_path: Path where JSON should be written
    """
    path = Path(output_path)

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to dict and write as JSON
    with open(path, "w", encoding="utf-8") as f:
        # Use model_dump() to convert Pydantic model to dict
        # exclude_none=False to preserve null values
        # by_alias=False to use field names, not aliases
        data = database.model_dump(mode="json")
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_default_database_path() -> Path:
    """
    Get the default path to the vendor database.

    Returns:
        Path to data/vendor_database.json relative to project root
    """
    # This file is in src/utils/, so go up two levels to project root
    project_root = Path(__file__).parent.parent.parent
    return project_root / "data" / "vendor_database.json"


def load_default_database() -> VendorDatabase:
    """
    Load vendor database from default location (data/vendor_database.json).

    Returns:
        VendorDatabase instance

    Raises:
        FileNotFoundError: If database file doesn't exist
    """
    return load_vendor_database(get_default_database_path())
