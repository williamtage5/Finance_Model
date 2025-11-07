# Monte Carlo Methods in Derivative Pricing

This project demonstrates the application of Monte Carlo simulation techniques to price a complex exotic option. The entire workflow is implemented in Python and documented in Jupyter Notebooks.

The project is segmented into two main parts:
1.  **Parameter Estimation:** Analyzing historical market data to calculate the key volatility and correlation parameters required for the pricing model.
2.  **Exotic Option Pricing:** Pricing an "Average Worst-of Put Option" using two different Monte Carlo discretization schemes to compare their accuracy and computational efficiency.

# Mission Definition

## Part I: Data Analysis and Parameter Estimation

Before any pricing can be performed, we must first derive the necessary model parameters from historical data. This part focuses on analyzing daily price data for two stocks ($S_1$ and $S_2$) to establish a consistent set of inputs for Part II.

The tasks in this section are:
* Convert raw daily price series into log-return series.
* Calculate the time series of **rolling realized volatility** for $S_1$ and $S_2$ using a 120-day window.
* Compute the **average rolling volatility** ($\overline{\sigma_1}$, $\overline{\sigma_2}$) from the series above. These averages will serve as the primary volatility inputs for the pricing model.
* Calculate the **static correlation coefficient** ($\rho_{12}$) between $S_1$ and $S_2$ using the entire data set. This will be used to model the joint movement of the two assets in Part II.

## Part II: Exotic Option Pricing (Average Worst-of Put)

This section focuses on pricing a complex exotic option using the parameters derived in Part I. The product is an **Average Worst-of Put Option** with a 2-year maturity.

The option's payoff is defined as:
**$Payoff = \max(100 - A\%, 0)$**

Where:
* **$A$** is the arithmetic average of three "worst-of" performance values: $A = (B_1 + B_2 + B_3) / 3$.
* **$B_k$** is the "worst-of" relative performance of the two stocks ($S_1$, $S_2$) at specific observation dates ($t=0.5, 1.0, 2.0$ years):
    * $B_1 = \min(S_{1,1}/S_{1,0}, S_{2,1}/S_{2,0})$
    * $B_2 = \min(S_{1,2}/S_{1,0}, S_{2,2}/S_{2,0})$
    * $B_3 = \min(S_{1,3}/S_{1,0}, S_{2,3}/S_{2,0})$

The central task is to price this option by implementing two distinct Monte Carlo schemes and comparing their results (for both 10,000 and 300,000 simulation paths).

* **Task 2.1: Non-Exact Scheme (Euler-Maruyama)**
    * Implement a simulation using the **non-exact Euler-Maruyama discretization** of the Geometric Brownian Motion (GBM) process.
    * This method requires a large number of small, discrete time steps ($N=200$, $\Delta t = 0.01$) to ensure accuracy.

* **Task 2.2: Exact Scheme (Analytical Solution)**
    * Implement a simulation using the **exact analytical solution** of the GBM process.
    * This mathematically precise formula allows for a far more efficient simulation, "jumping" directly to the required observation dates.
    * This simulation uses only three non-uniform time steps ($N=3$, with $\Delta t_1 = 0.5$, $\Delta t_2 = 0.5$, and $\Delta t_3 = 1.0$).


# Methodology and Known Parameters

## Methodology

The core of this project is the pricing of a complex, path-dependent option using the **Monte Carlo simulation** method.

### The Monte Carlo Pricing Framework

The fundamental principle of risk-neutral derivative pricing states that the fair price of an option today ($t=0$) is the discounted expected value of its future payoffs.

$Price = e^{-rT} \times E[Payoff]$

For a simple European option, this expectation $E[Payoff]$ can often be solved analytically (e.g., the Black-Scholes formula). However, for the complex **Average Worst-of Put Option** in this assignment, an analytical solution is intractable.

We, therefore, turn to Monte Carlo simulation to *estimate* this expected value. The process is as follows:
1.  **Simulate Paths:** Generate thousands of potential "future paths" for the underlying stock prices ($S_1, S_2$) from $t=0$ to $t=T$, following a specific stochastic process.
2.  **Calculate Payoffs:** For each simulated path, calculate the option's final payoff according to the contract's rules.
3.  **Average:** Calculate the arithmetic mean of all the individual payoffs from all paths. This average serves as our estimate for $E[Payoff]$.
4.  **Discount:** Discount this average payoff back to $t=0$ using the risk-free rate $r$ to find the option's present value (its price).

### Simulating Stock Paths: Two Discretization Schemes

To simulate the stock paths, we assume they follow a **Geometric Brownian Motion (GBM)** process. The continuous-time stochastic differential equation (SDE) for this process is:

$dS = rS dt + \sigma S dz$

To implement this on a computer, we must use a discrete-time version. This project explores two different discretization schemes as required by the assignment.

#### 1. Part (i): Non-Exact Scheme (Euler-Maruyama)

This is the most direct, but approximate, discretization of the SDE. It assumes that over a small time step $\Delta t$, the change in stock price is linear.

**Core Formula:**
$S(t+\Delta t) = S(t) + rS(t)\Delta t + \sigma S(t) \epsilon \sqrt{\Delta t}$
(where $\epsilon \sim N(0, 1)$)

**Simulation Strategy:**
This approximation is only accurate for *very small* time steps. Therefore, to price the 2-year option, we are required to use $N=200$ small, uniform steps (where $\Delta t = 0.01$). We must simulate all 200 steps to find the prices at the required observation dates (at steps 50, 100, and 200). This is computationally intensive.

#### 2. Part (ii): Exact Scheme (Analytical Solution)

This method does not approximate the SDE; it uses the known **analytical solution** to the GBM SDE. This formula is mathematically precise and holds true for *any* time step $\Delta t$, large or small.

**Core Formula:**
$S(t+\Delta t) = S(t) \exp\left\{(r - \frac{\sigma^2}{2})\Delta t + \sigma \epsilon \sqrt{\Delta t}\right\}$

**Simulation Strategy:**
Because this formula is exact, we are no longer required to take small steps. We only care about the prices at $t=0.5, 1.0, 2.0$. This scheme allows us to "jump" directly to these dates.
The simulation runs with only $N=3$ non-uniform time steps:
* **Jump 1:** $\Delta t_1 = 0.5$ (from $t=0 \to t=0.5$)
* **Jump 2:** $\Delta t_2 = 0.5$ (from $t=0.5 \to t=1.0$)
* **Jump 3:** $\Delta t_3 = 1.0$ (from $t=1.0 \to t=2.0$)

This "direct jump" method is far more efficient, as it only performs 3 calculations per path instead of 200.

### Handling Correlated Assets

Both stocks $S_1$ and $S_2$ are driven by random variables ($\epsilon_1, \epsilon_2$) that are correlated by $\rho_{12}$. To model this, we first generate two independent standard normal variables ($x_1, x_2$) and then use the Cholesky decomposition to create correlated variables:

$\epsilon_1 = x_1$
$\epsilon_2 = \rho_{12} x_1 + \sqrt{1 - \rho_{12}^2} x_2$

---

## Known Parameters

All calculations in this project are based on the following parameters, which were either given by the assignment or derived in Part I:

### Financial Parameters
* **Risk-Free Rate ($r$):** 3.25% (or 0.0325)
* **Total Maturity ($T$):** 2.0 years
* **Initial Price $S_{1,0}$:** 11.08
* **Initial Price $S_{2,0}$:** 73.40

### Part I: Calculated Statistical Parameters
* **Avg. Volatility $S_1$ ($\overline{\sigma_1}$):** 0.6039
* **Avg. Volatility $S_2$ ($\overline{\sigma_2}$):** 0.3481
* **Correlation ($\rho_{12}$):** 0.5456

### Simulation Parameters
* **Simulation Paths:** 10,000 and 300,000
* **Part (i) Steps:** $N=200$
* **Part (i) Time Step:** $\Delta t = 0.01$
* **Part (ii) Steps:** $N=3$
* **Part (ii) Time Steps:** $\Delta t_s = [0.5, 0.5, 1.0]$

# Part I: Data Analysis and Parameter Estimation

This part details the complete process of extracting and calculating the necessary statistical parameters from historical market data. These parameters serve as the essential inputs for the Monte Carlo pricing models in Part II.

## How It Was Done

1.  **Data Loading:** The process began by loading the daily historical price data for the two required stocks, $S_1$ and $S_2$.
2.  **Data Transformation:** All price series ($S$) were converted into log-return series ($u$) to analyze their periodic changes.
3.  **Rolling Volatility Calculation:** To understand volatility as a time-varying parameter, a rolling annualized volatility was calculated for both $S_1$ and $S_2$ using a 120-day window. This produced a time series of volatility values.
4.  **Average Volatility Calculation:** The arithmetic mean of the rolling volatility time series was then computed for both $S_1$ and $S_2$ to obtain the single average volatility figures ($\overline{\sigma_1}$, $\overline{\sigma_2}$) required for the pricing model.
5.  **Static Correlation Calculation:** The static correlation coefficient ($\rho_{12}$) between $S_1$ and $S_2$ was calculated. This calculation used the *entire* set of 244 log-return data points, not a rolling window, to provide a single, stable correlation value for the joint simulation in Part II.
6.  **Visualization:** The resulting time series for rolling volatility was visualized in a plot to observe its behavior over time.

## Methodology

The calculations were strictly based on the following financial formulas:

* **Log-Return Series ($u$):**
    $$u_{i,j} = \ln\left(\frac{S_{i,j}}{S_{i,j-1}}\right)$$
    Where $S_{i,j}$ is the price of asset $i$ on day $j$.

* **Annualized Volatility ($\sigma_i$):**
    $$\sigma_{i} = \sqrt{\frac{1}{n-1}\sum_{j=1}^{n}(u_{i,j}-\overline{u_{i}})^{2}} \times \sqrt{252}$$
    This formula was applied over a rolling window. The $\sqrt{252}$ factor annualizes the daily volatility.

* **Average Volatility ($\overline{\sigma_i}$):**
    $$\overline{\sigma_{i}} = \frac{1}{m}\sum_{k=1}^{m}\sigma_{i}(k)$$
    Where $m$ is the total number of data points in the generated rolling volatility time series (125).

* **Annualized Covariance ($\sigma_{12}$):**
    $$\sigma_{12} = \sum_{j=1}^{n}[(u_{1,j}-\overline{u_{1}})(u_{2,j}-\overline{u_{2}})] \times \frac{252}{n-1}$$

* **Correlation Coefficient ($\rho_{12}$):**
    $$\rho_{12} = \frac{\sigma_{12}}{\sigma_{1}\sigma_{2}}$$

## Key Parameters

* **Rolling Window Size ($n$):** 120 days
* **Annualization Factor:** 252 (trading days)
* **Total Log-Return Data Points:** 244
* **Rolling Volatility Data Points ($m$):** 125

## Results

The key numerical results obtained from this analysis, which are used as inputs for Part II, are:

* **Average Volatility for $S_1$ ($\overline{\sigma_1}$):** 0.6039
* **Average Volatility for $S_2$ ($\overline{\sigma_2}$):** 0.3481
* **Static Correlation $S_1$ vs. $S_2$ ($\rho_{12}$):** 0.5456

Additionally, a time-series plot was generated showing the 120-day rolling volatility for both $S_1$ and $S_2$ over the analysis period.

Here is the requested section for your project.

***

# Part II Operation

This section details the implementation of the pricing models for the **Average Worst-of Put Option**. Both required Monte Carlo schemes were built and executed to compare their performance and results.

## How It Was Done

The pricing was accomplished in a sequence of steps, applied to both the Non-Exact and Exact schemes:

1.  **Parameter Initialization:** All known financial parameters (initial prices $S_{1,0}$, $S_{2,0}$, risk-free rate $r$, maturity $T$) and statistical parameters from Part I (volatilities $\overline{\sigma_1}$, $\overline{\sigma_2}$, and correlation $\rho_{12}$) were defined.

2.  **Correlated Path Generation:** For both schemes, the joint price paths were simulated. This was achieved by first generating pairs of independent standard normal random variables ($x_1, x_2$) and then transforming them into correlated variables ($\epsilon_1, \epsilon_2$) using the Cholesky decomposition method.

3.  **Path Simulation (Task 2.1: Non-Exact Scheme):**
    * A loop was run for $N=200$ discrete time steps ($\Delta t = 0.01$).
    * In each step of the loop, the stock prices $S_1$ and $S_2$ were updated using the **Euler-Maruyama** formula.
    * The prices were recorded only at the required observation steps (step 50 for $t=0.5$, step 100 for $t=1.0$, and step 200 for $t=2.0$).

4.  **Path Simulation (Task 2.2: Exact Scheme):**
    * A more efficient loop was run for only $N=3$ discrete time steps.
    * The loop used the non-uniform time steps $\Delta t_1 = 0.5$, $\Delta t_2 = 0.5$, and $\Delta t_3 = 1.0$.
    * In each of the three steps, the stock prices were updated using the **exact analytical solution** formula, allowing a direct "jump" to the next required observation date.

5.  **Payoff Calculation:** For each simulated path (from both schemes), the final payoff was calculated:
    * The worst-of performances $B_1$, $B_2$, and $B_3$ were calculated by comparing the stocks' relative returns at $t=0.5, 1.0, 2.0$.
    * The average worst-of performance $A$ was computed ($A = (B_1+B_2+B_3)/3$).
    * The final payoff for the path was determined: $Payoff = \max(100 - A\%, 0)$.

6.  **Final Pricing:**
    * The process was run for both 10,000 and 300,000 paths.
    * The arithmetic average of the payoffs from all paths was calculated to find the estimated expected payoff, $E[Payoff]$.
    * This expected payoff was discounted to the present value (at $t=0$) using the risk-free rate $r$ to find the final option price.
    * The computation time for each run was recorded.

## Methodology

The implementation relied on the following key formulas:

* **Payoff Structure:**
    $$Payoff = \max(100 - A\%, 0)$$
    $$A = (B_1 + B_2 + B_3) / 3$$
    $$B_k = \min(S_{1,k}/S_{1,0}, S_{2,k}/S_{2,0})$$

* **Correlated Random Numbers:**
    $$\epsilon_1 = x_1$$
    $$\epsilon_2 = \rho_{12} x_1 + \sqrt{1 - \rho_{12}^2} x_2$$

* **Task 2.1 (Non-Exact Euler Scheme):**
    $$S(t+\Delta t) = S(t) + rS(t)\Delta t + \sigma S(t) \epsilon \sqrt{\Delta t}$$

* **Task 2.2 (Exact Analytical Scheme):**
    $$S(t+\Delta t) = S(t) \exp\left\{(r - \frac{\sigma^2}{2})\Delta t + \sigma \epsilon \sqrt{\Delta t}\right\}$$

* **Final Price (Risk-Neutral Discounting):**
    $$Price = e^{-rT} \times E[Payoff]$$

## Key Parameters

* **Financial Parameters:**
    * Risk-Free Rate ($r$): 0.0325
    * Total Maturity ($T$): 2.0 years
    * Initial Price $S_{1,0}$: 11.08
    * Initial Price $S_{2,0}$: 73.40
* **Statistical Parameters (from Part I):**
    * Volatility $S_1$ ($\overline{\sigma_1}$): 0.6039
    * Volatility $S_2$ ($\overline{\sigma_2}$): 0.3481
    * Correlation ($\rho_{12}$): 0.5456
* **Simulation Parameters (Task 2.1):**
    * Time Steps ($N$): 200
    * Step Size ($\Delta t$): 0.01
* **Simulation Parameters (Task 2.2):**
    * Time Steps ($N$): 3
    * Step Sizes ($\Delta t_s$): [0.5, 0.5, 1.0]
* **Path Counts:**
    * Run 1: 10,000 paths
    * Run 2: 300,000 paths

## Results

The two schemes produced highly comparable and consistent results for the option's price, validating both approaches. The main difference was in computational performance.

* **Task 2.1 (Non-Exact Scheme):**
    * 10,000 paths: Price = 23.2409%, Time = 0.1025s
    * 300,000 paths: Price = 23.1261%, Time = 4.5676s

* **Task 2.2 (Exact Scheme):**
    * 10,000 paths: Price = 23.2183%, Time = 0.0032s
    * 300,000 paths: Price = 23.1444%, Time = 0.1013s

As expected, the prices from both methods converged to a similar value (approx. 23.13-23.14%). The results clearly demonstrate that the Exact Scheme (Task 2.2) is significantly more efficient, achieving the same level of accuracy in a fraction of the computation time (0.10s vs 4.57s for 300,000 paths) by only simulating the 3 required time steps.

Here is the conclusion formatted using the STAR method.

# Conclusion

* **Situation:** The project required the fair-value pricing of a complex, path-dependent exotic derivative (an Average Worst-of Put Option). This option's price is not analytically solvable and depends on the joint movement of two correlated assets, requiring parameters derived from historical data.

* **Task:** The objective was twofold: first, to process historical stock data to calculate key statistical parameters (average volatility and correlation); second, to implement, execute, and compare two different Monte Carlo simulation schemes (a 200-step non-exact Euler scheme and a 3-step exact analytical scheme) to determine the fair price of the option and assess their computational efficiency.

* **Action:** A data analysis pipeline was built to calculate volatility and correlation from raw price data. Following this, two distinct, vectorized Monte Carlo pricing models were developed in Python. The first model implemented the 200-step Euler-Maruyama approximation as specified. The second, more efficient model implemented the exact analytical solution, enabling direct "jumps" to the 3 required observation dates. Both models were executed for 10,000 and 300,000 paths, and their final prices and computation times were recorded.

* **Result:** The required parameters were successfully calculated (e.g., $\overline{\sigma_1}=0.6039$, $\rho_{12}=0.5456$). Both pricing models produced highly consistent and convergent results, with the 300,000-path simulations yielding prices of 23.1261% (Non-Exact) and 23.1444% (Exact). The key finding was the vast superiority in efficiency of the exact scheme: it produced the same high-quality result while being approximately 45 times faster (0.10s vs 4.57s) than the 200-step Euler method, definitively demonstrating the practical benefits of using an analytical solution when available.
