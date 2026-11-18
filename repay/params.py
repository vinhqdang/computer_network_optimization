"""Model parameters and class/tier helpers for REPAY.

Tier index: 0 = free (F), 1 = premium (P), 2 = pay-as-you-go (Y).
Class code: 0 = elastic (E), 1 = video (V), 2 = gaming (G).
"""
from dataclasses import dataclass

import numpy as np

E_CLS, V_CLS, G_CLS = 0, 1, 2
F_TIER, P_TIER, Y_TIER = 0, 1, 2


def _out(x):
    """Return a Python float for scalar results, the array otherwise."""
    return float(x) if np.ndim(x) == 0 else x


@dataclass
class Params:
    """Problem constants (defaults from the final design)."""

    rmin_V: float = 0.5
    rmax_V: float = 3.0
    r_G: float = 0.2
    w: tuple = (1.0, 2.0, 1.5)
    V: float = 20.0
    alpha: float = 1.0
    theta_P: float = 0.8
    theta_Y: float = 0.6
    phi: float = 0.15
    commit: tuple = (float("inf"), 2.0, 1.5)  # committed rate per device, by tier
    varpi: float = 0.0
    price: float = 1.0
    queue_scale: float = 1.0  # tier-queue updates are multiplied by this factor (1 = original rule)

    def __post_init__(self):
        if self.alpha != 1.0:
            raise NotImplementedError("only alpha = 1 (u(x) = log(1+x)) is supported")

    @property
    def w_arr(self):
        """Tier weights as an array indexed by tier."""
        return np.asarray(self.w, dtype=float)

    def committed(self, tier, dem_dev):
        """Committed demand per device: its demand capped at the committed rate of its tier."""
        return np.minimum(np.asarray(dem_dev, dtype=float), np.asarray(self.commit, dtype=float)[tier])

    def rmin(self, k):
        """Minimum rate of RT class k (1 = video, 2 = gaming); array-friendly."""
        return _out(np.where(np.asarray(k) == V_CLS, self.rmin_V, self.r_G))

    def rmax(self, k):
        """Maximum rate of RT class k (gaming: equal to r_G)."""
        return _out(np.where(np.asarray(k) == V_CLS, self.rmax_V, self.r_G))

    def u_rt(self, k, z):
        """Per-slot utility of an RT flow of class k at rate z."""
        z = np.asarray(z, dtype=float)
        video = 1.0 + np.log(np.maximum(z, 1e-300) / self.rmin_V)
        return _out(np.where(np.asarray(k) == V_CLS, video, 1.0))

    def eta(self, k):
        """Maximal utility per unit rate, max_z u_k(z)/z = 1/rmin_k."""
        return 1.0 / self.rmin(k)

    def theta_bound(self, g, k):
        """Deficit scale Theta_{g,k} = V w_g eta_k."""
        return self.V * self.w[g] * self.eta(k)

    def B(self, g, k):
        """Deficit bound B_{g,k} = Theta_{g,k} + rmax_k."""
        return self.theta_bound(g, k) + self.rmax(k)
