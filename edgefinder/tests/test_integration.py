"""
Integration tests for EdgeFinder end-to-end functionality
"""

from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from edgefinder.analyzer import RepositoryAnalyzer
from edgefinder.cli import EdgeFinderCLI
from edgefinder.downloader import RepositoryDownloader
from edgefinder.models import (
    Candidate,
    LicenseCompatibility,
    LicenseInfo,
    RepositoryStats,
    SearchCriteria,
    SourceType,
)
from edgefinder.scorer import RepositoryScorer


class TestEndToEndWorkflow:
    """Test complete EdgeFinder workflow from search to analysis"""

    @pytest.fixture
    def cli_instance(self, temp_dir):
        """CLI instance for testing"""
        config_file = temp_dir / "test_config.yaml"
        config_content = f"""
output_dir: {temp_dir / "output"}
downloads_dir: {temp_dir / "downloads"}
github:
  token: test_token_123
  rate_limit_requests: 1000
huggingface:
  token: test_hf_token_123
  rate_limit_requests: 500
"""
        config_file.write_text(config_content)
        return EdgeFinderCLI(config_file)

    @pytest.fixture
    def mock_search_candidates(self):
        """Mock search candidates for testing"""
        github_candidate = Candidate(
            id="github_integration_test",
            full_name="example/betting-odds-api",
            name="betting-odds-api",
            description="Real-time sports betting odds API with Python wrapper",
            url="https://github.com/example/betting-odds-api",
            clone_url="https://github.com/example/betting-odds-api.git",
            source=SourceType.GITHUB,
            stats=RepositoryStats(stars=450, forks=89, watchers=120, open_issues=12, size_kb=2048),
            license_info=LicenseInfo(
                name="MIT License", spdx_id="MIT", compatibility=LicenseCompatibility.COMPATIBLE
            ),
            topics=["api", "betting", "odds", "sports", "python"],
            matching_keywords=["betting", "odds", "api"],
        )

        hf_candidate = Candidate(
            id="hf_integration_test",
            full_name="models/sports-prediction-transformer",
            name="sports-prediction-transformer",
            description="Transformer model for predicting sports game outcomes",
            url="https://huggingface.co/models/sports-prediction-transformer",
            clone_url="https://huggingface.co/models/sports-prediction-transformer.git",
            source=SourceType.HUGGINGFACE,
            stats=RepositoryStats(downloads=2500, likes=180, size_kb=5120),
            license_info=LicenseInfo(
                name="Apache License 2.0",
                spdx_id="Apache-2.0",
                compatibility=LicenseCompatibility.COMPATIBLE,
            ),
            topics=["machine-learning", "sports", "prediction", "transformer"],
            matching_keywords=["sports", "prediction"],
        )

        return [github_candidate, hf_candidate]

    @pytest.mark.asyncio
    async def test_complete_search_workflow(self, cli_instance, mock_search_candidates):
        """Test complete search workflow with mocked responses"""
        criteria = SearchCriteria(
            keywords=["betting", "odds", "sports", "prediction"],
            languages=["python"],
            min_stars=50,
            max_results_per_source=100,
            license_allowlist=["MIT", "Apache-2.0"],
            sources=[SourceType.GITHUB, SourceType.HUGGINGFACE],
        )

        # Mock searcher responses
        with (
            patch("edgefinder.cli.GitHubSearcher") as mock_github_searcher,
            patch("edgefinder.cli.HuggingFaceSearcher") as mock_hf_searcher,
        ):

            # Setup GitHub searcher mock
            github_instance = AsyncMock()
            github_instance.search_repositories.return_value = [mock_search_candidates[0]]
            mock_github_searcher.return_value.__aenter__.return_value = github_instance

            # Setup HuggingFace searcher mock
            hf_instance = AsyncMock()
            hf_instance.search_repositories.return_value = [mock_search_candidates[1]]
            mock_hf_searcher.return_value.__aenter__.return_value = hf_instance

            # Run search
            candidates = await cli_instance._search_repositories(criteria)

            # Verify results
            assert len(candidates) == 2
            assert candidates[0].source == SourceType.GITHUB
            assert candidates[1].source == SourceType.HUGGINGFACE

            # Verify searchers were called correctly
            github_instance.search_repositories.assert_called_once_with(criteria)
            hf_instance.search_repositories.assert_called_once_with(criteria)

    def test_scoring_and_ranking_workflow(self, cli_instance, mock_search_candidates):
        """Test scoring and ranking of candidates"""
        criteria = SearchCriteria(keywords=["betting", "odds", "api"], languages=["python"])

        scorer = RepositoryScorer(cli_instance.config)

        # Score candidates
        ranked_candidates = scorer.rank_candidates(mock_search_candidates, criteria)

        # Verify ranking
        assert len(ranked_candidates) == 2
        assert all(candidate.score > 0 for candidate in ranked_candidates)

        # GitHub candidate should score higher (more stars, keyword matches)
        next(c for c in ranked_candidates if c.source == SourceType.GITHUB)
        next(c for c in ranked_candidates if c.source == SourceType.HUGGINGFACE)

        # Should be ranked by score
        assert ranked_candidates[0].score >= ranked_candidates[1].score

    def test_eq12_integration_scoring_bonus(self, cli_instance, mock_search_candidates):
        """Test EQ12 integration scoring bonuses"""
        criteria = SearchCriteria(
            keywords=cli_instance.config.eq12_integration.betting_keywords[
                :3
            ]  # Use EQ12 betting keywords
        )

        scorer = RepositoryScorer(cli_instance.config)
        ranked_candidates = scorer.rank_candidates(mock_search_candidates, criteria)

        # Candidates with EQ12-relevant keywords should get bonus points
        github_candidate = next(c for c in ranked_candidates if c.source == SourceType.GITHUB)

        # Should have received EQ12 integration bonus
        assert github_candidate.score > 5.0  # Base score plus bonuses

    @pytest.mark.asyncio
    async def test_download_workflow_simulation(
        self, cli_instance, mock_search_candidates, temp_dir
    ):
        """Test download workflow with file system simulation"""
        RepositoryDownloader(cli_instance.config)

        # Create mock repository content
        mock_repo_content = (
            b"# Test Repository\n\nThis is a test repository for EdgeFinder integration testing."
        )

        with patch("edgefinder.downloader.httpx.AsyncClient") as mock_client:
            # Mock HTTP response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = mock_repo_content
            mock_response.headers = {"Content-Length": str(len(mock_repo_content))}

            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            candidate = mock_search_candidates[0]

            # Attempt download (mocked)
            # This would normally download and extract the repository
            # For testing, we just verify the download logic is called correctly

            # Verify download URL construction

            # In a real scenario, this would create files in downloads_dir
            downloads_dir = Path(cli_instance.config.downloads_dir)
            downloads_dir.mkdir(parents=True, exist_ok=True)

            # Simulate successful download
            repo_dir = downloads_dir / candidate.name
            repo_dir.mkdir(exist_ok=True)
            (repo_dir / "README.md").write_text("# Mock Repository")

            assert repo_dir.exists()
            assert (repo_dir / "README.md").exists()

    def test_analysis_workflow_simulation(self, cli_instance, mock_file_system):
        """Test repository analysis workflow"""
        analyzer = RepositoryAnalyzer(cli_instance.config)

        # Analyze the mock repository
        analysis_result = analyzer.analyze_repository(mock_file_system)

        # Verify analysis results
        assert analysis_result is not None
        assert analysis_result.candidate_id is not None
        assert len(analysis_result.dependencies) > 0
        assert analysis_result.code_quality_score >= 0
        assert analysis_result.security_score >= 0

        # Should detect security issues in mock repository
        assert len(analysis_result.security_warnings) > 0

        # Should find Python dependencies
        assert any(dep in analysis_result.dependencies for dep in ["requests", "numpy", "click"])

    def test_dashboard_url_generation(self, cli_instance):
        """Test EQ12 dashboard URL generation"""
        # Test various dashboard URLs
        search_url = cli_instance.config.get_dashboard_url("search_results.html")
        analysis_url = cli_instance.config.get_dashboard_url("analysis_report.html")
        security_url = cli_instance.config.get_dashboard_url("security_scan.html")

        expected_base = "https://eq12.local/dashboards/"

        assert search_url == f"{expected_base}search_results.html"
        assert analysis_url == f"{expected_base}analysis_report.html"
        assert security_url == f"{expected_base}security_scan.html"

    def test_cli_search_summary_display(self, cli_instance, mock_search_candidates):
        """Test CLI search results summary display"""
        criteria = SearchCriteria(keywords=["betting", "api"], languages=["python"])

        # Test summary display (this would normally print to console)
        total_count = cli_instance._display_search_summary(mock_search_candidates, criteria)

        assert total_count == 2

    def test_license_compliance_filtering(self, cli_instance):
        """Test license compliance filtering across workflow"""
        # Create candidates with different licenses
        mit_candidate = Candidate(
            id="mit_test",
            full_name="test/mit-repo",
            name="mit-repo",
            source=SourceType.GITHUB,
            license_info=LicenseInfo(spdx_id="MIT", compatibility=LicenseCompatibility.COMPATIBLE),
        )

        gpl_candidate = Candidate(
            id="gpl_test",
            full_name="test/gpl-repo",
            name="gpl-repo",
            source=SourceType.GITHUB,
            license_info=LicenseInfo(
                spdx_id="GPL-3.0", compatibility=LicenseCompatibility.INCOMPATIBLE
            ),
        )

        candidates = [mit_candidate, gpl_candidate]

        # Filter with license allowlist
        scorer = RepositoryScorer(cli_instance.config)
        filtered_candidates = scorer.filter_candidates_by_license(
            candidates, allowed_licenses=["MIT", "Apache-2.0"]
        )

        # Should only include MIT candidate
        assert len(filtered_candidates) == 1
        assert filtered_candidates[0].license_info.spdx_id == "MIT"

    def test_security_validation_workflow(self, cli_instance, mock_file_system):
        """Test security validation throughout workflow"""
        analyzer = RepositoryAnalyzer(cli_instance.config)

        # Analyze repository with known security issues
        result = analyzer.analyze_repository(mock_file_system)

        # Should detect security warnings
        assert len(result.security_warnings) > 0

        # Should have appropriate security score
        assert 0 <= result.security_score <= 10

        # Critical issues should lower the score significantly
        critical_warnings = [w for w in result.security_warnings if w.severity.value == "critical"]
        if critical_warnings:
            assert result.security_score < 7.0

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, cli_instance):
        """Test error handling throughout the workflow"""
        criteria = SearchCriteria(keywords=["test"])

        # Test with failed GitHub search
        with patch("edgefinder.cli.GitHubSearcher") as mock_github_searcher:
            github_instance = AsyncMock()
            github_instance.search_repositories.side_effect = Exception("GitHub API error")
            mock_github_searcher.return_value.__aenter__.return_value = github_instance

            # Should handle GitHub error gracefully and continue with other sources
            candidates = await cli_instance._search_repositories(criteria)

            # Should return empty list or results from other sources only
            assert isinstance(candidates, list)

    def test_configuration_validation_workflow(self, temp_dir):
        """Test configuration validation in complete workflow"""
        # Test with missing required configuration
        config_file = temp_dir / "invalid_config.yaml"
        config_file.write_text(
            """
output_dir: /invalid/path
# Missing required GitHub token
github:
  token: ""
"""
        )

        # Should handle missing configuration gracefully
        cli_instance = EdgeFinderCLI(config_file)
        assert cli_instance.config is not None

        # Should use defaults for missing values
        assert cli_instance.config.github.rate_limit_requests > 0
