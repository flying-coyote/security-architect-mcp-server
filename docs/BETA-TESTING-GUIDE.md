# Beta Testing Guide - Security Architecture Decision MCP Server

**Created**: October 30, 2025
**Version**: 1.0
**Target Audience**: Security architects testing Phase 1 foundational filtering
**Estimated Time**: 30-45 minutes per session

---

## Overview

Thank you for participating in beta testing the Security Architecture Decision MCP Server! This tool helps security architects filter 71 security data platforms to 3-5 personalized finalists using an evidence-based decision framework.

**What Makes This Different**: This tool asks **foundational architecture questions FIRST** (table format, catalog choice) before organizational constraints (team size, budget). This prevents vendor lock-in by establishing architectural commitments before filtering.

---

## Prerequisites

### Required

1. **Claude Desktop** installed and configured
2. **MCP Server** configured in Claude Desktop settings
3. **30-45 minutes** of uninterrupted time
4. **A real or realistic security architecture decision** you're facing (or use one of our sample scenarios)

### Helpful Context (Optional)

- Familiarity with Apache Iceberg vs Delta Lake
- Understanding of data catalogs (Polaris, Unity Catalog, AWS Glue)
- Experience with dbt or Spark for transformations
- Current security data platform experience (SIEM, data lakehouse, etc.)

---

## Beta Testing Session Structure

### Phase 1: Foundational Architecture (10-15 minutes)

You'll be asked to make 4 foundational decisions:

**Question F1: Table Format**
- Options: Apache Iceberg, Delta Lake, Hudi, proprietary, undecided
- **Guidance**: If unsure, start with "undecided" to see all options

**Question F2: Catalog**
- Options: Polaris, Unity Catalog, Nessie, AWS Glue, Hive Metastore, undecided
- **Guidance**: If you chose Iceberg, consider Polaris. If Delta, consider Unity Catalog.

**Question F3: Transformation Strategy**
- Options: dbt, Spark, vendor built-in, custom Python, undecided
- **Guidance**: dbt = SQL-based analytics, Spark = large-scale processing

**Question F4: Query Engine Characteristics**
- Options: low-latency (<1s), high-concurrency (100+ queries), serverless, cost-optimized, flexible
- **Guidance**: SOC analysts typically need low-latency

### Phase 2: Organizational Constraints (5-10 minutes)

Standard decision framework questions:
- Team size (lean 1-2, standard 3-5, large 6+)
- Budget range (<$500K, $500K-2M, $2M-5M, >$5M)
- Data sovereignty (cloud-first, hybrid, on-prem only)
- Vendor tolerance (OSS-first, OSS with support, commercial only)

### Phase 3: Feature Preferences (5-10 minutes)

Weighted preferences (1-3 scale):
- SQL interface, streaming query, multi-engine query
- Open table format, schema evolution
- SIEM integration, data governance, ML analytics, etc.

### Phase 4: Report & Finalists (5-10 minutes)

- Generate architecture report
- Review 3-5 finalists
- Calculate TCO for top choices
- Match to journey persona (Jennifer/Marcus/Priya)

---

## Sample Scenarios

### Scenario 1: Cloud-Native Startup (Jennifer's Journey)

**Context**: Series B startup, 5-person security team, $500K-2M budget, cloud-first

**Foundational Decisions**:
- Table Format: Apache Iceberg (portability, vendor flexibility)
- Catalog: Polaris (Iceberg-native, open source)
- Transformation: dbt (SQL-based, familiar to analysts)
- Query Engine: Low-latency (SOC needs <1s response)

**Expected Results**: 71 vendors → ~2-5 vendors (Trino, Starburst, potentially Dremio)

### Scenario 2: Enterprise Bank (Marcus's Journey)

**Context**: Fortune 500 bank, 12-person team, $2M-5M budget, on-prem required

**Foundational Decisions**:
- Table Format: Undecided (evaluating options)
- Catalog: Undecided (need guidance)
- Transformation: Spark (enterprise-scale processing)
- Query Engine: High-concurrency (many analysts)

**Expected Results**: 71 vendors → ~20-30 vendors (needs constraint filtering in Phase 2)

### Scenario 3: Databricks-Native Shop (Existing Investment)

**Context**: Mid-market company, already using Databricks for data engineering

**Foundational Decisions**:
- Table Format: Delta Lake (existing investment)
- Catalog: Unity Catalog (Databricks-native)
- Transformation: Spark (Databricks-native)
- Query Engine: Flexible (already have infrastructure)

**Expected Results**: 71 vendors → ~2-5 vendors (Databricks, Delta Lake, potentially Spark-based tools)

---

## What We're Testing

### Critical Validation Points

**1. Foundational Question Clarity**
- Are Questions F1-F4 understandable?
- Do you need more context/examples?
- Are the options clear (e.g., "Polaris vs Unity Catalog")?

**2. Filtering Accuracy**
- Do the finalists match your architecture preferences?
- Are elimination reasons clear and actionable?
- Do you agree with the vendors that were filtered out?

**3. Decision Flow Logic**
- Does asking foundational questions FIRST feel natural?
- Would you prefer constraints (team/budget) asked first?
- Does the 3-phase flow (foundational → constraints → features) make sense?

**4. Elimination Feedback**
- When a vendor is eliminated, is the reason clear?
- Can you understand WHY Databricks was eliminated (if you chose Iceberg)?
- Do elimination messages help you learn about trade-offs?

**5. Narrow Filtering Comfort**
- If you get 2-5 finalists (97% elimination), does this feel too narrow or just right?
- Do you trust the filtering logic?
- Would you want an "undo" or "loosen filters" option?

---

## Feedback Collection

### During Your Session

**Take notes on**:
1. Any confusing questions or terminology
2. Moments where you wanted more context
3. Elimination reasons that surprised you
4. Vendors you expected to see but didn't

### After Your Session

**Complete the Beta Feedback Template** (see `docs/BETA-FEEDBACK-TEMPLATE.md`):
- 5-point scale questions (1 = strongly disagree, 5 = strongly agree)
- Open-ended questions about your experience
- Suggestions for improvement

---

## Common Questions

### Q: What if I don't have preferences for all Phase 1 questions?

**A**: Select "undecided" or "flexible"! The tool won't eliminate vendors if you haven't decided. You can always re-run with more specific preferences later.

### Q: Can I change my Phase 1 answers after seeing results?

**A**: Yes! This is iterative. If you see results and think "I should have chosen Iceberg instead of Delta," start a new conversation and try different options.

### Q: Why are SO MANY vendors eliminated?

**A**: Phase 1 foundational filtering is intentionally aggressive (often 60-90% elimination). The goal is to establish architectural commitments before organizational constraints. This is the **key insight from the blog**: foundational decisions narrow the field dramatically.

### Q: What if my preferred vendor gets eliminated?

**A**: This is important feedback! Tell us:
1. Which vendor was eliminated?
2. Why do you prefer it?
3. Do you disagree with the elimination reason?

This helps us refine the capability matrix.

### Q: Can I test without a real decision?

**A**: Yes! Use one of the **Sample Scenarios** above. Pick one that roughly matches your organization (startup/enterprise, cloud/on-prem) and walk through it.

---

## Troubleshooting

### Issue: Tool doesn't respond or hangs

**Solution**:
1. Check Claude Desktop status (bottom-right corner)
2. Restart Claude Desktop
3. Verify MCP server is running (`ps aux | grep security-architect`)
4. Check MCP server logs (if accessible)

### Issue: Results don't match expectations

**Solution**:
1. Review the "filters_applied" section in results
2. Check which Phase 1 filters were active
3. Look at "eliminated_vendors" to understand why specific vendors were filtered
4. Try "undecided" for all Phase 1 questions to see full vendor list

### Issue: Want to see a specific vendor's capabilities

**Solution**:
Ask Claude: "Show me [vendor name]'s capabilities, especially Iceberg support, catalog support, and dbt integration"

The MCP server has access to the full vendor database.

---

## Success Criteria

We consider your beta test successful if:

**Minimum**:
- [ ] You completed a full decision flow (Phase 1 → Phase 2 → Phase 3)
- [ ] You received 3-5 finalist vendors
- [ ] You submitted the feedback template

**Ideal**:
- [ ] You tested 2-3 different scenarios (different table formats, catalogs)
- [ ] You compared results (e.g., "What changes if I choose Delta instead of Iceberg?")
- [ ] You provided detailed feedback on elimination reasons
- [ ] You identified at least one improvement suggestion

---

## After Testing

### Immediate Next Steps

1. **Submit Feedback**: Complete `docs/BETA-FEEDBACK-TEMPLATE.md`
2. **Share Results** (optional): We can anonymize your decision conversation for a blog case study (requires explicit permission)
3. **Follow-Up Interview** (optional): 15-minute call to discuss your experience in depth

### Long-Term

- We'll incorporate your feedback into the tool
- You'll receive updates when we release improvements
- You'll be credited as a beta tester (if you consent)
- You may be invited to test future features (POC test suite generator, blog post generator)

---

## Contact & Support

### During Beta Testing

- **Slack**: #mcp-server-beta (if you're in the workspace)
- **Email**: jeremy@securitydatacommons.com
- **GitHub Issues**: https://github.com/flying-coyote/security-architect-mcp-server/issues

### Reporting Bugs

If you encounter a bug:
1. Copy the full error message or unexpected behavior
2. Note which Phase you were in (1, 2, or 3)
3. Describe what you expected vs what happened
4. Submit via GitHub Issues or email

---

## Compensation & Thanks

**What You Get**:
- Free architecture consultation (30-minute session)
- Early access to tool updates
- Recognition as a beta tester (if you consent)
- Our sincere gratitude for helping validate this approach!

**What We Get**:
- Validation that Phase 1 foundational filtering works in real decisions
- Feedback on question clarity and elimination logic
- Real-world scenarios to test the decision framework
- Case studies for blog content (with permission)

---

**Thank you for participating in this beta test! Your feedback will directly shape the future of security architecture decision support tooling.**

---

**Version History**:
- v1.0 (Oct 30, 2025): Initial beta testing guide for Phase 1 foundational filtering

**Last Updated**: October 30, 2025
