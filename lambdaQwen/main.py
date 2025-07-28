#!/usr/bin/env python3
# main.py

import matplotlib.pyplot as plt
from model import LambdaSimModel


def plot_results(model):
    """Plots the collected data from the simulation."""
    steps = model.datacollector["Step"]
    total_gdp = model.datacollector["Total_GDP"]
    total_debt = model.datacollector["Total_Debt"]
    avg_growth = model.datacollector["Avg_Growth"]

    # Create figure and subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle("LambdaSim Macroeconomic Indicators Over Time")

    # Plot Total GDP
    ax1.plot(steps, total_gdp, label="Total GDP", color="green")
    ax1.set_ylabel("Total GDP")
    ax1.legend()
    ax1.grid(True)

    # Plot Total Debt
    ax2.plot(steps, total_debt, label="Total Debt", color="red")
    ax2.set_ylabel("Total Debt")
    ax2.legend()
    ax2.grid(True)

    # Plot Average Growth Rate
    ax3.plot(steps, avg_growth, label="Avg Growth Rate", color="blue")
    ax3.set_xlabel("Time Step")
    ax3.set_ylabel("Avg Growth Rate")
    ax3.legend()
    ax3.grid(True)

    # Adjust layout to prevent overlapping labels
    plt.tight_layout()
    # Display the plot
    plt.show()


def main():
    NUM_COUNTRIES = 10
    INITIAL_CONNECTIONS = 3
    SIMULATION_STEPS = 100

    model = LambdaSimModel(
        num_countries=NUM_COUNTRIES, initial_connections=INITIAL_CONNECTIONS
    )
    model.run_simulation(steps=SIMULATION_STEPS)

    plot_results(model)

    print("\n--- Final Simulation Data ---")
    print(
        f"Total GDP over time (last 5): {[f'{gdp:.2f}' for gdp in model.datacollector['Total_GDP'][-5:]]}"
    )
    print(
        f"Total Debt over time (last 5): {[f'{debt:.2f}' for debt in model.datacollector['Total_Debt'][-5:]]}"
    )
    print(
        f"Average Growth over time (last 5): {[f'{growth:.4f}' for growth in model.datacollector['Avg_Growth'][-5:]]}"
    )


if __name__ == "__main__":
    main()
