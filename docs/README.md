# Security Data Platform Architecture Decision Tool

Interactive decision tool for filtering 71 security data platforms to 3-5 personalized finalists based on your organizational constraints.

## 🎯 Purpose

Transform the decision framework from "Modern Data Stack for Cybersecurity" book into an accessible web-based tool that filters real vendors based on team size, budget, infrastructure patterns, and technical preferences.

## 🚀 Live Tool

**GitHub Pages URL:** `https://flying-coyote.github.io/security-architect-mcp-server/`

**Local Testing:** `http://localhost:8080/index-v2.html`

## ✨ Features (V2 - Constraint-First Design)

- **Single-Page Interactive Form:** All 7 questions visible, recommendations update in real-time
- **Constraint-First Filtering:** Team size, budget, and infrastructure constraints eliminate vendors BEFORE architecture preferences
- **Actual Vendor Filtering:** 71 vendors filtered to 3-5 finalists based on your answers
- **Top 5 Vendor Display:** See vendor names, descriptions, costs, and capabilities
- **Multi-Select Use Cases:** Security teams have multiple workloads (dashboards + hunting + compliance)
- **Derived Isolation Pattern:** Tool determines isolation pattern from "Do you have PII on same platform?" question
- **Performance Impact Analysis:** 0% vs 15-50% RLS overhead implications
- **TCO Guidance:** OSS catalogs ($0) vs Unity Catalog ($10K-50K/year)
- **Production Validation:** Examples from Netflix, Huntress, Okta, Arctic Wolf
- **Enhanced Downloadable Report:** Full vendor recommendations with capabilities, costs, and next steps

## 📊 Decision Flow (V2 - Constraint-First)

```
ORGANIZATIONAL CONSTRAINTS (eliminate vendors first)
Q1: Team Capacity
├─ Lean (1-2 engineers) → Eliminate 30 self-managed complex solutions
├─ Standard (3-5 engineers) → Hybrid architectures viable
└─ Large (6+ engineers) → Full composable stack manageable

Q2: Annual Budget
├─ <$500K → Eliminate Unity Catalog, Databricks, Snowflake, Splunk (−25 vendors)
├─ $500K-$2M → Balanced OSS + managed services
├─ $2M-$10M → Full vendor landscape available
└─ $10M+ → Cost less constrained

INFRASTRUCTURE PATTERN (derives isolation)
Q3: Data Co-location (KEY QUESTION)
├─ Isolated (security VPC) → Polaris/Nessie ($0), 0% RLS overhead, Iceberg
├─ Shared (PII+security) → Unity Catalog (REQUIRED), 15-50% overhead, Delta/Iceberg
└─ Multi-tenant MSSP → Unity Catalog (REQUIRED), 5-30% overhead

Q4: Cloud Environment
├─ AWS → AWS-native bonus (Athena, Glue)
├─ Azure → Azure-native bonus (Synapse)
├─ GCP → GCP-native bonus (BigQuery)
├─ Multi-cloud → Cloud-agnostic required (−15 vendors)
└─ On-premises → Eliminate cloud-only vendors (−35 vendors)

WORKLOAD REQUIREMENTS (multi-select)
Q5: Primary Use Cases (SELECT ALL THAT APPLY)
├─ Real-time dashboards → ClickHouse (1-3s P95)
├─ Ad-hoc hunting → DuckDB (laptop), Trino (team-wide)
├─ Compliance reporting → Athena (serverless), Trino (scheduled)
└─ Detection rules → Kafka + Flink (streaming)

ARCHITECTURE PREFERENCES (post-filtering)
Q6: Table Format Preference
├─ Iceberg → 28 vendors (vendor-neutral, broad support)
├─ Delta Lake → 15 vendors (Databricks ecosystem)
└─ No preference → Let tool decide based on isolation pattern

Q7: Vendor Relationship Tolerance
├─ OSS-first → Community support, maximum flexibility
├─ OSS with commercial support → Vendor SLAs for OSS products
└─ Commercial only → 24/7 support, legal accountability
```

## 🎨 Key Design Decisions (V2)

### Why Constraint-First Ordering?

**Problem with Architecture-First:** Asking "Do you prefer Iceberg or Delta Lake?" before budget/team constraints wastes time recommending unaffordable solutions.

**Solution:** Filter on constraints first (team, budget, sovereignty) → THEN ask architecture preferences on remaining viable vendors.

### Why Derive Isolation Pattern?

**Problem with Direct Question:** Users don't know what "isolation-first security pattern" means when researching architectures.

**Solution:** Ask concrete question ("Do you have PII on same platform as security logs?") and DERIVE isolation pattern from answer.

### Why Multi-Select for Use Cases?

**Problem:** Security teams don't have ONE primary use case—they need dashboards AND hunting AND compliance.

**Solution:** Q5 uses checkboxes (multi-select) to capture all workloads, then recommends architecture supporting ALL requirements.

## 🛠️ Technical Stack

- **Pure Client-Side:** HTML, CSS, JavaScript (no server needed)
- **Vendor Database:** `vendor_database.json` (71 vendors with capabilities matrix)
- **Decision Data:** `decision-data-v2.json` (7 questions, constraint-first ordering)
- **Hosting:** GitHub Pages (free, fast CDN)
- **Mobile-Responsive:** Works on desktop, tablet, mobile
- **No Dependencies:** Vanilla JS, no frameworks required

## 📁 File Structure

```
docs/
├── index-v2.html              # V2 single-page interactive form
├── styles-v2.css              # V2 two-column layout (questions + live recommendations)
├── decision-tree-v2.js        # V2 real-time filtering + vendor display
├── decision-data-v2.json      # V2 constraint-first question ordering
├── vendor_database.json       # 71 vendors with capability matrix
├── README.md                  # This file
└── SUBSTACK-INTEGRATION.md    # Blog integration guide
```

## 🚢 Deployment to GitHub Pages

### Option 1: Automatic (GitHub Settings)

1. **Push to GitHub:**
   ```bash
   git add docs/
   git commit -m "🚀 V2 decision tree: constraint-first + actual vendor filtering"
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
   - Visit: `https://flying-coyote.github.io/security-architect-mcp-server/index-v2.html`

### Option 2: Test Locally First

```bash
# Navigate to project root
cd /home/jerem/security-architect-mcp-server

# Start simple HTTP server (Python 3) serving docs/
python3 -m http.server 8080 --directory docs

# Open in browser
# http://localhost:8080/index-v2.html
```

Test all questions, validate vendor filtering, then deploy to GitHub Pages.

## 🔗 Integration with Substack Blog

See `SUBSTACK-INTEGRATION.md` for complete blog integration guide.

### Quick Integration

**Post #11: "How to Filter 71 Security Data Platforms to 3 Finalists in 5 Minutes"**
```markdown
# How to Filter 71 Security Data Platforms to 3 Finalists in 5 Minutes

Before this tool, filtering the security data platform landscape took 2-4 weeks
of vendor research, architecture analysis, and cost modeling.

Now: 7 questions, 5 minutes, 3-5 personalized finalists.

**Try the interactive decision tool →**
https://flying-coyote.github.io/security-architect-mcp-server/index-v2.html

[Screenshot of vendor filtering in action]
```

## 📈 Vendor Filtering Examples

### Example 1: Cost-Conscious Startup
- **Q1:** Lean (1-2 engineers)
- **Q2:** <$500K budget
- **Q3:** Isolated (security VPC)
- **Q4:** AWS
- **Q5:** Ad-hoc hunting + Compliance reporting
- **Q6:** Iceberg
- **Q7:** OSS-first

**Result:** 71 → 8 vendors (DuckDB, Athena, Trino, MinIO, Polaris, Nessie, Iceberg, Parquet)
**Top 3:** DuckDB + Athena + Polaris (total TCO: <$50K/year)

### Example 2: Enterprise MSSP
- **Q1:** Large (6+ engineers)
- **Q2:** $2M-$10M budget
- **Q3:** Multi-tenant MSSP
- **Q4:** Multi-cloud
- **Q5:** All use cases (dashboards + hunting + compliance + detection)
- **Q6:** Delta Lake
- **Q7:** Commercial only

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

Edit `decision-data-v2.json`:
```json
{
  "questions": [
    {
      "id": "q8_new_constraint",
      "order": 8,
      "section": "Additional Constraints",
      "title": "New Question",
      "type": "single_choice",
      "required": true,
      "options": [...]
    }
  ]
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
**Last Updated:** 2025-11-14 (V2 release: constraint-first + vendor filtering)
