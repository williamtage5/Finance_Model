# F:\Learning_journal_at_CUHK\FTEC5610_Computational_Finance\Assignment\Assigenment2-3\solver_i.py
# (This script calculates the final answer for Q1)

import numpy as np
import time
from scipy.optimize import brentq # use this module for quick root finding
import multiprocessing  # Required for parallel processing

# Import the accelerated core pricing function. We use anthithetic variates and multiprocessing.
try:
    from calculate_fair_value import calculate_fair_value
except ImportError:
    print("Error: Could not import 'calculate_fair_value' function.")
    exit()

# Define parameter dictionary
hkd_params_prod = {
    'NOM': 100000.0, 'r_f': 0.0287, 'sigma_stock': 0.6039, 'S0': 11.08,
    'time_points': np.array([1/12, 2/12, 3/12, 4/12, 5/12, 0.5]),
    'num_paths': 300000,
    'K0': 0.96, 'KI': 0.92, 'AC': 0.99
}

# Define the objective function for the solver
def objective_function(cp_guess, params, product_type, target_fv):
    """
    This is the function for the brentq solver to optimize.
    It calculates: Fair_Value(cp_guess) - Target_Fair_Value
    """
    
    # Call the core pricing engine
    current_fv = calculate_fair_value(
        CP_guess=cp_guess, # cp_guess will be supplied by the solver
        params=params, 
        product_type=product_type
    )
    
    error = current_fv - target_fv # difference between current fair value and target fair value
    
    print(f"  [Solver Step] Guess CP: {cp_guess: .6f}% -> FV: {current_fv/params['NOM'] * 100.0: .4f}% -> Error: {error/params['NOM'] * 100.0: .4f}%")
    
    return error

# Main solver function
def solve_for_cp(params, product_type, target_margin, cp_min_guess=0.01, cp_max_guess=10.0):
    """
    target_margin: Bank's target margin (e.g., 0.012 for 1.20%)
    cp_min_guess: the lower bound for the solver search
    cp_max_guess: the upper bound for the solver search
    """
    
    target_fv_pct = 1.0 - target_margin
    target_fv = params['NOM'] * target_fv_pct # Target fair value in currency units
    
    print("\n" + "="*50)
    print(f"--- Starting Solver ---")
    print(f"Target Margin: {target_margin*100: .2f}%")
    print(f"Target Fair Value: {target_fv: ,.2f} ({target_fv_pct*100: .2f}%)")
    print(f"Product Type: {product_type}")
    print(f"Monte Carlo Paths: {params['num_paths']} (Parallel + Antithetic)")
    print(f"CP Search Range: [{cp_min_guess}%, {cp_max_guess}%]")
    print("="*50)
    
    start_time = time.time()
    
    try:
        found_cp = brentq(
            objective_function,
            a=cp_min_guess, # min guess coupon
            b=cp_max_guess, # max guess coupon 
            args=(params, product_type, target_fv),
            xtol=1e-5, # the first tolerance level for stopping criteria
            rtol=1e-5 # the second tolerance level
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
        print("Maybe adjust the search range?")
        return None

# --- 5. Main entry point: Solve Q1(i) and Q1(ii) ---
if __name__ == "__main__":
    
    # This line is necessary to prevent multiprocessing errors on Windows
    multiprocessing.freeze_support() 
    
    print(f"--- Executing: solver_i.py (Q1 Production) ---")
    print("This script will calculate the *exact* answers for Q1(i) and Q1(ii).")
    print("This may take a few minutes depending on your CPU cores.")
    
    # --- Solve Q1(i): HKD, 1.20% Margin ---
    cp_q1_i = solve_for_cp(
        params=hkd_params_prod,
        product_type='HKD',
        target_margin=0.0120  # 1.20%
    )
    
    # --- Solve Q1(ii): HKD, 1.60% Margin ---
    cp_q1_ii = solve_for_cp(
        params=hkd_params_prod,
        product_type='HKD',
        target_margin=0.0160  # 1.60%
    )

    print("\n" + "="*50)
    print("--- Q1 Final Answers (300,000 Paths) ---")
    
    if cp_q1_i is not None:
        print(f"Q1(i) [1.20% Margin] CP1 Value: {cp_q1_i: .6f} %")
        print("==> :))) Note this 'CP1' value, it is needed for Q2.")
    else:
        print("Q1(i) [1.20% Margin] failed to find a solution.")
        
    if cp_q1_ii is not None:
        print(f"Q1(ii) [1.60% Margin] CP Value: {cp_q1_ii: .6f} %")
    else:
        print("Q1(ii) [1.60% Margin] failed to find a solution.")
    print("="*60)