# **Research-Plan**

## **Title**

**Reimagining Monetary Systems: A Comparative Simulation of Commercial and Central-Bank-Based Money Creation with Agent-Based Modeling**

---

## **Background and Motivation**

Contemporary monetary systems rely heavily on commercial banks to create money through lending, an approach that has shown repeated systemic fragility and a tendency toward unsustainable debt accumulation. Trond Andresen's doctoral thesis proposes a radical restructuring of this system, suggesting that only the central bank should be allowed to create money, while commercial banks function solely as lending agents of pre-existing funds.

This thesis aims to explore the outcome of such a proposal by combining:

- **System dynamics modeling** (from Andresen),
- **Agent-based modeling** (adressing the dificulties that arise and are described in complexity theory by using adaptive systems)

By embedding **agents** with individual behavior rules—capitalists, households, banks, central banks, one can explore **emergent patterns** under both systems (with and without Andresen's proposal) and test **resilience, fairness, efficiency, and stability** of such an economy in a dynamic economic environment.

---

## **Research Questions**

1. **How does a central-bank-only driven money creation system compare to the current commercial bank system in terms of debt buildup, economic stability, and resilience to shocks?**

2. **What emergent macroeconomic behaviors arise when individual agents operate under local rules in each system?**

3. **Can an agent-based framework reveal tipping points, feedback loops, or crisis dynamics that traditional models might miss?**

---

## **Methodology**

### 1. **Modeling Two Monetary Systems**

- **System A: Current Commercial Bank System**
  - Banks create money through lending
  - Debt grows over time at the "speed of money"
  - Positive feedback loop from profit motive
- **System B: Central Bank–Only Money Creation**
  - Central bank injects money directly (via transfers, spending, etc.)
  - Banks only allocate, not create, money

Both systems will be implemented with python to begin with. There will be configurable parameters for money supply, interest, repayment rates, GDP growte, household outlook bias etc.

### 2. **Agent-Based Layer (Complex Adaptive Systems)**

Agents include:

- **Households** (workers and capitalists)
- **Banks** (commercial or central, depending on system)
- **Government**
- **Firms**

Each agent will have:

- **Local decision rules** (e.g., consumption rate, lending preference, pessimism threshold)
- **Feedback responsiveness** (e.g., slowing spending when losses increase)
- **Emergent interaction** through markets, credit channels, and production.

### 3. **Simulation Scenarios**

Each system will be run under:

- **Baseline conditions**
- **Shock scenarios** (recession, inflation, bubbles, orange presidents)
- **Policy interventions** (Univeral basic income, interest rate controls, deficit spending, tarrifs)

Metrics that could be compared:

- GDP growth
- Debt-to-GDP ratio
- Bankrupsy/Insolvency rates
- Output volatility
- Money velocity
- Inequality indicators

---

## **Tools and Frameworks**

- **Python** (main language)
  - `numpy`, `pandas`, `matplotlib`, `scipy`
  - `mesa` or `agentpy` for agent-based modeling
  - `dash` or `streamlit` for interactive visualization (optional)
- **Markdown and Tex** for documentation
- **Git** for version control

---

## **Expected Contributions**

- A novel **simulation-based test** of central-bank-based money creation proposals
- Integration of **complex systems theory** into monetary economics
- A **replicable modeling framework** for exploring policy alternatives
- Possibly the clearest computational expression to date of Andresen’s ideas, modernized with emergent agent behaviors

---

## **Timeline draft**

| Time | Milestone                                                      |
| ---- | -------------------------------------------------------------- |
| 1    | Literature review: Andresen, CAS, ABM, historcal debt dynamics |
| 2    | Basic system prooof of concept                                 |
| 3    | Iterative implementation of different agents                   |
| 4    | Interation definition                                          |
| 5    | Interaction tuning                                             |
| 6    | Results analysis and robustness checks                         |
| 7    | Writing thesis + polishing codebase                            |
| 8    | Final submission                                               |
