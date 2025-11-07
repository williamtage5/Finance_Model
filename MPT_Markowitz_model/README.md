## Project Introduction

This project provides a comprehensive, hands-on implementation of core portfolio optimization and asset allocation models. It explores both classic Markowitz optimization and alternative risk-based strategies using historical market data for Hong Kong stocks and Exchange Traded Funds (ETFs).

The work is structured into three main parts:

### Part 1: Data Preparation and Statistical Analysis

This initial phase focuses on data engineering and statistical computation. The primary task is to process raw historical daily price data for two distinct sets of assets: a portfolio of Hong Kong stocks and a diversified basket of ETFs. The objective is to calculate the essential inputs required for all subsequent models: the **annualized standard deviation** of daily returns for each asset and the complete **annualized covariance matrix** for each portfolio.

### Part 2: Markowitz Portfolio Optimization (Stocks)

This section applies the principles of Modern Portfolio Theory (MPT) as developed by Harry Markowitz. Using the covariance matrix from Part 1 and a given set of expected returns for the Hong Kong stocks, this part focuses on constructing the **efficient frontier** under a no-short-selling constraint.

The key objectives are to:
* Visualize the risk-return trade-off by plotting the efficient frontier.
* Identify the **Minimum Variance Portfolio (MVP)**.
* Determine the **Optimal Portfolio (Tangency Portfolio)** that maximizes the Sharpe Ratio.
* Construct the **Capital Allocation Line (CAL)**.

This analysis is performed first on a five-stock portfolio and then repeated with a six-stock portfolio to analyze the impact of diversification.

### Part 3: Alternative Asset Allocation Strategies (ETFs)

The final part of the project explores alternative allocation strategies that do not rely on estimating expected returns, focusing instead on risk-based methodologies. This analysis is conducted on the ETF portfolio, which represents a mix of major asset classes (e.g., equity, fixed income, gold, oil, and cryptocurrency).

The tasks are to build, analyze, and compare three distinct models:
* **Equal Weight (EW) Portfolio:** The baseline "1/N" strategy.
* **Minimum Variance (MV) Portfolio:** The portfolio that minimizes total portfolio risk, derived solely from the covariance matrix.
* **Equal Risk Contribution (ERC) Portfolio:** An advanced model that allocates weights such that each asset contributes equally to the total portfolio risk.

This analysis is also performed on two different sets of assets to examine how the introduction of a high-volatility asset (a cryptocurrency ETF) impacts portfolio structure and risk.

Here is the "Dataset" section for your `README.md` file, incorporating the link to your Kaggle dataset.

---

## Dataset

This project utilizes a custom dataset of historical daily closing prices for 11 assets trading in Hong Kong, spanning the period from **July 31, 2024, to July 31, 2025**.

The dataset (`all_prices.csv`) includes:
* **6 Hong Kong Stocks (Hang Seng Index constituents):** 5, 700, 1024, 2628, 6618, 1044
* **5 Hong Kong ETFs (representing various asset classes):** 2823, 3199, 2840, 3175, 3046

This data serves as the foundation for calculating returns, standard deviations, and covariance matrices, which are essential inputs for the portfolio optimization models in Parts 2 and 3.

The complete dataset is publicly available on Kaggle and can be accessed here:
[**MPT Model Dataset on Kaggle**](https://www.kaggle.com/datasets/williamtage/mpt-model-dataset)

Here is the `README.md` section describing the operations for Part 1.

---

## Part 1: Operation

This section details the process of data preparation and statistical analysis. The objective was to compute the annualized standard deviations and covariance matrices for two distinct portfolios (one of 6 stocks, one of 5 ETFs), which serve as the primary inputs for the models in Parts 2 and 3.

### How It Was Done

The process was completed in the following steps:
1.  **Asset Definition:** Two lists of tickers were defined:
    * **Stocks:** `['0005.HK', '0700.HK', '1024.HK', '2628.HK', '6618.HK', '1044.HK']`
    * **ETFs:** `['2823.HK', '3199.HK', '2840.HK', '3175.HK', '3046.HK']`
2.  **Data Retrieval:** Historical daily 'Adj Close' prices for all 11 assets were downloaded from Yahoo Finance (using the `yfinance` library).
3.  **Return Calculation:** Daily logarithmic returns were calculated from the adjusted closing prices.
4.  **Statistical Calculation:**
    * The standard deviation of daily log returns was calculated for each individual asset.
    * The full covariance matrix of daily log returns was calculated for the 6-stock portfolio and the 5-ETF portfolio.
5.  **Annualization:** All daily statistics were annualized using a factor of 252 (representing the approximate number of trading days in a year).

### Methodology

The key statistical inputs were derived using the following formulas:

**1. Daily Log Return ($R_t$)**
The log return is used for its additive properties, making time-series calculations more robust.
$$R_{t} = \ln\left(\frac{P_t}{P_{t-1}}\right)$$
*Where $P_t$ is the adjusted closing price at time $t$.*

**2. Annualized Standard Deviation ($\sigma_{\text{ann}}$)**
This measures the volatility of an individual asset.
$$\sigma_{\text{daily}} = \text{std}(R_t)$$
$$\sigma_{\text{ann}} = \sigma_{\text{daily}} \times \sqrt{252}$$

**3. Annualized Covariance Matrix ($\Sigma_{\text{ann}}$)**
This measures how assets move in relation to each other. For a portfolio of $n$ assets, this is an $n \times n$ matrix.
$$\Sigma_{\text{daily}} = \text{cov}(R_{i,t}, R_{j,t})$$
$$\Sigma_{\text{ann}} = \Sigma_{\text{daily}} \times 252$$

### Key Parameters
* **Time Period:** July 31, 2024, to July 31, 2025
* **Data Source:** Yahoo Finance (`yfinance`)
* **Price Type:** Adjusted Close
* **Return Type:** Logarithmic Returns
* **Annualization Factor:** 252

### Results
The successful execution of this part produced two sets of key statistical inputs:
* The annualized standard deviation for each of the 11 assets.
* A 6x6 annualized covariance matrix for the stock portfolio.
* A 5x5 annualized covariance matrix for the ETF portfolio.

## Part 2: Operation

This section applies the principles of Modern Portfolio Theory (MPT) to construct optimal portfolios for the set of Hong Kong stocks. The analysis was performed twice: first on a 5-stock portfolio and then on a 6-stock portfolio to observe the effects of adding a lower-risk asset.

### How It Was Done

1.  **Data Loading:** The annualized covariance matrices from Part 1 were loaded, along with a separate file containing the "expected 1-yr return" for each stock.
2.  **Parameter Definition:** A risk-free rate ($r_f$) of 2.35% was defined.
3.  **Efficient Frontier Generation:**
    * An optimization function was created to find the portfolio weights that minimize volatility (standard deviation) for a given level of expected return.
    * This optimization was run iteratively across a range of target expected returns (from 13% to 30%).
    * The optimization was subject to two constraints: all weights must sum to 1, and no short selling is allowed (all weights must be greater than or equal to 0).
    * The resulting set of minimum-volatility portfolios for each return level was stored to plot the efficient frontier.
4.  **Optimal Portfolio (Tangency Portfolio) Calculation:**
    * A separate optimization was run to find the single portfolio that maximizes the Sharpe Ratio.
    * This was achieved by minimizing the *negative* Sharpe Ratio, using the same constraints (weights sum to 1, no short selling).
    * This portfolio represents the "Optimal Portfolio" (OP) of risky assets to be combined with the risk-free asset.
5.  **Capital Allocation Line (CAL) & Optimal Allocation (OA):**
    * The slope of the CAL (the maximized Sharpe Ratio) was calculated.
    * Using the investor's utility function, $U = E(r) - 1.5\sigma^2$, the optimal weight $w_1$ to be allocated to the risk-free asset and $(1-w_1)$ to the Optimal Portfolio was calculated.
6.  **Comparative Analysis:** Steps 3-5 were executed first for the 5-stock portfolio (5, 700, 1024, 2628, 6618) and then repeated for the 6-stock portfolio (adding stock 1044).

### Methodology

The core of this analysis relies on the following Markowitz optimization formulas:

**1. Portfolio Expected Return ($E(R_p)$):**
$$E(R_p) = w^T \mu$$
* $w$: vector of asset weights
* $\mu$: vector of expected asset returns

**2. Portfolio Variance ($\sigma_p^2$) and Standard Deviation ($\sigma_p$):**
$$\sigma_p^2 = w^T \Sigma w$$
$$\sigma_p = \sqrt{w^T \Sigma w}$$
* $\Sigma$: annualized covariance matrix

**3. Efficient Frontier Optimization:**
For each target return $\mu_{\text{target}}$, solve:
* **Minimize:** $\sigma_p(w) = \sqrt{w^T \Sigma w}$
* **Subject to:**
    1.  $w^T \mu = \mu_{\text{target}}$
    2.  $w^T \mathbf{1} = 1$
    3.  $w_i \ge 0$ for all $i$ (no short selling)

**4. Optimal Portfolio (Tangency Portfolio) Optimization:**
Find the weights $w$ that:
* **Maximize:** $\text{Sharpe Ratio (SR)} = \frac{E(R_p) - r_f}{\sigma_p} = \frac{w^T \mu - r_f}{\sqrt{w^T \Sigma w}}$
* **Subject to:**
    1.  $w^T \mathbf{1} = 1$
    2.  $w_i \ge 0$ for all $i$

**5. Optimal Allocation (OA):**
The optimal weight in the risky portfolio ($w^*$) is found by maximizing the investor's utility. For $U = E(R_C) - A \sigma_C^2$ with $A=1.5$, the optimal weight in the risky portfolio is:
$$w^* = \frac{E(R_{OP}) - r_f}{2 A \sigma_{OP}^2} = \frac{E(R_{OP}) - r_f}{3 \sigma_{OP}^2}$$
The weight in the risk-free asset ($w_1$) is therefore:
$$w_1 = 1 - w^*$$

### Key Parameters

* **Risk-Free Rate ($r_f$):** 2.35%
* **Expected Returns:** As provided by the input data.
* **Covariance Matrices:** As calculated in Part 1.
* **Constraints:** Short sale not allowed (weights $\ge 0$).
* **Optimization Solver:** SciPy Minimize (Method: 'SLSQP')
* **Investor Utility:** $U = E(r) - 1.5\sigma^2$ (implying a risk-aversion coefficient of $A=1.5$).

### Results

The execution of this notebook produced the following key outputs for both the 5-stock and 6-stock scenarios:
* **Efficient Frontier:** A complete set of data points (weights, returns, and volatilities) defining the efficient frontier.
* **Optimal Portfolio (OP):** The specific weights for the risky assets that form the tangency portfolio, along with its expected return, standard deviation, and the maximized Sharpe Ratio (CAL slope).
* **Optimal Allocation (OA):** The final calculated weights $w_1$ (for the risk-free asset) and $(1-w_1)$ (for the Optimal Portfolio), which maximize the investor's utility.
* A comparative analysis of these results, showing how the efficient frontier, optimal portfolio, and CAL slope changed after adding the sixth asset (stock 1044).

## Part 3: Operation

This section details the construction and analysis of alternative, risk-based asset allocation models. Unlike the Markowitz optimization in Part 2, these methods do not require expected return inputs. The analysis was conducted on the ETF portfolio, first with four assets and then with five, to observe the impact of adding a cryptocurrency ETF.

### How It Was Done

1.  **Data Loading:** The 5x5 annualized covariance matrix for the ETF portfolio (2823, 3199, 2840, 3175, 3046) was loaded from the results of Part 1.
2.  **Equal Weight (EW) Portfolio:** The weights were calculated as $w_i = 1/n$ (where $n$ is the number of assets). The portfolio's standard deviation was then computed using these weights and the covariance matrix.
3.  **Minimum Variance (MV) Portfolio:** An optimization function was created to find the set of weights that minimizes the total portfolio variance. The optimization was subject to the constraints that all weights must sum to 1 and no short selling is allowed (weights $\ge 0$).
4.  **Equal Risk Contribution (ERC) Portfolio:** A more complex optimization was performed to find the weights $w$ such that each asset contributes equally to the total portfolio risk. This involved an objective function designed to minimize the difference in risk contributions between assets, subject to the same constraints (weights sum to 1, weights $\ge 0$).
5.  **Comparative Analysis:** Steps 2-4 were executed twice:
    * **First Run (4 Assets):** Using a 4x4 covariance matrix for ETFs 2823, 3199, 2840, and 3175.
    * **Second Run (5 Assets):** Using the full 5x5 covariance matrix, which included the cryptocurrency ETF (3046).

### Methodology

**1. Equal Weight (EW) Portfolio**
A simple, non-optimized model where each asset is given the same weight.
$$w_i = \frac{1}{n}$$
* $n$: number of assets in the portfolio

**2. Minimum Variance (MV) Portfolio**
This portfolio is optimized to find the lowest possible portfolio volatility, regardless of return.
* **Minimize:** $\sigma_p^2(w) = w^T \Sigma w$
* **Subject to:**
    1.  $w^T \mathbf{1} = 1$
    2.  $w_i \ge 0$ for all $i$
* $w$: vector of asset weights
* $\Sigma$: annualized covariance matrix

**3. Equal Risk Contribution (ERC) Portfolio**
This portfolio is optimized so that each asset's contribution to total portfolio risk is identical.
* **Marginal Risk Contribution (MRC):** The sensitivity of portfolio volatility to a small change in the weight of one asset.
    $$MRC_i = \frac{\partial \sigma_p}{\partial w_i} = \frac{(\Sigma w)_i}{\sigma_p}$$
* **Total Risk Contribution ($RC_i$):** The total amount of risk contributed by asset $i$.
    $$RC_i = w_i \times MRC_i = \frac{w_i (\Sigma w)_i}{\sigma_p}$$
* **Optimization Goal:** Find the weights $w$ that solve:
    $$RC_i = RC_j \quad \text{for all } i, j$$
* **Subject to:**
    1.  $w^T \mathbf{1} = 1$
    2.  $w_i \ge 0$ for all $i$

This is typically solved numerically by minimizing the variance of the assets' risk contributions.

### Key Parameters

* **Covariance Matrices:** As calculated in Part 1 (a 4x4 and a 5x5 matrix for the ETFs).
* **Asset Sets:**
    * Set 1 (4 ETFs): 2823, 3199, 2840, 3175
    * Set 2 (5 ETFs): 2823, 3199, 2840, 3175, 3046
* **Constraints:** Short sale not allowed (weights $\ge 0$), weights sum to 1.
* **Optimization Solver:** SciPy Minimize (Method: 'SLSQP').

### Results

The execution of this part successfully generated six distinct portfolios: an EW, MV, and ERC portfolio for both the 4-asset and 5-asset scenarios.

The key outputs for each portfolio were:
* The final vector of optimal asset weights.
* The resulting portfolio standard deviation (volatility).
* For the ERC portfolios, the marginal risk contribution of each asset was also produced to verify that the "equal risk" objective was met.

These results provide a direct comparison of portfolio composition and risk under each of the three methodologies and clearly demonstrate the significant impact of adding the high-volatility cryptocurrency asset to the portfolio.

Here is a "Conclusion" section based on the STAR framework, summarizing your project.

---

## Conclusion

This project provides a comprehensive, practical application of modern portfolio theory and risk-based asset allocation.

* ### Situation
    This project was initiated to solve a practical computational finance problem: how to construct, optimize, and analyze investment portfolios using real-world data. The environment consisted of historical daily price data for 11 assets (Hong Kong stocks and ETFs) and a defined set of objectives for modeling both return-driven (Markowitz) and risk-driven (EW, MV, ERC) strategies.

* ### Task
    The central task was to execute a three-part analysis. This involved:
    1.  **Data Preparation:** Processing raw price data to compute foundational statistical inputs (annualized standard deviations and covariance matrices).
    2.  **Markowitz Optimization:** Building the efficient frontier, identifying the optimal (tangency) portfolio that maximizes the Sharpe Ratio, and calculating a final asset allocation based on a specific investor utility function.
    3.  **Risk-Based Modeling:** Constructing and comparing three alternative portfolios (Equal Weight, Minimum Variance, and Equal Risk Contribution) that do not rely on expected return estimates.

* ### Action
    A systematic, quantitative workflow was implemented using Python:
    1.  **Part 1:** Fetched data using `yfinance` and used `pandas` to calculate daily log returns, which were then annualized to create the covariance matrices and volatility figures.
    2.  **Part 2:** Implemented optimization routines using `scipy.minimize` (SLSQP method) to solve for constrained minimums/maximums. This was used iteratively to trace the efficient frontier and to solve for the single tangency portfolio (by maximizing the Sharpe Ratio).
    3.  **Part 3:** Adapted the optimization functions to solve for the specific objectives of the MV portfolio (minimizing $w^T \Sigma w$) and the ERC portfolio (minimizing the variance of assets' risk contributions).
    4.  All analyses were performed on different asset subsets (5 vs. 6 stocks; 4 vs. 5 ETFs) to conduct a comparative analysis of how portfolio composition affects the results.

* ### Result
    The project successfully generated all required analytical outputs, demonstrating a complete end-to-end application of portfolio theory. The key results include:
    * The foundational annualized covariance matrices and volatilities for all assets.
    * A complete dataset and visualization of the efficient frontier for the stock portfolios.
    * The precise optimal weights, risk, and return for the Markowitz tangency portfolio (both 5- and 6-stock versions).
    * The final asset allocations (risk-free vs. risky) based on the specified investor utility.
    * A full comparative analysis of the EW, MV, and ERC portfolios, highlighting the distinct risk/weighting profiles generated by each methodology.