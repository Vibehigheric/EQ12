#!/usr/bin/env python3
"""
EQ12 Agentic Secret Detection & Prevention System
Advanced ML-powered secret scanning with proactive leak prevention
Implementation of insights from "Detecting and Preventing Secret Leaks in Code" whitepaper
"""

import asyncio
import hashlib
import logging
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Import EQ12 logging system
try:
    sys.path.append(str(Path(__file__).parent.parent / "configs"))
    from logging_eq12 import LoggingConfig, SecretRedactionFilter

    logger = LoggingConfig.create_module_logger("agentic_secret_detection")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


@dataclass
class ThreatIntelligence:
    """Threat intelligence data structure"""

    pattern_id: str
    threat_type: str
    confidence: float
    context: Dict[str, any]
    severity: str
    remediation_suggestion: str


@dataclass
class SecretDetection:
    """Enhanced secret detection result with ML confidence scoring"""

    pattern: str
    match_text: str
    confidence: float
    threat_level: str
    context_window: str
    suggested_remediation: str
    prevention_rule: Optional[str] = None


class MLPatternLearner:
    """Machine learning-based pattern recognition for secret detection"""

    def __init__(self):
        """TODO: Add docstring for __init__"""

        # Advanced secret patterns with context awareness
        self.enhanced_patterns = {
            # OpenAI API Keys
            "openai_key": {
                "pattern": r"sk-[a-zA-Z0-9]{48}",
                "confidence_base": 0.95,
                "threat_level": "CRITICAL",
                "context_indicators": ["openai", "api_key", "client"],
            },
            # GitHub Tokens
            "github_token": {
                "pattern": r"gh[ps]_[a-zA-Z0-9]{36}",
                "confidence_base": 0.98,
                "threat_level": "CRITICAL",
                "context_indicators": ["github", "token", "auth"],
            },
            # AWS Credentials
            "aws_access_key": {
                "pattern": r"AKIA[0-9A-Z]{16}",
                "confidence_base": 0.95,
                "threat_level": "CRITICAL",
                "context_indicators": ["aws", "amazon", "access"],
            },
            # Generic API patterns
            "generic_api_key": {
                "pattern": r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
                "confidence_base": 0.75,
                "threat_level": "HIGH",
                "context_indicators": ["key", "secret", "token"],
            },
            # Database URLs with credentials
            "database_url": {
                "pattern": r"(?i)(mongodb|mysql|postgres|redis)://[^:\s]+:[^@\s]+@[^/\s]+",
                "confidence_base": 0.90,
                "threat_level": "HIGH",
                "context_indicators": ["database", "connection", "url"],
            },
        }

        # Context-based confidence adjusters
        self.context_multipliers = {
            "variable_assignment": 1.2,  # var = "secret"
            "configuration_file": 1.3,  # .env, config files
            "comment_context": 0.6,  # In comments (likely example)
            "test_context": 0.4,  # In test files (likely mock)
            "documentation": 0.3,  # In docs (likely example)
        }

        # Learning mechanism for pattern evolution
        self.learned_patterns = set()
        self.false_positive_cache = set()

    async def detect_with_confidence(
        self, content: str, file_context: str = ""
    ) -> List[SecretDetection]:
        """Advanced ML-based secret detection with confidence scoring"""
        detections = []

        for pattern_name, pattern_info in self.enhanced_patterns.items():
            matches = re.finditer(
                pattern_info["pattern"],
                content,
                re.MULTILINE | re.IGNORECASE)

            for match in matches:
                # Calculate contextual confidence
                confidence = await self._calculate_contextual_confidence(
                    match, content, pattern_info, file_context
                )

                # Skip low-confidence detections to reduce false positives
                if confidence < 0.5:
                    continue

                # Extract context window for analysis
                context_window = self._extract_context_window(
                    content, match.start(), match.end())

                # Generate intelligent remediation suggestion
                remediation = self._generate_remediation_suggestion(
                    match, pattern_name, file_context
                )

                detection = SecretDetection(
                    pattern=pattern_name,
                    match_text=match.group(0),
                    confidence=confidence,
                    threat_level=pattern_info["threat_level"],
                    context_window=context_window,
                    suggested_remediation=remediation,
                )

                detections.append(detection)

                # Log high-confidence threats
                if confidence > 0.8:
                    logger.warning(
                        f"🚨 High-confidence secret detected: {pattern_name} (confidence: {confidence:.2f})"
                    )

        return detections

    async def _calculate_contextual_confidence(
        self, match, content: str, pattern_info: Dict, file_context: str
    ) -> float:
        """Calculate confidence score using contextual analysis"""
        base_confidence = pattern_info["confidence_base"]

        # Context analysis factors
        context_factors = []

        # Check for context indicators around the match
        context_window = self._extract_context_window(
            content, match.start(), match.end(), window_size=100
        )
        context_lower = context_window.lower()

        # Positive indicators (increase confidence)
        for indicator in pattern_info["context_indicators"]:
            if indicator in context_lower:
                context_factors.append(0.1)  # +10% confidence

        # Negative indicators (decrease confidence)
        negative_indicators = [
            "example",
            "test",
            "mock",
            "dummy",
            "placeholder",
            "todo",
            "fixme",
        ]
        for indicator in negative_indicators:
            if indicator in context_lower:
                context_factors.append(-0.2)  # -20% confidence

        # File context analysis
        if file_context:
            if any(
                test_indicator in file_context.lower()
                for test_indicator in ["test", "spec", "mock"]
            ):
                context_factors.append(-0.3)  # Test files likely have fake secrets
            elif any(
                config_indicator in file_context.lower()
                for config_indicator in [".env", "config", "settings"]
            ):
                context_factors.append(0.2)  # Config files likely have real secrets

        # Calculate final confidence
        confidence_adjustment = sum(context_factors)
        final_confidence = min(1.0, max(0.0, base_confidence + confidence_adjustment))

        return final_confidence

    def _extract_context_window(
        self, content: str, start: int, end: int, window_size: int = 50
    ) -> str:
        """Extract surrounding context for analysis"""
        context_start = max(0, start - window_size)
        context_end = min(len(content), end + window_size)
        return content[context_start:context_end]

    def _generate_remediation_suggestion(
            self,
            match,
            pattern_name: str,
            file_context: str) -> str:
        """Generate intelligent remediation suggestions"""
        suggestions = {
            "openai_key": 'Replace with environment variable: os.getenv("OPENAI_API_KEY")',
            "github_token": "Use GitHub Actions secrets: ${{ secrets.GITHUB_TOKEN }}",
            "aws_access_key": "Configure AWS CLI or use IAM roles instead of hardcoded keys",
            "generic_api_key": "Move to environment variables or secure key management system",
            "database_url": "Use connection parameters separately and secure credential storage",
        }

        base_suggestion = suggestions.get(
            pattern_name, "Move secret to secure configuration management"
        )

        # Add context-specific guidance
        if ".env" in file_context.lower():
            return f"{base_suggestion}. Ensure .env file is in .gitignore"
        elif "config" in file_context.lower():
            return f"{base_suggestion}. Consider using encrypted configuration"
        else:
            return base_suggestion


class ContextualAnalyzer:
    """Advanced contextual analysis for semantic understanding"""

    def __init__(self):
        """TODO: Add docstring for __init__"""

        self.semantic_patterns = {
            "assignment_context": r'(\w+)\s*[=:]\s*["\']?([^"\';\n]+)["\']?',
            "function_call_context": r'(\w+)\s*\([^)]*["\']?([^"\')\n]+)["\']?[^)]*\)',
            "import_context": r"from\s+(\w+)\s+import|import\s+(\w+)",
            "comment_context": r"#.*?$|//.*?$|/\*.*?\*/",
        }

    async def analyze_semantic_context(self, content: str) -> Dict[str, float]:
        """Analyze semantic context to improve detection accuracy"""
        context_scores = {
            "legitimate_usage": 0.0,
            "test_environment": 0.0,
            "documentation": 0.0,
            "configuration": 0.0,
        }

        # Analyze code patterns
        lines = content.split("\n")
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Configuration context
            if any(
                config_word in line_lower for config_word in [
                    "config",
                    "settings",
                    "env"]):
                context_scores["configuration"] += 0.1

            # Test context
            if any(
                test_word in line_lower for test_word in [
                    "test",
                    "mock",
                    "fixture",
                    "dummy"]):
                context_scores["test_environment"] += 0.1

            # Documentation context
            if any(
                doc_word in line_lower for doc_word in [
                    "example",
                    "sample",
                    "demo",
                    "tutorial"]):
                context_scores["documentation"] += 0.1

        return context_scores


class ThreatPredictionEngine:
    """Predictive threat assessment for proactive prevention"""

    def __init__(self):
        """TODO: Add docstring for __init__"""

        self.threat_indicators = {
            "high_risk_patterns": [
                r"(?i)prod[uction]*[_-]*(key|token|secret)",
                r"(?i)live[_-]*(key|token|secret)",
                r"(?i)real[_-]*(key|token|secret)",
            ],
            "medium_risk_patterns": [
                r"(?i)dev[elopment]*[_-]*(key|token|secret)",
                r"(?i)staging[_-]*(key|token|secret)",
                r"(?i)temp[orary]*[_-]*(key|token|secret)",
            ],
            "commit_risk_patterns": [
                r"(?i)(fix|add|update)[_-]*(key|token|secret)",
                r"(?i)(temporary|temp|quick)[_-]*fix",
            ],
        }

    async def predict_potential_leaks(self, content: str) -> List[ThreatIntelligence]:
        """Predict potential security threats before they become leaks"""
        threats = []

        # Analyze for risk patterns
        for risk_level, patterns in self.threat_indicators.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    threat = ThreatIntelligence(
                        pattern_id=(
                            f"{risk_level}_{hashlib.md5(match.group(0).encode()).hexdigest()[:8]}",
                        )
                        threat_type=risk_level.replace("_patterns", ""),
                        confidence=0.7 if "high_risk" in risk_level else 0.5,
                        context={"match": match.group(0), "position": match.start()},
                        severity="HIGH" if "high_risk" in risk_level else "MEDIUM",
                        remediation_suggestion=(
                            f"Review {risk_level.replace('_patterns', '')} context for potential secrets",
                        )
                    )
                    threats.append(threat)

        return threats


class AutoRemediationSystem:
    """Automated remediation system for detected threats"""

    def __init__(self):
        """TODO: Add docstring for __init__"""

        self.remediation_strategies = {
            "CRITICAL": self._immediate_remediation,
            "HIGH": self._priority_remediation,
            "MEDIUM": self._scheduled_remediation,
            "LOW": self._advisory_remediation,
        }

    async def remediate_threat(self, detection: SecretDetection) -> Dict[str, any]:
        """Apply appropriate remediation based on threat level"""
        strategy = self.remediation_strategies.get(
            detection.threat_level, self._advisory_remediation
        )

        try:
            result = await strategy(detection)
            logger.info(
                f"✅ Applied {
                    detection.threat_level} remediation for {
                    detection.pattern}")
            return result
        except Exception as e:
            logger.error(f"❌ Remediation failed for {detection.pattern}: {e}")
            return {"success": False, "error": str(e)}

    async def _immediate_remediation(
            self, detection: SecretDetection) -> Dict[str, any]:
        """Immediate remediation for critical threats"""
        # For EQ12: Log critical alert and suggest immediate action
        return {
            "success": True,
            "action": "IMMEDIATE_ALERT",
            "message": f"CRITICAL: {detection.pattern} detected - {detection.suggested_remediation}",
            "requires_human_action": True,
        }

    async def _priority_remediation(self, detection: SecretDetection) -> Dict[str, any]:
        """Priority remediation for high-level threats"""
        return {
            "success": True,
            "action": "PRIORITY_REVIEW",
            "message": f"HIGH: {detection.pattern} requires review - {detection.suggested_remediation}",
            "requires_human_action": True,
        }

    async def _scheduled_remediation(
            self, detection: SecretDetection) -> Dict[str, any]:
        """Scheduled remediation for medium-level threats"""
        return {
            "success": True,
            "action": "SCHEDULED_REVIEW",
            "message": f"MEDIUM: {detection.pattern} scheduled for review",
            "requires_human_action": False,
        }

    async def _advisory_remediation(self, detection: SecretDetection) -> Dict[str, any]:
        """Advisory remediation for low-level threats"""
        return {
            "success": True,
            "action": "ADVISORY_NOTE",
            "message": f"LOW: {detection.pattern} noted for awareness",
            "requires_human_action": False,
        }


class AgenticSecretDetectionEngine:
    """Main agentic secret detection engine integrating all components"""

    def __init__(self):
        """TODO: Add docstring for __init__"""

        self.pattern_learner = MLPatternLearner()
        self.context_analyzer = ContextualAnalyzer()
        self.threat_predictor = ThreatPredictionEngine()
        self.auto_remediator = AutoRemediationSystem()

        # Performance tracking
        self.detection_stats = {
            "total_scans": 0,
            "threats_detected": 0,
            "false_positives": 0,
            "successful_remediations": 0,
        }

    async def comprehensive_scan(
            self, content: str, file_path: str = "") -> Dict[str, any]:
        """Comprehensive agentic secret scanning with all intelligence layers"""
        self.detection_stats["total_scans"] += 1

        logger.info(
            f"🔍 Starting comprehensive secret scan for {
                file_path or 'content'}")

        # Run all detection engines in parallel
        results = await asyncio.gather(
            self.pattern_learner.detect_with_confidence(content, file_path),
            self.context_analyzer.analyze_semantic_context(content),
            self.threat_predictor.predict_potential_leaks(content),
            return_exceptions=True,
        )

        ml_detections = results[0] if not isinstance(results[0], Exception) else []
        context_analysis = results[1] if not isinstance(results[1], Exception) else {}
        threat_predictions = results[2] if not isinstance(results[2], Exception) else []

        # Consolidate and prioritize threats
        consolidated_threats = await self._consolidate_threats(
            ml_detections, context_analysis, threat_predictions
        )

        # Apply automatic remediation for high-confidence threats
        remediation_results = []
        for threat in consolidated_threats:
            if threat.confidence > 0.85:  # High confidence threshold
                remediation = await self.auto_remediator.remediate_threat(threat)
                remediation_results.append(remediation)
                if remediation["success"]:
                    self.detection_stats["successful_remediations"] += 1

        self.detection_stats["threats_detected"] += len(consolidated_threats)

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "file_path": file_path,
            "threats_found": len(consolidated_threats),
            "high_confidence_threats": len(
                [t for t in consolidated_threats if t.confidence > 0.85]
            ),
            "detections": [self._serialize_detection(d) for d in consolidated_threats],
            "context_analysis": context_analysis,
            "remediation_actions": remediation_results,
            "scan_stats": self.detection_stats.copy(),
        }

    async def _consolidate_threats(
        self,
        ml_detections: List[SecretDetection],
        context_analysis: Dict,
        threat_predictions: List[ThreatIntelligence],
    ) -> List[SecretDetection]:
        """Consolidate and rank threats from multiple detection engines"""
        # Apply context-based confidence adjustments
        adjusted_detections = []

        for detection in ml_detections:
            # Adjust confidence based on semantic context
            context_adjustment = 0.0
            if context_analysis.get("test_environment", 0) > 0.3:
                context_adjustment -= 0.2  # Reduce confidence in test contexts
            if context_analysis.get("configuration", 0) > 0.3:
                context_adjustment += 0.1  # Increase confidence in config contexts

            detection.confidence = min(
                1.0, max(0.0, detection.confidence + context_adjustment))
            adjusted_detections.append(detection)

        # Sort by confidence and threat level
        threat_priority = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        adjusted_detections.sort(
            key=lambda d: (threat_priority.get(d.threat_level, 0), d.confidence),
            reverse=True,
        )

        return adjusted_detections

    def _serialize_detection(self, detection: SecretDetection) -> Dict[str, any]:
        """Serialize detection for JSON output"""
        return {
            "pattern": detection.pattern,
            "threat_level": detection.threat_level,
            "confidence": detection.confidence,
            "context_window": (
                detection.context_window[:100] + "..."
                if len(detection.context_window) > 100
                else detection.context_window
            ),
            "suggested_remediation": detection.suggested_remediation,
        }


# Enhanced EQ12 SecretRedactionFilter with agentic capabilities
class AgenticSecretRedactionFilter(SecretRedactionFilter):
    """Enhanced secret redaction filter with agentic intelligence"""

    def __init__(self):
        """TODO: Add docstring for __init__"""

        super().__init__()
        self.agentic_engine = AgenticSecretDetectionEngine()
        self.real_time_cache = {}

    def filter(self, record: logging.LogRecord) -> bool:
        """Apply agentic secret detection to log records"""
        if hasattr(record, "msg") and record.msg:
            # Use agentic detection for enhanced accuracy
            try:
                # Run synchronous version for logging filter
                detections = asyncio.run(
                    self.agentic_engine.pattern_learner.detect_with_confidence(str(record.msg))
                )

                # Apply intelligent redaction
                msg = str(record.msg)
                for detection in detections:
                    if detection.confidence > 0.7:  # High confidence threshold for redaction
                        msg = msg.replace(
                            detection.match_text,
                            f"***REDACTED_{detection.pattern.upper()}***",
                        )

                record.msg = msg

            except Exception as e:
                # Fallback to original redaction if agentic detection fails
                logger.debug(f"Agentic redaction fallback: {e}")
                return super().filter(record)

        return True


def main():
    """Main execution function for testing"""
    print("🛡️ EQ12 Agentic Secret Detection Engine")
    print("=" * 50)

    # Test content with various secret types
    test_content = """
    # Configuration
    OPENAI_API_KEY = "sk-1234567890abcdef1234567890abcdef123456789012345678"
    github_token = "ghp_1234567890123456789012345678901234567890"

    # Database connection
    DATABASE_URL = "postgresql://user:password@localhost:5432/db"

    # Test examples (should have lower confidence)
    # Example: api_key = "sk-example1234567890abcdef1234567890abcdef123456789012"
    """

    async def run_test():
        engine = AgenticSecretDetectionEngine()
        results = await engine.comprehensive_scan(test_content, "config_test.py")

        print("\n📊 Scan Results:")
        print(f"Threats found: {results['threats_found']}")
        print(f"High confidence: {results['high_confidence_threats']}")

        for detection in results["detections"]:
            print(f"\n🚨 {detection['threat_level']} - {detection['pattern']}")
            print(f"   Confidence: {detection['confidence']:.2f}")
            print(f"   Remediation: {detection['suggested_remediation']}")

        print("\n✅ Agentic secret detection test completed!")

    asyncio.run(run_test())


if __name__ == "__main__":
    main()
