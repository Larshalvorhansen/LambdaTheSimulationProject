# g7_abm_game_theory.py

import numpy as np
import pandas as pd
import sqlite3
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import matplotlib.pyplot as plt
import seaborn as sns


class Strategy(Enum):
    COOPERATE = "cooperate"
    DEFECT = "defect"
    COMPROMISE = "compromise"
    AGGRESSIVE = "aggressive"


@dataclass
class AgentState:
    """Represents the current state of an agent"""

    position: float  # Current policy position (0-1 scale)
    satisfaction: float  # Satisfaction level
    power: float  # Influence/power level
    resources: float  # Available resources


@dataclass
class AgentParameters:
    """Parameters Z, X, C for each agent from SQL"""

    Z: Dict[str, float]  # Strategic parameters
    X: Dict[str, float]  # Preference parameters
    C: Dict[str, float]  # Constraint parameters


class G7Agent:
    """Individual G7 country agent with behavioral model"""

    def __init__(self, name: str, params: AgentParameters, initial_state: AgentState):
        self.name = name
        self.params = params
        self.state = initial_state
        self.history = []
        self.relationships = {}  # Bilateral relationship scores

    def calculate_utility(
        self, own_action: float, other_actions: Dict[str, float]
    ) -> float:
        """
        Calculate utility based on own action and others' actions
        This is where the behavioral model from the figure would be implemented
        """
        # Base utility from own position
        utility = self.params.X.get("preference_weight", 1.0) * own_action

        # Strategic interaction term (Z parameters)
        strategic_value = 0
        for other_name, other_action in other_actions.items():
            cooperation_benefit = self.params.Z.get(f"cooperation_{other_name}", 0.5)
            strategic_value += cooperation_benefit * (
                1 - abs(own_action - other_action)
            )

        # Constraint penalties (C parameters)
        constraint_penalty = 0
        for constraint_name, constraint_value in self.params.C.items():
            if "min" in constraint_name:
                constraint_penalty += max(0, constraint_value - own_action) ** 2
            elif "max" in constraint_name:
                constraint_penalty += max(0, own_action - constraint_value) ** 2

        total_utility = utility + strategic_value - constraint_penalty
        return total_utility

    def choose_action(
        self, others_actions: Dict[str, float], learning_rate: float = 0.1
    ) -> float:
        """
        Choose action based on behavioral model
        Implements best response dynamics with learning
        """
        # Grid search for best response
        action_space = np.linspace(0, 1, 20)
        best_action = self.state.position
        best_utility = float("-inf")

        for action in action_space:
            utility = self.calculate_utility(action, others_actions)
            if utility > best_utility:
                best_utility = utility
                best_action = action

        # Gradual adjustment (bounded rationality)
        new_position = (
            self.state.position * (1 - learning_rate) + best_action * learning_rate
        )

        return new_position

    def update_state(self, new_position: float, round_outcome: Dict):
        """Update agent state after a round"""
        self.state.position = new_position
        self.state.satisfaction = round_outcome.get("satisfaction", 0.5)
        self.history.append(
            {
                "position": new_position,
                "satisfaction": self.state.satisfaction,
                "power": self.state.power,
            }
        )

    def update_relationships(self, other_name: str, interaction_outcome: float):
        """Update bilateral relationships based on interactions"""
        if other_name not in self.relationships:
            self.relationships[other_name] = 0.5

        # Exponential moving average
        alpha = 0.3
        self.relationships[other_name] = (
            alpha * interaction_outcome + (1 - alpha) * self.relationships[other_name]
        )


class G7Summit:
    """Main simulation environment for G7 summit"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.agents: Dict[str, G7Agent] = {}
        self.history = []
        self.load_parameters()

    def load_parameters(self):
        """Load Z, X, C parameters from SQL database"""
        conn = sqlite3.connect(self.db_path)

        countries = [
            "Canada",
            "France",
            "Germany",
            "Italy",
            "Japan",
            "United Kingdom",
            "United States",
        ]

        for country in countries:
            # Load Z parameters
            z_query = f"SELECT * FROM z_parameters WHERE country = '{country}'"
            z_df = pd.read_sql_query(z_query, conn)
            Z = dict(zip(z_df["parameter_name"], z_df["value"]))

            # Load X parameters
            x_query = f"SELECT * FROM x_parameters WHERE country = '{country}'"
            x_df = pd.read_sql_query(x_query, conn)
            X = dict(zip(x_df["parameter_name"], x_df["value"]))

            # Load C parameters
            c_query = f"SELECT * FROM c_parameters WHERE country = '{country}'"
            c_df = pd.read_sql_query(c_query, conn)
            C = dict(zip(c_df["parameter_name"], c_df["value"]))

            params = AgentParameters(Z=Z, X=X, C=C)

            # Initialize agent state
            initial_state = AgentState(
                position=X.get("initial_position", 0.5),
                satisfaction=0.5,
                power=Z.get("power", 1.0),
                resources=1.0,
            )

            self.agents[country] = G7Agent(country, params, initial_state)

        conn.close()

    def run_negotiation_round(self, round_num: int) -> Dict:
        """Execute one round of negotiation"""
        # Get current positions
        current_positions = {
            name: agent.state.position for name, agent in self.agents.items()
        }

        # Each agent chooses new action
        new_positions = {}
        for name, agent in self.agents.items():
            others_positions = {k: v for k, v in current_positions.items() if k != name}
            new_positions[name] = agent.choose_action(others_positions)

        # Calculate outcomes
        round_outcome = self.calculate_round_outcome(new_positions)

        # Update all agents
        for name, agent in self.agents.items():
            agent.update_state(new_positions[name], round_outcome[name])

            # Update relationships
            for other_name in self.agents.keys():
                if other_name != name:
                    interaction = self.calculate_bilateral_outcome(
                        new_positions[name], new_positions[other_name]
                    )
                    agent.update_relationships(other_name, interaction)

        # Record history
        self.history.append(
            {
                "round": round_num,
                "positions": new_positions.copy(),
                "outcomes": round_outcome,
            }
        )

        return round_outcome

    def calculate_round_outcome(self, positions: Dict[str, float]) -> Dict:
        """Calculate outcomes for all agents"""
        outcomes = {}
        for name, agent in self.agents.items():
            others_positions = {k: v for k, v in positions.items() if k != name}
            utility = agent.calculate_utility(positions[name], others_positions)

            outcomes[name] = {
                "utility": utility,
                "satisfaction": 1 / (1 + np.exp(-utility)),  # Sigmoid
            }
        return outcomes

    def calculate_bilateral_outcome(self, pos1: float, pos2: float) -> float:
        """Calculate bilateral interaction outcome"""
        # Closer positions = better relationship
        return 1 - abs(pos1 - pos2)

    def check_convergence(self, threshold: float = 0.01) -> bool:
        """Check if positions have converged"""
        if len(self.history) < 2:
            return False

        prev_positions = self.history[-2]["positions"]
        curr_positions = self.history[-1]["positions"]

        max_change = max(
            abs(curr_positions[name] - prev_positions[name])
            for name in self.agents.keys()
        )

        return max_change < threshold

    def run_summit(
        self, max_rounds: int = 50, convergence_threshold: float = 0.01
    ) -> pd.DataFrame:
        """Run full summit simulation"""
        print(f"Starting G7 Summit simulation with {len(self.agents)} agents")

        for round_num in range(max_rounds):
            outcome = self.run_negotiation_round(round_num)

            if round_num % 10 == 0:
                avg_satisfaction = np.mean(
                    [o["satisfaction"] for o in outcome.values()]
                )
                print(f"Round {round_num}: Avg satisfaction = {avg_satisfaction:.3f}")

            if self.check_convergence(convergence_threshold):
                print(f"Converged at round {round_num}")
                break

        return self.get_results_dataframe()

    def get_results_dataframe(self) -> pd.DataFrame:
        """Convert history to pandas DataFrame"""
        records = []
        for h in self.history:
            for country, position in h["positions"].items():
                records.append(
                    {
                        "round": h["round"],
                        "country": country,
                        "position": position,
                        "utility": h["outcomes"][country]["utility"],
                        "satisfaction": h["outcomes"][country]["satisfaction"],
                    }
                )
        return pd.DataFrame(records)

    def plot_results(self):
        """Visualize simulation results"""
        df = self.get_results_dataframe()

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # Position evolution
        for country in self.agents.keys():
            country_data = df[df["country"] == country]
            axes[0, 0].plot(
                country_data["round"],
                country_data["position"],
                label=country,
                marker="o",
            )
        axes[0, 0].set_xlabel("Round")
        axes[0, 0].set_ylabel("Position")
        axes[0, 0].set_title("Policy Position Evolution")
        axes[0, 0].legend()
        axes[0, 0].grid(True)

        # Satisfaction evolution
        for country in self.agents.keys():
            country_data = df[df["country"] == country]
            axes[0, 1].plot(
                country_data["round"],
                country_data["satisfaction"],
                label=country,
                marker="s",
            )
        axes[0, 1].set_xlabel("Round")
        axes[0, 1].set_ylabel("Satisfaction")
        axes[0, 1].set_title("Satisfaction Evolution")
        axes[0, 1].legend()
        axes[0, 1].grid(True)

        # Final positions
        final_round = df["round"].max()
        final_data = df[df["round"] == final_round].sort_values("position")
        axes[1, 0].barh(final_data["country"], final_data["position"])
        axes[1, 0].set_xlabel("Final Position")
        axes[1, 0].set_title("Final Negotiation Positions")

        # Relationship heatmap
        relationship_matrix = np.zeros((len(self.agents), len(self.agents)))
        countries = list(self.agents.keys())
        for i, country1 in enumerate(countries):
            for j, country2 in enumerate(countries):
                if country1 != country2:
                    relationship_matrix[i, j] = self.agents[country1].relationships.get(
                        country2, 0.5
                    )
                else:
                    relationship_matrix[i, j] = 1.0

        sns.heatmap(
            relationship_matrix,
            annot=True,
            fmt=".2f",
            xticklabels=countries,
            yticklabels=countries,
            cmap="RdYlGn",
            ax=axes[1, 1],
            vmin=0,
            vmax=1,
        )
        axes[1, 1].set_title("Final Bilateral Relationships")

        plt.tight_layout()
        plt.savefig("g7_summit_results.png", dpi=300, bbox_inches="tight")
        plt.show()

    def analyze_coalitions(self) -> Dict:
        """Identify potential coalitions based on final positions"""
        final_positions = {
            name: agent.state.position for name, agent in self.agents.items()
        }

        # Hierarchical clustering of positions
        from scipy.cluster.hierarchy import linkage, fcluster
        from scipy.spatial.distance import pdist

        positions_array = np.array(list(final_positions.values())).reshape(-1, 1)
        distances = pdist(positions_array)
        linkage_matrix = linkage(distances, method="ward")
        clusters = fcluster(linkage_matrix, t=2, criterion="maxclust")

        coalitions = {}
        for idx, (country, cluster_id) in enumerate(
            zip(final_positions.keys(), clusters)
        ):
            if cluster_id not in coalitions:
                coalitions[cluster_id] = []
            coalitions[cluster_id].append(country)

        return coalitions


# Example usage and SQL setup
def create_example_database(db_path: str = "g7_parameters.db"):
    """Create example SQL database with Z, X, C parameters"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS z_parameters (
            country TEXT,
            parameter_name TEXT,
            value REAL
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS x_parameters (
            country TEXT,
            parameter_name TEXT,
            value REAL
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS c_parameters (
            country TEXT,
            parameter_name TEXT,
            value REAL
        )
    """
    )

    countries = [
        "Canada",
        "France",
        "Germany",
        "Italy",
        "Japan",
        "United Kingdom",
        "United States",
    ]

    # Example parameters (you'll replace these with actual values)
    for country in countries:
        # Z parameters (strategic factors)
        cursor.execute(
            "INSERT INTO z_parameters VALUES (?, ?, ?)",
            (country, "power", np.random.uniform(0.8, 1.2)),
        )

        for other_country in countries:
            if other_country != country:
                cursor.execute(
                    "INSERT INTO z_parameters VALUES (?, ?, ?)",
                    (
                        country,
                        f"cooperation_{other_country}",
                        np.random.uniform(0.3, 0.7),
                    ),
                )

        # X parameters (preferences)
        cursor.execute(
            "INSERT INTO x_parameters VALUES (?, ?, ?)",
            (country, "initial_position", np.random.uniform(0.3, 0.7)),
        )
        cursor.execute(
            "INSERT INTO x_parameters VALUES (?, ?, ?)",
            (country, "preference_weight", np.random.uniform(0.5, 1.5)),
        )

        # C parameters (constraints)
        cursor.execute(
            "INSERT INTO c_parameters VALUES (?, ?, ?)",
            (country, "min_acceptable", np.random.uniform(0.2, 0.4)),
        )
        cursor.execute(
            "INSERT INTO c_parameters VALUES (?, ?, ?)",
            (country, "max_acceptable", np.random.uniform(0.6, 0.8)),
        )

    conn.commit()
    conn.close()
    print(f"Database created at {db_path}")


if __name__ == "__main__":
    # Create example database
    create_example_database()

    # Initialize and run simulation
    summit = G7Summit("g7_parameters.db")
    results_df = summit.run_summit(max_rounds=50)

    # Analyze results
    print("\n=== Final Positions ===")
    final_positions = results_df[results_df["round"] == results_df["round"].max()]
    print(
        final_positions[["country", "position", "satisfaction"]].to_string(index=False)
    )

    print("\n=== Coalition Analysis ===")
    coalitions = summit.analyze_coalitions()
    for coalition_id, members in coalitions.items():
        print(f"Coalition {coalition_id}: {', '.join(members)}")

    # Visualize
    summit.plot_results()

    # Export results
    results_df.to_csv("g7_summit_results.csv", index=False)
    print("\nResults exported to g7_summit_results.csv")
