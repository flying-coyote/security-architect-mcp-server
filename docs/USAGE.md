# Usage Guide - Security Architecture Decision Tool

## Quick Start

1. **Visit the tool**: https://flying-coyote.github.io/security-architect-mcp-server/
2. **Answer questions** about your data volume, budget, and architecture preferences
3. **See vendors filter** in real-time as you make selections
4. **Click vendor count** to see all matching vendors at any time
5. **Download report** when you've narrowed to your top candidates

## Decision Flow

The tool guides you through 4 phases to find your ideal security data platform:

### Phase 0: Sizing Constraints (Questions S1-S4)

**Purpose**: Eliminate vendors that can't handle your scale

**S1: Data Volume**
- Slider: 1 GB/day to 100 TB/day
- **Tip**: Consider growth - select higher if you expect 2x growth in 2 years
- **Example**: 500 GB/day eliminates DuckDB (single-process limit)

**S2: Annual Growth Rate**
- Slider: 0% to 300%
- **Tip**: High growth (>100%) favors serverless/elastic platforms
- **Example**: 200% growth → Prefer Athena, BigQuery over self-hosted

**S3: Data Source Count**
- Slider: 1 to 500 sources
- **Tip**: >50 sources requires enterprise ETL
- **Example**: 100 sources → Fivetran, Airbyte become essential

**S4: Retention Requirement**
- Slider: 1 day to 7 years
- **Tip**: Compliance drives this (SOX=7yr, PCI=1yr, GDPR=varies)
- **Example**: 3 years → Need cost-effective cold storage (S3, Blob)

### Phase 1: Foundational Architecture (Questions F0-F4)

**Purpose**: Establish your architectural commitments

**F0: Isolation Pattern**
- **Shared Everything**: Multi-tenant SaaS (Splunk, Sentinel)
- **Isolated Dedicated**: Dedicated clusters (Databricks, Snowflake)
- **Isolated Bring-Your-Own**: Self-hosted (Trino, ClickHouse)
- **Tip**: Pick based on compliance needs, not preferences

**F1: Table Format**
- Apache Iceberg vs. Delta Lake vs. Vendor-specific
- **Tip**: Iceberg = vendor neutrality, Delta = Databricks ecosystem
- **Lock-in alert**: Proprietary formats (Splunk, Sentinel) = high switching costs

**F2: Data Catalog**
- Unity Catalog, Polaris, Nessie, etc.
- **Tip**: Catalog choice locks in ecosystem (Unity = Databricks bias)

**F3: Transformation Layer**
- dbt vs. Spark vs. Vendor-specific
- **Tip**: dbt = portability, Spark = complex logic

**F4: Query Engine Characteristics** (Multi-select)
- SQL interface, streaming, multi-engine, etc.
- **Tip**: Select ALL that you need - this scores vendors, doesn't eliminate

### Phase 2: Organizational Constraints (Questions Q1-Q4)

**Purpose**: Filter based on your team and organization

**Q1: Team Size**
- 0-1 data engineers → Managed services only
- 2-5 → Can handle some self-hosted
- 6+ → Full self-hosted viable
- **Reality check**: Don't overestimate your ops capacity

**Q2: Annual Budget**
- Slider: $50K to $50M
- **Tip**: Include hidden costs (training, ops, integration)
- **Example**: Splunk at 5TB/day = $3-12M (not $500K)

**Q3: Cloud Environment** (Multi-select)
- AWS, Azure, GCP, On-prem, Multi-cloud
- **Tip**: Select ALL that apply - scores vendors by fit

**Q4: Vendor Tolerance**
- Open source preferred vs. Commercial accepted
- **Tip**: OSS = flexibility + ops burden, Commercial = convenience + cost

### Phase 3: Use Cases (Question Q5)

**Purpose**: Score vendors on your specific needs (Multi-select)

- **Real-time dashboards**: Requires fast query engines
- **Ad-hoc hunting**: Needs flexible SQL interface
- **Compliance reporting**: Requires long retention + audit trails
- **Detection engineering**: Needs streaming + low latency

**Tip**: Select ALL that apply - this scores vendors, doesn't filter

## Interactive Features

### Clickable Vendor Count

**What it does**: Click on "79 Vendors Match" to see the full list

**What you see**:
- Filter summary explaining current constraints
- Grid of all matching vendors with:
  - Name, category, and cost range
  - Volume capacity (e.g., "5TB/day", "10K tables")
  - Capability badges (Cloud, Managed, Score)
- Click any vendor to visit their website

**Use cases**:
- Explore alternatives beyond the top 5
- Understand why certain vendors match
- Compare costs at similar volumes
- Discover vendors you hadn't considered

### Volume Context

**What it shows**: Every cost includes data volume capacity

**Examples**:
- "$100K-500K for 5TB/day" (not just "$100K-500K")
- "$50K-300K for 1-5TB/day"
- "$30K-300K for 100TB total storage"

**Why it matters**:
- Understand what you're getting for the price
- Compare vendors at similar scales
- Validate vendor can handle your volume
- Calculate cost efficiency ($/TB)

### Real-time Filtering

**What happens**: Vendor count updates as you answer each question

**Watch for**:
- Big drops (e.g., 79 → 23) = important constraint
- Small changes (79 → 75) = less critical filter
- No change = question doesn't affect current set

**Tip**: Use this to understand which decisions matter most

## Download Report

Click "Download Report" to get a detailed recommendation including:

1. **Architecture Summary**: Your selected isolation, catalog, format, etc.
2. **Top 5 Vendors**: Detailed comparison with pros/cons
3. **Cost Analysis**: TCO projections for each vendor
4. **Performance Implications**: Query speed, overhead, limitations
5. **Production Examples**: Real deployments at similar scale
6. **Next Steps**: How to evaluate finalists with POC testing

## Common Decision Paths

### Small Team, Moderate Budget ($100K-500K)

**Typical selections**:
- Data volume: 100 GB - 1 TB/day
- Team: 0-1 data engineers
- Isolation: Shared Everything (managed SaaS)
- Budget: $100K-500K

**Result**: ~8-12 vendors (Athena, BigQuery, Sentinel, Chronicle)

**Recommendation**: Start with serverless query engines + managed SIEM

### Enterprise, High Volume (5TB+/day)

**Typical selections**:
- Data volume: 5-50 TB/day
- Team: 6+ data engineers
- Isolation: Isolated Dedicated or BYOC
- Budget: $1M-5M+

**Result**: ~5-8 vendors (Databricks, Snowflake, Elastic, CrowdStrike)

**Recommendation**: Invest in lakehouse platform + specialized SIEM

### MSSP Multi-tenant

**Typical selections**:
- Data volume: 10-100 TB/day (aggregated)
- Cloud: Multi-cloud
- Use cases: All (dashboards, hunting, compliance, detection)
- Team: 10+ data engineers

**Result**: ~3-5 vendors (Databricks, ClickHouse, custom Iceberg)

**Recommendation**: Build on Iceberg for customer isolation

## Tips and Best Practices

### Be Honest About Your Team

**Don't**: Select "6+ data engineers" if you have 2 generalists
**Do**: Account for turnover and learning curves

**Reality**: Self-hosted platforms need 24/7 ops coverage

### Budget for Hidden Costs

**Include**:
- Training: $10-50K/year per engineer
- Integration: 20-40% of license cost
- Data transfer: $0.01-0.09/GB (can be huge)
- Support: 15-25% of license annually

**Example**: $500K Splunk license → $750K total first year

### Start Conservative, Grow Later

**Approach**:
1. Start with managed service at small scale
2. Prove value for 6-12 months
3. Re-evaluate with actual data
4. Migrate to self-hosted if ROI justifies ops burden

**Why**: Easier to grow than to downsize

### Use the Modal to Explore

**Workflow**:
1. Answer sizing questions
2. Click vendor count to see what's eliminated
3. Understand why (check filter summary)
4. Adjust if needed
5. Continue through questions

**Benefit**: Transparency builds confidence in recommendations

## Troubleshooting

### "No vendors match my criteria"

**Cause**: Conflicting constraints (e.g., $50K budget + 10TB/day)

**Fix**: Relax budget or reduce volume, or select "Isolated BYOC" for DIY

### "Too many vendors still match"

**Cause**: Haven't specified enough constraints

**Fix**: Answer more questions, especially F0-F4 architectural choices

### "My preferred vendor was eliminated"

**Cause**: Vendor can't meet one of your constraints

**Fix**: Click vendor count modal, check filter summary, identify which constraint eliminated them

### "Costs seem too high"

**Reality check**: Enterprise security data at scale is expensive

**Options**:
1. Reduce retention (1yr instead of 3yr)
2. Reduce volume (sample/filter at source)
3. Choose OSS self-hosted (trade cost for ops)
4. Stagger rollout (start with critical sources)

## Getting Help

- **Documentation**: See README.md for project overview
- **GitHub Issues**: https://github.com/flying-coyote/security-architect-mcp-server/issues
- **Blog**: https://securitydatacommons.substack.com
- **Book**: "Modern Data Stack for Cybersecurity" (source framework)

## Next Steps After Using the Tool

1. **Validate assumptions**: Confirm your volume/growth estimates
2. **Contact vendors**: Request demos from top 3-5 finalists
3. **Run POCs**: Test with your real data (30-60 days)
4. **Check references**: Talk to customers at similar scale
5. **Review contracts**: Watch for hidden costs, lock-in clauses

The tool gets you from 79 vendors to 3-5 finalists. You still need to validate with hands-on testing!