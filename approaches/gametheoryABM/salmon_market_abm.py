"""
Spillteori ABM med ML-kalibrering
Domene: Norsk lakseoppdrett (Cournot oligopol)

Konsept:
- Agenter representerer store lakseselskaper (Mowi, Lerøy, SalMar, etc.)
- Spillmekanikk: Cournot-konkurranse (velg produksjonsmengde)
- ML: Gradient-basert justering av agentparametere mot historiske data
- Regularisering for å unngå overparametrisering

Forfatter: Lars Halvor / Claude
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import json


# ============================================================================
# AGENTDEFINISJON
# ============================================================================

@dataclass
class SalmonProducer:
    """
    En lakseprodusent med spillteoretiske beslutningsparametere.
    
    Parametere som skal læres:
    - alpha: Risikoaversjon (0 = risikonøytral, 1 = svært risikoavers)
    - beta: Hvor mye de reagerer på konkurrenters forventede produksjon
    - gamma: Treghet/momentum i produksjonsbeslutninger
    - epsilon: Bounded rationality støy
    """
    name: str
    capacity: float  # Maks produksjonskapasitet (tonn/kvartal)
    
    # Lærbare parametere (initialisert med reasonable defaults)
    alpha: float = 0.3    # Risikoaversjon
    beta: float = 0.5     # Konkurranserespons
    gamma: float = 0.4    # Produksjonstreghet
    epsilon: float = 0.05 # Støynivå
    
    # Tilstand
    current_production: float = 0.0
    profit_history: List[float] = field(default_factory=list)
    
    def decide_production(
        self, 
        expected_price: float,
        expected_competitor_production: float,
        marginal_cost: float,
        rng: np.random.Generator
    ) -> float:
        """
        Beslutt produksjonsmengde basert på Cournot-logikk med bounded rationality.
        
        Cournot beste-respons: q* = (a - c - b*Q_andre) / (2*b)
        der a = maksimal betalingsvillighet, b = prissensitivitet, c = marginalkost
        """
        # Forenklet Cournot beste-respons
        # Antar lineær etterspørsel: P = a - b*Q_total
        a = 80  # NOK/kg ved null produksjon (interkept)
        b = 0.00005  # Prissensitivitet
        
        # Teoretisk optimal produksjon (Nash-respons)
        optimal_q = (a - marginal_cost - b * expected_competitor_production) / (2 * b)
        optimal_q = max(0, min(optimal_q, self.capacity))
        
        # Juster for risikoaversjon (produser mindre ved usikkerhet)
        price_uncertainty = 0.15 * expected_price  # Antatt volatilitet
        risk_adjustment = 1 - self.alpha * (price_uncertainty / expected_price)
        optimal_q *= risk_adjustment
        
        # Juster for konkurranserespons (beta)
        # Høy beta = sterkere reaksjon på konkurrenters produksjon
        competitive_adjustment = 1 - self.beta * (expected_competitor_production / 500000)
        optimal_q *= max(0.5, min(1.5, competitive_adjustment))
        
        # Treghet (gamma) - vektet snitt av nåværende og optimal
        if self.current_production > 0:
            target_q = self.gamma * self.current_production + (1 - self.gamma) * optimal_q
        else:
            target_q = optimal_q
        
        # Bounded rationality støy
        noise = rng.normal(0, self.epsilon * target_q)
        final_q = max(0, min(self.capacity, target_q + noise))
        
        return final_q
    
    def get_learnable_params(self) -> np.ndarray:
        """Returner lærbare parametere som vektor."""
        return np.array([self.alpha, self.beta, self.gamma, self.epsilon])
    
    def set_learnable_params(self, params: np.ndarray):
        """Sett lærbare parametere fra vektor."""
        self.alpha = np.clip(params[0], 0.0, 1.0)
        self.beta = np.clip(params[1], 0.0, 1.0)
        self.gamma = np.clip(params[2], 0.0, 1.0)
        self.epsilon = np.clip(params[3], 0.01, 0.3)


# ============================================================================
# MARKEDSMODELL
# ============================================================================

@dataclass
class SalmonMarket:
    """
    Norsk laksemarked med sesongvariasjoner og global etterspørsel.
    """
    # Markedsparametere
    base_demand: float = 600000  # Tonn/kvartal global etterspørsel
    price_intercept: float = 80  # NOK/kg ved null tilbud
    price_sensitivity: float = 0.00005  # Prisfall per tonn tilbud
    
    # Kostnadsstruktur (NOK/kg)
    base_marginal_cost: float = 35
    
    # Sesongfaktorer (Q1, Q2, Q3, Q4)
    seasonal_demand: np.ndarray = field(
        default_factory=lambda: np.array([0.9, 1.0, 1.1, 1.0])
    )
    seasonal_cost: np.ndarray = field(
        default_factory=lambda: np.array([1.05, 1.0, 0.95, 1.0])
    )
    
    def clear_market(
        self, 
        productions: Dict[str, float], 
        quarter: int
    ) -> Tuple[float, Dict[str, float]]:
        """
        Markedsklaring: Bestem pris og profitt gitt produksjonsbeslutninger.
        
        Returns:
            price: Markedspris (NOK/kg)
            profits: Dict med profitt per produsent
        """
        total_production = sum(productions.values())
        season_idx = quarter % 4
        
        # Etterspørselsjustert pris
        seasonal_factor = self.seasonal_demand[season_idx]
        effective_demand = self.base_demand * seasonal_factor
        
        # Lineær etterspørselskurve: P = a - b*Q
        price = self.price_intercept - self.price_sensitivity * total_production
        price = max(20, price)  # Gulv på pris
        
        # Beregn profitt for hver produsent
        marginal_cost = self.base_marginal_cost * self.seasonal_cost[season_idx]
        profits = {}
        for name, q in productions.items():
            profit = (price - marginal_cost) * q * 1000  # Konverter til kg
            profits[name] = profit
        
        return price, profits


# ============================================================================
# SIMULERINGSMOTOR
# ============================================================================

class SalmonABM:
    """
    Agent-basert modell for norsk laksemarked.
    """
    
    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)
        self.market = SalmonMarket()
        
        # Initialiser produsenter (basert på faktiske markedsandeler ca. 2023)
        self.producers = [
            SalmonProducer("Mowi", capacity=120000),
            SalmonProducer("Lerøy", capacity=80000),
            SalmonProducer("SalMar", capacity=70000),
            SalmonProducer("Grieg", capacity=35000),
            SalmonProducer("Norway Royal Salmon", capacity=30000),
        ]
        
        # Historikk
        self.history = {
            "quarter": [],
            "total_production": [],
            "price": [],
            "productions": {p.name: [] for p in self.producers},
            "profits": {p.name: [] for p in self.producers},
        }
    
    def step(self, quarter: int) -> Dict:
        """Kjør ett tidssteg (ett kvartal)."""
        
        # Hver produsent estimerer konkurrenters produksjon
        # (forenklet: bruker forrige periodes produksjon)
        total_last = sum(p.current_production for p in self.producers)
        
        # Forventet pris (naiv forventning basert på forrige kvartal)
        if len(self.history["price"]) > 0:
            expected_price = self.history["price"][-1]
        else:
            expected_price = 55  # Startverdi
        
        # Marginalkost for dette kvartalet
        season_idx = quarter % 4
        marginal_cost = self.market.base_marginal_cost * self.market.seasonal_cost[season_idx]
        
        # Samle produksjonsbeslutninger
        productions = {}
        for producer in self.producers:
            other_production = total_last - producer.current_production
            q = producer.decide_production(
                expected_price=expected_price,
                expected_competitor_production=other_production,
                marginal_cost=marginal_cost,
                rng=self.rng
            )
            productions[producer.name] = q
        
        # Markedsklaring
        price, profits = self.market.clear_market(productions, quarter)
        
        # Oppdater tilstand
        for producer in self.producers:
            producer.current_production = productions[producer.name]
            producer.profit_history.append(profits[producer.name])
        
        # Logg historikk
        self.history["quarter"].append(quarter)
        self.history["total_production"].append(sum(productions.values()))
        self.history["price"].append(price)
        for name, q in productions.items():
            self.history["productions"][name].append(q)
        for name, profit in profits.items():
            self.history["profits"][name].append(profit)
        
        return {
            "quarter": quarter,
            "price": price,
            "total_production": sum(productions.values()),
            "productions": productions,
            "profits": profits
        }
    
    def run(self, n_quarters: int = 20) -> Dict:
        """Kjør simulering over flere kvartaler."""
        for q in range(n_quarters):
            self.step(q)
        return self.history
    
    def reset(self):
        """Nullstill simulering."""
        for p in self.producers:
            p.current_production = 0.0
            p.profit_history = []
        self.history = {
            "quarter": [],
            "total_production": [],
            "price": [],
            "productions": {p.name: [] for p in self.producers},
            "profits": {p.name: [] for p in self.producers},
        }
    
    def get_all_params(self) -> np.ndarray:
        """Hent alle lærbare parametere som én vektor."""
        params = []
        for p in self.producers:
            params.extend(p.get_learnable_params())
        return np.array(params)
    
    def set_all_params(self, params: np.ndarray):
        """Sett alle lærbare parametere fra én vektor."""
        n_params_per_agent = 4
        for i, producer in enumerate(self.producers):
            start = i * n_params_per_agent
            end = start + n_params_per_agent
            producer.set_learnable_params(params[start:end])


# ============================================================================
# ML-KALIBRERING
# ============================================================================

class ABMCalibrator:
    """
    ML-basert kalibrering av ABM-parametere mot observerte data.
    
    Bruker gradient-fri optimalisering (siden ABM ikke er differensierbar)
    med regularisering for å unngå overparametrisering.
    """
    
    def __init__(self, abm: SalmonABM, target_data: Dict):
        self.abm = abm
        self.target_data = target_data
        self.best_params = None
        self.best_loss = float('inf')
        self.loss_history = []
    
    def compute_loss(
        self, 
        params: np.ndarray, 
        lambda_reg: float = 0.01
    ) -> float:
        """
        Beregn tap mellom simulert og observert data.
        
        Loss = MSE(price) + MSE(production) + lambda * L2(params)
        """
        # Sett parametere og kjør simulering
        self.abm.set_all_params(params)
        self.abm.reset()
        history = self.abm.run(len(self.target_data["price"]))
        
        # MSE for pris
        sim_prices = np.array(history["price"])
        target_prices = np.array(self.target_data["price"])
        price_mse = np.mean((sim_prices - target_prices) ** 2)
        
        # MSE for total produksjon
        sim_prod = np.array(history["total_production"])
        target_prod = np.array(self.target_data["total_production"])
        prod_mse = np.mean((sim_prod - target_prod) ** 2)
        
        # Normaliser MSE til sammenlignbar skala
        price_loss = price_mse / (np.std(target_prices) ** 2 + 1e-6)
        prod_loss = prod_mse / (np.std(target_prod) ** 2 + 1e-6)
        
        # L2-regularisering
        # Straff avvik fra "nøytrale" verdier (0.5 for de fleste parametere)
        neutral_params = np.array([0.3, 0.5, 0.4, 0.05] * len(self.abm.producers))
        reg_loss = lambda_reg * np.sum((params - neutral_params) ** 2)
        
        total_loss = price_loss + prod_loss + reg_loss
        return total_loss
    
    def calibrate(
        self, 
        n_iterations: int = 100,
        learning_rate: float = 0.1,
        lambda_reg: float = 0.01,
        patience: int = 20
    ) -> np.ndarray:
        """
        Kalibrer parametere ved hjelp av evolusjonsstrategi (ES).
        
        ES er robust for ikke-differensierbare funksjoner og gir
        naturlig utforskning av parameterrommet.
        """
        n_params = len(self.abm.get_all_params())
        
        # Initialiser med nåværende parametere
        current_params = self.abm.get_all_params()
        current_loss = self.compute_loss(current_params, lambda_reg)
        
        self.best_params = current_params.copy()
        self.best_loss = current_loss
        self.loss_history = [current_loss]
        
        no_improvement = 0
        
        print(f"Starter kalibrering med {n_params} parametere")
        print(f"Initial loss: {current_loss:.4f}")
        print("-" * 50)
        
        for iteration in range(n_iterations):
            # Generer kandidater ved å perturbere nåværende parametere
            n_candidates = 10
            noise_scale = learning_rate * (1 - iteration / n_iterations)  # Decay
            
            candidates = []
            losses = []
            
            for _ in range(n_candidates):
                noise = np.random.randn(n_params) * noise_scale
                candidate = np.clip(current_params + noise, 0, 1)
                # Sørg for at epsilon er minst 0.01
                for i in range(3, len(candidate), 4):
                    candidate[i] = max(0.01, candidate[i])
                
                loss = self.compute_loss(candidate, lambda_reg)
                candidates.append(candidate)
                losses.append(loss)
            
            # Velg beste kandidat
            best_idx = np.argmin(losses)
            best_candidate_loss = losses[best_idx]
            
            if best_candidate_loss < current_loss:
                current_params = candidates[best_idx]
                current_loss = best_candidate_loss
                no_improvement = 0
                
                if current_loss < self.best_loss:
                    self.best_loss = current_loss
                    self.best_params = current_params.copy()
            else:
                no_improvement += 1
            
            self.loss_history.append(current_loss)
            
            if iteration % 10 == 0:
                print(f"Iterasjon {iteration}: loss = {current_loss:.4f}, best = {self.best_loss:.4f}")
            
            # Early stopping
            if no_improvement >= patience:
                print(f"Early stopping etter {iteration} iterasjoner")
                break
        
        print("-" * 50)
        print(f"Kalibrering ferdig. Beste loss: {self.best_loss:.4f}")
        
        # Sett beste parametere
        self.abm.set_all_params(self.best_params)
        return self.best_params


# ============================================================================
# SYNTETISKE MÅLDATA (for testing)
# ============================================================================

def generate_synthetic_target_data(n_quarters: int = 20, seed: int = 123) -> Dict:
    """
    Generer syntetiske "måldata" som representerer historiske observasjoner.
    
    I en virkelig anvendelse ville dette være faktiske data fra SSB/Nasdaq.
    """
    rng = np.random.default_rng(seed)
    
    # Simuler med "sanne" parametere
    true_abm = SalmonABM(seed=seed)
    
    # Sett "sanne" parametere som vi vil prøve å finne igjen
    true_params = np.array([
        0.25, 0.6, 0.35, 0.08,  # Mowi
        0.35, 0.5, 0.45, 0.06,  # Lerøy
        0.20, 0.55, 0.30, 0.07, # SalMar
        0.40, 0.45, 0.50, 0.05, # Grieg
        0.30, 0.50, 0.40, 0.06, # NRS
    ])
    true_abm.set_all_params(true_params)
    
    history = true_abm.run(n_quarters)
    
    # Legg til litt observasjonsstøy
    noisy_prices = np.array(history["price"]) + rng.normal(0, 2, n_quarters)
    noisy_production = np.array(history["total_production"]) + rng.normal(0, 5000, n_quarters)
    
    return {
        "price": noisy_prices.tolist(),
        "total_production": noisy_production.tolist(),
        "true_params": true_params,
    }


# ============================================================================
# HOVEDPROGRAM
# ============================================================================

def main():
    print("=" * 60)
    print("SPILLTEORI ABM MED ML-KALIBRERING")
    print("Domene: Norsk lakseoppdrett")
    print("=" * 60)
    print()
    
    # Generer syntetiske måldata
    print("1. Genererer syntetiske måldata...")
    target_data = generate_synthetic_target_data(n_quarters=20)
    print(f"   Antall kvartaler: {len(target_data['price'])}")
    print(f"   Prisrange: {min(target_data['price']):.1f} - {max(target_data['price']):.1f} NOK/kg")
    print(f"   Produksjonsrange: {min(target_data['total_production']):.0f} - {max(target_data['total_production']):.0f} tonn")
    print()
    
    # Initialiser ABM med "feil" parametere
    print("2. Initialiserer ABM med standardparametere...")
    abm = SalmonABM(seed=42)
    initial_params = abm.get_all_params()
    print(f"   Antall lærbare parametere: {len(initial_params)}")
    print(f"   Parametere per agent: 4 (alpha, beta, gamma, epsilon)")
    print()
    
    # Kalibrer
    print("3. Starter ML-kalibrering...")
    print()
    calibrator = ABMCalibrator(abm, target_data)
    best_params = calibrator.calibrate(
        n_iterations=100,
        learning_rate=0.15,
        lambda_reg=0.01,
        patience=25
    )
    print()
    
    # Sammenlign med sanne parametere
    print("4. Evaluering av kalibrering:")
    print()
    true_params = target_data["true_params"]
    
    param_names = ["alpha", "beta", "gamma", "epsilon"]
    for i, producer in enumerate(abm.producers):
        print(f"   {producer.name}:")
        for j, name in enumerate(param_names):
            true_val = true_params[i * 4 + j]
            learned_val = best_params[i * 4 + j]
            error = abs(true_val - learned_val)
            print(f"      {name}: sant={true_val:.3f}, lært={learned_val:.3f}, feil={error:.3f}")
        print()
    
    # Kjør endelig simulering og vis resultater
    print("5. Sammenligning av simulert vs måldata:")
    abm.reset()
    final_history = abm.run(len(target_data["price"]))
    
    price_rmse = np.sqrt(np.mean(
        (np.array(final_history["price"]) - np.array(target_data["price"])) ** 2
    ))
    prod_rmse = np.sqrt(np.mean(
        (np.array(final_history["total_production"]) - np.array(target_data["total_production"])) ** 2
    ))
    
    print(f"   Pris RMSE: {price_rmse:.2f} NOK/kg")
    print(f"   Produksjon RMSE: {prod_rmse:.0f} tonn")
    print()
    
    # Lagre resultater (konverter numpy arrays til lister)
    def to_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [to_serializable(v) for v in obj]
        return obj
    
    results = {
        "target_data": to_serializable(target_data),
        "simulated_data": {
            "price": final_history["price"],
            "total_production": final_history["total_production"],
        },
        "learned_params": best_params.tolist(),
        "true_params": true_params.tolist() if isinstance(true_params, np.ndarray) else true_params,
        "loss_history": calibrator.loss_history,
        "metrics": {
            "price_rmse": float(price_rmse),
            "production_rmse": float(prod_rmse),
        }
    }
    
    with open("calibration_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("Resultater lagret til calibration_results.json")
    print()
    print("=" * 60)
    print("FERDIG")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    main()
