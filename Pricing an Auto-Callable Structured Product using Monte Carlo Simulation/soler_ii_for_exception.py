# F:\Learning_journal_at_CUHK\FTEC5610_Computational_Finance\Assignment\Assigenment2-3\solver_ii.py
# This script calculates the final answer for Q2: Aggressive search for KI)

import numpy as np
import time
from scipy.optimize import brentq 
import multiprocessing
import copy 

try:
    from calculate_fair_value import calculate_fair_value
except ImportError:
    print("Error: Could not import 'calculate_fair_value' function.")
    exit()

# --- 2. Define parameters required for Q2 ---

# Q1 "Production" level parameters (Our baseline)
hkd_params_prod = {
    'NOM': 100000.0, 'r_f': 0.0287, 'sigma_stock': 0.6039, 'S0': 11.08,
    'time_points': np.array([1/12, 2/12, 3/12, 4/12, 5/12, 0.5]),
    'num_paths': 300000, # Production paths
    'K0': 0.96, 'KI': 0.92, 'AC': 0.99
}

# --- Q2 Core known conditions ---
CP1_VALUE = 3.458654  # This is the value you obtained from Q1(i)
CP_NEW = CP1_VALUE - 0.10
TARGET_MARGIN = 0.0120 # 1.20%
TARGET_FV = hkd_params_prod['NOM'] * (1.0 - TARGET_MARGIN) # 98,800.00

# --- 3. Define the generic objective function (Q2 specific) ---

def generic_objective_function(param_guess, param_name_to_solve, base_params, fixed_cp, target_fv):
    """
    Generic objective function, used to solve for K0, KI, or AC.
    """
    
    temp_params = copy.deepcopy(base_params)
    temp_params[param_name_to_solve] = param_guess
    
    current_fv = calculate_fair_value(
        CP_guess=fixed_cp, 
        params=temp_params, 
        product_type='HKD'
    )
    
    error = current_fv - target_fv
    
    print(f"  [Solver Step: {param_name_to_solve}] Guess {param_name_to_solve} = {param_guess: .6f} -> FV: {current_fv/temp_params['NOM'] * 100.0: .4f}% -> Error: {error: .2f}")
    
    return error

# --- 4. Main entry point: Solve the three exercises in Q2 ---
if __name__ == "__main__":
    
    multiprocessing.freeze_support() 
    
    print(f"--- Executing: solver_ii.py (V3 - Aggressive search KI) ---")
    print("This script will *only* re-run Q2-B (Solving for KI).")
    print("-" * 50)
    print(f"Q1(i) CP1 Value: {CP1_VALUE:.6f} %")
    print(f"New coupon used for Q2 (CP_new): {CP_NEW:.6f} %")
    print(f"Target Fair Value (Cost): {TARGET_FV:,.2f} HKD")
    print("-" * 50)
    
    # Define base parameters (Q1 original values)
    base_params = hkd_params_prod
    
    # --- Exercise A: Solve for K0 (Skipped) ---
    print("\n" + "="*50)
    print(f"Exercise A: Solving for K0 (Skipped)")
    print("="*50)
    found_K0 = None # Skipped

    # --- Exercise B: Solve for KI ---
    # Fixed: CP=CP_new, K0=0.96, AC=0.99
    # Solve: KI
    print("\n" + "="*50)
    print(f"Exercise B: Solving for KI (Keep K0=0.96, AC=0.99)")
    
    # **** Bug Fix: Aggressively expand the lower bound of the search range ****
    # Previously, the FVs at both ends of the [0.70, 0.92] range were below the target
    # This means KI must drop below 0.70 for the FV to rise above 98.80%
    # We are expanding the lower bound from 0.70 to 0.50
    new_lower_bound = 0.50
    print(f"Search Range: [{new_lower_bound:.2f}, {base_params['KI']:.2f}]") 
    print("="*50)
    
    start_time = time.time()
    try:
        found_KI = brentq(
            generic_objective_function,
            a=new_lower_bound, # Use the new, aggressive lower bound
            b=base_params['KI'], # Original value as upper bound
            args=('KI', base_params, CP_NEW, TARGET_FV),
            xtol=1e-6
        )
        print(f"--- Exercise B Finished (Time: {time.time() - start_time:.2f}s) ---")
        print(f"==> Found new KI: {found_KI:.6f} (Original: {base_params['KI']})")
        print(f"==> Change: {found_KI - base_params['KI']:.6f}")
    except ValueError as e:
        print(f"--- Exercise B Solver FAILED: {e} ---")
        print(f"--- Failed even in the [{new_lower_bound}, {base_params['KI']}] range. ---")
        found_KI = None

    # --- Exercise C: Solve for AC (Skipped) ---
    print("\n" + "="*50)
    print(f"Exercise C: Solving for AC (Skipped)")
    print("="*50)
    found_AC = None # Skipped

    # --- Final Summary ---
    print("\n" + "="*60)
    print(f"--- Q2 Re-run KI Results (300,000 Paths) ---")
    if found_KI is not None:
        print(f"Exercise B (KI): {base_params['KI']: .4f} -> {found_KI: .6f} (Δ {found_KI - base_params['KI']:.6f})")
    else:
        print("Exercise B (KI): Failed to find solution.")
    print("="*60)