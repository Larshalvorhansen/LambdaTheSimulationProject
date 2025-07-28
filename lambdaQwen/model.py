# model.py
import random
import numpy as np


class Country:
    """
    Represents a country agent in the simulation.
    """

    def __init__(
        self, unique_id, model, initial_gdp, initial_debt, trade_partners=None
    ):
        self.unique_id = unique_id
        self.model = model
        self.gdp = initial_gdp
        self.debt = initial_debt
        self.trade_partners = trade_partners if trade_partners is not None else []
        self.gdp_growth_rate = 0.0
        self.policy_rate = 0.05  # Initial policy interest rate

    def step(self):
        """
        Defines the agent's behavior at each step.
        """
        # --- Simplified Economic Logic ---
        shock = random.uniform(-0.02, 0.02)

        debt_to_gdp = self.debt / self.gdp if self.gdp > 0 else 0
        debt_impact = -0.01 * max(0, debt_to_gdp - 0.6)

        partner_growth = 0.0
        if self.trade_partners:
            partner_growths = [
                p.gdp_growth_rate for p in self.trade_partners if p != self
            ]
            if partner_growths:
                partner_growth = np.mean(partner_growths) * 0.3

        self.gdp_growth_rate = shock + debt_impact + partner_growth + 0.02

        self.gdp *= 1 + self.gdp_growth_rate

        interest_payment = self.debt * self.policy_rate
        primary_balance = 0.02 * self.gdp
        self.debt = self.debt + interest_payment - primary_balance

        # --- Simple Policy Reaction Function ---
        if self.gdp_growth_rate > 0.03:
            self.policy_rate = max(0.01, self.policy_rate - 0.005)
        elif self.gdp_growth_rate < 0.01:
            self.policy_rate = min(0.15, self.policy_rate + 0.005)

        if debt_to_gdp > 0.8:
            self.policy_rate = min(0.20, self.policy_rate + 0.01)


class LambdaSimModel:
    """
    The main model that contains the countries and runs the simulation.
    """

    def __init__(self, num_countries=5, initial_connections=2):
        self.num_countries = num_countries
        self.schedule = []
        # Store data for plotting
        self.datacollector = {
            "Step": [],
            "Total_GDP": [],
            "Total_Debt": [],
            "Avg_Growth": [],
            # Optional: Store individual country data
            # "Country_GDPs": {i: [] for i in range(num_countries)},
            # "Country_Debts": {i: [] for i in range(num_countries)},
        }
        self.create_countries()
        self.create_initial_connections(initial_connections)

    def create_countries(self):
        """Initializes country agents."""
        for i in range(self.num_countries):
            initial_gdp = random.uniform(1000, 5000)
            initial_debt = random.uniform(200, 1500)
            country = Country(i, self, initial_gdp, initial_debt)
            self.schedule.append(country)

    def create_initial_connections(self, initial_connections):
        """Creates initial random trade relationships."""
        for country in self.schedule:
            potential_partners = [c for c in self.schedule if c != country]
            if len(potential_partners) >= initial_connections:
                country.trade_partners = random.sample(
                    potential_partners, initial_connections
                )
            else:
                country.trade_partners = potential_partners

    def step(self):
        """
        Executes one step of the model.
        """
        # Collect data before the agents act
        current_step = len(self.datacollector["Step"])  # Steps are 0-indexed
        self.datacollector["Step"].append(current_step)

        total_gdp = sum(c.gdp for c in self.schedule)
        total_debt = sum(c.debt for c in self.schedule)
        avg_growth = (
            np.mean([c.gdp_growth_rate for c in self.schedule]) if self.schedule else 0
        )

        self.datacollector["Total_GDP"].append(total_gdp)
        self.datacollector["Total_Debt"].append(total_debt)
        self.datacollector["Avg_Growth"].append(avg_growth)

        # Optional: Collect individual data
        # for country in self.schedule:
        #     self.datacollector["Country_GDPs"][country.unique_id].append(country.gdp)
        #     self.datacollector["Country_Debts"][country.unique_id].append(country.debt)

        # Activate all agents
        for country in self.schedule:
            country.step()

    def run_simulation(self, steps):
        """Runs the simulation for a given number of steps."""
        print(
            f"Starting simulation with {self.num_countries} countries for {steps} steps."
        )
        for _ in range(steps):
            self.step()
        print("Simulation finished.")
        # Append final state data point if needed for plotting continuity
        # (Not strictly necessary as step() is called 'steps' times)
        print(f"Final Total GDP: {self.datacollector['Total_GDP'][-1]:.2f}")
        print(f"Final Total Debt: {self.datacollector['Total_Debt'][-1]:.2f}")
        print(
            f"Average Growth Rate in Final Step: {self.datacollector['Avg_Growth'][-1]:.4f}"
        )
