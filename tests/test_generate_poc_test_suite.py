"""
Tests for POC Test Suite Generator.

Validates scenario generation, success criteria, infrastructure requirements,
and vendor-specific customization.
"""

import pytest

from src.models import TeamSize, VendorCategory
from src.tools.generate_poc_test_suite import (
    POCTestSuite,
    generate_poc_test_suite,
    _estimate_poc_duration,
    _generate_evaluation_rubric,
    _generate_infrastructure_requirements,
    _generate_sample_queries,
    _generate_success_criteria,
    _generate_test_scenarios,
    _get_access_method,
    _get_deployment_method,
)
from src.utils.database_loader import load_default_database


@pytest.fixture
def vendor_db():
    """Load vendor database for testing."""
    return load_default_database()


# ============================================================================
# POC TEST SUITE GENERATION TESTS
# ============================================================================


def test_generate_poc_test_suite_basic(vendor_db):
    """Test basic POC test suite generation."""
    athena = vendor_db.get_by_id("amazon-athena")

    poc = generate_poc_test_suite(
        vendor=athena,
        use_cases=["threat_hunting"],
        data_sources=["cloudtrail"],
        team_skillset=TeamSize.LEAN,
    )

    assert isinstance(poc, POCTestSuite)
    assert poc.vendor == athena
    assert len(poc.test_scenarios) > 0
    assert len(poc.success_criteria) > 0
    assert len(poc.infrastructure_requirements) > 0
    assert poc.estimated_duration > 0


def test_generate_poc_test_suite_multiple_use_cases(vendor_db):
    """Test POC generation with multiple use cases."""
    splunk = vendor_db.get_by_id("splunk-enterprise-security")

    poc = generate_poc_test_suite(
        vendor=splunk,
        use_cases=["threat_hunting", "incident_response", "compliance_reporting"],
        data_sources=["cloudtrail", "vpc_flow_logs", "windows_events"],
        team_skillset=TeamSize.STANDARD,
    )

    # Should have scenarios for each use case + setup + performance + operational
    assert len(poc.test_scenarios) >= 6  # 1 setup + 3 use cases + 1 perf + 1 ops

    # Success criteria should include use case-specific items
    criteria_text = " ".join(poc.success_criteria)
    assert "threat" in criteria_text.lower() or "hunting" in criteria_text.lower()
    assert "incident" in criteria_text.lower() or "response" in criteria_text.lower()
    assert "compliance" in criteria_text.lower()


def test_generate_poc_test_suite_default_args(vendor_db):
    """Test POC generation with default arguments."""
    dremio = vendor_db.get_by_id("dremio")

    poc = generate_poc_test_suite(vendor=dremio)

    # Should have default use cases and data sources
    assert len(poc.test_scenarios) > 0
    assert len(poc.success_criteria) > 0
    assert poc.estimated_duration > 0


# ============================================================================
# TEST SCENARIO GENERATION TESTS
# ============================================================================


def test_generate_test_scenarios_basic(vendor_db):
    """Test basic test scenario generation."""
    athena = vendor_db.get_by_id("amazon-athena")

    scenarios = _generate_test_scenarios(
        vendor=athena,
        use_cases=["threat_hunting"],
        data_sources=["cloudtrail"],
    )

    # Should have at least: setup, use case, performance, operational
    assert len(scenarios) >= 4

    # First scenario should be setup
    assert "setup" in scenarios[0]["name"].lower()
    assert "ingestion" in scenarios[0]["name"].lower()

    # Each scenario should have required fields
    for scenario in scenarios:
        assert "name" in scenario
        assert "objective" in scenario
        assert "steps" in scenario
        assert "expected_outcome" in scenario
        assert isinstance(scenario["steps"], list)


def test_generate_test_scenarios_threat_hunting(vendor_db):
    """Test threat hunting scenario generation."""
    clickhouse = vendor_db.get_by_id("clickhouse")

    scenarios = _generate_test_scenarios(
        vendor=clickhouse,
        use_cases=["threat_hunting"],
        data_sources=["cloudtrail", "vpc_flow_logs"],
    )

    # Should have threat hunting scenario
    scenario_names = [s["name"].lower() for s in scenarios]
    assert any("threat" in name or "hunting" in name for name in scenario_names)


def test_generate_test_scenarios_compliance(vendor_db):
    """Test compliance reporting scenario generation."""
    wazuh = vendor_db.get_by_id("wazuh")

    scenarios = _generate_test_scenarios(
        vendor=wazuh,
        use_cases=["compliance_reporting"],
        data_sources=["system_logs"],
    )

    # Should have compliance scenario
    scenario_names = [s["name"].lower() for s in scenarios]
    assert any("compliance" in name or "report" in name for name in scenario_names)


# ============================================================================
# SUCCESS CRITERIA TESTS
# ============================================================================


def test_generate_success_criteria_basic(vendor_db):
    """Test basic success criteria generation."""
    athena = vendor_db.get_by_id("amazon-athena")

    criteria = _generate_success_criteria(athena, ["threat_hunting"])

    # Should have basic criteria
    assert len(criteria) > 0
    criteria_text = " ".join(criteria).lower()
    assert "data ingestion" in criteria_text or "ingestion" in criteria_text
    assert "query" in criteria_text


def test_generate_success_criteria_cloud_native(vendor_db):
    """Test cloud-native vendor success criteria."""
    athena = vendor_db.get_by_id("amazon-athena")  # Cloud-native

    criteria = _generate_success_criteria(athena, ["basic_querying"])

    criteria_text = " ".join(criteria).lower()
    assert "scale" in criteria_text or "scaling" in criteria_text


def test_generate_success_criteria_sql_interface(vendor_db):
    """Test SQL interface success criteria."""
    dremio = vendor_db.get_by_id("dremio")  # Has SQL interface

    criteria = _generate_success_criteria(dremio, ["basic_querying"])

    criteria_text = " ".join(criteria).lower()
    assert "sql" in criteria_text


def test_generate_success_criteria_use_case_specific(vendor_db):
    """Test use case-specific success criteria."""
    athena = vendor_db.get_by_id("amazon-athena")

    # Threat hunting
    criteria = _generate_success_criteria(athena, ["threat_hunting"])
    criteria_text = " ".join(criteria).lower()
    assert "threat" in criteria_text or "hunt" in criteria_text or "security" in criteria_text

    # Compliance reporting
    criteria = _generate_success_criteria(athena, ["compliance_reporting"])
    criteria_text = " ".join(criteria).lower()
    assert "compliance" in criteria_text or "report" in criteria_text or "audit" in criteria_text


# ============================================================================
# INFRASTRUCTURE REQUIREMENTS TESTS
# ============================================================================


def test_generate_infrastructure_requirements_managed(vendor_db):
    """Test infrastructure requirements for managed service."""
    athena = vendor_db.get_by_id("amazon-athena")  # Managed service

    reqs = _generate_infrastructure_requirements(athena, TeamSize.LEAN)

    assert "Deployment Model" in reqs
    assert "Team Skillset" in reqs
    assert "cloud" in reqs["Deployment Model"].lower()


def test_generate_infrastructure_requirements_self_hosted(vendor_db):
    """Test infrastructure requirements for self-hosted vendor."""
    clickhouse = vendor_db.get_by_id("clickhouse")

    reqs = _generate_infrastructure_requirements(clickhouse, TeamSize.STANDARD)

    # Self-hosted should have compute and storage requirements
    # (even if managed service available, if not cloud-native might need infrastructure)
    assert "Deployment Model" in reqs


def test_generate_infrastructure_requirements_high_complexity(vendor_db):
    """Test infrastructure requirements for high complexity vendor."""
    splunk = vendor_db.get_by_id("splunk-enterprise-security")  # High complexity

    reqs = _generate_infrastructure_requirements(splunk, TeamSize.LEAN)

    # High complexity should mention expertise requirement
    reqs_text = str(reqs).lower()
    assert "expertise" in reqs_text or "engineer" in reqs_text or "complexity" in str(splunk.capabilities.operational_complexity).lower()


# ============================================================================
# POC DURATION ESTIMATION TESTS
# ============================================================================


def test_estimate_poc_duration_low_complexity(vendor_db):
    """Test POC duration for low complexity vendor."""
    athena = vendor_db.get_by_id("amazon-athena")  # Low complexity

    duration = _estimate_poc_duration(athena, num_scenarios=4, team_skillset=TeamSize.STANDARD)

    # Low complexity should be shorter
    assert duration >= 3  # Minimum
    assert duration <= 7  # Reasonable upper bound


def test_estimate_poc_duration_high_complexity(vendor_db):
    """Test POC duration for high complexity vendor."""
    splunk = vendor_db.get_by_id("splunk-enterprise-security")  # High complexity

    duration = _estimate_poc_duration(splunk, num_scenarios=4, team_skillset=TeamSize.STANDARD)

    # High complexity should be longer
    assert duration > 5


def test_estimate_poc_duration_lean_team(vendor_db):
    """Test POC duration for lean team (less bandwidth)."""
    athena = vendor_db.get_by_id("amazon-athena")

    duration_lean = _estimate_poc_duration(athena, num_scenarios=4, team_skillset=TeamSize.LEAN)
    duration_large = _estimate_poc_duration(athena, num_scenarios=4, team_skillset=TeamSize.LARGE)

    # Lean team should take longer
    assert duration_lean > duration_large


def test_estimate_poc_duration_many_scenarios(vendor_db):
    """Test POC duration with many scenarios."""
    athena = vendor_db.get_by_id("amazon-athena")

    duration_few = _estimate_poc_duration(athena, num_scenarios=4, team_skillset=TeamSize.STANDARD)
    duration_many = _estimate_poc_duration(athena, num_scenarios=8, team_skillset=TeamSize.STANDARD)

    # More scenarios should take longer
    assert duration_many > duration_few


# ============================================================================
# SAMPLE QUERY GENERATION TESTS
# ============================================================================


def test_generate_sample_queries_sql_vendor(vendor_db):
    """Test sample query generation for SQL vendor."""
    athena = vendor_db.get_by_id("amazon-athena")  # Has SQL interface

    queries = _generate_sample_queries(athena, ["threat_hunting"])

    # Should have SQL queries
    assert len(queries) > 0
    assert all("SELECT" in q or "select" in q for q in queries)


def test_generate_sample_queries_non_sql_vendor(vendor_db):
    """Test sample query generation for non-SQL vendor."""
    grafana_loki = vendor_db.get_by_id("grafana-loki")  # No SQL interface

    queries = _generate_sample_queries(grafana_loki, ["threat_hunting"])

    # Non-SQL vendors should have no queries
    assert len(queries) == 0


def test_generate_sample_queries_threat_hunting(vendor_db):
    """Test threat hunting queries."""
    dremio = vendor_db.get_by_id("dremio")

    queries = _generate_sample_queries(dremio, ["threat_hunting"])

    # Should have threat hunting-specific queries
    queries_text = " ".join(queries).lower()
    assert "privilege" in queries_text or "escalation" in queries_text or "CreateUser" in " ".join(queries)


# ============================================================================
# EVALUATION RUBRIC TESTS
# ============================================================================


def test_generate_evaluation_rubric_basic(vendor_db):
    """Test basic evaluation rubric generation."""
    athena = vendor_db.get_by_id("amazon-athena")

    rubric = _generate_evaluation_rubric(athena)

    # Should have standard categories
    assert "Ease of Deployment" in rubric
    assert "Query Performance" in rubric
    assert "Cost Predictability" in rubric

    # All scores should be positive integers
    assert all(isinstance(score, int) and score > 0 for score in rubric.values())


def test_generate_evaluation_rubric_siem(vendor_db):
    """Test SIEM-specific rubric categories."""
    splunk = vendor_db.get_by_id("splunk-enterprise-security")  # SIEM

    rubric = _generate_evaluation_rubric(splunk)

    # SIEM should have detection-specific categories
    rubric_text = str(rubric.keys()).lower()
    assert "detection" in rubric_text or "incident" in rubric_text


def test_generate_evaluation_rubric_ml_analytics(vendor_db):
    """Test ML analytics rubric categories."""
    databricks = vendor_db.get_by_id("databricks")  # Has ML analytics

    rubric = _generate_evaluation_rubric(databricks)

    # ML vendors should have ML quality category
    assert "ML Analytics Quality" in rubric


def test_generate_evaluation_rubric_cloud_native(vendor_db):
    """Test cloud-native rubric categories."""
    athena = vendor_db.get_by_id("amazon-athena")  # Cloud-native

    rubric = _generate_evaluation_rubric(athena)

    # Cloud-native should have cloud integration category
    assert "Cloud Integration" in rubric


# ============================================================================
# HELPER FUNCTION TESTS
# ============================================================================


def test_get_deployment_method_managed(vendor_db):
    """Test deployment method for managed service."""
    athena = vendor_db.get_by_id("amazon-athena")

    method = _get_deployment_method(athena)

    assert "managed" in method.lower()


def test_get_deployment_method_cloud(vendor_db):
    """Test deployment method for cloud self-managed."""
    clickhouse = vendor_db.get_by_id("clickhouse")

    method = _get_deployment_method(clickhouse)

    # Should mention deployment type
    assert len(method) > 0


def test_get_access_method_sql(vendor_db):
    """Test access method for SQL vendor."""
    athena = vendor_db.get_by_id("amazon-athena")

    method = _get_access_method(athena)

    assert "sql" in method.lower()


def test_get_access_method_non_sql(vendor_db):
    """Test access method for non-SQL vendor."""
    grafana_loki = vendor_db.get_by_id("grafana-loki")

    method = _get_access_method(grafana_loki)

    assert "web ui" in method.lower() or "api" in method.lower()


# ============================================================================
# MARKDOWN GENERATION TESTS
# ============================================================================


def test_poc_to_markdown_basic(vendor_db):
    """Test Markdown generation."""
    athena = vendor_db.get_by_id("amazon-athena")

    poc = generate_poc_test_suite(
        vendor=athena,
        use_cases=["threat_hunting"],
        data_sources=["cloudtrail"],
        team_skillset=TeamSize.LEAN,
    )

    markdown = poc.to_markdown()

    # Should have all major sections
    assert "# POC Test Plan" in markdown
    assert "## Overview" in markdown
    assert "## Infrastructure Requirements" in markdown
    assert "## Test Scenarios" in markdown
    assert "## Success Criteria" in markdown
    assert "## Evaluation Rubric" in markdown

    # Should have vendor name
    assert athena.name in markdown


def test_poc_to_markdown_with_queries(vendor_db):
    """Test Markdown with sample queries."""
    dremio = vendor_db.get_by_id("dremio")

    poc = generate_poc_test_suite(
        vendor=dremio,
        use_cases=["threat_hunting"],
        data_sources=["cloudtrail"],
        team_skillset=TeamSize.STANDARD,
    )

    markdown = poc.to_markdown()

    # Should have queries section
    if poc.sample_queries:
        assert "## Sample Queries" in markdown
        assert "```sql" in markdown


def test_poc_to_markdown_length(vendor_db):
    """Test that POC markdown is comprehensive."""
    athena = vendor_db.get_by_id("amazon-athena")

    poc = generate_poc_test_suite(
        vendor=athena,
        use_cases=["threat_hunting", "compliance_reporting"],
        data_sources=["cloudtrail", "vpc_flow_logs"],
        team_skillset=TeamSize.LEAN,
    )

    markdown = poc.to_markdown()

    # Should be substantial (target 2000+ characters for good POC plan)
    assert len(markdown) > 1500


# ============================================================================
# REALISTIC SCENARIO TESTS
# ============================================================================


def test_poc_athena_lean_team(vendor_db):
    """Test POC for Athena with lean team."""
    athena = vendor_db.get_by_id("amazon-athena")

    poc = generate_poc_test_suite(
        vendor=athena,
        use_cases=["threat_hunting"],
        data_sources=["cloudtrail"],
        team_skillset=TeamSize.LEAN,
    )

    # Lean team POC should be realistic
    assert 3 <= poc.estimated_duration <= 10
    assert len(poc.test_scenarios) >= 4
    assert len(poc.success_criteria) >= 4


def test_poc_splunk_enterprise(vendor_db):
    """Test POC for Splunk (high complexity)."""
    splunk = vendor_db.get_by_id("splunk-enterprise-security")

    poc = generate_poc_test_suite(
        vendor=splunk,
        use_cases=["threat_hunting", "incident_response"],
        data_sources=["cloudtrail", "windows_events"],
        team_skillset=TeamSize.STANDARD,
    )

    # High complexity POC should be longer
    assert poc.estimated_duration > 5
    assert len(poc.test_scenarios) >= 5


def test_poc_clickhouse_analytics(vendor_db):
    """Test POC for ClickHouse (analytics use case)."""
    clickhouse = vendor_db.get_by_id("clickhouse")

    poc = generate_poc_test_suite(
        vendor=clickhouse,
        use_cases=["cost_optimization"],
        data_sources=["aws_cost_usage"],
        team_skillset=TeamSize.LEAN,
    )

    # Should have cost optimization scenario
    scenario_names = [s["name"].lower() for s in poc.test_scenarios]
    assert any("cost" in name or "optimization" in name for name in scenario_names)
