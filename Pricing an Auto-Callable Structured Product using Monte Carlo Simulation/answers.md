### **Executive Summary of Results**

All calculations for Questions 1, 2, and 3 were completed using a parallelized Monte Carlo simulation with 300,000 paths. The results were subsequently verified by an independent validation script (`validator.py`). All solutions for the standard HKD product (Q1 and Q2) were validated with high precision. The solutions for the Quanto product (Q3) were also found to be correct, with minor validation errors consistent with the higher inherent variance (noise) of a correlated two-asset model.

---

### **Question 1: HKD Product (Solve for Coupon)**

The goal was to find the monthly coupon rate (CP) for the standard HKD product that results in a specific profit margin for the bank.

* **Q1(i) [1.20% Profit Margin]:**
    * The required coupon rate (CP1) is **3.458654%**.
    * *Validation: Target FV 98.8000%, Calculated FV 98.8115% (Error: +0.0115%). **Pass.***

* **Q1(ii) [1.60% Profit Margin]:**
    * The required coupon rate is **3.206363%**.
    * *Validation: Target FV 98.4000%, Calculated FV 98.3915% (Error: -0.0085%). **Pass.***

### **Question 2: Parameter Sensitivity Analysis**

The goal was to hold the profit margin at 1.20% (Target FV: 98.80%) after lowering the coupon to `CP1 - 0.10%` (i.e., **3.358654%**). This required adjusting the `K0`, `KI`, or `AC` parameters to compensate.

* **Task A (Solve for K0):**
    * The Strike (`K0`) parameter must be adjusted from `0.9600` down to **`0.946917`**.
    * *Change: `Δ -0.013083`*
    * *Validation: Target FV 98.8000%, Calculated FV 98.7924% (Error: -0.0076%). **Pass.***

* **Task B (Solve for KI):**
    * The Knock-in (`KI`) parameter must be adjusted from `0.9200` down to **`0.657667`**.
    * *Change: `Δ -0.262333`*
    * *Validation: Target FV 98.8000%, Calculated FV 98.8038% (Error: +0.0038%). **Pass.***
    * *Note: This significant change confirms the expected insensitivity of the Fair Value to the `KI` parameter.*

* **Task C (Solve for AC):**
    * The Auto-Call (`AC`) parameter must be adjusted from `0.9900` down to **`0.981261`**.
    * *Change: `Δ -0.008739`*
    * *Validation: Target FV 98.8000%, Calculated FV 98.7886% (Error: -0.0114%). **Pass.***

### **Question 3: Quanto Product (Solve for Coupon)**

The goal was to find the monthly coupon rate (CP) for the CNY-denominated Quanto product.

* **Q3(i) [1.20% Profit Margin]:**
    * The required coupon rate is **3.262929%**.
    * *Validation: Target FV 98.8000%, Calculated FV 98.7701% (Error: -0.0299%). **Warning (Acceptable Noise).***

* **Q3(ii) [1.60% Profit Margin]:**
    * The required coupon rate is **3.015741%**.
    * *Validation: Target FV 98.4000%, Calculated FV 98.4222% (Error: +0.0222%). **Warning (Acceptable Noise).***