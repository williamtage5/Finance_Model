# Pricing an Auto-Callable Structured Product using Monte Carlo Simulation

This project contains a high-performance Python implementation for pricing a 6-month, auto-callable structured product (an "Autocall" or "Snowball"). The core task is to perform reverse-engineering (root-finding) to determine the product parameters (Coupon, Strike, Barriers) that achieve a specific target profit margin for the issuing bank.

The solution is notable for its accuracy (using daily time-stepping) and performance (using parallel processing and antithetic variates).

-----

## Problem Description

The task is to price a 6-month, path-dependent derivative with the following key features:

  * **Monthly Coupons (CP):** Paid if the product has not terminated.
  * **Knock-In (KI):** A "danger" barrier. If the underlying's price *at any date* drops below the Knock-in Price (`P_K`), the principal protection at maturity is lost.
  * **Auto-Call (AC):** An "early profit" barrier. If the underlying's price *at any date on or after the first call date* rises above the Auto-Call Price (`P_C`), the product terminates, paying the principal plus an accrued coupon.
  * **Maturity Payoff:** If not auto-called, the payoff depends on whether a knock-in event occurred and where the final price (`S_M`) is relative to the Strike Price (`K`).

The project is divided into three parts:

1.  **Q1 (HKD Product):** Solve for the monthly coupon (CP) for the standard HKD product to achieve a 1.20% and 1.60% profit margin.
2.  **Q2 (Sensitivity):** Analyze parameter sensitivity. After lowering the coupon by 0.10%, solve for the new `K0`, `KI`, and `AC` required to maintain the 1.20% margin.
3.  **Q3 (Quanto Product):** Solve for the monthly coupon (CP) for a CNY-denominated "Quanto" version of the product, which introduces correlation risk between the HKD stock and the CNYHKD exchange rate.

## Parameter Settings

All simulations are run with a `N=180` daily time-step model to satisfy the "at any date" monitoring requirement.

| Parameter | Symbol | Q1/Q2 (HKD) Value | Q3 (Quanto) Value | Description |
| :--- | :--- | :--- | :--- | :--- |
| Nominal | `NOM` | 100,000 HKD | 100,000 **CNY** | The principal amount. |
| Initial Price | `S0` | 11.08 | 11.08 | Stock S1 initial price. |
| Volatility | `sigma_stock` | 0.6039 (60.39%) | 0.6039 (60.39%) | Stock S1 volatility. |
| HKD Rate | `r_f` | 0.0287 (2.87%) | 0.0287 (2.87%) | HKD risk-free rate. |
| Strike Pct. | `K0` | 0.96 (96%) | 0.96 (96%) | Strike price percentage. |
| Knock-In Pct. | `KI` | 0.92 (92%) | 0.92 (92%) | Knock-in barrier percentage. |
| Auto-Call Pct. | `AC` | 0.99 (99%) | 0.99 (99%) | Auto-call barrier percentage. |
| Tenor (Time) | `T` | 0.5 Years | 0.5 Years | Total life of the product. |
| Time Steps | `N` | 180 | 180 | Daily simulation steps. |
| **CNY Rate** | `r_d` | N/A | **0.0169 (1.69%)** | CNY risk-free rate. |
| **FX Volatility** | `sigma_fx` | N/A | **0.0740 (7.40%)** | CNYHKD exchange rate volatility. |
| **Correlation** | `rho` | N/A | **0.42** | Correlation(Stock, FX). |

## Solution Methodology

A multi-file Python solution was developed to separate the pricing engine from the solver scripts.

### 1\. The Pricing Engine (`calculate_fair_value.py`)

This file contains the core logic for calculating the product's Fair Value (FV).

  * **Accurate Modeling:** Implements a daily (`N=180`) time-step simulation using the Euler-Maruyama discretization of Geometric Brownian Motion (GBM). This correctly captures the "at any date" daily monitoring for knock-in and auto-call events, a critical feature that a simple monthly (N=6) model would fail to price correctly.
  * **Quanto Pricing:** Correctly implements the "Quanto adjustment" (as per `image_83108f.png`, Case 2) for Q3. The model uses:
      * **Discount Rate ($r_{disc}$):** The foreign (CNY) rate, `r_d = 0.0169`.
      * **Drift Rate ($r_g$):** The adjusted drift, $r_g = r_f + \rho \sigma_S \sigma_{fx}$, to account for the correlation risk.
  * **Performance (Parallelism):** The `multiprocessing` library is used to parallelize the simulation. The total `num_paths` are split among all available CPU cores, dramatically reducing computation time.
  * **Accuracy (Variance Reduction):** The **Antithetic Variates** (`Z` and `-Z`) technique is implemented. By simulating paths in negatively correlated pairs, the statistical noise (variance) of the simulation is significantly reduced, leading to a more stable and accurate FV with fewer total paths.

### 2\. The Solvers (`solver_*.py`)

These scripts act as the "control" layer to find the unknown parameters.

  * **Robust Root-Finding:** Instead of a simple manual bisection, the `scipy.optimize.brentq` solver is used. This is a hybrid method (combining bisection, secant, and interpolation) that is significantly faster and more robust, requiring fewer calls to the expensive pricing engine.
  * **Objective Function:** A flexible `objective_function` is defined, which calculates the `Error = Calculated_FV - Target_FV`. `brentq` is tasked with finding the parameter (e.g., `CP`) that makes this `Error` equal to zero.

### 3\. The Validator (`validator.py`)

This script serves as a final "sanity check." It imports all 7 final answers from the solver scripts and plugs them back into the `calculate_fair_value` engine to confirm that they produce the expected profit margins (1.20% or 1.60%) within an acceptable margin of Monte Carlo noise.

## How to Run

**Prerequisites:** Python 3, `numpy`, `scipy`.

The scripts must be run in the correct order, as the output from Q1 is required for Q2.

**Step 1: Solve for Q1 (HKD Coupon)**
This script runs the simulation (using 300,000 paths) to find the two coupons for Q1.

```bash
python solver_i.py
```

  * **Output:** Note the `CP1` value (e.g., `3.458654`) for the 1.20% margin.

**Step 2: Solve for Q2 (Parameter Sensitivity)**
You must manually edit the `solver_ii.py` script.

1.  Open `solver_ii.py`.
2.  Find the line `CP1_VALUE = 3.458654` and replace the value with your exact output from Step 1.
3.  Save the file and run:
    ```bash
    python solver_ii.py
    ```

<!-- end list -->

  * **Note:** If the solver fails for one parameter (e.g., `KI`), it means the search interval `[a, b]` was too small. This is expected for insensitive parameters. Widen the search interval (e.g., `a=0.50`) and re-run.

**Step 3: Solve for Q3 (Quanto Coupon)**
This script runs the simulation for the Quanto model.

```bash
python solver_iii.py
```

**Step 4: (Recommended) Validate All Results**
You must manually edit the `validator.py` script.

1.  Open `validator.py`.
2.  Copy all 7 solutions (CP1, CP2, K0\_Q2, KI\_Q2, AC\_Q2, CP3, CP4) from your console output into the top of the `main` block.
3.  Save the file and run:
    ```bash
    python validator.py
    ```

<!-- end list -->

  * **Output:** The script will print a validation report for all 7 answers, showing the calculated profit margin versus the target margin.

-----

## STAR Summary

  * **Situation:** I was tasked with pricing a complex, 6-month auto-callable structured product. The product featured path-dependent "at any date" knock-in and auto-call barriers. The primary goal was to reverse-engineer product parameters (Coupon, Strike, Barriers) to precisely meet the bank's target profit margins of 1.20% and 1.60%.

  * **Task:**

    1.  **Q1:** Find the monthly coupon (CP) for the standard HKD-denominated product.
    2.  **Q2:** Analyze parameter sensitivity by fixing the profit margin at 1.20% and solving for `K0`, `KI`, and `AC` after a 0.10% coupon reduction.
    3.  **Q3:** Find the monthly coupon (CP) for the CNY-denominated "Quanto" version, which required modeling correlation risk.

  * **Action:**

    1.  **Engine:** I built a pricing engine in Python based on a daily time-step (`N=180`) Monte Carlo simulation. This was critical for accurately modeling the "at any date" barrier logic, a feature a simpler monthly model would miss.
    2.  **Models:** I implemented the standard GBM model for Q1/Q2 and the correct "Quanto adjustment" model ($r_g = r_f + \rho\sigma_S\sigma_{fx}$, $r_{disc} = r_d$) for Q3, as specified in the problem's guide.
    3.  **Optimization:** To ensure both speed and accuracy, I optimized the engine using two key techniques:
          * **`multiprocessing`:** Parallelized the 300,000 simulations across all available CPU cores.
          * **Antithetic Variates:** Implemented the `Z` and `-Z` technique to significantly reduce statistical variance (noise).
    4.  **Solvers:** I used the `scipy.optimize.brentq` root-finder (a hybrid bisection/secant method) to create robust solver scripts (`solver_i.py`, `solver_ii.py`, `solver_iii.py`) that automatically find the required parameters.
    5.  **Validation:** I created a final `validator.py` script to take all 7 solutions, plug them back into the pricing engine, and verify they all produced the correct target profit margins.

  * **Result:**

    1.  **Successful Calculation:** All 7 required parameters were successfully calculated. The parallelized, antithetic-aware engine performed these tasks in minutes, rather than hours.
    2.  **Verified Accuracy:** The `validator.py` script confirmed all 7 solutions were correct.
          * Q1/Q2 solutions were accurate to within `~0.01%` of the target margin.
          * Q3 solutions were accurate to within `~0.03%`, with the slightly larger (but acceptable) error correctly identifying the higher inherent variance of the more complex Quanto model.
    3.  **Key Insight (Q2):** The analysis quantified parameter sensitivity. It proved that `AC` was the most sensitive parameter and `KI` was the least. To compensate for a `0.10%` coupon reduction, the `KI` barrier had to be massively adjusted by **-26.23%** (from 0.92 to 0.657), confirming the "insensitivity" hinted at in the problem description.