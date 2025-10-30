# Phase 1 Foundational Filtering - Testing Guide

**Created**: October 30, 2025
**Purpose**: Validate Phase 1 foundational architecture filtering works correctly in Claude Desktop
**Estimated Time**: 15-20 minutes

---

## Prerequisites

1. **Claude Desktop** installed and running
2. **MCP Server** configured in Claude Desktop settings
3. **This Session**: You should be in a Claude Desktop conversation with the Security Architect MCP Server loaded

---

## Test Scenarios

### Test 1: Iceberg Preference (LIGER Stack)

**Goal**: Verify Iceberg table format preference filters out Delta-only vendors

**Steps**:
1. Call the `apply_foundational_filters` tool with:
   ```json
   {
     "table_format": "iceberg"
   }
   ```

**Expected Results**:
- ✅ **Viable vendors** should include:
  - apache-iceberg
  - amazon-athena (Iceberg native)
  - dremio (Iceberg native)
  - snowflake (Iceberg support)
  - trino (Iceberg support)
  - starburst (Iceberg support)

- ❌ **Eliminated vendors** should include:
  - databricks (Delta native, no Iceberg)
  - delta-lake (Delta native)

- **Metrics**:
  - Initial count: 71
  - Filtered count: ~25-30 vendors
  - Eliminated count: ~41-46 vendors

**Validation**:
- [ ] Databricks is eliminated with reason mentioning "no Iceberg support"
- [ ] Athena, Dremio pass the filter
- [ ] Elimination reasons are clear and actionable

---

### Test 2: Delta Lake Preference (Databricks-Native)

**Goal**: Verify Delta Lake preference filters out Iceberg-only vendors

**Steps**:
1. Call the `apply_foundational_filters` tool with:
   ```json
   {
     "table_format": "delta_lake"
   }
   ```

**Expected Results**:
- ✅ **Viable vendors** should include:
  - databricks (Delta native)
  - delta-lake (Delta native)
  - trino (Delta support)
  - starburst (Delta support)

- ❌ **Eliminated vendors** should include:
  - apache-iceberg (Iceberg only)
  - amazon-athena (Iceberg only)
  - dremio (Iceberg only)

- **Metrics**:
  - Initial count: 71
  - Filtered count: ~10-15 vendors
  - Eliminated count: ~56-61 vendors

**Validation**:
- [ ] Athena is eliminated with reason mentioning "no Delta Lake support"
- [ ] Databricks passes the filter
- [ ] Substantially fewer vendors than Iceberg preference

---

### Test 3: Combined Filtering (Iceberg + Polaris + dbt)

**Goal**: Verify combined foundational filters produce very narrow vendor list (LIGER Stack default)

**Steps**:
1. Call the `apply_foundational_filters` tool with:
   ```json
   {
     "table_format": "iceberg",
     "catalog": "polaris",
     "transformation_strategy": "dbt"
   }
   ```

**Expected Results**:
- ✅ **Viable vendors** should include:
  - trino (Iceberg + Polaris + dbt)
  - starburst (Iceberg + Polaris + dbt)

- ❌ **Eliminated vendors** should include:
  - databricks (Delta, not Iceberg)
  - amazon-athena (Glue catalog, not Polaris)
  - apache-iceberg (no dbt integration)

- **Metrics**:
  - Initial count: 71
  - Filtered count: ~2-5 vendors
  - Eliminated count: ~66-69 vendors

**Validation**:
- [ ] Only 2-5 vendors survive (very narrow)
- [ ] Trino and Starburst are in the finalist list
- [ ] Athena eliminated for "Glue catalog" not matching Polaris
- [ ] Apache Iceberg eliminated for "no dbt integration"

---

### Test 4: Low-Latency Query Engine Preference

**Goal**: Verify query engine characteristics filtering works (P95 < 1000ms)

**Steps**:
1. Call the `apply_foundational_filters` tool with:
   ```json
   {
     "query_engine_preference": "low_latency"
   }
   ```

**Expected Results**:
- ✅ **Viable vendors** should include:
  - clickhouse (200ms P95)
  - dremio (500ms P95)
  - apache-druid (500ms P95)

- ❌ **Eliminated vendors** should include:
  - amazon-athena (2000ms P95 - serverless latency)

- **Metrics**:
  - Initial count: 71
  - Filtered count: ~15-25 vendors
  - Eliminated count: ~46-56 vendors

**Validation**:
- [ ] ClickHouse passes (fastest)
- [ ] Athena eliminated with reason mentioning "2000ms P95 exceeds low-latency threshold"
- [ ] Vendors without query_latency_p95 data are NOT eliminated (no data ≠ disqualification)

---

### Test 5: "Undecided" Passes All Vendors

**Goal**: Verify "undecided" responses don't eliminate any vendors

**Steps**:
1. Call the `apply_foundational_filters` tool with:
   ```json
   {
     "table_format": "undecided",
     "catalog": "undecided",
     "transformation_strategy": "undecided",
     "query_engine_preference": "flexible"
   }
   ```

**Expected Results**:
- ✅ **All vendors** pass:
  - Initial count: 71
  - Filtered count: 71
  - Eliminated count: 0

**Validation**:
- [ ] No vendors eliminated
- [ ] Summary shows "71 vendors → 71 viable (0 eliminated)"

---

### Test 6: No Parameters (Default Behavior)

**Goal**: Verify calling with no parameters doesn't filter anything

**Steps**:
1. Call the `apply_foundational_filters` tool with:
   ```json
   {}
   ```

**Expected Results**:
- ✅ **All vendors** pass:
  - Initial count: 71
  - Filtered count: 71
  - Eliminated count: 0

**Validation**:
- [ ] No vendors eliminated
- [ ] Works identically to Test 5

---

## Error Cases to Test

### Test 7: Invalid Enum Value

**Goal**: Verify invalid values are handled gracefully

**Steps**:
1. Call the `apply_foundational_filters` tool with:
   ```json
   {
     "table_format": "invalid_format"
   }
   ```

**Expected Results**:
- ❌ Should return an error or ignore invalid value

**Validation**:
- [ ] Error message is clear
- [ ] Or invalid value is silently ignored (treated as undecided)

---

## Integration Test: Full Decision Flow

**Goal**: Verify Phase 1 → Phase 2 → Phase 3 flow works end-to-end

**Steps**:

1. **Phase 1**: Apply foundational filters
   ```json
   {
     "table_format": "iceberg",
     "catalog": "polaris",
     "transformation_strategy": "dbt",
     "query_engine_preference": "low_latency"
   }
   ```

2. **Phase 2**: Apply organizational constraints to Phase 1 survivors
   - Copy `viable_vendors` IDs from Phase 1 output
   - Call `filter_vendors_tier1` with:
     ```json
     {
       "team_size": "standard",
       "budget": "500K-2M",
       "data_sovereignty": "cloud-first",
       "tier_1_requirements": {
         "sql_interface": true
       }
     }
     ```
   - **Note**: This will filter ALL vendors, not just Phase 1 survivors
   - **Future Enhancement**: filter_vendors_tier1 should accept vendor_ids parameter to filter subset

3. **Phase 3**: Score finalists
   - Copy `viable_vendors` IDs from Phase 2 output
   - Call `score_vendors_tier2` with Phase 2 survivor IDs and preferences

**Expected Flow**:
- Phase 1: 71 → ~2-5 vendors (foundational architecture)
- Phase 2: 71 → ~10-15 vendors (organizational constraints)
- Phase 3: Rank top 3-5 by preferences

**Issue Identified**: filter_vendors_tier1 doesn't accept vendor_ids input to filter a subset!
**Workaround**: For now, Phase 1 and Phase 2 are independent. User must manually cross-reference results.

**TODO**: Add `vendor_ids` parameter to `filter_vendors_tier1` to enable sequential filtering

---

## Success Criteria

**Critical (Must Pass)**:
- [ ] Test 1: Iceberg filtering works correctly
- [ ] Test 2: Delta filtering works correctly
- [ ] Test 3: Combined filtering produces <10 vendors
- [ ] Test 5: "Undecided" passes all vendors
- [ ] All elimination reasons are clear and actionable

**Important (Should Pass)**:
- [ ] Test 4: Query engine latency filtering works
- [ ] Test 6: No parameters passes all vendors
- [ ] Vendor counts match expectations (±3 vendors acceptable)

**Nice to Have**:
- [ ] Test 7: Invalid values handled gracefully
- [ ] Integration test: Phase 1 → Phase 2 → Phase 3 flows logically

---

## Troubleshooting

### Issue: Tool not found in Claude Desktop

**Solution**:
1. Restart Claude Desktop
2. Check MCP server configuration in `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
3. Verify server is running with `ps aux | grep security-architect`

### Issue: Unexpected vendor counts

**Solution**:
1. Check vendor database has 71 vendors total
2. Verify all vendors have foundational capability fields populated
3. Review elimination reasons to understand why vendors were filtered

### Issue: Elimination reasons unclear

**Solution**:
1. Check `eliminated_vendors` dictionary in result
2. Each eliminated vendor should have clear reason (e.g., "Delta Lake required but vendor has delta_lake_support=false")
3. If reason is missing, report bug

---

## Reporting Issues

If any test fails, please capture:
1. Test number and description
2. Input parameters used
3. Expected vs actual results
4. Full JSON output from tool call
5. Claude Desktop version

**Submit to**: `.archive/sessions/2025-10-30-foundational-filtering/test-results.md`

---

## Next Steps After Testing

Once all critical tests pass:
1. ✅ Mark "Test Phase 1 filtering end-to-end in Claude Desktop" as complete
2. Move to "Create beta testing guide and feedback template"
3. Recruit 3-5 beta testers for supervised decision interviews
4. Update Blog Post #10 with "Phase 1 filtering operational" status

---

**Last Updated**: October 30, 2025
**Test Status**: ⏳ Awaiting validation in Claude Desktop
