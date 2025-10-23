# Contributing to Security Architect MCP Server

Thank you for your interest in contributing to the Security Architect MCP Server! This project helps cybersecurity architects filter 80+ security data platforms to 3-5 personalized finalists in 30 minutes.

## Ways to Contribute

### 1. Vendor Database Updates

The vendor database (`data/vendor_database.json`) is the heart of this project. We welcome contributions that improve vendor data quality.

#### Adding a New Vendor

**Prerequisites:**
- Vendor must be a security data platform (SIEM, query engine, lakehouse, catalog, streaming, etc.)
- Evidence-based capability assessment required (no marketing hype)
- Production deployment validation preferred

**Process:**

1. **Fork the repository** and create a feature branch:
   ```bash
   git checkout -b vendor/add-[vendor-name]
   ```

2. **Research the vendor** using evidence-based sources:
   - Production deployments (Tier 1 evidence - best)
   - Peer-reviewed research, industry benchmarks (Tier 2 evidence)
   - Expert consensus, framework inclusion (Tier 3 evidence)
   - Vendor documentation only (Tier 4 - mark as unvalidated)

3. **Add vendor entry** to `data/vendor_database.json`:
   ```json
   {
     "id": "vendor_XXX",
     "name": "Vendor Name",
     "category": "query_engine|lakehouse|siem|streaming|catalog|observability|governance|integration|storage",
     "cost_model": "per_gb|consumption|subscription|oss|hybrid",
     "tier1_filters": {
       "min_budget": 50000,
       "min_team_size": "small|medium|large",
       "supports_on_prem": true,
       "supports_cloud": true,
       "data_sovereignty_compliant": true
     },
     "tier2_capabilities": {
       "query_performance": 0-5,
       "schema_flexibility": 0-5,
       "security_integration": 0-5,
       "data_lake_support": 0-5,
       "real_time_capability": 0-5,
       "cost_efficiency": 0-5,
       "ease_of_use": 0-5,
       "ecosystem_maturity": 0-5,
       "vendor_support": 0-5
     },
     "description": "Evidence-based description with specific metrics, known limitations, and use case scope. No marketing hype.",
     "evidence_tier": 1-5,
     "production_deployments": ["Enterprise A (2024)", "Enterprise B (2024)"],
     "evidence_sources": [
       {
         "url": "https://example.com/case-study",
         "title": "Production Deployment Case Study",
         "tier": "A"
       }
     ],
     "last_validated": "2025-10-23"
   }
   ```

4. **Run validation tests**:
   ```bash
   pytest tests/test_vendor_database.py -v
   python3 -m src.server  # Verify MCP server loads
   ```

5. **Submit pull request** with:
   - Vendor name in PR title: "Add vendor: [Vendor Name]"
   - Evidence sources cited
   - Rationale for capability scores
   - Production deployment validation (if available)

#### Updating Existing Vendor Data

**Valid reasons to update:**
- ✅ New production deployment validation discovered
- ✅ Vendor pricing model changed
- ✅ Capability improvements with evidence
- ✅ Vendor acquisition/sunset/deprecation
- ✅ Evidence tier upgrade (Tier 3 → Tier 1 with new validation)

**Invalid updates:**
- ❌ Marketing claims without evidence
- ❌ Capability score inflation without validation
- ❌ Vendor self-promotion
- ❌ Competitive downgrading of rivals

**Process:**
1. Fork and create branch: `vendor/update-[vendor-name]`
2. Update vendor entry with evidence
3. Document evidence sources in PR description
4. Run validation tests
5. Submit PR with rationale

### 2. Bug Reports

Found a bug? Please report it!

**Good bug reports include:**
- MCP server version (git commit hash)
- Python version (`python3 --version`)
- Operating system
- Steps to reproduce
- Expected vs. actual behavior
- Error messages (full stack trace)

**Where to report:**
- GitHub Issues: https://github.com/flying-coyote/security-architect-mcp-server/issues

### 3. Feature Requests

Have an idea for improvement? We'd love to hear it!

**Good feature requests include:**
- Problem statement (what pain point does this solve?)
- Proposed solution (how would it work?)
- Use case (who would benefit?)
- Alternatives considered

**Scope boundaries:**
- ✅ MCP tools, resources, prompts
- ✅ Vendor database improvements
- ✅ Report generation enhancements
- ✅ Decision interview improvements
- ❌ Web UI (out of scope - MCP only)
- ❌ SaaS product features (research tool only)
- ❌ Vendor-specific integrations (vendor-neutral requirement)

### 4. Documentation Improvements

Documentation PRs are always welcome!

**Areas needing improvement:**
- Setup instructions (SETUP.md)
- Usage examples
- Vendor database schema documentation
- MCP tool descriptions

### 5. Code Contributions

**Before starting:**
- Open an issue to discuss your proposed changes
- Ensure it aligns with project scope (see PROJECT-BRIEF.md)
- Check existing issues/PRs for duplicates

**Development setup:**
```bash
# Clone repository
git clone https://github.com/flying-coyote/security-architect-mcp-server.git
cd security-architect-mcp-server

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linters
black src/ tests/
ruff check src/ tests/
mypy src/
```

**Code quality standards:**
- Python 3.10+ type hints throughout
- Black formatting (100 char line length)
- Ruff linting (pycodestyle, pyflakes, isort)
- 80%+ test coverage (pytest with coverage)
- Evidence-based vendor data (no marketing hype)

**Pull request process:**
1. Fork the repository
2. Create feature branch: `feature/your-feature-name`
3. Write tests FIRST (TDD - test-driven development)
4. Implement feature
5. Run full test suite: `pytest`
6. Run linters: `black src/ tests/ && ruff check src/ tests/`
7. Update documentation if needed
8. Submit PR with clear description

## Quality Standards

### Evidence-Based Vendor Data

All vendor capability scores must be evidence-based:

**Score 5 (Exceptional)**: Tier 1 evidence (production deployments with metrics)
**Score 4 (Strong)**: Tier 2 evidence (peer-reviewed research, benchmarks)
**Score 3 (Adequate)**: Tier 3 evidence (expert consensus, framework inclusion)
**Score 2 (Limited)**: Tier 4 evidence (vendor claims only - mark as unvalidated)
**Score 1 (Weak)**: Tier 5 evidence (theoretical - note "unvalidated in production")
**Score 0 (N/A)**: Not supported or not applicable

### Marketing Hype Detection

**RED FLAGS (will be rejected):**
- ❌ "Revolutionary", "game-changing", "transformative"
- ❌ "Best-in-class", "industry-leading", "world-class"
- ❌ "Unmatched", "unparalleled", "unprecedented"
- ❌ Vague benefits without numbers
- ❌ Superlatives without comparisons

**REQUIRED SPECIFICS:**
- ✅ Quantitative metrics (QPS, latency, cost)
- ✅ Known limitations documented
- ✅ Scope boundaries ("Best for X, not suitable for Y")
- ✅ Evidence tier classification
- ✅ Trade-offs acknowledged

### Vendor Neutrality

This project maintains strict vendor neutrality:

- **No vendor sponsorships accepted** (credibility requirement)
- **Equal treatment in filtering logic** (all vendors use same algorithm)
- **Capability matrix based on evidence** (not vendor relationships)
- **Cost data verified from public sources** (no hidden vendor deals)

**If you work for a vendor:**
- You may submit updates for your vendor, but they will be held to the same evidence standards as all others
- Capability scores must cite independent validation (Tier 1-3 evidence)
- Marketing language will be rejected
- Competitive comparisons must be fair and evidence-based

## Code of Conduct

**Be respectful:**
- Assume good intent
- Constructive criticism only
- No personal attacks
- No vendor advocacy or competitive attacks

**Be honest:**
- Evidence-based claims only
- Acknowledge limitations
- Cite sources
- Admit uncertainty when appropriate

**Be collaborative:**
- Help reviewers understand your changes
- Accept feedback gracefully
- Iterate based on review comments
- Test thoroughly before submitting

## License

By contributing, you agree that your contributions will be licensed under:
- **Code**: Apache 2.0 License (permissive open source)
- **Vendor Database**: CC BY-SA 4.0 (Creative Commons Attribution-ShareAlike)

See LICENSE and data/LICENSE for full terms.

## Questions?

- **GitHub Issues**: https://github.com/flying-coyote/security-architect-mcp-server/issues
- **Documentation**: README.md, docs/SETUP.md, docs/archive/ULTRATHINK-MCP-SERVER-DESIGN.md
- **Project Brief**: PROJECT-BRIEF.md (comprehensive project context)

---

**Thank you for contributing to the Security Architect MCP Server!** Your evidence-based vendor data improvements help cybersecurity architects worldwide make better platform decisions.
