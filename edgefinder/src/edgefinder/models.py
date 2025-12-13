"""
EdgeFinder Data Models
Pydantic models for type safety and validation
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, validator


class SourceType(str, Enum):
    """Repository source types"""

    GITHUB = "github"
    HUGGINGFACE = "huggingface"


class LicenseCompatibility(str, Enum):
    """License compatibility status"""

    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"
    REQUIRES_REVIEW = "requires_review"


class SecurityLevel(str, Enum):
    """Security warning levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnalysisStatus(str, Enum):
    """Analysis completion status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class SecurityWarning(BaseModel):
    """Security analysis warning"""

    level: SecurityLevel
    title: str
    description: str
    file_path: str | None = None
    line_number: int | None = None
    rule_id: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class LicenseInfo(BaseModel):
    """Repository license information"""

    name: str | None = None
    spdx_id: str | None = None
    compatibility: LicenseCompatibility
    url: HttpUrl | None = None
    text: str | None = None
    requires_attribution: bool = False
    commercial_use_allowed: bool = False


class RepositoryStats(BaseModel):
    """Repository statistics and metadata"""

    stars: int = 0
    forks: int = 0
    watchers: int = 0
    open_issues: int = 0
    size_kb: int = 0
    default_branch: str = "main"
    created_at: datetime | None = None
    updated_at: datetime | None = None
    pushed_at: datetime | None = None


class DependencyInfo(BaseModel):
    """Dependency analysis results"""

    name: str
    version: str | None = None
    ecosystem: str  # npm, pypi, crates.io, etc.
    security_advisories: list[str] = Field(default_factory=list)
    license: str | None = None
    outdated: bool = False


class CodeMetrics(BaseModel):
    """Code quality and complexity metrics"""

    lines_of_code: int = 0
    cyclomatic_complexity: float | None = None
    maintainability_index: float | None = None
    test_coverage: float | None = None
    documentation_coverage: float | None = None
    code_duplication: float | None = None


class Candidate(BaseModel):
    """Repository candidate model"""

    id: str = Field(description="Unique identifier")
    source: SourceType
    owner: str
    name: str
    full_name: str
    description: str | None = None
    url: HttpUrl
    clone_url: str | None = None
    homepage: HttpUrl | None = None

    # Repository metadata
    stats: RepositoryStats = Field(default_factory=RepositoryStats)
    license_info: LicenseInfo | None = None
    languages: dict[str, int] = Field(default_factory=dict)  # language -> bytes
    topics: list[str] = Field(default_factory=list)

    # Analysis results
    score: float = Field(default=0.0, ge=0.0, le=100.0)
    reason_summary: str = ""
    keyword_matches: list[str] = Field(default_factory=list)

    # Download and analysis
    download_path: str | None = None
    analysis_status: AnalysisStatus = AnalysisStatus.PENDING

    @validator("id", pre=True, always=True)
    def generate_id(cls, v, values):
        if v is None:
            source = values.get("source", "")
            owner = values.get("owner", "")
            name = values.get("name", "")
            return f"{source}:{owner}/{name}"
        return v

    @property
    def primary_language(self) -> str | None:
        """Get the primary programming language"""
        if not self.languages:
            return None
        return max(self.languages.items(), key=lambda x: x[1])[0]


class SearchCriteria(BaseModel):
    """Search parameters and filters"""

    keywords: list[str] = Field(min_items=1)
    languages: list[str] = Field(default_factory=list)
    min_stars: int = Field(default=0, ge=0)
    max_results_per_source: int = Field(default=50, ge=1, le=1000)
    updated_since: datetime | None = None
    license_allowlist: list[str] = Field(default_factory=list)
    sources: list[SourceType] = Field(
        default_factory=lambda: [SourceType.GITHUB, SourceType.HUGGINGFACE]
    )

    @validator("keywords", pre=True)
    def validate_keywords(cls, v):
        if isinstance(v, str):
            return [k.strip() for k in v.split() if k.strip()]
        return [str(k).strip() for k in v if str(k).strip()]

    @validator("languages", pre=True)
    def validate_languages(cls, v):
        if isinstance(v, str):
            return [lang.strip().lower() for lang in v.split(",") if lang.strip()]
        return [str(lang).strip().lower() for lang in v if str(lang).strip()]


class SearchResult(BaseModel):
    """Search operation results"""

    criteria: SearchCriteria
    candidates: list[Candidate] = Field(default_factory=list)
    total_found: int = 0
    sources_searched: list[SourceType] = Field(default_factory=list)
    search_time_seconds: float = 0.0
    rate_limited: bool = False
    errors: list[str] = Field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate search success rate"""
        if not self.sources_searched:
            return 0.0
        successful_sources = len(
            [s for s in self.sources_searched if s in [c.source for c in self.candidates]]
        )
        return successful_sources / len(self.sources_searched)


class AnalysisResult(BaseModel):
    """Repository analysis results"""

    candidate_id: str
    analysis_status: AnalysisStatus = AnalysisStatus.PENDING

    # Security analysis
    security_warnings: list[SecurityWarning] = Field(default_factory=list)
    dependencies: list[DependencyInfo] = Field(default_factory=list)

    # Code quality
    code_metrics: CodeMetrics | None = None

    # Files analysis
    readme_content: str | None = None
    license_text: str | None = None
    important_files: list[str] = Field(default_factory=list)

    # Patch generation
    suggested_patch: str | None = None
    patch_description: str | None = None

    # Integration suggestions
    suggested_pr_text: dict[str, str] | None = None
    integration_notes: list[str] = Field(default_factory=list)

    # Timestamps
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @property
    def analysis_duration(self) -> float | None:
        """Get analysis duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def security_score(self) -> float:
        """Calculate security score (0-100, higher is better)"""
        if not self.security_warnings:
            return 100.0

        # Penalty based on warning levels
        penalties = {
            SecurityLevel.LOW: 5,
            SecurityLevel.MEDIUM: 15,
            SecurityLevel.HIGH: 30,
            SecurityLevel.CRITICAL: 50,
        }

        total_penalty = sum(penalties.get(w.level, 0) for w in self.security_warnings)
        return max(0.0, 100.0 - total_penalty)


class AuditLogEntry(BaseModel):
    """Audit trail entry"""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str
    details: dict[str, Any] = Field(default_factory=dict)
    user_agent: str = "EdgeFinder/1.0.0"
    api_endpoint: str | None = None
    response_code: int | None = None
    rate_limit_remaining: int | None = None


class ReportSummary(BaseModel):
    """Comprehensive analysis report"""

    generated_at: datetime = Field(default_factory=datetime.utcnow)
    search_criteria: SearchCriteria
    total_candidates: int = 0
    analyzed_candidates: int = 0

    # Top candidates by score
    top_candidates: list[Candidate] = Field(default_factory=list)

    # Analysis summaries
    analysis_results: list[AnalysisResult] = Field(default_factory=list)

    # Security overview
    total_security_warnings: int = 0
    critical_security_issues: int = 0

    # License compliance
    license_compatible_count: int = 0
    license_incompatible_count: int = 0

    # Recommendations
    recommendations: list[str] = Field(default_factory=list)

    # Audit trail
    audit_log: list[AuditLogEntry] = Field(default_factory=list)

    @property
    def analysis_completion_rate(self) -> float:
        """Percentage of candidates that were analyzed"""
        if self.total_candidates == 0:
            return 0.0
        return (self.analyzed_candidates / self.total_candidates) * 100.0
