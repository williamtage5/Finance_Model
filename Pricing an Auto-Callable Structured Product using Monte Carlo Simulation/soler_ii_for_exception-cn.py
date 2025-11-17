# F:\Learning_journal_at_CUHK\FTEC5610_Computational_Finance\Assignment\Assigenment2-3\solver_ii.py
# (此脚本用于计算 Q2 的最终答案 - V3: 激进搜索 KI)

import numpy as np
import time
from scipy.optimize import brentq 
import multiprocessing
import copy 

# --- 1. 导入您的 *加速版* 核心定价函数 ---
try:
    from calculate_fair_value import calculate_fair_value
    print("成功导入 'calculate_fair_value' (V3-并行版)。\n")
except ImportError:
    print("="*50)
    print("错误: 无法导入 'calculate_fair_value' 函数。")
    print("请确保 'calculate_fair_value.py' (V3版) 和 'solver_ii.py' 在同一目录下。")
    print("="*50)
    exit()

# --- 2. 定义 Q2 所需的参数 ---

# Q1 的“生产”级别参数 (我们的基准)
hkd_params_prod = {
    'NOM': 100000.0, 'r_f': 0.0287, 'sigma_stock': 0.6039, 'S0': 11.08,
    'time_points': np.array([1/12, 2/12, 3/12, 4/12, 5/12, 0.5]),
    'num_paths': 300000, # 生产环境路径
    'K0': 0.96, 'KI': 0.92, 'AC': 0.99
}

# --- Q2 的核心已知条件 ---
CP1_VALUE = 3.458654  # 这是您从 Q1(i) 获得的值
CP_NEW = CP1_VALUE - 0.10
TARGET_MARGIN = 0.0120 # 1.20%
TARGET_FV = hkd_params_prod['NOM'] * (1.0 - TARGET_MARGIN) # 98,800.00

# --- 3. 定义通用的目标函数 (Q2 专用) ---

def generic_objective_function(param_guess, param_name_to_solve, base_params, fixed_cp, target_fv):
    """
    通用的目标函数, 用于求解 K0, KI, 或 AC。
    """
    
    temp_params = copy.deepcopy(base_params)
    temp_params[param_name_to_solve] = param_guess
    
    current_fv = calculate_fair_value(
        CP_guess=fixed_cp, 
        params=temp_params, 
        product_type='HKD'
    )
    
    error = current_fv - target_fv
    
    print(f"  [Solver Step: {param_name_to_solve}] 猜想 {param_name_to_solve} = {param_guess: .6f} -> FV: {current_fv/temp_params['NOM'] * 100.0: .4f}% -> 误差: {error: .2f}")
    
    return error

# --- 4. Main 入口: 求解 Q2 的三个练习 ---
if __name__ == "__main__":
    
    multiprocessing.freeze_support() 
    
    print(f"--- 正在执行: solver_ii.py (V3 - 激进搜索 KI) ---")
    print("本脚本将 *仅* 重新运行 Q2-B (求解 KI)。")
    print("-" * 50)
    print(f"Q1(i) 的 CP1 值为: {CP1_VALUE:.6f} %")
    print(f"Q2 使用的新票息 (CP_new): {CP_NEW:.6f} %")
    print(f"目标公允价值 (成本): {TARGET_FV:,.2f} HKD")
    print("-" * 50)
    
    # 定义基础参数 (Q1的原始值)
    base_params = hkd_params_prod
    
    # --- 练习 A: 求解 K0 (已跳过) ---
    print("\n" + "="*50)
    print(f"练习 A: 求解 K0 (已跳过)")
    print("="*50)
    found_K0 = None # 跳过

    # --- 练习 B: 求解 KI ---
    # 固定: CP=CP_new, K0=0.96, AC=0.99
    # 求解: KI
    print("\n" + "="*50)
    print(f"练习 B: 求解 KI (保持 K0=0.96, AC=0.99)")
    
    # **** 错误修复: 激进地扩大搜索区间的下界 ****
    # 之前 [0.70, 0.92] 区间两端的 FV 都低于目标值
    # 这意味着 KI 必须降到 0.70 以下才能让 FV 升过 98.80%
    # 我们将下界从 0.70 扩大到 0.50
    new_lower_bound = 0.50
    print(f"搜索区间: [{new_lower_bound:.2f}, {base_params['KI']:.2f}]") 
    print("="*50)
    
    start_time = time.time()
    try:
        found_KI = brentq(
            generic_objective_function,
            a=new_lower_bound, # 使用新的、激进的下界
            b=base_params['KI'], # 原始值作为上界
            args=('KI', base_params, CP_NEW, TARGET_FV),
            xtol=1e-6
        )
        print(f"--- 练习 B 完成 (用时: {time.time() - start_time:.2f}s) ---")
        print(f"==> 找到的新 KI: {found_KI:.6f} (原始值: {base_params['KI']})")
        print(f"==> 变化量: {found_KI - base_params['KI']:.6f}")
    except ValueError as e:
        print(f"--- 练习 B 求解失败: {e} ---")
        print(f"--- 即使在 [{new_lower_bound}, {base_params['KI']}] 区间也失败了。---")
        found_KI = None

    # --- 练习 C: 求解 AC (已跳过) ---
    print("\n" + "="*50)
    print(f"练习 C: 求解 AC (已跳过)")
    print("="*50)
    found_AC = None # 跳过

    # --- 最终总结 ---
    print("\n" + "="*60)
    print(f"--- Q2 重试 KI 结果 (300,000 路径) ---")
    if found_KI is not None:
        print(f"练习 B (KI): {base_params['KI']: .4f} -> {found_KI: .6f} (Δ {found_KI - base_params['KI']:.6f})")
    else:
        print("练习 B (KI): 未能找到解。")
    print("="*60)