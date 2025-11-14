# Security Data Platform Architecture Decision Tool

Interactive decision tree for filtering 71 security data platforms to 3-5 finalists in 5 minutes.

## 🎯 Purpose

Transform the decision framework from "Modern Data Stack for Cybersecurity" book into an accessible web-based tool that architects can use to make evidence-based architecture decisions.

## 🚀 Live Tool

**GitHub Pages URL:** `https://flying-coyote.github.io/security-architect-mcp-server/`

## ✨ Features

- **5-Question Progressive Disclosure:** Infrastructure isolation → table format → catalog → transformation → query engine
- **Real-time Vendor Filtering:** See compatible vendor count update as you answer questions
- **Personalized Recommendations:** Get architecture stack recommendations based on your isolation pattern
- **Performance Impact Analysis:** Understand 0% vs 15-50% RLS overhead implications
- **TCO Guidance:** Low vs High cost implications for catalog choices
- **Production Validation:** Examples from Netflix, Huntress, Okta
- **Downloadable Report:** Export text report with your recommendations

## 📊 Decision Flow

```
Question F0: Isolation Pattern (most important)
├─ Isolated dedicated → Polaris/Nessie (0% overhead, low TCO)
├─ Shared corporate → Unity Catalog (15-50% overhead, high TCO)
└─ Multi-tenant MSSP → Unity Catalog (5-30% overhead, essential)

Question F1: Table Format
├─ Iceberg (28 vendors, broad query engine support)
├─ Delta Lake (15 vendors, Databricks ecosystem)
├─ Hudi (8 vendors, CDC focus)
└─ Proprietary (12 vendors, vendor lock-in)

Question F2: Catalog
├─ Polaris (12 vendors, vendor-neutral, best for isolated)
├─ Unity Catalog (18 vendors, fine-grained access, required for shared)
├─ Nessie (8 vendors, Git workflows)
├─ AWS Glue (10 vendors, AWS-native)
└─ Hive Metastore (15 vendors, legacy)

Question F3: Transformation
├─ dbt (25 vendors, SQL-based)
├─ Spark (30 vendors, PySpark/Scala)
├─ Vendor built-in (20 vendors, SPL/KQL)
└─ Custom Python (15 vendors, Pandas/Polars)

Question F4: Query Engine
├─ Low-latency (10 vendors, ClickHouse <1s)
├─ High concurrency (15 vendors, Trino 100+ queries)
├─ Serverless (5 vendors, Athena no-ops)
└─ Cost-optimized (8 vendors, DuckDB efficiency)
```

## 🛠️ Technical Stack

- **Pure Client-Side:** HTML, CSS, JavaScript (no server needed)
- **Data:** JSON decision tree (`decision-data.json`)
- **Hosting:** GitHub Pages (free, fast CDN)
- **Mobile-Responsive:** Works on desktop, tablet, mobile
- **No Dependencies:** Vanilla JS, no frameworks required

## 📁 File Structure

```
docs/
├── index.html          # Main HTML structure
├── styles.css          # Responsive CSS styling
├── decision-tree.js    # Interactive logic
├── decision-data.json  # Decision tree data
└── README.md           # This file
```

## 🚢 Deployment to GitHub Pages

### Option 1: Automatic (GitHub Settings)

1. **Push to GitHub:**
   ```bash
   git add docs/
   git commit -m "Add interactive decision tree for GitHub Pages"
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
# Navigate to docs directory
cd docs/

# Start simple HTTP server (Python 3)
python3 -m http.server 8000

# Open in browser
# http://localhost:8000
```

Test all questions, validate recommendations, then deploy to GitHub Pages.

## 🔗 Integration with Substack Blog

### Blog Post Strategy

**Post #11: "The Isolation-First Security Pattern"**
```markdown
# The Isolation-First Security Pattern

When security data lives on isolated infrastructure (dedicated VPC/VNet),
architectural decisions shift dramatically...

[Continue with analysis]

**Try the interactive decision tool →**
https://flying-coyote.github.io/security-architect-mcp-server/

[Screenshot of decision tree]
```

**Post #12: "Catalog Selection Guide: Polaris vs Unity Catalog vs Nessie"**
```markdown
# Catalog Selection Guide

Your isolation pattern determines which catalog is optimal...

**Explore catalog recommendations →**
https://flying-coyote.github.io/security-architect-mcp-server/

Filter 71 vendors to your personalized finalists in 5 minutes.
```

### Embedding Options

Since Substack doesn't support iframe embeds, use:

1. **Call-to-action link:** Prominent link to decision tool
2. **Static screenshot:** Screenshot of decision tree UI
3. **QR code:** For newsletter readers to scan
4. **Button graphic:** Design custom CTA button image

## 📈 Analytics (Optional)

Add Google Analytics or Plausible to track:
- Page visits
- Question completion rate
- Popular architecture patterns
- Download report clicks

## 🎨 Customization

### Update Vendor Counts

Edit `decision-data.json`:
```json
{
  "options": [
    {
      "vendor_count_estimate": 45  // Update based on latest data
    }
  ]
}
```

### Add New Questions

Add to `questions` array in `decision-data.json`:
```json
{
  "id": "f5_new_question",
  "order": 6,
  "title": "New Decision Point",
  "options": [...]
}
```

### Styling

Edit `styles.css`:
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
3. Test changes locally
4. Submit pull request

## 📄 License

- **Code:** Apache 2.0 (open source)
- **Content:** CC BY-SA 4.0 (attribution required)
- **Data:** Evidence-based from book research (no vendor sponsorships)

## 📚 Related Resources

- **Blog:** https://securitydatacommons.substack.com
- **Book:** "Modern Data Stack for Cybersecurity" by Jeremy Wiley
- **GitHub:** https://github.com/flying-coyote/security-architect-mcp-server

## 🐛 Issues & Feedback

Report issues: https://github.com/flying-coyote/security-architect-mcp-server/issues

---

**Generated with:** Claude Code
**Last Updated:** 2025-11-14
