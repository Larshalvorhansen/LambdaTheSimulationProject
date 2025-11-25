"""
Animert 2D-simulering av to lakseagenter i strategisk rom.

X-akse: Produksjonsmengde (tonn/kvartal)
Y-akse: Profittmargin (NOK/kg)

Agentene "jakter" på Nash-likevekt mens de reagerer på hverandre.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.collections import LineCollection
from dataclasses import dataclass, field
from typing import List, Tuple
import matplotlib

matplotlib.use("Agg")


# ============================================================================
# FORENKLET TO-AGENT MODELL
# ============================================================================


@dataclass
class DuopolyAgent:
    """En agent i Cournot-duopol."""

    name: str
    color: str
    capacity: float

    # Lærbare parametere
    alpha: float = 0.3  # Risikoaversjon
    beta: float = 0.5  # Reaksjonsintensitet på konkurrent
    gamma: float = 0.3  # Treghet i tilpasning

    # Tilstand
    production: float = 0.0
    profit_margin: float = 0.0

    # Historikk for trail
    history_x: List[float] = field(default_factory=list)
    history_y: List[float] = field(default_factory=list)


class DuopolyMarket:
    """
    Forenklet Cournot-duopol for visualisering.

    Etterspørsel: P = a - b*(q1 + q2)
    Kostnad: C = c * q
    """

    def __init__(
        self,
        a: float = 80,  # Prisinterkept (NOK/kg)
        b: float = 0.0003,  # Prissensitivitet
        c: float = 35,  # Marginalkost (NOK/kg)
        seed: int = 42,
    ):
        self.a = a
        self.b = b
        self.c = c
        self.rng = np.random.default_rng(seed)

        # Beregn Nash-likevekt for referanse
        # q* = (a - c) / (3*b) for symmetrisk duopol
        self.nash_q = (a - c) / (3 * b)
        self.nash_price = a - 2 * b * self.nash_q
        self.nash_margin = self.nash_price - c

        # Agenter
        self.agents = [
            DuopolyAgent("Mowi", "#1f77b4", capacity=100000),
            DuopolyAgent("Lerøy", "#ff7f0e", capacity=80000),
        ]

        # Sett ulike startparametere
        self.agents[0].alpha = 0.25
        self.agents[0].beta = 0.6
        self.agents[0].gamma = 0.35

        self.agents[1].alpha = 0.35
        self.agents[1].beta = 0.5
        self.agents[1].gamma = 0.45

        # Initialiser posisjoner (litt tilfeldig start)
        self.agents[0].production = self.nash_q * 0.6 + self.rng.normal(0, 5000)
        self.agents[1].production = self.nash_q * 0.8 + self.rng.normal(0, 5000)

        self._update_margins()

    def _update_margins(self):
        """Oppdater profittmarginer basert på nåværende produksjon."""
        total_q = sum(a.production for a in self.agents)
        price = self.a - self.b * total_q
        price = max(self.c, price)  # Pris kan ikke gå under kostnad

        for agent in self.agents:
            agent.profit_margin = price - self.c

    def step(self) -> dict:
        """Kjør ett tidssteg i simuleringen."""

        # Lagre historikk før oppdatering
        for agent in self.agents:
            agent.history_x.append(agent.production)
            agent.history_y.append(agent.profit_margin)

        # Hver agent beregner beste respons
        new_productions = []

        for i, agent in enumerate(self.agents):
            other = self.agents[1 - i]

            # Cournot beste-respons: q* = (a - c - b*q_other) / (2*b)
            best_response = (self.a - self.c - self.b * other.production) / (2 * self.b)
            best_response = max(0, min(agent.capacity, best_response))

            # Juster for risikoaversjon (trekk mot Nash)
            risk_adj = agent.alpha * (self.nash_q - best_response)
            best_response += risk_adj

            # Juster for konkurranserespons
            # Høy beta = sterkere reaksjon (mer aggressiv)
            competitive_factor = 1 + agent.beta * 0.2 * np.sign(
                agent.production - other.production
            )
            best_response *= competitive_factor

            # Treghet - vektet bevegelse mot målet
            new_q = agent.gamma * agent.production + (1 - agent.gamma) * best_response

            # Legg til litt støy for dynamikk
            noise = self.rng.normal(0, 1000)
            new_q = max(0, min(agent.capacity, new_q + noise))

            new_productions.append(new_q)

        # Oppdater alle agenter samtidig (synkron oppdatering)
        for agent, new_q in zip(self.agents, new_productions):
            agent.production = new_q

        self._update_margins()

        return {
            "productions": [a.production for a in self.agents],
            "margins": [a.profit_margin for a in self.agents],
        }

    def run(self, n_steps: int = 100) -> dict:
        """Kjør simulering over flere steg."""
        history = {
            "step": [],
            "productions": [[] for _ in self.agents],
            "margins": [[] for _ in self.agents],
        }

        for step in range(n_steps):
            result = self.step()
            history["step"].append(step)
            for i, agent in enumerate(self.agents):
                history["productions"][i].append(agent.production)
                history["margins"][i].append(agent.profit_margin)

        return history


# ============================================================================
# ANIMASJON
# ============================================================================


def create_animation(n_frames: int = 150, output_path: str = "duopoly_animation.gif"):
    """Lag animert GIF av duopol-simuleringen."""

    print("Initialiserer simulering...")
    market = DuopolyMarket(seed=42)

    # Kjør simulering først for å få historikk
    print(f"Kjører {n_frames} tidssteg...")
    history = market.run(n_frames)

    # Opprett figur
    fig, ax = plt.subplots(figsize=(12, 9))

    # Beregn akseområder
    all_productions = [p for prods in history["productions"] for p in prods]
    all_margins = [m for margs in history["margins"] for m in margs]

    x_min, x_max = min(all_productions) * 0.9, max(all_productions) * 1.1
    y_min, y_max = min(all_margins) * 0.9, max(all_margins) * 1.1

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel("Produksjon (tonn/kvartal)", fontsize=12)
    ax.set_ylabel("Profittmargin (NOK/kg)", fontsize=12)
    ax.set_title(
        "Cournot Duopol: Strategisk Dynamikk i Laksemarkedet",
        fontsize=14,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.3)

    # Marker Nash-likevekt
    nash_q = market.nash_q
    nash_margin = market.nash_margin
    ax.axvline(
        nash_q,
        color="green",
        linestyle="--",
        alpha=0.5,
        label=f"Nash-likevekt: {nash_q/1000:.0f}k tonn",
    )
    ax.axhline(nash_margin, color="green", linestyle="--", alpha=0.5)
    ax.plot(nash_q, nash_margin, "g*", markersize=20, alpha=0.7, zorder=5)
    ax.annotate(
        "Nash",
        (nash_q, nash_margin),
        xytext=(10, 10),
        textcoords="offset points",
        fontsize=10,
        color="green",
    )

    # Beste-respons kurver (for referanse)
    q_range = np.linspace(0, 100000, 100)
    # BR1(q2) = (a-c-b*q2)/(2b)
    br1 = (market.a - market.c - market.b * q_range) / (2 * market.b)
    br2 = (market.a - market.c - market.b * q_range) / (2 * market.b)

    # Initialiser plot-elementer
    colors = ["#1f77b4", "#ff7f0e"]
    names = ["Mowi", "Lerøy"]

    # Trails (spor)
    trail_lines = []
    for i, color in enumerate(colors):
        (line,) = ax.plot([], [], "-", color=color, alpha=0.3, linewidth=1)
        trail_lines.append(line)

    # Agentmarkører (større sirkler)
    agent_markers = []
    for i, (color, name) in enumerate(zip(colors, names)):
        (marker,) = ax.plot(
            [],
            [],
            "o",
            color=color,
            markersize=20,
            label=name,
            markeredgecolor="white",
            markeredgewidth=2,
        )
        agent_markers.append(marker)

    # Profitt-areal indikator (bakgrunn)
    profit_text = ax.text(
        0.02,
        0.98,
        "",
        transform=ax.transAxes,
        fontsize=11,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )

    # Tidsstempel
    time_text = ax.text(
        0.98,
        0.02,
        "",
        transform=ax.transAxes,
        fontsize=12,
        ha="right",
        bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.8),
    )

    ax.legend(loc="upper right", fontsize=10)

    def init():
        """Initialiser animasjon."""
        for line in trail_lines:
            line.set_data([], [])
        for marker in agent_markers:
            marker.set_data([], [])
        profit_text.set_text("")
        time_text.set_text("")
        return trail_lines + agent_markers + [profit_text, time_text]

    def animate(frame):
        """Oppdater animasjon for hvert bilde."""

        # Oppdater trails (vis siste N punkter)
        trail_length = min(frame + 1, 50)
        start_idx = max(0, frame - trail_length + 1)

        for i, line in enumerate(trail_lines):
            x_trail = history["productions"][i][start_idx : frame + 1]
            y_trail = history["margins"][i][start_idx : frame + 1]
            line.set_data(x_trail, y_trail)

        # Oppdater agentposisjoner
        for i, marker in enumerate(agent_markers):
            x = history["productions"][i][frame]
            y = history["margins"][i][frame]
            marker.set_data([x], [y])

        # Beregn og vis statistikk
        q1 = history["productions"][0][frame]
        q2 = history["productions"][1][frame]
        m1 = history["margins"][0][frame]
        m2 = history["margins"][1][frame]

        profit1 = q1 * m1 / 1e6  # MNOK
        profit2 = q2 * m2 / 1e6  # MNOK
        total_q = q1 + q2
        price = market.a - market.b * total_q

        stats_text = (
            f"Mowi:  {q1/1000:5.1f}k t → {profit1:5.1f} MNOK\n"
            f"Lerøy: {q2/1000:5.1f}k t → {profit2:5.1f} MNOK\n"
            f"─────────────────────\n"
            f"Total: {total_q/1000:5.1f}k t\n"
            f"Pris:  {price:5.1f} NOK/kg"
        )
        profit_text.set_text(stats_text)

        # Kvartal-visning
        quarter = frame % 4 + 1
        year = 2024 + frame // 4
        time_text.set_text(f"Q{quarter} {year}")

        return trail_lines + agent_markers + [profit_text, time_text]

    print("Genererer animasjon...")
    anim = animation.FuncAnimation(
        fig, animate, init_func=init, frames=n_frames, interval=100, blit=True
    )

    print(f"Lagrer til {output_path}...")
    anim.save(output_path, writer="pillow", fps=10, dpi=100)
    plt.close()

    print(f"Animasjon lagret til {output_path}")
    return output_path


def create_phase_portrait(output_path: str = "phase_portrait.png"):
    """
    Lag et fasediagram som viser flere simuleringsforløp fra ulike startpunkter.
    """

    fig, ax = plt.subplots(figsize=(12, 10))

    # Kjør flere simuleringer fra ulike startpunkter
    n_runs = 8
    colors = plt.cm.viridis(np.linspace(0, 1, n_runs))

    market_base = DuopolyMarket(seed=42)
    nash_q = market_base.nash_q
    nash_margin = market_base.nash_margin

    for run in range(n_runs):
        market = DuopolyMarket(seed=run * 10)

        # Ulike startpunkter
        angle = 2 * np.pi * run / n_runs
        radius = nash_q * 0.5
        market.agents[0].production = nash_q + radius * np.cos(angle)
        market.agents[1].production = nash_q + radius * np.sin(angle)
        market._update_margins()

        history = market.run(80)

        # Plot bane for agent 0 (Mowi)
        ax.plot(
            history["productions"][0],
            history["margins"][0],
            "-",
            color=colors[run],
            alpha=0.6,
            linewidth=1.5,
        )

        # Markør for start og slutt
        ax.plot(
            history["productions"][0][0],
            history["margins"][0][0],
            "o",
            color=colors[run],
            markersize=8,
        )
        ax.plot(
            history["productions"][0][-1],
            history["margins"][0][-1],
            "s",
            color=colors[run],
            markersize=10,
            markeredgecolor="black",
        )

    # Nash-likevekt
    ax.plot(nash_q, nash_margin, "r*", markersize=25, label="Nash-likevekt", zorder=10)

    ax.set_xlabel("Mowi produksjon (tonn/kvartal)", fontsize=12)
    ax.set_ylabel("Mowi profittmargin (NOK/kg)", fontsize=12)
    ax.set_title(
        "Fasediagram: Konvergens mot Nash-likevekt\n(fra ulike startposisjoner)",
        fontsize=14,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    # Legg til forklaring
    ax.text(
        0.02,
        0.02,
        "○ = Start\n□ = Slutt\n★ = Nash",
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="bottom",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Fasediagram lagret til {output_path}")
    return output_path


def create_combined_view(output_path: str = "duopoly_combined.png"):
    """
    Lag en kombinert visning med:
    1. 2D strategisk rom (begge agenter)
    2. Produksjon over tid
    3. Profitt over tid
    """

    market = DuopolyMarket(seed=42)
    history = market.run(100)

    fig = plt.figure(figsize=(16, 10))

    # Layout: 2x2 grid
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)

    # Plot 1: 2D strategisk rom (hovedplot)
    ax1 = fig.add_subplot(gs[:, 0])

    colors = ["#1f77b4", "#ff7f0e"]
    names = ["Mowi", "Lerøy"]

    for i, (color, name) in enumerate(zip(colors, names)):
        x = history["productions"][i]
        y = history["margins"][i]

        # Fargegradient basert på tid
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        # Bruk LineCollection for gradient
        norm = plt.Normalize(0, len(x))
        lc = LineCollection(
            segments,
            cmap=plt.cm.Blues if i == 0 else plt.cm.Oranges,
            norm=norm,
            alpha=0.7,
            linewidth=2,
        )
        lc.set_array(np.arange(len(x)))
        ax1.add_collection(lc)

        # Start og slutt markører
        ax1.plot(
            x[0],
            y[0],
            "o",
            color=color,
            markersize=15,
            label=f"{name} start",
            markeredgecolor="white",
            markeredgewidth=2,
        )
        ax1.plot(
            x[-1],
            y[-1],
            "s",
            color=color,
            markersize=15,
            label=f"{name} slutt",
            markeredgecolor="black",
            markeredgewidth=2,
        )

    # Nash-likevekt
    ax1.plot(
        market.nash_q,
        market.nash_margin,
        "g*",
        markersize=25,
        label="Nash-likevekt",
        zorder=10,
    )
    ax1.axvline(market.nash_q, color="green", linestyle="--", alpha=0.3)
    ax1.axhline(market.nash_margin, color="green", linestyle="--", alpha=0.3)

    ax1.set_xlabel("Produksjon (tonn/kvartal)", fontsize=11)
    ax1.set_ylabel("Profittmargin (NOK/kg)", fontsize=11)
    ax1.set_title(
        "Strategisk rom: Produksjon vs Margin", fontsize=12, fontweight="bold"
    )
    ax1.legend(loc="upper right", fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.autoscale()

    # Plot 2: Produksjon over tid
    ax2 = fig.add_subplot(gs[0, 1])

    steps = history["step"]
    for i, (color, name) in enumerate(zip(colors, names)):
        ax2.plot(
            steps,
            np.array(history["productions"][i]) / 1000,
            color=color,
            linewidth=2,
            label=name,
        )

    ax2.axhline(
        market.nash_q / 1000, color="green", linestyle="--", alpha=0.5, label="Nash"
    )
    ax2.set_xlabel("Tidssteg (kvartal)", fontsize=11)
    ax2.set_ylabel("Produksjon (1000 tonn)", fontsize=11)
    ax2.set_title("Produksjon over tid", fontsize=12, fontweight="bold")
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    # Plot 3: Profitt over tid
    ax3 = fig.add_subplot(gs[1, 1])

    for i, (color, name) in enumerate(zip(colors, names)):
        profits = (
            np.array(history["productions"][i]) * np.array(history["margins"][i]) / 1e6
        )
        ax3.plot(steps, profits, color=color, linewidth=2, label=name)

    ax3.set_xlabel("Tidssteg (kvartal)", fontsize=11)
    ax3.set_ylabel("Profitt (MNOK)", fontsize=11)
    ax3.set_title("Profitt over tid", fontsize=12, fontweight="bold")
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)

    fig.suptitle(
        "Cournot Duopol: Norsk Laksemarked - Simuleringsresultater",
        fontsize=14,
        fontweight="bold",
        y=0.98,
    )

    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Kombinert visning lagret til {output_path}")
    return output_path


# ============================================================================
# HOVEDPROGRAM
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ANIMERT DUOPOL-SIMULERING")
    print("=" * 60)
    print()

    # Lag statisk kombinert visning
    print("1. Genererer kombinert oversikt...")
    create_combined_view("duopoly_combined.png")
    print()

    # Lag fasediagram
    print("2. Genererer fasediagram...")
    create_phase_portrait("phase_portrait.png")
    print()

    # Lag animasjon
    print("3. Genererer animasjon (dette tar litt tid)...")
    create_animation(n_frames=100, output_path="duopoly_animation.gif")
    print()

    print("=" * 60)
    print("FERDIG!")
    print("=" * 60)
