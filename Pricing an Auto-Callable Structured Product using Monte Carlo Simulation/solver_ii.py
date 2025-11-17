# F:\Learning_journal_at_CUHK\FTEC5610_Computational_Finance\Assignment\Assigenment2-3\solver_ii.py
# (This script calculates the final answer for Q2)

import numpy as np
import time
from scipy.optimize import brentq 
import multiprocessing
import copy # Used for deep copying the parameter dictionary

try:
    from calculate_fair_value import calculate_fair_value
except ImportError:
    print("="*50)
    print("Error: Could not import 'calculate_fair_value' function.")
    exit()

# Define parameters required for Q2

# Q1 "Production" level parameters (Our baseline)
hkd_params_prod = {
    'NOM': 100000.0, 'r_f': 0.0287, 'sigma_stock': 0.6039, 'S0': 11.08,
    'time_points': np.array([1/12, 2/12, 3/12, 4/12, 5/12, 0.5]),
    'num_paths': 300000, # Production paths
    'K0': 0.96, 'KI': 0.92, 'AC': 0.99
}

# Q2 Core known conditions
CP1_VALUE = 3.458654  # This is the value you obtained from Q1(i)
CP_NEW = CP1_VALUE - 0.10 # The demanded new coupon
TARGET_MARGIN = 0.0120 # 1.20%
TARGET_FV = hkd_params_prod['NOM'] * (1.0 - TARGET_MARGIN) # 98,800.00

# Define the generic objective function (Q2 specific)
def generic_objective_function(param_guess, param_name_to_solve, base_params, fixed_cp, target_fv):
    """
    Generic objective function, used to solve for K0, KI, or AC.
    
    param_guess: The new parameter value guessed by the solver (e.g., 0.95)
    param_name_to_solve: The name of the parameter to modify, which param to search (e.g., 'K0')
    base_params: Dictionary containing the original K0, KI, AC
    fixed_cp: The fixed new coupon (CP_new)
    target_fv: The target fair value (98,800)
    :return: Error (FV - Target)
    """
    
    # Create a copy of the parameters to avoid modifying the original dictionary
    temp_params = copy.deepcopy(base_params)
    
    # Set the "guessed value" in the dictionary
    temp_params[param_name_to_solve] = param_guess
    
    # Call the core pricing engine
    current_fv = calculate_fair_value(
        CP_guess=fixed_cp, # coupon is fixed
        params=temp_params, # the 3 changed params
        product_type='HKD'
    )
    
    # 4. Calculate the error
    error = current_fv - target_fv
    
    print(f"  [Solver Step: {param_name_to_solve}] Guess {param_name_to_solve} = {param_guess: .6f} -> FV: {current_fv/temp_params['NOM'] * 100.0: .4f}% -> Error: {error: .2f}")
    
    return error

# Main entry point: Solve the three exercises in Q2
if __name__ == "__main__":
    
    multiprocessing.freeze_support() 
    
    print(f"--- Executing: solver_ii.py (Q2 Production) ---")
    print("This script will calculate the three independent exercises for Q2.")
    print("Using 300,000 paths, this may take a few minutes...")
    print(f"Q1(i) CP1 Value: {CP1_VALUE:.6f} %")
    print(f"New coupon used for Q2 (CP_new): {CP_NEW:.6f} %")
    print(f"Target Margin: {TARGET_MARGIN*100:.2f} %")
    print(f"Target Fair Value (Cost): {TARGET_FV:,.2f} HKD")
    print("-" * 50)
    
    # Define base parameters (Q1 original values)
    base_params = hkd_params_prod
    
    # We will try to solve for K0, KI, and AC one by one.
    # Just like what we did before, we set a lower and upper bound, but this range is mannually defined.
    # If we fail to find a solution, we can always expand the range.
    # For example, I can not find the solution for K0, then I expand the bound and try in soler_ii_for_exception.py.


    # --- Exercise A: Solve for K0 ---
    # Fixed: CP=CP_new, KI=0.92, AC=0.99
    # Solve: K0
    # Expect: K0 < 0.96
    print("\n" + "="*50)
    print(f"Exercise A: Solving for K0 (Keep KI=0.92, AC=0.99)")
    print(f"Search Range: [0.80, {base_params['K0']}]") # Upper bound is the original value
    print("="*50)
    
    start_time = time.time()
    try:
        found_K0 = brentq(
            generic_objective_function,
            a=0.80, # Safe lower bound
            b=base_params['K0'], # Original value as upper bound
            args=('K0', base_params, CP_NEW, TARGET_FV),
            xtol=1e-6
        )
        print(f"--- Exercise A Finished (Time: {time.time() - start_time:.2f}s) ---")
        print(f"==> Found new K0: {found_K0:.6f} (Original: {base_params['K0']})")
        print(f"==> Change: {found_K0 - base_params['K0']:.6f}")
    except ValueError as e:
        print(f"--- Exercise A Solver FAILED: {e} ---")
        found_K0 = None

    # --- Exercise B: Solve for KI ---
    # Fixed: CP=CP_new, K0=0.96, AC=0.99
    # Solve: KI
    # Expect: KI < 0.92
    print("\n" + "="*50)
    print(f"Exercise B: Solving for KI (Keep K0=0.96, AC=0.99)")
    print(f"Search Range: [0.80, {base_params['KI']}]") # Upper bound is the original value
    print("="*50)
    
    start_time = time.time()
    try:
        found_KI = brentq(
            generic_objective_function,
            a=0.80, # Safe lower bound
            b=base_params['KI'], # Original value as upper bound
            args=('KI', base_params, CP_NEW, TARGET_FV),
            xtol=1e-6
        )
        print(f"--- Exercise B Finished (Time: {time.time() - start_time:.2f}s) ---")
        print(f"==> Found new KI: {found_KI:.6f} (Original: {base_params['KI']})")
        print(f"==> Change: {found_KI - base_params['KI']:.6f}")
    except ValueError as e:
        print(f"--- Exercise B Solver FAILED: {e} ---")
        found_KI = None

    # --- Exercise C: Solve for AC ---
    # Fixed: CP=CP_new, K0=0.96, KI=0.92
    # Solve: AC
    # Expect: AC < 0.99
    print("\n" + "="*50)
    print(f"Exercise C: Solving for AC (Keep K0=0.96, KI=0.92)")
    print(f"Search Range: [0.90, {base_params['AC']}]") # Upper bound is the original value
    print("="*50)
    
    start_time = time.time()
    try:
        found_AC = brentq(
            generic_objective_function,
            a=0.90, # Safe lower bound (AC unlikely to be lower than K0)
            b=base_params['AC'], # Original value as upper bound
            args=('AC', base_params, CP_NEW, TARGET_FV),
            xtol=1e-6
        )
        print(f"--- Exercise C Finished (Time: {time.time() - start_time:.2f}s) ---")
        print(f"==> Found new AC: {found_AC:.6f} (Original: {base_params['AC']})")
        print(f"==> Change: {found_AC - base_params['AC']:.6f}")
    except ValueError as e:
        print(f"--- Exercise C Solver FAILED: {e} ---")
        found_AC = None

    # --- Final Summary ---
    print("\n" + "="*60)
    print(f"--- Q2 Final Answers (300,000 Paths) ---")
    print(f"Original CP1: {CP1_VALUE:.6f}% | New CP_new: {CP_NEW:.6f}% (Δ -0.10%)")
    print(f"Target Fair Value: {TARGET_FV:,.2f} HKD (1.20% Margin)")
    print("-" * 60)
    if found_K0 is not None:
        print(f"Exercise A (K0): {base_params['K0']: .4f} -> {found_K0: .6f} (Δ {found_K0 - base_params['K0']:.6f})")
    else:
        print("Exercise A (K0): Failed to find solution.")
        
    if found_KI is not None:
        print(f"Exercise B (KI): {base_params['KI']: .4f} -> {found_KI: .6f} (Δ {found_KI - base_params['KI']:.6f})")
    else:
        print("Exercise B (KI): Failed to find solution.")

    if found_AC is not None:
        print(f"Exercise C (AC): {base_params['AC']: .4f} -> {found_AC: .6f} (Δ {found_AC - base_params['AC']:.6f})")
    else:
        print("Exercise C (AC): Failed to find solution.")
    print("="*60)