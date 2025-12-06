#!/usr/bin/env python3
"""
Add volume capacity context to vendor costs in the database.
Maps cost ranges to expected data volumes based on vendor category and tier.
"""

import json
import re

def parse_cost_range(cost_str):
    """Extract min and max costs from a cost string."""
    # Remove common words
    cost_str = cost_str.replace('annually', '').replace('infrastructure costs', '')
    cost_str = cost_str.replace('storage costs', '').replace('for managed service', '')
    cost_str = cost_str.replace('infrastructure only', '').replace('(', '').replace(')', '')

    # Extract numbers
    numbers = re.findall(r'(\d+)K', cost_str)
    if not numbers:
        numbers = re.findall(r'(\d+(?:\.\d+)?)M', cost_str)
        if numbers:
            numbers = [float(n) * 1000 for n in numbers]
    else:
        numbers = [int(n) for n in numbers]

    if len(numbers) >= 2:
        return min(numbers), max(numbers)
    elif len(numbers) == 1:
        return numbers[0], numbers[0] * 3
    else:
        return 50, 500  # Default range

def get_volume_tier(min_cost, max_cost, category):
    """
    Determine appropriate volume tier based on cost and category.
    Returns a volume string like "1TB/day" or "100GB-1TB/day"
    """

    # Category-specific volume mappings
    if category == "SIEM":
        if min_cost < 200:
            return "100GB/day"
        elif min_cost < 500:
            return "500GB/day"
        elif min_cost < 1000:
            return "1TB/day"
        elif min_cost < 3000:
            return "5TB/day"
        else:
            return "10TB/day"

    elif category == "Query Engine":
        if min_cost < 100:
            return "1-5TB/day"
        elif min_cost < 300:
            return "5-10TB/day"
        elif min_cost < 800:
            return "10-50TB/day"
        else:
            return "50-100TB/day"

    elif category == "Data Lakehouse":
        if min_cost < 100:
            return "1-10TB/day"
        elif min_cost < 500:
            return "10-50TB/day"
        else:
            return "50-100TB/day"

    elif category == "ETL/ELT Platform":
        if min_cost < 50:
            return "100GB-1TB/day"
        elif min_cost < 200:
            return "1-5TB/day"
        elif min_cost < 500:
            return "5-10TB/day"
        else:
            return "10-50TB/day"

    elif category == "Streaming Platform":
        if min_cost < 100:
            return "1TB/day events"
        elif min_cost < 300:
            return "5TB/day events"
        elif min_cost < 600:
            return "10TB/day events"
        else:
            return "50TB/day events"

    elif category == "Object Storage":
        if min_cost < 50:
            return "100TB total"
        elif min_cost < 200:
            return "500TB total"
        elif min_cost < 500:
            return "1PB total"
        else:
            return "5PB total"

    elif category == "Data Catalog & Governance":
        if min_cost < 100:
            return "1000 tables"
        elif min_cost < 300:
            return "10K tables"
        else:
            return "100K+ tables"

    else:  # Default for other categories
        if min_cost < 100:
            return "1TB/day"
        elif min_cost < 500:
            return "5TB/day"
        else:
            return "10TB/day"

def add_volume_context(vendor):
    """Add volume context to a vendor's cost if it doesn't already have it."""

    cost = vendor.get('typical_annual_cost_range', '')

    # Check if volume context already exists
    volume_patterns = ['/day', '/month', 'GB', 'TB', 'PB', 'tables']
    if any(pattern in cost for pattern in volume_patterns):
        return vendor  # Already has volume context

    # Parse cost range
    min_cost, max_cost = parse_cost_range(cost)

    # Get volume tier
    volume_tier = get_volume_tier(min_cost, max_cost, vendor['category'])

    # Create new cost string with volume context
    if 'infrastructure' in cost.lower():
        base_cost = re.sub(r'\s*\(?infrastructure.*\)?', '', cost, flags=re.IGNORECASE).strip()
        new_cost = f"{base_cost} for {volume_tier} (infrastructure)"
    elif 'storage' in cost.lower():
        base_cost = re.sub(r'\s*\(?storage.*\)?', '', cost, flags=re.IGNORECASE).strip()
        new_cost = f"{base_cost} for {volume_tier} (storage)"
    elif 'managed service' in cost.lower():
        base_cost = re.sub(r'for managed service', '', cost, flags=re.IGNORECASE).strip()
        new_cost = f"{base_cost} for {volume_tier} (managed)"
    else:
        # Add volume context
        base_cost = cost.replace('annually', '').strip()
        new_cost = f"{base_cost} for {volume_tier}"

    vendor['typical_annual_cost_range'] = new_cost

    # Also add a structured volume_capacity field
    vendor['volume_capacity'] = volume_tier

    return vendor

def main():
    # Load vendor database
    with open('data/vendor_database.json', 'r') as f:
        data = json.load(f)

    # Update vendors
    updated_count = 0
    for vendor in data['vendors']:
        original_cost = vendor.get('typical_annual_cost_range', '')
        updated_vendor = add_volume_context(vendor)
        if updated_vendor['typical_annual_cost_range'] != original_cost:
            updated_count += 1
            print(f"✓ {vendor['name']}:")
            print(f"  Before: {original_cost}")
            print(f"  After:  {updated_vendor['typical_annual_cost_range']}")

    # Save updated database
    with open('data/vendor_database.json', 'w') as f:
        json.dump(data, f, indent=2)

    # Also update the web tool database
    with open('docs/vendor_database.json', 'r') as f:
        web_data = json.load(f)

    # Create a lookup of updated vendors
    vendor_lookup = {v['id']: v for v in data['vendors']}

    # Update web vendors
    for vendor in web_data['vendors']:
        if vendor['id'] in vendor_lookup:
            vendor['typical_annual_cost_range'] = vendor_lookup[vendor['id']]['typical_annual_cost_range']
            if 'volume_capacity' in vendor_lookup[vendor['id']]:
                vendor['volume_capacity'] = vendor_lookup[vendor['id']]['volume_capacity']

    # Save updated web database
    with open('docs/vendor_database.json', 'w') as f:
        json.dump(web_data, f, indent=2)

    print(f"\n✅ Updated {updated_count} vendors with volume context")
    print("✅ Both MCP and web databases updated")

if __name__ == '__main__':
    main()