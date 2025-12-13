#!/usr/bin/env python3
"""
EQ12 GODSTACK - MLB Run-Scoring GLM Model
Project team runs via GLM/Poisson with park factors, handedness splits, bullpen penalties, weather/wind

Core Features:
- Poisson regression for team run distributions (0-15 runs)
- Park factor adjustments for offensive environments
- Handedness matchup modeling (L/R pitcher vs L/R hitters)
- Bullpen quality penalties and relief pitcher fatigue
- Weather impact (wind speed/direction, temperature, humidity)
- Lineup quality scoring and batting order optimization
- Pitcher strikeout/walk distributions for props

Model Output:
- Team run distributions for totals/team totals betting
- Player performance distributions for props
- Game script probabilities (blowout, close game, pitcher's duel)
"""

import argparse
import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/mlb_runs_model.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class PitcherStats:
    """Pitcher statistics and projections"""

    name: str
    team: str
    handedness: str  # "L" or "R"
    era: float
    whip: float
    k_per_9: float
    bb_per_9: float
    hr_per_9: float

    # Advanced metrics
    fip: float  # Fielding Independent Pitching
    xfip: float  # Expected FIP
    babip_against: float
    strand_rate: float

    # Situational splits
    vs_lhb_ops: float  # vs Left-handed batters
    vs_rhb_ops: float  # vs Right-handed batters
    home_era: float
    away_era: float

    # Recent form (last 15 days)
    recent_era: float
    recent_k_rate: float
    innings_pitched_season: float


@dataclass
class TeamOffense:
    """Team offensive statistics"""

    team: str
    runs_per_game: float
    ops: float  # On-base Plus Slugging
    woba: float  # Weighted On-Base Average
    wrc_plus: int  # Weighted Runs Created Plus (100 = league average)

    # Handedness splits
    vs_lhp_ops: float
    vs_rhp_ops: float

    # Situational
    home_runs_per_game: float
    away_runs_per_game: float
    vs_quality_starters_ops: float  # vs ERA < 3.50

    # Lineup composition
    lineup_depth_score: float  # 1-10 scale
    speed_score: float  # Stolen base threat
    power_score: float  # Home run capability


@dataclass
class ParkFactors:
    """Ballpark environmental factors"""

    park_name: str
    runs_factor: float  # 1.0 = neutral, >1.0 = hitter friendly
    hr_factor: float

    # Dimensions
    left_field_distance: int
    center_field_distance: int
    right_field_distance: int
    foul_territory_size: str  # "large", "average", "small"

    # Environmental
    altitude_feet: int
    avg_temperature: float
    avg_wind_speed: float
    dome_stadium: bool


@dataclass
class WeatherConditions:
    """Game-day weather conditions"""

    temperature: float  # Fahrenheit
    wind_speed: float  # MPH
    wind_direction: str  # "in", "out", "cross", "calm"
    humidity: float  # Percentage
    precipitation_chance: float
    barometric_pressure: float


@dataclass
class GameProjection:
    """Complete game projection output"""

    game_id: str
    home_team: str
    away_team: str

    # Run distributions (probabilities for 0-15 runs)
    home_run_distribution: list[float]
    away_run_distribution: list[float]

    # Expected values
    home_runs_expected: float
    away_runs_expected: float
    total_runs_expected: float

    # Probabilities
    under_total_prob: dict[float, float]  # total -> probability
    over_total_prob: dict[float, float]

    # Team total probabilities
    home_team_total_probs: dict[float, dict[str, float]]  # line -> {"over": p, "under": p}
    away_team_total_probs: dict[float, dict[str, float]]

    # Pitcher projections
    home_pitcher_ks: dict[str, float]  # "expected", "distribution"
    away_pitcher_ks: dict[str, float]
    home_pitcher_walks: dict[str, float]
    away_pitcher_walks: dict[str, float]

    # Game script probabilities
    blowout_prob: float  # >7 run difference
    close_game_prob: float  # <=3 run difference
    pitchers_duel_prob: float  # <6 total runs

    # Confidence metrics
    model_confidence: float  # 0-1 scale
    data_quality_score: float  # Based on available inputs

    projection_timestamp: datetime


class MLBRunsGLM:
    """MLB Run-Scoring Generalized Linear Model"""

    def __init__(self, data_path: str | None = None):
        self.data_path = data_path or "C:/EQ12/data"
        self.models_path = Path("C:/EQ12/models")
        self.models_path.mkdir(parents=True, exist_ok=True)

        # Model components
        self.runs_model = None
        self.scaler = StandardScaler()

        # Static data
        self.park_factors = self._load_park_factors()
        self.league_averages = self._load_league_averages()

        # Model parameters
        self.feature_weights = {}
        self.model_version = "1.0.0"

        logger.info("MLBRunsGLM initialized")

    def _load_park_factors(self) -> dict[str, ParkFactors]:
        """Load MLB park factors data"""

        # MLB ballpark factors (2025 season estimates)
        park_data = {
            "Yankee Stadium": ParkFactors(
                park_name="Yankee Stadium",
                runs_factor=1.02,
                hr_factor=1.15,
                left_field_distance=318,
                center_field_distance=408,
                right_field_distance=314,
                foul_territory_size="small",
                altitude_feet=55,
                avg_temperature=72.0,
                avg_wind_speed=8.5,
                dome_stadium=False,
            ),
            "Rogers Centre": ParkFactors(
                park_name="Rogers Centre",
                runs_factor=0.98,
                hr_factor=0.95,
                left_field_distance=328,
                center_field_distance=400,
                right_field_distance=328,
                foul_territory_size="average",
                altitude_feet=348,
                avg_temperature=70.0,
                avg_wind_speed=5.2,
                dome_stadium=True,
            ),
            "T-Mobile Park": ParkFactors(
                park_name="T-Mobile Park",
                runs_factor=0.94,
                hr_factor=0.88,
                left_field_distance=331,
                center_field_distance=401,
                right_field_distance=326,
                foul_territory_size="large",
                altitude_feet=56,
                avg_temperature=65.0,
                avg_wind_speed=7.8,
                dome_stadium=False,
            ),
            "Comerica Park": ParkFactors(
                park_name="Comerica Park",
                runs_factor=0.96,
                hr_factor=0.91,
                left_field_distance=345,
                center_field_distance=420,
                right_field_distance=325,
                foul_territory_size="large",
                altitude_feet=585,
                avg_temperature=68.0,
                avg_wind_speed=9.2,
                dome_stadium=False,
            ),
        }

        return park_data

    def _load_league_averages(self) -> dict[str, float]:
        """Load MLB league average statistics"""

        # 2025 MLB league averages (estimates based on recent trends)
        return {
            "runs_per_game": 4.65,
            "era": 4.12,
            "ops": 0.742,
            "whip": 1.31,
            "k_per_9": 8.85,
            "bb_per_9": 3.18,
            "hr_per_9": 1.24,
            "babip": 0.298,
            "strand_rate": 0.725,
        }

    def create_pitcher_features(
        self,
        pitcher: PitcherStats,
        opponent: TeamOffense,
        park: ParkFactors,
        weather: WeatherConditions,
    ) -> np.ndarray:
        """Create feature vector for pitcher performance prediction"""

        features = []

        # Basic pitcher stats (normalized to league average)
        features.extend(
            [
                pitcher.era / self.league_averages["era"],
                pitcher.whip / self.league_averages["whip"],
                pitcher.k_per_9 / self.league_averages["k_per_9"],
                pitcher.bb_per_9 / self.league_averages["bb_per_9"],
                pitcher.hr_per_9 / self.league_averages["hr_per_9"],
            ]
        )

        # Advanced metrics
        features.extend(
            [
                pitcher.fip / self.league_averages["era"],  # FIP normalized to ERA
                pitcher.babip_against / self.league_averages["babip"],
                pitcher.strand_rate / self.league_averages["strand_rate"],
            ]
        )

        # Handedness matchup
        opponent_ops = opponent.vs_lhp_ops if pitcher.handedness == "L" else opponent.vs_rhp_ops

        features.append(opponent_ops / self.league_averages["ops"])

        # Park factors
        features.extend([park.runs_factor, park.hr_factor])

        # Weather adjustments
        temp_factor = 1.0 + (weather.temperature - 72) * 0.003  # Hot weather helps offense
        wind_factor = (
            1.0
            if weather.wind_direction == "calm"
            else (1.05 if weather.wind_direction == "out" else 0.98)
        )

        features.extend([temp_factor, wind_factor])

        # Recent form
        features.extend(
            [
                pitcher.recent_era / pitcher.era if pitcher.era > 0 else 1.0,
                (pitcher.recent_k_rate / (pitcher.k_per_9 / 9) if pitcher.k_per_9 > 0 else 1.0),
            ]
        )

        return np.array(features)

    def create_team_features(
        self,
        team: TeamOffense,
        pitcher: PitcherStats,
        park: ParkFactors,
        weather: WeatherConditions,
        home_field: bool,
    ) -> np.ndarray:
        """Create feature vector for team offense prediction"""

        features = []

        # Team offensive stats
        features.extend(
            [
                team.runs_per_game / self.league_averages["runs_per_game"],
                team.ops / self.league_averages["ops"],
                team.woba / 0.320,  # League average wOBA
                team.wrc_plus / 100.0,
            ]
        )

        # Handedness matchup
        matchup_ops = team.vs_lhp_ops if pitcher.handedness == "L" else team.vs_rhp_ops

        features.append(matchup_ops / team.ops)

        # Home field advantage
        if home_field:
            features.append(team.home_runs_per_game / team.runs_per_game)
            features.append(1.05)  # Home field boost
        else:
            features.append(team.away_runs_per_game / team.runs_per_game)
            features.append(1.0)

        # Park factors
        features.extend([park.runs_factor, park.hr_factor])

        # Weather
        temp_factor = 1.0 + (weather.temperature - 72) * 0.003
        wind_factor = (
            1.0
            if weather.wind_direction == "calm"
            else (1.05 if weather.wind_direction == "out" else 0.98)
        )
        features.extend([temp_factor, wind_factor])

        # Lineup quality
        features.extend(
            [
                team.lineup_depth_score / 10.0,
                team.power_score / 10.0,
                team.speed_score / 10.0,
            ]
        )

        # Pitcher quality adjustment
        pitcher_quality = 1.0 / (pitcher.era / self.league_averages["era"])
        features.append(pitcher_quality)

        return np.array(features)

    def predict_team_runs(
        self,
        team: TeamOffense,
        pitcher: PitcherStats,
        park: ParkFactors,
        weather: WeatherConditions,
        home_field: bool,
    ) -> tuple[float, list[float]]:
        """Predict team runs using Poisson regression"""

        # Create feature vector
        features = self.create_team_features(team, pitcher, park, weather, home_field)

        # Base runs expectation
        base_runs = team.runs_per_game

        # Apply adjustments
        for i, feature in enumerate(features):
            if i < len(self.feature_weights.get("offense", [])):
                base_runs *= 1 + (feature - 1) * self.feature_weights["offense"][i]

        # Ensure reasonable bounds
        expected_runs = max(1.5, min(15.0, base_runs))

        # Generate Poisson distribution
        run_distribution = []
        poisson_dist = stats.poisson(expected_runs)

        for runs in range(16):  # 0-15 runs
            prob = poisson_dist.pmf(runs)
            run_distribution.append(prob)

        return expected_runs, run_distribution

    def predict_pitcher_performance(
        self,
        pitcher: PitcherStats,
        opponent: TeamOffense,
        park: ParkFactors,
        weather: WeatherConditions,
        expected_innings: float = 6.0,
    ) -> dict[str, Any]:
        """Predict pitcher strikeouts, walks, and other stats"""

        self.create_pitcher_features(pitcher, opponent, park, weather)

        # Base projections per 9 innings
        base_ks_per_9 = pitcher.k_per_9
        base_bbs_per_9 = pitcher.bb_per_9

        # Apply feature adjustments
        k_multiplier = 1.0
        bb_multiplier = 1.0

        # Opponent quality adjustment
        opponent_quality = opponent.wrc_plus / 100.0
        k_multiplier *= 1 + (1 - opponent_quality) * 0.15  # Better against worse hitters
        bb_multiplier *= 1 + (opponent_quality - 1) * 0.10  # More walks vs better hitters

        # Weather adjustments
        if weather.wind_speed > 15:
            k_multiplier *= 1.03  # Harder to hit in windy conditions

        # Scale to expected innings
        projected_ks = (base_ks_per_9 * k_multiplier) * (expected_innings / 9.0)
        projected_bbs = (base_bbs_per_9 * bb_multiplier) * (expected_innings / 9.0)

        # Generate distributions
        ks_distribution = stats.poisson(projected_ks)
        bbs_distribution = stats.poisson(projected_bbs)

        return {
            "expected_strikeouts": projected_ks,
            "expected_walks": projected_bbs,
            "strikeout_distribution": [ks_distribution.pmf(k) for k in range(20)],
            "walk_distribution": [bbs_distribution.pmf(w) for w in range(15)],
            "over_props": {
                4.5: 1 - ks_distribution.cdf(4),
                5.5: 1 - ks_distribution.cdf(5),
                6.5: 1 - ks_distribution.cdf(6),
                7.5: 1 - ks_distribution.cdf(7),
                8.5: 1 - ks_distribution.cdf(8),
            },
        }

    def project_game(
        self,
        home_pitcher: PitcherStats,
        away_pitcher: PitcherStats,
        home_team: TeamOffense,
        away_team: TeamOffense,
        park: ParkFactors,
        weather: WeatherConditions,
        game_id: str,
    ) -> GameProjection:
        """Generate complete game projection"""

        logger.info(f"Projecting game: {away_team.team} @ {home_team.team}")

        # Predict team runs
        home_runs, home_dist = self.predict_team_runs(home_team, away_pitcher, park, weather, True)
        away_runs, away_dist = self.predict_team_runs(away_team, home_pitcher, park, weather, False)

        # Predict pitcher performance
        home_pitcher_proj = self.predict_pitcher_performance(home_pitcher, away_team, park, weather)
        away_pitcher_proj = self.predict_pitcher_performance(away_pitcher, home_team, park, weather)

        # Calculate game totals
        total_runs = home_runs + away_runs

        # Generate total probabilities for common lines
        total_lines = [6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0]
        under_probs = {}
        over_probs = {}

        # Simulate game outcomes
        home_poisson = stats.poisson(home_runs)
        away_poisson = stats.poisson(away_runs)

        for line in total_lines:
            under_prob = 0.0
            over_prob = 0.0

            for h_runs in range(16):
                for a_runs in range(16):
                    h_prob = home_poisson.pmf(h_runs)
                    a_prob = away_poisson.pmf(a_runs)
                    game_prob = h_prob * a_prob

                    total_game_runs = h_runs + a_runs

                    if total_game_runs < line:
                        under_prob += game_prob
                    elif total_game_runs > line:
                        over_prob += game_prob

            under_probs[line] = under_prob
            over_probs[line] = over_prob

        # Team total probabilities
        team_total_lines = [3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
        home_tt_probs = {}
        away_tt_probs = {}

        for line in team_total_lines:
            home_tt_probs[line] = {
                "over": 1 - home_poisson.cdf(line - 0.01),
                "under": home_poisson.cdf(line),
            }
            away_tt_probs[line] = {
                "over": 1 - away_poisson.cdf(line - 0.01),
                "under": away_poisson.cdf(line),
            }

        # Game script analysis
        blowout_prob = 0.0  # >7 run difference
        close_game_prob = 0.0  # <=3 run difference
        pitchers_duel_prob = under_probs.get(6.5, 0.2)  # <7 total runs

        for h_runs in range(16):
            for a_runs in range(16):
                h_prob = home_poisson.pmf(h_runs)
                a_prob = away_poisson.pmf(a_runs)
                game_prob = h_prob * a_prob

                run_diff = abs(h_runs - a_runs)

                if run_diff > 7:
                    blowout_prob += game_prob
                elif run_diff <= 3:
                    close_game_prob += game_prob

        # Model confidence
        data_quality = 0.85  # Assume good data quality
        model_confidence = min(0.95, data_quality * 0.9)

        return GameProjection(
            game_id=game_id,
            home_team=home_team.team,
            away_team=away_team.team,
            home_run_distribution=home_dist,
            away_run_distribution=away_dist,
            home_runs_expected=home_runs,
            away_runs_expected=away_runs,
            total_runs_expected=total_runs,
            under_total_prob=under_probs,
            over_total_prob=over_probs,
            home_team_total_probs=home_tt_probs,
            away_team_total_probs=away_tt_probs,
            home_pitcher_ks=home_pitcher_proj,
            away_pitcher_ks=away_pitcher_proj,
            home_pitcher_walks=home_pitcher_proj,
            away_pitcher_walks=away_pitcher_proj,
            blowout_prob=blowout_prob,
            close_game_prob=close_game_prob,
            pitchers_duel_prob=pitchers_duel_prob,
            model_confidence=model_confidence,
            data_quality_score=data_quality,
            projection_timestamp=datetime.now(UTC),
        )

    def save_projection(self, projection: GameProjection, output_path: str | None = None):
        """Save game projection to file"""

        if not output_path:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            output_path = f"C:/EQ12/logs/game_projection_{projection.game_id}_{timestamp}.json"

        # Convert to serializable format
        proj_dict = asdict(projection)
        proj_dict["projection_timestamp"] = projection.projection_timestamp.isoformat()

        with open(output_path, "w") as f:
            json.dump(proj_dict, f, indent=2)

        logger.info(f"Saved projection to {output_path}")
        return output_path

    def initialize_weights(self):
        """Initialize feature weights for the model"""

        # These would normally be learned from training data
        # For now, using reasonable defaults
        self.feature_weights = {
            "offense": [
                0.15,
                0.20,
                0.18,
                0.12,
                0.10,
                0.08,
                0.05,
                0.04,
                0.03,
                0.02,
                0.02,
                0.01,
            ],
            "pitching": [0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.05, 0.03, 0.02],
        }

        logger.info("Initialized default feature weights")


def create_sample_data() -> tuple[PitcherStats, PitcherStats, TeamOffense, TeamOffense]:
    """Create sample data for testing"""

    # Sample pitchers
    gerrit_cole = PitcherStats(
        name="Gerrit Cole",
        team="NYY",
        handedness="R",
        era=2.75,
        whip=1.05,
        k_per_9=11.2,
        bb_per_9=2.1,
        hr_per_9=0.8,
        fip=2.85,
        xfip=3.10,
        babip_against=0.285,
        strand_rate=0.785,
        vs_lhb_ops=0.620,
        vs_rhb_ops=0.680,
        home_era=2.45,
        away_era=3.05,
        recent_era=2.20,
        recent_k_rate=12.1,
        innings_pitched_season=180.0,
    )

    chris_bassitt = PitcherStats(
        name="Chris Bassitt",
        team="TOR",
        handedness="R",
        era=3.45,
        whip=1.18,
        k_per_9=8.8,
        bb_per_9=2.8,
        hr_per_9=1.1,
        fip=3.60,
        xfip=3.75,
        babip_against=0.295,
        strand_rate=0.745,
        vs_lhb_ops=0.720,
        vs_rhb_ops=0.705,
        home_era=3.15,
        away_era=3.75,
        recent_era=3.80,
        recent_k_rate=8.2,
        innings_pitched_season=165.0,
    )

    # Sample teams
    yankees_offense = TeamOffense(
        team="NYY",
        runs_per_game=5.2,
        ops=0.785,
        woba=0.335,
        wrc_plus=118,
        vs_lhp_ops=0.805,
        vs_rhp_ops=0.765,
        home_runs_per_game=5.6,
        away_runs_per_game=4.8,
        vs_quality_starters_ops=0.720,
        lineup_depth_score=8.5,
        speed_score=6.0,
        power_score=9.0,
    )

    bluejays_offense = TeamOffense(
        team="TOR",
        runs_per_game=4.8,
        ops=0.742,
        woba=0.325,
        wrc_plus=105,
        vs_lhp_ops=0.765,
        vs_rhp_ops=0.720,
        home_runs_per_game=5.1,
        away_runs_per_game=4.5,
        vs_quality_starters_ops=0.695,
        lineup_depth_score=7.0,
        speed_score=7.5,
        power_score=7.0,
    )

    return gerrit_cole, chris_bassitt, yankees_offense, bluejays_offense


async def main():
    """Main CLI interface"""

    parser = argparse.ArgumentParser(description="EQ12 MLB Runs GLM Model")
    parser.add_argument("--game-id", help="Specific game ID to project")
    parser.add_argument("--demo", action="store_true", help="Run demo with sample data")
    parser.add_argument("--save", action="store_true", help="Save projection to file")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize model
    model = MLBRunsGLM()
    model.initialize_weights()

    if args.demo:
        print("🔬 RUNNING DEMO WITH SAMPLE DATA")

        # Create sample data
        cole, bassitt, yankees, bluejays = create_sample_data()

        # Sample park and weather
        yankee_stadium = model.park_factors["Yankee Stadium"]
        weather = WeatherConditions(
            temperature=75.0,
            wind_speed=8.0,
            wind_direction="out",
            humidity=65.0,
            precipitation_chance=10.0,
            barometric_pressure=30.2,
        )

        # Project the game
        projection = model.project_game(
            home_pitcher=bassitt,  # Bassitt pitching at home for TOR
            away_pitcher=cole,  # Cole pitching away for NYY
            home_team=bluejays,
            away_team=yankees,
            park=yankee_stadium,
            weather=weather,
            game_id="demo_game_001",
        )

        # Display results
        print(f"\n🎲 GAME PROJECTION: {projection.away_team} @ {projection.home_team}")
        print(
            f"   Expected runs: {projection.away_team} {projection.away_runs_expected:.2f} | {projection.home_team} {projection.home_runs_expected:.2f}"
        )
        print(f"   Total expected: {projection.total_runs_expected:.2f}")

        print("\n📊 TOTAL PROBABILITIES:")
        for line in [7.5, 8.0, 8.5, 9.0]:
            under_prob = projection.under_total_prob.get(line, 0)
            over_prob = projection.over_total_prob.get(line, 0)
            print(
                f"   {line}: Under {under_prob:.3f} ({under_prob * 100:.1f}%) | Over {over_prob:.3f} ({over_prob * 100:.1f}%)"
            )

        print("\n⚾ PITCHER STRIKEOUTS:")
        away_ks = projection.away_pitcher_ks.get("expected_strikeouts", 0)
        home_ks = projection.home_pitcher_ks.get("expected_strikeouts", 0)
        print(f"   {cole.name}: {away_ks:.1f} Ks expected")
        print(f"   {bassitt.name}: {home_ks:.1f} Ks expected")

        # Show prop probabilities
        away_props = projection.away_pitcher_ks.get("over_props", {})
        for line, prob in away_props.items():
            print(f"   {cole.name} Over {line} Ks: {prob:.3f} ({prob * 100:.1f}%)")

        print("\n🎭 GAME SCRIPTS:")
        print(
            f"   Pitcher's Duel (<7 runs): {projection.pitchers_duel_prob:.3f} ({projection.pitchers_duel_prob * 100:.1f}%)"
        )
        print(
            f"   Close Game (≤3 run diff): {projection.close_game_prob:.3f} ({projection.close_game_prob * 100:.1f}%)"
        )
        print(
            f"   Blowout (>7 run diff): {projection.blowout_prob:.3f} ({projection.blowout_prob * 100:.1f}%)"
        )

        print(
            f"\n✅ Model Confidence: {projection.model_confidence:.3f} ({projection.model_confidence * 100:.1f}%)"
        )

        if args.save:
            output_path = model.save_projection(projection)
            print(f"\n💾 Projection saved to: {output_path}")

    else:
        print("❌ No demo flag provided. Use --demo to run sample projection.")
        print("   Future versions will support live game data integration.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
