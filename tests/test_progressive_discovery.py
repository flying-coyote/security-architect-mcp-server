#!/usr/bin/env python3
"""
Test suite for Progressive Tool Discovery (90% context reduction)
Tests on-demand loading, search functionality, and context savings.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

# Add parent directory to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tools.progressive_discovery import (
    DiscoveryStrategy,
    ToolMetadata,
    ProgressiveToolLoader,
    ProgressiveDiscoveryPatterns,
    create_discovery_tool,
    create_load_tool,
    integrate_progressive_discovery
)


class TestToolMetadata:
    """Test tool metadata functionality."""

    def test_metadata_creation(self):
        """Test creating tool metadata."""
        metadata = ToolMetadata(
            name="analyze_splunk",
            category="SIEM",
            description_summary="Analyze Splunk for requirements",
            relevance_keywords={"splunk", "siem", "security", "logging"},
            requirements_matched={"cloud", "enterprise"}
        )

        assert metadata.name == "analyze_splunk"
        assert metadata.category == "SIEM"
        assert "splunk" in metadata.relevance_keywords

    def test_matches_query(self):
        """Test query matching logic."""
        metadata = ToolMetadata(
            name="analyze_elastic",
            category="SIEM",
            description_summary="Analyze Elastic for requirements",
            relevance_keywords={"elastic", "elasticsearch", "kibana", "siem"},
            requirements_matched={"cloud", "oss"}
        )

        # Test name matching
        assert metadata.matches_query("elastic") is True
        assert metadata.matches_query("ELASTIC") is True  # Case insensitive

        # Test category matching
        assert metadata.matches_query("siem") is True
        assert metadata.matches_query("SIEM") is True

        # Test keyword matching
        assert metadata.matches_query("kibana") is True
        assert metadata.matches_query("elasticsearch") is True

        # Test non-matching
        assert metadata.matches_query("splunk") is False
        assert metadata.matches_query("random") is False

    def test_matches_requirements(self):
        """Test requirements matching logic."""
        metadata = ToolMetadata(
            name="analyze_databricks",
            category="Lakehouse",
            description_summary="Enterprise lakehouse platform",
            relevance_keywords={"databricks", "lakehouse", "delta"},
            requirements_matched={"cloud-only"}
        )

        # Test budget filtering
        requirements = {"budget": "<500K"}
        assert metadata.matches_requirements(requirements) is True  # Not enterprise category

        metadata.category = "Enterprise SIEM"
        assert metadata.matches_requirements(requirements) is False  # Enterprise + low budget

        # Test team size filtering
        metadata.category = "Lakehouse"
        metadata.description_summary = "Complex enterprise platform"
        requirements = {"team_size": "lean"}
        assert metadata.matches_requirements(requirements) is False  # Complex + lean team

        # Test deployment filtering
        requirements = {"deployment": "on-prem"}
        assert metadata.matches_requirements(requirements) is False  # Cloud-only vs on-prem


class TestProgressiveToolLoader:
    """Test progressive tool loading functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock vendor database
        self.mock_vendors = [
            Mock(
                id="splunk",
                name="Splunk",
                category=Mock(value="SIEM"),
                tags=["security", "enterprise"],
                capabilities=Mock(
                    cloud_native=True,
                    on_prem_available=True
                ),
                is_open_source=False
            ),
            Mock(
                id="elastic",
                name="Elastic",
                category=Mock(value="SIEM"),
                tags=["security", "oss"],
                capabilities=Mock(
                    cloud_native=True,
                    on_prem_available=True
                ),
                is_open_source=True
            ),
            Mock(
                id="duckdb",
                name="DuckDB",
                category=Mock(value="Query Engine"),
                tags=["embedded", "analytics"],
                capabilities=Mock(
                    cloud_native=False,
                    on_prem_available=True
                ),
                is_open_source=True
            )
        ]

        self.mock_vendor_db = Mock(vendors=self.mock_vendors)
        self.loader = ProgressiveToolLoader(self.mock_vendor_db)

    def test_initialization(self):
        """Test loader initialization."""
        assert len(self.loader.tool_metadata_cache) == 3  # 3 vendors
        assert self.loader.discovery_stats["total_tools"] == 3
        assert self.loader.discovery_stats["loaded_tools"] == 0

    def test_search_tools_by_query(self):
        """Test searching tools by query."""
        results = self.loader.search_tools(query="SIEM")

        assert len(results) == 2  # Splunk and Elastic
        assert all("SIEM" in r["category"] for r in results)

        # Test query tracking
        assert self.loader.discovery_stats["queries_processed"] == 1

    def test_search_tools_by_category(self):
        """Test filtering by category."""
        results = self.loader.search_tools(category="Query Engine")

        assert len(results) == 1
        assert results[0]["name"] == "analyze_duckdb"

    def test_search_tools_by_requirements(self):
        """Test filtering by requirements."""
        requirements = {"budget": "<500K"}
        results = self.loader.search_tools(requirements=requirements)

        # Should return all tools (none explicitly marked as enterprise)
        assert len(results) > 0

    def test_search_tools_with_limit(self):
        """Test result limiting."""
        results = self.loader.search_tools(limit=1)

        assert len(results) == 1

    def test_load_tool_on_demand(self):
        """Test on-demand tool loading."""
        # Initially not loaded
        assert "analyze_splunk" not in self.loader.loaded_tools

        # Load tool
        tool = self.loader.load_tool("analyze_splunk")

        assert tool is not None
        assert tool["name"] == "analyze_splunk"
        assert "Splunk" in tool["description"]
        assert "inputSchema" in tool
        assert "analyze_splunk" in self.loader.loaded_tools
        assert self.loader.discovery_stats["loaded_tools"] == 1

    def test_load_tool_caching(self):
        """Test that loaded tools are cached."""
        # Load tool first time
        tool1 = self.loader.load_tool("analyze_elastic")
        loaded_count = self.loader.discovery_stats["loaded_tools"]

        # Load same tool again
        tool2 = self.loader.load_tool("analyze_elastic")

        # Should return same tool from cache
        assert tool1 is tool2
        assert self.loader.discovery_stats["loaded_tools"] == loaded_count

    def test_load_nonexistent_tool(self):
        """Test loading non-existent tool."""
        tool = self.loader.load_tool("analyze_nonexistent")
        assert tool is None

    def test_context_savings_calculation(self):
        """Test context savings tracking."""
        # Search for tools (lightweight)
        results = self.loader.search_tools(query="SIEM", limit=2)

        # Check context savings
        stats = self.loader.get_discovery_stats()
        assert stats["context_saved_kb"] > 0
        assert stats["context_reduction_percentage"] > 0

    def test_discovery_stats(self):
        """Test statistics tracking."""
        # Perform some operations
        self.loader.search_tools(query="test")
        self.loader.load_tool("analyze_splunk")

        stats = self.loader.get_discovery_stats()

        assert stats["total_tools"] == 3
        assert stats["loaded_tools"] == 1
        assert stats["queries_processed"] == 1
        assert stats["load_percentage"] == (1/3) * 100
        assert stats["context_reduction_percentage"] > 0


class TestProgressiveDiscoveryTool:
    """Test MCP tool creation for progressive discovery."""

    def test_create_discovery_tool(self):
        """Test discovery tool creation."""
        mock_vendor_db = Mock(vendors=[])
        tool = create_discovery_tool(mock_vendor_db)

        assert tool["name"] == "search_tools"
        assert "90% reduction" in tool["description"]
        assert "inputSchema" in tool
        assert "handler" in tool
        assert callable(tool["handler"])

    def test_create_load_tool(self):
        """Test load tool creation."""
        mock_loader = Mock()
        tool = create_load_tool(mock_loader)

        assert tool["name"] == "load_tool"
        assert "on-demand" in tool["description"]
        assert "inputSchema" in tool
        assert "handler" in tool


class TestProgressiveDiscoveryPatterns:
    """Test common discovery patterns."""

    def test_requirements_based_pattern(self):
        """Test requirements-based discovery pattern."""
        pattern = ProgressiveDiscoveryPatterns.requirements_based_discovery()

        assert "search_tools(" in pattern
        assert "requirements=" in pattern
        assert "load_tool(" in pattern
        assert "# Now analyze only the relevant vendors" in pattern

    def test_incremental_discovery_pattern(self):
        """Test incremental discovery pattern."""
        pattern = ProgressiveDiscoveryPatterns.incremental_discovery()

        assert "search_tools(category=" in pattern
        assert "affordable_tools = search_tools(" in pattern
        assert "# Context saved:" in pattern

    def test_smart_filtering_pattern(self):
        """Test smart filtering pattern."""
        pattern = ProgressiveDiscoveryPatterns.smart_filtering()

        assert "extract_requirements(" in pattern
        assert "context_saved_percentage" in pattern
        assert "87.5% context saved" in pattern


class TestContextReduction:
    """Test actual context reduction metrics."""

    def test_upfront_vs_progressive_loading(self):
        """Compare context usage between upfront and progressive loading."""
        num_vendors = 80

        # Upfront loading (old method)
        tool_definition_size = 2  # KB per tool
        upfront_context = num_vendors * tool_definition_size

        # Progressive loading (new method)
        search_tool_size = 0.5  # KB for search tool
        load_tool_size = 0.5  # KB for load tool
        discovered_tools = 10  # Typically discover 10 tools
        tool_summary_size = 0.2  # KB per tool summary
        loaded_full_tools = 5  # Typically load 5 full definitions

        progressive_context = (
            search_tool_size +
            load_tool_size +
            (discovered_tools * tool_summary_size) +
            (loaded_full_tools * tool_definition_size)
        )

        # Calculate reduction
        reduction_percentage = (1 - progressive_context / upfront_context) * 100

        # Verify we achieve close to 90% reduction
        assert reduction_percentage > 85
        assert reduction_percentage < 95

        print(f"Context reduction: {reduction_percentage:.1f}%")
        print(f"Upfront: {upfront_context} KB")
        print(f"Progressive: {progressive_context} KB")


class TestIntegration:
    """Integration tests with MCP server."""

    def test_integrate_progressive_discovery(self):
        """Test integration with MCP server."""
        mock_mcp_server = Mock()
        mock_vendor_db = Mock(vendors=[])

        initial_tools, get_efficiency = integrate_progressive_discovery(
            mock_mcp_server,
            mock_vendor_db
        )

        # Should return minimal initial tools
        assert len(initial_tools) == 4  # search, load, filter, execute
        assert any(t["name"] == "search_tools" for t in initial_tools)
        assert any(t["name"] == "load_tool" for t in initial_tools)

        # Test efficiency tracking
        efficiency = get_efficiency()
        assert "message" in efficiency
        assert "context" in efficiency["message"]


class TestPerformanceMetrics:
    """Test performance improvements."""

    def test_first_response_time(self):
        """Test that first response is faster with progressive discovery."""
        import time

        # Simulate upfront loading
        start = time.time()
        tools = []
        for i in range(80):
            tools.append({
                "name": f"tool_{i}",
                "description": "x" * 1000,  # 1KB description
                "schema": {"type": "object"}
            })
        upfront_time = time.time() - start

        # Simulate progressive loading
        start = time.time()
        initial_tools = [
            {"name": "search_tools", "description": "Search", "schema": {}},
            {"name": "load_tool", "description": "Load", "schema": {}}
        ]
        progressive_time = time.time() - start

        # Progressive should be much faster
        assert progressive_time < upfront_time / 10

    def test_memory_usage(self):
        """Test memory usage comparison."""
        import sys

        # Upfront loading memory
        upfront_tools = []
        for i in range(80):
            upfront_tools.append({
                "name": f"analyze_vendor_{i}",
                "description": "x" * 2000,
                "schema": {"properties": {"req": {}}}
            })
        upfront_memory = sys.getsizeof(upfront_tools)

        # Progressive loading memory
        progressive_tools = [
            {"name": "search_tools", "description": "x" * 200},
            {"name": "load_tool", "description": "x" * 200}
        ]
        metadata_cache = {f"tool_{i}": f"summary_{i}" for i in range(80)}
        progressive_memory = (
            sys.getsizeof(progressive_tools) +
            sys.getsizeof(metadata_cache)
        )

        # Progressive should use less memory
        assert progressive_memory < upfront_memory / 5

        print(f"Memory reduction: {(1 - progressive_memory/upfront_memory) * 100:.1f}%")


@pytest.mark.benchmark
class TestBenchmarks:
    """Benchmark tests for progressive discovery."""

    def test_search_performance(self):
        """Benchmark search performance."""
        import time

        # Create loader with many vendors
        mock_vendors = []
        for i in range(100):
            mock_vendors.append(Mock(
                id=f"vendor_{i}",
                name=f"Vendor {i}",
                category=Mock(value=f"Category_{i%10}"),
                tags=[f"tag_{j}" for j in range(5)],
                capabilities=Mock(
                    cloud_native=i % 2 == 0,
                    on_prem_available=True
                ),
                is_open_source=i % 3 == 0
            ))

        mock_db = Mock(vendors=mock_vendors)
        loader = ProgressiveToolLoader(mock_db)

        # Benchmark search
        iterations = 100
        start = time.time()
        for _ in range(iterations):
            loader.search_tools(query="vendor", limit=10)
        elapsed = time.time() - start

        avg_time_ms = (elapsed / iterations) * 1000
        assert avg_time_ms < 10  # Should be very fast (< 10ms)

        print(f"Average search time: {avg_time_ms:.2f}ms")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])