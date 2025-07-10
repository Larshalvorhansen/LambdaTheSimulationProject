import matplotlib.pyplot as plt

# Parameters
timesteps = 50
loan_growth_rate = (
    0.05  # New loans issued per time step in System A (as % of total money)
)
interest_rate = 0.02  # Interest on outstanding debt in System A
cb_injection_rate = (
    0.03  # Central bank injection per time step in System B (as % of starting money)
)

# Initial conditions
initial_money = 1000

money_supply_A = [initial_money]
debt_A = [initial_money * 0.8]  # Initial debt: 80% of money

money_supply_B = [initial_money]

# Simulate over time
for t in range(1, timesteps + 1):
    # --- System A ---
    new_loans = loan_growth_rate * money_supply_A[-1]
    interest = interest_rate * debt_A[-1]
    new_money_A = new_loans + interest
    money_supply_A.append(money_supply_A[-1] + new_money_A)
    debt_A.append(debt_A[-1] + new_loans + interest)

    # --- System B ---
    new_money_B = cb_injection_rate * initial_money
    money_supply_B.append(money_supply_B[-1] + new_money_B)

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(money_supply_A, label="System A: Money Supply")
plt.plot(money_supply_B, label="System B: Money Supply")
plt.plot(debt_A, label="System A: Debt", linestyle="--")
plt.title("Comparison of Monetary Systems Over Time")
plt.xlabel("Time Step")
plt.ylabel("Amount")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
