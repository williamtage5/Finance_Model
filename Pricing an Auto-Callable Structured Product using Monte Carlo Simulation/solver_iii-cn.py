# F:\Learning_journal_at_CUHK\FTEC5610_Computational_Finance\Assignment\Assigenment2-3\solver_iii.py
# (This script calculates the final answer for Q3)

import numpy as np
import time
from scipy.optimize import brentq 
import multiprocessing 

# --- 1. Import the *accelerated* core pricing function ---
try:
    from calculate_fair_value import calculate_fair_value
except ImportError:
    print("Error: Could not import 'calculate_fair_value' function.")
    exit()

# --- 2. Define parameters required for Q3 ---

# Q3 Quanto "Production" level parameters
# (Note: We copied base values from Q1's hkd_params and added Quanto-specific keys)
quanto_params_prod = {
    'NOM': 100000.0,          # 100,000 CNY
    'S0': 11.08,              # Stock S1 initial price (HKD)
    'sigma_stock': 0.6039,    # Stock S1 volatility
    'K0': 0.96,
    'KI': 0.92,
    'AC': 0.99,
    'time_points': np.array([1/12, 2/12, 3/12, 4/12, 5/12, 0.5]),
    'num_paths': 300000,
    
    # --- New Quanto-specific parameters ---
    'r_d': 0.0169,            # CNY rate (for discounting r_disc)
    'r_f': 0.0287,            # HKD rate (for drift rate r_g)
    'sigma_fx': 0.074,        # FX volatility
    'rho': 0.42               # Correlation between stock and FX
}


# --- 3. Define the objective function for the solver (identical to solver_i.py) ---

def objective_function(cp_guess, params, product_type, target_fv):
    """
    This is the function for the brentq solver to optimize.
    It calculates: Fair_Value(cp_guess) - Target_Fair_Value
    """
    
    # Call the core pricing engine (V3 Parallel version)
    current_fv = calculate_fair_value(
        CP_guess=cp_guess, 
        params=params, 
        product_type=product_type # This will be passed as 'Quanto'
    )
    
    error = current_fv - target_fv
    
    print(f"  [Solver Step] Guess CP: {cp_guess: .6f}% -> FV: {current_fv/params['NOM'] * 100.0: .4f}% -> Error: {error/params['NOM'] * 100.0: .4f}%")
    
    return error

# --- 4. Main solver function (identical to solver_i.py) ---
def solve_for_cp(params, product_type, target_margin, cp_min_guess=0.01, cp_max_guess=10.0):
    """
    A complete solver function to find the CP.
    """
    
    target_fv_pct = 1.0 - target_margin
    target_fv = params['NOM'] * target_fv_pct
    
    print("\n" + "="*50)
    print(f"--- Starting Solver (Production Mode) ---")
    print(f"Target Margin: {target_margin*100: .2f}%")
    print(f"Target Fair Value: {target_fv: ,.2f} ({target_fv_pct*100: .2f}%)")
    print(f"Product Type: {product_type}") # <--- This will print 'Quanto'
    print(f"Monte Carlo Paths: {params['num_paths']} (Parallel + Antithetic)")
    print(f"CP Search Range: [{cp_min_guess}%, {cp_max_guess}%]")
    print("="*50)
    
    start_time = time.time()
    
    try:
        found_cp = brentq(
            objective_function,
            a=cp_min_guess,
            b=cp_max_guess,
            args=(params, product_type, target_fv), # Key: passing 'Quanto'
            xtol=1e-5,
            rtol=1e-5
        )
        
        end_time = time.time()
        print("--- Solver Finished ---")
        print(f"Total Time Elapsed: {end_time - start_time: .2f} seconds.")
        print(f"==> Solved Monthly Coupon (CP): {found_cp: .6f} %")
        print("="*50)
        
        return found_cp

    except ValueError as e:
        print(f"--- Solver FAILED ---")
        print(f"Error: {e}")
        print("The error signs for f(a) and f(b) are the same.")
        print("Try expanding 'cp_max_guess' (e.g., to 15.0) in the 'solve_for_cp' function call.")
        return None

# --- 5. Main entry point: Solve Q3(i) and Q3(ii) ---
if __name__ == "__main__":
    
    multiprocessing.freeze_support() 
    
    print(f"--- Executing: solver_iii.py (Q3 Production) ---")
    print("This script will calculate the *exact* answers for Q3(i) and Q3(ii) (Quanto version).")
    print("This may take a few minutes.")
    
    # --- Solve Q3(i): Quanto, 1.20% Margin ---
    # !! Use Quanto parameters and 'Quanto' type !!
    cp_q3_i = solve_for_cp(
        params=quanto_params_prod,
        product_type='Quanto',       # <--- Key
        target_margin=0.0120     # 1.20%
    )
    
    # --- Solve Q3(ii): Quanto, 1.60% Margin ---
    # !! Use Quanto parameters and 'Quanto' type !!
    cp_q3_ii = solve_for_cp(
        params=quanto_params_prod,
        product_type='Quanto',       # <--- Key
        target_margin=0.0160    # 1.60%
    )

    print("\n" + "="*60)
    print("--- Q3 Final Answers (300,000 Paths, Quanto) ---")
    
    if cp_q3_i is not None:
        print(f"Q3(i) [1.20% Margin] CP Value: {cp_q3_i: .6f} %")
    else:
        print("Q3(i) [1.20% Margin] failed to find a solution.")
        
    if cp_q3_ii is not None:
        print(f"Q3(ii) [1.60% Margin] CP Value: {cp_q3_ii: .6f} %")
    else:
        print("Q3(ii) [1.60% Margin] failed to find a solution.")
    print("="*60)