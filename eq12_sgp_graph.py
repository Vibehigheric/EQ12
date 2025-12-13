#!/usr/bin/env python3
"""
EQ12 GODSTACK - SGP Graph Builder
Represent legs as nodes; edges carry correlation/constraint weights.
Build valid combos (respect "mutually exclusive" & "too-tight" rules) and rank by EV/coherence.

Core Features:
- Graph-based SGP representation with legs as nodes
- Edge weights representing correlations and constraints
- Valid combination generator respecting DraftKings rules
- EV and coherence ranking of generated SGPs
- Constraint satisfaction for juice penalties
- Optimal leg selection algorithms
"""

import argparse
import itertools
import json
import logging
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/sgp_graph.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of nodes in the SGP graph"""

    MONEYLINE = "moneyline"
    TOTAL = "total"
    TEAM_TOTAL = "team_total"
    PLAYER_PROP = "player_prop"
    FIRST_FIVE = "first_five"
    ALTERNATIVE_LINE = "alt_line"


class EdgeConstraint(Enum):
    """Constraint types between SGP legs"""

    ALLOWED = "allowed"  # No restrictions
    CORRELATED_JUICE = "correlated_juice"  # Slight juice penalty
    HEAVY_JUICE = "heavy_juice"  # Significant juice penalty
    RESTRICTED = "restricted"  # High juice penalty
    MUTUALLY_EXCLUSIVE = "mutually_exclusive"  # Cannot combine


@dataclass
class SGPNode:
    """Node in the SGP graph representing a potential leg"""

    node_id: str
    node_type: NodeType

    # Leg details
    market: str  # e.g., "game_total", "player_strikeouts"
    selection: str  # "over", "under", "home", "away"
    line: float | None

    # Teams/players involved
    primary_team: str | None
    secondary_team: str | None
    player: str | None

    # Betting data
    offered_odds: int  # American format
    true_probability: float
    expected_value: float
    kelly_fraction: float

    # Graph properties
    correlation_category: str
    narrative_weight: float  # How much this leg contributes to story

    # Metadata
    confidence_score: float
    data_freshness: float  # how recent is the underlying data


@dataclass
class SGPEdge:
    """Edge between SGP nodes representing correlation/constraint"""

    edge_id: str
    from_node: str
    to_node: str

    # Correlation data
    correlation_coefficient: float  # -1 to 1
    correlation_strength: str  # "weak", "moderate", "strong"

    # DraftKings constraints
    constraint_type: EdgeConstraint
    juice_penalty: float  # Additional juice applied (0.0 to 1.0)

    # Narrative coherence
    narrative_synergy: float  # How well these legs work together in story

    # Context
    game_situation_modifier: float
    weather_modifier: float

    reasoning: str


@dataclass
class SGPPath:
    """A valid path through the SGP graph (complete SGP)"""

    path_id: str
    nodes: list[SGPNode]
    edges: list[SGPEdge]

    # Metrics
    combined_odds: int  # Final parlay odds
    total_expected_value: float
    coherence_score: float
    narrative_grade: str

    # Risk metrics
    correlation_risk: float
    variance_inflation: float
    kelly_sizing: float

    # DraftKings specific
    buildable_on_dk: bool
    estimated_juice_penalty: float

    # Rankings
    ev_rank: int
    coherence_rank: int
    combined_rank: int

    path_timestamp: datetime


class SGPGraphBuilder:
    """Main SGP graph construction and path-finding engine"""

    def __init__(self):
        self.nodes = {}  # node_id -> SGPNode
        self.edges = {}  # edge_id -> SGPEdge
        self.adjacency_list = defaultdict(list)  # node_id -> [connected_node_ids]

        # Path generation parameters
        self.max_legs = 6
        self.min_legs = 2
        self.max_paths_to_generate = 50

        # Ranking weights
        self.ev_weight = 0.4
        self.coherence_weight = 0.3
        self.buildability_weight = 0.2
        self.risk_weight = 0.1

        logger.info("SGPGraphBuilder initialized")

    def add_node(self, node: SGPNode):
        """Add a node (potential leg) to the graph"""

        self.nodes[node.node_id] = node
        logger.debug(f"Added node {node.node_id}: {node.market} {node.selection}")

    def add_edge(self, edge: SGPEdge):
        """Add an edge (correlation/constraint) between nodes"""

        if edge.from_node not in self.nodes or edge.to_node not in self.nodes:
            logger.warning(f"Edge {edge.edge_id} references non-existent nodes")
            return False

        self.edges[edge.edge_id] = edge
        self.adjacency_list[edge.from_node].append(edge.to_node)
        self.adjacency_list[edge.to_node].append(edge.from_node)  # Undirected graph

        logger.debug(f"Added edge {edge.edge_id}: {edge.from_node} ↔ {edge.to_node}")
        return True

    def build_graph_from_legs(
        self, available_legs: list[dict[str, Any]], correlations: list[dict[str, Any]]
    ):
        """Build the complete SGP graph from available legs and correlations"""

        logger.info(
            f"Building graph from {len(available_legs)} legs and {len(correlations)} correlations"
        )

        # Add all legs as nodes
        for i, leg in enumerate(available_legs):
            node = SGPNode(
                node_id=f"node_{i}",
                node_type=NodeType(leg.get("leg_type", "player_prop")),
                market=leg.get("market", "unknown"),
                selection=leg.get("selection", "over"),
                line=leg.get("line"),
                primary_team=leg.get("team"),
                secondary_team=leg.get("opposing_team"),
                player=leg.get("player"),
                offered_odds=leg.get("odds", 100),
                true_probability=leg.get("true_prob", 0.5),
                expected_value=leg.get("ev", 0.0),
                kelly_fraction=leg.get("kelly", 0.0),
                correlation_category=leg.get("category", "general"),
                narrative_weight=leg.get("narrative_weight", 1.0),
                confidence_score=leg.get("confidence", 0.8),
                data_freshness=leg.get("freshness", 0.9),
            )
            self.add_node(node)

        # Add correlations as edges
        edge_counter = 0
        for corr in correlations:
            from_idx = corr.get("leg1_index")
            to_idx = corr.get("leg2_index")

            if from_idx is not None and to_idx is not None:
                from_node_id = f"node_{from_idx}"
                to_node_id = f"node_{to_idx}"

                if from_node_id in self.nodes and to_node_id in self.nodes:
                    edge = SGPEdge(
                        edge_id=f"edge_{edge_counter}",
                        from_node=from_node_id,
                        to_node=to_node_id,
                        correlation_coefficient=corr.get("correlation", 0.0),
                        correlation_strength=corr.get("strength", "weak"),
                        constraint_type=EdgeConstraint(corr.get("constraint", "allowed")),
                        juice_penalty=corr.get("juice_penalty", 0.0),
                        narrative_synergy=corr.get("synergy", 0.5),
                        game_situation_modifier=corr.get("situation_mod", 0.0),
                        weather_modifier=corr.get("weather_mod", 0.0),
                        reasoning=corr.get("reasoning", "Unknown correlation"),
                    )
                    self.add_edge(edge)
                    edge_counter += 1

        logger.info(f"Graph built: {len(self.nodes)} nodes, {len(self.edges)} edges")

    def find_valid_paths(self, min_legs: int = 2, max_legs: int = 6) -> list[SGPPath]:
        """Find all valid SGP paths through the graph"""

        logger.info(f"Finding valid paths with {min_legs}-{max_legs} legs")

        valid_paths = []
        node_ids = list(self.nodes.keys())

        # Generate all possible combinations
        for path_length in range(min_legs, max_legs + 1):
            for node_combo in itertools.combinations(node_ids, path_length):
                # Check if this combination is valid
                if self._is_valid_combination(node_combo):
                    path = self._create_path_from_nodes(node_combo)
                    if path and path.buildable_on_dk:
                        valid_paths.append(path)

                        # Limit total paths generated
                        if len(valid_paths) >= self.max_paths_to_generate:
                            logger.info(f"Reached max paths limit: {self.max_paths_to_generate}")
                            return valid_paths[: self.max_paths_to_generate]

        logger.info(f"Generated {len(valid_paths)} valid paths")
        return valid_paths

    def _is_valid_combination(self, node_ids: tuple[str, ...]) -> bool:
        """Check if a combination of nodes forms a valid SGP"""

        nodes = [self.nodes[node_id] for node_id in node_ids]

        # Check for mutually exclusive constraints
        for i, node1 in enumerate(nodes):
            for _j, node2 in enumerate(nodes[i + 1 :], i + 1):
                edge = self._get_edge_between_nodes(node1.node_id, node2.node_id)
                if edge and edge.constraint_type == EdgeConstraint.MUTUALLY_EXCLUSIVE:
                    return False

        # Check for same market different lines (usually not allowed)
        markets_seen = defaultdict(list)
        for node in nodes:
            market_key = (node.market, node.primary_team, node.player)
            markets_seen[market_key].append(node)

        for market_nodes in markets_seen.values():
            if len(market_nodes) > 1:
                # Multiple legs on same market - check if allowed
                selections = [node.selection for node in market_nodes]
                if len(set(selections)) > 1:  # Different selections on same market
                    return False

        # Check for excessive same-player props
        player_props = defaultdict(int)
        for node in nodes:
            if node.node_type == NodeType.PLAYER_PROP and node.player:
                player_props[node.player] += 1

        return all(prop_count <= 3 for player, prop_count in player_props.items())

    def _get_edge_between_nodes(self, node1_id: str, node2_id: str) -> SGPEdge | None:
        """Get the edge between two nodes if it exists"""

        for edge in self.edges.values():
            if (edge.from_node == node1_id and edge.to_node == node2_id) or (
                edge.from_node == node2_id and edge.to_node == node1_id
            ):
                return edge

        return None

    def _create_path_from_nodes(self, node_ids: tuple[str, ...]) -> SGPPath | None:
        """Create an SGPPath object from a combination of nodes"""

        nodes = [self.nodes[node_id] for node_id in node_ids]

        # Collect edges between nodes
        path_edges = []
        total_juice_penalty = 0.0

        for i, node1 in enumerate(nodes):
            for node2 in nodes[i + 1 :]:
                edge = self._get_edge_between_nodes(node1.node_id, node2.node_id)
                if edge:
                    path_edges.append(edge)
                    total_juice_penalty += edge.juice_penalty

        # Calculate combined odds
        combined_prob = 1.0
        for node in nodes:
            combined_prob *= node.true_probability

        # Apply juice penalty
        adjusted_prob = combined_prob * (1 + total_juice_penalty)

        # Convert to American odds
        if adjusted_prob > 0.5:
            combined_odds = int(-100 / (1 / adjusted_prob - 1))
        else:
            combined_odds = int(100 * (1 / adjusted_prob - 1))

        # Calculate total EV
        total_ev = sum(node.expected_value for node in nodes)

        # Calculate coherence score
        coherence_score = self._calculate_path_coherence(nodes, path_edges)

        # Check DraftKings buildability
        buildable = self._check_dk_buildability(path_edges)

        # Calculate risk metrics
        correlation_risk = self._calculate_path_correlation_risk(path_edges)
        variance_inflation = self._calculate_path_variance_inflation(nodes, path_edges)

        # Kelly sizing
        kelly_sizing = min(0.05, sum(node.kelly_fraction for node in nodes) / len(nodes))

        path_id = f"path_{hash(node_ids) % 100000}"

        return SGPPath(
            path_id=path_id,
            nodes=nodes,
            edges=path_edges,
            combined_odds=combined_odds,
            total_expected_value=total_ev,
            coherence_score=coherence_score,
            narrative_grade=self._assign_narrative_grade(coherence_score),
            correlation_risk=correlation_risk,
            variance_inflation=variance_inflation,
            kelly_sizing=kelly_sizing,
            buildable_on_dk=buildable,
            estimated_juice_penalty=total_juice_penalty,
            ev_rank=0,  # Will be set during ranking
            coherence_rank=0,
            combined_rank=0,
            path_timestamp=datetime.now(UTC),
        )

    def _calculate_path_coherence(self, nodes: list[SGPNode], edges: list[SGPEdge]) -> float:
        """Calculate coherence score for a path"""

        if not edges:
            return 0.5  # Independent legs have medium coherence

        # Average narrative synergy
        avg_synergy = sum(edge.narrative_synergy for edge in edges) / len(edges)

        # Positive correlation bonus
        positive_correlations = [edge for edge in edges if edge.correlation_coefficient > 0]
        positive_bonus = len(positive_correlations) / len(edges) * 0.2

        # Team focus bonus
        teams = {node.primary_team for node in nodes if node.primary_team}
        team_focus_bonus = 0.15 if len(teams) <= 2 else -0.1

        coherence = avg_synergy + positive_bonus + team_focus_bonus
        return max(0.0, min(1.0, coherence))

    def _check_dk_buildability(self, edges: list[SGPEdge]) -> bool:
        """Check if path can be built on DraftKings"""

        # Any mutually exclusive edges = not buildable
        for edge in edges:
            if edge.constraint_type == EdgeConstraint.MUTUALLY_EXCLUSIVE:
                return False

        # Too many restricted edges = unlikely to be buildable
        restricted_count = sum(
            1 for edge in edges if edge.constraint_type == EdgeConstraint.RESTRICTED
        )
        return not restricted_count > len(edges) / 2

    def _calculate_path_correlation_risk(self, edges: list[SGPEdge]) -> float:
        """Calculate correlation risk for the path"""

        if not edges:
            return 0.0

        high_corr_count = sum(1 for edge in edges if abs(edge.correlation_coefficient) > 0.4)
        return high_corr_count / len(edges)

    def _calculate_path_variance_inflation(
        self, nodes: list[SGPNode], edges: list[SGPEdge]
    ) -> float:
        """Calculate variance inflation from correlations"""

        if len(nodes) < 2:
            return 1.0

        # Simplified VIF calculation
        avg_correlation = 0.0
        if edges:
            avg_correlation = sum(abs(edge.correlation_coefficient) for edge in edges) / len(edges)

        return 1.0 + avg_correlation * 1.5

    def _assign_narrative_grade(self, coherence_score: float) -> str:
        """Assign letter grade based on narrative coherence"""

        if coherence_score >= 0.9:
            return "A+"
        if coherence_score >= 0.85:
            return "A"
        if coherence_score >= 0.8:
            return "B+"
        if coherence_score >= 0.75:
            return "B"
        if coherence_score >= 0.7:
            return "C+"
        if coherence_score >= 0.6:
            return "C"
        return "D"

    def rank_paths(self, paths: list[SGPPath]) -> list[SGPPath]:
        """Rank paths by combined EV and coherence score"""

        if not paths:
            return []

        # Calculate individual rankings
        sorted_by_ev = sorted(paths, key=lambda p: p.total_expected_value, reverse=True)
        sorted_by_coherence = sorted(paths, key=lambda p: p.coherence_score, reverse=True)

        # Assign ranks
        for i, path in enumerate(sorted_by_ev):
            path.ev_rank = i + 1

        for i, path in enumerate(sorted_by_coherence):
            path.coherence_rank = i + 1

        # Calculate combined score
        for path in paths:
            ev_score = 1.0 - (path.ev_rank - 1) / len(paths)
            coherence_score = 1.0 - (path.coherence_rank - 1) / len(paths)
            buildability_score = 1.0 if path.buildable_on_dk else 0.3
            risk_score = 1.0 - path.correlation_risk

            combined_score = (
                ev_score * self.ev_weight
                + coherence_score * self.coherence_weight
                + buildability_score * self.buildability_weight
                + risk_score * self.risk_weight
            )

            path.combined_rank = combined_score

        # Sort by combined score
        ranked_paths = sorted(paths, key=lambda p: p.combined_rank, reverse=True)

        # Update combined ranks
        for i, path in enumerate(ranked_paths):
            path.combined_rank = i + 1

        logger.info(f"Ranked {len(paths)} paths")
        return ranked_paths

    def get_top_sgps(self, num_sgps: int = 5) -> list[SGPPath]:
        """Generate and return top SGPs"""

        logger.info(f"Generating top {num_sgps} SGPs")

        # Find all valid paths
        all_paths = self.find_valid_paths(self.min_legs, self.max_legs)

        if not all_paths:
            logger.warning("No valid paths found")
            return []

        # Rank paths
        ranked_paths = self.rank_paths(all_paths)

        # Return top N
        top_paths = ranked_paths[:num_sgps]

        logger.info(f"Returning top {len(top_paths)} SGPs")
        return top_paths

    def export_graph_analysis(self, output_path: str | None = None) -> str:
        """Export detailed graph analysis"""

        if not output_path:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            output_path = f"C:/EQ12/logs/sgp_graph_analysis_{timestamp}.json"

        analysis = {
            "graph_stats": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "avg_node_degree": (
                    sum(len(neighbors) for neighbors in self.adjacency_list.values())
                    / len(self.nodes)
                    if self.nodes
                    else 0
                ),
            },
            "nodes": [asdict(node) for node in self.nodes.values()],
            "edges": [asdict(edge) for edge in self.edges.values()],
            "analysis_timestamp": datetime.now(UTC).isoformat(),
        }

        with open(output_path, "w") as f:
            json.dump(analysis, f, indent=2, default=str)

        logger.info(f"Graph analysis exported to {output_path}")
        return output_path


def create_sample_graph_data():
    """Create sample data for testing the graph builder"""

    # Sample legs
    available_legs = [
        {
            "leg_type": "total",
            "market": "game_total",
            "selection": "under",
            "line": 8.0,
            "team": None,
            "odds": -110,
            "true_prob": 0.55,
            "ev": 0.05,
            "kelly": 0.02,
            "category": "totals",
            "narrative_weight": 0.8,
            "confidence": 0.85,
        },
        {
            "leg_type": "player_prop",
            "market": "pitcher_strikeouts",
            "selection": "over",
            "line": 6.5,
            "team": "NYY",
            "player": "Gerrit Cole",
            "odds": -115,
            "true_prob": 0.60,
            "ev": 0.08,
            "kelly": 0.03,
            "category": "pitching",
            "narrative_weight": 0.9,
            "confidence": 0.82,
        },
        {
            "leg_type": "player_prop",
            "market": "pitcher_strikeouts",
            "selection": "over",
            "line": 6.5,
            "team": "TOR",
            "player": "Chris Bassitt",
            "odds": -120,
            "true_prob": 0.58,
            "ev": 0.06,
            "kelly": 0.025,
            "category": "pitching",
            "narrative_weight": 0.85,
            "confidence": 0.80,
        },
        {
            "leg_type": "team_total",
            "market": "team_total",
            "selection": "under",
            "line": 4.5,
            "team": "TOR",
            "odds": +105,
            "true_prob": 0.52,
            "ev": 0.04,
            "kelly": 0.015,
            "category": "team_performance",
            "narrative_weight": 0.7,
            "confidence": 0.78,
        },
    ]

    # Sample correlations
    correlations = [
        {
            "leg1_index": 0,
            "leg2_index": 1,
            "correlation": 0.28,
            "strength": "moderate",
            "constraint": "usually_allowed",
            "juice_penalty": 0.02,
            "synergy": 0.8,
            "reasoning": "Pitcher strikeouts support game under",
        },
        {
            "leg1_index": 0,
            "leg2_index": 2,
            "correlation": 0.25,
            "strength": "moderate",
            "constraint": "usually_allowed",
            "juice_penalty": 0.02,
            "synergy": 0.75,
            "reasoning": "Both pitchers performing well supports low total",
        },
        {
            "leg1_index": 1,
            "leg2_index": 2,
            "correlation": 0.05,
            "strength": "weak",
            "constraint": "allowed",
            "juice_penalty": 0.0,
            "synergy": 0.6,
            "reasoning": "Opposing pitchers largely independent",
        },
        {
            "leg1_index": 0,
            "leg2_index": 3,
            "correlation": 0.35,
            "strength": "moderate",
            "constraint": "allowed",
            "juice_penalty": 0.01,
            "synergy": 0.7,
            "reasoning": "Game under correlates with team under",
        },
    ]

    return available_legs, correlations


async def main():
    """Main CLI interface"""

    parser = argparse.ArgumentParser(description="EQ12 SGP Graph Builder")
    parser.add_argument("--demo", action="store_true", help="Run demo with sample data")
    parser.add_argument("--num-sgps", type=int, default=5, help="Number of top SGPs to generate")
    parser.add_argument("--export", action="store_true", help="Export graph analysis")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize graph builder
    builder = SGPGraphBuilder()

    if args.demo:
        print("📊 RUNNING SGP GRAPH BUILDER DEMO")

        # Create sample data
        legs, correlations = create_sample_graph_data()

        # Build graph
        builder.build_graph_from_legs(legs, correlations)

        # Generate top SGPs
        top_sgps = builder.get_top_sgps(args.num_sgps)

        # Display results
        print(f"\n🏆 TOP {len(top_sgps)} SGPs GENERATED:")

        for i, sgp in enumerate(top_sgps, 1):
            print(f"\n{i}. SGP #{sgp.path_id}")
            print(f"   Combined Odds: {sgp.combined_odds:+d}")
            print(f"   Expected Value: {sgp.total_expected_value:.4f}")
            print(f"   Coherence: {sgp.coherence_score:.3f} (Grade: {sgp.narrative_grade})")
            print(f"   DK Buildable: {'✅' if sgp.buildable_on_dk else '❌'}")
            print(f"   Kelly Size: {sgp.kelly_sizing:.3f}")

            print("   Legs:")
            for leg in sgp.nodes:
                odds_str = (
                    f"{leg.offered_odds:+d}" if leg.offered_odds >= 0 else str(leg.offered_odds)
                )
                player_str = f" ({leg.player})" if leg.player else ""
                team_str = f" [{leg.primary_team}]" if leg.primary_team else ""
                print(
                    f"      • {leg.market} {leg.selection} {leg.line}{player_str}{team_str} ({odds_str})"
                )

            if sgp.edges:
                print("   Correlations:")
                for edge in sgp.edges:
                    print(
                        f"      • {edge.correlation_coefficient:+.3f} ({edge.constraint_type.value})"
                    )

        # Graph statistics
        print("\n📈 GRAPH STATISTICS:")
        print(f"   Total nodes: {len(builder.nodes)}")
        print(f"   Total edges: {len(builder.edges)}")
        print(f"   Valid paths found: {len(top_sgps)}")

        if args.export:
            export_path = builder.export_graph_analysis()
            print(f"\n💾 Graph analysis exported to: {export_path}")

    else:
        print("❌ Use --demo to run SGP graph builder demo")
        print("   Future versions will integrate with live odds data")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
