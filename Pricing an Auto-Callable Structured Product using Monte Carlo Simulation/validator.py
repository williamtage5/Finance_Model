# F:\Learning_journal_at_CUHK\FTEC5610_Computational_Finance\Assignment\Assigenment2-3\validator.py
# (This script is used to validate all final answers for Q1, Q2, Q3)

import numpy as np
import time
import multiprocessing 
import copy # For deep copying parameter dictionaries

# --- 1. Import the *accelerated* core pricing function ---
try:
    from calculate_fair_value import calculate_fair_value
except ImportError:
    print("Please ensure 'calculate_fair_value.py' (V3) and 'validator.py' are in the same directory.")
    exit()

# --- 2. Define Base Parameter Dictionaries ---

# Q1/Q2 Base "Production" Parameters
hkd_params_prod = {
    'NOM': 100000.0, 'r_f': 0.0287, 'sigma_stock': 0.6039, 'S0': 11.08,
    'time_points': np.array([1/12, 2/12, 3/12, 4/12, 5/12, 0.5]),
    'num_paths': 300000, # Must use production path count
    'K0': 0.96, 'KI': 0.92, 'AC': 0.99
}

# Q3 Base "Production" Parameters
quanto_params_prod = {
    'NOM': 100000.0, 'S0': 11.08, 'sigma_stock': 0.6039,
    'K0': 0.96, 'KI': 0.92, 'AC': 0.99,
    'time_points': np.array([1/12, 2/12, 3/12, 4/12, 5/12, 0.5]),
    'num_paths': 300000,
    'r_d': 0.0169, 'r_f': 0.0287, 'sigma_fx': 0.074, 'rho': 0.42
}

# --- 3. Define a general validation helper function ---

def validate_run(description, cp_to_test, params, product_type, target_margin_pct):
    """
    Run one simulation and print the validation results
    """
    print("\n" + "="*60)
    print(f"--- Validating: {description} ---")
    
    NOM = params['NOM']
    target_margin_rate = target_margin_pct / 100.0
    target_fv_pct = 100.0 - target_margin_pct
    target_fv = NOM * (1.0 - target_margin_rate)

    print(f"Parameters: CP={cp_to_test:.6f}%, {product_type}")
    if 'K0' != hkd_params_prod['K0']: print(f"      K0={params['K0']:.6f}")
    if 'KI' != hkd_params_prod['KI']: print(f"      KI={params['KI']:.6f}")
    if 'AC' != hkd_params_prod['AC']: print(f"      AC={params['AC']:.6f}")
    print(f"Path Count: {params['num_paths']}")
    print(f"Target Margin: {target_margin_pct:.2f}% (Target FV: {target_fv_pct:.4f}%)")
    
    start_time = time.time()
    
    # --- Running Pricer ---
    calculated_fv = calculate_fair_value(
        CP_guess=cp_to_test,
        params=params,
        product_type=product_type
    )
    
    end_time = time.time()
    
    # --- Analyzing Results ---
    calculated_fv_pct = (calculated_fv / NOM) * 100.0
    calculated_margin_pct = 100.0 - calculated_fv_pct
    error_pct = calculated_fv_pct - target_fv_pct # (Error in FV)
    
    print("-" * 60)
    print(f"Validation Time: {end_time - start_time:.2f} seconds")
    print(f"Calculated Fair Value (FV): {calculated_fv_pct:.4f}%")
    print(f"Calculated Margin: {calculated_margin_pct:.4f}%")
    print("-" * 60)
    print(f"==> Result: Target Margin {target_margin_pct:.2f}%, Actual Margin {calculated_margin_pct:.4f}%")
    print(f"==> Fair Value Error (Actual - Target): {error_pct:.4f}%")
    
    if abs(error_pct) > 0.02: # Allowing 0.02% error for MC noise
        print("==> WARNING: Large error. Please check answers or MC noise.")
    else:
        print("==> Conclusion: Validation PASSED.")
    print("="*60)


# --- 4. Main entry point: Run all 7 validations ---
if __name__ == "__main__":
    
    multiprocessing.freeze_support() 
    
    print(f"--- Executing: validator.py (Q1, Q2, Q3 Final Validation) ---")
    print("This script will re-run all final answers using 300,000 paths...")

    # --- Final Answers (extracted from your logs) ---
    CP_Q1_I  = 3.458654
    CP_Q1_II = 3.206363
    
    CP_Q2 = CP_Q1_I - 0.10 # = 3.358654
    K0_Q2_A = 0.946917
    KI_Q2_B = 0.657667
    AC_Q2_C = 0.981261
    
    CP_Q3_I  = 3.262929
    CP_Q3_II = 3.015741
    # --- End of Answer Definitions ---
    
    
    # --- Q1 Validation ---
    validate_run(
        "Q1(i) [1.20% Margin]", 
        CP_Q1_I, hkd_params_prod, "HKD", 1.20
    )
    validate_run(
        "Q1(ii) [1.60% Margin]", 
        CP_Q1_II, hkd_params_prod, "HKD", 1.60
    )
    
    # --- Q2 Validation ---
    # Exercise A (K0)
    params_q2a = copy.deepcopy(hkd_params_prod)
    params_q2a['K0'] = K0_Q2_A
    validate_run(
        "Q2(A) [1.20% Margin, new K0]",
        CP_Q2, params_q2a, "HKD", 1.20
    )
    
    # Exercise B (KI)
    params_q2b = copy.deepcopy(hkd_params_prod)
    params_q2b['KI'] = KI_Q2_B
    validate_run(
        "Q2(B) [1.20% Margin, new KI]",
        CP_Q2, params_q2b, "HKD", 1.20
    )
    
    # Exercise C (AC)
    params_q2c = copy.deepcopy(hkd_params_prod)
    params_q2c['AC'] = AC_Q2_C
    validate_run(
        "Q2(C) [1.20% Margin, new AC]",
        CP_Q2, params_q2c, "HKD", 1.20
    )
    
    # --- Q3 Validation ---
    validate_run(
        "Q3(i) [1.20% Margin, Quanto]",
        CP_Q3_I, quanto_params_prod, "Quanto", 1.20
    )
    validate_run(
        "Q3(ii) [1.60% Margin, Quanto]",
        CP_Q3_II, quanto_params_prod, "Quanto", 1.60
    )

    print("\n--- All Validations Complete ---")