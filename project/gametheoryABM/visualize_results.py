"""
Visualisering av kalibrert ABM vs måldata.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


def load_results(filepath="calibration_results.json"):
    with open(filepath, "r") as f:
        return json.load(f)


def plot_calibration_results(results, output_path="calibration_plot.png"):
    """Lag sammenlignende plot av simulert vs måldata."""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Spillteori ABM: Kalibrering mot Norsk Laksemarked", fontsize=14, fontweight='bold')
    
    quarters = list(range(len(results["target_data"]["price"])))
    
    # Plot 1: Pris over tid
    ax1 = axes[0, 0]
    ax1.plot(quarters, results["target_data"]["price"], 'b-o', label='Måldata (observert)', linewidth=2, markersize=6)
    ax1.plot(quarters, results["simulated_data"]["price"], 'r--s', label='Simulert (kalibrert)', linewidth=2, markersize=5)
    ax1.set_xlabel("Kvartal")
    ax1.set_ylabel("Pris (NOK/kg)")
    ax1.set_title("Laksepris over tid")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Total produksjon over tid
    ax2 = axes[0, 1]
    ax2.plot(quarters, np.array(results["target_data"]["total_production"]) / 1000, 'b-o', 
             label='Måldata', linewidth=2, markersize=6)
    ax2.plot(quarters, np.array(results["simulated_data"]["total_production"]) / 1000, 'r--s', 
             label='Simulert', linewidth=2, markersize=5)
    ax2.set_xlabel("Kvartal")
    ax2.set_ylabel("Produksjon (1000 tonn)")
    ax2.set_title("Total produksjon over tid")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Loss history
    ax3 = axes[1, 0]
    ax3.plot(results["loss_history"], 'g-', linewidth=2)
    ax3.axhline(y=min(results["loss_history"]), color='r', linestyle='--', alpha=0.7, label=f'Beste: {min(results["loss_history"]):.4f}')
    ax3.set_xlabel("Iterasjon")
    ax3.set_ylabel("Loss")
    ax3.set_title("Kalibreringsforløp (Loss over tid)")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_yscale('log')
    
    # Plot 4: Parameter sammenligning
    ax4 = axes[1, 1]
    param_names = ["α", "β", "γ", "ε"]
    producer_names = ["Mowi", "Lerøy", "SalMar", "Grieg", "NRS"]
    
    x = np.arange(len(param_names))
    width = 0.15
    
    true_params = np.array(results["true_params"]).reshape(-1, 4)
    learned_params = np.array(results["learned_params"]).reshape(-1, 4)
    
    # Gjennomsnittlig parameter på tvers av produsenter
    true_avg = true_params.mean(axis=0)
    learned_avg = learned_params.mean(axis=0)
    
    bars1 = ax4.bar(x - width/2, true_avg, width, label='Sann verdi', color='steelblue')
    bars2 = ax4.bar(x + width/2, learned_avg, width, label='Lært verdi', color='coral')
    
    ax4.set_ylabel('Parameterverdi')
    ax4.set_title('Gjennomsnittlige lærte vs sanne parametere')
    ax4.set_xticks(x)
    ax4.set_xticklabels(['Risikoaversjon\n(α)', 'Konkurranserespons\n(β)', 
                         'Treghet\n(γ)', 'Støy\n(ε)'])
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.set_ylim(0, 0.7)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Plot lagret til {output_path}")
    return output_path


def create_detailed_param_comparison(results, output_path="param_comparison.png"):
    """Detaljert sammenligning av parametere per produsent."""
    
    fig, axes = plt.subplots(1, 5, figsize=(16, 4))
    fig.suptitle("Parametersammenligning per produsent", fontsize=12, fontweight='bold')
    
    producer_names = ["Mowi", "Lerøy", "SalMar", "Grieg", "NRS"]
    param_names = ["α", "β", "γ", "ε"]
    
    true_params = np.array(results["true_params"]).reshape(-1, 4)
    learned_params = np.array(results["learned_params"]).reshape(-1, 4)
    
    for i, (ax, name) in enumerate(zip(axes, producer_names)):
        x = np.arange(len(param_names))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, true_params[i], width, label='Sann', color='steelblue', alpha=0.8)
        bars2 = ax.bar(x + width/2, learned_params[i], width, label='Lært', color='coral', alpha=0.8)
        
        ax.set_title(name)
        ax.set_xticks(x)
        ax.set_xticklabels(param_names)
        ax.set_ylim(0, 1.0)
        ax.grid(True, alpha=0.3, axis='y')
        
        if i == 0:
            ax.set_ylabel('Verdi')
            ax.legend(loc='upper right', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Detaljert plot lagret til {output_path}")
    return output_path


def print_analysis(results):
    """Skriv ut analyse av kalibreringen."""
    
    print("\n" + "=" * 60)
    print("ANALYSE AV KALIBRERING")
    print("=" * 60)
    
    # Beregn feil
    true_params = np.array(results["true_params"]).reshape(-1, 4)
    learned_params = np.array(results["learned_params"]).reshape(-1, 4)
    
    param_errors = np.abs(true_params - learned_params)
    
    print("\nGjennomsnittlig absolutt feil per parameter:")
    param_names = ["alpha (risikoaversjon)", "beta (konkurranserespons)", 
                   "gamma (treghet)", "epsilon (støy)"]
    for i, name in enumerate(param_names):
        avg_error = param_errors[:, i].mean()
        std_error = param_errors[:, i].std()
        print(f"  {name}: {avg_error:.3f} ± {std_error:.3f}")
    
    print(f"\nTotal gjennomsnittlig parameterfeil: {param_errors.mean():.3f}")
    
    print("\nNøkkelobservasjoner:")
    
    # Identifiser mest/minst nøyaktige parametere
    avg_errors = param_errors.mean(axis=0)
    best_param = param_names[np.argmin(avg_errors)]
    worst_param = param_names[np.argmax(avg_errors)]
    
    print(f"  - Best estimert: {best_param}")
    print(f"  - Vanskeligst å estimere: {worst_param}")
    
    # Vurder overparametrisering
    n_params = len(results["learned_params"])
    n_datapoints = len(results["target_data"]["price"]) * 2  # pris + produksjon
    ratio = n_params / n_datapoints
    
    print(f"\nOverparametriseringsvurdering:")
    print(f"  - Antall parametere: {n_params}")
    print(f"  - Antall datapunkter: {n_datapoints}")
    print(f"  - Parameter/data ratio: {ratio:.2f}")
    
    if ratio > 0.5:
        print("  - ADVARSEL: Høy risiko for overparametrisering!")
        print("    Anbefaling: Reduser antall frie parametere eller øk datamengde.")
    elif ratio > 0.3:
        print("  - MODERAT: Akseptabel ratio, men vær oppmerksom.")
    else:
        print("  - OK: God balanse mellom parametere og data.")


if __name__ == "__main__":
    # Last resultater og generer visualiseringer
    results = load_results()
    plot_calibration_results(results)
    create_detailed_param_comparison(results)
    print_analysis(results)
