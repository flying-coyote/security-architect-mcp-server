"""
Journey Persona Matching

Matches architect's organizational context to Chapter 4 journey personas
from "Modern Data Stack for Cybersecurity" book:

- **Jennifer**: Cloud-native startup, 5-person team, $500K-2M budget
- **Marcus**: Financial services SOC, 2-person team, <$500K budget, on-prem
- **Priya**: Enterprise security architect, 8-person team, $2M+ budget

Helps architects identify relevant case studies and architecture patterns.
"""

from typing import Any

from src.models import BudgetRange, DataSovereignty, DecisionState, TeamSize, VendorTolerance


class JourneyMatch:
    """
    Journey persona match result.

    Attributes:
        persona: Matched persona name (jennifer, marcus, priya, hybrid)
        confidence: Match confidence 0-100%
        reasoning: Explanation of why this persona matched
        architecture_pattern: Recommended architecture pattern from book
        key_constraints: Key constraints that drove the match
    """

    def __init__(
        self,
        persona: str,
        confidence: float,
        reasoning: str,
        architecture_pattern: str,
        key_constraints: list[str],
    ):
        self.persona = persona
        self.confidence = confidence
        self.reasoning = reasoning
        self.architecture_pattern = architecture_pattern
        self.key_constraints = key_constraints

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "persona": self.persona,
            "confidence": round(self.confidence, 1),
            "reasoning": self.reasoning,
            "architecture_pattern": self.architecture_pattern,
            "key_constraints": self.key_constraints,
        }

    def summary(self) -> str:
        """Generate human-readable summary."""
        return f"Journey Match: {self.persona.title()} ({self.confidence:.0f}% confidence)"


# ============================================================================
# JOURNEY PERSONAS (from Chapter 4)
# ============================================================================

JENNIFER_PROFILE = {
    "name": "Jennifer - Cloud-Native Startup",
    "team_size": TeamSize.STANDARD,  # 5 engineers
    "budget": BudgetRange.RANGE_500K_2M,  # $500K-2M
    "data_sovereignty": DataSovereignty.CLOUD_FIRST,  # Cloud-native
    "vendor_tolerance": VendorTolerance.OSS_WITH_SUPPORT,  # OSS acceptable
    "architecture_pattern": "Cloud-Native Lakehouse",
    "description": """Jennifer leads security at a fast-growing startup. She needs:
- Scalable, cloud-native solutions
- Managed services to reduce operational overhead
- Open formats to avoid vendor lock-in
- Mid-range budget ($500K-2M)
- 5-person engineering team""",
    "recommended_vendors": ["Amazon Athena", "Dremio", "Starburst", "Databricks", "Snowflake"],
}

MARCUS_PROFILE = {
    "name": "Marcus - Financial Services SOC",
    "team_size": TeamSize.LEAN,  # 2 engineers
    "budget": BudgetRange.UNDER_500K,  # <$500K
    "data_sovereignty": DataSovereignty.ON_PREM_ONLY,  # Regulatory requirements
    "vendor_tolerance": VendorTolerance.COMMERCIAL_ONLY,  # Need vendor support
    "architecture_pattern": "Hybrid On-Prem/Cloud SIEM",
    "description": """Marcus runs a 2-person SOC at a regional bank. He needs:
- Cost-effective solutions (<$500K)
- On-premises deployment (regulatory requirement)
- Low operational complexity (lean team)
- Vendor support and SLAs
- Compliance certifications (FedRAMP, SOC2)""",
    "recommended_vendors": ["Elastic Security", "Dremio", "Apache Drill", "Trino"],
}

PRIYA_PROFILE = {
    "name": "Priya - Enterprise Security Architect",
    "team_size": TeamSize.LARGE,  # 8+ engineers
    "budget": BudgetRange.RANGE_2M_10M,  # $2M-10M
    "data_sovereignty": DataSovereignty.HYBRID,  # Multi-region, hybrid cloud
    "vendor_tolerance": VendorTolerance.COMMERCIAL_ONLY,  # Enterprise support required
    "architecture_pattern": "Enterprise Data Mesh",
    "description": """Priya architects security data platforms for a Fortune 500. She needs:
- Enterprise-grade platforms with full support
- Multi-cloud, hybrid deployment
- Advanced capabilities (ML, UEBA, threat intelligence)
- Large budget ($2M+)
- 8+ person engineering team
- Global scale and compliance""",
    "recommended_vendors": ["Splunk Enterprise Security", "Databricks", "Snowflake", "Denodo", "Securonix"],
}


# ============================================================================
# MATCHING LOGIC
# ============================================================================


def calculate_match_score(
    architect_context: dict[str, Any],
    persona_profile: dict[str, Any],
) -> tuple[float, list[str]]:
    """
    Calculate match score between architect context and persona profile.

    Returns:
        Tuple of (score 0-100, list of matching constraints)
    """
    score = 0.0
    max_score = 0.0
    matching_constraints = []

    # Team size (weight: 25 points)
    max_score += 25
    team_size = architect_context.get("team_size")
    if team_size == persona_profile["team_size"]:
        score += 25
        matching_constraints.append(f"Team size: {team_size.value}")
    elif team_size and persona_profile["team_size"]:
        # Partial credit for adjacent team sizes
        team_order = [TeamSize.LEAN, TeamSize.STANDARD, TeamSize.LARGE]
        architect_idx = team_order.index(team_size)
        persona_idx = team_order.index(persona_profile["team_size"])
        if abs(architect_idx - persona_idx) == 1:
            score += 12.5  # Half credit for adjacent
            matching_constraints.append(f"Team size: {team_size.value} (close to {persona_profile['team_size'].value})")

    # Budget (weight: 30 points)
    max_score += 30
    budget = architect_context.get("budget")
    if budget == persona_profile["budget"]:
        score += 30
        matching_constraints.append(f"Budget: {budget.value}")
    elif budget and persona_profile["budget"]:
        # Partial credit for adjacent budgets
        budget_order = [BudgetRange.UNDER_500K, BudgetRange.RANGE_500K_2M, BudgetRange.RANGE_2M_10M, BudgetRange.OVER_10M]
        architect_idx = budget_order.index(budget)
        persona_idx = budget_order.index(persona_profile["budget"])
        if abs(architect_idx - persona_idx) == 1:
            score += 15  # Half credit for adjacent
            matching_constraints.append(f"Budget: {budget.value} (close to {persona_profile['budget'].value})")

    # Data sovereignty (weight: 25 points)
    max_score += 25
    sovereignty = architect_context.get("data_sovereignty")
    if sovereignty == persona_profile["data_sovereignty"]:
        score += 25
        matching_constraints.append(f"Data sovereignty: {sovereignty.value}")
    elif sovereignty and persona_profile["data_sovereignty"]:
        # Partial credit for compatible sovereignty
        if sovereignty == DataSovereignty.HYBRID and persona_profile["data_sovereignty"] in [DataSovereignty.CLOUD_FIRST, DataSovereignty.ON_PREM_ONLY]:
            score += 12.5
            matching_constraints.append(f"Data sovereignty: {sovereignty.value} (compatible with {persona_profile['data_sovereignty'].value})")

    # Vendor tolerance (weight: 20 points)
    max_score += 20
    tolerance = architect_context.get("vendor_tolerance")
    if tolerance == persona_profile["vendor_tolerance"]:
        score += 20
        matching_constraints.append(f"Vendor tolerance: {tolerance.value}")
    elif tolerance and persona_profile["vendor_tolerance"]:
        # Partial credit for compatible tolerance
        tolerance_order = [VendorTolerance.OSS_FIRST, VendorTolerance.OSS_WITH_SUPPORT, VendorTolerance.COMMERCIAL_ONLY]
        architect_idx = tolerance_order.index(tolerance)
        persona_idx = tolerance_order.index(persona_profile["vendor_tolerance"])
        if abs(architect_idx - persona_idx) == 1:
            score += 10
            matching_constraints.append(f"Vendor tolerance: {tolerance.value} (similar to {persona_profile['vendor_tolerance'].value})")

    # Convert to percentage
    percentage = (score / max_score * 100) if max_score > 0 else 0
    return percentage, matching_constraints


def match_journey_persona(
    team_size: TeamSize | None = None,
    budget: BudgetRange | None = None,
    data_sovereignty: DataSovereignty | None = None,
    vendor_tolerance: VendorTolerance | None = None,
    decision_state: DecisionState | None = None,
) -> JourneyMatch:
    """
    Match architect's context to Chapter 4 journey persona.

    Args:
        team_size: Team capacity (lean/standard/large)
        budget: Annual budget range
        data_sovereignty: Data sovereignty requirement
        vendor_tolerance: Vendor relationship tolerance
        decision_state: Optional DecisionState with context

    Returns:
        JourneyMatch with persona, confidence, reasoning, and architecture pattern

    Example:
        ```python
        from src.tools.match_journey import match_journey_persona
        from src.models import TeamSize, BudgetRange, DataSovereignty

        match = match_journey_persona(
            team_size=TeamSize.STANDARD,
            budget=BudgetRange.RANGE_500K_2M,
            data_sovereignty=DataSovereignty.CLOUD_FIRST,
        )

        print(match.summary())
        print(f"Architecture pattern: {match.architecture_pattern}")
        print(f"Reasoning: {match.reasoning}")
        ```
    """
    # Build architect context
    architect_context = {}

    # Prefer explicit parameters
    if team_size:
        architect_context["team_size"] = team_size
    if budget:
        architect_context["budget"] = budget
    if data_sovereignty:
        architect_context["data_sovereignty"] = data_sovereignty
    if vendor_tolerance:
        architect_context["vendor_tolerance"] = vendor_tolerance

    # Fall back to decision_state if parameters not provided
    if decision_state:
        if "team_size" not in architect_context and decision_state.team_size:
            architect_context["team_size"] = decision_state.team_size
        if "budget" not in architect_context and decision_state.budget:
            architect_context["budget"] = decision_state.budget
        if "data_sovereignty" not in architect_context and decision_state.data_sovereignty:
            architect_context["data_sovereignty"] = decision_state.data_sovereignty
        if "vendor_tolerance" not in architect_context and decision_state.vendor_tolerance:
            architect_context["vendor_tolerance"] = decision_state.vendor_tolerance

    # If no context provided, return generic match
    if not architect_context:
        return JourneyMatch(
            persona="unknown",
            confidence=0.0,
            reasoning="No organizational context provided. Please specify team size, budget, and data sovereignty requirements.",
            architecture_pattern="Generic Security Data Platform",
            key_constraints=[],
        )

    # Calculate match scores for each persona
    personas = [
        ("jennifer", JENNIFER_PROFILE),
        ("marcus", MARCUS_PROFILE),
        ("priya", PRIYA_PROFILE),
    ]

    matches = []
    for persona_name, profile in personas:
        score, constraints = calculate_match_score(architect_context, profile)
        matches.append({
            "persona": persona_name,
            "profile": profile,
            "score": score,
            "constraints": constraints,
        })

    # Sort by score
    matches.sort(key=lambda x: x["score"], reverse=True)
    best_match = matches[0]
    second_match = matches[1] if len(matches) > 1 else None

    # Determine if this is a hybrid scenario
    is_hybrid = False
    if second_match and abs(best_match["score"] - second_match["score"]) < 15:
        # Close match - hybrid scenario
        is_hybrid = True

    # Build reasoning
    if is_hybrid:
        reasoning = f"""Your organization shares characteristics with both {best_match['profile']['name']} and {second_match['profile']['name']} from Chapter 4.

**Primary Match ({best_match['score']:.0f}%)**: {best_match['profile']['name']}
{best_match['profile']['description']}

**Secondary Match ({second_match['score']:.0f}%)**: {second_match['profile']['name']}

**Your Matching Constraints**:
"""
        for constraint in best_match["constraints"]:
            reasoning += f"- {constraint}\n"

        reasoning += f"\n**Recommendation**: Consider a hybrid architecture combining patterns from both journeys."

        persona = f"hybrid-{best_match['persona']}-{second_match['persona']}"
        architecture_pattern = f"{best_match['profile']['architecture_pattern']} + {second_match['profile']['architecture_pattern']}"
        confidence = (best_match["score"] + second_match["score"]) / 2

    else:
        # Clear match
        reasoning = f"""Your organization closely matches **{best_match['profile']['name']}** from Chapter 4 ({best_match['score']:.0f}% match).

{best_match['profile']['description']}

**Your Matching Constraints**:
"""
        for constraint in best_match["constraints"]:
            reasoning += f"- {constraint}\n"

        reasoning += f"""

**Recommended Vendors** (from {best_match['profile']['name']} journey):
"""
        for vendor in best_match["profile"]["recommended_vendors"]:
            reasoning += f"- {vendor}\n"

        persona = best_match["persona"]
        architecture_pattern = best_match["profile"]["architecture_pattern"]
        confidence = best_match["score"]

    return JourneyMatch(
        persona=persona,
        confidence=confidence,
        reasoning=reasoning,
        architecture_pattern=architecture_pattern,
        key_constraints=best_match["constraints"],
    )


def get_journey_description(persona: str) -> str:
    """
    Get detailed description of a journey persona.

    Args:
        persona: Persona name (jennifer, marcus, priya)

    Returns:
        Detailed description of persona and architecture pattern
    """
    profiles = {
        "jennifer": JENNIFER_PROFILE,
        "marcus": MARCUS_PROFILE,
        "priya": PRIYA_PROFILE,
    }

    profile = profiles.get(persona.lower())
    if not profile:
        return f"Unknown persona: {persona}"

    return f"""{profile['name']}

{profile['description']}

**Architecture Pattern**: {profile['architecture_pattern']}

**Recommended Vendors**:
{chr(10).join(f"- {v}" for v in profile['recommended_vendors'])}
"""
