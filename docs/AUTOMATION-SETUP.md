# Vendor Database Automation Setup Guide

**Purpose**: Automate weekly vendor database refresh to maintain enterprise-grade quality
**Last Updated**: October 23, 2025

---

## Overview

This guide sets up automated processes for:

1. **Weekly Vendor Refresh** - Validates evidence sources, checks for new analyst reports
2. **GitHub Metrics Tracking** - Updates OSS vendor adoption metrics (stars, forks, contributors)
3. **MCP Server Sync** - Automatically syncs enriched database to MCP server

---

## Prerequisites

### Required

- Python 3.10+
- Access to both repositories:
  - `~/security-data-literature-review` (vendor database)
  - `~/security-architect-mcp-server` (MCP server)
- Unix/Linux system with cron (or Windows with Task Scheduler)

### Optional (Recommended)

- **GitHub Personal Access Token** (increases API rate limit from 60 to 5,000 requests/hour)
  - Create at: https://github.com/settings/tokens
  - Required scopes: `public_repo` (read-only)

---

## Installation

### 1. Install Python Dependencies

```bash
cd ~/security-architect-mcp-server

# Install requests library for GitHub API
pip install requests

# Verify scripts are executable
chmod +x scripts/weekly_vendor_refresh.py
chmod +x scripts/github_metrics_tracker.py
```

### 2. Configure GitHub Token (Optional but Recommended)

```bash
# Add to ~/.bashrc or ~/.zshrc
export GITHUB_TOKEN="ghp_your_personal_access_token_here"

# Reload shell configuration
source ~/.bashrc  # or source ~/.zshrc
```

**Why?**
- Without token: 60 requests/hour (sufficient for ~25 OSS vendors)
- With token: 5,000 requests/hour (sufficient for hundreds of vendors)

### 3. Test Scripts Manually

```bash
# Test weekly refresh (dry run)
cd ~/security-architect-mcp-server
python3 scripts/weekly_vendor_refresh.py --dry-run

# Test GitHub metrics tracker (dry run)
python3 scripts/github_metrics_tracker.py --dry-run

# Run live (makes actual changes)
python3 scripts/weekly_vendor_refresh.py
python3 scripts/github_metrics_tracker.py
```

**Expected Output**:
```
✅ WEEKLY REFRESH COMPLETE
📊 GitHub metrics updated: 24
⚠️  URL validation failures: 0
📝 Analyst report checks: 30
🔄 Vendors modified: 24
```

---

## Automation Setup

### Option 1: Cron Jobs (Linux/Mac)

#### Edit Crontab

```bash
crontab -e
```

#### Add Automation Jobs

```bash
# Vendor database automation
# Run every Monday at 9:00 AM UTC
0 9 * * 1 cd ~/security-architect-mcp-server && python3 scripts/weekly_vendor_refresh.py >> logs/weekly-refresh.log 2>&1

# GitHub metrics tracking
# Run on the 1st of every month at 10:00 AM UTC
0 10 1 * * cd ~/security-architect-mcp-server && python3 scripts/github_metrics_tracker.py >> logs/github-metrics.log 2>&1

# Weekly health check (existing)
# Run every Sunday at 8:00 AM UTC
0 8 * * 0 cd ~/security-architect-mcp-server && python3 scripts/weekly_health_check.py >> logs/health-check.log 2>&1
```

#### Create Logs Directory

```bash
mkdir -p ~/security-architect-mcp-server/logs
```

#### Verify Cron Jobs

```bash
crontab -l
```

**Expected Output**:
```
0 9 * * 1 cd ~/security-architect-mcp-server && python3 scripts/weekly_vendor_refresh.py >> logs/weekly-refresh.log 2>&1
0 10 1 * * cd ~/security-architect-mcp-server && python3 scripts/github_metrics_tracker.py >> logs/github-metrics.log 2>&1
0 8 * * 0 cd ~/security-architect-mcp-server && python3 scripts/weekly_health_check.py >> logs/health-check.log 2>&1
```

---

### Option 2: GitHub Actions (Recommended for Collaboration)

Create `.github/workflows/vendor-database-refresh.yml`:

```yaml
name: Vendor Database Weekly Refresh

on:
  schedule:
    # Run every Monday at 9:00 AM UTC
    - cron: '0 9 * * 1'
  workflow_dispatch:  # Allow manual trigger

jobs:
  refresh:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout MCP Server repo
        uses: actions/checkout@v3
        with:
          repository: flying-coyote/security-architect-mcp-server
          path: mcp-server

      - name: Checkout Literature Review repo
        uses: actions/checkout@v3
        with:
          repository: flying-coyote/security-data-literature-review
          path: literature-review
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install requests

      - name: Run weekly vendor refresh
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          cd mcp-server
          python3 scripts/weekly_vendor_refresh.py \
            --lit-review-path ../literature-review \
            --mcp-server-path .

      - name: Run GitHub metrics tracker
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          cd mcp-server
          python3 scripts/github_metrics_tracker.py \
            --lit-review-path ../literature-review

      - name: Commit and push changes
        run: |
          cd literature-review
          git config user.name "GitHub Actions Bot"
          git config user.email "actions@github.com"
          git add vendor-landscape/vendor-database.json
          git diff --staged --quiet || git commit -m "🤖 Automated vendor database refresh"
          git push

      - name: Sync to MCP server
        run: |
          cd mcp-server
          python3 scripts/sync_from_literature_review.py \
            --lit-review-path ../literature-review \
            --mcp-server-path .

          git config user.name "GitHub Actions Bot"
          git config user.email "actions@github.com"
          git add data/vendor_database.json data/INTEGRATION_STATUS.md
          git diff --staged --quiet || git commit -m "🤖 Sync vendor database from literature review"
          git push
```

**Advantages**:
- ✅ Runs automatically on GitHub infrastructure
- ✅ No local machine required
- ✅ Audit trail in GitHub Actions logs
- ✅ Easy to disable/modify schedule
- ✅ Team visibility

---

## Maintenance Schedule

### Weekly (Every Monday)

**Script**: `weekly_vendor_refresh.py`

**Tasks**:
- ✅ Validate analyst report URLs are accessible
- ✅ Check for new Gartner MQ / Forrester Wave publications
- ✅ Update evidence timestamps
- ✅ Generate weekly health report
- ✅ Auto-sync to MCP server

**Time Required**: 2-5 minutes (automated)

### Monthly (1st of Month)

**Script**: `github_metrics_tracker.py`

**Tasks**:
- ✅ Fetch current GitHub stars for 24 OSS vendors
- ✅ Update adoption_metrics evidence sources
- ✅ Generate metrics trend report
- ✅ Identify trending OSS vendors

**Time Required**: 3-8 minutes (automated)

**Expected Updates**: 10-15 vendors with star count changes

### Quarterly (Manual Review Required)

**Tasks**:
- 🔍 Check Gartner website for new Magic Quadrant publications
  - SIEM MQ (typically published Q1)
  - Cloud Database MQ (typically published Q2)
  - Data Integration MQ (typically published Q3)
- 🔍 Check Forrester website for new Wave reports
  - Security Analytics Platforms (typically published Q2)
  - Streaming Data Platforms (typically published Q4)
- 🔍 Review vendor production deployment news
  - Search for new Fortune 500 case studies
  - Update production_deployment evidence sources

**Time Required**: 2-4 hours manual research

**Deliverable**: Update evidence_sources with new analyst reports or production evidence

### Annual (Major Refresh)

**Tasks**:
- 🔄 Review all 65 vendors for continued relevance
- 🔄 Add 5-10 new emerging vendors
- 🔄 Deprecate vendors that ceased operations or were acquired
- 🔄 Major cost model updates (pricing changes)
- 🔄 Validate all production deployment evidence is still current

**Time Required**: 8-16 hours

**Deliverable**: Comprehensive vendor database refresh

---

## Monitoring and Alerts

### Check Automation Logs

```bash
# View latest weekly refresh log
tail -50 ~/security-architect-mcp-server/logs/weekly-refresh.log

# View latest GitHub metrics log
tail -50 ~/security-architect-mcp-server/logs/github-metrics.log

# Check for errors
grep -i error ~/security-architect-mcp-server/logs/*.log
```

### Success Indicators

**Weekly Refresh**:
- ✅ 0 URL validation failures
- ✅ 0 sync errors
- ✅ Evidence timestamps updated

**GitHub Metrics**:
- ✅ 20+ vendors tracked
- ✅ Star counts increasing over time
- ✅ No GitHub API rate limit errors

### Failure Indicators

**Weekly Refresh**:
- ❌ URL validation failures > 3 (analyst report links broken)
- ❌ Sync script errors (database schema issues)
- ❌ No weekly report generated

**GitHub Metrics**:
- ❌ GitHub API rate limit exceeded (need token)
- ❌ Star counts decreasing (repo moved or archived)
- ❌ Multiple 404 errors (repo renamed)

### Alert Setup (Optional)

```bash
# Add to cron jobs for email alerts on failure
MAILTO=your-email@example.com

# Weekly refresh with alert on failure
0 9 * * 1 cd ~/security-architect-mcp-server && python3 scripts/weekly_vendor_refresh.py || echo "Weekly refresh failed" | mail -s "MCP Vendor Refresh Failed" $MAILTO
```

---

## Troubleshooting

### Issue: GitHub API Rate Limit Exceeded

**Symptoms**:
```
⚠️  WARNING: GitHub API rate limit low (0 remaining)
   Resets at: 14:23:45 UTC
```

**Solution**:
1. Configure GitHub token (see Installation step 2)
2. Or wait for rate limit reset (shown in warning)
3. Or reduce tracking frequency (monthly → quarterly)

### Issue: Analyst URL Validation Failures

**Symptoms**:
```
⚠️  Microsoft Sentinel: HTTP error 404
⚠️  Splunk: URL returned 403
```

**Solution**:
1. Check if URL moved (vendor press releases often change)
2. Update URL in evidence_sources
3. Or mark evidence as deprecated if URL permanently gone
4. Or replace with vendor press release announcing MQ positioning

### Issue: Sync Script Fails

**Symptoms**:
```
❌ ERROR: Invalid JSON in vendor database
❌ ERROR: Failed to sync to MCP server
```

**Solution**:
1. Validate JSON syntax:
   ```bash
   python3 -m json.tool vendor-database.json > /dev/null
   ```
2. Check for merge conflicts (if using Git)
3. Restore from backup if corrupted:
   ```bash
   cp vendor-database.json.backup vendor-database.json
   ```

### Issue: Cron Job Not Running

**Symptoms**:
- No log entries for scheduled time
- Log file empty or missing

**Solution**:
1. Check cron service is running:
   ```bash
   sudo systemctl status cron  # Linux
   # or
   ps aux | grep cron  # Mac
   ```
2. Verify crontab syntax:
   ```bash
   crontab -l
   ```
3. Check for typos in paths
4. Verify script has execute permissions:
   ```bash
   ls -la scripts/weekly_vendor_refresh.py
   ```

---

## Advanced Configuration

### Custom Refresh Frequency

Edit crontab to change schedule:

```bash
# Every Monday and Thursday (2×/week)
0 9 * * 1,4 cd ~/security-architect-mcp-server && python3 scripts/weekly_vendor_refresh.py

# First Monday of every month (1×/month)
0 9 1-7 * 1 cd ~/security-architect-mcp-server && python3 scripts/weekly_vendor_refresh.py
```

### Dry Run for Testing

Test automation without making changes:

```bash
# Dry run weekly refresh
python3 scripts/weekly_vendor_refresh.py --dry-run

# Dry run GitHub tracker
python3 scripts/github_metrics_tracker.py --dry-run
```

### Custom Paths

If repositories are in non-default locations:

```bash
python3 scripts/weekly_vendor_refresh.py \
  --lit-review-path /custom/path/to/literature-review \
  --mcp-server-path /custom/path/to/mcp-server
```

---

## Security Considerations

### GitHub Token Storage

**Best Practices**:
- ✅ Use environment variables (not hardcoded in scripts)
- ✅ Use GitHub Secrets for GitHub Actions
- ✅ Rotate tokens annually
- ✅ Use minimal scopes (`public_repo` only)
- ❌ Never commit tokens to Git
- ❌ Never share tokens in logs or documentation

### Rate Limiting

**Respect GitHub API limits**:
- Without token: 60 requests/hour
- With token: 5,000 requests/hour
- Scripts include rate limit checking
- Auto-throttling with 0.5s delay between requests

### Data Validation

**All automated updates validated**:
- JSON schema validation before saving
- Evidence tier classification maintained (Tier A only)
- Existing evidence preserved (append-only updates)
- Git history provides rollback capability

---

## Success Metrics

### Week 1 (Setup)
- ✅ Scripts installed and tested
- ✅ Cron jobs or GitHub Actions configured
- ✅ First automated refresh completes successfully
- ✅ Logs directory created and populated

### Month 1 (Validation)
- ✅ 4 weekly refreshes completed (0 failures)
- ✅ 1 monthly GitHub metrics update completed
- ✅ Evidence quality maintained (100% Tier A for enrichment sources)
- ✅ MCP server auto-syncs successfully

### Quarter 1 (Mature)
- ✅ 12 weekly refreshes completed (<5% failure rate)
- ✅ 3 monthly GitHub metrics updates completed
- ✅ 1 manual quarterly review completed
- ✅ Vendor database stays current without manual intervention

---

## Next Steps

1. **Install and Test** (30 minutes)
   - Install Python dependencies
   - Configure GitHub token
   - Run dry-run tests

2. **Setup Automation** (15 minutes)
   - Choose cron or GitHub Actions
   - Configure schedule
   - Verify first run

3. **Monitor** (ongoing)
   - Check logs weekly
   - Review quarterly reports
   - Adjust schedule as needed

4. **Expand** (future)
   - Add more OSS vendor GitHub repos
   - Integrate IT Harvest API (if partnership succeeds)
   - Add Slack/email notifications for failures

---

**Setup Guide Created**: October 23, 2025
**Scripts**: `weekly_vendor_refresh.py`, `github_metrics_tracker.py`
**Status**: Ready for production use
