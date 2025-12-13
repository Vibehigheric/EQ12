#!/usr/bin/env python3
"""
EQ12 Sportsbook Management
Centralized whitelist enforcement for DraftKings, FanDuel, and BetMGM only.

This module provides the single source of truth for allowed sportsbooks
in the EQ12 professional sports betting automation stack.
"""

import logging

logger = logging.getLogger(__name__)

# EQ12 OFFICIAL SPORTSBOOK POLICY
# Only these three sportsbooks are allowed in the EQ12 system
ALLOWED_SPORTSBOOKS: set[str] = {"draftkings", "fanduel", "betmgm"}

# Alternative names and aliases that map to allowed books
SPORTSBOOK_ALIASES: dict[str, str] = {
    # DraftKings variants
    "dk": "draftkings",
    "draft kings": "draftkings",
    "draftkings sportsbook": "draftkings",
    # FanDuel variants
    "fd": "fanduel",
    "fan duel": "fanduel",
    "fanduel sportsbook": "fanduel",
    # BetMGM variants
    "mgm": "betmgm",
    "bet mgm": "betmgm",
    "betmgm sportsbook": "betmgm",
    "mgm sportsbook": "betmgm",
}

# Explicitly unauthorized sportsbooks (will trigger warnings/errors)
UNAUTHORIZED_SPORTSBOOKS: set[str] = {
    "caesars",
    "bet365",
    "barstool",
    "pointsbet",
    "wynnbet",
    "betrivers",
    "unibet",
    "bovada",
    "circa",
    "superbook",
}


class SportsBookValidator:
    """Professional sportsbook validation and normalization."""

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.validation_log: list[dict] = []

    def normalize_sportsbook_name(self, raw_name: str) -> str | None:
        """
        Normalize sportsbook name to official EQ12 format.

        Args:
            raw_name: Raw sportsbook name from API or user input

        Returns:
            Normalized name if allowed, None if unauthorized

        Raises:
            ValueError: If strict_mode=True and unauthorized book provided
        """
        if not raw_name:
            return None

        # Clean and normalize input
        cleaned = raw_name.lower().strip()

        # Direct match to allowed books
        if cleaned in ALLOWED_SPORTSBOOKS:
            return cleaned

        # Check aliases
        if cleaned in SPORTSBOOK_ALIASES:
            normalized = SPORTSBOOK_ALIASES[cleaned]
            logger.debug(f"Normalized '{raw_name}' -> '{normalized}'")
            return normalized

        # Check for unauthorized books
        if cleaned in UNAUTHORIZED_SPORTSBOOKS:
            error_msg = f"Unauthorized sportsbook: '{raw_name}' - EQ12 policy allows only DK/FD/MGM"

            self.validation_log.append(
                {
                    "type": "unauthorized_book",
                    "raw_name": raw_name,
                    "message": error_msg,
                }
            )

            if self.strict_mode:
                raise ValueError(error_msg)
            else:
                logger.warning(error_msg)
                return None

        # Unknown sportsbook
        warning_msg = f"Unknown sportsbook: '{raw_name}' - not in EQ12 whitelist"

        self.validation_log.append(
            {"type": "unknown_book", "raw_name": raw_name, "message": warning_msg}
        )

        logger.warning(warning_msg)
        return None if self.strict_mode else cleaned

    def validate_sportsbook_list(self, sportsbooks: list[str]) -> list[str]:
        """
        Validate and normalize a list of sportsbooks.

        Args:
            sportsbooks: List of raw sportsbook names

        Returns:
            List of normalized, valid sportsbook names
        """
        validated = []

        for book in sportsbooks:
            try:
                normalized = self.normalize_sportsbook_name(book)
                if normalized:
                    validated.append(normalized)
            except ValueError:
                # Skip unauthorized books in strict mode
                continue

        return list(set(validated))  # Remove duplicates

    def is_authorized_sportsbook(self, sportsbook_name: str) -> bool:
        """
        Quick check if a sportsbook is authorized.

        Args:
            sportsbook_name: Raw sportsbook name

        Returns:
            True if authorized, False otherwise
        """
        try:
            normalized = self.normalize_sportsbook_name(sportsbook_name)
            return normalized is not None
        except ValueError:
            return False

    def get_allowed_sportsbooks(self) -> list[str]:
        """Get list of all allowed sportsbooks."""
        return list(ALLOWED_SPORTSBOOKS)

    def get_validation_report(self) -> dict:
        """Get validation report with warnings and errors."""
        unauthorized_count = len(
            [log for log in self.validation_log if log["type"] == "unauthorized_book"]
        )
        unknown_count = len(
            [log for log in self.validation_log if log["type"] == "unknown_book"])

        return {
            "total_validations": len(self.validation_log),
            "unauthorized_books": unauthorized_count,
            "unknown_books": unknown_count,
            "allowed_books": list(ALLOWED_SPORTSBOOKS),
            "validation_log": self.validation_log[-10:],  # Last 10 entries
        }


def filter_authorized_odds_data(odds_data: list[dict]) -> list[dict]:
    """
    Filter odds data to only include authorized sportsbooks.

    Args:
        odds_data: List of odds records with 'book' or 'bookmaker' fields

    Returns:
        Filtered list containing only DK/FD/MGM data
    """
    validator = SportsBookValidator(strict_mode=False)
    filtered = []

    for record in odds_data:
        # Try common field names for sportsbook
        book_name = record.get("book") or record.get(
            "bookmaker") or record.get("sportsbook")

        if book_name and validator.is_authorized_sportsbook(book_name):
            # Normalize the book name in the record
            record = record.copy()  # Don't modify original
            normalized_name = validator.normalize_sportsbook_name(book_name)

            # Update with normalized name
            if "book" in record:
                record["book"] = normalized_name
            elif "bookmaker" in record:
                record["bookmaker"] = normalized_name
            elif "sportsbook" in record:
                record["sportsbook"] = normalized_name

            filtered.append(record)

    logger.info(
        f"Filtered {len(odds_data)} records -> {len(filtered)} authorized sportsbooks")
    return filtered


def get_sportsbook_api_mapping() -> dict[str, str]:
    """
    Get mapping of EQ12 normalized names to external API identifiers.

    Returns:
        Mapping for API integration (e.g., The Odds API format)
    """
    return {"draftkings": "draftkings", "fanduel": "fanduel", "betmgm": "betmgm"}


def validate_environment_sportsbooks() -> bool:
    """
    Validate that environment/config only references authorized sportsbooks.
    Used in CI/CD pipeline validation.

    Returns:
        True if all sportsbooks in environment are authorized
    """
    import os

    # Check common environment variable patterns
    env_vars_to_check = [
        "ALLOWED_SPORTSBOOKS",
        "SPORTSBOOK_WHITELIST",
        "BOOKMAKER_LIST",
    ]

    validator = SportsBookValidator(strict_mode=False)
    all_valid = True

    for env_var in env_vars_to_check:
        env_value = os.getenv(env_var)
        if env_value:
            sportsbooks = [book.strip() for book in env_value.split(",")]

            for book in sportsbooks:
                if not validator.is_authorized_sportsbook(book):
                    logger.error(f"Unauthorized sportsbook in {env_var}: {book}")
                    all_valid = False

    return all_valid


# Convenience functions for common operations
def is_draftkings(sportsbook_name: str) -> bool:
    """Check if sportsbook is DraftKings (any variant)."""
    validator = SportsBookValidator()
    normalized = validator.normalize_sportsbook_name(sportsbook_name)
    return normalized == "draftkings"


def is_fanduel(sportsbook_name: str) -> bool:
    """Check if sportsbook is FanDuel (any variant)."""
    validator = SportsBookValidator()
    normalized = validator.normalize_sportsbook_name(sportsbook_name)
    return normalized == "fanduel"


def is_betmgm(sportsbook_name: str) -> bool:
    """Check if sportsbook is BetMGM (any variant)."""
    validator = SportsBookValidator()
    normalized = validator.normalize_sportsbook_name(sportsbook_name)
    return normalized == "betmgm"


# Module-level validator instance for convenience
default_validator = SportsBookValidator()

# Export key functions for easy imports
__all__ = [
    "ALLOWED_SPORTSBOOKS",
    "SportsBookValidator",
    "default_validator",
    "filter_authorized_odds_data",
    "get_sportsbook_api_mapping",
    "is_betmgm",
    "is_draftkings",
    "is_fanduel",
    "validate_environment_sportsbooks",
]
