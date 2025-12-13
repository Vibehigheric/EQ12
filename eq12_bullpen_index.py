#!/usr/bin/env python3
"""
EQ12 MLB Playoffs Bullpen Readiness & Leverage Index
===================================================
Calculate BullpenReadinessScore (0-100) based on:
- Last 3 days innings pitched
- Back-to-back appearances
- High-leverage (gmLI) pitch counts
- Rest days for closers
- Playoff workload factors

Used to adjust: totals, team ML, late-inning live models
"""

import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta

import aiohttp


@dataclass
class PitcherWorkload:
    name: str
    pitcher_id: str
    innings_last_3_days: float
    appearances_last_3_days: int
    back_to_back_games: int
    high_leverage_pitches: int  # gmLI > 1.5
    rest_days: int
    is_closer: bool
    playoff_innings_total: float
    fatigue_score: float  # 0-100 (100 = fresh)


@dataclass
class BullpenReadiness:
    team: str
    game_pk: str
    overall_score: int  # 0-100
    closer_available: bool
    setup_men_available: int
    total_fresh_arms: int
    high_leverage_ready: int
    fatigue_concerns: list[str]
    workload_details: list[PitcherWorkload]
    adjustment_factors: dict[str, float]  # For totals/ML
    last_updated: datetime


class MLBBullpenIndex:
    """Calculates bullpen readiness for playoff betting adjustments"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

        # MLB Stats API
        self.mlb_base = "https://statsapi.mlb.com/api/v1"

        # Bullpen role classifications
        self.closer_roles = ["Closer"]
        self.setup_roles = ["Setup", "Middle Reliever"]
        self.high_leverage_threshold = 1.5  # gmLI threshold

        # Scoring weights
        self.weights = {
            "innings_penalty": 15,  # Points lost per IP in last 3 days
            "back_to_back_penalty": 25,  # Points lost per consecutive game
            "rest_bonus": 10,  # Points gained per rest day
            "closer_factor": 1.5,  # Multiplier for closer availability
            "playoff_fatigue": 5,  # Extra penalty per playoff IP
        }

    def setup_logging(self):
        """Setup bullpen logging"""
        log_dir = r"C:\EQ12\logs"
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(
            log_dir, f"bullpen_readiness_{datetime.now().strftime('%Y%m%d')}.log"
        )

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )

    async def get_team_bullpen_data(self, team_id: int, days_back: int = 3) -> list[dict]:
        """Get recent bullpen usage data for team"""

        async with aiohttp.ClientSession() as session:
            # Get last X days of games
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back + 5)  # Buffer for games

            params = {
                "teamId": team_id,
                "startDate": start_date.strftime("%Y-%m-%d"),
                "endDate": end_date.strftime("%Y-%m-%d"),
                "gameTypes": "P,F,D,L,W",  # Playoff types
                "hydrate": "pitchingStats",
            }

            try:
                async with session.get(
                    f"{self.mlb_base}/teams/{team_id}/stats", params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_bullpen_usage(data, days_back)
                    self.logger.error(
                        f"Failed to get bullpen data for team {team_id}: {response.status}"
                    )
                    return []

            except Exception as e:
                self.logger.error(f"Error fetching bullpen data: {e}")
                return []

    def _parse_bullpen_usage(self, stats_data: dict, days_back: int) -> list[dict]:
        """Parse bullpen usage from stats data"""
        bullpen_usage = []

        try:
            # Get pitching stats for relievers
            pitching_stats = stats_data.get("stats", [])

            for stat_group in pitching_stats:
                splits = stat_group.get("splits", [])

                for split in splits:
                    player = split.get("player", {})
                    stats = split.get("stat", {})

                    # Only relievers
                    if stats.get("gamesStarted", 0) == 0 and stats.get("gamesPlayed", 0) > 0:
                        pitcher_data = {
                            "name": player.get("fullName", ""),
                            "pitcher_id": player.get("id", ""),
                            "games_played": stats.get("gamesPlayed", 0),
                            "innings_pitched": float(stats.get("inningsPitched", "0.0")),
                            "saves": stats.get("saves", 0),
                            "holds": stats.get("holds", 0),
                            "era": float(stats.get("era", "0.00")),
                            "pitches_thrown": stats.get("pitchesThrown", 0),
                        }

                        bullpen_usage.append(pitcher_data)

        except Exception as e:
            self.logger.error(f"Error parsing bullpen usage: {e}")

        return bullpen_usage

    async def calculate_pitcher_workload(self, pitcher_data: dict, team_id: int) -> PitcherWorkload:
        """Calculate individual pitcher workload and fatigue"""

        name = pitcher_data.get("name", "")
        pitcher_id = pitcher_data.get("pitcher_id", "")

        # Get detailed game logs for last 3 days
        innings_last_3 = await self._get_recent_innings(pitcher_id, 3)
        appearances_last_3 = await self._get_recent_appearances(pitcher_id, 3)
        back_to_back = await self._get_back_to_back_count(pitcher_id)

        # Determine role
        saves = pitcher_data.get("saves", 0)
        holds = pitcher_data.get("holds", 0)
        is_closer = saves >= 3 or (saves >= 1 and holds <= saves)

        # Calculate fatigue score (starts at 100 = fresh)
        fatigue_score = 100.0

        # Penalties
        fatigue_score -= innings_last_3 * self.weights["innings_penalty"]
        fatigue_score -= back_to_back * self.weights["back_to_back_penalty"]

        # Rest bonus (if no appearances in last 2 days)
        rest_days = await self._get_rest_days(pitcher_id)
        if rest_days >= 2:
            fatigue_score += rest_days * self.weights["rest_bonus"]

        # Playoff fatigue (extra workload penalty)
        playoff_innings = pitcher_data.get("innings_pitched", 0)
        fatigue_score -= playoff_innings * self.weights["playoff_fatigue"]

        # Clamp to 0-100
        fatigue_score = max(0, min(100, fatigue_score))

        return PitcherWorkload(
            name=name,
            pitcher_id=pitcher_id,
            innings_last_3_days=innings_last_3,
            appearances_last_3_days=appearances_last_3,
            back_to_back_games=back_to_back,
            high_leverage_pitches=await self._get_high_leverage_pitches(pitcher_id),
            rest_days=rest_days,
            is_closer=is_closer,
            playoff_innings_total=playoff_innings,
            fatigue_score=fatigue_score,
        )

    async def _get_recent_innings(self, pitcher_id: str, days: int) -> float:
        """Get innings pitched in last N days"""
        # Simplified - in production would query game logs
        # For now, return estimated based on typical usage
        return 1.5  # Average recent usage

    async def _get_recent_appearances(self, pitcher_id: str, days: int) -> int:
        """Get appearance count in last N days"""
        return 2  # Typical playoff usage

    async def _get_back_to_back_count(self, pitcher_id: str) -> int:
        """Get consecutive game appearances"""
        return 1  # Conservative estimate

    async def _get_rest_days(self, pitcher_id: str) -> int:
        """Get days since last appearance"""
        return 1  # Typical rest

    async def _get_high_leverage_pitches(self, pitcher_id: str) -> int:
        """Get high-leverage pitches thrown recently"""
        return 25  # Estimated high-leverage work

    async def calculate_team_bullpen_readiness(
        self, team_id: int, team_name: str, game_pk: str = ""
    ) -> BullpenReadiness:
        """Calculate overall bullpen readiness score for team"""

        self.logger.info(f"📊 Calculating bullpen readiness for {team_name}")

        # Get bullpen data
        bullpen_data = await self.get_team_bullpen_data(team_id)

        if not bullpen_data:
            # Return default/fallback readiness
            return self._create_fallback_readiness(team_name, game_pk)

        # Calculate individual workloads
        workloads = []
        for pitcher_data in bullpen_data:
            workload = await self.calculate_pitcher_workload(pitcher_data, team_id)
            workloads.append(workload)

        # Analyze bullpen composition
        closers = [w for w in workloads if w.is_closer]
        setup_men = [w for w in workloads if not w.is_closer and w.fatigue_score >= 70]
        fresh_arms = [w for w in workloads if w.fatigue_score >= 80]
        high_leverage_ready = [w for w in workloads if w.fatigue_score >= 75]

        # Calculate overall score
        overall_score = self._calculate_overall_score(workloads)

        # Identify concerns
        fatigue_concerns = []
        for w in workloads:
            if w.is_closer and w.fatigue_score < 60:
                fatigue_concerns.append(f"Closer {w.name} fatigued ({w.fatigue_score:.0f}/100)")
            elif w.fatigue_score < 40:
                fatigue_concerns.append(f"{w.name} heavily fatigued ({w.fatigue_score:.0f}/100)")

        # Calculate betting adjustments
        adjustment_factors = self._calculate_adjustments(
            overall_score, len(closers) > 0, len(fresh_arms)
        )

        readiness = BullpenReadiness(
            team=team_name,
            game_pk=game_pk,
            overall_score=overall_score,
            closer_available=len([c for c in closers if c.fatigue_score >= 65]) > 0,
            setup_men_available=len(setup_men),
            total_fresh_arms=len(fresh_arms),
            high_leverage_ready=len(high_leverage_ready),
            fatigue_concerns=fatigue_concerns,
            workload_details=workloads,
            adjustment_factors=adjustment_factors,
            last_updated=datetime.now(UTC),
        )

        self.logger.info(f"🎯 {team_name} Bullpen Score: {overall_score}/100")
        self.logger.info(f"   Closer Available: {'✅' if readiness.closer_available else '❌'}")
        self.logger.info(f"   Fresh Arms: {len(fresh_arms)}")
        self.logger.info(f"   Concerns: {len(fatigue_concerns)}")

        return readiness

    def _calculate_overall_score(self, workloads: list[PitcherWorkload]) -> int:
        """Calculate team bullpen readiness score 0-100"""
        if not workloads:
            return 50  # Neutral

        # Weight by role importance
        total_weighted_score = 0
        total_weight = 0

        for workload in workloads:
            weight = self.weights["closer_factor"] if workload.is_closer else 1.0
            total_weighted_score += workload.fatigue_score * weight
            total_weight += weight

        overall_score = total_weighted_score / total_weight if total_weight > 0 else 50
        return int(overall_score)

    def _calculate_adjustments(
        self, bullpen_score: int, closer_available: bool, fresh_arms_count: int
    ) -> dict[str, float]:
        """Calculate betting line adjustments based on bullpen readiness"""

        adjustments = {
            "game_total": 0.0,
            "team_total": 0.0,
            "moneyline": 0.0,
            "late_inning_props": 0.0,
        }

        # Bullpen score adjustments
        if bullpen_score >= 85:
            # Elite bullpen
            adjustments["game_total"] = -0.25  # Lower totals
            adjustments["team_total"] = -0.15
            adjustments["moneyline"] = +0.02  # Small ML boost
            adjustments["late_inning_props"] = -0.10  # Favor unders

        elif bullpen_score <= 40:
            # Exhausted bullpen
            adjustments["game_total"] = +0.50  # Higher totals
            adjustments["team_total"] = +0.30
            adjustments["moneyline"] = -0.03  # ML penalty
            adjustments["late_inning_props"] = +0.15  # Favor overs

        # Closer availability
        if not closer_available:
            adjustments["late_inning_props"] += 0.20  # Big late-inning penalty
            adjustments["moneyline"] -= 0.02

        # Fresh arms depth
        if fresh_arms_count <= 2:
            adjustments["game_total"] += 0.25
            adjustments["team_total"] += 0.15

        return adjustments

    def _create_fallback_readiness(self, team_name: str, game_pk: str) -> BullpenReadiness:
        """Create fallback readiness when data unavailable"""
        return BullpenReadiness(
            team=team_name,
            game_pk=game_pk,
            overall_score=65,  # Neutral-good assumption
            closer_available=True,
            setup_men_available=2,
            total_fresh_arms=3,
            high_leverage_ready=4,
            fatigue_concerns=["Data unavailable - using estimates"],
            workload_details=[],
            adjustment_factors={
                "game_total": 0.0,
                "team_total": 0.0,
                "moneyline": 0.0,
                "late_inning_props": 0.0,
            },
            last_updated=datetime.now(UTC),
        )

    def export_readiness_report(
        self, readiness_scores: list[BullpenReadiness], output_path: str | None = None
    ):
        """Export bullpen readiness to JSON"""
        if output_path is None:
            log_dir = r"C:\EQ12\logs"
            output_path = os.path.join(
                log_dir,
                f"bullpen_readiness_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            )

        export_data = {
            "export_time": datetime.now(UTC).isoformat(),
            "teams_analyzed": len(readiness_scores),
            "bullpen_data": [],
        }

        for readiness in readiness_scores:
            team_data = asdict(readiness)
            team_data["last_updated"] = readiness.last_updated.isoformat()
            export_data["bullpen_data"].append(team_data)

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)

        self.logger.info(f"📁 Bullpen readiness exported to {output_path}")
        return output_path


async def main():
    """Demo bullpen readiness calculation"""
    index = MLBBullpenIndex()

    print("🏆 MLB Playoff Bullpen Readiness Calculator")
    print("=" * 50)

    # Example teams (would get from active playoff games)
    example_teams = [
        (119, "Los Angeles Dodgers"),
        (147, "New York Yankees"),
        (117, "Houston Astros"),
        (144, "Atlanta Braves"),
    ]

    readiness_scores = []

    for team_id, team_name in example_teams:
        readiness = await index.calculate_team_bullpen_readiness(team_id, team_name)
        readiness_scores.append(readiness)

        print(f"\n📊 {team_name}:")
        print(f"   Overall Score: {readiness.overall_score}/100")
        print(f"   Closer Available: {'✅' if readiness.closer_available else '❌'}")
        print(f"   Fresh Arms: {readiness.total_fresh_arms}")
        print(f"   Adjustments: Total {readiness.adjustment_factors['game_total']:+.2f}")

        if readiness.fatigue_concerns:
            print("   ⚠️ Concerns:")
            for concern in readiness.fatigue_concerns[:2]:  # Show top 2
                print(f"      • {concern}")

    # Export report
    report_path = index.export_readiness_report(readiness_scores)
    print(f"\n📁 Full report: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
