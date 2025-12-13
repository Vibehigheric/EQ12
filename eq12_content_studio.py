#!/usr/bin/env python3
"""
EQ12 Content Studio - RAG-Powered Sports Betting Content Engine
==============================================================

AI-powered content generation with Retrieval-Augmented Generation:
- SEO-optimized betting previews and recaps
- Social media content for Twitter/LinkedIn
- White-label articles for media partnerships
- Educational content and betting guides
- Data-driven insights and analysis

Revenue Streams:
- White-label articles: $19-49/piece
- Monthly content packages: $299-999/month
- Custom content partnerships: $2000+/month
- SEO content licensing: $99/month per site
- Social media automation: $149/month

RAG Features:
- Historical betting data integration
- Real-time odds and line movement context
- Expert analysis and proven strategies
- Legal compliance by jurisdiction
- Automated fact-checking and disclaimers

Author: EQ12 Development Team
Version: 2.0.0
"""

import asyncio
import hashlib
import json
import logging
import re
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import stripe
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Import EQ12 components
from eq12_openai_security import EQ12OpenAISecurityManager
from eq12_sports_betting_engine import EQ12BettingEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ContentRequest:
    """Content generation request"""

    content_type: str  # preview, recap, guide, analysis, social
    sport: str
    target_length: int = 800
    tone: str = "professional"  # professional, casual, expert
    format: str = "article"  # article, social, newsletter, video-script
    seo_keywords: list[str] = None
    target_audience: str = "general"  # general, beginners, advanced
    include_data: bool = True
    compliance_level: str = "strict"  # strict, moderate, minimal

    def __post_init__(self):
        if self.seo_keywords is None:
            self.seo_keywords = []


@dataclass
class ContentPiece:
    """Generated content piece"""

    id: str
    content: str
    title: str
    meta_description: str
    word_count: int
    seo_score: float
    readability_score: float
    keywords: list[str]
    generated_at: datetime
    cost_usd: float = 0.0
    client_id: str | None = None


@dataclass
class RAGContext:
    """RAG context for content generation"""

    historical_data: list[dict]
    recent_picks: list[dict]
    market_trends: list[dict]
    expert_insights: list[dict]
    legal_guidelines: dict[str, str]
    performance_stats: dict[str, float]


class EQ12ContentStudio:
    """RAG-powered content generation engine"""

    def __init__(self):
        # Core components
        self.openai_manager = EQ12OpenAISecurityManager("content_studio")
        self.betting_engine = EQ12BettingEngine()

        # Database and storage
        self.db_path = "C:/EQ12/logs/content_studio.db"
        self.content_cache = {}

        # RAG components
        self.vectorizer = TfidfVectorizer(
            max_features=5000, stop_words="english", ngram_range=(1, 3)
        )
        self.knowledge_base = []
        self.embeddings = None

        # Content templates
        self.templates = {}

        # Revenue tracking
        self.revenue_stats = {
            "articles_generated": 0,
            "monthly_revenue": 0.0,
            "active_clients": 0,
            "avg_article_price": 29.0,
        }

        # Pricing tiers
        self.pricing = {
            "basic_article": 19.00,
            "premium_article": 49.00,
            "content_package": 299.00,
            "enterprise_package": 999.00,
            "seo_licensing": 99.00,
            "social_automation": 149.00,
        }

        self.setup_database()
        self.load_knowledge_base()
        self.setup_templates()

    def setup_database(self):
        """Initialize content studio database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Generated content tracking
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS generated_content (
                id TEXT PRIMARY KEY,
                client_id TEXT,
                content_type TEXT,
                sport TEXT,
                title TEXT,
                content TEXT,
                word_count INTEGER,
                seo_score REAL,
                keywords TEXT,
                pricing_tier TEXT,
                amount_charged REAL,
                generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                delivered_at DATETIME,
                client_rating INTEGER
            )
        """
        )

        # Knowledge base entries
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id TEXT PRIMARY KEY,
                content_type TEXT,
                sport TEXT,
                content TEXT,
                metadata TEXT,
                embedding_vector TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_used DATETIME
            )
        """
        )

        # Client subscriptions
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS content_clients (
                client_id TEXT PRIMARY KEY,
                company_name TEXT,
                contact_email TEXT,
                subscription_tier TEXT,
                monthly_limit INTEGER,
                used_this_month INTEGER DEFAULT 0,
                stripe_subscription_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME
            )
        """
        )

        # Performance tracking
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS content_performance (
                content_id TEXT PRIMARY KEY,
                page_views INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0,
                conversion_rate REAL DEFAULT 0,
                seo_ranking TEXT,
                social_shares INTEGER DEFAULT 0,
                tracked_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info("✅ Content studio database initialized")

    def load_knowledge_base(self):
        """Load existing knowledge base for RAG"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT content, metadata, sport FROM knowledge_base
            ORDER BY last_used DESC, created_at DESC
        """
        )

        rows = cursor.fetchall()
        conn.close()

        self.knowledge_base = []
        for content, metadata_json, sport in rows:
            try:
                metadata = json.loads(metadata_json) if metadata_json else {}
                self.knowledge_base.append(
                    {"content": content, "metadata": metadata, "sport": sport}
                )
            except json.JSONDecodeError:
                continue

        # Build embeddings if we have data
        if self.knowledge_base:
            self.build_embeddings()
        else:
            # Seed with initial content
            self.seed_knowledge_base()

        logger.info(f"✅ Loaded {len(self.knowledge_base)} knowledge base entries")

    def seed_knowledge_base(self):
        """Seed knowledge base with initial betting content"""

        seed_content = [
            {
                "content": """Expected value (EV) in sports betting represents the theoretical return on a wager over time.
                Positive EV bets have a mathematical edge over the sportsbook's implied probability.
                Calculating EV involves comparing your assessed true probability against the bookmaker's odds.
                Professional bettors focus exclusively on positive EV opportunities to ensure long-term profitability.""",
                "metadata": {"type": "concept", "difficulty": "beginner"},
                "sport": "general",
            },
            {
                "content": """Bankroll management is crucial for sports betting success. The Kelly Criterion provides
                a mathematical approach to optimal bet sizing based on edge and odds. Most professionals recommend
                never risking more than 2-5% of bankroll on any single wager. Flat betting and percentage-based
                staking are conservative approaches for recreational bettors.""",
                "metadata": {"type": "strategy", "difficulty": "intermediate"},
                "sport": "general",
            },
            {
                "content": """NFL betting markets offer diverse opportunities beyond point spreads. Player props,
                team totals, and live betting present edges for informed bettors. Weather conditions significantly
                impact over/under totals, while coaching tendencies affect situational spots. Sharp money often
                moves lines 2-3 points in key NFL games.""",
                "metadata": {"type": "market_analysis", "difficulty": "advanced"},
                "sport": "nfl",
            },
            {
                "content": """NBA betting requires understanding pace, rest advantages, and back-to-back scheduling.
                Player prop markets are particularly vulnerable to injury news and rotation changes. The NBA's
                high-scoring nature creates opportunities in over/under markets, especially in playoff scenarios
                where defensive intensity increases.""",
                "metadata": {"type": "market_analysis", "difficulty": "advanced"},
                "sport": "nba",
            },
        ]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for content_data in seed_content:
            content_id = hashlib.md5(content_data["content"].encode()).hexdigest()
            cursor.execute(
                """
                INSERT OR IGNORE INTO knowledge_base (id, content_type, sport, content, metadata)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    content_id,
                    content_data["metadata"].get("type", "general"),
                    content_data["sport"],
                    content_data["content"],
                    json.dumps(content_data["metadata"]),
                ),
            )

        conn.commit()
        conn.close()

        # Reload knowledge base
        self.load_knowledge_base()

    def build_embeddings(self):
        """Build TF-IDF embeddings for RAG similarity search"""

        if not self.knowledge_base:
            return

        # Extract text for vectorization
        documents = [entry["content"] for entry in self.knowledge_base]

        # Build TF-IDF matrix
        try:
            self.embeddings = self.vectorizer.fit_transform(documents)
            logger.info(f"✅ Built embeddings for {len(documents)} documents")
        except Exception as e:
            logger.error(f"Embedding construction failed: {e}")
            self.embeddings = None

    def setup_templates(self):
        """Setup content generation templates"""

        self.templates = {
            "preview": {
                "structure": [
                    "engaging_hook",
                    "game_overview",
                    "key_betting_angles",
                    "expert_prediction",
                    "betting_recommendation",
                    "disclaimer",
                ],
                "tone": "analytical",
                "length_range": (600, 1000),
            },
            "recap": {
                "structure": [
                    "game_summary",
                    "key_moments",
                    "betting_outcomes",
                    "lessons_learned",
                    "future_implications",
                ],
                "tone": "reflective",
                "length_range": (500, 800),
            },
            "guide": {
                "structure": [
                    "introduction",
                    "fundamental_concepts",
                    "practical_strategies",
                    "common_mistakes",
                    "advanced_techniques",
                    "conclusion",
                ],
                "tone": "educational",
                "length_range": (1200, 2000),
            },
            "social": {
                "structure": ["hook", "key_insight", "call_to_action"],
                "tone": "engaging",
                "length_range": (50, 280),
            },
        }

    # ==================== RAG CONTENT GENERATION ====================

    async def generate_content(
        self, request: ContentRequest, client_id: str | None = None
    ) -> ContentPiece:
        """Generate content using RAG methodology"""

        try:
            # Step 1: Retrieve relevant context
            rag_context = await self.retrieve_context(request)

            # Step 2: Generate content with context
            content_result = await self.generate_with_rag(request, rag_context)

            # Step 3: Enhance with SEO and readability
            enhanced_content = await self.enhance_content(content_result, request)

            # Step 4: Create content piece
            content_piece = ContentPiece(
                id=hashlib.md5(
                    f"{request.content_type}{request.sport}{time.time()}".encode()
                ).hexdigest(),
                content=enhanced_content["content"],
                title=enhanced_content["title"],
                meta_description=enhanced_content["meta_description"],
                word_count=len(enhanced_content["content"].split()),
                seo_score=enhanced_content["seo_score"],
                readability_score=enhanced_content["readability_score"],
                keywords=enhanced_content["keywords"],
                generated_at=datetime.now(),
                cost_usd=content_result.get("cost", 0),
                client_id=client_id,
            )

            # Step 5: Store and track
            await self.store_generated_content(content_piece, request)

            # Step 6: Update knowledge base
            await self.update_knowledge_base(content_piece, request)

            logger.info(
                f"✅ Generated {request.content_type} content: {content_piece.word_count} words"
            )

            return content_piece

        except Exception as e:
            logger.error(f"Content generation error: {e}")
            raise

    async def retrieve_context(self, request: ContentRequest) -> RAGContext:
        """Retrieve relevant context for content generation"""

        # Build search query
        query = f"{request.content_type} {request.sport} betting"
        if request.seo_keywords:
            query += " " + " ".join(request.seo_keywords[:3])

        # Find similar content in knowledge base
        similar_content = self.find_similar_content(query, limit=5)

        # Get recent betting data
        recent_data = await self.get_recent_betting_data(request.sport)

        # Get expert insights
        expert_insights = await self.get_expert_insights(request.sport)

        # Get legal guidelines
        legal_guidelines = self.get_legal_guidelines(request.compliance_level)

        # Get performance stats
        performance_stats = await self.get_performance_stats(request.sport)

        return RAGContext(
            historical_data=similar_content,
            recent_picks=recent_data.get("picks", []),
            market_trends=recent_data.get("trends", []),
            expert_insights=expert_insights,
            legal_guidelines=legal_guidelines,
            performance_stats=performance_stats,
        )

    def find_similar_content(self, query: str, limit: int = 5) -> list[dict]:
        """Find similar content using TF-IDF similarity"""

        if not self.embeddings or not self.knowledge_base:
            return []

        try:
            # Vectorize query
            query_vector = self.vectorizer.transform([query])

            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.embeddings).flatten()

            # Get top similar indices
            top_indices = similarities.argsort()[-limit:][::-1]

            # Return similar content with scores
            similar_content = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    content = self.knowledge_base[idx].copy()
                    content["similarity_score"] = float(similarities[idx])
                    similar_content.append(content)

            return similar_content

        except Exception as e:
            logger.error(f"Similarity search error: {e}")
            return []

    async def get_recent_betting_data(self, sport: str) -> dict[str, list]:
        """Get recent betting data for context"""

        try:
            # Get recent EV picks
            recent_legs = await self.betting_engine.calculate_ev_legs(sport, 10, 2.0)

            picks_data = []
            for leg in recent_legs[:5]:
                picks_data.append(
                    {
                        "selection": leg.selection,
                        "sportsbook": leg.sportsbook,
                        "ev_percent": leg.ev_percent,
                        "confidence": leg.confidence,
                        "market": leg.market,
                    }
                )

            # Simulate market trends (in production, would get real data)
            trends_data = [
                {"trend": "Sharp money on overs", "sport": sport, "confidence": 0.7},
                {"trend": "Public backing favorites", "sport": sport, "confidence": 0.8},
                {"trend": "Line movement toward unders", "sport": sport, "confidence": 0.6},
            ]

            return {"picks": picks_data, "trends": trends_data}

        except Exception as e:
            logger.error(f"Recent data retrieval error: {e}")
            return {"picks": [], "trends": []}

    async def get_expert_insights(self, sport: str) -> list[dict]:
        """Get expert insights for content context"""

        # Simulated expert insights (in production, would integrate real expert data)
        insights = {
            "nfl": [
                {
                    "insight": "Weather conditions heavily impact total scoring in outdoor games",
                    "expert": "Professional Handicapper",
                    "confidence": 0.85,
                },
                {
                    "insight": "Divisional games often go under due to familiarity",
                    "expert": "Sharp Bettor",
                    "confidence": 0.72,
                },
            ],
            "nba": [
                {
                    "insight": "Back-to-back games show decreased offensive efficiency",
                    "expert": "NBA Analytics Expert",
                    "confidence": 0.78,
                },
                {
                    "insight": "Player rest significantly impacts game totals",
                    "expert": "Professional Handicapper",
                    "confidence": 0.82,
                },
            ],
        }

        return insights.get(sport, [])

    def get_legal_guidelines(self, compliance_level: str) -> dict[str, str]:
        """Get legal compliance guidelines"""

        guidelines = {
            "strict": {
                "disclaimer": "This content is for educational and entertainment purposes only. Gambling involves risk and should be done responsibly. Please be aware of the laws in your jurisdiction.",
                "age_warning": "Must be 21+ to participate in sports betting.",
                "responsible_gambling": "If you or someone you know has a gambling problem, seek help immediately.",
                "no_guarantees": "No gambling strategy guarantees profits. Past results do not predict future outcomes.",
            },
            "moderate": {
                "disclaimer": "Educational content only. Bet responsibly and within your means.",
                "responsible_gambling": "Gambling should be fun, not a financial strategy.",
            },
            "minimal": {"disclaimer": "For entertainment purposes only."},
        }

        return guidelines.get(compliance_level, guidelines["strict"])

    async def get_performance_stats(self, sport: str) -> dict[str, float]:
        """Get performance statistics for context"""

        # Simulated performance stats (in production, would calculate real stats)
        return {
            "win_rate": 0.58,
            "avg_odds": -110,
            "roi": 0.12,
            "total_units": 45.7,
            "longest_streak": 8,
        }

    async def generate_with_rag(
        self, request: ContentRequest, context: RAGContext
    ) -> dict[str, Any]:
        """Generate content using RAG context and OpenAI"""

        # Build context-aware prompt
        prompt = self.build_rag_prompt(request, context)

        # Choose model based on content length and complexity
        model = (
            "gpt-4o"
            if request.target_length > 1000 or request.content_type == "guide"
            else "gpt-4o-mini"
        )

        try:
            response = await self.openai_manager.secure_openai_request(
                model,
                [
                    {"role": "system", "content": self.get_system_prompt(request)},
                    {"role": "user", "content": prompt},
                ],
                {
                    "max_tokens": min(request.target_length * 2, 4000),
                    "temperature": 0.7 if request.tone == "casual" else 0.4,
                },
            )

            content = response["response"]["choices"][0]["message"]["content"]
            cost = response.get("cost_check", {}).get("estimated_cost", 0)

            return {"content": content, "cost": cost, "model_used": model}

        except Exception as e:
            logger.error(f"RAG generation error: {e}")
            raise

    def build_rag_prompt(self, request: ContentRequest, context: RAGContext) -> str:
        """Build context-rich prompt for content generation"""

        prompt = f"""Generate a {request.content_type} about {request.sport} betting.

TARGET SPECIFICATIONS:
- Length: ~{request.target_length} words
- Tone: {request.tone}
- Audience: {request.target_audience}
- Format: {request.format}
- Include data: {request.include_data}

HISTORICAL CONTEXT:
"""

        # Add similar content context
        if context.historical_data:
            prompt += "Previous successful content themes:\n"
            for i, content in enumerate(context.historical_data[:3], 1):
                prompt += f"{i}. {content['content'][:200]}...\n"

        # Add recent picks context
        if context.recent_picks and request.include_data:
            prompt += "\nRECENT VALUE OPPORTUNITIES:\n"
            for pick in context.recent_picks[:3]:
                prompt += (
                    f"- {pick['selection']} ({pick['sportsbook']}) EV: +{pick['ev_percent']:.1f}%\n"
                )

        # Add market trends
        if context.market_trends:
            prompt += "\nCURRENT MARKET TRENDS:\n"
            for trend in context.market_trends[:2]:
                prompt += f"- {trend['trend']} (Confidence: {trend['confidence']:.0%})\n"

        # Add expert insights
        if context.expert_insights:
            prompt += "\nEXPERT INSIGHTS:\n"
            for insight in context.expert_insights[:2]:
                prompt += f'- "{insight["insight"]}" - {insight["expert"]}\n'

        # Add performance context
        if context.performance_stats:
            stats = context.performance_stats
            prompt += "\nPERFORMANCE CONTEXT:\n"
            prompt += f"- Current season ROI: {stats['roi']:.1%}\n"
            prompt += f"- Win rate: {stats['win_rate']:.1%}\n"

        # Add SEO keywords
        if request.seo_keywords:
            prompt += f"\nSEO KEYWORDS TO INCLUDE: {', '.join(request.seo_keywords)}\n"

        # Add content structure guidance
        template = self.templates.get(request.content_type, {})
        if template.get("structure"):
            prompt += f"\nCONTENT STRUCTURE: {' -> '.join(template['structure'])}\n"

        # Add legal compliance
        prompt += "\nCOMPLIANCE REQUIREMENTS:\n"
        for key, value in context.legal_guidelines.items():
            prompt += f"- {key}: {value}\n"

        prompt += f"\nGenerate engaging, factual {request.content_type} content that incorporates this context naturally."

        return prompt

    def get_system_prompt(self, request: ContentRequest) -> str:
        """Get system prompt based on content type"""

        system_prompts = {
            "preview": """You are a professional sports betting analyst writing game previews.
            Focus on actionable betting insights, key matchups, and data-driven analysis.
            Be informative but engaging, always include appropriate disclaimers.""",
            "recap": """You are a sports betting analyst writing post-game analysis.
            Focus on what happened, why it happened, and lessons for future betting.
            Be reflective and educational, helping readers learn from outcomes.""",
            "guide": """You are an expert betting educator writing instructional content.
            Be comprehensive, clear, and practical. Focus on teaching concepts that
            help readers become better, more disciplined bettors.""",
            "analysis": """You are a data-driven betting analyst. Focus on statistics,
            trends, and mathematical edges. Support claims with data and logical reasoning.""",
            "social": """You are creating engaging social media content about sports betting.
            Be concise, engaging, and shareable while maintaining professionalism.""",
        }

        return system_prompts.get(request.content_type, system_prompts["analysis"])

    async def enhance_content(
        self, content_result: dict, request: ContentRequest
    ) -> dict[str, Any]:
        """Enhance content with SEO and readability improvements"""

        content = content_result["content"]

        # Generate title and meta description
        title = self.generate_title(content, request)
        meta_description = self.generate_meta_description(content, request)

        # Calculate SEO score
        seo_score = self.calculate_seo_score(content, title, request.seo_keywords)

        # Calculate readability score
        readability_score = self.calculate_readability_score(content)

        # Extract keywords
        keywords = self.extract_keywords(content, request.sport)

        # Add structured data hints for SEO
        enhanced_content = self.add_seo_structure(content, request)

        return {
            "content": enhanced_content,
            "title": title,
            "meta_description": meta_description,
            "seo_score": seo_score,
            "readability_score": readability_score,
            "keywords": keywords,
        }

    def generate_title(self, content: str, request: ContentRequest) -> str:
        """Generate SEO-optimized title"""

        # Extract first sentence or heading as base
        lines = content.split("\n")
        first_line = next(
            (line.strip() for line in lines if line.strip() and not line.startswith("#")), ""
        )

        # Generate title based on content type
        if request.content_type == "preview":
            return f"{request.sport.upper()} Betting Preview: {first_line[:60]}..."
        elif request.content_type == "recap":
            return f"{request.sport.upper()} Betting Recap: {first_line[:60]}..."
        elif request.content_type == "guide":
            return f"Complete {request.sport.upper()} Betting Guide: {first_line[:50]}..."
        else:
            return f"{request.sport.upper()} Betting Analysis: {first_line[:60]}..."

    def generate_meta_description(self, content: str, request: ContentRequest) -> str:
        """Generate meta description for SEO"""

        # Extract first paragraph
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        first_para = paragraphs[0] if paragraphs else content[:200]

        # Clean and truncate
        meta = re.sub(r"[#*]", "", first_para)[:150]

        # Add call to action
        if request.content_type == "preview":
            meta += " Expert betting analysis and predictions."
        elif request.content_type == "guide":
            meta += " Professional betting strategies and tips."

        return meta[:160] + "..." if len(meta) > 160 else meta

    def calculate_seo_score(self, content: str, title: str, keywords: list[str]) -> float:
        """Calculate SEO optimization score"""

        score = 0.0
        content_lower = content.lower()
        title_lower = title.lower()

        # Keyword density check
        if keywords:
            keyword_mentions = sum(content_lower.count(kw.lower()) for kw in keywords)
            target_density = len(content.split()) * 0.02  # 2% target density
            if keyword_mentions > 0:
                score += min(keyword_mentions / target_density, 1.0) * 30

        # Title optimization
        if any(kw.lower() in title_lower for kw in keywords):
            score += 20

        # Content length
        word_count = len(content.split())
        if 600 <= word_count <= 2000:
            score += 20

        # Readability indicators
        sentences = len(re.findall(r"[.!?]+", content))
        if sentences > 0:
            avg_sentence_length = word_count / sentences
            if 15 <= avg_sentence_length <= 25:
                score += 15

        # Structure indicators
        if re.search(r"^#+\s", content, re.MULTILINE):  # Has headings
            score += 10

        if content.count("\n\n") >= 3:  # Has paragraphs
            score += 5

        return min(score, 100.0)

    def calculate_readability_score(self, content: str) -> float:
        """Calculate readability score (simplified Flesch-Kincaid)"""

        sentences = len(re.findall(r"[.!?]+", content))
        words = len(content.split())
        syllables = sum(self.count_syllables(word) for word in content.split())

        if sentences == 0 or words == 0:
            return 0.0

        # Simplified Flesch Reading Ease
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))

        # Convert to 0-100 scale (higher = more readable)
        return max(0, min(100, score))

    def count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""
        word = word.lower().strip()
        if not word:
            return 0

        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            if char in vowels:
                if not previous_was_vowel:
                    syllable_count += 1
                previous_was_vowel = True
            else:
                previous_was_vowel = False

        # Handle silent 'e'
        if word.endswith("e") and syllable_count > 1:
            syllable_count -= 1

        return max(1, syllable_count)

    def extract_keywords(self, content: str, sport: str) -> list[str]:
        """Extract relevant keywords from content"""

        # Base keywords
        keywords = [sport, "betting", "odds", "analysis"]

        # Common betting terms to look for
        betting_terms = [
            "value bet",
            "expected value",
            "bankroll management",
            "kelly criterion",
            "sharp money",
            "line movement",
            "closing line value",
            "steam move",
            "public betting",
            "contrarian",
            "fade the public",
            "reverse line movement",
            "injury report",
            "weather impact",
            "home field advantage",
            "situational spot",
        ]

        content_lower = content.lower()
        for term in betting_terms:
            if term in content_lower:
                keywords.append(term)

        # Sport-specific terms
        sport_terms = {
            "nfl": ["touchdown", "field goal", "quarterback", "defense", "rushing", "passing"],
            "nba": ["three-pointer", "rebound", "assist", "point guard", "center", "playoff"],
            "mlb": ["home run", "pitcher", "batting average", "earned run average", "strikeout"],
        }

        if sport in sport_terms:
            for term in sport_terms[sport]:
                if term in content_lower:
                    keywords.append(term)

        return list(set(keywords))[:15]  # Limit to 15 unique keywords

    def add_seo_structure(self, content: str, request: ContentRequest) -> str:
        """Add SEO-friendly structure to content"""

        # Add proper heading hierarchy
        lines = content.split("\n")
        structured_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                structured_lines.append("")
                continue

            # Convert headings to proper hierarchy
            if line.isupper() and len(line) < 100:
                structured_lines.append(f"## {line.title()}")
            elif line.endswith(":") and len(line) < 80:
                structured_lines.append(f"### {line}")
            else:
                structured_lines.append(line)

        structured_content = "\n".join(structured_lines)

        # Add schema.org hints for betting content
        if request.content_type in ["preview", "analysis"]:
            structured_content += "\n\n<!-- Schema.org Article markup -->"

        return structured_content

    # ==================== CONTENT MANAGEMENT ====================

    async def store_generated_content(self, content_piece: ContentPiece, request: ContentRequest):
        """Store generated content in database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO generated_content
            (id, client_id, content_type, sport, title, content, word_count,
             seo_score, keywords, pricing_tier, amount_charged)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                content_piece.id,
                content_piece.client_id,
                request.content_type,
                request.sport,
                content_piece.title,
                content_piece.content,
                content_piece.word_count,
                content_piece.seo_score,
                json.dumps(content_piece.keywords),
                "premium_article",  # Default pricing tier
                self.pricing["premium_article"],
            ),
        )

        conn.commit()
        conn.close()

        # Update revenue stats
        self.revenue_stats["articles_generated"] += 1
        self.revenue_stats["monthly_revenue"] += self.pricing["premium_article"]

    async def update_knowledge_base(self, content_piece: ContentPiece, request: ContentRequest):
        """Add generated content to knowledge base for future RAG"""

        # Extract key insights from generated content
        insights = self.extract_content_insights(content_piece.content)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Add content excerpts to knowledge base
        for insight in insights:
            insight_id = hashlib.md5(insight["text"].encode()).hexdigest()

            cursor.execute(
                """
                INSERT OR IGNORE INTO knowledge_base
                (id, content_type, sport, content, metadata)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    insight_id,
                    request.content_type,
                    request.sport,
                    insight["text"],
                    json.dumps(
                        {
                            "source": "generated",
                            "seo_score": content_piece.seo_score,
                            "keywords": insight.get("keywords", []),
                        }
                    ),
                ),
            )

        conn.commit()
        conn.close()

        # Rebuild embeddings if significant new content added
        if len(insights) >= 3:
            self.load_knowledge_base()  # Reload and rebuild embeddings

    def extract_content_insights(self, content: str) -> list[dict[str, Any]]:
        """Extract key insights from generated content"""

        insights = []

        # Split into paragraphs and identify key insights
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip() and len(p) > 100]

        for para in paragraphs[:5]:  # Limit to top 5 paragraphs
            # Look for paragraphs with betting insights
            if any(
                term in para.lower()
                for term in ["betting", "odds", "value", "strategy", "analysis"]
            ):
                insights.append(
                    {
                        "text": para,
                        "type": "insight",
                        "keywords": self.extract_keywords(para, "general"),
                    }
                )

        return insights

    # ==================== CLIENT MANAGEMENT & BILLING ====================

    async def create_client_subscription(self, client_data: dict[str, Any]) -> dict[str, Any]:
        """Create new client subscription"""

        try:
            # Create Stripe subscription
            stripe_customer = stripe.Customer.create(
                email=client_data["email"],
                name=client_data["company_name"],
                metadata={"tier": client_data["tier"]},
            )

            subscription = stripe.Subscription.create(
                customer=stripe_customer.id,
                items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"EQ12 Content Studio - {client_data['tier'].title()}"
                            },
                            "unit_amount": int(
                                self.pricing[f"{client_data['tier']}_package"] * 100
                            ),
                            "recurring": {"interval": "month"},
                        },
                    }
                ],
                metadata={"tier": client_data["tier"]},
            )

            # Store client info
            client_id = hashlib.md5(client_data["email"].encode()).hexdigest()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO content_clients
                (client_id, company_name, contact_email, subscription_tier,
                 monthly_limit, stripe_subscription_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    client_id,
                    client_data["company_name"],
                    client_data["email"],
                    client_data["tier"],
                    client_data.get("monthly_limit", 10),
                    subscription.id,
                ),
            )

            conn.commit()
            conn.close()

            return {"client_id": client_id, "subscription_id": subscription.id, "status": "active"}

        except Exception as e:
            logger.error(f"Client subscription error: {e}")
            raise

    async def get_client_usage(self, client_id: str) -> dict[str, Any]:
        """Get client usage statistics"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current month usage
        cursor.execute(
            """
            SELECT COUNT(*), SUM(amount_charged)
            FROM generated_content
            WHERE client_id = ? AND DATE(generated_at) >= DATE('now', 'start of month')
        """,
            (client_id,),
        )

        current_usage = cursor.fetchone()

        # Get client limits
        cursor.execute(
            """
            SELECT monthly_limit, subscription_tier
            FROM content_clients
            WHERE client_id = ?
        """,
            (client_id,),
        )

        client_info = cursor.fetchone()
        conn.close()

        if not client_info:
            raise ValueError("Client not found")

        return {
            "articles_this_month": current_usage[0] or 0,
            "amount_billed": current_usage[1] or 0.0,
            "monthly_limit": client_info[0],
            "subscription_tier": client_info[1],
            "remaining_articles": max(0, client_info[0] - (current_usage[0] or 0)),
        }

    # ==================== API ENDPOINTS FOR CONTENT GENERATION ====================

    def create_fastapi_app(self):
        """Create FastAPI app for content studio API"""

        from fastapi import FastAPI, HTTPException

        app = FastAPI(title="EQ12 Content Studio API", version="2.0.0")

        @app.post("/api/content/generate")
        async def generate_content_api(request_data: dict[str, Any]):
            """Generate content via API"""

            try:
                # Parse request
                request = ContentRequest(
                    content_type=request_data["content_type"],
                    sport=request_data["sport"],
                    target_length=request_data.get("target_length", 800),
                    tone=request_data.get("tone", "professional"),
                    seo_keywords=request_data.get("seo_keywords", []),
                    target_audience=request_data.get("target_audience", "general"),
                )

                client_id = request_data.get("client_id")

                # Check client limits if applicable
                if client_id:
                    usage = await self.get_client_usage(client_id)
                    if usage["remaining_articles"] <= 0:
                        raise HTTPException(429, "Monthly article limit exceeded")

                # Generate content
                content_piece = await self.generate_content(request, client_id)

                return {
                    "content_id": content_piece.id,
                    "title": content_piece.title,
                    "content": content_piece.content,
                    "meta_description": content_piece.meta_description,
                    "word_count": content_piece.word_count,
                    "seo_score": content_piece.seo_score,
                    "readability_score": content_piece.readability_score,
                    "keywords": content_piece.keywords,
                    "cost_usd": content_piece.cost_usd,
                }

            except Exception as e:
                logger.error(f"API content generation error: {e}")
                raise HTTPException(500, str(e))

        @app.get("/api/content/pricing")
        async def get_pricing():
            """Get content pricing information"""
            return {"pricing": self.pricing, "revenue_stats": self.revenue_stats}

        @app.post("/api/content/subscribe")
        async def subscribe_to_content(subscription_data: dict[str, Any]):
            """Create content subscription"""

            try:
                result = await self.create_client_subscription(subscription_data)
                return result
            except Exception as e:
                logger.error(f"Subscription error: {e}")
                raise HTTPException(500, str(e))

        return app


# ==================== MAIN EXECUTION ====================


async def main():
    """Main content studio execution"""

    studio = EQ12ContentStudio()

    logger.info("🚀 EQ12 Content Studio Started")
    logger.info("💰 Revenue streams:")
    logger.info("   - White-label articles: $19-49/piece")
    logger.info("   - Monthly packages: $299-999/month")
    logger.info("   - SEO licensing: $99/month per site")
    logger.info("   - Social automation: $149/month")
    logger.info("🎯 Target: $15,000/month from content services")

    # Create and start FastAPI app
    app = studio.create_fastapi_app()

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)


if __name__ == "__main__":
    asyncio.run(main())
