import numpy as np
import sqlite3

# Note: Z, X, C are supposed to be defined in a separate SQL file.
# Assuming the SQL file creates a database with tables for Z (country characteristics like GDP per capita),
# X (attributes of alternatives), and C (context for each country).
# For example, you can run the SQL script to create 'g7.db', then query.
# Here, since no file is attached, we use hard-coded values based on real data.

# If you have the SQL file, you can load like this:
# conn = sqlite3.connect('g7.db')
# z_df = pd.import pandas as pd  # if using pandas
# z = pd.read_sql_query("SELECT * FROM Z", conn)['gdp_per_cap'].tolist()
# Similarly for X and C.
# For now, hard-coded.

countries = [
    "Canada",
    "France",
    "Germany",
    "Italy",
    "Japan",
    "United Kingdom",
    "United States",
]

# Hard-coded Z (GDP per capita in USD, approx 2025)
z = [56894, 50442, 59637, 43012, 34768, 56922, 88160]

# Hard-coded X (attributes: cost, benefit for Low, Medium, High)
X = np.array([[1, 1], [2, 5], [3, 10]])  # Low  # Medium  # High

# Hard-coded C (context, e.g., vulnerability or urgency, arbitrary values for demonstration)
c = [1.0, 1.2, 0.8, 1.5, 2.0, 1.1, 0.9]

alternatives = ["Low", "Medium", "High"]

gamma = 50.0  # Normalization factor for Z

choices = []
probabilities = []

for i in range(7):
    zi = z[i] / 1000  # in thousands
    beta_cost = -4.0 * (gamma / zi)  # Richer countries less sensitive to cost
    beta_benefit = 1.0
    beta = np.array([beta_cost, beta_benefit])

    V = np.dot(X, beta)

    # Incorporate C into benefits
    V += c[i] * X[:, 1] * 0.2  # Context affects benefit perception

    # Softmax probabilities
    exp_V = np.exp(V - np.max(V))
    P = exp_V / np.sum(exp_V)
    probabilities.append(P)

    # Choose based on probabilities (agent's choice in the model)
    choice_idx = np.random.choice(3, p=P)
    choices.append(alternatives[choice_idx])

# Output the simulation results
print("Agent-Based Model Simulation for G7 Summit")
print(
    "Behavioral model: Discrete choice logit with utilities based on cost and benefit attributes."
)
print(
    "Game theory element: Choices are independent but can be interpreted as strategies in a coordination game."
)
print("Each agent's choice:")

for i in range(7):
    print(
        f"{countries[i]} (Z={z[i]}, C={c[i]}): Choice = {choices[i]}, Probabilities (Low, Med, High) = {probabilities[i]}"
    )

# To add game theory interaction: Calculate collective outcome
num_high = choices.count("High")
collective_bonus = (
    num_high / 7 * 5
)  # Example: Bonus benefit if many cooperate (high commitment)

print(f"\nCollective outcome: {num_high} countries chose High commitment.")
print(f"Assumed global benefit bonus: {collective_bonus}")
print(
    "In a full model, agents could iterate choices based on previous rounds, simulating negotiation."
)
