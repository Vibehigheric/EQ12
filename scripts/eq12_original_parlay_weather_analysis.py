"""
EQ12 Original Parlay Analysis vs Weather Intelligence

Analyzing our original +64,515 odds 10-leg parlay against comprehensive weather data
to determine if any legs should be adjusted based on stadium locations and weather conditions.

Original 10-Leg Parlay:
1. Kings @ Jets UNDER 5.5 (-110) - NHL
2. Boston ML (-125) - NHL
3. Alabama -7 (-110) - College Football
4. Ohio State -14 (-110) - College Football
5. Broncos @ Jets UNDER 41 (-110) - NFL
6. Ravens -2.5 (-110) - NFL
7. Cardinals +3.5 (-110) - NFL
8. Titans @ Colts OVER 42.5 (-110) - NFL
9. Dolphins -6 (-110) - NFL
10. Chiefs -9.5 (-110) - NFL
"""

import json
import logging
from datetime import UTC, datetime
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OriginalParlayWeatherAnalysis:
    """Analyze original parlay legs against weather intelligence data"""

    def __init__(self):
        # Original parlay legs
        self.original_parlay = [
            {
                "sport": "NHL",
                "pick": "Kings @ Jets UNDER 5.5",
                "odds": -110,
                "confidence": 0.85,
            },
            {"sport": "NHL", "pick": "Boston ML", "odds": -125, "confidence": 0.80},
            {"sport": "NCAA", "pick": "Alabama -7", "odds": -110, "confidence": 0.80},
            {
                "sport": "NCAAF",
                "pick": "Ohio State -14",
                "odds": -110,
                "confidence": 0.75,
            },
            {
                "sport": "NFL",
                "pick": "Broncos @ Jets UNDER 41",
                "odds": -110,
                "confidence": 0.85,
            },
            {"sport": "NFL", "pick": "Ravens -2.5", "odds": -110, "confidence": 0.75},
            {
                "sport": "NFL",
                "pick": "Cardinals +3.5",
                "odds": -110,
                "confidence": 0.70,
            },
            {
                "sport": "NFL",
                "pick": "Titans @ Colts OVER 42.5",
                "odds": -110,
                "confidence": 0.80,
            },
            {"sport": "NFL", "pick": "Dolphins -6", "odds": -110, "confidence": 0.75},
            {"sport": "NFL", "pick": "Chiefs -9.5", "odds": -110, "confidence": 0.85},
        ]

        # Load weather intelligence data
        self.college_weather_data = self._load_college_weather_data()
        self.nfl_weather_data = self._load_nfl_weather_data()

    def _load_college_weather_data(self) -> dict[str, Any]:
        """Load college football weather analysis"""
        try:
            import glob

            college_files = glob.glob(
                "C:\\\\EQ12\\\\data\\college_stadium_weather_*.json")
            if college_files:
                latest_file = max(college_files)
                with open(latest_file) as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Could not load college weather data: {e}")
        return {}

    def _load_nfl_weather_data(self) -> dict[str, Any]:
        """Load NFL weather analysis"""
        try:
            import glob

            nfl_files = glob.glob("C:\\\\EQ12\\\\data\\nfl_stadium_weather_*.json")
            if nfl_files:
                latest_file = max(nfl_files)
                with open(latest_file) as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Could not load NFL weather data: {e}")
        return {}

    def analyze_parlay_against_weather(self) -> dict[str, Any]:
        """Analyze each parlay leg against weather intelligence"""

        analysis = {
            "timestamp": datetime.now(UTC).isoformat(),
            "original_parlay_analysis": {
                "total_legs": len(self.original_parlay),
                "total_odds": "+64,515",
                "potential_payout": "$6,462 on $10 bet",
                "original_average_confidence": "80%",
            },
            "weather_impact_assessment": [],
            "recommended_adjustments": [],
            "final_recommendation": {},
            "leg_by_leg_analysis": [],
        }

        logger.info("Analyzing original parlay legs against weather intelligence...")

        for i, leg in enumerate(self.original_parlay, 1):
            leg_analysis = self._analyze_individual_leg(leg, i)
            analysis["leg_by_leg_analysis"].append(leg_analysis)

            # Check for weather impacts
            if leg_analysis.get("weather_impact_detected"):
                analysis["weather_impact_assessment"].append(leg_analysis)

            # Check for recommended changes
            if leg_analysis.get("recommendation") != "KEEP":
                analysis["recommended_adjustments"].append(leg_analysis)

        # Generate final recommendation
        analysis["final_recommendation"] = self._generate_final_recommendation(analysis)

        return analysis

    def _analyze_individual_leg(
            self, leg: dict[str, Any], leg_number: int) -> dict[str, Any]:
        """Analyze individual parlay leg against weather data"""

        leg_analysis = {
            "leg_number": leg_number,
            "original_pick": leg["pick"],
            "sport": leg["sport"],
            "original_confidence": leg["confidence"],
            "weather_impact_detected": False,
            "weather_details": {},
            "adjusted_confidence": leg["confidence"],
            "recommendation": "KEEP",
            "reasoning": "No weather impact",
        }

        # NHL games - indoor venues, no weather impact
        if leg["sport"] == "NHL":
            leg_analysis["reasoning"] = "Indoor arena - weather neutral"
            return leg_analysis

        # College Football analysis
        if leg["sport"] == "NCAAF":
            leg_analysis = self._analyze_college_leg(leg, leg_analysis)

        # NFL analysis
        if leg["sport"] == "NFL":
            leg_analysis = self._analyze_nfl_leg(leg, leg_analysis)

        return leg_analysis

    def _analyze_college_leg(
        self, leg: dict[str, Any], leg_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze college football leg against weather data"""

        pick = leg["pick"]

        # Alabama -7 analysis
        if "Alabama" in pick:
            # Find Alabama @ Missouri in weather data
            college_games = self.college_weather_data.get("games", [])
            for game in college_games:
                matchup = game.get("matchup", "")
                if "Alabama" in matchup and "Missouri" in matchup:
                    weather_data = game.get("weather_data", {})
                    if weather_data:
                        betting_impact = weather_data.get("betting_impact", {})

                        leg_analysis["weather_impact_detected"] = True
                        leg_analysis["weather_details"] = {
                            "stadium": "Faurot Field at Memorial Stadium",
                            "location": "Columbia, Missouri",
                            "conditions": weather_data.get("current", {}),
                            "impact": betting_impact,
                        }

                        # Check if weather affects confidence
                        confidence_mod = betting_impact.get("confidence_modifier", 0)
                        if abs(confidence_mod) > 0.05:  # Significant weather impact
                            leg_analysis["adjusted_confidence"] = max(
                                0.1, min(0.95, leg["confidence"] + confidence_mod)
                            )
                            leg_analysis["reasoning"] = (
                                f"Weather impact: {
                                    confidence_mod:+.1%} confidence adjustment")

                    break

        # Ohio State -14 analysis (similar process)
        elif "Ohio State" in pick:
            leg_analysis["reasoning"] = "Stadium location not in weather database - keep original"

        return leg_analysis

    def _analyze_nfl_leg(self, leg: dict[str, Any],
                         leg_analysis: dict[str, Any]) -> dict[str, Any]:
        """Analyze NFL leg against weather data"""

        pick = leg["pick"]

        # Find corresponding NFL game in weather data
        nfl_games = self.nfl_weather_data.get("games", [])

        for game in nfl_games:
            matchup = game.get("matchup", "")

            # Check each NFL leg
            if self._match_nfl_leg_to_game(pick, matchup):
                stadium_info = game.get("stadium_info", {})
                weather_data = game.get("weather_data", {})

                if weather_data:
                    betting_impact = weather_data.get("nfl_betting_impact", {})

                    leg_analysis["weather_impact_detected"] = True
                    leg_analysis["weather_details"] = {
                        "stadium": stadium_info.get("stadium", "Unknown"),
                        "location": f"{stadium_info.get(
                            'city',
                            '')}, {stadium_info.get('state',
                                                    ''
                                                    )}",
                        "roof_type": stadium_info.get("roof_type", "Unknown"),
                        "conditions": weather_data.get("current", {}),
                        "impact_level": betting_impact.get("impact_level", "none"),
                    }

                    # Analyze specific impact on this leg
                    leg_analysis = self._assess_nfl_leg_impact(
                        leg, leg_analysis, betting_impact)

                break

        return leg_analysis

    def _match_nfl_leg_to_game(self, pick: str, matchup: str) -> bool:
        """Match parlay leg to NFL game matchup"""

        # Extract teams from pick and matchup
        pick_lower = pick.lower()
        matchup_lower = matchup.lower()

        # Common team name mappings
        team_mappings = {
            "broncos": ["denver", "broncos"],
            "jets": ["new york jets", "jets"],
            "ravens": ["baltimore", "ravens"],
            "cardinals": ["arizona", "cardinals"],
            "titans": ["tennessee", "titans"],
            "colts": ["indianapolis", "colts"],
            "dolphins": ["miami", "dolphins"],
            "chiefs": ["kansas city", "chiefs"],
        }

        # Check if any team names match
        for pick_team, match_variants in team_mappings.items():
            if pick_team in pick_lower:
                if any(variant in matchup_lower for variant in match_variants):
                    return True

        return False

    def _assess_nfl_leg_impact(
        self,
        leg: dict[str, Any],
        leg_analysis: dict[str, Any],
        betting_impact: dict[str, Any],
    ) -> dict[str, Any]:
        """Assess weather impact on specific NFL leg"""

        pick = leg["pick"]
        impact_level = betting_impact.get("impact_level", "none")
        confidence_mod = betting_impact.get("confidence_modifier", 0)

        # Broncos @ Jets UNDER 41
        if "broncos" in pick.lower() and "under" in pick.lower():
            if impact_level in ["high", "extreme"]:
                # Weather strongly favors UNDER - BOOST confidence
                leg_analysis["adjusted_confidence"] = min(
                    0.95, leg["confidence"] + abs(confidence_mod)
                )
                leg_analysis["recommendation"] = "STRONG KEEP"
                leg_analysis["reasoning"] = (
                    f"Weather STRONGLY favors UNDER - {impact_level} impact boosts confidence")
            else:
                leg_analysis["reasoning"] = "Weather neutral or minimal impact"

        # Ravens -2.5
        elif "ravens" in pick.lower():
            if impact_level in ["high", "extreme"]:
                # High weather impact may affect point spread accuracy
                leg_analysis["adjusted_confidence"] = max(
                    0.5, leg["confidence"] + confidence_mod)
                leg_analysis["recommendation"] = "CAUTION"
                leg_analysis["reasoning"] = (
                    f"Weather may affect game flow - {impact_level} conditions"
                )
            else:
                leg_analysis["reasoning"] = "Weather minimal impact on spread"

        # Cardinals +3.5
        elif "cardinals" in pick.lower():
            # Cardinals @ Colts is dome game (Lucas Oil Stadium)
            if betting_impact.get("impact_level") == "none":
                leg_analysis["recommendation"] = "STRONG KEEP"
                leg_analysis["reasoning"] = "Dome game - weather neutral, good underdog value"

        # Titans @ Colts OVER 42.5
        elif "titans" in pick.lower() and "over" in pick.lower():
            # Also dome game
            if betting_impact.get("impact_level") == "none":
                leg_analysis["recommendation"] = "STRONG KEEP"
                leg_analysis["reasoning"] = (
                    "Dome game - weather neutral, favor OVER in controlled conditions"
                )

        # Other NFL legs
        else:
            if impact_level in ["high", "extreme"]:
                leg_analysis["adjusted_confidence"] = max(
                    0.5, leg["confidence"] + confidence_mod)
                leg_analysis["reasoning"] = (
                    f"Weather impact: {impact_level} conditions may affect game"
                )

        return leg_analysis

    def _generate_final_recommendation(
            self, analysis: dict[str, Any]) -> dict[str, Any]:
        """Generate final recommendation for parlay adjustments"""

        legs_analysis = analysis["leg_by_leg_analysis"]
        weather_impacts = len(analysis["weather_impact_assessment"])
        len(analysis["recommended_adjustments"])

        # Calculate new average confidence
        total_confidence = sum(leg.get("adjusted_confidence", 0.75)
                               for leg in legs_analysis)
        new_avg_confidence = total_confidence / len(legs_analysis)

        # Count strong keeps and cautions
        strong_keeps = sum(1 for leg in legs_analysis if leg.get(
            "recommendation") == "STRONG KEEP")
        cautions = sum(1 for leg in legs_analysis if leg.get(
            "recommendation") == "CAUTION")

        recommendation = {
            "overall_verdict": "KEEP ORIGINAL PARLAY",
            "confidence_change": f"{new_avg_confidence:.1%} (vs original 80%)",
            "weather_impacts_detected": weather_impacts,
            "legs_with_positive_weather": strong_keeps,
            "legs_with_caution": cautions,
            "reasoning": [],
            "alternative_strategy": {},
        }

        # Generate reasoning
        if strong_keeps >= 2:
            recommendation["reasoning"].append(
                f"{strong_keeps} legs benefit from weather intelligence"
            )

        if weather_impacts >= 3:
            recommendation["reasoning"].append(
                "Multiple weather impacts detected - good data advantage"
            )

        if new_avg_confidence > 0.80:
            recommendation["overall_verdict"] = "ENHANCED KEEP - Weather Boosts Confidence"
            recommendation["reasoning"].append(
                "Weather intelligence increases overall confidence")
        elif new_avg_confidence < 0.75:
            recommendation["overall_verdict"] = "CONSIDER MODIFICATIONS"
            recommendation["reasoning"].append(
                "Weather conditions may reduce some leg confidence")

        # Alternative strategy
        recommendation["alternative_strategy"] = {
            "option_1": "Keep original +64,515 parlay as entertainment bet ($5-10)",
            "option_2": "Create separate weather-enhanced smaller parlays with higher probability",
            "option_3": "Mix individual weather-enhanced bets with reduced parlay size",
        }

        return recommendation

    def save_analysis(self, analysis: dict[str, Any]) -> str:
        """Save parlay weather analysis"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\\\EQ12\\\\data\\original_parlay_weather_analysis_{timestamp}.json"

        try:
            with open(filename, "w") as f:
                json.dump(analysis, f, indent=2)

            logger.info(f"Parlay analysis saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Could not save analysis: {e}")
            return ""


def main():
    """Analyze original +64,515 parlay against weather intelligence"""

    print("🎯 EQ12 ORIGINAL PARLAY vs WEATHER INTELLIGENCE ANALYSIS")
    print("=" * 60)

    # Initialize analyzer
    analyzer = OriginalParlayWeatherAnalysis()

    # Run analysis
    analysis = analyzer.analyze_parlay_against_weather()

    # Save results
    filename = analyzer.save_analysis(analysis)

    # Display results
    print("\\n📋 ORIGINAL PARLAY OVERVIEW:")
    original = analysis["original_parlay_analysis"]
    print(f"Legs: {original['total_legs']}")
    print(f"Odds: {original['total_odds']}")
    print(f"Payout: {original['potential_payout']}")
    print(f"Original Confidence: {original['original_average_confidence']}")

    print("\\n🌦️ WEATHER IMPACT ASSESSMENT:")
    print(f"Legs with weather impact: {len(analysis['weather_impact_assessment'])}")
    print(f"Recommended adjustments: {len(analysis['recommended_adjustments'])}")

    print("\\n🔍 LEG-BY-LEG ANALYSIS:")
    for leg in analysis["leg_by_leg_analysis"]:
        leg_num = leg["leg_number"]
        pick = leg["original_pick"]
        recommendation = leg["recommendation"]
        reasoning = leg["reasoning"]
        confidence = leg.get(
            "adjusted_confidence", leg.get(
                "original_confidence", 0.75))

        status_emoji = ("✅" if recommendation ==
                        "STRONG KEEP" else "⚠️" if recommendation == "CAUTION" else "➡️")

        print(f"\\n{status_emoji} Leg {leg_num}: {pick}")
        print(f"   Confidence: {confidence:.1%} | Rec: {recommendation}")
        print(f"   Reasoning: {reasoning}")

        if leg.get("weather_impact_detected"):
            weather = leg.get("weather_details", {})
            stadium = weather.get("stadium", "Unknown")
            impact = weather.get("impact_level", "none")
            print(f"   Weather: {stadium} - {impact} impact")

    print("\\n🎯 FINAL RECOMMENDATION:")
    final_rec = analysis["final_recommendation"]
    print(f"Verdict: {final_rec['overall_verdict']}")
    print(f"New Confidence: {final_rec['confidence_change']}")
    print(f"Weather Advantages: {final_rec['legs_with_positive_weather']} legs")

    print("\\nReasons:")
    for reason in final_rec["reasoning"]:
        print(f"• {reason}")

    print("\\n💡 STRATEGY OPTIONS:")
    strategy = final_rec["alternative_strategy"]
    for option, description in strategy.items():
        print(f"• {option.replace('_', ' ').title()}: {description}")

    if filename:
        print(f"\\n💾 Full analysis saved to: {filename}")

    print("\\n✅ PARLAY WEATHER ANALYSIS COMPLETE!")


if __name__ == "__main__":
    main()
