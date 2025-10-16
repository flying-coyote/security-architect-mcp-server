"""
POC Test Suite Generator

Generates vendor-specific proof-of-concept test plans to help architects
evaluate finalists hands-on with realistic scenarios, success criteria,
and infrastructure requirements.

Phase 2: Living Literature Review Integration deliverable.
"""

from typing import Any

from src.models import TeamSize, Vendor, VendorCategory


class POCTestSuite:
    """
    Proof-of-concept test suite for a vendor.

    Attributes:
        vendor: Vendor being tested
        test_scenarios: List of test scenarios to execute
        success_criteria: Measurable success criteria
        infrastructure_requirements: Required infrastructure
        estimated_duration: Estimated POC duration in days
        sample_queries: Example queries/dashboards to build
        evaluation_rubric: Scoring rubric for POC
    """

    def __init__(
        self,
        vendor: Vendor,
        test_scenarios: list[dict[str, Any]],
        success_criteria: list[str],
        infrastructure_requirements: dict[str, Any],
        estimated_duration: int,
        sample_queries: list[str],
        evaluation_rubric: dict[str, int],
    ):
        self.vendor = vendor
        self.test_scenarios = test_scenarios
        self.success_criteria = success_criteria
        self.infrastructure_requirements = infrastructure_requirements
        self.estimated_duration = estimated_duration
        self.sample_queries = sample_queries
        self.evaluation_rubric = evaluation_rubric

    def to_markdown(self) -> str:
        """Generate Markdown POC test plan."""
        sections = []

        # Header
        sections.append(f"# POC Test Plan: {self.vendor.name}")
        sections.append("")
        sections.append(f"**Vendor**: {self.vendor.name}")
        sections.append(f"**Category**: {self.vendor.category.value}")
        sections.append(f"**Estimated Duration**: {self.estimated_duration} days")
        sections.append(f"**Website**: {self.vendor.website}")
        sections.append("")

        # Overview
        sections.append("## Overview")
        sections.append("")
        sections.append(self.vendor.description)
        sections.append("")

        # Infrastructure Requirements
        sections.append("## Infrastructure Requirements")
        sections.append("")
        for key, value in self.infrastructure_requirements.items():
            sections.append(f"- **{key}**: {value}")
        sections.append("")

        # Test Scenarios
        sections.append("## Test Scenarios")
        sections.append("")
        for i, scenario in enumerate(self.test_scenarios, 1):
            sections.append(f"### Scenario {i}: {scenario['name']}")
            sections.append("")
            sections.append(f"**Objective**: {scenario['objective']}")
            sections.append("")
            sections.append("**Steps**:")
            for step in scenario['steps']:
                sections.append(f"1. {step}")
            sections.append("")
            sections.append(f"**Expected Outcome**: {scenario['expected_outcome']}")
            sections.append("")

        # Sample Queries
        if self.sample_queries:
            sections.append("## Sample Queries/Dashboards")
            sections.append("")
            for i, query in enumerate(self.sample_queries, 1):
                sections.append(f"### Query {i}")
                sections.append("```sql")
                sections.append(query)
                sections.append("```")
                sections.append("")

        # Success Criteria
        sections.append("## Success Criteria")
        sections.append("")
        for criterion in self.success_criteria:
            sections.append(f"- [ ] {criterion}")
        sections.append("")

        # Evaluation Rubric
        sections.append("## Evaluation Rubric")
        sections.append("")
        sections.append("Rate each category 1-5 (5 = excellent):")
        sections.append("")
        for category, max_score in self.evaluation_rubric.items():
            sections.append(f"- **{category}**: ___/{max_score}")
        sections.append("")
        total_score = sum(self.evaluation_rubric.values())
        sections.append(f"**Total Score**: ___/{total_score}")
        sections.append("")

        return "\n".join(sections)


def generate_poc_test_suite(
    vendor: Vendor,
    use_cases: list[str] | None = None,
    data_sources: list[str] | None = None,
    team_skillset: TeamSize = TeamSize.STANDARD,
) -> POCTestSuite:
    """
    Generate vendor-specific POC test suite.

    Args:
        vendor: Vendor to generate POC for
        use_cases: Use cases to test (e.g., ['threat_hunting', 'compliance_reporting'])
        data_sources: Data sources available (e.g., ['cloudtrail', 'vpc_flow_logs'])
        team_skillset: Team capacity (affects POC complexity)

    Returns:
        POCTestSuite with scenarios, success criteria, infrastructure requirements

    Example:
        ```python
        from src.utils.database_loader import load_default_database
        from src.tools.generate_poc_test_suite import generate_poc_test_suite

        db = load_default_database()
        athena = db.get_by_id("amazon-athena")

        poc = generate_poc_test_suite(
            vendor=athena,
            use_cases=["threat_hunting", "compliance_reporting"],
            data_sources=["cloudtrail", "vpc_flow_logs"],
            team_skillset=TeamSize.LEAN,
        )

        print(poc.to_markdown())
        ```
    """
    use_cases = use_cases or ["basic_querying"]
    data_sources = data_sources or ["sample_logs"]

    # Generate test scenarios based on vendor category
    test_scenarios = _generate_test_scenarios(vendor, use_cases, data_sources)

    # Generate success criteria
    success_criteria = _generate_success_criteria(vendor, use_cases)

    # Generate infrastructure requirements
    infrastructure_requirements = _generate_infrastructure_requirements(vendor, team_skillset)

    # Estimate POC duration
    estimated_duration = _estimate_poc_duration(vendor, len(test_scenarios), team_skillset)

    # Generate sample queries
    sample_queries = _generate_sample_queries(vendor, use_cases)

    # Generate evaluation rubric
    evaluation_rubric = _generate_evaluation_rubric(vendor)

    return POCTestSuite(
        vendor=vendor,
        test_scenarios=test_scenarios,
        success_criteria=success_criteria,
        infrastructure_requirements=infrastructure_requirements,
        estimated_duration=estimated_duration,
        sample_queries=sample_queries,
        evaluation_rubric=evaluation_rubric,
    )


def _generate_test_scenarios(
    vendor: Vendor,
    use_cases: list[str],
    data_sources: list[str],
) -> list[dict[str, Any]]:
    """Generate test scenarios based on vendor category and use cases."""
    scenarios = []

    # Scenario 1: Basic Setup and Data Ingestion
    scenarios.append({
        "name": "Setup and Data Ingestion",
        "objective": f"Deploy {vendor.name} and ingest sample data sources",
        "steps": [
            f"Deploy {vendor.name} using {_get_deployment_method(vendor)}",
            f"Configure data sources: {', '.join(data_sources)}",
            "Ingest 24 hours of sample data",
            "Verify data ingestion completeness and schema",
        ],
        "expected_outcome": "Data successfully ingested and queryable within deployment model",
    })

    # Scenario 2: Use Case-Specific Testing
    for use_case in use_cases:
        scenario = _generate_use_case_scenario(vendor, use_case, data_sources)
        if scenario:
            scenarios.append(scenario)

    # Scenario 3: Performance Testing
    scenarios.append({
        "name": "Query Performance Testing",
        "objective": "Evaluate query latency and throughput",
        "steps": [
            "Run 10 sample queries across different complexity levels",
            "Measure query latency (p50, p95, p99)",
            "Test concurrent query execution (5-10 users)",
            "Monitor resource utilization (CPU, memory, network)",
        ],
        "expected_outcome": f"Queries complete within acceptable latency for {vendor.category.value}",
    })

    # Scenario 4: Operational Testing
    scenarios.append({
        "name": "Operational Capabilities",
        "objective": "Test monitoring, alerting, and maintenance workflows",
        "steps": [
            "Configure monitoring dashboards",
            "Set up alerting rules (data quality, performance)",
            "Test backup/restore procedures (if applicable)",
            "Evaluate administrative overhead",
        ],
        "expected_outcome": "Platform operational capabilities meet team requirements",
    })

    return scenarios


def _generate_use_case_scenario(
    vendor: Vendor,
    use_case: str,
    data_sources: list[str],
) -> dict[str, Any] | None:
    """Generate use case-specific test scenario."""
    use_case_scenarios = {
        "threat_hunting": {
            "name": "Threat Hunting Workflow",
            "objective": "Validate threat hunting capabilities with real-world scenarios",
            "steps": [
                "Hunt for suspicious AWS API calls (cloudtrail)",
                "Investigate lateral movement patterns (vpc_flow_logs)",
                "Correlate events across multiple data sources",
                "Build reusable hunting queries",
            ],
            "expected_outcome": "Successfully identify and investigate security anomalies",
        },
        "compliance_reporting": {
            "name": "Compliance Reporting",
            "objective": "Generate compliance reports for audit requirements",
            "steps": [
                "Create PCI DSS access control report",
                "Generate HIPAA audit log retention report",
                "Build SOC 2 change management dashboard",
                "Test report scheduling and delivery",
            ],
            "expected_outcome": "Compliance reports meet audit requirements with minimal manual effort",
        },
        "incident_response": {
            "name": "Incident Response Investigation",
            "objective": "Simulate incident response workflow",
            "steps": [
                "Ingest alert from detection system",
                "Pivot across data sources for context",
                "Timeline reconstruction (15-minute window)",
                "Export investigation findings",
            ],
            "expected_outcome": "Complete investigation workflow in <30 minutes",
        },
        "cost_optimization": {
            "name": "Cost Optimization Analysis",
            "objective": "Identify cost optimization opportunities",
            "steps": [
                "Analyze resource utilization patterns",
                "Identify idle/underutilized resources",
                "Calculate potential savings",
                "Generate cost optimization recommendations",
            ],
            "expected_outcome": "Identify actionable cost savings opportunities",
        },
    }

    return use_case_scenarios.get(use_case)


def _generate_success_criteria(vendor: Vendor, use_cases: list[str]) -> list[str]:
    """Generate measurable success criteria."""
    criteria = [
        "Data ingestion completes successfully for all configured sources",
        f"Platform accessible via {_get_access_method(vendor)}",
        "Query latency meets performance expectations for use cases",
        "Team can operate platform without extensive training",
    ]

    # Add use case-specific criteria
    if "threat_hunting" in use_cases:
        criteria.append("Successfully hunt and investigate security threats within 30 minutes")

    if "compliance_reporting" in use_cases:
        criteria.append("Generate compliance reports meeting audit requirements")

    if "incident_response" in use_cases:
        criteria.append("Complete incident investigation workflow in <30 minutes")

    # Add vendor-specific criteria
    if vendor.capabilities.cloud_native:
        criteria.append("Platform scales automatically with data volume")

    if vendor.capabilities.sql_interface:
        criteria.append("SQL queries execute correctly without vendor-specific syntax learning")

    if vendor.capabilities.ml_analytics:
        criteria.append("ML-based detections provide actionable insights")

    return criteria


def _generate_infrastructure_requirements(
    vendor: Vendor,
    team_skillset: TeamSize,
) -> dict[str, Any]:
    """Generate infrastructure requirements."""
    requirements = {
        "Deployment Model": ", ".join([d.value for d in vendor.capabilities.deployment_models]),
        "Team Skillset": team_skillset.value,
    }

    # Add cloud requirements
    if "cloud" in [d.value for d in vendor.capabilities.deployment_models]:
        requirements["Cloud Account"] = "AWS/Azure/GCP account with appropriate permissions"

    # Add compute requirements
    if not vendor.capabilities.managed_service_available:
        requirements["Compute"] = "4-8 vCPUs, 16-32 GB RAM (self-hosted)"
        requirements["Storage"] = "500 GB - 1 TB for POC data"

    # Add network requirements
    if vendor.capabilities.siem_integration:
        requirements["Network"] = "Connectivity to existing SIEM/security tools"

    # Add skillset requirements
    if vendor.capabilities.operational_complexity == "high":
        requirements["Expertise Required"] = "Dedicated engineer for POC duration"

    return requirements


def _estimate_poc_duration(
    vendor: Vendor,
    num_scenarios: int,
    team_skillset: TeamSize,
) -> int:
    """Estimate POC duration in days."""
    base_days = 5  # 1 week baseline

    # Adjust for operational complexity
    if vendor.capabilities.operational_complexity == "high":
        base_days += 3
    elif vendor.capabilities.operational_complexity == "low":
        base_days -= 1

    # Adjust for team skillset
    if team_skillset == TeamSize.LEAN:
        base_days += 2  # Less bandwidth
    elif team_skillset == TeamSize.LARGE:
        base_days -= 1  # More resources

    # Adjust for scenario count
    base_days += max(0, num_scenarios - 4)  # Extra day per additional scenario

    return max(3, base_days)  # Minimum 3 days


def _generate_sample_queries(vendor: Vendor, use_cases: list[str]) -> list[str]:
    """Generate sample queries for vendor."""
    queries = []

    if not vendor.capabilities.sql_interface:
        return []  # Non-SQL vendors don't have sample queries

    # Basic query
    queries.append("""-- Find failed login attempts
SELECT
    user_identity.username,
    source_ip_address,
    event_time,
    error_message
FROM cloudtrail_logs
WHERE event_name = 'ConsoleLogin'
  AND error_code = 'Failed authentication'
  AND event_time > NOW() - INTERVAL '24' HOUR
ORDER BY event_time DESC
LIMIT 100;""")

    # Use case-specific queries
    if "threat_hunting" in use_cases:
        queries.append("""-- Hunt for privilege escalation attempts
SELECT
    user_identity.username,
    event_name,
    COUNT(*) as attempt_count,
    ARRAY_AGG(DISTINCT resources.arn) as affected_resources
FROM cloudtrail_logs
WHERE event_name IN ('CreateUser', 'AttachUserPolicy', 'PutUserPolicy')
  AND user_identity.type = 'IAMUser'
  AND event_time > NOW() - INTERVAL '7' DAY
GROUP BY user_identity.username, event_name
HAVING COUNT(*) > 5
ORDER BY attempt_count DESC;""")

    return queries


def _generate_evaluation_rubric(vendor: Vendor) -> dict[str, int]:
    """Generate evaluation rubric with max scores."""
    rubric = {
        "Ease of Deployment": 5,
        "Query Performance": 5,
        "User Interface/Experience": 5,
        "Documentation Quality": 5,
        "Operational Overhead": 5,
        "Feature Completeness": 5,
        "Cost Predictability": 5,
        "Vendor Support Responsiveness": 5,
    }

    # Add category-specific rubric items
    if vendor.category == VendorCategory.SIEM:
        rubric["Detection Coverage"] = 5
        rubric["Incident Response Workflow"] = 5

    if vendor.capabilities.ml_analytics:
        rubric["ML Analytics Quality"] = 5

    if vendor.capabilities.cloud_native:
        rubric["Cloud Integration"] = 5

    return rubric


def _get_deployment_method(vendor: Vendor) -> str:
    """Get deployment method description."""
    if vendor.capabilities.managed_service_available:
        return "managed service"
    elif "cloud" in [d.value for d in vendor.capabilities.deployment_models]:
        return "cloud deployment (self-managed)"
    else:
        return "on-premises installation"


def _get_access_method(vendor: Vendor) -> str:
    """Get access method description."""
    if vendor.capabilities.sql_interface:
        return "SQL interface or web UI"
    else:
        return "web UI or API"
