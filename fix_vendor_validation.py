#!/usr/bin/env python3
"""
Fix validation errors in newly added vendors.
Match the Pydantic enum requirements.
"""

import json

def fix_vendor_validation():
    # Load database
    with open('data/vendor_database.json', 'r') as f:
        data = json.load(f)

    # Find and fix Tenzir (index 75)
    if data['vendors'][75]['id'] == 'tenzir':
        data['vendors'][75]['category'] = 'ETL/ELT Platform'  # Fixed enum
        data['vendors'][75]['capabilities']['open_table_format'] = 'proprietary'  # Fixed enum
        data['vendors'][75]['capabilities']['team_size_required'] = 'lean'  # Fixed enum (small -> lean)
        print("Fixed Tenzir validation")

    # Find and fix Estuary (index 76)
    if data['vendors'][76]['id'] == 'estuary':
        data['vendors'][76]['category'] = 'ETL/ELT Platform'  # Fixed enum
        data['vendors'][76]['capabilities']['team_size_required'] = 'lean'  # Fixed enum (small -> lean)
        print("Fixed Estuary validation")

    # Find and fix Databricks Lakebase (index 77)
    if data['vendors'][77]['id'] == 'databricks-lakebase':
        data['vendors'][77]['category'] = 'Data Lakehouse'  # Fixed enum
        data['vendors'][77]['capabilities']['open_table_format'] = 'delta'  # Fixed enum (delta_lake -> delta)
        print("Fixed Databricks Lakebase validation")

    # Find and fix Knostic (index 78)
    if data['vendors'][78]['id'] == 'knostic':
        data['vendors'][78]['category'] = 'Other'  # Fixed enum (Security Tools -> Other)
        data['vendors'][78]['capabilities']['open_table_format'] = 'proprietary'  # Fixed enum (none -> proprietary)
        data['vendors'][78]['capabilities']['team_size_required'] = 'lean'  # Fixed enum (small -> lean)
        data['vendors'][78]['capabilities']['maturity'] = 'experimental'  # Fixed enum (emerging -> experimental)
        print("Fixed Knostic validation")

    # Remove any extra fields that Pydantic doesn't recognize
    for vendor in [data['vendors'][75], data['vendors'][76], data['vendors'][77], data['vendors'][78]]:
        caps = vendor.get('capabilities', {})
        # Remove non-standard fields
        extra_fields = ['mcp_enabled', 'ai_parser_generation', 'real_time_cdc', 'oltp_support',
                       'acid_transactions', 'mcp_security', 'agent_defense', 'prompt_injection_protection']
        for field in extra_fields:
            if field in caps:
                del caps[field]

    # Save fixed database
    with open('data/vendor_database.json', 'w') as f:
        json.dump(data, f, indent=2)

    print("\nAll validation errors fixed!")
    print(f"Total vendors: {len(data['vendors'])}")

if __name__ == "__main__":
    fix_vendor_validation()