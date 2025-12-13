"""
Unit tests for EdgeFinder data models
"""

from datetime import UTC, datetime

import pytest

from edgefinder.models import (
    AnalysisResult,
    AuditEventType,
    AuditLogEntry,
    Candidate,
    LicenseCompatibility,
    LicenseInfo,
    RepositoryStats,
    SearchCriteria,
    SearchResult,
    SecurityWarning,
    SeverityLevel,
    SourceType,
)


class TestSearchCriteria:
    """Test search criteria model"""

    def test_basic_criteria_creation(self):
        """Test creating basic search criteria"""
        criteria = SearchCriteria(keywords=["api", "betting"], languages=["python"], min_stars=10)

        assert criteria.keywords == ["api", "betting"]
        assert criteria.languages == ["python"]
        assert criteria.min_stars == 10
        assert criteria.max_results_per_source == 100  # Default
        assert SourceType.GITHUB in criteria.sources  # Default

    def test_criteria_validation(self):
        """Test search criteria validation"""
        # Valid criteria
        criteria = SearchCriteria(keywords=["test"], min_stars=0, max_results_per_source=50)
        assert criteria.min_stars == 0

        # Invalid min_stars (negative)
        with pytest.raises(ValueError, match="min_stars must be non-negative"):
            SearchCriteria(keywords=["test"], min_stars=-1)

        # Invalid max_results (too large)
        with pytest.raises(ValueError, match="max_results_per_source cannot exceed 1000"):
            SearchCriteria(keywords=["test"], max_results_per_source=1001)

        # Empty keywords
        with pytest.raises(ValueError, match="At least one keyword is required"):
            SearchCriteria(keywords=[])

    def test_criteria_with_optional_fields(self):
        """Test criteria with all optional fields"""
        update_time = datetime(2024, 1, 1, tzinfo=UTC)

        criteria = SearchCriteria(
            keywords=["machine-learning", "pytorch"],
            languages=["python", "jupyter"],
            min_stars=50,
            max_results_per_source=25,
            updated_since=update_time,
            license_allowlist=["MIT", "Apache-2.0"],
            sources=[SourceType.HUGGINGFACE],
        )

        assert len(criteria.keywords) == 2
        assert len(criteria.languages) == 2
        assert criteria.updated_since == update_time
        assert "MIT" in criteria.license_allowlist
        assert criteria.sources == [SourceType.HUGGINGFACE]


class TestCandidate:
    """Test candidate model"""

    def test_github_candidate_creation(self):
        """Test creating GitHub candidate"""
        stats = RepositoryStats(stars=100, forks=25, watchers=50, open_issues=5, size_kb=1024)

        license_info = LicenseInfo(
            name="MIT License", spdx_id="MIT", compatibility=LicenseCompatibility.COMPATIBLE
        )

        candidate = Candidate(
            id="github_123",
            full_name="example/test-repo",
            name="test-repo",
            description="A test repository",
            url="https://github.com/example/test-repo",
            clone_url="https://github.com/example/test-repo.git",
            source=SourceType.GITHUB,
            stats=stats,
            license_info=license_info,
        )

        assert candidate.source == SourceType.GITHUB
        assert candidate.stats.stars == 100
        assert candidate.license_info.compatibility == LicenseCompatibility.COMPATIBLE
        assert candidate.score == 0.0  # Default

    def test_huggingface_candidate_creation(self):
        """Test creating Hugging Face candidate"""
        stats = RepositoryStats(downloads=1500, likes=89, size_kb=2048)

        candidate = Candidate(
            id="hf_456",
            full_name="huggingface/model",
            name="model",
            source=SourceType.HUGGINGFACE,
            stats=stats,
        )

        assert candidate.source == SourceType.HUGGINGFACE
        assert candidate.stats.downloads == 1500
        assert candidate.stats.likes == 89

    def test_candidate_scoring(self):
        """Test candidate scoring functionality"""
        candidate = Candidate(
            id="test_789",
            full_name="test/repo",
            name="repo",
            source=SourceType.GITHUB,
            score=7.5,
            matching_keywords=["api", "python", "testing"],
        )

        assert candidate.score == 7.5
        assert len(candidate.matching_keywords) == 3
        assert "python" in candidate.matching_keywords


class TestLicenseInfo:
    """Test license information model"""

    def test_compatible_license(self):
        """Test compatible license info"""
        license_info = LicenseInfo(
            name="MIT License",
            spdx_id="MIT",
            url="https://opensource.org/licenses/MIT",
            compatibility=LicenseCompatibility.COMPATIBLE,
        )

        assert license_info.name == "MIT License"
        assert license_info.spdx_id == "MIT"
        assert license_info.compatibility == LicenseCompatibility.COMPATIBLE

    def test_incompatible_license(self):
        """Test incompatible license info"""
        license_info = LicenseInfo(
            name="GNU General Public License v3.0",
            spdx_id="GPL-3.0",
            compatibility=LicenseCompatibility.INCOMPATIBLE,
        )

        assert license_info.spdx_id == "GPL-3.0"
        assert license_info.compatibility == LicenseCompatibility.INCOMPATIBLE

    def test_unknown_license(self):
        """Test unknown license compatibility"""
        license_info = LicenseInfo(compatibility=LicenseCompatibility.UNKNOWN)

        assert license_info.name is None
        assert license_info.spdx_id is None
        assert license_info.compatibility == LicenseCompatibility.UNKNOWN


class TestRepositoryStats:
    """Test repository statistics model"""

    def test_github_stats(self):
        """Test GitHub repository statistics"""
        stats = RepositoryStats(
            stars=1250,
            forks=340,
            watchers=890,
            open_issues=42,
            size_kb=5120,
            updated_at=datetime(2024, 1, 15, tzinfo=UTC),
        )

        assert stats.stars == 1250
        assert stats.forks == 340
        assert stats.watchers == 890
        assert stats.open_issues == 42
        assert stats.size_kb == 5120

    def test_huggingface_stats(self):
        """Test Hugging Face model statistics"""
        stats = RepositoryStats(downloads=5000, likes=150, size_kb=2048)

        assert stats.downloads == 5000
        assert stats.likes == 150
        assert stats.stars is None  # Not applicable for HF
        assert stats.forks is None


class TestSecurityWarning:
    """Test security warning model"""

    def test_security_warning_creation(self):
        """Test creating security warning"""
        warning = SecurityWarning(
            rule_id="B101",
            message="Use of assert detected",
            severity=SeverityLevel.LOW,
            file_path="src/main.py",
            line_number=42,
            details="Assert statements are removed in optimized Python",
        )

        assert warning.rule_id == "B101"
        assert warning.severity == SeverityLevel.LOW
        assert warning.file_path == "src/main.py"
        assert warning.line_number == 42

    def test_critical_security_warning(self):
        """Test critical security warning"""
        warning = SecurityWarning(
            rule_id="B602",
            message="subprocess call with shell=True identified",
            severity=SeverityLevel.CRITICAL,
            file_path="vulnerable.py",
            line_number=10,
        )

        assert warning.severity == SeverityLevel.CRITICAL
        assert "shell=True" in warning.message


class TestAnalysisResult:
    """Test analysis result model"""

    def test_analysis_result_creation(self):
        """Test creating analysis result"""
        warnings = [
            SecurityWarning(
                rule_id="B101",
                message="Assert usage",
                severity=SeverityLevel.LOW,
                file_path="test.py",
                line_number=1,
            )
        ]

        result = AnalysisResult(
            candidate_id="github_123",
            dependencies=["requests", "numpy"],
            security_warnings=warnings,
            code_quality_score=8.5,
            maintainability_score=7.8,
            security_score=9.2,
            license_compliance=True,
            eq12_integration_potential=8.9,
        )

        assert result.candidate_id == "github_123"
        assert len(result.dependencies) == 2
        assert len(result.security_warnings) == 1
        assert result.code_quality_score == 8.5
        assert result.license_compliance is True
        assert result.eq12_integration_potential == 8.9

    def test_analysis_result_scores_validation(self):
        """Test analysis result score validation"""
        # Valid scores (0-10 range)
        result = AnalysisResult(
            candidate_id="test",
            code_quality_score=8.5,
            maintainability_score=7.0,
            security_score=9.9,
            eq12_integration_potential=10.0,
        )

        assert 0 <= result.code_quality_score <= 10
        assert 0 <= result.security_score <= 10

        # Invalid scores should raise validation error
        with pytest.raises(ValueError):
            AnalysisResult(candidate_id="test", code_quality_score=-1.0)  # Invalid

        with pytest.raises(ValueError):
            AnalysisResult(candidate_id="test", security_score=11.0)  # Invalid


class TestSearchResult:
    """Test search result model"""

    def test_search_result_creation(self, sample_github_candidate, sample_huggingface_candidate):
        """Test creating search result"""
        candidates = [sample_github_candidate, sample_huggingface_candidate]

        result = SearchResult(
            query="betting api python",
            candidates=candidates,
            total_found=2,
            sources_searched=[SourceType.GITHUB, SourceType.HUGGINGFACE],
        )

        assert result.query == "betting api python"
        assert len(result.candidates) == 2
        assert result.total_found == 2
        assert len(result.sources_searched) == 2

    def test_empty_search_result(self):
        """Test empty search result"""
        result = SearchResult(
            query="nonexistent query",
            candidates=[],
            total_found=0,
            sources_searched=[SourceType.GITHUB],
        )

        assert len(result.candidates) == 0
        assert result.total_found == 0


class TestAuditLogEntry:
    """Test audit log entry model"""

    def test_audit_log_entry_creation(self):
        """Test creating audit log entry"""
        timestamp = datetime.now(UTC)

        entry = AuditLogEntry(
            timestamp=timestamp,
            event_type=AuditEventType.SEARCH_EXECUTED,
            details={"query": "test query", "results": 5},
            user="test_user",
            ip_address="192.168.1.1",
        )

        assert entry.event_type == AuditEventType.SEARCH_EXECUTED
        assert entry.details["query"] == "test query"
        assert entry.user == "test_user"
        assert entry.ip_address == "192.168.1.1"

    def test_audit_log_security_event(self):
        """Test security-related audit log entry"""
        entry = AuditLogEntry(
            event_type=AuditEventType.SECURITY_SCAN_COMPLETED,
            details={"candidate_id": "github_123", "warnings_found": 3, "severity": "medium"},
        )

        assert entry.event_type == AuditEventType.SECURITY_SCAN_COMPLETED
        assert entry.details["warnings_found"] == 3
