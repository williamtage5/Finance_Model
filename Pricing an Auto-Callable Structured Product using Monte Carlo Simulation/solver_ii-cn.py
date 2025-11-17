# F:\Learning_journal_at_CUHK\FTEC5610_Computational_Finance\Assignment\Assigenment2-3\solver_ii.py
# (此脚本用于计算 Q2 的最终答案)

import numpy as np
import time
from scipy.optimize import brentq 
import multiprocessing
import copy # 用于深拷贝参数字典

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
    
    :param param_guess: 求解器猜想的新参数值 (例如 0.95)
    :param param_name_to_solve: 要修改的参数名称 (例如 'K0')
    :param base_params: 包含原始 K0, KI, AC 的字典
    :param fixed_cp: 固定的新票息 (CP_new)
    :param target_fv: 目标公允价值 (98,800)
    :return: 误差 (FV - Target)
    """
    
    # 1. 创建参数副本以避免修改原始字典
    temp_params = copy.deepcopy(base_params)
    
    # 2. 将“猜想值”设置到字典中
    temp_params[param_name_to_solve] = param_guess
    
    # 3. 调用核心定价引擎
    current_fv = calculate_fair_value(
        CP_guess=fixed_cp, 
        params=temp_params, 
        product_type='HKD'
    )
    
    # 4. 计算误差
    error = current_fv - target_fv
    
    print(f"  [Solver Step: {param_name_to_solve}] 猜想 {param_name_to_solve} = {param_guess: .6f} -> FV: {current_fv/temp_params['NOM'] * 100.0: .4f}% -> 误差: {error: .2f}")
    
    return error

# --- 4. Main 入口: 求解 Q2 的三个练习 ---
if __name__ == "__main__":
    
    multiprocessing.freeze_support() 
    
    print(f"--- 正在执行: solver_ii.py (Q2 生产版) ---")
    print("本脚本将计算 Q2 的三个独立练习。")
    print("将使用 300,000 条路径，这可能需要几分钟时间。")
    print("-" * 50)
    print(f"Q1(i) 的 CP1 值为: {CP1_VALUE:.6f} %")
    print(f"Q2 使用的新票息 (CP_new): {CP_NEW:.6f} %")
    print(f"目标利润率: {TARGET_MARGIN*100:.2f} %")
    print(f"目标公允价值 (成本): {TARGET_FV:,.2f} HKD")
    print("-" * 50)
    
    # 定义基础参数 (Q1的原始值)
    base_params = hkd_params_prod
    
    # --- 练习 A: 求解 K0 ---
    # 固定: CP=CP_new, KI=0.92, AC=0.99
    # 求解: K0
    # 预期: K0 < 0.96
    print("\n" + "="*50)
    print(f"练习 A: 求解 K0 (保持 KI=0.92, AC=0.99)")
    print(f"搜索区间: [0.80, {base_params['K0']}]") # 上界为原始值
    print("="*50)
    
    start_time = time.time()
    try:
        found_K0 = brentq(
            generic_objective_function,
            a=0.80, # 安全下界
            b=base_params['K0'], # 原始值作为上界
            args=('K0', base_params, CP_NEW, TARGET_FV),
            xtol=1e-6
        )
        print(f"--- 练习 A 完成 (用时: {time.time() - start_time:.2f}s) ---")
        print(f"==> 找到的新 K0: {found_K0:.6f} (原始值: {base_params['K0']})")
        print(f"==> 变化量: {found_K0 - base_params['K0']:.6f}")
    except ValueError as e:
        print(f"--- 练习 A 求解失败: {e} ---")
        found_K0 = None

    # --- 练习 B: 求解 KI ---
    # 固定: CP=CP_new, K0=0.96, AC=0.99
    # 求解: KI
    # 预期: KI < 0.92
    print("\n" + "="*50)
    print(f"练习 B: 求解 KI (保持 K0=0.96, AC=0.99)")
    print(f"搜索区间: [0.80, {base_params['KI']}]") # 上界为原始值
    print("="*50)
    
    start_time = time.time()
    try:
        found_KI = brentq(
            generic_objective_function,
            a=0.80, # 安全下界
            b=base_params['KI'], # 原始值作为上界
            args=('KI', base_params, CP_NEW, TARGET_FV),
            xtol=1e-6
        )
        print(f"--- 练习 B 完成 (用时: {time.time() - start_time:.2f}s) ---")
        print(f"==> 找到的新 KI: {found_KI:.6f} (原始值: {base_params['KI']})")
        print(f"==> 变化量: {found_KI - base_params['KI']:.6f}")
    except ValueError as e:
        print(f"--- 练习 B 求解失败: {e} ---")
        found_KI = None

    # --- 练习 C: 求解 AC ---
    # 固定: CP=CP_new, K0=0.96, KI=0.92
    # 求解: AC
    # 预期: AC < 0.99
    print("\n" + "="*50)
    print(f"练习 C: 求解 AC (保持 K0=0.96, KI=0.92)")
    print(f"搜索区间: [0.90, {base_params['AC']}]") # 上界为原始值
    print("="*50)
    
    start_time = time.time()
    try:
        found_AC = brentq(
            generic_objective_function,
            a=0.90, # 安全下界 (AC 不太可能低于 K0)
            b=base_params['AC'], # 原始值作为上界
            args=('AC', base_params, CP_NEW, TARGET_FV),
            xtol=1e-6
        )
        print(f"--- 练习 C 完成 (用时: {time.time() - start_time:.2f}s) ---")
        print(f"==> 找到的新 AC: {found_AC:.6f} (原始值: {base_params['AC']})")
        print(f"==> 变化量: {found_AC - base_params['AC']:.6f}")
    except ValueError as e:
        print(f"--- 练习 C 求解失败: {e} ---")
        found_AC = None

    # --- 最终总结 ---
    print("\n" + "="*60)
    print(f"--- Q2 最终答案 (300,000 路径) ---")
    print(f"原始 CP1: {CP1_VALUE:.6f}% | 新 CP_new: {CP_NEW:.6f}% (Δ -0.10%)")
    print(f"目标公允价值: {TARGET_FV:,.2f} HKD (1.20% 利润率)")
    print("-" * 60)
    if found_K0 is not None:
        print(f"练习 A (K0): {base_params['K0']: .4f} -> {found_K0: .6f} (Δ {found_K0 - base_params['K0']:.6f})")
    else:
        print("练习 A (K0): 未能找到解。")
        
    if found_KI is not None:
        print(f"练习 B (KI): {base_params['KI']: .4f} -> {found_KI: .6f} (Δ {found_KI - base_params['KI']:.6f})")
    else:
        print("练习 B (KI): 未能找到解。")

    if found_AC is not None:
        print(f"练习 C (AC): {base_params['AC']: .4f} -> {found_AC: .6f} (Δ {found_AC - base_params['AC']:.6f})")
    else:
        print("练习 C (AC): 未能找到解。")
    print("="*60)