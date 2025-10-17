# Security Architect MCP Server - Claude Skills

**Project**: AI-powered decision support tool (Model Context Protocol server)
**Status**: Phase 2 Active (64→80 vendors, TCO calculator, POC generator)
**Skills**: 2 project-specific + 6 personal skills
**Last Updated**: 2025-10-17

---

## Project-Specific Skills

### 1. mcp-schema-validator
**Purpose**: Validate MCP server schemas against Anthropic's official specification
**Triggers**: "validate schema", "check MCP", "test server", "add tool", "add resource"
**Value**: Catches schema errors before runtime failures during Claude interactions
**Status**: ✅ Active (Phase 1 implementation)

**Key Validations:**
- JSON schema structure compliance
- Tool input schema validation (all properties have "type", enum non-empty)
- Implementation consistency (tool code matches schema declarations)
- Resource/tool/prompt schemas correct
- Error handling patterns verified
- Vendor database schema completeness

**Integration**: Works with systematic-debugger, tdd-enforcer

---

### 2. vendor-data-quality-checker
**Purpose**: Maintain evidence-based quality for 64+ vendor database (expanding to 80)
**Triggers**: "add vendor", "update vendor", "capability score", "vendor database"
**Value**: Prevents marketing hype, ensures evidence-based vendor descriptions
**Status**: ✅ Active (Phase 1 implementation)

**Quality Standards:**
- No marketing hype in descriptions ("revolutionary", "game-changing" prohibited)
- Capability scores (0-5) require Tier 1-3 evidence
- All 9 capability categories scored
- Cost models accurate (per_gb, consumption, subscription, oss, hybrid)
- Production deployments documented for Tier 1 evidence
- Cross-referenced with book Chapter 5 vendor landscape

**Evidence Tier Requirements:**
- Score 5 (Exceptional): Tier 1 evidence (production with metrics)
- Score 4 (Strong): Tier 2-3 evidence (peer-reviewed, expert consensus)
- Score 3 (Adequate): Tier 3 evidence (expert opinion)
- Score 2 (Limited): Tier 4 evidence (vendor claims - marked unvalidated)
- Score 1 (Weak): Tier 5 evidence (theoretical - noted as unvalidated)
- Score 0 (N/A): Feature not supported

**Integration**: Works with mcp-schema-validator, academic-citation-manager, evidence-tier-classifier

---

## Personal Skills Used

From `~/.claude/skills/` (shared across all projects):

1. **systematic-debugger**: 4-phase debugging for MCP runtime errors
2. **tdd-enforcer**: RED-GREEN-REFACTOR for tool implementation
3. **git-workflow-helper**: Conventional commits for MCP development
4. **ultrathink-analyst**: Deep analysis of MCP architecture decisions
5. **academic-citation-manager**: Evidence tier classification for vendor capabilities
6. **voice-consistency-enforcer**: Maintains quality in documentation

---

## MCP Development Workflow

### Adding New Tool
```
1. tdd-enforcer → Write test for tool FIRST
2. Implement tool in src/tools/
3. mcp-schema-validator → Validate JSON schema
4. Run tests (tdd-enforcer enforces test-first)
5. git-workflow-helper → Commit with conventional message
```

### Adding/Updating Vendor
```
1. Research vendor capabilities (gather evidence)
2. vendor-data-quality-checker → Validate quality standards
   - Evidence tier classification
   - No marketing hype
   - All 9 capabilities scored
   - Cost model accurate
3. mcp-schema-validator → Validate JSON structure
4. Cross-reference with book Chapter 5
5. git-workflow-helper → Commit vendor database update
```

### Schema Validation
```
1. Modify server.py, resources/, tools/, or prompts/
2. mcp-schema-validator → Run compliance check
   - JSON schema structure
   - Tool descriptions quality
   - Implementation consistency
   - Error handling
3. Fix any issues flagged
4. tdd-enforcer → Ensure tests exist
5. Test with Claude desktop app
```

---

## Current MCP Project Status

**Phase 2 Progress** (as of Oct 17, 2025):
- 7 MCP tools operational
- 64 vendors in database (expanding to 80)
- 144 tests passing, 87% coverage
- TCO calculator implemented
- POC test suite generator (next)

**MCP Components:**

**Resources** (3):
- vendor://database (64+ security platforms)
- decision://state (architect conversation progress)
- chapter://framework (Chapter 3-4 decision tree)

**Tools** (7):
1. list_vendors() - Browse vendors by category
2. filter_vendors_tier1() - Apply mandatory filters
3. score_vendors_tier2() - Score on preferred capabilities
4. generate_architecture_report() - 8-12 page recommendation
5. match_journey_persona() - Chapter 4 journey match
6. calculate_tco() - 5-year cost projections
7. compare_vendors_tco() - Multi-vendor TCO comparison

**Prompts** (2):
1. decision_interview - 12-step guided questionnaire
2. journey_matching - Persona match explanation

---

## Vendor Database Quality Metrics

**Current Standards** (as of Oct 17, 2025):
- Total vendors: 64 (target: 80)
- Evidence quality: 70%+ Tier 1-3 (production, peer-reviewed, expert consensus)
- Marketing hype tolerance: 0% (strict evidence-based descriptions)
- Capability completeness: 100% (all 9 categories scored)
- Book Chapter 5 cross-reference: 100% consistency required

**9 Capability Categories** (all scored 0-5):
1. query_performance
2. schema_flexibility
3. security_integration
4. data_lake_support
5. real_time_capability
6. cost_efficiency
7. ease_of_use
8. ecosystem_maturity
9. vendor_support

**Cost Models Supported:**
- per_gb: Per-GB storage/query pricing
- consumption: Pay-per-query execution
- subscription: Fixed annual/monthly fees
- oss: Open source (infrastructure costs only)
- hybrid: Mix of subscription + consumption

---

## Integration with Book

**Modern Data Stack for Cybersecurity** (115,500 words):
- Chapter 3: Architectural requirements mapping (filters, scoring)
- Chapter 4: Three architect journeys (Jennifer, Marcus, Priya)
- Chapter 5: Vendor landscape analysis (80+ vendors)
- Chapter 6: Decision framework (quantitative decision tree)

**MCP Server as Interactive Book:**
- Transforms static book content into conversational assistant
- 80+ vendors → 3-5 personalized finalists in 30 minutes
- Decision framework → 12-step guided questionnaire
- Journey personas → Pattern matching to architect context

---

## Skills Implementation Roadmap

**Phase 1: COMPLETE** ✅ (Oct 17, 2025)
- mcp-schema-validator: Prevent runtime schema errors
- vendor-data-quality-checker: Maintain evidence-based quality

**Phase 2: Planned** (Week 4-6, Book Review)
- No MCP-specific skills needed during book review phase
- Focus shifts to book-chapter-consistency-checker (different project)

**Phase 3: Future** (As needed)
- poc-test-plan-generator: Generate vendor-specific test plans (if manual process becomes tedious)
- hypothesis-to-tool-mapper: Link book hypotheses to MCP validation (if cross-reference becomes complex)

---

## Testing & Validation

**Schema Validation Tests:**
```python
# tests/test_mcp_schema.py
- test_list_resources() - Verify resources properly declared
- test_list_tools() - Verify tools have valid schemas
- test_tool_input_validation() - Verify tools validate inputs
- test_vendor_database_schema() - Verify vendor data quality
```

**Quality Standards Tests:**
```python
# tests/test_vendor_quality.py
- test_no_marketing_hype() - Scan for prohibited language
- test_capability_evidence() - Verify scores match evidence tiers
- test_cost_model_accuracy() - Validate pricing structures
- test_book_consistency() - Cross-reference with Chapter 5
```

**Integration Tests:**
```python
# tests/test_mcp_integration.py
- test_full_decision_workflow() - End-to-end architect journey
- test_tco_calculations() - Verify 5-year projections
- test_vendor_filtering() - Tier1 + Tier2 filtering accuracy
```

---

## Quick Reference: Common Tasks

### Validate Schema Before Testing
```bash
# User: "validate MCP schema"
# → mcp-schema-validator activates
# → Checks all tools, resources, prompts
# → Reports issues with priority levels
```

### Add New Vendor
```bash
# User: "add vendor Starburst to database"
# → vendor-data-quality-checker activates
# → Validates evidence tier
# → Checks for marketing hype
# → Ensures all 9 capabilities scored
# → Cross-references book Chapter 5
```

### Update Capability Score
```bash
# User: "update Dremio query_performance to 5"
# → vendor-data-quality-checker activates
# → Requires Tier 1 evidence for score 5
# → Checks production deployment documented
# → Validates against book assessment
```

---

## Community Best Practices Applied

**From Anthropic Official Docs:**
- ✅ Third-person skill descriptions with explicit triggers
- ✅ DO-NOT-ACTIVATE conditions prevent false positives
- ✅ All skills <500 lines (progressive disclosure)
- ✅ Read-only tools for validation skills (guidance, not automated changes)

**From obra/superpowers:**
- ✅ Integration patterns documented
- ✅ Complementary skill sequencing
- ✅ Tool access control appropriate to task

**From Simon Willison Analysis:**
- ✅ Testing mindset (monitor activation patterns)
- ✅ Refinement based on experience
- ✅ Documentation of skill relationships

---

## References

**Official MCP Documentation:**
- Specification: https://modelcontextprotocol.io/docs/specification
- Anthropic SDK: https://github.com/anthropics/anthropic-sdk-python

**Project Documentation:**
- MCP Design: `/home/jerem/security-architect-mcp-server/ULTRATHINK-MCP-SERVER-DESIGN.md`
- Project README: `/home/jerem/security-architect-mcp-server/README.md`
- Book Chapter 5: `/home/jerem/modern-data-stack-for-cybersecurity-book/chapters/05-vendor-landscape.md`

**Personal Skills:**
- `~/.claude/skills/README.md` (6 personal skills available)

**Related Project Skills:**
- `/home/jerem/project1/.claude/skills/` (6 research/knowledge skills)
- `/home/jerem/security-data-literature-review/.claude/skills/` (evidence tier classification)

---

**Implementation**: 2025-10-17 (Phase 1)
**Version**: 1.0
**Next Review**: Phase 2 completion (POC generator, vendor expansion to 80)
