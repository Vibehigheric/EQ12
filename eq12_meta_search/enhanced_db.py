#!/usr/bin/env python3
"""
Enhanced Database Schema for EQ12 Meta-Search with Intelligence Integration
Extends existing db.py to store enriched intelligence data while maintaining backward compatibility.

Author: EQ12 AI Assistant
Created: 2025-01-27
"""

import json
import logging
import os
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from typing import Any

logger = logging.getLogger("enhanced_db")

# Environment configuration
DB_PATH = os.getenv("META_DB_PATH", "meta_search_enhanced.sqlite3")
LEGACY_DB_PATH = os.getenv("LEGACY_META_DB_PATH", "meta_search.sqlite3")

# Enhanced schema with intelligence data support
ENHANCED_SCHEMA = """
-- Original results table (backward compatibility)
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    title TEXT,
    url TEXT UNIQUE,
    snippet TEXT,
    source TEXT,
    published_at TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced results table with intelligence metadata
CREATE TABLE IF NOT EXISTS results_enhanced (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    title TEXT,
    url TEXT,
    snippet TEXT,
    source TEXT,
    published_at TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Intelligence enhancement fields
    detected_stack TEXT,                    -- betting, travel, cannabis, finance, fleet
    confidence_score REAL,                  -- 0.0-1.0 confidence in stack detection
    intelligence_used BOOLEAN DEFAULT 0,    -- Whether intelligence module was used
    enhancement_source TEXT,                -- Which intelligence module provided enhancement

    -- Rich metadata (JSON)
    metadata TEXT,                         -- JSON blob for stack-specific metadata
    analysis_results TEXT,                 -- JSON blob for analysis results
    keywords_matched TEXT,                 -- JSON array of matched keywords
    sentiment_score REAL,                  -- Sentiment analysis score (-1.0 to 1.0)
    relevance_score REAL,                  -- Relevance score (0.0-1.0)

    -- Categorization
    primary_category TEXT,                 -- Main category (e.g., "injury", "booking")
    secondary_category TEXT,               -- Sub-category
    tags TEXT,                            -- JSON array of tags

    -- Content analysis
    content_type TEXT,                    -- news, blog, official, social, etc.
    language_detected TEXT,               -- Language code (en, es, etc.)

    -- Performance metrics
    processing_time_ms INTEGER,           -- Time to process this result
    api_calls_used INTEGER DEFAULT 1,    -- Number of API calls for this result

    UNIQUE(query, url, source)            -- Prevent duplicates per query/url/source combo
);

-- News articles with intelligence analysis
CREATE TABLE IF NOT EXISTS news_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    snippet TEXT,
    content TEXT,                         -- Full article content if scraped
    source TEXT NOT NULL,
    published_at TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- News-specific fields
    detected_stack TEXT,                  -- betting, travel, cannabis, finance, fleet
    confidence_score REAL,               -- Confidence in stack detection

    -- Sentiment analysis
    sentiment_analysis TEXT,             -- JSON blob with sentiment data
    overall_sentiment TEXT,              -- positive, negative, neutral
    sentiment_score REAL,                -- -1.0 to 1.0
    sentiment_confidence REAL,           -- Confidence in sentiment analysis
    key_indicators TEXT,                 -- JSON array of sentiment indicators

    -- Urgency analysis
    urgency_analysis TEXT,               -- JSON blob with urgency data
    urgency_score REAL,                  -- 0.0 to 1.0 urgency score
    time_sensitivity TEXT,               -- critical, high, medium, normal
    action_required BOOLEAN DEFAULT 0,   -- Whether immediate action needed

    -- Content categorization
    news_category TEXT,                  -- breaking, sports, finance, etc.
    content_type TEXT,                   -- news, analysis, opinion, etc.
    authority_score REAL,                -- Source authority (0.0-1.0)

    -- Processing metadata
    processing_timestamp TEXT,
    enhancement_source TEXT DEFAULT 'news_intelligence',
    telegram_emoji TEXT,                 -- Emoji for Telegram alerts

    UNIQUE(url, query)                   -- Prevent duplicate articles per query
);

-- Swagbucks offers with stack intelligence
CREATE TABLE IF NOT EXISTS swagbucks_offers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT,
    offer_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    url TEXT NOT NULL,
    offer_url TEXT,                      -- Direct offer URL

    -- Offer details
    cashback_amount REAL,                -- Cashback amount
    cashback_type TEXT,                  -- percentage, fixed, points
    retailer TEXT,                       -- Retailer/merchant name
    category TEXT,                       -- Shopping category

    -- Stack intelligence
    detected_stack TEXT,                 -- betting, travel, cannabis, finance, fleet
    confidence_score REAL,               -- Confidence in stack detection
    offer_quality TEXT,                  -- JSON blob with quality analysis
    overall_score REAL,                  -- Overall offer quality (0.0-1.0)

    -- Stack-specific metadata
    stack_metadata TEXT,                 -- JSON blob with stack-specific data
    relevance_factors TEXT,              -- JSON array of relevance factors

    -- Temporal data
    expires_at TEXT,                     -- Offer expiration
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Processing metadata
    enhancement_source TEXT DEFAULT 'swagbucks_intelligence',
    processing_timestamp TEXT,

    UNIQUE(offer_id, url)               -- Prevent duplicate offers
);

-- Autosuggest and query expansions with intelligence
CREATE TABLE IF NOT EXISTS autosuggest_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    base_query TEXT NOT NULL,
    suggestion TEXT NOT NULL,

    -- Source information
    suggestion_source TEXT,              -- bing, google, stack_expansion
    detected_stack TEXT,                 -- betting, travel, cannabis, finance, fleet
    confidence_score REAL,               -- Confidence in stack detection

    -- Quality metrics
    quality_metrics TEXT,                -- JSON blob with quality analysis
    overall_quality REAL,                -- Overall quality score (0.0-1.0)
    relevance_score REAL,               -- Relevance to base query (0.0-1.0)

    -- SEO and search intent
    seo_potential TEXT,                  -- JSON blob with SEO analysis
    search_intent TEXT,                  -- informational, transactional, local, commercial, navigational
    long_tail_score REAL,               -- Long-tail keyword score (0.0-1.0)

    -- Usage and performance
    times_suggested INTEGER DEFAULT 1,   -- How many times this suggestion appeared
    click_through_rate REAL,            -- CTR if tracked
    conversion_rate REAL,               -- Conversion rate if tracked

    -- Processing metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    enhancement_source TEXT DEFAULT 'autosuggest_intelligence',

    UNIQUE(base_query, suggestion)       -- Prevent duplicate suggestions per base query
);

-- SEO keywords and intent analysis
CREATE TABLE IF NOT EXISTS seo_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    base_query TEXT NOT NULL,
    keyword TEXT NOT NULL,
    intent_type TEXT NOT NULL,           -- informational, transactional, local, commercial

    -- Keyword metrics
    search_volume INTEGER,               -- Estimated search volume
    competition_level REAL,              -- Competition score (0.0-1.0)
    keyword_difficulty REAL,            -- SEO difficulty (0.0-1.0)

    -- Stack alignment
    detected_stack TEXT,
    stack_relevance REAL,               -- How relevant to detected stack (0.0-1.0)

    -- Performance tracking
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    times_generated INTEGER DEFAULT 1,
    success_rate REAL,                  -- Success rate if tracked

    UNIQUE(base_query, keyword, intent_type)
);

-- Cross-system integration tracking
CREATE TABLE IF NOT EXISTS integration_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,            -- search, automation, alert, etc.
    source_system TEXT NOT NULL,        -- news_intelligence, swagbucks_intelligence, etc.
    target_system TEXT,                 -- telegram, automation_bridge, etc.

    -- Event data
    query TEXT,
    detected_stack TEXT,
    confidence_score REAL,

    -- Event metadata
    event_data TEXT,                     -- JSON blob with event details
    result_count INTEGER,
    success BOOLEAN DEFAULT 1,
    error_message TEXT,

    -- Timing
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_time_ms INTEGER,

    -- Analytics
    user_session TEXT,
    correlation_id TEXT                  -- For tracking related events
);

-- Query tracking and analytics
CREATE TABLE IF NOT EXISTS query_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    query_hash TEXT,                      -- MD5 hash of query for grouping
    stack_detected TEXT,                  -- Detected stack
    stack_confidence REAL,               -- Confidence in stack detection
    intelligence_used BOOLEAN DEFAULT 0, -- Whether intelligence was used

    -- Query metadata
    query_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_agent TEXT,                     -- If tracking different clients
    session_id TEXT,                     -- Session tracking

    -- Results summary
    total_results INTEGER DEFAULT 0,     -- Total results returned
    meta_bing_results INTEGER DEFAULT 0, -- Results from meta Bing
    google_results INTEGER DEFAULT 0,    -- Results from Google
    intelligence_results INTEGER DEFAULT 0, -- Results from intelligence modules

    -- Performance metrics
    total_processing_time_ms INTEGER,    -- Total processing time
    cache_hits INTEGER DEFAULT 0,       -- Number of cache hits
    api_calls_total INTEGER DEFAULT 0,  -- Total API calls made

    -- Quality metrics
    avg_relevance_score REAL,           -- Average relevance of results
    avg_sentiment_score REAL,           -- Average sentiment
    high_confidence_results INTEGER DEFAULT 0, -- Number of high-confidence results

    -- Success indicators
    telegram_sent BOOLEAN DEFAULT 0,    -- Whether Telegram alert was sent
    user_clicked_results INTEGER DEFAULT 0, -- Number of clicked results (if tracked)
    query_satisfied BOOLEAN,            -- User satisfaction (if tracked)

    -- Error tracking
    errors_encountered TEXT,            -- JSON array of any errors
    fallback_used BOOLEAN DEFAULT 0    -- Whether fallback to basic search was used
);

-- Stack-specific analysis cache
CREATE TABLE IF NOT EXISTS stack_analysis_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_hash TEXT NOT NULL,
    stack TEXT NOT NULL,
    analysis_results TEXT,              -- JSON blob with analysis
    confidence_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,               -- Cache expiration
    cache_hits INTEGER DEFAULT 0,      -- Usage tracking

    UNIQUE(query_hash, stack)
);

-- Performance monitoring
CREATE TABLE IF NOT EXISTS performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,          -- e.g., "api_response_time", "cache_hit_rate"
    metric_value REAL,
    stack TEXT,                         -- Which stack this metric applies to
    source TEXT,                        -- Which component generated this metric
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT                       -- JSON blob for additional context
);

-- User feedback and learning data (for future ML improvements)
CREATE TABLE IF NOT EXISTS user_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    result_url TEXT,
    feedback_type TEXT,                 -- "relevant", "irrelevant", "helpful", "spam"
    feedback_score INTEGER,             -- 1-5 rating
    detected_stack TEXT,
    actual_stack TEXT,                  -- Corrected stack if detection was wrong
    feedback_text TEXT,                 -- Free-form feedback
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_results_query ON results(query);
CREATE INDEX IF NOT EXISTS idx_results_source ON results(source);

CREATE INDEX IF NOT EXISTS idx_results_enhanced_query ON results_enhanced(query);
CREATE INDEX IF NOT EXISTS idx_results_enhanced_stack ON results_enhanced(detected_stack);
CREATE INDEX IF NOT EXISTS idx_results_enhanced_source ON results_enhanced(source);
CREATE INDEX IF NOT EXISTS idx_results_enhanced_fetched ON results_enhanced(fetched_at);
CREATE INDEX IF NOT EXISTS idx_results_enhanced_confidence ON results_enhanced(confidence_score);

CREATE INDEX IF NOT EXISTS idx_query_analytics_timestamp ON query_analytics(query_timestamp);
CREATE INDEX IF NOT EXISTS idx_query_analytics_stack ON query_analytics(stack_detected);
CREATE INDEX IF NOT EXISTS idx_query_analytics_hash ON query_analytics(query_hash);

CREATE INDEX IF NOT EXISTS idx_stack_cache_hash_stack ON stack_analysis_cache(query_hash, stack);
CREATE INDEX IF NOT EXISTS idx_stack_cache_expires ON stack_analysis_cache(expires_at);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_name ON performance_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_stack ON performance_metrics(stack);

-- News articles indexes
CREATE INDEX IF NOT EXISTS idx_news_query ON news_articles(query);
CREATE INDEX IF NOT EXISTS idx_news_stack ON news_articles(detected_stack);
CREATE INDEX IF NOT EXISTS idx_news_fetched ON news_articles(fetched_at);
CREATE INDEX IF NOT EXISTS idx_news_urgency ON news_articles(urgency_score);
CREATE INDEX IF NOT EXISTS idx_news_sentiment ON news_articles(sentiment_score);
CREATE INDEX IF NOT EXISTS idx_news_published ON news_articles(published_at);
CREATE INDEX IF NOT EXISTS idx_news_source ON news_articles(source);

-- Swagbucks offers indexes
CREATE INDEX IF NOT EXISTS idx_offers_query ON swagbucks_offers(query);
CREATE INDEX IF NOT EXISTS idx_offers_stack ON swagbucks_offers(detected_stack);
CREATE INDEX IF NOT EXISTS idx_offers_retailer ON swagbucks_offers(retailer);
CREATE INDEX IF NOT EXISTS idx_offers_expires ON swagbucks_offers(expires_at);
CREATE INDEX IF NOT EXISTS idx_offers_scraped ON swagbucks_offers(scraped_at);
CREATE INDEX IF NOT EXISTS idx_offers_quality ON swagbucks_offers(overall_score);

-- Autosuggest data indexes
CREATE INDEX IF NOT EXISTS idx_autosuggest_base ON autosuggest_data(base_query);
CREATE INDEX IF NOT EXISTS idx_autosuggest_stack ON autosuggest_data(detected_stack);
CREATE INDEX IF NOT EXISTS idx_autosuggest_quality ON autosuggest_data(overall_quality);
CREATE INDEX IF NOT EXISTS idx_autosuggest_intent ON autosuggest_data(search_intent);
CREATE INDEX IF NOT EXISTS idx_autosuggest_created ON autosuggest_data(created_at);

-- SEO keywords indexes
CREATE INDEX IF NOT EXISTS idx_seo_base_query ON seo_keywords(base_query);
CREATE INDEX IF NOT EXISTS idx_seo_intent ON seo_keywords(intent_type);
CREATE INDEX IF NOT EXISTS idx_seo_stack ON seo_keywords(detected_stack);
CREATE INDEX IF NOT EXISTS idx_seo_generated ON seo_keywords(generated_at);

-- Integration events indexes
CREATE INDEX IF NOT EXISTS idx_integration_type ON integration_events(event_type);
CREATE INDEX IF NOT EXISTS idx_integration_source ON integration_events(source_system);
CREATE INDEX IF NOT EXISTS idx_integration_timestamp ON integration_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_integration_stack ON integration_events(detected_stack);
CREATE INDEX IF NOT EXISTS idx_integration_correlation ON integration_events(correlation_id);
"""


@contextmanager
def get_conn(db_path: str | None = None):
    """Get database connection with optional custom path"""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


def init_enhanced_db(db_path: str | None = None):
    """Initialize enhanced database with full schema"""
    with get_conn(db_path) as conn:
        conn.executescript(ENHANCED_SCHEMA)
        logger.info(f"Enhanced database initialized at {db_path or DB_PATH}")


def migrate_from_legacy(legacy_path: str | None = None, enhanced_path: str | None = None):
    """Migrate data from legacy database to enhanced database"""
    legacy_db = legacy_path or LEGACY_DB_PATH
    enhanced_db = enhanced_path or DB_PATH

    if not os.path.exists(legacy_db):
        logger.info("No legacy database found, skipping migration")
        return

    logger.info(f"Migrating data from {legacy_db} to {enhanced_db}")

    # Initialize enhanced database
    init_enhanced_db(enhanced_db)

    # Copy data from legacy to enhanced
    with get_conn(legacy_db) as legacy_conn:
        legacy_cursor = legacy_conn.cursor()
        legacy_cursor.execute("SELECT * FROM results")
        legacy_data = legacy_cursor.fetchall()

        # Get column names
        legacy_columns = [description[0] for description in legacy_cursor.description]

    with get_conn(enhanced_db) as enhanced_conn:
        for row in legacy_data:
            row_dict = dict(zip(legacy_columns, row, strict=False))

            # Insert into both original results table (for backward compatibility)
            # and enhanced table
            enhanced_conn.execute(
                "INSERT OR IGNORE INTO results (query, title, url, snippet, source, published_at, fetched_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    row_dict.get("query"),
                    row_dict.get("title"),
                    row_dict.get("url"),
                    row_dict.get("snippet"),
                    row_dict.get("source"),
                    row_dict.get("published_at"),
                    row_dict.get("fetched_at"),
                ),
            )

            enhanced_conn.execute(
                "INSERT OR IGNORE INTO results_enhanced (query, title, url, snippet, source, published_at, fetched_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    row_dict.get("query"),
                    row_dict.get("title"),
                    row_dict.get("url"),
                    row_dict.get("snippet"),
                    row_dict.get("source"),
                    row_dict.get("published_at"),
                    row_dict.get("fetched_at"),
                ),
            )

    logger.info(f"Migration completed: {len(legacy_data)} records migrated")


def upsert_enhanced_results(
    query: str,
    results: list[dict[str, Any]],
    intelligence_data: dict[str, Any] | None = None,
) -> int:
    """
    Upsert results with enhanced intelligence metadata

    Args:
        query: Search query
        results: List of result dictionaries
        intelligence_data: Optional intelligence analysis data

    Returns:
        Number of records inserted/updated
    """
    if not results:
        return 0

    count = 0
    with get_conn() as conn:
        for result in results:
            try:
                # Extract basic result data
                title = result.get("title", "")
                url = result.get("url", "")
                snippet = result.get("snippet", "")
                source = result.get("source", "")
                published_at = result.get("published_at")

                # Extract enhanced data
                detected_stack = result.get("detected_stack") or (
                    intelligence_data.get("detected_stack") if intelligence_data else None
                )
                confidence_score = result.get("confidence_score", 0.0)
                intelligence_used = result.get("intelligence_used", False)
                enhancement_source = result.get("enhancement_source") or (
                    intelligence_data.get("enhancement_source") if intelligence_data else None
                )

                # JSON fields
                metadata = (
                    json.dumps(result.get("metadata", {})) if result.get("metadata") else None
                )
                analysis_results = (
                    json.dumps(result.get("analysis", {})) if result.get("analysis") else None
                )
                keywords_matched = (
                    json.dumps(result.get("keywords_matched", []))
                    if result.get("keywords_matched")
                    else None
                )
                tags = json.dumps(result.get("tags", [])) if result.get("tags") else None

                # Scores
                sentiment_score = result.get("sentiment_score")
                relevance_score = result.get("relevance_score", 0.0)

                # Categories
                primary_category = result.get("primary_category")
                secondary_category = result.get("secondary_category")
                content_type = result.get("content_type")
                language_detected = result.get("language_detected", "en")

                # Performance metrics
                processing_time_ms = result.get("processing_time_ms", 0)
                api_calls_used = result.get("api_calls_used", 1)

                # Insert into backward-compatible table
                conn.execute(
                    "INSERT OR IGNORE INTO results (query, title, url, snippet, source, published_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (query, title, url, snippet, source, published_at),
                )

                # Insert into enhanced table
                conn.execute(
                    """INSERT OR REPLACE INTO results_enhanced
                    (query, title, url, snippet, source, published_at,
                     detected_stack, confidence_score, intelligence_used, enhancement_source,
                     metadata, analysis_results, keywords_matched, sentiment_score, relevance_score,
                     primary_category, secondary_category, tags, content_type, language_detected,
                     processing_time_ms, api_calls_used)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        query,
                        title,
                        url,
                        snippet,
                        source,
                        published_at,
                        detected_stack,
                        confidence_score,
                        intelligence_used,
                        enhancement_source,
                        metadata,
                        analysis_results,
                        keywords_matched,
                        sentiment_score,
                        relevance_score,
                        primary_category,
                        secondary_category,
                        tags,
                        content_type,
                        language_detected,
                        processing_time_ms,
                        api_calls_used,
                    ),
                )
                count += 1

            except Exception as e:
                logger.error(f"Failed to upsert result {result.get('url', 'unknown')}: {e}")

    return count


def record_query_analytics(
    query: str, intelligence_data: dict[str, Any], results_summary: dict[str, Any]
) -> None:
    """Record query analytics and performance metrics"""
    import hashlib

    query_hash = hashlib.md5(query.encode()).hexdigest()

    with get_conn() as conn:
        conn.execute(
            """INSERT INTO query_analytics
            (query, query_hash, stack_detected, stack_confidence, intelligence_used,
             total_results, meta_bing_results, google_results, intelligence_results,
             total_processing_time_ms, api_calls_total, avg_relevance_score, avg_sentiment_score,
             telegram_sent, errors_encountered, fallback_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                query,
                query_hash,
                intelligence_data.get("detected_stack"),
                intelligence_data.get("stack_confidence", 0.0),
                intelligence_data.get("intelligence_used", False),
                results_summary.get("total_results", 0),
                results_summary.get("meta_bing_results", 0),
                results_summary.get("google_results", 0),
                results_summary.get("intelligence_results", 0),
                results_summary.get("total_processing_time_ms", 0),
                results_summary.get("api_calls_total", 0),
                results_summary.get("avg_relevance_score"),
                results_summary.get("avg_sentiment_score"),
                results_summary.get("telegram_sent", False),
                json.dumps(results_summary.get("errors", [])),
                results_summary.get("fallback_used", False),
            ),
        )


def cache_stack_analysis(
    query: str,
    stack: str,
    analysis: dict[str, Any],
    confidence: float,
    expires_hours: int = 24,
) -> None:
    """Cache stack analysis results for performance"""
    import hashlib
    from datetime import timedelta

    query_hash = hashlib.md5(query.encode()).hexdigest()
    expires_at = datetime.now(UTC) + timedelta(hours=expires_hours)

    with get_conn() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO stack_analysis_cache
            (query_hash, stack, analysis_results, confidence_score, expires_at)
            VALUES (?, ?, ?, ?, ?)""",
            (
                query_hash,
                stack,
                json.dumps(analysis),
                confidence,
                expires_at.isoformat(),
            ),
        )


def get_cached_analysis(query: str, stack: str) -> dict[str, Any] | None:
    """Retrieve cached stack analysis if available and not expired"""
    import hashlib

    query_hash = hashlib.md5(query.encode()).hexdigest()

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT analysis_results, confidence_score FROM stack_analysis_cache
            WHERE query_hash = ? AND stack = ? AND expires_at > datetime('now')""",
            (query_hash, stack),
        )
        result = cursor.fetchone()

        if result:
            # Update cache hit counter
            conn.execute(
                "UPDATE stack_analysis_cache SET cache_hits = cache_hits + 1 WHERE query_hash = ? AND stack = ?",
                (query_hash, stack),
            )

            return {"analysis": json.loads(result[0]), "confidence_score": result[1]}

    return None


def record_performance_metric(
    metric_name: str,
    value: float,
    stack: str | None = None,
    source: str | None = None,
    metadata: dict | None = None,
):
    """Record performance metrics for monitoring"""
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO performance_metrics (metric_name, metric_value, stack, source, metadata) VALUES (?, ?, ?, ?, ?)",
            (
                metric_name,
                value,
                stack,
                source,
                json.dumps(metadata) if metadata else None,
            ),
        )


def get_enhanced_results_by_query(
    query: str, limit: int = 20, stack_filter: str | None = None
) -> list[dict]:
    """Get enhanced results with full metadata"""
    with get_conn() as conn:
        cursor = conn.cursor()

        sql = """SELECT * FROM results_enhanced WHERE query = ?"""
        params = [query]

        if stack_filter:
            sql += " AND detected_stack = ?"
            params.append(stack_filter)

        sql += " ORDER BY fetched_at DESC, confidence_score DESC LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        columns = [description[0] for description in cursor.description]

        results = []
        for row in cursor.fetchall():
            result = dict(zip(columns, row, strict=False))

            # Parse JSON fields
            for json_field in [
                "metadata",
                "analysis_results",
                "keywords_matched",
                "tags",
            ]:
                if result.get(json_field):
                    try:
                        result[json_field] = json.loads(result[json_field])
                    except json.JSONDecodeError:
                        result[json_field] = {}

            results.append(result)

        return results


def get_query_analytics_summary(hours: int = 24) -> dict[str, Any]:
    """Get analytics summary for the past N hours"""
    with get_conn() as conn:
        cursor = conn.cursor()

        # Query analytics for the past N hours
        cursor.execute(
            f"""SELECT
                COUNT(*) as total_queries,
                COUNT(DISTINCT query) as unique_queries,
                AVG(total_results) as avg_results_per_query,
                AVG(total_processing_time_ms) as avg_processing_time,
                SUM(CASE WHEN intelligence_used = 1 THEN 1 ELSE 0 END) as intelligence_queries,
                SUM(CASE WHEN telegram_sent = 1 THEN 1 ELSE 0 END) as telegram_alerts,
                SUM(api_calls_total) as total_api_calls,
                AVG(avg_relevance_score) as overall_avg_relevance,
                COUNT(DISTINCT stack_detected) as unique_stacks_detected
            FROM query_analytics
            WHERE query_timestamp > datetime('now', '-{hours} hours')"""
        )

        summary = dict(zip([d[0] for d in cursor.description], cursor.fetchone(), strict=False))

        # Stack breakdown
        cursor.execute(
            f"""SELECT stack_detected, COUNT(*) as count, AVG(stack_confidence) as avg_confidence
            FROM query_analytics
            WHERE query_timestamp > datetime('now', '-{hours} hours') AND stack_detected IS NOT NULL
            GROUP BY stack_detected
            ORDER BY count DESC"""
        )

        summary["stack_breakdown"] = [
            dict(zip([d[0] for d in cursor.description], row, strict=False))
            for row in cursor.fetchall()
        ]

        return summary


# Backward compatibility functions
def upsert_results(query: str, rows: list[dict]) -> int:
    """Backward compatible upsert function - routes to enhanced version"""
    return upsert_enhanced_results(query, rows)


def latest_by_query(query: str, limit: int = 20) -> list[dict]:
    """Backward compatible function - returns basic format from enhanced table"""
    enhanced_results = get_enhanced_results_by_query(query, limit)

    # Convert to original format for backward compatibility
    basic_results = []
    for result in enhanced_results:
        basic_results.append(
            {
                "title": result.get("title"),
                "url": result.get("url"),
                "snippet": result.get("snippet"),
                "source": result.get("source"),
                "published_at": result.get("published_at"),
                "fetched_at": result.get("fetched_at"),
            }
        )

    return basic_results


def init_db(db_path: str | None = None):
    """Backward compatible init function"""
    init_enhanced_db(db_path)

    # Also migrate legacy data if it exists
    migrate_from_legacy()


# Cleanup and maintenance functions
def cleanup_expired_cache():
    """Remove expired cache entries"""
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM stack_analysis_cache WHERE expires_at < datetime('now')")
        deleted = cursor.rowcount
        logger.info(f"Cleaned up {deleted} expired cache entries")
        return deleted


# New functions for enhanced intelligence data


def upsert_news_articles(articles: list[dict[str, Any]]) -> int:
    """Store news articles with intelligence analysis"""
    count = 0

    with get_conn() as conn:
        for article in articles:
            try:
                # Extract fields with defaults
                query = article.get("query", "")
                title = article.get("title", "")
                url = article.get("url", "")
                snippet = article.get("snippet", "")
                content = article.get("content", "")
                source = article.get("source", "")
                published_at = article.get("published_at", "")

                # Intelligence fields
                detected_stack = article.get("detected_stack")
                confidence_score = article.get("confidence_score", 0.0)

                # Sentiment analysis
                sentiment_analysis = json.dumps(article.get("sentiment_analysis", {}))
                overall_sentiment = article.get("sentiment_analysis", {}).get(
                    "overall_sentiment", "neutral"
                )
                sentiment_score = article.get("sentiment_score", 0.0)
                sentiment_confidence = article.get("sentiment_analysis", {}).get("confidence", 0.5)
                key_indicators = json.dumps(
                    article.get("sentiment_analysis", {}).get("key_indicators", [])
                )

                # Urgency analysis
                urgency_analysis = json.dumps(article.get("urgency_analysis", {}))
                urgency_score = article.get("urgency_score", 0.0)
                time_sensitivity = article.get("time_sensitivity", "normal")
                action_required = article.get("action_required", False)

                # Content fields
                news_category = article.get("news_category", "")
                content_type = article.get("content_type", "news")
                authority_score = article.get("authority_score", 0.5)

                # Metadata
                processing_timestamp = article.get(
                    "processing_timestamp", datetime.now(UTC).isoformat()
                )
                enhancement_source = article.get("enhancement_source", "news_intelligence")
                telegram_emoji = article.get("telegram_emoji", "📰")

                # Insert into database
                conn.execute(
                    """INSERT OR REPLACE INTO news_articles
                    (query, title, url, snippet, content, source, published_at,
                     detected_stack, confidence_score, sentiment_analysis, overall_sentiment,
                     sentiment_score, sentiment_confidence, key_indicators, urgency_analysis,
                     urgency_score, time_sensitivity, action_required, news_category,
                     content_type, authority_score, processing_timestamp, enhancement_source, telegram_emoji)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        query,
                        title,
                        url,
                        snippet,
                        content,
                        source,
                        published_at,
                        detected_stack,
                        confidence_score,
                        sentiment_analysis,
                        overall_sentiment,
                        sentiment_score,
                        sentiment_confidence,
                        key_indicators,
                        urgency_analysis,
                        urgency_score,
                        time_sensitivity,
                        action_required,
                        news_category,
                        content_type,
                        authority_score,
                        processing_timestamp,
                        enhancement_source,
                        telegram_emoji,
                    ),
                )
                count += 1

            except Exception as e:
                logger.error(f"Failed to upsert news article {article.get('url', 'unknown')}: {e}")

    return count


def get_news_by_stack(stack: str, hours: int = 24, limit: int = 20) -> list[dict[str, Any]]:
    """Get recent news articles for a specific stack"""
    cutoff_time = datetime.now(UTC) - timedelta(hours=hours)

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM news_articles
            WHERE detected_stack = ? AND fetched_at >= ?
            ORDER BY urgency_score DESC, sentiment_score DESC, fetched_at DESC
            LIMIT ?""",
            (stack, cutoff_time.isoformat(), limit),
        )

        results = []
        for row in cursor.fetchall():
            # Convert row to dictionary
            columns = [desc[0] for desc in cursor.description]
            result = dict(zip(columns, row, strict=False))

            # Parse JSON fields
            try:
                result["sentiment_analysis"] = json.loads(result["sentiment_analysis"])
                result["urgency_analysis"] = json.loads(result["urgency_analysis"])
                result["key_indicators"] = json.loads(result["key_indicators"])
            except (json.JSONDecodeError, TypeError):
                pass

            results.append(result)

        return results


def upsert_swagbucks_offers(offers: list[dict[str, Any]]) -> int:
    """Store Swagbucks offers with intelligence analysis"""
    count = 0

    with get_conn() as conn:
        for offer in offers:
            try:
                # Extract fields with defaults
                query = offer.get("query", "")
                offer_id = offer.get("offer_id", "")
                title = offer.get("title", "")
                description = offer.get("description", "")
                url = offer.get("url", "")
                offer_url = offer.get("offer_url", "")

                # Offer details
                cashback_amount = offer.get("cashback_amount", 0.0)
                cashback_type = offer.get("cashback_type", "")
                retailer = offer.get("retailer", "")
                category = offer.get("category", "")

                # Intelligence fields
                detected_stack = offer.get("detected_stack")
                confidence_score = offer.get("confidence_score", 0.0)
                offer_quality = json.dumps(offer.get("offer_quality", {}))
                overall_score = offer.get("offer_quality", {}).get("overall_score", 0.0)

                # Stack metadata
                stack_metadata = json.dumps(offer.get("stack_metadata", {}))
                relevance_factors = json.dumps(offer.get("relevance_factors", []))

                # Temporal data
                expires_at = offer.get("expires_at", "")

                # Processing metadata
                enhancement_source = offer.get("enhancement_source", "swagbucks_intelligence")
                processing_timestamp = offer.get(
                    "processing_timestamp", datetime.now(UTC).isoformat()
                )

                # Insert into database
                conn.execute(
                    """INSERT OR REPLACE INTO swagbucks_offers
                    (query, offer_id, title, description, url, offer_url, cashback_amount,
                     cashback_type, retailer, category, detected_stack, confidence_score,
                     offer_quality, overall_score, stack_metadata, relevance_factors,
                     expires_at, enhancement_source, processing_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        query,
                        offer_id,
                        title,
                        description,
                        url,
                        offer_url,
                        cashback_amount,
                        cashback_type,
                        retailer,
                        category,
                        detected_stack,
                        confidence_score,
                        offer_quality,
                        overall_score,
                        stack_metadata,
                        relevance_factors,
                        expires_at,
                        enhancement_source,
                        processing_timestamp,
                    ),
                )
                count += 1

            except Exception as e:
                logger.error(f"Failed to upsert offer {offer.get('offer_id', 'unknown')}: {e}")

    return count


def get_offers_by_stack(stack: str, limit: int = 20) -> list[dict[str, Any]]:
    """Get Swagbucks offers for a specific stack"""
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM swagbucks_offers
            WHERE detected_stack = ? AND (expires_at = '' OR expires_at > datetime('now'))
            ORDER BY overall_score DESC, confidence_score DESC, scraped_at DESC
            LIMIT ?""",
            (stack, limit),
        )

        results = []
        for row in cursor.fetchall():
            # Convert row to dictionary
            columns = [desc[0] for desc in cursor.description]
            result = dict(zip(columns, row, strict=False))

            # Parse JSON fields
            try:
                result["offer_quality"] = json.loads(result["offer_quality"])
                result["stack_metadata"] = json.loads(result["stack_metadata"])
                result["relevance_factors"] = json.loads(result["relevance_factors"])
            except (json.JSONDecodeError, TypeError):
                pass

            results.append(result)

        return results


def upsert_autosuggest_data(suggestions: list[dict[str, Any]]) -> int:
    """Store autosuggest data with intelligence analysis"""
    count = 0

    with get_conn() as conn:
        for suggestion in suggestions:
            try:
                # Extract fields
                base_query = suggestion.get("base_query", "")
                suggestion_text = suggestion.get("suggestion", "")
                suggestion_source = suggestion.get("suggestion_source", "unknown")
                detected_stack = suggestion.get("detected_stack")
                confidence_score = suggestion.get("confidence_score", 0.0)

                # Quality metrics
                quality_metrics = json.dumps(suggestion.get("quality_metrics", {}))
                overall_quality = suggestion.get("quality_metrics", {}).get("overall_quality", 0.0)
                relevance_score = suggestion.get("relevance_score", 0.0)

                # SEO and intent
                seo_potential = json.dumps(suggestion.get("seo_potential", {}))
                search_intent = suggestion.get("search_intent", "navigational")
                long_tail_score = suggestion.get("long_tail_score", 0.0)

                # Processing metadata
                enhancement_source = suggestion.get(
                    "enhancement_source", "autosuggest_intelligence"
                )

                # Insert into database
                conn.execute(
                    """INSERT OR REPLACE INTO autosuggest_data
                    (base_query, suggestion, suggestion_source, detected_stack, confidence_score,
                     quality_metrics, overall_quality, relevance_score, seo_potential,
                     search_intent, long_tail_score, enhancement_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(base_query, suggestion) DO UPDATE SET
                    times_suggested = times_suggested + 1,
                    last_seen_at = CURRENT_TIMESTAMP""",
                    (
                        base_query,
                        suggestion_text,
                        suggestion_source,
                        detected_stack,
                        confidence_score,
                        quality_metrics,
                        overall_quality,
                        relevance_score,
                        seo_potential,
                        search_intent,
                        long_tail_score,
                        enhancement_source,
                    ),
                )
                count += 1

            except Exception as e:
                logger.error(
                    f"Failed to upsert suggestion '{suggestion.get('suggestion', 'unknown')}': {e}"
                )

    return count


def get_suggestions_by_query(base_query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Get autosuggest data for a base query"""
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM autosuggest_data
            WHERE base_query = ?
            ORDER BY overall_quality DESC, times_suggested DESC, created_at DESC
            LIMIT ?""",
            (base_query, limit),
        )

        results = []
        for row in cursor.fetchall():
            # Convert row to dictionary
            columns = [desc[0] for desc in cursor.description]
            result = dict(zip(columns, row, strict=False))

            # Parse JSON fields
            try:
                result["quality_metrics"] = json.loads(result["quality_metrics"])
                result["seo_potential"] = json.loads(result["seo_potential"])
            except (json.JSONDecodeError, TypeError):
                pass

            results.append(result)

        return results


def upsert_seo_keywords(keywords: list[dict[str, Any]]) -> int:
    """Store SEO keywords and intent analysis"""
    count = 0

    with get_conn() as conn:
        for keyword_data in keywords:
            try:
                # Extract fields
                base_query = keyword_data.get("base_query", "")
                keyword = keyword_data.get("keyword", "")
                intent_type = keyword_data.get("intent_type", "informational")

                # Metrics
                search_volume = keyword_data.get("search_volume", 0)
                competition_level = keyword_data.get("competition_level", 0.5)
                keyword_difficulty = keyword_data.get("keyword_difficulty", 0.5)

                # Stack alignment
                detected_stack = keyword_data.get("detected_stack")
                stack_relevance = keyword_data.get("stack_relevance", 0.5)

                # Insert into database
                conn.execute(
                    """INSERT OR REPLACE INTO seo_keywords
                    (base_query, keyword, intent_type, search_volume, competition_level,
                     keyword_difficulty, detected_stack, stack_relevance)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(base_query, keyword, intent_type) DO UPDATE SET
                    times_generated = times_generated + 1""",
                    (
                        base_query,
                        keyword,
                        intent_type,
                        search_volume,
                        competition_level,
                        keyword_difficulty,
                        detected_stack,
                        stack_relevance,
                    ),
                )
                count += 1

            except Exception as e:
                logger.error(
                    f"Failed to upsert SEO keyword '{keyword_data.get('keyword', 'unknown')}': {e}"
                )

    return count


def record_integration_event(
    event_type: str,
    source_system: str,
    query: str | None = None,
    detected_stack: str | None = None,
    event_data: dict[str, Any] | None = None,
    target_system: str | None = None,
    success: bool = True,
    error_message: str | None = None,
    processing_time_ms: int | None = None,
    correlation_id: str | None = None,
) -> None:
    """Record integration events for analytics"""
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO integration_events
            (event_type, source_system, target_system, query, detected_stack,
             confidence_score, event_data, result_count, success, error_message,
             processing_time_ms, correlation_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                event_type,
                source_system,
                target_system,
                query,
                detected_stack,
                event_data.get("confidence_score", 0.0) if event_data else 0.0,
                json.dumps(event_data or {}),
                event_data.get("result_count", 0) if event_data else 0,
                success,
                error_message,
                processing_time_ms,
                correlation_id,
            ),
        )


# Convenience function to create all tables
def create_tables(db_path: str | None = None):
    """Create all enhanced database tables"""
    init_enhanced_db(db_path)
    logger.info("All enhanced database tables created successfully")


def cleanup_old_analytics(days: int = 90):
    """Remove analytics older than N days"""
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"DELETE FROM query_analytics WHERE query_timestamp < datetime('now', '-{days} days')"
        )
        cursor.execute(
            f"DELETE FROM performance_metrics WHERE timestamp < datetime('now', '-{days} days')"
        )
        deleted = cursor.rowcount
        logger.info(f"Cleaned up analytics older than {days} days: {deleted} records")
        return deleted


if __name__ == "__main__":
    # Initialize and test the enhanced database
    logging.basicConfig(level=logging.INFO)

    print("🗄️ Initializing Enhanced EQ12 Meta-Search Database...")
    init_enhanced_db()

    print("📊 Database schema ready with enhanced intelligence support!")
    print("\nFeatures available:")
    print("✅ Backward compatibility with original meta-search")
    print("✅ Enhanced results with intelligence metadata")
    print("✅ Query analytics and performance tracking")
    print("✅ Stack-specific analysis caching")
    print("✅ User feedback collection")
    print("✅ Performance monitoring")

    # Run cleanup
    cleanup_expired_cache()

    print("\n📈 Getting analytics summary...")
    summary = get_query_analytics_summary(24)
    print(f"Total queries (24h): {summary.get('total_queries', 0)}")
    print(f"Intelligence queries: {summary.get('intelligence_queries', 0)}")
    print(f"Unique stacks detected: {summary.get('unique_stacks_detected', 0)}")
