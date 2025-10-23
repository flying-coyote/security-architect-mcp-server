#!/usr/bin/env python3
"""
Sync vendor database from literature review to MCP server.

This script:
1. Loads vendor database from literature review repository
2. Validates evidence tier quality
3. Generates MCP-compatible vendor_database.json
4. Creates sync status report

Usage:
    python scripts/sync_from_literature_review.py

Output:
    - data/vendor_database.json (generated)
    - data/.last_sync (sync metadata)
    - data/INTEGRATION_STATUS.md (sync report)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class LiteratureReviewSync:
    """Sync vendor database from literature review to MCP server."""

    def __init__(
        self,
        lit_review_path: str = "~/security-data-literature-review",
        mcp_server_path: str = "~/security-architect-mcp-server"
    ):
        self.lit_review_path = Path(lit_review_path).expanduser()
        self.mcp_server_path = Path(mcp_server_path).expanduser()

        # Paths
        self.source_db_path = self.lit_review_path / "vendor-landscape" / "vendor-database.json"
        self.target_db_path = self.mcp_server_path / "data" / "vendor_database.json"
        self.sync_meta_path = self.mcp_server_path / "data" / ".last_sync"
        self.status_report_path = self.mcp_server_path / "data" / "INTEGRATION_STATUS.md"

        # Sync results
        self.vendors_synced = 0
        self.evidence_sources_total = 0
        self.tier_a_count = 0
        self.tier_b_count = 0
        self.tier_c_count = 0
        self.tier_d_count = 0
        self.warnings = []
        self.errors = []

    def run_sync(self) -> bool:
        """Run full sync workflow."""
        print("🔄 Starting Literature Review → MCP Server Sync...")
        print(f"📚 Source: {self.source_db_path}")
        print(f"🎯 Target: {self.target_db_path}\n")

        # Check if source exists
        if not self.source_db_path.exists():
            self.errors.append(f"Source vendor database not found: {self.source_db_path}")
            print(f"❌ ERROR: {self.errors[0]}")
            print("\n💡 TIP: The integrated vendor database hasn't been created yet.")
            print("   This is expected if you're still using the standalone MCP vendor database.")
            print("   To enable integration, create the master database in the literature review:")
            print(f"   {self.lit_review_path}/vendor-landscape/vendor-database.json\n")
            return False

        # Load source database
        print("📖 Loading source vendor database...")
        try:
            with open(self.source_db_path, 'r') as f:
                source_data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in source database: {e}")
            print(f"❌ ERROR: {self.errors[0]}")
            return False
        except Exception as e:
            self.errors.append(f"Failed to load source database: {e}")
            print(f"❌ ERROR: {self.errors[0]}")
            return False

        vendors = source_data.get("vendors", [])
        self.vendors_synced = len(vendors)
        print(f"✅ Loaded {self.vendors_synced} vendors\n")

        # Validate evidence tiers
        print("🔍 Validating evidence tier quality...")
        self.validate_evidence_tiers(vendors)

        # Calculate tier distribution
        tier_a_pct = (self.tier_a_count / max(1, self.evidence_sources_total)) * 100
        tier_b_pct = (self.tier_b_count / max(1, self.evidence_sources_total)) * 100

        print(f"📊 Evidence Tier Distribution:")
        print(f"   Tier A: {self.tier_a_count} ({tier_a_pct:.0f}%)")
        print(f"   Tier B: {self.tier_b_count} ({tier_b_pct:.0f}%)")
        print(f"   Tier C: {self.tier_c_count}")
        print(f"   Tier D: {self.tier_d_count}")
        print(f"   Total: {self.evidence_sources_total} evidence sources\n")

        # Check quality threshold
        if tier_a_pct < 70:
            self.warnings.append(f"Tier A evidence only {tier_a_pct:.0f}% (target: 70%+)")
            print(f"⚠️  WARNING: {self.warnings[-1]}\n")
        else:
            print(f"✅ Evidence quality meets target (70%+ Tier A)\n")

        # Generate MCP-compatible database
        print("🔨 Generating MCP-compatible vendor database...")
        mcp_data = self.generate_mcp_database(source_data)

        # Backup existing database if it exists
        if self.target_db_path.exists():
            backup_path = self.target_db_path.with_suffix('.json.backup')
            print(f"💾 Backing up existing database to {backup_path.name}...")
            with open(backup_path, 'w') as f:
                with open(self.target_db_path, 'r') as src:
                    f.write(src.read())

        # Write new database
        self.target_db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.target_db_path, 'w') as f:
            json.dump(mcp_data, f, indent=2)

        print(f"✅ Generated {self.target_db_path}\n")

        # Write sync metadata
        print("📝 Writing sync metadata...")
        self.write_sync_metadata(source_data)

        # Generate status report
        print("📄 Generating integration status report...")
        self.generate_status_report()

        # Summary
        print("\n" + "="*60)
        print("✅ SYNC COMPLETE")
        print("="*60)
        print(f"📦 Vendors Synced: {self.vendors_synced}")
        print(f"📊 Evidence Sources: {self.evidence_sources_total}")
        print(f"🟢 Tier A: {tier_a_pct:.0f}%")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"📄 Status Report: {self.status_report_path}")
        print("="*60 + "\n")

        return len(self.errors) == 0

    def validate_evidence_tiers(self, vendors: List[Dict]):
        """Validate evidence tier quality."""
        for vendor in vendors:
            # Check new evidence_sources format (vendor-level evidence)
            evidence_sources = vendor.get("evidence_sources", [])
            self.evidence_sources_total += len(evidence_sources)

            for source in evidence_sources:
                tier = source.get("evidence_tier", "unknown")
                if tier == "A":
                    self.tier_a_count += 1
                elif tier == "B":
                    self.tier_b_count += 1
                elif tier == "C":
                    self.tier_c_count += 1
                elif tier == "D":
                    self.tier_d_count += 1

            # Also check old format (capability-level evidence) for backwards compatibility
            caps = vendor.get("capabilities", {})

            for cap_name, cap_value in caps.items():
                if isinstance(cap_value, dict) and "evidence" in cap_value:
                    evidence = cap_value["evidence"]

                    if isinstance(evidence, dict):
                        # Count evidence sources
                        sources = evidence.get("sources", [])
                        self.evidence_sources_total += len(sources)

                        # Count by tier
                        for source in sources:
                            tier = source.get("evidence_tier", "unknown")
                            if tier == "A":
                                self.tier_a_count += 1
                            elif tier == "B":
                                self.tier_b_count += 1
                            elif tier == "C":
                                self.tier_c_count += 1
                            elif tier == "D":
                                self.tier_d_count += 1

                        # Validate high scores have good evidence
                        score = cap_value.get("score", 0)
                        tier = evidence.get("tier", "unknown")

                        if score >= 4 and tier not in ["A", "B"]:
                            warning = f"{vendor.get('id', 'unknown')}: {cap_name} score={score} has Tier {tier} evidence (should be A/B)"
                            if warning not in self.warnings:
                                self.warnings.append(warning)

    def generate_mcp_database(self, source_data: Dict) -> Dict:
        """Generate MCP-compatible database from source."""
        # Transform integrated schema → MCP schema
        mcp_data = {
            "vendors": [],
            "update_cadence": source_data.get("meta", {}).get("sync_cadence", "quarterly"),
            "last_full_update": source_data.get("meta", {}).get("last_updated", datetime.now().isoformat()),
            "total_vendors": source_data.get("meta", {}).get("vendor_count", 0)
        }

        # Transform each vendor
        for vendor in source_data.get("vendors", []):
            mcp_vendor = self.transform_vendor(vendor)
            mcp_data["vendors"].append(mcp_vendor)

        return mcp_data

    def transform_vendor(self, vendor: Dict) -> Dict:
        """Transform integrated vendor schema to MCP schema."""
        caps = vendor.get("capabilities", {})

        # Map category names
        category_map = {
            "OLAP/Analytics Engine": "Query Engine",
            "SIEM Platform": "SIEM",
            "Query Engine": "Query Engine"
        }
        original_category = vendor.get("category", "Other")
        mcp_category = category_map.get(original_category, original_category)

        # Map cost model values
        cost_model_map = {
            "oss": "open-source",
            "hybrid": "hybrid",
            "consumption": "consumption",
            "per-gb": "per-gb",
            "subscription": "subscription"
        }
        original_cost_model = caps.get("cost_model", "hybrid")
        mcp_cost_model = cost_model_map.get(original_cost_model, "hybrid")

        # Build MCP capabilities with required fields
        mcp_capabilities = {
            # Core query capabilities
            "sql_interface": caps.get("sql_interface", True),
            "streaming_query": caps.get("streaming_query", False),
            "multi_engine_query": False,

            # Data format and interoperability (REQUIRED)
            "open_table_format": "proprietary",  # Default for now
            "schema_evolution": False,

            # Deployment and infrastructure
            "deployment_models": caps.get("deployment_models", ["cloud"]),
            "cloud_native": True,  # Default assumption
            "multi_cloud": False,

            # Operational complexity
            "operational_complexity": caps.get("operational_complexity", "medium"),
            "managed_service_available": False,
            "team_size_required": caps.get("team_size_required", "standard"),

            # Cost and licensing (REQUIRED)
            "cost_model": mcp_cost_model,
            "cost_predictability": "medium",  # Default

            # Security-specific capabilities
            "siem_integration": False,
            "compliance_certifications": [],
            "data_governance": False,

            # Maturity and support
            "maturity": caps.get("maturity", "production"),
            "vendor_support": None,
            "community_size": "unknown",

            # Advanced capabilities
            "ocsf_support": False,
            "ml_analytics": False,
            "api_extensibility": False
        }

        # Build MCP vendor entry
        cost_modeling = vendor.get("cost_modeling", {})

        mcp_vendor = {
            "id": vendor.get("id"),
            "name": vendor.get("name"),
            "category": mcp_category,
            "description": vendor.get("description"),
            "website": vendor.get("website"),
            "capabilities": mcp_capabilities,
            "typical_annual_cost_range": cost_modeling.get("typical_annual_cost_range"),
            "cost_notes": cost_modeling.get("cost_notes"),
            "evidence_source": "literature-review",
            "evidence_sources": vendor.get("evidence_sources", []),  # Include vendor-level evidence
            "evidence_summary": vendor.get("evidence_summary", {}),  # Include evidence summary
            "last_updated": vendor.get("last_updated", datetime.now().isoformat()),
            "validated_by": vendor.get("evidence_summary", {}).get("validated_by"),
            "tags": vendor.get("tags", [])
        }

        return mcp_vendor

    def write_sync_metadata(self, source_data: Dict):
        """Write sync metadata file."""
        metadata = {
            "sync_timestamp": datetime.now().isoformat() + "Z",
            "source_version": source_data.get("sync_version", "unknown"),
            "source_path": str(self.source_db_path),
            "vendors_synced": self.vendors_synced,
            "evidence_sources_total": self.evidence_sources_total,
            "tier_a_percentage": (self.tier_a_count / max(1, self.evidence_sources_total)) * 100,
            "tier_b_percentage": (self.tier_b_count / max(1, self.evidence_sources_total)) * 100,
            "tier_c_percentage": (self.tier_c_count / max(1, self.evidence_sources_total)) * 100,
            "tier_d_percentage": (self.tier_d_count / max(1, self.evidence_sources_total)) * 100,
            "sync_status": "success" if len(self.errors) == 0 else "failed",
            "warnings": self.warnings,
            "errors": self.errors
        }

        with open(self.sync_meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Wrote sync metadata to {self.sync_meta_path.name}")

    def generate_status_report(self):
        """Generate integration status report."""
        tier_a_pct = (self.tier_a_count / max(1, self.evidence_sources_total)) * 100
        tier_b_pct = (self.tier_b_count / max(1, self.evidence_sources_total)) * 100

        report = f"""# MCP Server - Literature Review Integration Status

**Last Sync**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status**: {"✅ Success" if len(self.errors) == 0 else "❌ Failed"}

---

## Sync Summary

| Metric | Value |
|--------|-------|
| **Vendors Synced** | {self.vendors_synced} |
| **Evidence Sources** | {self.evidence_sources_total} |
| **Tier A Evidence** | {self.tier_a_count} ({tier_a_pct:.0f}%) |
| **Tier B Evidence** | {self.tier_b_count} ({tier_b_pct:.0f}%) |
| **Warnings** | {len(self.warnings)} |
| **Errors** | {len(self.errors)} |

---

## Evidence Quality

"""
        if tier_a_pct >= 70:
            report += f"✅ **Evidence quality meets target** ({tier_a_pct:.0f}% Tier A)\n\n"
        else:
            report += f"⚠️  **Evidence quality below target** ({tier_a_pct:.0f}% Tier A, target: 70%+)\n\n"

        # Warnings
        if self.warnings:
            report += f"""
## Warnings ({len(self.warnings)})

"""
            for warning in self.warnings[:10]:  # Limit to 10
                report += f"- ⚠️  {warning}\n"

            if len(self.warnings) > 10:
                report += f"\n_... and {len(self.warnings) - 10} more warnings_\n"
        else:
            report += "## Warnings\n\n_No warnings_\n"

        # Errors
        if self.errors:
            report += f"""
## Errors ({len(self.errors)})

"""
            for error in self.errors:
                report += f"- ❌ {error}\n"
        else:
            report += "\n## Errors\n\n_No errors_\n"

        # Integration info
        report += f"""
---

## Integration Details

**Source Database**: `{self.source_db_path}`
**Target Database**: `{self.target_db_path}`
**Sync Metadata**: `{self.sync_meta_path}`

---

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Script**: `scripts/sync_from_literature_review.py`
"""

        with open(self.status_report_path, 'w') as f:
            f.write(report)

        print(f"✅ Generated status report: {self.status_report_path.name}")


def main():
    """Run sync."""
    syncer = LiteratureReviewSync()
    success = syncer.run_sync()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
