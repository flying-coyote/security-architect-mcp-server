"""
Architecture Report Generator

Generates comprehensive 12-15 page architecture recommendation reports
based on Tier 1-2 filtering results. Produces honest, evidence-based
vendor recommendations with trade-off analysis.

Output format: Markdown (for easy rendering in Claude Desktop)
"""

from datetime import datetime
from typing import Any

from src.models import BudgetRange, DataSovereignty, TeamSize, Vendor, VendorTolerance
from src.tools.filter_vendors import FilterResult
from src.tools.score_vendors import ScoreResult, ScoredVendor


class ArchitectureReport:
    """
    Architecture recommendation report with vendor analysis.

    Structure:
    1. Executive Summary
    2. Organizational Context
    3. Decision Constraints
    4. Vendor Landscape Analysis
    5. Top 3-5 Finalist Recommendations
    6. Honest Trade-off Analysis
    7. Implementation Considerations
    8. Next Steps
    """

    def __init__(
        self,
        filter_result: FilterResult | None = None,
        score_result: ScoreResult | None = None,
        architect_context: dict[str, Any] | None = None,
    ):
        self.filter_result = filter_result
        self.score_result = score_result
        self.architect_context = architect_context or {}
        self.generated_at = datetime.now()

    def generate_markdown(self) -> str:
        """Generate full Markdown report."""
        sections = [
            self._header(),
            self._executive_summary(),
            self._organizational_context(),
            self._decision_constraints(),
            self._vendor_landscape(),
            self._finalists(),
            self._trade_off_analysis(),
            self._implementation_considerations(),
            self._next_steps(),
            self._footer(),
        ]

        return "\n\n".join(sections)

    def _header(self) -> str:
        """Report header with title and metadata."""
        return f"""# Security Architecture Recommendation Report

**Generated**: {self.generated_at.strftime('%B %d, %Y at %I:%M %p')}
**Status**: Draft Recommendation
**Methodology**: Chapter 3 Decision Framework from "Modern Data Stack for Cybersecurity"

---"""

    def _executive_summary(self) -> str:
        """1-2 paragraph executive summary."""
        if not self.filter_result and not self.score_result:
            return """## Executive Summary

This report provides vendor recommendations based on your organizational constraints and technical requirements. The recommendations are derived from an evidence-based filtering process across 54 security data platforms."""

        filtered_count = self.filter_result.filtered_count if self.filter_result else 0
        eliminated_count = self.filter_result.eliminated_count if self.filter_result else 0
        initial_count = self.filter_result.initial_count if self.filter_result else 54

        top_vendor = None
        if self.score_result and self.score_result.scored_vendors:
            top_vendor = self.score_result.scored_vendors[0]

        summary = f"""## Executive Summary

After applying Tier 1 organizational constraints to {initial_count} security data platforms, **{filtered_count} vendors remain viable** for your organization. {eliminated_count} vendors were eliminated due to budget, team capacity, or deployment constraints."""

        if top_vendor:
            summary += f"""

Based on your Tier 2 technical preferences, **{top_vendor.vendor.name}** ranks highest with a {top_vendor.score_percentage:.0f}% match. This report provides detailed analysis of the top 3-5 finalists with honest trade-off discussions to support your decision."""

        return summary

    def _organizational_context(self) -> str:
        """Section 2: Organizational context."""
        context = self.architect_context

        section = """## Organizational Context

This section captures your organization's profile to contextualize the recommendations."""

        # Team size
        team_size = context.get("team_size")
        if team_size:
            team_desc = {
                TeamSize.LEAN: "1-2 engineers (lean team)",
                TeamSize.STANDARD: "3-5 engineers (standard team)",
                TeamSize.LARGE: "6+ engineers (large team)",
            }
            section += f"""

### Team Capacity

**Team Size**: {team_desc.get(team_size, team_size)}

"""
            if team_size == TeamSize.LEAN:
                section += "**Implication**: Platforms requiring high operational complexity (self-managed Kafka, complex SIEM tuning) were eliminated. Focus on managed services and serverless options."
            elif team_size == TeamSize.STANDARD:
                section += "**Implication**: Standard team can handle moderate operational complexity. Self-managed platforms with strong documentation are viable."
            else:
                section += "**Implication**: Large team can handle high operational complexity, including self-hosted Kafka, custom SIEM playbooks, and multi-platform architectures."

        # Budget
        budget = context.get("budget")
        if budget:
            budget_desc = {
                BudgetRange.UNDER_500K: "Under $500K/year",
                BudgetRange.RANGE_500K_2M: "$500K-2M/year",
                BudgetRange.RANGE_2M_10M: "$2M-10M/year",
                BudgetRange.OVER_10M: "Over $10M/year",
            }
            section += f"""

### Budget Constraints

**Annual Budget**: {budget_desc.get(budget, budget)}

"""
            if budget == BudgetRange.UNDER_500K:
                section += "**Implication**: Eliminates enterprise SIEMs (Splunk, QRadar) and high-cost data warehouses. Focus on consumption-based pricing (Athena, BigQuery) and open-source options."
            elif budget == BudgetRange.RANGE_500K_2M:
                section += "**Implication**: Mid-range platforms viable (Dremio, Starburst, Elastic). Carefully evaluate consumption vs. subscription pricing."
            else:
                section += "**Implication**: Enterprise platforms viable. Focus on capabilities over cost, but still evaluate TCO across 5-year horizon."

        # Data sovereignty
        sovereignty = context.get("data_sovereignty")
        if sovereignty:
            sov_desc = {
                DataSovereignty.CLOUD_FIRST: "Cloud-first (prefers cloud-native solutions)",
                DataSovereignty.HYBRID: "Hybrid (requires cloud + on-prem support)",
                DataSovereignty.ON_PREM_ONLY: "On-premises only (regulatory/sovereignty requirement)",
                DataSovereignty.MULTI_REGION: "Multi-region (data residency requirements)",
            }
            section += f"""

### Data Sovereignty

**Requirement**: {sov_desc.get(sovereignty, sovereignty)}

"""
            if sovereignty == DataSovereignty.ON_PREM_ONLY:
                section += "**Implication**: Cloud-only platforms eliminated (Athena, Snowflake, Sentinel). Focus on platforms with on-prem deployment (Splunk, Elastic, Dremio, self-hosted OSS)."
            elif sovereignty == DataSovereignty.CLOUD_FIRST:
                section += "**Implication**: Prioritize cloud-native platforms. On-prem platforms not eliminated but ranked lower."

        # Vendor tolerance
        tolerance = context.get("vendor_tolerance")
        if tolerance:
            tol_desc = {
                VendorTolerance.OSS_FIRST: "Open source first (prefers OSS with commercial support optional)",
                VendorTolerance.OSS_WITH_SUPPORT: "OSS acceptable if vendor provides support",
                VendorTolerance.COMMERCIAL_ONLY: "Commercial only (requires vendor SLA and 24/7 support)",
            }
            section += f"""

### Vendor Relationship Tolerance

**Preference**: {tol_desc.get(tolerance, tolerance)}

"""
            if tolerance == VendorTolerance.COMMERCIAL_ONLY:
                section += "**Implication**: Pure OSS platforms without commercial support eliminated. Focus on vendors with enterprise SLAs."

        return section

    def _decision_constraints(self) -> str:
        """Section 3: Tier 1-2 constraints applied."""
        if not self.filter_result:
            return """## Decision Constraints

No filtering constraints were applied. All 54 vendors are viable."""

        section = """## Decision Constraints Applied

This section documents the mandatory (Tier 1) and preferred (Tier 2) requirements used to filter and score vendors."""

        # Tier 1 filters
        if self.filter_result.eliminated_vendors:
            section += f"""

### Tier 1: Mandatory Filters

These are hard constraints that eliminated vendors outright. **{self.filter_result.eliminated_count} vendors eliminated**.

**Top Elimination Reasons**:
"""
            # Count elimination reasons
            reasons: dict[str, int] = {}
            for reason in self.filter_result.eliminated_vendors.values():
                reasons[reason] = reasons.get(reason, 0) + 1

            for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True)[:5]:
                section += f"\n- **{reason}**: {count} vendors"

        # Tier 2 preferences
        if self.score_result:
            section += f"""

### Tier 2: Preferred Capabilities

These are weighted preferences used to rank remaining vendors. **Max possible score: {self.score_result.max_possible_score}**.

**Your Preferences**:
"""
            # Sort preferences by weight
            prefs = sorted(
                self.score_result.preferences.items(),
                key=lambda x: x[1],
                reverse=True
            )

            weight_desc = {
                3: "Strongly preferred (critical for success)",
                2: "Preferred (important but not critical)",
                1: "Nice-to-have (marginal benefit)",
            }

            for capability, weight in prefs:
                # Format capability name for readability
                cap_display = capability.replace("_", " ").title()
                section += f"\n- **{cap_display}** (weight {weight}): {weight_desc.get(weight, '')}"

        return section

    def _vendor_landscape(self) -> str:
        """Section 4: Overview of vendor landscape after filtering."""
        if not self.filter_result:
            return """## Vendor Landscape Analysis

All 54 vendors across 9 categories remain viable."""

        section = f"""## Vendor Landscape Analysis

After Tier 1 filtering, **{self.filter_result.filtered_count} vendors** remain viable for your organization."""

        # Category breakdown
        if self.filter_result.filtered_vendors:
            categories: dict[str, int] = {}
            for vendor in self.filter_result.filtered_vendors:
                cat = vendor.category.value
                categories[cat] = categories.get(cat, 0) + 1

            section += """

### Vendor Categories (Viable)

"""
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                section += f"- **{cat}**: {count} vendors\n"

        # Eliminated categories
        if self.filter_result.eliminated_vendors:
            section += """

### Notable Eliminations

"""
            # Find high-profile vendors that were eliminated
            high_profile = [
                "splunk-enterprise-security",
                "snowflake",
                "databricks",
                "elastic-security",
                "microsoft-sentinel",
            ]

            for vendor_id in high_profile:
                if vendor_id in self.filter_result.eliminated_vendors:
                    reason = self.filter_result.eliminated_vendors[vendor_id]
                    vendor_name = vendor_id.replace("-", " ").title()
                    section += f"- **{vendor_name}**: {reason}\n"

        return section

    def _finalists(self) -> str:
        """Section 5: Top 3-5 finalist recommendations."""
        if not self.score_result or not self.score_result.scored_vendors:
            return """## Finalist Recommendations

No scoring was performed. Please apply Tier 2 preferences to rank vendors."""

        finalists = self.score_result.get_top_n(5)

        section = f"""## Finalist Recommendations

Based on your Tier 2 preferences, here are the top {len(finalists)} vendors ranked by fit:

---
"""

        for i, scored in enumerate(finalists, 1):
            section += self._vendor_detail(i, scored)
            section += "\n---\n"

        return section

    def _vendor_detail(self, rank: int, scored: ScoredVendor) -> str:
        """Detailed vendor analysis."""
        vendor = scored.vendor

        detail = f"""
### {rank}. {vendor.name}

**Score**: {scored.score}/{scored.max_score} ({scored.score_percentage:.1f}% match)
**Category**: {vendor.category.value}
**Website**: {vendor.website or 'N/A'}

**Description**: {vendor.description}

#### Key Capabilities

"""

        # Highlight scored capabilities
        for capability, points in scored.score_breakdown.items():
            if points > 0:
                cap_display = capability.replace("_", " ").title()
                cap_value = getattr(vendor.capabilities, capability, None)
                detail += f"- ✅ **{cap_display}**: {cap_value} ({points} points)\n"

        # Show missing capabilities
        missing = [cap for cap, points in scored.score_breakdown.items() if points == 0]
        if missing:
            detail += "\n**Missing Capabilities**:\n"
            for capability in missing[:3]:  # Show top 3 missing
                cap_display = capability.replace("_", " ").title()
                detail += f"- ❌ {cap_display}\n"

        # Cost and deployment
        detail += f"""

#### Cost & Deployment

**Cost Model**: {vendor.capabilities.cost_model.value}
**Typical Cost**: {vendor.typical_annual_cost_range or 'Contact vendor'}
**Deployment**: {', '.join([d.value for d in vendor.capabilities.deployment_models])}
**Team Size Required**: {vendor.capabilities.team_size_required.value}
**Operational Complexity**: {vendor.capabilities.operational_complexity}

"""

        # Compliance
        if vendor.capabilities.compliance_certifications:
            detail += f"**Compliance**: {', '.join(vendor.capabilities.compliance_certifications[:5])}\n"

        return detail

    def _trade_off_analysis(self) -> str:
        """Section 6: Honest trade-off analysis."""
        if not self.score_result or not self.score_result.scored_vendors:
            return """## Trade-off Analysis

No trade-off analysis available without scoring results."""

        top_3 = self.score_result.get_top_n(3)

        section = """## Honest Trade-off Analysis

No vendor is perfect. This section provides objective trade-off analysis to help you make an informed decision.

"""

        for i, scored in enumerate(top_3, 1):
            vendor = scored.vendor
            section += f"""
### {vendor.name}

**Strengths**:
"""
            # Identify strengths
            strengths = []
            if vendor.capabilities.operational_complexity == "low":
                strengths.append("Low operational overhead (managed service or serverless)")
            if vendor.capabilities.cost_predictability == "high":
                strengths.append("Predictable costs (subscription or fixed consumption)")
            if vendor.capabilities.sql_interface:
                strengths.append("Standard SQL interface (no proprietary query language)")
            if vendor.capabilities.open_table_format in ["iceberg-native", "iceberg-support"]:
                strengths.append("Open table format (vendor-neutral data format)")
            if vendor.capabilities.multi_cloud:
                strengths.append("Multi-cloud support (avoid cloud vendor lock-in)")

            for strength in strengths[:4]:
                section += f"- {strength}\n"

            section += "\n**Limitations**:\n"

            # Identify limitations
            limitations = []
            if vendor.capabilities.operational_complexity == "high":
                limitations.append("High operational overhead (requires dedicated engineering team)")
            if vendor.capabilities.cost_predictability == "low":
                limitations.append("Unpredictable costs (per-GB pricing can spike)")
            if not vendor.capabilities.sql_interface:
                limitations.append("Proprietary query language (team retraining required)")
            if vendor.capabilities.open_table_format == "proprietary":
                limitations.append("Proprietary format (vendor lock-in risk)")
            if vendor.capabilities.team_size_required == "large":
                limitations.append("Requires large team (6+ engineers for effective operation)")
            if not vendor.capabilities.cloud_native and "cloud" in [d.value for d in vendor.capabilities.deployment_models]:
                limitations.append("Retrofitted for cloud (not cloud-native architecture)")

            for limitation in limitations[:4]:
                section += f"- {limitation}\n"

            section += "\n"

        return section

    def _implementation_considerations(self) -> str:
        """Section 7: Implementation considerations."""
        return """## Implementation Considerations

### Proof of Concept (POC) Testing

Before committing to a vendor, conduct a 30-90 day POC with production-like data:

1. **Data Volume**: Test with realistic log volume (e.g., 1-5TB/day)
2. **Query Performance**: Benchmark typical security queries (threat hunts, compliance reports)
3. **Operational Overhead**: Measure time spent on tuning, maintenance, upgrades
4. **Cost Validation**: Track actual costs vs. vendor estimates
5. **Integration Testing**: Validate SIEM integration, API reliability, export formats

### Migration Strategy

**Phased Approach** (Recommended):
1. **Pilot** (Month 1-2): Deploy with single use case (e.g., CloudTrail logs)
2. **Expand** (Month 3-6): Add additional log sources incrementally
3. **Production** (Month 6-12): Full cutover with legacy system parallel run

**Big Bang** (Higher Risk):
- Only viable if vendor has proven migration tools
- Requires comprehensive testing and rollback plan

### Team Training

**Timeline**: Budget 2-4 weeks for team ramp-up

**Training Areas**:
- Query language (SQL vs. proprietary)
- Detection engineering (writing rules, playbooks)
- Cost optimization (query tuning, data tiering)
- Operational runbooks (incident response, disaster recovery)

### Vendor Negotiation

**Cost Optimization**:
- Request multi-year discount (20-30% typical)
- Negotiate egress fee waivers (critical for multi-cloud)
- Ask for POC credits ($10K-50K common)

**Contract Terms**:
- Ensure exit clause (60-90 day termination notice)
- Negotiate data export format (prefer open formats like Parquet/Iceberg)
- Request SLA commitments (99.9% uptime for critical systems)
"""

    def _next_steps(self) -> str:
        """Section 8: Next steps."""
        if not self.score_result or not self.score_result.scored_vendors:
            return """## Next Steps

1. Apply Tier 2 preferences to rank vendors
2. Review top 3-5 finalists
3. Schedule vendor demos
4. Conduct proof of concept testing
"""

        top_vendor = self.score_result.scored_vendors[0]

        return f"""## Recommended Next Steps

### Immediate (Week 1-2)

1. **Vendor Demos**: Schedule demos with top 3 vendors ({', '.join([sv.vendor.name for sv in self.score_result.get_top_n(3)])})
2. **Reference Calls**: Request customer references in similar industries
3. **Cost Estimates**: Get detailed pricing for your specific volume

### Short-term (Month 1-2)

4. **POC Design**: Define success criteria for 30-day proof of concept
5. **POC Execution**: Deploy {top_vendor.vendor.name} (top-ranked) with production-like data
6. **Cost Validation**: Track actual costs vs. vendor estimates

### Medium-term (Month 3-6)

7. **Vendor Negotiation**: Negotiate pricing, contract terms, SLAs
8. **Migration Planning**: Design phased migration from legacy system
9. **Team Training**: Ramp up SOC team on new platform

### Decision Timeline

**Target Decision Date**: {(self.generated_at.replace(month=self.generated_at.month + 1) if self.generated_at.month < 12 else self.generated_at.replace(year=self.generated_at.year + 1, month=1)).strftime('%B %d, %Y')} (30 days from report generation)

**Decision Criteria**:
- POC success (query performance, operational overhead)
- Cost validation (actual vs. estimated)
- Team confidence (training effectiveness)
"""

    def _footer(self) -> str:
        """Report footer with methodology and disclaimers."""
        return """---

## Methodology

This report was generated using the Chapter 3 decision framework from "Modern Data Stack for Cybersecurity" by Jeremy Wiley. The framework applies:

- **Tier 1 Filtering**: Mandatory organizational constraints (budget, team, sovereignty)
- **Tier 2 Scoring**: Weighted technical preferences (3× strongly preferred, 2× preferred, 1× nice-to-have)
- **Evidence-Based Data**: All vendor capabilities validated from official documentation (2025 data)

## Disclaimers

- **No Vendor Sponsorship**: This tool accepts no vendor payments or sponsorships. All vendor data is publicly sourced.
- **Independent Analysis**: Recommendations based solely on your stated constraints and preferences.
- **Not Financial Advice**: Cost estimates are indicative only. Validate pricing with vendors directly.
- **No Warranty**: Use recommendations as decision support input, not sole decision criteria.

## Feedback

To provide feedback or report inaccuracies:
- **GitHub**: https://github.com/flying-coyote/security-architect-mcp-server/issues
- **Email**: feedback@securitydatacommons.com

---

**Report Version**: 1.0
**Database Version**: Phase 2 (54 vendors)
**Generated with**: Security Architect MCP Server
**License**: Apache 2.0 (code), CC BY-SA 4.0 (report content)
"""

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary for JSON serialization."""
        return {
            "generated_at": self.generated_at.isoformat(),
            "filter_summary": self.filter_result.to_dict() if self.filter_result else None,
            "score_summary": self.score_result.to_dict() if self.score_result else None,
            "architect_context": self.architect_context,
            "markdown": self.generate_markdown(),
        }


def generate_architecture_report(
    filter_result: FilterResult | None = None,
    score_result: ScoreResult | None = None,
    architect_context: dict[str, Any] | None = None,
) -> str:
    """
    Generate architecture recommendation report.

    Args:
        filter_result: Tier 1 filtering results
        score_result: Tier 2 scoring results
        architect_context: Organization profile (team size, budget, etc.)

    Returns:
        Markdown report (12-15 pages)

    Example:
        ```python
        from src.tools.filter_vendors import apply_tier1_filters
        from src.tools.score_vendors import score_vendors_tier2
        from src.tools.generate_report import generate_architecture_report
        from src.utils.database_loader import load_default_database

        db = load_default_database()

        # Apply Tier 1 filters
        filter_result = apply_tier1_filters(
            db,
            team_size=TeamSize.LEAN,
            budget=BudgetRange.UNDER_500K,
            tier_1_requirements={"sql_interface": True}
        )

        # Apply Tier 2 scoring
        score_result = score_vendors_tier2(
            filter_result.filtered_vendors,
            preferences={
                "open_table_format": 3,
                "cloud_native": 2,
                "managed_service_available": 2,
            }
        )

        # Generate report
        report_md = generate_architecture_report(
            filter_result=filter_result,
            score_result=score_result,
            architect_context={
                "team_size": TeamSize.LEAN,
                "budget": BudgetRange.UNDER_500K,
                "data_sovereignty": DataSovereignty.CLOUD_FIRST,
            }
        )

        print(report_md)
        ```
    """
    report = ArchitectureReport(
        filter_result=filter_result,
        score_result=score_result,
        architect_context=architect_context,
    )

    return report.generate_markdown()
