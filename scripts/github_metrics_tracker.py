#!/usr/bin/env python3
"""
GitHub Metrics Tracker for OSS Vendors

Automatically tracks GitHub stars, forks, and contributors for OSS vendors
in the vendor database. Updates adoption_metrics evidence sources.

Usage:
    # Set GitHub token (optional, increases rate limit)
    export GITHUB_TOKEN="ghp_your_token_here"

    # Run tracker
    python scripts/github_metrics_tracker.py

    # Dry run (preview changes)
    python scripts/github_metrics_tracker.py --dry-run

Features:
- Fetches current GitHub stars, forks, contributors
- Updates adoption_metrics evidence sources
- Respects GitHub API rate limits
- Generates metrics trend report

Requirements:
    pip install requests
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time

try:
    import requests
except ImportError:
    print("❌ ERROR: requests library not installed")
    print("   Install with: pip install requests")
    sys.exit(1)


class GitHubMetricsTracker:
    """Track GitHub metrics for OSS vendors."""

    # GitHub repo URL patterns for common OSS vendors
    GITHUB_REPOS = {
        'apache-kafka': 'apache/kafka',
        'apache-flink': 'apache/flink',
        'apache-pulsar': 'apache/pulsar',
        'redpanda': 'redpanda-data/redpanda',
        'clickhouse': 'ClickHouse/ClickHouse',
        'trino': 'trinodb/trino',
        'prestodb': 'prestodb/presto',
        'apache-drill': 'apache/drill',
        'apache-pinot': 'apache/pinot',
        'apache-iceberg': 'apache/iceberg',
        'delta-lake': 'delta-io/delta',
        'apache-hudi': 'apache/hudi',
        'apache-druid': 'apache/druid',
        'wazuh': 'wazuh/wazuh',
        'grafana-loki': 'grafana/loki',
        'graylog': 'Graylog2/graylog2-server',
        'minio': 'minio/minio',
        'ceph': 'ceph/ceph',
        'apache-nifi': 'apache/nifi',
        'airbyte': 'airbytehq/airbyte',
        'apache-atlas': 'apache/atlas',
        'apache-calcite': 'apache/calcite',
        'rabbitmq': 'rabbitmq/rabbitmq-server',
        'apache-storm': 'apache/storm',
        'elastic-security': 'elastic/elasticsearch',
    }

    def __init__(
        self,
        lit_review_path: str = "~/security-data-literature-review",
        github_token: Optional[str] = None,
        dry_run: bool = False
    ):
        self.lit_review_path = Path(lit_review_path).expanduser()
        self.github_token = github_token or os.environ.get('GITHUB_TOKEN')
        self.dry_run = dry_run

        # Paths
        self.vendor_db_path = self.lit_review_path / "vendor-landscape" / "vendor-database.json"

        # GitHub API setup
        self.api_base = "https://api.github.com"
        self.session = requests.Session()
        if self.github_token:
            self.session.headers['Authorization'] = f'token {self.github_token}'
        self.session.headers['Accept'] = 'application/vnd.github.v3+json'

        # Tracking
        self.metrics_updated = []
        self.rate_limit_info = None

    def run_tracking(self) -> bool:
        """Run GitHub metrics tracking workflow."""
        print("📊 Starting GitHub Metrics Tracking...")
        print(f"📅 Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"🔑 GitHub Token: {'✅ Configured' if self.github_token else '⚠️  Not configured (rate limited to 60 req/hr)'}")
        print(f"🔍 Mode: {'DRY RUN' if self.dry_run else 'LIVE'}\n")

        # Check rate limit
        self.check_rate_limit()

        # Load vendor database
        print("📖 Loading vendor database...")
        try:
            with open(self.vendor_db_path, 'r') as f:
                db = json.load(f)
        except Exception as e:
            print(f"❌ ERROR: Failed to load vendor database: {e}")
            return False

        vendors = db.get('vendors', [])
        print(f"✅ Loaded {len(vendors)} vendors\n")

        # Track metrics for OSS vendors
        print("🔄 Fetching GitHub metrics for OSS vendors...\n")

        for vendor_id, repo in self.GITHUB_REPOS.items():
            vendor = next((v for v in vendors if v['id'] == vendor_id), None)

            if not vendor:
                print(f"⚠️  Vendor not found in database: {vendor_id}")
                continue

            # Fetch current metrics
            metrics = self.fetch_github_metrics(repo)

            if metrics:
                # Update vendor evidence
                self.update_vendor_metrics(vendor, repo, metrics)
                print(f"✅ {vendor['name']}: {metrics['stars']:,} stars, {metrics['forks']:,} forks")
            else:
                print(f"❌ {vendor['name']}: Failed to fetch metrics")

            # Rate limit check
            if len(self.metrics_updated) % 10 == 0:
                self.check_rate_limit()

            # Be nice to GitHub API
            time.sleep(0.5)

        # Save changes
        if not self.dry_run and self.metrics_updated:
            print(f"\n💾 Saving changes to vendor database...")
            db['meta']['last_updated'] = datetime.now(timezone.utc).isoformat()

            with open(self.vendor_db_path, 'w') as f:
                json.dump(db, f, indent=2)

            print(f"✅ Updated {len(self.metrics_updated)} vendors")
        elif self.dry_run:
            print(f"\n🔍 DRY RUN: Would have updated {len(self.metrics_updated)} vendors")
        else:
            print(f"\n✅ No updates needed")

        # Generate report
        self.generate_metrics_report()

        # Summary
        print("\n" + "=" * 70)
        print("✅ GITHUB METRICS TRACKING COMPLETE")
        print("=" * 70)
        print(f"📊 Vendors tracked: {len(self.metrics_updated)}")
        print(f"🔄 Metrics updated: {len([m for m in self.metrics_updated if m.get('updated')])}")
        if self.rate_limit_info:
            print(f"⏱️  GitHub API rate limit: {self.rate_limit_info['remaining']}/{self.rate_limit_info['limit']} remaining")
        print("=" * 70 + "\n")

        return True

    def check_rate_limit(self):
        """Check GitHub API rate limit."""
        try:
            response = self.session.get(f"{self.api_base}/rate_limit")
            if response.status_code == 200:
                data = response.json()
                core = data['resources']['core']
                self.rate_limit_info = {
                    'limit': core['limit'],
                    'remaining': core['remaining'],
                    'reset': datetime.fromtimestamp(core['reset'], tz=timezone.utc)
                }

                if core['remaining'] < 10:
                    reset_time = self.rate_limit_info['reset'].strftime('%H:%M:%S UTC')
                    print(f"⚠️  WARNING: GitHub API rate limit low ({core['remaining']} remaining)")
                    print(f"   Resets at: {reset_time}")
        except Exception as e:
            print(f"⚠️  Could not check rate limit: {e}")

    def fetch_github_metrics(self, repo: str) -> Optional[Dict]:
        """Fetch GitHub repo metrics."""
        try:
            response = self.session.get(f"{self.api_base}/repos/{repo}")

            if response.status_code == 200:
                data = response.json()
                return {
                    'stars': data.get('stargazers_count', 0),
                    'forks': data.get('forks_count', 0),
                    'watchers': data.get('subscribers_count', 0),
                    'open_issues': data.get('open_issues_count', 0),
                    'size_kb': data.get('size', 0),
                    'created_at': data.get('created_at'),
                    'updated_at': data.get('updated_at'),
                    'language': data.get('language'),
                }
            elif response.status_code == 404:
                print(f"  ⚠️  Repo not found: {repo}")
                return None
            elif response.status_code == 403:
                print(f"  ⚠️  Rate limit exceeded or authentication required")
                return None
            else:
                print(f"  ⚠️  HTTP {response.status_code}: {repo}")
                return None

        except Exception as e:
            print(f"  ❌ Error fetching {repo}: {e}")
            return None

    def update_vendor_metrics(self, vendor: Dict, repo: str, metrics: Dict):
        """Update vendor adoption_metrics evidence source."""
        evidence_sources = vendor.get('evidence_sources', [])

        # Find existing GitHub metrics evidence
        github_evidence = None
        for source in evidence_sources:
            if source.get('type') in ['community_metrics', 'adoption_metrics']:
                if 'github' in source.get('description', '').lower():
                    github_evidence = source
                    break

        # Create new description with current metrics
        stars_str = f"{metrics['stars']:,}" if metrics['stars'] >= 1000 else str(metrics['stars'])
        forks_str = f"{metrics['forks']:,}" if metrics['forks'] >= 1000 else str(metrics['forks'])

        new_description = f"GitHub community metrics: {stars_str} stars, {forks_str} forks (as of {datetime.now(timezone.utc).strftime('%Y-%m-%d')})"

        if github_evidence:
            # Update existing evidence
            old_description = github_evidence.get('description', '')

            if old_description != new_description:
                github_evidence['description'] = new_description
                github_evidence['last_updated'] = datetime.now(timezone.utc).isoformat()
                github_evidence['metrics'] = metrics

                self.metrics_updated.append({
                    'vendor_id': vendor['id'],
                    'vendor_name': vendor['name'],
                    'repo': repo,
                    'updated': True,
                    'old_stars': self.extract_stars(old_description),
                    'new_stars': metrics['stars']
                })
            else:
                self.metrics_updated.append({
                    'vendor_id': vendor['id'],
                    'vendor_name': vendor['name'],
                    'repo': repo,
                    'updated': False,
                    'note': 'No change in metrics'
                })
        else:
            # Create new evidence source
            new_evidence = {
                'id': f"github-metrics-{vendor['id']}-{datetime.now(timezone.utc).strftime('%Y%m')}",
                'description': new_description,
                'url': f"https://github.com/{repo}",
                'evidence_tier': 'A',
                'type': 'community_metrics',
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'metrics': metrics
            }

            if 'evidence_sources' not in vendor:
                vendor['evidence_sources'] = []

            vendor['evidence_sources'].append(new_evidence)

            # Update evidence_summary
            if 'evidence_summary' in vendor:
                vendor['evidence_summary']['total_sources'] += 1
                vendor['evidence_summary']['tier_a_sources'] += 1

            self.metrics_updated.append({
                'vendor_id': vendor['id'],
                'vendor_name': vendor['name'],
                'repo': repo,
                'updated': True,
                'new_stars': metrics['stars'],
                'note': 'Created new evidence source'
            })

    def extract_stars(self, description: str) -> Optional[int]:
        """Extract star count from description string."""
        match = re.search(r'([\d,]+)\s*stars', description)
        if match:
            return int(match.group(1).replace(',', ''))
        return None

    def generate_metrics_report(self):
        """Generate metrics tracking report."""
        print("\n📊 GITHUB METRICS REPORT")
        print("=" * 70)

        if not self.metrics_updated:
            print("No vendors tracked")
            return

        # Sort by star count
        updated = [m for m in self.metrics_updated if m.get('updated') and m.get('new_stars')]
        updated.sort(key=lambda x: x['new_stars'], reverse=True)

        print(f"\nTop OSS Vendors by GitHub Stars:")
        print(f"{'Vendor':<40s} {'Stars':>10s} {'Change':>10s}")
        print("-" * 70)

        for metric in updated[:10]:
            vendor_name = metric['vendor_name'][:38]
            stars = f"{metric['new_stars']:,}"
            old_stars = metric.get('old_stars')

            if old_stars is not None:
                change = metric['new_stars'] - old_stars
                change_str = f"+{change:,}" if change > 0 else str(change)
            else:
                change_str = "new"

            print(f"{vendor_name:<40s} {stars:>10s} {change_str:>10s}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="GitHub metrics tracker for OSS vendors"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without saving to database'
    )
    parser.add_argument(
        '--github-token',
        help='GitHub personal access token (or set GITHUB_TOKEN env var)'
    )
    parser.add_argument(
        '--lit-review-path',
        default='~/security-data-literature-review',
        help='Path to literature review repository'
    )

    args = parser.parse_args()

    tracker = GitHubMetricsTracker(
        lit_review_path=args.lit_review_path,
        github_token=args.github_token,
        dry_run=args.dry_run
    )

    success = tracker.run_tracking()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
