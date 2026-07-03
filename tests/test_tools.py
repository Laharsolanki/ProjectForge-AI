"""
Tests for ProjectForge AI — Custom Tools

Tests the cost estimator, report tools, and memory tools.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi import HTTPException


class TestCostEstimator:
    """Tests for the cloud cost estimation tool."""

    def test_basic_aws_estimate(self):
        from tools.cost_estimator import estimate_cloud_costs

        result = estimate_cloud_costs(
            services="compute,database",
            scale="small",
            provider="aws",
        )
        assert result["provider"] == "AWS"
        assert result["scale"] == "small"
        assert result["total_monthly_usd"] > 0
        assert result["total_annual_usd"] == result["total_monthly_usd"] * 12
        assert len(result["line_items"]) >= 2

    def test_gcp_estimate(self):
        from tools.cost_estimator import estimate_cloud_costs

        result = estimate_cloud_costs(
            services="compute,database,cache",
            scale="medium",
            provider="gcp",
        )
        assert result["provider"] == "GCP"
        assert len(result["line_items"]) >= 3

    def test_azure_large_scale(self):
        from tools.cost_estimator import estimate_cloud_costs

        result = estimate_cloud_costs(
            services="compute,database,cache,monitoring,cdn",
            scale="large",
            provider="azure",
        )
        assert result["provider"] == "AZURE"
        assert result["total_monthly_usd"] > 100  # Should be significant at large scale

    def test_invalid_provider_defaults_to_aws(self):
        from tools.cost_estimator import estimate_cloud_costs

        result = estimate_cloud_costs(
            services="compute",
            scale="small",
            provider="invalid",
        )
        assert result["provider"] == "AWS"

    def test_storage_estimation(self):
        from tools.cost_estimator import estimate_cloud_costs

        result = estimate_cloud_costs(
            services="storage",
            scale="medium",
            provider="aws",
        )
        assert len(result["line_items"]) == 1
        assert "GB" in result["line_items"][0]["description"]

    def test_includes_assumptions(self):
        from tools.cost_estimator import estimate_cloud_costs

        result = estimate_cloud_costs(
            services="compute",
            scale="small",
            provider="aws",
        )
        assert len(result["assumptions"]) > 0

    def test_optimization_tips_for_small_scale(self):
        from tools.cost_estimator import estimate_cloud_costs

        result = estimate_cloud_costs(
            services="compute",
            scale="small",
            provider="aws",
        )
        assert len(result["optimization_tips"]) > 0


class TestReportTools:
    """Tests for the report generation tools."""

    def test_save_report(self, tmp_path):
        from tools.report_tools import save_report

        with patch("tools.report_tools.REPORTS_DIR", tmp_path):
            result = save_report(
                content="# Test Report\n\nThis is a test.",
                project_name="Test Project",
            )
            assert result["status"] == "success"
            assert Path(result["filepath"]).exists()
            content = Path(result["filepath"]).read_text()
            assert "# Test Report" in content

    def test_save_report_sanitizes_filename(self, tmp_path):
        from tools.report_tools import save_report

        with patch("tools.report_tools.REPORTS_DIR", tmp_path):
            result = save_report(
                content="test",
                project_name="My Project!!! @#$%",
            )
            assert result["status"] == "success"
            filename = result["filename"]
            assert "!" not in filename
            assert "@" not in filename

    def test_generate_mermaid_diagram(self):
        from tools.report_tools import generate_mermaid_diagram

        result = generate_mermaid_diagram("graph TD\nA-->B\nB-->C")
        assert result["status"] == "success"
        assert "```mermaid" in result["mermaid_code"]
        assert "graph TD" in result["raw_diagram"]

    def test_generate_mermaid_adds_default_directive(self):
        from tools.report_tools import generate_mermaid_diagram

        result = generate_mermaid_diagram("A-->B\nB-->C")
        assert result["raw_diagram"].startswith("graph TD")


class TestMemoryTools:
    """Tests for the session memory tools."""

    def test_save_and_load_project(self, tmp_path):
        from tools.memory_tools import save_project_summary, load_project_history

        with patch("tools.memory_tools.MEMORY_DIR", tmp_path):
            # Save
            save_result = save_project_summary(
                project_name="Test App",
                summary="A test application for unit testing.",
            )
            assert save_result["status"] == "success"
            assert save_result["entries"] == 1

            # Load
            load_result = load_project_history(project_name="Test App")
            assert load_result["status"] == "success"
            assert load_result["entries"] == 1
            assert "test application" in load_result["history"][0]["summary"]

    def test_append_to_existing_project(self, tmp_path):
        from tools.memory_tools import save_project_summary

        with patch("tools.memory_tools.MEMORY_DIR", tmp_path):
            save_project_summary("App", "First session")
            save_project_summary("App", "Second session")
            result = save_project_summary("App", "Third session")
            assert result["entries"] == 3

    def test_load_nonexistent_project(self, tmp_path):
        from tools.memory_tools import load_project_history

        with patch("tools.memory_tools.MEMORY_DIR", tmp_path):
            result = load_project_history("nonexistent")
            assert result["status"] == "not_found"

    def test_list_projects(self, tmp_path):
        from tools.memory_tools import save_project_summary, list_projects

        with patch("tools.memory_tools.MEMORY_DIR", tmp_path):
            save_project_summary("Project A", "Summary A")
            save_project_summary("Project B", "Summary B")

            result = list_projects()
            assert result["count"] == 2

    def test_list_empty_projects(self, tmp_path):
        from tools.memory_tools import list_projects

        with patch("tools.memory_tools.MEMORY_DIR", tmp_path):
            result = list_projects()
            assert result["count"] == 0


class TestWebReports:
    """Tests for web report download safety."""

    @pytest.mark.asyncio
    async def test_download_report_rejects_path_traversal(self, tmp_path):
        from web.app import download_report

        outside_report = tmp_path.parent / "outside.md"
        outside_report.write_text("# Outside")

        with patch("web.app.REPORTS_DIR", tmp_path):
            with pytest.raises(HTTPException) as exc_info:
                await download_report("../outside.md")

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_download_report_rejects_non_markdown(self, tmp_path):
        from web.app import download_report

        with patch("web.app.REPORTS_DIR", tmp_path):
            with pytest.raises(HTTPException) as exc_info:
                await download_report("notes.txt")

        assert exc_info.value.status_code == 400
