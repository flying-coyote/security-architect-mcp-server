#!/usr/bin/env python3
"""
Test script to invoke apply_foundational_filters with specific parameters.

Parameters:
- table_format='iceberg'
- catalog='polaris'
- transformation_strategy='dbt'
"""

import json
from src.utils.database_loader import load_default_database
from src.tools.filter_vendors import apply_foundational_filters


def main():
    print("=" * 80)
    print("FOUNDATIONAL ARCHITECTURE FILTERING TEST")
    print("=" * 80)
    print()

    # Load vendor database
    print("Loading vendor database...")
    vendor_db = load_default_database()
    print(f"✓ Loaded {vendor_db.total_vendors} vendors")
    print()

    # Apply foundational filters
    print("Applying foundational filters:")
    print("  - table_format: iceberg")
    print("  - catalog: polaris")
    print("  - transformation_strategy: dbt")
    print()

    filter_result = apply_foundational_filters(
        database=vendor_db,
        table_format='iceberg',
        catalog='polaris',
        transformation_strategy='dbt'
    )

    # Display summary
    print("=" * 80)
    print("FILTERING RESULTS")
    print("=" * 80)
    print(f"Summary: {filter_result.summary()}")
    print(f"  Initial count: {filter_result.initial_count}")
    print(f"  Filtered count: {filter_result.filtered_count}")
    print(f"  Eliminated count: {filter_result.eliminated_count}")
    print()

    # Display viable vendors
    print("=" * 80)
    print(f"VIABLE VENDORS ({filter_result.filtered_count})")
    print("=" * 80)
    for vendor in filter_result.filtered_vendors:
        print(f"\n{vendor.name} ({vendor.id})")
        print(f"  Category: {vendor.category.value}")
        print(f"  Description: {vendor.description}")
        print(f"  Cost Range: {vendor.typical_annual_cost_range}")
        print(f"  Iceberg Support: {vendor.capabilities.iceberg_support}")
        print(f"  Polaris Catalog: {vendor.capabilities.polaris_catalog_support}")
        print(f"  dbt Integration: {vendor.capabilities.dbt_integration}")
        print(f"  Tags: {', '.join(vendor.tags)}")

    # Display eliminated vendors
    print()
    print("=" * 80)
    print(f"ELIMINATED VENDORS ({filter_result.eliminated_count})")
    print("=" * 80)
    for vendor_id, reason in sorted(filter_result.eliminated_vendors.items()):
        # Get vendor name from database
        vendor = vendor_db.get_by_id(vendor_id)
        vendor_name = vendor.name if vendor else vendor_id
        print(f"\n{vendor_name} ({vendor_id})")
        print(f"  Reason: {reason}")

    # Export to JSON
    print()
    print("=" * 80)
    print("JSON OUTPUT")
    print("=" * 80)

    output = {
        "filters_applied": {
            "table_format": "iceberg",
            "catalog": "polaris",
            "transformation_strategy": "dbt",
            "query_engine_preference": None
        },
        "summary": filter_result.summary(),
        "initial_count": filter_result.initial_count,
        "filtered_count": filter_result.filtered_count,
        "eliminated_count": filter_result.eliminated_count,
        "viable_vendors": [
            {
                "id": v.id,
                "name": v.name,
                "category": v.category.value,
                "description": v.description,
                "cost_range": v.typical_annual_cost_range,
                "iceberg_support": v.capabilities.iceberg_support,
                "polaris_catalog_support": v.capabilities.polaris_catalog_support,
                "dbt_integration": v.capabilities.dbt_integration,
                "tags": v.tags
            }
            for v in filter_result.filtered_vendors
        ],
        "eliminated_vendors": filter_result.eliminated_vendors
    }

    print(json.dumps(output, indent=2))

    # Save to file
    output_file = "/home/user/security-architect-mcp-server/foundational_filter_results.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    print()
    print(f"✓ Results saved to: {output_file}")


if __name__ == "__main__":
    main()
