#!/usr/bin/env python3
"""
MCP Server - Weekly Health Check

Automated maintenance script to check MCP server health:
- Test suite status (must be 100% passing)
- Vendor database sync status
- Evidence tier quality
- Integration with literature review
- Code coverage metrics
- Schema validation

Run weekly via cron to maintain MCP server quality.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class HealthCheckResult:
    """Results from health check."""

    timestamp: str
    status: str  # "healthy", "warning", "critical"
    checks_passed: int = 0
    checks_failed: int = 0
    checks_warning: int = 0

    # Test metrics
    tests_total: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    coverage_percentage: float = 0.0

    # Vendor database metrics
    vendor_count: int = 0
    vendors_with_evidence_tiers: int = 0
    tier_a_percentage: float = 0.0
    sync_status: str = "unknown"
    days_since_sync: int = 0

    # Integration status
    lit_review_integration: bool = False
    last_sync_version: str = ""

    # Issues
    failing_tests: List[str] = field(default_factory=list)
    schema_errors: List[str] = field(default_factory=list)
    evidence_quality_issues: List[str] = field(default_factory=list)

    # Git status
    uncommitted_changes: int = 0
    last_commit_date: str = ""
    days_since_commit: int = 0


class MCPServerHealthCheck:
    """Weekly health check for MCP server."""

    def __init__(self, repo_path: str = "~/security-architect-mcp-server"):
        self.repo_path = Path(repo_path).expanduser()
        self.result = HealthCheckResult(
            timestamp=datetime.now().isoformat(),
            status="healthy"
        )

    def run_all_checks(self) -> HealthCheckResult:
        """Run all health checks."""
        print("🏥 Running MCP Server Health Check...")
        print(f"📁 Repository: {self.repo_path}")
        print(f"🕐 Timestamp: {self.result.timestamp}\n")

        # Core health checks
        self.check_git_status()
        self.check_test_suite()
        self.check_vendor_database()
        self.check_evidence_tier_quality()
        self.check_integration_status()
        self.check_schema_validation()

        # Calculate overall status
        self.calculate_overall_status()

        return self.result

    def check_git_status(self):
        """Check git repository status."""
        print("📊 Checking Git Status...")

        try:
            os.chdir(self.repo_path)

            # Check for uncommitted changes
            status_output = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            uncommitted = len(status_output.stdout.strip().split('\n')) if status_output.stdout.strip() else 0
            self.result.uncommitted_changes = uncommitted

            # Get last commit date
            last_commit_output = subprocess.run(
                ["git", "log", "-1", "--format=%ci"],
                capture_output=True,
                text=True,
                check=True
            )
            last_commit_str = last_commit_output.stdout.strip()
            if last_commit_str:
                last_commit_date = datetime.fromisoformat(last_commit_str.rsplit(' ', 1)[0])
                self.result.last_commit_date = last_commit_date.strftime("%Y-%m-%d")
                self.result.days_since_commit = (datetime.now() - last_commit_date).days

            # Warnings
            if uncommitted > 0:
                self.result.checks_warning += 1
                print(f"  ⚠️  {uncommitted} uncommitted changes")
            else:
                self.result.checks_passed += 1
                print(f"  ✅ No uncommitted changes")

            if self.result.days_since_commit > 14:  # MCP should be more active
                self.result.checks_warning += 1
                print(f"  ⚠️  Last commit {self.result.days_since_commit} days ago")
            else:
                self.result.checks_passed += 1
                print(f"  ✅ Last commit {self.result.days_since_commit} days ago")

        except subprocess.CalledProcessError as e:
            self.result.checks_failed += 1
            print(f"  ❌ Git check failed: {e}")

    def check_test_suite(self):
        """Run pytest and check results."""
        print("\n🧪 Checking Test Suite...")

        try:
            # Activate venv and run pytest
            venv_python = self.repo_path / "venv" / "bin" / "python"
            if not venv_python.exists():
                venv_python = sys.executable  # Fallback to current Python

            # Run pytest with JSON report
            result = subprocess.run(
                [str(venv_python), "-m", "pytest", "tests/", "-v", "--tb=no", "-q"],
                capture_output=True,
                text=True,
                cwd=self.repo_path
            )

            # Parse pytest output
            output = result.stdout + result.stderr

            # Extract test counts (e.g., "177 passed, 1 failed")
            import re
            passed_match = re.search(r'(\d+) passed', output)
            failed_match = re.search(r'(\d+) failed', output)

            self.result.tests_passed = int(passed_match.group(1)) if passed_match else 0
            self.result.tests_failed = int(failed_match.group(1)) if failed_match else 0
            self.result.tests_total = self.result.tests_passed + self.result.tests_failed

            # Extract failing test names
            if self.result.tests_failed > 0:
                failed_tests = re.findall(r'FAILED\s+([\w/:.]+)', output)
                self.result.failing_tests = failed_tests

            # Check coverage if available
            if "TOTAL" in output and "%" in output:
                coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
                if coverage_match:
                    self.result.coverage_percentage = float(coverage_match.group(1))

            # Status check
            if self.result.tests_failed == 0:
                self.result.checks_passed += 1
                print(f"  ✅ All {self.result.tests_total} tests passing")
            else:
                self.result.checks_failed += 1
                print(f"  ❌ {self.result.tests_failed}/{self.result.tests_total} tests failing")
                for test in self.result.failing_tests[:5]:  # Show first 5
                    print(f"     - {test}")

            # Coverage check
            if self.result.coverage_percentage >= 85:
                self.result.checks_passed += 1
                print(f"  ✅ Code coverage: {self.result.coverage_percentage}%")
            elif self.result.coverage_percentage >= 70:
                self.result.checks_warning += 1
                print(f"  ⚠️  Code coverage: {self.result.coverage_percentage}% (target: 85%)")
            else:
                self.result.checks_failed += 1
                print(f"  ❌ Code coverage: {self.result.coverage_percentage}% (critical: <70%)")

        except Exception as e:
            self.result.checks_failed += 1
            print(f"  ❌ Test suite check failed: {e}")

    def check_vendor_database(self):
        """Check vendor database status."""
        print("\n🏢 Checking Vendor Database...")

        vendor_db_path = self.repo_path / "data" / "vendor_database.json"

        if not vendor_db_path.exists():
            self.result.checks_failed += 1
            print(f"  ❌ Vendor database not found")
            return

        try:
            with open(vendor_db_path, 'r') as f:
                data = json.load(f)

            vendors = data.get("vendors", [])
            self.result.vendor_count = len(vendors)

            # Check for evidence tier fields (post-integration)
            vendors_with_tiers = sum(
                1 for v in vendors
                if "capabilities" in v and
                any("evidence" in str(cap) for cap in v["capabilities"].values() if isinstance(cap, dict))
            )
            self.result.vendors_with_evidence_tiers = vendors_with_tiers

            # Calculate tier A percentage (if integrated)
            tier_a_count = 0
            total_evidence = 0

            for vendor in vendors:
                caps = vendor.get("capabilities", {})
                for cap_name, cap_value in caps.items():
                    if isinstance(cap_value, dict) and "evidence" in cap_value:
                        evidence = cap_value["evidence"]
                        if isinstance(evidence, dict) and "tier" in evidence:
                            total_evidence += 1
                            if evidence["tier"] == "A":
                                tier_a_count += 1

            if total_evidence > 0:
                self.result.tier_a_percentage = (tier_a_count / total_evidence) * 100

            # Status checks
            if self.result.vendor_count >= 64:
                self.result.checks_passed += 1
                print(f"  ✅ Vendor count: {self.result.vendor_count}")
            else:
                self.result.checks_warning += 1
                print(f"  ⚠️  Vendor count: {self.result.vendor_count} (target: 64+)")

            # Evidence tier quality (if integrated)
            if vendors_with_tiers > 0:
                integration_pct = (vendors_with_tiers / len(vendors)) * 100
                if integration_pct >= 90:
                    self.result.checks_passed += 1
                    print(f"  ✅ Evidence tier integration: {integration_pct:.0f}%")
                else:
                    self.result.checks_warning += 1
                    print(f"  ⚠️  Evidence tier integration: {integration_pct:.0f}% (target: 90%+)")

                if self.result.tier_a_percentage >= 70:
                    self.result.checks_passed += 1
                    print(f"  ✅ Tier A evidence: {self.result.tier_a_percentage:.0f}%")
                else:
                    self.result.checks_warning += 1
                    print(f"  ⚠️  Tier A evidence: {self.result.tier_a_percentage:.0f}% (target: 70%+)")

        except json.JSONDecodeError as e:
            self.result.checks_failed += 1
            print(f"  ❌ Invalid JSON in vendor database: {e}")
        except Exception as e:
            self.result.checks_failed += 1
            print(f"  ❌ Vendor database check failed: {e}")

    def check_evidence_tier_quality(self):
        """Check evidence tier quality standards."""
        print("\n📊 Checking Evidence Tier Quality...")

        vendor_db_path = self.repo_path / "data" / "vendor_database.json"
        if not vendor_db_path.exists():
            return

        try:
            with open(vendor_db_path, 'r') as f:
                data = json.load(f)

            vendors = data.get("vendors", [])
            issues = []

            for vendor in vendors:
                vendor_id = vendor.get("id", "unknown")
                caps = vendor.get("capabilities", {})

                for cap_name, cap_value in caps.items():
                    # Check scores 4-5 have proper evidence
                    if isinstance(cap_value, dict):
                        score = cap_value.get("score", 0)
                        evidence = cap_value.get("evidence", {})

                        if score >= 4:
                            # High scores should have evidence
                            if not evidence or not isinstance(evidence, dict):
                                issues.append(f"{vendor_id}: {cap_name} score={score} lacks evidence")
                            elif evidence.get("tier") not in ["A", "B"]:
                                issues.append(f"{vendor_id}: {cap_name} score={score} has Tier {evidence.get('tier', 'unknown')} (need A/B)")
                            elif not evidence.get("sources"):
                                issues.append(f"{vendor_id}: {cap_name} score={score} lacks evidence sources")

            self.result.evidence_quality_issues = issues[:20]  # Limit to 20

            if not issues:
                self.result.checks_passed += 1
                print(f"  ✅ No evidence quality issues")
            elif len(issues) <= 5:
                self.result.checks_warning += 1
                print(f"  ⚠️  {len(issues)} evidence quality issues")
            else:
                self.result.checks_failed += 1
                print(f"  ❌ {len(issues)} evidence quality issues (showing first 5):")
                for issue in issues[:5]:
                    print(f"     - {issue}")

        except Exception as e:
            print(f"  ⚠️  Evidence tier quality check skipped: {e}")

    def check_integration_status(self):
        """Check literature review integration status."""
        print("\n🔗 Checking Literature Review Integration...")

        # Check for .last_sync file
        sync_file = self.repo_path / "data" / ".last_sync"

        if sync_file.exists():
            try:
                with open(sync_file, 'r') as f:
                    sync_data = json.load(f)

                self.result.lit_review_integration = True
                self.result.last_sync_version = sync_data.get("source_version", "unknown")
                sync_timestamp_str = sync_data.get("sync_timestamp", "")

                if sync_timestamp_str:
                    sync_timestamp = datetime.fromisoformat(sync_timestamp_str.replace('Z', '+00:00'))
                    self.result.days_since_sync = (datetime.now() - sync_timestamp.replace(tzinfo=None)).days

                self.result.checks_passed += 1
                print(f"  ✅ Integrated with literature review")
                print(f"     Version: {self.result.last_sync_version}")
                print(f"     Last sync: {self.result.days_since_sync} days ago")

                # Warn if sync is old
                if self.result.days_since_sync > 90:  # More than a quarter
                    self.result.checks_warning += 1
                    print(f"  ⚠️  Sync overdue (>90 days)")

            except Exception as e:
                self.result.checks_warning += 1
                print(f"  ⚠️  Integration status unclear: {e}")
        else:
            self.result.checks_warning += 1
            print(f"  ⚠️  Literature review integration pending")
            print(f"     Expected: data/.last_sync file")

    def check_schema_validation(self):
        """Validate vendor database schema."""
        print("\n✅ Checking Schema Validation...")

        # This would run Pydantic validation or JSON schema validation
        # Placeholder for now
        print(f"  ℹ️  Schema validation: TODO (implement with Pydantic)")

    def calculate_overall_status(self):
        """Calculate overall health status."""
        if self.result.checks_failed > 0:
            self.result.status = "critical"
        elif self.result.checks_warning > 3:
            self.result.status = "warning"
        else:
            self.result.status = "healthy"

    def generate_report(self, output_path: Path) -> str:
        """Generate markdown health report."""
        report = f"""# MCP Server - Weekly Health Check

**Date**: {datetime.fromisoformat(self.result.timestamp).strftime('%Y-%m-%d %H:%M:%S')}
**Status**: {self.result.status.upper()} {"🟢" if self.result.status == "healthy" else "🟡" if self.result.status == "warning" else "🔴"}

---

## Summary

| Metric | Value |
|--------|-------|
| ✅ Checks Passed | {self.result.checks_passed} |
| ⚠️ Checks Warning | {self.result.checks_warning} |
| ❌ Checks Failed | {self.result.checks_failed} |
| 🧪 Tests Passing | {self.result.tests_passed}/{self.result.tests_total} |
| 📊 Code Coverage | {self.result.coverage_percentage}% |
| 🏢 Vendor Count | {self.result.vendor_count} |
| 📅 Last Commit | {self.result.last_commit_date} ({self.result.days_since_commit} days ago) |

---

## Test Suite Status

"""
        if self.result.tests_failed == 0:
            report += f"✅ **All {self.result.tests_total} tests passing**\n\n"
        else:
            report += f"❌ **{self.result.tests_failed}/{self.result.tests_total} tests failing**\n\n"
            if self.result.failing_tests:
                report += "**Failing Tests**:\n"
                for test in self.result.failing_tests:
                    report += f"- `{test}`\n"

        report += f"""
---

## Vendor Database Status

- **Total Vendors**: {self.result.vendor_count}
- **With Evidence Tiers**: {self.result.vendors_with_evidence_tiers} ({self.result.vendors_with_evidence_tiers / max(1, self.result.vendor_count) * 100:.0f}%)
- **Tier A Evidence**: {self.result.tier_a_percentage:.0f}%
- **Integration Status**: {"✅ Integrated" if self.result.lit_review_integration else "⚠️ Pending"}

"""
        if self.result.lit_review_integration:
            report += f"""
**Literature Review Sync**:
- Version: {self.result.last_sync_version}
- Last Sync: {self.result.days_since_sync} days ago

"""

        report += f"""
---

## Evidence Quality Issues ({len(self.result.evidence_quality_issues)})

"""
        if self.result.evidence_quality_issues:
            for issue in self.result.evidence_quality_issues[:10]:
                report += f"- ⚠️ {issue}\n"
        else:
            report += "_No evidence quality issues detected_\n"

        report += f"""
---

## Recommendations

"""
        # Generate actionable recommendations
        if self.result.tests_failed > 0:
            report += f"- 🧪 **CRITICAL**: Fix {self.result.tests_failed} failing tests before next deployment\n"

        if self.result.coverage_percentage < 85:
            report += f"- 📊 **Action**: Improve code coverage to 85%+ (current: {self.result.coverage_percentage}%)\n"

        if self.result.vendor_count < 64:
            report += f"- 🏢 **Action**: Add more vendors to database (current: {self.result.vendor_count}, target: 64+)\n"

        if not self.result.lit_review_integration:
            report += f"- 🔗 **Action**: Complete literature review integration\n"

        if self.result.days_since_sync > 90:
            report += f"- 📅 **Action**: Sync with literature review (last sync: {self.result.days_since_sync} days ago)\n"

        if len(self.result.evidence_quality_issues) > 10:
            report += f"- 📊 **Action**: Address {len(self.result.evidence_quality_issues)} evidence quality issues\n"

        if not any([self.result.tests_failed, self.result.coverage_percentage < 85, not self.result.lit_review_integration]):
            report += "_No critical actions needed - MCP server healthy! 🎉_\n"

        report += f"""
---

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Script**: `scripts/weekly_health_check.py`
"""

        # Write report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report)

        return report


def main():
    """Run weekly health check."""
    checker = MCPServerHealthCheck()
    result = checker.run_all_checks()

    # Generate report
    report_dir = Path("~/weekly-review-reports").expanduser()
    report_path = report_dir / f"{datetime.now().strftime('%Y-%m-%d')}-mcp-server-health.md"

    report_content = checker.generate_report(report_path)

    print(f"\n📊 Health Check Complete!")
    print(f"📄 Report: {report_path}")
    print(f"🏥 Status: {result.status.upper()}")

    # Return exit code based on status
    if result.status == "critical":
        return 1
    else:
        return 0


if __name__ == "__main__":
    exit(main())
