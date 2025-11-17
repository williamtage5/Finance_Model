### **Accelerating Monte Carlo Simulation Path Generation using Antithetic Variates**

**Antithetic Variates** is a very powerful and classic Monte Carlo optimization technique.

Its core idea is: **Rather than trying to *eliminate* randomness, it *utilizes* the symmetry of randomness to "cancel" it out.**

## 1. Concept

**Antithetic Variates** is a Monte Carlo variance reduction technique. Its core idea is: **Instead of generating $N$ completely independent simulation paths, $N/2$ pairs of paths are generated. The two paths in each pair are "antithetic," meaning they are driven by mutually opposite random numbers, thereby creating a statistical negative correlation.**

By averaging the (payoff) results of these two negatively correlated paths, a paired estimator with a smaller variance is obtained. Ultimately, the variance of the entire simulation will be significantly lower than that of a standard Monte Carlo simulation using $N$ independent paths.

## 2. Principle: Why Can Negative Correlation Optimize the Simulation? (The Principle)

Let us elaborate on the principle mathematically.

Assume our goal is to estimate the expected value $\theta = E[X]$ of some random variable $X$.
(In finance, $X$ is typically the discounted payoff of a derivative, and $\theta$ is the derivative's price.)

### A. Standard Monte Carlo (Standard MC)

We generate $N$ independent samples $X_1, X_2, \dots, X_N$, all identically distributed as $X$.
The estimator is:
$$
\hat{\theta}_{MC} = \frac{1}{N} \sum_{i=1}^N X_i
$$
Its variance is:
$$
Var(\hat{\theta}_{MC}) = Var\left( \frac{1}{N} \sum_{i=1}^N X_i \right) = \frac{1}{N^2} \sum_{i=1}^N Var(X_i) = \frac{1}{N^2} \cdot N \cdot Var(X) = \frac{Var(X)}{N}
$$
(This utilizes the independence between $X_i$, where the covariance is 0).

### B. Antithetic Variates (AV)

Our goal is to construct a new estimator with a variance less than $\frac{Var(X)}{N}$.

We do not generate $N$ independent samples, but rather $N/2$ pairs of samples $(Y_1, Y_2)$. These two are **generated antithetically**, but their individual marginal distributions are still identical to $X$. That is, $E[Y_1] = E[Y_2] = E[X] = \theta$.

We construct a new paired variable:
$$
Y^* = \frac{Y_1 + Y_2}{2}
$$
The expected value of this new variable is clearly correct:
$$
E[Y^*] = E\left[ \frac{Y_1 + Y_2}{2} \right] = \frac{E[Y_1] + E[Y_2]}{2} = \frac{\theta + \theta}{2} = \theta
$$
Therefore, $Y^*$ is an unbiased estimator of $\theta$.

Our total estimator is the average of $N/2$ such $Y^*$ variables (using a total of $N$ paths):
$$
\hat{\theta}_{AV} = \frac{1}{N/2} \sum_{i=1}^{N/2} Y_i^*
$$
Its variance is:
$$
Var(\hat{\theta}_{AV}) = \frac{Var(Y^*)}{N/2}
$$

#### C. Proof of Variance Reduction

Now, let us analyze $Var(Y^*)$:
$$
Var(Y^*) = Var\left( \frac{Y_1 + Y_2}{2} \right) = \frac{1}{4} Var(Y_1 + Y_2)
$$
Using the variance and covariance property $Var(A+B) = Var(A) + Var(B) + 2Cov(A, B)$:
$$
Var(Y^*) = \frac{1}{4} [Var(Y_1) + Var(Y_2) + 2Cov(Y_1, Y_2)]
$$
Because $Y_1$ and $Y_2$ have the same distribution as $X$, $Var(Y_1) = Var(Y_2) = Var(X)$.
$$
Var(Y^*) = \frac{1}{4} [2Var(X) + 2Cov(Y_1, Y_2)] = \frac{1}{2} [Var(X) + Cov(Y_1, Y_2)]
$$
Substituting this back into $Var(\hat{\theta}_{AV})$:
$$
Var(\hat{\theta}_{AV}) = \frac{Var(Y^*)}{N/2} = \frac{\frac{1}{2} [Var(X) + Cov(Y_1, Y_2)]}{N/2} = \frac{Var(X) + Cov(Y_1, Y_2)}{N}
$$

#### D. Comparing the Variance

Now we compare the variance of Standard MC and AV:
* **Standard MC:** $Var(\hat{\theta}_{MC}) = \frac{Var(X)}{N}$
* **Antithetic Variates:** $Var(\hat{\theta}_{AV}) = \frac{Var(X)}{N} + \frac{Cov(Y_1, Y_2)}{N}$

**The key to the optimization is:**
If $Cov(Y_1, Y_2) < 0$ (i.e., $Y_1$ and $Y_2$ are negatively correlated), then $Var(\hat{\theta}_{AV})$ will be less than $Var(\hat{\theta}_{MC})$. **The more negative the covariance, the greater the variance reduction effect.**

### 3. How it Optimizes: Application in Path Generation

The goal of the antithetic variates method is to design a generation method for $(Y_1, Y_2)$ such that they are naturally negatively correlated.

In Monte Carlo path generation (e.g., simulating stock prices), the Payoff $Y$ is typically a function of standard normal random numbers $Z$, i.e., $Y = f(Z)$. (If the path has multiple steps, $Y = f(Z_1, Z_2, \dots, Z_M)$).

We utilize the **symmetry of the standard normal distribution** to construct the antithetic variables.

#### A. Basic Method: Inverting Random Numbers

1.  Instead of generating $Z \sim N(0, 1)$, we first generate $U \sim U[0, 1]$ (a uniformly distributed random number).
2.  Using the **Inverse Transform Method**, we get the normal random number: $Z = \Phi^{-1}(U)$, where $\Phi^{-1}$ is the inverse of the standard normal cumulative distribution function (CDF).
3.  **Path 1 (Y1):** Use $U$ to generate $Z_1 = \Phi^{-1}(U)$, and use $Z_1$ to drive the simulation, yielding payoff $Y_1 = f(Z_1)$.
4.  **Path 2 (Y2):** Use $1-U$ to generate $Z_2$.
    * $Z_2 = \Phi^{-1}(1 - U)$
    * **Key Insight:** Due to the symmetry of the standard normal distribution about 0, we have $\Phi^{-1}(1-U) = -\Phi^{-1}(U)$.
    * Therefore, $Z_2 = -Z_1$.
    * We use $Z_2$ (i.e., $-Z_1$) to drive the simulation, yielding payoff $Y_2 = f(Z_2) = f(-Z_1)$.

#### B. Condition for Optimization: Monotonic Function

How do we guarantee that $Cov(Y_1, Y_2) < 0$?
That is, $Cov(f(Z_1), f(-Z_1)) < 0$?

The answer is: **If $f(z)$ is a Monotonic Function, this condition will be met.**

* **Intuitive Understanding:**
    * Assume $f(z)$ is **monotonically increasing** (e.g., a European call option).
    * If $Z_1$ is a large positive number (e.g., 2.0), then $Y_1 = f(2.0)$ will be large.
    * Its antithetic variable $Z_2 = -2.0$ is a small negative number, so $Y_2 = f(-2.0)$ will be small.
    * Conversely, if $Z_1$ is small (-2.0), then $Y_1$ is small; $Z_2$ is large (2.0), then $Y_2$ is large.
    * $Y_1$ and $Y_2$ always tend to move in opposite directions, which creates **negative correlation**.

#### C. Application in Multi-Step Path Generation

When simulating a complete asset path, such as Geometric Brownian Motion (GBM), we may need $M$ random numbers to simulate $M$ time steps.
$$
S_{t_i} = S_{t_{i-1}} \exp\left( (r - \frac{1}{2}\sigma^2)\Delta t + \sigma \sqrt{\Delta t} Z_i \right), \quad i=1, \dots, M
$$
where $Z_i \sim N(0, 1)$.

**The optimization steps are as follows:**

1.  **Generate $N/2$ random vectors:**
    Generate $N/2$ $M$-dimensional standard normal random vectors $\mathbf{Z}^{(j)} = (Z_1^{(j)}, Z_2^{(j)}, \dots, Z_M^{(j)})$, where $j = 1, \dots, N/2$.

2.  **Generate two paths for each $j$:**
    * **Path A:**
        Use the random vector $\mathbf{Z}^{(j)}$ to drive the GBM, generating path $\mathbf{S}_A^{(j)}$, and calculate its payoff $Y_A^{(j)}$.
    * **Path B (Antithetic Path):**
        Use the **inverted** random vector $-\mathbf{Z}^{(j)} = (-Z_1^{(j)}, -Z_2^{(j)}, \dots, -Z_M^{(j)})$ to drive the GBM, generating path $\mathbf{S}_B^{(j)}$, and calculate its payoff $Y_B^{(j)}$.

3.  **Calculate the paired estimator:**
    For each pair $j$, calculate $Y^{*(j)} = \frac{Y_A^{(j)} + Y_B^{(j)}}{2}$.

4.  **Calculate the final price:**
    The final estimated price is $\hat{\theta}_{AV} = \frac{1}{N/2} \sum_{j=1}^{N/2} Y^{*(j)}$.

For many common derivatives (such as European options, Asian options), their final payoff, as a function of the underlying random drivers $(Z_1, \dots, Z_M)$, is largely monotonic. Therefore, the payoffs $Y_A$ and $Y_B$ from the two paths generated using $\mathbf{Z}$ and $-\mathbf{Z}$ are almost always negatively correlated, thereby achieving significant variance reduction.

---

### Summary

Antithetic Variates systematically **introduces negative correlation** between pairs of simulated paths by **exploiting the symmetry of the random number generator (e.g., $U$ and $1-U$, or $Z$ and $-Z$)**.

The mathematical principle relies on $Var(\frac{Y_1+Y_2}{2}) = \frac{Var(Y) + Cov(Y_1, Y_2)}{2}$. When $Cov(Y_1, Y_2) < 0$, the variance of this paired estimator, $Var(Y^*)$, will be less than the variance of a single path, $Var(Y)$.

This allows the Monte Carlo simulation to converge faster, yielding a more precise price estimate with a smaller variance for the same total number of $N$ paths.