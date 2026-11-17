"""Counterexample search: less deficit does not imply less cumulative volume.

Two copies of an elastic device face the same price-taking environment (capacity price, demand cap,
real-time reference per slot) and differ only in their initial deficits, D_q <= D_p. The elastic
response and the deficit recursion are those of REPAY (log utility, tier price zero). The script
reports the largest value of (cumulative volume of q) - (cumulative volume of p) found by random
search; a positive value refutes the monotonicity conjecture discussed in the analysis section.
Run from the repository root: python -m experiments.check_credit_monotonicity
"""
import numpy as np


def response(D_total, lam, d, Vw):
    """Elastic response x(lambda) of REPAY for u(x) = log(1 + x) and bonus D_total."""
    p = lam - D_total
    return d if p <= 0 else min(d, max(0.0, Vw / p - 1.0))


def search(trials=20000, seed=1):
    rng = np.random.default_rng(seed)
    worst = {1: 0.0, 2: 0.0}
    for _ in range(trials):
        K = int(rng.choice([1, 2]))            # number of real-time classes
        T = int(rng.integers(5, 60))
        Vw = rng.uniform(0.5, 20)
        Dp = rng.uniform(0, 10, K)
        Dq = Dp * rng.uniform(0, 1, K)         # componentwise less credit
        Xp = Xq = 0.0
        for _ in range(T):
            lam = rng.choice([0.0, rng.uniform(0, 30)])
            d = rng.choice([0.2, 1.0, 5.0, 50.0])
            r = np.array([rng.choice([0.0, rng.uniform(0.2, 3)]) for _ in range(K)])
            r = np.minimum(r, d)
            xp, xq = response(Dp.sum(), lam, d, Vw), response(Dq.sum(), lam, d, Vw)
            Xp += xp
            Xq += xq
            Dp = np.maximum(Dp + r - xp, 0.0)
            Dq = np.maximum(Dq + r - xq, 0.0)
            worst[K] = max(worst[K], Xq - Xp)
    return worst


if __name__ == "__main__":
    w = search()
    print(f"largest volume advantage of the copy with LESS credit: one class {w[1]:.2f} Mbit, "
          f"two classes {w[2]:.2f} Mbit")
