#!/usr/bin/env python3
"""
EQ12 OpenAI Status Monitor
Monitors OpenAI service status and integrates with EQ12 optimization workflows
"""

import asyncio
import json
import logging
import os
import sqlite3
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import requests

# Add EQ12 modules to path
sys.path.append(os.path.dirname(__file__))

logger = logging.getLogger(__name__)


@dataclass
class ServiceStatus:
    """OpenAI service status information"""

    service_name: str
    status: str  # operational, degraded_performance, partial_outage, major_outage
    description: str
    last_updated: str
    impact_level: str = "none"  # none, minor, major, critical
    affected_models: list[str] = field(default_factory=list)
    estimated_resolution: str | None = None


@dataclass
class StatusIncident:
    """OpenAI status incident information"""

    incident_id: str
    title: str
    status: str
    impact: str
    created_at: str
    updated_at: str
    resolved_at: str | None = None
    description: str = ""
    affected_services: list[str] = field(default_factory=list)
    updates: list[dict[str, str]] = field(default_factory=list)


class EQ12OpenAIStatusMonitor:
    """
    Monitor OpenAI service status and provide recommendations for EQ12 workflows
    """

    def __init__(self, db_path: str = "eq12_openai_status.db"):
        """Initialize the status monitor"""
        self.db_path = db_path
        self.rss_url = "https://status.openai.com/feed.rss"
        self.atom_url = "https://status.openai.com/feed.atom"
        self.api_base_url = "https://status.openai.com/api/v2"

        # OpenAI service mappings
        self.service_model_mapping = {
            "API": [
                "gpt-4.1-2025-04-14",
                "gpt-4.1-mini-2025-04-14",
                "gpt-4.1-nano-2025-04-14",
                "o4-mini-2025-04-16",
            ],
            "ChatGPT": ["gpt-4.1-2025-04-14"],
            "Playground": ["gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14"],
            "Fine-tuning": [
                "gpt-4.1-2025-04-14",
                "gpt-4.1-mini-2025-04-14",
                "gpt-4o-2024-08-06",
            ],
            "Embeddings": ["text-embedding-3-small", "text-embedding-3-large"],
            "DALL-E": ["dall-e-3", "dall-e-2"],
            "Whisper": ["whisper-1"],
            "TTS": ["tts-1", "tts-1-hd"],
        }

        # EQ12 optimization impact levels
        self.eq12_impact_mapping = {
            "API": "critical",  # Core EQ12 functionality depends on API
            "Fine-tuning": "major",  # Optimization workflows affected
            "ChatGPT": "minor",  # Development assistance only
            "Playground": "minor",  # Testing and development
            "Embeddings": "moderate",  # Search and similarity features
            "DALL-E": "low",  # Image generation features
            "Whisper": "low",  # Audio processing features
            "TTS": "low",  # Text-to-speech features
        }

        self._init_database()
        logger.info("EQ12 OpenAI Status Monitor initialized")

    def _init_database(self):
        """Initialize SQLite database for status tracking"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Service status table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS service_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                status TEXT NOT NULL,
                description TEXT,
                last_updated TEXT,
                impact_level TEXT,
                affected_models TEXT,
                estimated_resolution TEXT,
                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Incidents table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT UNIQUE,
                title TEXT,
                status TEXT,
                impact TEXT,
                created_at TEXT,
                updated_at TEXT,
                resolved_at TEXT,
                description TEXT,
                affected_services TEXT,
                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # EQ12 optimization recommendations table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS eq12_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                status TEXT,
                recommendation TEXT,
                priority TEXT,
                affected_use_cases TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT
            )
        """
        )

        conn.commit()
        conn.close()

    async def fetch_status_feed(self, feed_type: str = "rss") -> str | None:
        """
        Fetch OpenAI status feed

        Args:
            feed_type: "rss" or "atom"

        Returns:
            Raw feed content or None if failed
        """

        url = self.rss_url if feed_type == "rss" else self.atom_url

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            logger.info(f"Successfully fetched {feed_type.upper()} status feed")
            return response.text

        except requests.RequestException as e:
            logger.error(f"Failed to fetch {feed_type} status feed: {e}")
            return None

    def parse_rss_feed(self, rss_content: str) -> list[StatusIncident]:
        """
        Parse RSS feed content to extract incidents

        Args:
            rss_content: Raw RSS XML content

        Returns:
            List of parsed incidents
        """

        incidents = []

        try:
            root = ET.fromstring(rss_content)

            for item in root.findall(".//item"):
                title_elem = item.find("title")
                description_elem = item.find("description")
                pub_date_elem = item.find("pubDate")
                link_elem = item.find("link")

                if title_elem is not None and description_elem is not None:
                    # Extract incident ID from link if available
                    incident_id = ""
                    if link_elem is not None and "incidents" in link_elem.text:
                        incident_id = link_elem.text.split("/")[-1]

                    # Parse status and impact from title
                    title = title_elem.text
                    status = "investigating"
                    impact = "minor"

                    if "resolved" in title.lower():
                        status = "resolved"
                    elif "monitoring" in title.lower():
                        status = "monitoring"
                    elif "identified" in title.lower():
                        status = "identified"

                    if "major" in title.lower() or "outage" in title.lower():
                        impact = "major"
                    elif "critical" in title.lower():
                        impact = "critical"

                    pub_date = (
                        pub_date_elem.text
                        if pub_date_elem is not None
                        else datetime.utcnow().isoformat()
                    )

                    incident = StatusIncident(
                        incident_id=incident_id or f"rss_{hash(title)}",
                        title=title,
                        status=status,
                        impact=impact,
                        created_at=pub_date,
                        updated_at=pub_date,
                        description=description_elem.text,
                        affected_services=self._extract_affected_services(
                            title + " " + description_elem.text
                        ),
                    )

                    incidents.append(incident)

            logger.info(f"Parsed {len(incidents)} incidents from RSS feed")

        except ET.ParseError as e:
            logger.error(f"Failed to parse RSS feed: {e}")

        return incidents

    def _extract_affected_services(self, text: str) -> list[str]:
        """
        Extract affected services from incident text

        Args:
            text: Incident title and description

        Returns:
            List of affected service names
        """

        affected_services = []
        text_lower = text.lower()

        for service in self.service_model_mapping:
            if service.lower() in text_lower:
                affected_services.append(service)

        # Additional keyword matching
        if "api" in text_lower or "endpoint" in text_lower:
            affected_services.append("API")

        if "fine-tun" in text_lower or "training" in text_lower:
            affected_services.append("Fine-tuning")

        if "chatgpt" in text_lower or "chat gpt" in text_lower:
            affected_services.append("ChatGPT")

        return list(set(affected_services))  # Remove duplicates

    async def get_current_status(self) -> dict[str, ServiceStatus]:
        """
        Get current status of all OpenAI services

        Returns:
            Dictionary mapping service names to their current status
        """

        service_statuses = {}

        # Fetch and parse RSS feed
        rss_content = await self.fetch_status_feed("rss")
        if rss_content:
            incidents = self.parse_rss_feed(rss_content)

            # Initialize all services as operational
            for service in self.service_model_mapping:
                service_statuses[service] = ServiceStatus(
                    service_name=service,
                    status="operational",
                    description="No reported issues",
                    last_updated=datetime.utcnow().isoformat(),
                    impact_level="none",
                    affected_models=self.service_model_mapping[service],
                )

            # Update status based on recent incidents
            for incident in incidents:
                if incident.status != "resolved":
                    for service in incident.affected_services:
                        if service in service_statuses:
                            # Determine status level
                            if incident.impact == "critical":
                                status = "major_outage"
                            elif incident.impact == "major":
                                status = "partial_outage"
                            else:
                                status = "degraded_performance"

                            service_statuses[service].status = status
                            service_statuses[service].description = incident.title
                            service_statuses[service].last_updated = incident.updated_at
                            service_statuses[service].impact_level = incident.impact

            # Store in database
            self._store_service_statuses(service_statuses)

        return service_statuses

    def _store_service_statuses(self, statuses: dict[str, ServiceStatus]):
        """Store service statuses in database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for service_name, status in statuses.items():
            cursor.execute(
                """
                INSERT INTO service_status
                (service_name, status, description, last_updated, impact_level, affected_models)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    service_name,
                    status.status,
                    status.description,
                    status.last_updated,
                    status.impact_level,
                    json.dumps(status.affected_models),
                ),
            )

        conn.commit()
        conn.close()

    def generate_eq12_recommendations(
        self, statuses: dict[str, ServiceStatus]
    ) -> list[dict[str, Any]]:
        """
        Generate EQ12-specific recommendations based on OpenAI status

        Args:
            statuses: Current service statuses

        Returns:
            List of recommendations for EQ12 workflows
        """

        recommendations = []

        for service_name, status in statuses.items():
            if status.status != "operational":
                self.eq12_impact_mapping.get(service_name, "low")

                # API service recommendations
                if service_name == "API":
                    if status.status == "major_outage":
                        recommendations.append(
                            {
                                "service": service_name,
                                "priority": "critical",
                                "action": "pause_optimization_workflows",
                                "description": "Pause all EQ12 optimization workflows until API service is restored",
                                "affected_use_cases": ["all"],
                                "estimated_impact": "All AI-powered features unavailable",
                            }
                        )
                    elif (
                        status.status == "partial_outage" or status.status == "degraded_performance"
                    ):
                        recommendations.append(
                            {
                                "service": service_name,
                                "priority": "high",
                                "action": "enable_fallback_mode",
                                "description": "Enable fallback mode with cached responses and reduced API calls",
                                "affected_use_cases": [
                                    "betting_analysis",
                                    "cannabis_compliance",
                                    "credit_assessment",
                                ],
                                "estimated_impact": "Reduced AI functionality, slower response times",
                            }
                        )

                # Fine-tuning service recommendations
                elif service_name == "Fine-tuning":
                    if status.status in ["major_outage", "partial_outage"]:
                        recommendations.append(
                            {
                                "service": service_name,
                                "priority": "major",
                                "action": "postpone_fine_tuning",
                                "description": "Postpone fine-tuning jobs until service is restored",
                                "affected_use_cases": ["model_optimization"],
                                "estimated_impact": "Model optimization workflows delayed",
                            }
                        )

                # Model-specific recommendations
                affected_models = status.affected_models
                if affected_models:
                    recommendations.append(
                        {
                            "service": service_name,
                            "priority": "moderate",
                            "action": "switch_model_variants",
                            "description": f"Switch to alternative models if {', '.join(affected_models)} are affected",
                            "affected_use_cases": ["all"],
                            "estimated_impact": "Temporary use of backup models with potentially different performance",
                        }
                    )

        # Store recommendations in database
        self._store_recommendations(recommendations)

        return recommendations

    def _store_recommendations(self, recommendations: list[dict[str, Any]]):
        """Store recommendations in database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clear old recommendations (older than 24 hours)
        twenty_four_hours_ago = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        cursor.execute(
            "DELETE FROM eq12_recommendations WHERE created_at < ?",
            (twenty_four_hours_ago,),
        )

        # Insert new recommendations
        for rec in recommendations:
            cursor.execute(
                """
                INSERT INTO eq12_recommendations
                (service_name, status, recommendation, priority, affected_use_cases, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    rec["service"],
                    rec.get("status", "active"),
                    json.dumps(rec),
                    rec["priority"],
                    json.dumps(rec["affected_use_cases"]),
                    (datetime.utcnow() + timedelta(hours=12)).isoformat(),  # Expire after 12 hours
                ),
            )

        conn.commit()
        conn.close()

    async def check_model_availability(self, model_name: str) -> dict[str, Any]:
        """
        Check availability of specific OpenAI model

        Args:
            model_name: Name of the model to check

        Returns:
            Availability status and recommendations
        """

        statuses = await self.get_current_status()

        model_status = {
            "model": model_name,
            "available": True,
            "status": "operational",
            "affected_services": [],
            "recommendations": [],
        }

        # Check which services affect this model
        for service_name, service_models in self.service_model_mapping.items():
            if model_name in service_models:
                service_status = statuses.get(service_name)
                if service_status and service_status.status != "operational":
                    model_status["available"] = False
                    model_status["status"] = service_status.status
                    model_status["affected_services"].append(service_name)

        # Generate model-specific recommendations
        if not model_status["available"]:
            model_status["recommendations"].append(
                {
                    "action": "use_alternative_model",
                    "description": f"Consider using alternative models while {model_name} is affected",
                    "alternative_models": self._get_alternative_models(model_name),
                }
            )

        return model_status

    def _get_alternative_models(self, model_name: str) -> list[str]:
        """Get alternative models for a given model"""

        alternatives = {
            "gpt-4.1-2025-04-14": [
                "gpt-4.1-mini-2025-04-14",
                "gpt-4.1-nano-2025-04-14",
            ],
            "gpt-4.1-mini-2025-04-14": [
                "gpt-4.1-nano-2025-04-14",
                "gpt-4.1-2025-04-14",
            ],
            "gpt-4.1-nano-2025-04-14": ["gpt-4.1-mini-2025-04-14"],
            "o4-mini-2025-04-16": ["gpt-4.1-mini-2025-04-14"],
        }

        return alternatives.get(model_name, [])

    def get_status_summary(self) -> dict[str, Any]:
        """
        Get comprehensive status summary for EQ12 dashboard

        Returns:
            Status summary including all services and recommendations
        """

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get latest service statuses
        cursor.execute(
            """
            SELECT service_name, status, description, last_updated, impact_level
            FROM service_status
            WHERE recorded_at IN (
                SELECT MAX(recorded_at)
                FROM service_status
                GROUP BY service_name
            )
        """
        )

        service_data = cursor.fetchall()

        # Get active recommendations
        cursor.execute(
            """
            SELECT recommendation, priority, created_at
            FROM eq12_recommendations
            WHERE expires_at > ?
            ORDER BY
                CASE priority
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'major' THEN 3
                    WHEN 'moderate' THEN 4
                    ELSE 5
                END,
                created_at DESC
        """,
            (datetime.utcnow().isoformat(),),
        )

        recommendation_data = cursor.fetchall()

        conn.close()

        # Calculate overall health score
        operational_count = len([s for s in service_data if s[1] == "operational"])
        total_services = len(service_data)
        health_score = (operational_count / total_services * 100) if total_services > 0 else 100

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_health": health_score,
            "status": (
                "healthy"
                if health_score >= 90
                else "degraded" if health_score >= 70 else "unhealthy"
            ),
            "services": [
                {
                    "name": row[0],
                    "status": row[1],
                    "description": row[2],
                    "last_updated": row[3],
                    "impact_level": row[4],
                }
                for row in service_data
            ],
            "active_recommendations": [
                {
                    "recommendation": json.loads(row[0]),
                    "priority": row[1],
                    "created_at": row[2],
                }
                for row in recommendation_data
            ],
            "eq12_impact_assessment": self._assess_eq12_impact(service_data),
        }

    def _assess_eq12_impact(self, service_data: list[tuple]) -> dict[str, Any]:
        """Assess impact on EQ12 workflows"""

        impact_assessment = {
            "betting_analysis": "operational",
            "cannabis_compliance": "operational",
            "credit_assessment": "operational",
            "governance_automation": "operational",
            "code_generation": "operational",
            "model_optimization": "operational",
        }

        for service_name, status, _, _, _impact_level in service_data:
            if status != "operational":
                # Map service issues to EQ12 use cases
                if service_name == "API":
                    # API issues affect all use cases
                    for use_case in impact_assessment:
                        if status == "major_outage":
                            impact_assessment[use_case] = "unavailable"
                        elif impact_assessment[use_case] == "operational":
                            impact_assessment[use_case] = "degraded"

                elif service_name == "Fine-tuning":
                    # Fine-tuning issues affect optimization workflows
                    if impact_assessment["model_optimization"] == "operational":
                        impact_assessment["model_optimization"] = (
                            "degraded" if status == "degraded_performance" else "unavailable"
                        )

        return impact_assessment


# CLI interface
async def main():
    """Main CLI interface for OpenAI status monitoring"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 OpenAI Status Monitor")
    parser.add_argument(
        "--check-status",
        action="store_true",
        help="Check current OpenAI service status",
    )
    parser.add_argument("--check-model", help="Check availability of specific model")
    parser.add_argument("--summary", action="store_true", help="Get comprehensive status summary")
    parser.add_argument("--output", help="Output file for results")

    args = parser.parse_args()

    monitor = EQ12OpenAIStatusMonitor()

    if args.check_status:
        statuses = await monitor.get_current_status()
        recommendations = monitor.generate_eq12_recommendations(statuses)

        result = {
            "service_statuses": {
                name: {
                    "status": status.status,
                    "description": status.description,
                    "impact_level": status.impact_level,
                    "affected_models": status.affected_models,
                }
                for name, status in statuses.items()
            },
            "eq12_recommendations": recommendations,
        }

    elif args.check_model:
        result = await monitor.check_model_availability(args.check_model)

    elif args.summary:
        result = monitor.get_status_summary()

    else:
        # Default: check status
        statuses = await monitor.get_current_status()
        result = monitor.get_status_summary()

    # Output results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
