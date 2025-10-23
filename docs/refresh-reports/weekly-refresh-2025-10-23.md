# Weekly Vendor Database Refresh Report

**Date**: 2025-10-23 07:06:57 UTC
**Mode**: DRY RUN
**Database**: /home/jerem/security-data-literature-review/vendor-landscape/vendor-database.json

---

## Summary

| Metric | Count |
|--------|-------|
| Total Vendors | 65 |
| GitHub Metrics Updated | 0 |
| Analyst URL Validations | 1 |
| URL Failures Detected | 5 |
| Evidence Timestamps Updated | 30 |
| Vendors Modified | 30 |

---

## GitHub Metrics Updates

_No GitHub metric updates this week_

---

## Analyst URL Validation

- **New Publications Check**: manual_review_required - Check Gartner and Forrester websites quarterly

---

## Issues Detected

### URL Validation Failures

- **Microsoft Azure Sentinel**: https://www.gartner.com/en/documents/magic-quadrant-siem
  - Error: HTTP 403
  - Source ID: gartner-mq-siem-2024-azure-sentinel

- **Amazon Athena**: https://www.forrester.com/wave/cloud-data-warehouse-2024
  - Error: HTTP 404
  - Source ID: forrester-wave-cloud-dw-2024-athena

- **Snowflake Data Cloud**: https://www.gartner.com/en/documents/magic-quadrant-cloud-database
  - Error: HTTP 403
  - Source ID: gartner-mq-cloud-database-2024-snowflake

- **Databricks Lakehouse Platform**: https://www.gartner.com/en/documents/magic-quadrant-data-science
  - Error: HTTP 404
  - Source ID: gartner-mq-data-science-2024-databricks

- **Google BigQuery**: https://www.gartner.com/en/documents/magic-quadrant-cloud-database
  - Error: HTTP 403
  - Source ID: gartner-mq-cloud-database-2024-bigquery


---

## Next Steps

### High Priority
1. Investigate failed analyst report URLs
2. Update URLs or mark evidence sources as deprecated

### Routine Maintenance
1. Review new Gartner MQ / Forrester Wave publications (quarterly)
2. Update GitHub star counts for trending OSS vendors (monthly)
3. Check for new vendor capabilities (monthly)
4. Validate production deployment evidence is still current (quarterly)

---

**Generated**: 2025-10-23 07:06:57 UTC
**Script**: `scripts/weekly_vendor_refresh.py`
