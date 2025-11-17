# F:\Learning_journal_at_CUHK\FTEC5610_Computational_Finance\Assignment\Assigenment2-3\solver_i.py
# (此脚本用于计算 Q1 的最终答案)

import numpy as np
import time
from scipy.optimize import brentq 
import multiprocessing # <--- **** 错误修复: 添加这一行 ****

# --- 1. 导入您的 *加速版* 核心定价函数 ---
try:
    from calculate_fair_value import calculate_fair_value
    print("成功导入 'calculate_fair_value' (V3-并行版)。\n")
except ImportError:
    print("="*50)
    print("错误: 无法导入 'calculate_fair_value' 函数。")
    print("请确保 'calculate_fair_value.py' (V3版) 和 'solver_i.py' 在同一目录下。")
    print("="*50)
    exit()

# --- 2. 定义参数字典 ---

# “生产” (Production) 级别参数 (用于最终答案)
hkd_params_prod = {
    'NOM': 100000.0, 'r_f': 0.0287, 'sigma_stock': 0.6039, 'S0': 11.08,
    'time_points': np.array([1/12, 2/12, 3/12, 4/12, 5/12, 0.5]),
    'num_paths': 300000, # 生产环境路径
    'K0': 0.96, 'KI': 0.92, 'AC': 0.99
}

# (Q3 Quanto "生产" 参数 - 供您后续使用)
quanto_params_prod = {
    'NOM': 100000.0, 'r_d': 0.0169, 'r_f': 0.0287, 'sigma_stock': 0.6039,
    'S0': 11.08, 'time_points': np.array([1/12, 2/12, 3/12, 4/12, 5/12, 0.5]),
    'num_paths': 300000, 'K0': 0.96, 'KI': 0.92, 'AC': 0.99,
    'sigma_fx': 0.074, 'rho': 0.42
}


# --- 3. 定义求解器所需的目标函数 ---

def objective_function(cp_guess, params, product_type, target_fv):
    """
    这是 brentq 求解器要优化的函数。
    它计算: Fair_Value(cp_guess) - Target_Fair_Value
    """
    
    # 调用您的核心定价引擎 (V3 并行版)
    current_fv = calculate_fair_value(
        CP_guess=cp_guess, 
        params=params, 
        product_type=product_type
    )
    
    error = current_fv - target_fv
    
    print(f"  [Solver Step] 猜想 CP: {cp_guess: .6f}% -> FV: {current_fv/params['NOM'] * 100.0: .4f}% -> 误差: {error/params['NOM'] * 100.0: .4f}%")
    
    return error

# --- 4. 主求解器函数 ---
def solve_for_cp(params, product_type, target_margin, cp_min_guess=0.01, cp_max_guess=10.0):
    """
    一个完整的求解器函数，用于寻找 CP。
    我们将搜索区间扩大到 10.0%, 因为高波动性可能需要高票息。
    """
    
    target_fv_pct = 1.0 - target_margin
    target_fv = params['NOM'] * target_fv_pct
    
    print("\n" + "="*50)
    print(f"--- 正在启动求解器 (生产模式) ---")
    print(f"目标利润率: {target_margin*100: .2f}%")
    print(f"目标公允价值: {target_fv: ,.2f} ({target_fv_pct*100: .2f}%)")
    print(f"产品类型: {product_type}")
    print(f"蒙特卡洛路径: {params['num_paths']} (已启用并行 + 对偶变量)")
    print(f"CP 搜索区间: [{cp_min_guess}%, {cp_max_guess}%]")
    print("="*50)
    
    start_time = time.time()
    
    try:
        found_cp = brentq(
            objective_function,
            a=cp_min_guess,
            b=cp_max_guess,
            args=(params, product_type, target_fv),
            xtol=1e-5,
            rtol=1e-5
        )
        
        end_time = time.time()
        print("--- 求解器完成 ---")
        print(f"总计用时: {end_time - start_time: .2f} 秒.")
        print(f"==> 求解得到的每月票息 (CP): {found_cp: .6f} %")
        print("="*50)
        
        return found_cp

    except ValueError as e:
        print(f"--- 求解器失败 ---")
        print(f"错误: {e}")
        print("f(a) 和 f(b) 的误差符号相同。")
        print("请尝试在 'solve_for_cp' 函数中进一步扩大 'cp_max_guess' (例如: 15.0)。")
        return None

# --- 5. Main 入口: 求解 Q1(i) 和 Q1(ii) ---
if __name__ == "__main__":
    
    # 这一行对于防止多进程在 Windows 上出错是必需的
    multiprocessing.freeze_support() 
    
    print(f"--- 正在执行: solver_i.py (Q1 生产版) ---")
    print("本脚本将计算 Q1(i) 和 Q1(ii) 的 *精确* 答案。")
    print("这可能需要几分钟时间，具体取决于您的 CPU 核心数。")
    
    # --- 求解 Q1(i): HKD, 1.20% 利润率 ---
    # !! 使用生产参数 !!
    cp_q1_i = solve_for_cp(
        params=hkd_params_prod,
        product_type='HKD',
        target_margin=0.0120     # 1.20%
    )
    
    # --- 求解 Q1(ii): HKD, 1.60% 利润率 ---
    # !! 使用生产参数 !!
    cp_q1_ii = solve_for_cp(
        params=hkd_params_prod,
        product_type='HKD',
        target_margin=0.0160    # 1.60%
    )

    print("\n" + "="*60)
    print("--- Q1 最终答案 (300,000 路径) ---")
    
    if cp_q1_i is not None:
        print(f"Q1(i) [1.20% 利润] 的 CP1 值为: {cp_q1_i: .6f} %")
        print("==> (请记下这个 'CP1' 值，Q2 需要它)")
    else:
        print("Q1(i) [1.20% 利润] 未能找到解。")
        
    if cp_q1_ii is not None:
        print(f"Q1(ii) [1.60% 利润] 的 CP 值为: {cp_q1_ii: .6f} %")
    else:
        print("Q1(ii) [1.60% 利润] 未能找到解。")
    print("="*60)