"""
Repository Scoring System
Intelligent scoring and ranking of repository candidates based on multiple criteria
"""

import logging
from datetime import UTC, datetime

from .config import Config
from .models import (
    AnalysisResult,
    Candidate,
    LicenseCompatibility,
    SearchCriteria,
    SecurityLevel,
)

logger = logging.getLogger(__name__)


class RepositoryScorer:
    """
    Intelligent scoring system for repository candidates

    Combines multiple factors including license compatibility, popularity,
    recent activity, keyword matches, and security analysis to produce
    a comprehensive score from 0-100.
    """

    def __init__(self, config: Config):
        self.config = config

    def _score_license_compatibility(self, candidate: Candidate) -> float:
        """
        Score based on license compatibility

        Args:
            candidate: Repository candidate

        Returns:
            License compatibility score (0-20)
        """
        if not candidate.license_info:
            return 0.0

        if candidate.license_info.compatibility == LicenseCompatibility.COMPATIBLE:
            return self.config.scoring.license_bonus
        elif candidate.license_info.compatibility == LicenseCompatibility.REQUIRES_REVIEW:
            return self.config.scoring.license_bonus * 0.5
        else:
            return 0.0  # Incompatible or unknown

    def _score_popularity(self, candidate: Candidate) -> float:
        """
        Score based on repository popularity (stars, forks, etc.)

        Args:
            candidate: Repository candidate

        Returns:
            Popularity score (0-30)
        """
        max_score = 30.0

        # Use stars as primary popularity metric
        stars = candidate.stats.stars

        if stars == 0:
            return 0.0

        # Logarithmic scaling to handle wide range of star counts
        # 1 star = 5 points, 10 stars = 10 points, 100 stars = 15 points,
        # 1000 stars = 20 points, 10000+ stars = 25-30 points
        import math

        log_stars = math.log10(max(1, stars))
        score = min(max_score, log_stars * 7.5)

        # Bonus for additional engagement metrics
        if candidate.stats.forks > 0:
            score += min(5, candidate.stats.forks / 10)

        if candidate.stats.watchers > 0:
            score += min(2, candidate.stats.watchers / 50)

        return min(max_score, score)

    def _score_recent_activity(self, candidate: Candidate) -> float:
        """
        Score based on recent activity and maintenance

        Args:
            candidate: Repository candidate

        Returns:
            Activity score (0-20)
        """
        max_score = 20.0

        # Use the most recent update timestamp
        latest_update = None
        for timestamp in [candidate.stats.updated_at, candidate.stats.pushed_at]:
            if timestamp and (latest_update is None or timestamp > latest_update):
                latest_update = timestamp

        if not latest_update:
            return 0.0

        # Calculate days since last update
        now = datetime.now(UTC)
        days_ago = (now - latest_update).days

        if days_ago <= 7:
            return max_score  # Very recent
        elif days_ago <= 30:
            return max_score * 0.9  # Recent
        elif days_ago <= 90:
            return max_score * 0.7  # Somewhat recent
        elif days_ago <= 365:
            return max_score * 0.4  # Within a year
        elif days_ago <= 730:
            return max_score * 0.2  # Within 2 years
        else:
            return 0.0  # Too old

    def _score_keyword_relevance(
        self, candidate: Candidate, search_criteria: SearchCriteria
    ) -> float:
        """
        Score based on keyword matches in description, topics, and name

        Args:
            candidate: Repository candidate
            search_criteria: Original search criteria

        Returns:
            Keyword relevance score (0-20)
        """
        max_score = 20.0

        if not search_criteria.keywords:
            return max_score * 0.5  # Neutral score if no keywords

        # Combine searchable text
        searchable_text = []

        if candidate.name:
            searchable_text.append(candidate.name.lower())

        if candidate.description:
            searchable_text.append(candidate.description.lower())

        if candidate.topics:
            searchable_text.extend([topic.lower() for topic in candidate.topics])

        combined_text = " ".join(searchable_text)

        # Score based on keyword matches
        total_keywords = len(search_criteria.keywords)
        matched_keywords = 0

        for keyword in search_criteria.keywords:
            keyword_lower = keyword.lower()

            # Direct match gets full score
            if keyword_lower in combined_text:
                matched_keywords += 1
            # Partial match gets half score
            elif any(keyword_lower in text_part for text_part in searchable_text):
                matched_keywords += 0.5

        # Calculate match ratio
        match_ratio = matched_keywords / total_keywords if total_keywords > 0 else 0

        return max_score * match_ratio

    def _score_language_match(self, candidate: Candidate, search_criteria: SearchCriteria) -> float:
        """
        Score based on programming language matches

        Args:
            candidate: Repository candidate
            search_criteria: Original search criteria

        Returns:
            Language match bonus (0-10)
        """
        max_bonus = self.config.scoring.language_bonus

        if not search_criteria.languages or not candidate.languages:
            return 0.0

        # Check if any of the requested languages are present
        requested_languages = [lang.lower() for lang in search_criteria.languages]
        repo_languages = [lang.lower() for lang in candidate.languages]

        matches = set(requested_languages) & set(repo_languages)

        if matches:
            # Bonus proportional to number of matches
            return max_bonus * (len(matches) / len(requested_languages))

        return 0.0

    def _calculate_security_penalty(self, analysis: AnalysisResult | None) -> float:
        """
        Calculate penalty based on security warnings

        Args:
            analysis: Analysis result with security warnings

        Returns:
            Security penalty (negative value)
        """
        if not analysis or not analysis.security_warnings:
            return 0.0

        penalty = 0.0
        penalty_per_level = {
            SecurityLevel.LOW: 2,
            SecurityLevel.MEDIUM: 8,
            SecurityLevel.HIGH: 20,
            SecurityLevel.CRITICAL: 50,
        }

        for warning in analysis.security_warnings:
            penalty += penalty_per_level.get(warning.level, 0)

        return -penalty

    def _calculate_eq12_integration_bonus(
        self, candidate: Candidate, search_criteria: SearchCriteria
    ) -> float:
        """
        Calculate bonus for EQ12-specific integration potential

        Args:
            candidate: Repository candidate
            search_criteria: Search criteria

        Returns:
            EQ12 integration bonus (0-15)
        """
        bonus = 0.0

        # Check if search is related to EQ12 betting functionality
        if self.config.is_eq12_betting_related(search_criteria.keywords):
            betting_indicators = [
                "odds",
                "parlay",
                "sportsbook",
                "betting",
                "wager",
                "mlb",
                "nfl",
                "nba",
                "nhl",
                "sports",
            ]

            searchable_text = (
                f"{candidate.name} {candidate.description} " + " ".join(candidate.topics or [])
            ).lower()

            matches = sum(1 for indicator in betting_indicators if indicator in searchable_text)
            bonus += min(10, matches * 2)

        # Check if search is related to EQ12 AI functionality
        if self.config.is_eq12_ai_related(search_criteria.keywords):
            ai_indicators = [
                "llama",
                "transformer",
                "gpt",
                "ai",
                "ml",
                "machine learning",
                "neural",
                "model",
                "agent",
                "assistant",
            ]

            searchable_text = (
                f"{candidate.name} {candidate.description} " + " ".join(candidate.topics or [])
            ).lower()

            matches = sum(1 for indicator in ai_indicators if indicator in searchable_text)
            bonus += min(8, matches * 1.5)

        # Bonus for having good documentation
        if candidate.description and len(candidate.description) > 50:
            bonus += 2

        # Bonus for having topics/tags
        if candidate.topics and len(candidate.topics) >= 3:
            bonus += 2

        return bonus

    def score_candidate(
        self,
        candidate: Candidate,
        search_criteria: SearchCriteria,
        analysis: AnalysisResult | None = None,
    ) -> float:
        """
        Calculate comprehensive score for repository candidate

        Args:
            candidate: Repository candidate
            search_criteria: Original search criteria
            analysis: Optional analysis results for security scoring

        Returns:
            Comprehensive score (0-100)
        """
        logger.debug(f"Scoring candidate: {candidate.id}")

        # Calculate component scores
        license_score = self._score_license_compatibility(candidate)
        popularity_score = self._score_popularity(candidate)
        activity_score = self._score_recent_activity(candidate)
        keyword_score = self._score_keyword_relevance(candidate, search_criteria)
        language_bonus = self._score_language_match(candidate, search_criteria)
        security_penalty = self._calculate_security_penalty(analysis)
        eq12_bonus = self._calculate_eq12_integration_bonus(candidate, search_criteria)

        # Calculate total score
        total_score = (
            license_score
            + popularity_score
            + activity_score
            + keyword_score
            + language_bonus
            + security_penalty
            + eq12_bonus
        )

        # Ensure score is within bounds
        final_score = max(0.0, min(100.0, total_score))

        # Store component scores for debugging
        scoring_details = {
            "license": license_score,
            "popularity": popularity_score,
            "activity": activity_score,
            "keywords": keyword_score,
            "language": language_bonus,
            "security": security_penalty,
            "eq12_integration": eq12_bonus,
            "total": final_score,
        }

        logger.debug(f"Scoring details for {candidate.id}: {scoring_details}")

        # Generate human-readable reason
        reason_parts = []

        if license_score > 0:
            reason_parts.append(f"Compatible license (+{license_score:.1f})")

        if popularity_score > 15:
            reason_parts.append(f"Popular repository (+{popularity_score:.1f})")
        elif popularity_score > 5:
            reason_parts.append(f"Some popularity (+{popularity_score:.1f})")

        if activity_score > 15:
            reason_parts.append("Recently active")
        elif activity_score > 5:
            reason_parts.append("Moderately active")

        if keyword_score > 10:
            reason_parts.append("Strong keyword match")
        elif keyword_score > 5:
            reason_parts.append("Partial keyword match")

        if language_bonus > 0:
            reason_parts.append("Language match")

        if security_penalty < -10:
            reason_parts.append("Security concerns")

        if eq12_bonus > 5:
            reason_parts.append("Good EQ12 integration potential")

        candidate.score = final_score
        candidate.reason_summary = "; ".join(reason_parts) if reason_parts else "Basic scoring"

        return final_score

    def rank_candidates(
        self,
        candidates: list[Candidate],
        search_criteria: SearchCriteria,
        analyses: dict[str, AnalysisResult] | None = None,
    ) -> list[Candidate]:
        """
        Score and rank all candidates

        Args:
            candidates: List of repository candidates
            search_criteria: Original search criteria
            analyses: Optional mapping of candidate_id to analysis results

        Returns:
            Sorted list of candidates (highest score first)
        """
        logger.info(f"Ranking {len(candidates)} candidates")

        analyses = analyses or {}

        # Score all candidates
        for candidate in candidates:
            analysis = analyses.get(candidate.id)
            self.score_candidate(candidate, search_criteria, analysis)

        # Sort by score (descending)
        ranked_candidates = sorted(candidates, key=lambda c: c.score, reverse=True)

        # Log top candidates
        logger.info("Top 5 candidates by score:")
        for i, candidate in enumerate(ranked_candidates[:5], 1):
            logger.info(
                f"  {i}. {candidate.full_name}: {candidate.score:.1f} - {candidate.reason_summary}"
            )

        return ranked_candidates

    def filter_candidates_by_score(
        self,
        candidates: list[Candidate],
        min_score: float = 50.0,
        max_candidates: int | None = None,
    ) -> list[Candidate]:
        """
        Filter candidates by minimum score and optionally limit count

        Args:
            candidates: List of scored candidates
            min_score: Minimum score threshold
            max_candidates: Maximum number of candidates to return

        Returns:
            Filtered list of candidates
        """
        # Filter by minimum score
        filtered = [c for c in candidates if c.score >= min_score]

        # Limit count if specified
        if max_candidates:
            filtered = filtered[:max_candidates]

        logger.info(f"Filtered to {len(filtered)} candidates (min_score: {min_score})")

        return filtered
