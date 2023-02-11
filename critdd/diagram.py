"""A module for assembling critical difference diagrams."""

import networkx as nx
import numpy as np
from scipy import stats
from .stats import friedman
from . import tikz

class Diagram(): # TODO extend to an arbitrary number of *Xs
    """A critical difference diagram.

    Args:
        X: An ``(n, k)``-shaped matrix of observations, where ``n`` is the number of observations and ``k`` is the number of treatments.
        treatment_names (optional): The names of the ``k`` treatments. Defaults to None.
        maximize_outcome (optional): Whether the ranks represent a maximization (True) or a minimization (False) of the outcome. Defaults to False.
    """
    def __init__(self, X, *, treatment_names=None, maximize_outcome=False):
        if treatment_names is None:
            treatment_names = map(lambda i: f"treatment {i}", range(X.shape[1]))
        elif len(treatment_names) != X.shape[1]:
            raise ValueError("len(treatment_names) != X.shape[1]")
        self.treatment_names = np.array(treatment_names)
        self.r = friedman(X, maximize_outcome=maximize_outcome)
        self.P = _pairwise_tests(X)

    @property
    def maximize_outcome(self):
        return self.r.chi_square_result.maximize_outcome
    @property
    def average_ranks(self):
        return self.r.chi_square_result.average_ranks

    def get_groups(self, alpha=.05, adjustment="holm", return_names=False):
        """Get the groups of indistinguishable treatments.

        Args:
            alpha (optional): The threshold for rejecting a p value. Defaults to 0.05.
            adjustment (optional): The multiple testing adjustment. Defaults to "holm". Another possible value is "bonferroni".
            return_names (optional): Whether to represent the treatments in the groups by their names (True) or by their indices (False). Defaults to False.

        Returns:
            A list of statistically indistinguishable groups.
        """
        if self.r.pvalue >= alpha: # does the Friedman test fail to reject?
            return [ np.arange(len(self.average_ranks)) ] # all treatments in a single group
        P = _adjust_pairwise_tests(self.P, adjustment)
        G = nx.Graph(np.logical_and(np.isfinite(P), P >= alpha))
        groups = list(nx.find_cliques(G)) # groups = maximal cliques
        r_min = np.empty(len(groups)) # minimum and maximum rank per group
        r_max = np.empty(len(groups))
        for i in range(len(groups)):
            r_g = self.average_ranks[groups[i]]
            r_min[i] = np.min(r_g)
            r_max[i] = np.max(r_g)
        is_maximal = np.empty(len(groups), bool)
        for i in range(len(groups)):
            is_maximal[i] = np.all(np.logical_and(
                np.logical_or(r_min > r_min[i], r_max <= r_max[i]),
                np.logical_or(r_min >= r_min[i], r_max < r_max[i])
            ))
        groups = [ g for (g, i) in zip(groups, is_maximal) if i ] # remove non-maximal groups
        if return_names:
            names = []
            for g in groups:
                names.append(list(self.treatment_names[g]))
            return names
        return groups

    def to_str(self, alpha=.05, adjustment="holm", **kwargs):
        """Get a ``str`` object with the Tikz code for this diagram.

        Args:
            alpha (optional): The threshold for rejecting a p value. Defaults to 0.05.
            adjustment (optional): The multiple testing adjustment. Defaults to "holm". Another possible value is "bonferroni".
            title (optional): The title of this diagram. Defaults to None.
            reverse_x (optional): Whether to reverse the x direction. Defaults to False.

        Returns:
            A ``str`` object with the Tikz code for this diagram.
        """
        return tikz.to_str(
            self.average_ranks,
            self.get_groups(alpha, adjustment),
            self.treatment_names,
            **kwargs
        )

    def to_file(self, path, alpha=.05, adjustment="holm", **kwargs):
        """Store this diagram in a file.

        Note:
            Storing Tikz code in a ".png" file or ".svg" file is not yet supported.

        Args:
            path: The file path where this diagram is to be stored. Has to be ending on ".tex", ".tikz", ".pdf", ".png", or ".svg".
            alpha (optional): The threshold for rejecting a p value. Defaults to 0.05.
            adjustment (optional): The multiple testing adjustment. Defaults to "holm". Another possible value is "bonferroni".
            title (optional): The title of this diagram. Defaults to None.
            reverse_x (optional): Whether to reverse the x direction. Defaults to False.
        """
        return tikz.to_file(
            path,
            self.average_ranks,
            self.get_groups(alpha, adjustment),
            self.treatment_names,
            **kwargs
        )

def _pairwise_tests(X):
    k = X.shape[1] # number of treatments
    P = np.ones((k, k)) * np.nan
    for i in range(1, k):
        for j in range(i):
            P[i,j] = stats.wilcoxon(
                X[:,i],
                X[:,j],
                method = "exact",
                zero_method = 'pratt'
            ).pvalue
    return P

def _adjust_pairwise_tests(P, adjustment):
    ij_finite = np.argwhere(np.isfinite(P))
    p = np.array([ P[tuple(ij)] for ij in ij_finite ]) # flat array of finite elements
    sortperm = np.argsort(p)
    p_ = p[sortperm] # sorted p values
    if adjustment == "holm":
        p_ = np.maximum.accumulate(p_ * np.arange(len(p_), 0, -1))
    elif adjustment == "bonferroni":
        p_ *= len(p_)
    else:
        raise ValueError("adjustment must be either \"holm\" or \"bonferroni\"")
    p[sortperm] = p_ # restore the original order
    P = np.ones_like(P) * np.nan
    for ((i, j), p_ij) in zip(ij_finite, p):
        P[i,j] = p_ij
    return P
