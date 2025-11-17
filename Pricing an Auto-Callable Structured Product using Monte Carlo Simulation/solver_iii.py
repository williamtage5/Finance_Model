# F:\Learning_journal_at_CUHK\FTEC5610_Computational_Finance\Assignment\Assigenment2-3\solver_iii.py
# (此脚本用于计算 Q3 的最终答案)

import numpy as np
import time
from scipy.optimize import brentq 
import multiprocessing 

# --- 1. 导入您的 *加速版* 核心定价函数 ---
try:
    from calculate_fair_value import calculate_fair_value
    print("成功导入 'calculate_fair_value' (V3-并行版)。\n")
except ImportError:
    print("="*50)
    print("错误: 无法导入 'calculate_fair_value' 函数。")
    print("请确保 'calculate_fair_value.py' (V3版) 和 'solver_iii.py' 在同一目录下。")
    print("="*50)
    exit()

# --- 2. 定义 Q3 所需的参数 ---

# Q3 Quanto "生产" 级别参数
# (注意: 我们从 Q1 的 hkd_params 复制了基础值, 并添加了 Quanto 特定的键)
quanto_params_prod = {
    'NOM': 100000.0,          # 100,000 CNY
    'S0': 11.08,              # 股票 S1 初始价 (HKD)
    'sigma_stock': 0.6039,    # 股票 S1 波动率
    'K0': 0.96,
    'KI': 0.92,
    'AC': 0.99,
    'time_points': np.array([1/12, 2/12, 3/12, 4/12, 5/12, 0.5]),
    'num_paths': 300000,
    
    # --- Quanto 特定的新参数 ---
    'r_d': 0.0169,            # CNY 利率 (用于贴现 r_disc)
    'r_f': 0.0287,            # HKD 利率 (用于漂移率 r_g)
    'sigma_fx': 0.074,        # 汇率波动率
    'rho': 0.42               # 股票与汇率的相关性
}


# --- 3. 定义求解器所需的目标函数 (与 solver_i.py 中完全相同) ---

def objective_function(cp_guess, params, product_type, target_fv):
    """
    这是 brentq 求解器要优化的函数。
    它计算: Fair_Value(cp_guess) - Target_Fair_Value
    """
    
    # 调用您的核心定价引擎 (V3 并行版)
    current_fv = calculate_fair_value(
        CP_guess=cp_guess, 
        params=params, 
        product_type=product_type # 这里将被传入 'Quanto'
    )
    
    error = current_fv - target_fv
    
    print(f"  [Solver Step] 猜想 CP: {cp_guess: .6f}% -> FV: {current_fv/params['NOM'] * 100.0: .4f}% -> 误差: {error/params['NOM'] * 100.0: .4f}%")
    
    return error

# --- 4. 主求解器函数 (与 solver_i.py 中完全相同) ---
def solve_for_cp(params, product_type, target_margin, cp_min_guess=0.01, cp_max_guess=10.0):
    """
    一个完整的求解器函数，用于寻找 CP。
    """
    
    target_fv_pct = 1.0 - target_margin
    target_fv = params['NOM'] * target_fv_pct
    
    print("\n" + "="*50)
    print(f"--- 正在启动求解器 (生产模式) ---")
    print(f"目标利润率: {target_margin*100: .2f}%")
    print(f"目标公允价值: {target_fv: ,.2f} ({target_fv_pct*100: .2f}%)")
    print(f"产品类型: {product_type}") # <--- 这里会打印 'Quanto'
    print(f"蒙特卡洛路径: {params['num_paths']} (已启用并行 + 对偶变量)")
    print(f"CP 搜索区间: [{cp_min_guess}%, {cp_max_guess}%]")
    print("="*50)
    
    start_time = time.time()
    
    try:
        found_cp = brentq(
            objective_function,
            a=cp_min_guess,
            b=cp_max_guess,
            args=(params, product_type, target_fv), # 关键: 传入 'Quanto'
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

# --- 5. Main 入口: 求解 Q3(i) 和 Q3(ii) ---
if __name__ == "__main__":
    
    multiprocessing.freeze_support() 
    
    print(f"--- 正在执行: solver_iii.py (Q3 生产版) ---")
    print("本脚本将计算 Q3(i) 和 Q3(ii) (Quanto 版本) 的 *精确* 答案。")
    print("这可能需要几分钟时间。")
    
    # --- 求解 Q3(i): Quanto, 1.20% 利润率 ---
    # !! 使用 Quanto 参数 和 'Quanto' 类型 !!
    cp_q3_i = solve_for_cp(
        params=quanto_params_prod,
        product_type='Quanto',       # <--- 关键
        target_margin=0.0120     # 1.20%
    )
    
    # --- 求解 Q3(ii): Quanto, 1.60% 利润率 ---
    # !! 使用 Quanto 参数 和 'Quanto' 类型 !!
    cp_q3_ii = solve_for_cp(
        params=quanto_params_prod,
        product_type='Quanto',       # <--- 关键
        target_margin=0.0160    # 1.60%
    )

    print("\n" + "="*60)
    print("--- Q3 最终答案 (300,000 路径, Quanto) ---")
    
    if cp_q3_i is not None:
        print(f"Q3(i) [1.20% 利润] 的 CP 值为: {cp_q3_i: .6f} %")
    else:
        print("Q3(i) [1.20% 利润] 未能找到解。")
        
    if cp_q3_ii is not None:
        print(f"Q3(ii) [1.60% 利润] 的 CP 值为: {cp_q3_ii: .6f} %")
    else:
        print("Q3(ii) [1.60% 利润] 未能找到解。")
    print("="*60)