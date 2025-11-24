# Security Data Platform Architecture Decision Tool

Interactive decision tool for filtering 71 security data platforms to 3-5 personalized finalists based on your organizational constraints.

## 🎯 Purpose

Transform the decision framework from "Modern Data Stack for Cybersecurity" book into an accessible web-based tool that filters real vendors based on team size, budget, infrastructure patterns, and technical preferences.

## 🚀 Live Tool

**GitHub Pages URL:** `https://flying-coyote.github.io/security-architect-mcp-server/`

**Local Testing:** `http://localhost:8080/index-v2.html`

## ✨ Features (V3 - Sizing-First + Multi-Select + Sliders)

- **Sizing Constraints First:** 5 sliders (data volume 1 GB-100 TB, growth 0-300%, sources 1-500, retention 1d-7yr, budget $50K-$50M)
- **Architecture-First Ordering:** Sizing → Foundational Architecture → Organizational Constraints → Use Cases
- **Multi-Select Support:** Query engine (F4) and cloud environment (Q3) allow multiple selections (e.g., AWS + Azure + on-prem)
- **Enhanced UX:** Deselectable radio buttons (click to unselect), logarithmic sliders, real-time vendor filtering
- **14 Questions Total:** 5 sliders (S1-S4, Q2), 6 single-select (F0-F3, Q1, Q4), 3 multi-select (F4, Q3, Q5)
- **Actual Vendor Filtering:** 71 vendors filtered to 3-5 finalists based on your answers
- **Top 5 Vendor Display:** See vendor names, descriptions, costs, and capabilities
- **Performance Impact Analysis:** 0% vs 15-50% RLS overhead implications
- **TCO Guidance:** OSS catalogs ($0) vs Unity Catalog ($10K-50K/year)
- **Production Validation:** Examples from Netflix, Huntress, Okta, Arctic Wolf
- **Enhanced Downloadable Report:** Full vendor recommendations with capabilities, costs, and next steps

## 📊 Decision Flow (V3 - Sizing-First Architecture)

```
PHASE 0: SIZING CONSTRAINTS (eliminate by scale)
S1: Data Volume (1 GB - 100 TB/day)
├─ <10 GB/day → DuckDB viable, Splunk overkill
├─ 10-100 GB/day → Most distributed engines viable
├─ 100 GB-1 TB/day → Eliminate single-process engines (DuckDB)
└─ 1+ TB/day → Require distributed query engines (Trino, Spark, ClickHouse)

S2: Annual Growth Rate (0-300%)
├─ <50% → Stable capacity planning
├─ 50-150% → Plan for 2-3× growth
└─ 150%+ → Elastic/serverless strongly preferred

S3: Data Source Count (1-500 sources)
├─ <10 sources → Manual ingestion viable
├─ 10-50 sources → ETL orchestration (Airflow, dbt)
└─ 50+ sources → Enterprise ETL required (Fivetran, Airbyte)

S4: Retention Requirement (1 day - 7 years)
├─ 1-7 days → Real-time detection, hot storage only
├─ 30-90 days → Compliance minimum (GDPR)
├─ 1-2 years → Fraud/forensics investigations
└─ 3-7 years → SOX, HIPAA, financial regulations

PHASE 1: FOUNDATIONAL ARCHITECTURE (establishes commitments)
F0: Isolation Pattern (KEY DECISION)
├─ Isolated (security VPC) → Polaris/Nessie ($0), 0% RLS overhead, Iceberg
├─ Shared (PII+security) → Unity Catalog (REQUIRED), 15-50% overhead, Delta/Iceberg
└─ Multi-tenant MSSP → Unity Catalog (REQUIRED), 5-30% overhead

F1: Table Format Preference
├─ Iceberg → 28 vendors (vendor-neutral, broad support)
├─ Delta Lake → 15 vendors (Databricks ecosystem)
└─ No preference → Derived from F0 isolation pattern

F2: Catalog Strategy
├─ Polaris/Nessie → OSS, $0 cost, isolation-first pattern
├─ Unity Catalog → $10K-50K/year, shared platforms, RLS overhead
└─ AWS Glue/Azure Purview → Cloud-native, managed service

F3: Transformation Approach
├─ dbt Core → SQL-based, OSS, Git workflows
├─ Spark/Flink → Complex transformations, streaming
└─ Cloud ETL → Managed services (Glue, Data Factory)

F4: Query Engine Characteristics (MULTI-SELECT)
□ Low-latency (<3s) → ClickHouse, Pinot
□ High-concurrency (100+ users) → Trino, Presto
□ Serverless (auto-scaling) → Athena, Snowflake
□ Cost-optimized → DuckDB, Parquet + S3

PHASE 2: ORGANIZATIONAL CONSTRAINTS (filter within architecture)
Q1: Team Capacity
├─ Lean (1-2 engineers) → Managed services required
├─ Standard (3-5 engineers) → Hybrid viable
└─ Large (6+ engineers) → Full composable stack manageable

Q2: Annual Budget Slider ($50K - $50M/year)
├─ <$500K → Eliminate Unity Catalog, Databricks, Snowflake, Splunk
├─ $500K-$2M → Balanced OSS + managed services
├─ $2M-$10M → Full vendor landscape available
└─ $10M+ → Cost less constrained

Q3: Cloud Environment (MULTI-SELECT)
□ AWS → AWS-native bonus (Athena, Glue)
□ Azure → Azure-native bonus (Synapse)
□ GCP → GCP-native bonus (BigQuery)
□ Multi-cloud → Cloud-agnostic required (Trino, Iceberg)
□ On-premises → Hybrid support required

Q4: Vendor Relationship Tolerance
├─ OSS-first → Community support, maximum flexibility
├─ OSS with commercial support → Vendor SLAs for OSS products
└─ Commercial only → 24/7 support, legal accountability

PHASE 3: USE CASES (score on fit)
Q5: Primary Use Cases (MULTI-SELECT)
□ Real-time dashboards → ClickHouse (1-3s P95)
□ Ad-hoc hunting → DuckDB (laptop), Trino (team-wide)
□ Compliance reporting → Athena (serverless), Trino (scheduled)
□ Detection rules → Kafka + Flink (streaming)
```

## 🎨 Key Design Decisions (V3)

### Why Sizing-First Ordering?

**Problem with Constraint-First (V2):** Asking team size and budget before sizing wastes time on vendors that can't handle your data volume (e.g., DuckDB for 10 TB/day) or are overkill for small datasets (e.g., Splunk for 1 GB/day).

**Solution (V3):** Size-based elimination FIRST (data volume, growth, sources, retention) → THEN establish foundational architecture → THEN filter on organizational constraints (team, budget, cloud).

**Impact:** Vendors eliminated by scale before asking about preferred table format or budget. Aligns with proven MCP server architecture-first approach.

### Why Multi-Select for Query Engine and Cloud?

**Problem with Single-Select:** Most architectures need MULTIPLE capabilities:
- Query engine: Low-latency dashboards + high-concurrency analysts + serverless reports
- Cloud: AWS production + Azure DR, or AWS + on-prem hybrid

**Solution:** F4 (query engine) and Q3 (cloud environment) use checkboxes (multi-select), vendors SCORED on how many requirements they meet instead of hard filtering.

**Impact:** Better UX - express complex needs (need BOTH low-latency AND high-concurrency), vendors ranked by fit instead of eliminated.

### Why Logarithmic Sliders for Sizing?

**Problem with Fixed Options:** Data volume (0.1 GB - 100 TB) and budget ($50K - $50M) span 6 orders of magnitude. Fixed options (Small/Medium/Large) lack precision.

**Solution:** Logarithmic sliders with labeled markers (1 GB, 10 GB, 100 GB, 1 TB, 10 TB, 100 TB) provide intuitive UX for exponential ranges.

**Impact:** More granular specification, better vendor matching on actual data scale.

### Why Deselectable Radio Buttons?

**Problem with Standard Radios:** Users can't unselect an option once clicked, forcing restart to change answer.

**Solution:** Click-to-deselect pattern using CSS class tracking. Click selected radio → deselects it → returns to unanswered state.

**Impact:** Better UX for exploration and decision refinement.

## 🛠️ Technical Stack

- **Pure Client-Side:** HTML, CSS, JavaScript (no server needed)
- **Vendor Database:** `vendor_database.json` (71 vendors with capabilities matrix)
- **Decision Data:** `decision-data-v3.json` (14 questions: 5 sliders, 6 single-select, 3 multi-select)
- **Hosting:** GitHub Pages (free, fast CDN)
- **Mobile-Responsive:** Works on desktop, tablet, mobile
- **No Dependencies:** Vanilla JS, no frameworks required

## 📁 File Structure

```
docs/
├── index.html                 # V3 default landing page (GitHub Pages entry)
├── index-v2.html              # V3 interactive form (same as index.html)
├── styles-v2.css              # V3 styling: two-column layout, sliders, multi-select
├── decision-tree-v2.js        # V3 filtering logic: 4-phase filtering, multi-select scoring
├── decision-data-v3.json      # V3 sizing-first question ordering (S1-S4, F0-F4, Q1-Q5)
├── vendor_database.json       # 71 vendors with capability matrix
├── README.md                  # This file
└── SUBSTACK-INTEGRATION.md    # Blog integration guide
```

## 🚢 Deployment to GitHub Pages

### Option 1: Automatic (GitHub Settings)

1. **Push to GitHub:**
   ```bash
   git add docs/
   git commit -m "🎯 Decision Tree V3 - Sizing-first + multi-select + sliders"
   git push origin main
   ```

2. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main`
   - Folder: `/docs`
   - Save

3. **Access:**
   - Wait 1-2 minutes for deployment
   - Visit: `https://flying-coyote.github.io/security-architect-mcp-server/`

### Option 2: Test Locally First

```bash
# Navigate to project root
cd /home/jerem/security-architect-mcp-server

# Start simple HTTP server (Python 3) serving docs/
python3 -m http.server 8080 --directory docs

# Open in browser
# http://localhost:8080/index.html (or index-v2.html)
```

Test all questions (sliders, single-select, multi-select), validate vendor filtering, then deploy to GitHub Pages.

## 🔗 Integration with Substack Blog

See `SUBSTACK-INTEGRATION.md` for complete blog integration guide.

### Quick Integration

**Post #11: "How to Filter 71 Security Data Platforms to 3 Finalists in 5 Minutes"**
```markdown
# How to Filter 71 Security Data Platforms to 3 Finalists in 5 Minutes

Before this tool, filtering the security data platform landscape took 2-4 weeks
of vendor research, architecture analysis, and cost modeling.

Now: 14 questions (5 sliders + 9 choices), 5 minutes, 3-5 personalized finalists.

**Try the interactive decision tool →**
https://flying-coyote.github.io/security-architect-mcp-server/

[Screenshot of vendor filtering in action with sliders and multi-select]
```

## 📈 Vendor Filtering Examples

### Example 1: Cost-Conscious Startup
**Sizing:**
- **S1:** 50 GB/day data volume
- **S2:** 100% annual growth
- **S3:** 15 data sources
- **S4:** 90 days retention

**Foundational Architecture:**
- **F0:** Isolated (security VPC)
- **F1:** Iceberg (vendor-neutral)
- **F2:** Polaris (OSS catalog)
- **F3:** dbt Core
- **F4:** High-concurrency + Cost-optimized (multi-select)

**Organizational Constraints:**
- **Q1:** Lean (1-2 engineers)
- **Q2:** $200K budget
- **Q3:** AWS (single cloud)
- **Q4:** OSS-first

**Use Cases:**
- **Q5:** Ad-hoc hunting + Compliance reporting (multi-select)

**Result:** 71 → 8 vendors (DuckDB, Athena, Trino, MinIO, Polaris, Nessie, Iceberg, Parquet)
**Top 3:** DuckDB + Athena + Polaris (total TCO: <$50K/year)

### Example 2: Enterprise MSSP
**Sizing:**
- **S1:** 5 TB/day data volume
- **S2:** 150% annual growth
- **S3:** 200 data sources
- **S4:** 2 years retention

**Foundational Architecture:**
- **F0:** Multi-tenant MSSP
- **F1:** Delta Lake
- **F2:** Unity Catalog (required for RLS)
- **F3:** Spark
- **F4:** Low-latency + High-concurrency + Serverless (multi-select)

**Organizational Constraints:**
- **Q1:** Large (6+ engineers)
- **Q2:** $5M budget
- **Q3:** AWS + Azure (multi-cloud, multi-select)
- **Q4:** Commercial only

**Use Cases:**
- **Q5:** All use cases (dashboards + hunting + compliance + detection, multi-select)

**Result:** 71 → 5 vendors (Databricks, Unity Catalog, Delta Lake, ClickHouse, Kafka)
**Top 3:** Databricks + Unity Catalog + ClickHouse (total TCO: $1.5M-3M/year)

## 🎨 Customization

### Update Vendor Database

Edit `vendor_database.json`:
```json
{
  "vendors": [
    {
      "id": "new-vendor",
      "name": "New Vendor",
      "category": "Query Engine",
      "description": "...",
      "capabilities": {
        "iceberg_support": true,
        "operational_complexity": "low",
        "managed_service_available": true
      },
      "typical_annual_cost_range": "$50K-200K annually"
    }
  ]
}
```

### Add New Questions

Edit `decision-data-v3.json`:
```json
{
  "questions": [
    {
      "id": "q6_new_question",
      "order": 15,
      "section": "Additional Constraints",
      "title": "New Question",
      "type": "single_choice",
      "required": true,
      "options": [...]
    }
  ]
}
```

For sliders, use:
```json
{
  "id": "s5_new_sizing",
  "order": 5,
  "section": "Sizing Constraints",
  "title": "New Slider",
  "type": "slider",
  "min": 1,
  "max": 1000,
  "default": 100,
  "scale": "logarithmic",
  "unit": "TB/day",
  "markers": [1, 10, 100, 1000]
}
```

### Styling

Edit `styles-v2.css`:
```css
:root {
    --primary-color: #2563eb;  /* Change primary color */
    --secondary-color: #10b981;
}
```

## 🤝 Contributing

This tool is part of the Security Data Commons project. Improvements welcome:

1. Fork repository
2. Create feature branch
3. Test changes locally (`python3 -m http.server 8080 --directory docs`)
4. Submit pull request

## 📄 License

- **Code:** Apache 2.0 (open source)
- **Content:** CC BY-SA 4.0 (attribution required)
- **Vendor Database:** Evidence-based from book research (no vendor sponsorships)

## 📚 Related Resources

- **Blog:** https://securitydatacommons.substack.com
- **Book:** "Modern Data Stack for Cybersecurity" by Jeremy Wiley
- **GitHub:** https://github.com/flying-coyote/security-architect-mcp-server
- **MCP Server:** Conversational decision support (Claude Desktop integration)

## 🐛 Issues & Feedback

Report issues: https://github.com/flying-coyote/security-architect-mcp-server/issues

---

**Generated with:** Claude Code via Happy
**Last Updated:** 2025-11-24 (V3 release: sizing-first + multi-select + sliders)
