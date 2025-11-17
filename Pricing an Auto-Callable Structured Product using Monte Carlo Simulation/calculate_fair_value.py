# F:\Learning_journal_at_CUHK\FTEC5610_Computational_Finance\Assignment\Assigenment2-3\calculate_fair_value.py
# In this simulation, we use Antithetic Variates with Multiprocessing to speed up the Monte Carlo simulation.

import numpy as np
import warnings
import multiprocessing # Import this module for parallel processing
import time

warnings.filterwarnings('ignore')

# This fuction is a process worker MC simulation chunk, which will be run by one CPU core.
def run_simulation_chunk(args):

    # Unpack arguments
    # num_paires is the number of antithetic pairs to simulate in this chunk
    num_pairs, CP_rate, r_g, r_disc, params = args
    
    NOM = params['NOM']
    S0 = params['S0']
    sigma = params['sigma_stock']
    
    K0_pct = params['K0']
    KI_pct = params['KI']
    AC_pct = params['AC']

    T = 0.5 # Refer to: Expiry date (T): t + 1/2 year
    N = 180 # Refer to: For example, if the expiry date of the product is 6 months, use 180 time steps.
    dt = T / N # dt is crucial for GBM path generation
    
    # Retrieves the time_points array from the params dictionary and stores it in the coupon_times variable for later use
    coupon_times = params['time_points']
    # coupon_times / T is every coupon time as a fraction of total time T
    # coupon_times / T * N is to convert these fractions into discrete time steps
    coupon_steps = (coupon_times / T * N).astype(int)

    # Define the first autocall time
    first_autocall_step = coupon_steps[0] # Refer to: First auto-call date (Dc): t + 1/12 year
    # Creates a complete array of all interest period "boundary points"
    # [0, 30, 60, 90, 120, 150, 180]
    all_period_boundaries = np.union1d([0, N], coupon_steps).astype(int)
    
    # Knock-in Price
    P_K = S0 * KI_pct
    # Auto-Call Price
    P_C = S0 * AC_pct
    # Strick Price at Maturity
    K = S0 * K0_pct
    
    # Accumulator for this chunk's total payoff
    chunk_payoff_accumulator = 0.0

    # genrate antithetic variable paths
    for _ in range(num_pairs):
        
        # generate Z, representing the "random shock"  for each day of the stock's future 180-day path
        Z = np.random.standard_normal(N)
        paths_Z = [Z, -Z] # antithetic pair
        
        # calculate the payoff for both paths in the antithetic pair
        for z_vector in paths_Z:
            
            path_total_cost = 0.0
            knock_in_occurred = False
            product_terminated_early = False

            # A. generate the stock pirce path
            # Refer to: dS = r_g S dt + \sigma S Z \sqrt{dt}
            S_path = np.zeros(N + 1) # We need to store 181 price points. Points 1 to 180: The future 180 simulated daily prices.
            S_path[0] = S0 # Initial the first price
            # calculate every day point price
            for i in range(N):
                dS = r_g * S_path[i] * dt + sigma * S_path[i] * z_vector[i] * np.sqrt(dt) # z_vector[i] is the random shock for day i
                S_path[i+1] = S_path[i] + dS # later date prce is previous date price + change
            # When we simulate every path, we can then use every path to calculate the payoff.

            # B. Check: Knock-in event
            if np.min(S_path[1:]) < P_K:
                knock_in_occurred = True

            # C. Check each step for auto-call and coupon payments
            for step in range(1, N + 1):
                # price
                current_price = S_path[step]
                # transform step to annual time
                current_time = step * dt

                # Check for auto-call
                # This part is to simulate Early termination condition
                # auto call condition, the two condition must be simultaneously sastisfied: 
                # (1) Is today (step) on or after the first_autocall_step (day 30)? 
                # (2) Is the current_price greater than or equal to the auto-call price (P_C)?
                if step >= first_autocall_step and current_price >= P_C:
                    # Tell the code that this path has "terminated early".
                    product_terminated_early = True
                    # Investor will receive NOM first, then based on it, we can add interest.
                    payoff = NOM
                    
                    # The accrued interest refer to:
                    # Investor receives NOM + accrued interest... Accrued interest = NOM * CP% * num_days / total_days, where num_days = number of days between the call date and the coupon date immediately preceding the call date total_days = number of days between the coupon dates immediately preceding and following the call date

                    # Becauese there are different coupon periods and action, we have to calculate wchih coupon period we are in.
                    period_index = np.searchsorted(all_period_boundaries, step, side='left') - 1
                    # Find the preceding and next coupon step boundaries
                    preceding_coupon_step = all_period_boundaries[period_index]
                    next_coupon_step = all_period_boundaries[period_index + 1]
                    
                    # denominator: how many days have actually passed within this period?
                    num_steps = step - preceding_coupon_step
                    # nominator: what is the total length of this interest period?
                    total_steps = next_coupon_step - preceding_coupon_step
                    
                    # Nominal * CouponRate * (Days_Passed / Total_Days)
                    accrued_interest = NOM * CP_rate * (num_steps / total_steps)
                    # NOM + Accurued Interest
                    payoff += accrued_interest
                    
                    # Discount from current to present
                    discount_factor = np.exp(-r_disc * current_time)
                    path_total_cost = payoff * discount_factor
                    break 

                # This part is to simulate Coupons to be paid to investor in 6 coupon dates
                # calculate the coupon payment if the date is a coupon date
                if step in coupon_steps and step < N: # The last coupon payment at expiry is handled separately in the next section
                    payoff = NOM * CP_rate # NOM * CP%
                    discount_factor = np.exp(-r_disc * current_time) # transdorm to present value
                    path_total_cost += payoff * discount_factor # accumulate the coupon payment

            # This part is to simulate Payoff at expiry if the product has not terminated early, the terminated date is defined as before.
            if not product_terminated_early: # If the product is not terminated early
                T_expiry = T # Sets a variable T_expiry to the total tenor T (which is 0.5 years).
                discount_factor_expiry = np.exp(-r_disc * T_expiry) # Discount factor from expiry to present
                S_M = S_path[N] # Gets the final step (step 180, N=180) price from the simulation path S_path.

                payoff_coupon = NOM * CP_rate # Calculates the final coupon amount.
                path_total_cost += payoff_coupon * discount_factor_expiry # Add to the cosy total cost

                principal_payoff = 0.0
                if not knock_in_occurred: # knock_in_occurred is checked in section B, where check the whole fluctuation path
                    principal_payoff = NOM # Refer to: If a knock-in event has not occurred, then investor receives NOM
                else: # If a knock-in event has occurred
                    if S_M >= K:
                        principal_payoff = NOM # Refer to: if... S_M is greater than or equal to the strike price K, ... receives NOM
                    else:
                        principal_payoff = NOM * S_M / K # Refer to: The investor receives NOM * S_M / K”
                
                # Finally, add the principal payoff at expiry to the total cost
                path_total_cost += principal_payoff * discount_factor_expiry

            # E. Accumulate the total cost for this path into the chunk accumulator, for the MC average calculation later
            chunk_payoff_accumulator += path_total_cost
    
    # return the total payoff accumulated in this chunk
    return chunk_payoff_accumulator


# Calculate fair value through Monte Carlo simulation with Antithetic Variates and Multiprocessing
def calculate_fair_value(CP_guess, params, product_type='HKD'): 
    # product_type can be 'HKD' or 'Quanto'
    # CP_guess is a persentage, which is a guess of the coupon rate, beacause we guess and validate the coupon, and finally find the right coupon

    # load the nomber of paths
    num_paths = params['num_paths']
    
    # Becaues we ues antithetic variates, each "pair" consists of 2 paths
    num_pairs = num_paths // 2 
    
    CP_rate = CP_guess / 100.0 # Because CP_guess is given in percentage, we need to convert it to decimal for calculation

    if product_type == 'HKD':
        # Refer to: We can set $r_g = r_f$... $r_{disc} = r_f$
        r_g = params['r_f'] 
        r_disc = params['r_f']
    elif product_type == 'Quanto':
        # Refer to: n option on Hang Seng Index that pays CNY... We can set $r_g = r_f + \rho \sigma_S \sigma_{fx}$ ...$r_{disc} = r_d$
        r_g = params['r_f'] + params['rho'] * params['sigma_stock'] * params['sigma_fx']
        r_disc = params['r_d']
    else:
        raise ValueError("product_type in this senario must be 'HKD' or 'Quanto'")

    # Excute the parallel simulations
    num_cores = multiprocessing.cpu_count() # Get the number of available CPU cores
    # Ensure at least one pair per core
    pairs_per_core = max(1, num_pairs // num_cores) 
    
    # (num_pairs, CP_rate, r_g, r_disc, params)
    args_list = []
    
    # Allocate pairs to each core
    remaining_pairs = num_pairs
    for i in range(num_cores):
        # Ensure the last core takes any remaining pairs
        pairs_to_run = min(pairs_per_core, remaining_pairs)
        if i == num_cores - 1: # The last core to take all remaining pairs
            pairs_to_run = remaining_pairs
            
        if pairs_to_run > 0:
            args_list.append((pairs_to_run, CP_rate, r_g, r_disc, params)) # Add the argument tuple for this core, except the last core
            remaining_pairs -= pairs_to_run
        
        if remaining_pairs <= 0:
            break
            

    total_payoff_accumulator = 0.0
    
    try:
        with multiprocessing.Pool(processes=num_cores) as pool:
            results = pool.map(run_simulation_chunk, args_list) # Run simulations in parallel across multiple CPU cores
        
        # grand total discounted cost of all 300,000 paths
        total_payoff_accumulator = sum(results)

    except Exception as e:
        print(f"There are some error in parallel simulations: {e}")
        return 0.0

    # Average cost across all simulated paths
    average_cost = total_payoff_accumulator / (num_pairs * 2) 
    
    return average_cost

if __name__ == "__main__":
    
    print(f"--- Test 'calculate_fair_value'  ---")
    print("-" * 50)
    
    hkd_params_test = {
        'NOM': 100000.0, 'r_f': 0.0287, 'sigma_stock': 0.6039, 'S0': 11.08,
        'time_points': np.array([1/12, 2/12, 3/12, 4/12, 5/12, 0.5]),
        'num_paths': 30000, # Main, when you want to test for the first time, you can set a smaller number of this parameter
        'K0': 0.96, 'KI': 0.92, 'AC': 0.99
    }
    
    test_cp = 0.5 
    print(f"Test config para: {hkd_params_test}")
    print(f"Test coupon rate (CP_guess): {test_cp:.2f}% per month")
    print(f"The programme is running {hkd_params_test['num_paths']} MC simulation with {multiprocessing.cpu_count()} cpu(s)...")
    
    start_time = time.time()
    fair_value = calculate_fair_value(test_cp, hkd_params_test, product_type='HKD')
    end_time = time.time()
    
    fv_percent = (fair_value / hkd_params_test['NOM']) * 100.0
    
    print(f"Total time cost: {end_time - start_time:.2f} seconds")
    print(f"Test Fair Value: {fair_value:,.2f} HKD")
    print(f"Test Fair Value persentage: {fv_percent:.4f} %")
    print("-" * 50)