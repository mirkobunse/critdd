"""A module for assembling critical difference diagrams."""

import networkx as nx
import numpy as np
from scipy import stats
from .stats import friedman

def _pairwise_tests(X):
    k = X.shape[1] # number of treatments
    P = np.ones((k, k)) * np.nan
    for i in range(1, k):
        for j in range(i):
            P[i,j] = stats.wilcoxon(X[:,i], X[:,j], method="approx").pvalue
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

class Diagram(): # TODO extend to an arbitrary number of *Xs
    """A critical difference diagram."""
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

    def get_cliques(self, alpha=.05, adjustment="holm", return_names=False):
        if self.r.pvalue >= alpha: # does the Friedman test fail to reject?
            return [ np.arange(len(self.average_ranks)) ] # all treatments in a single clique
        P = _adjust_pairwise_tests(self.P, adjustment)
        G = nx.Graph()
        for ij in np.argwhere(np.logical_and(np.isfinite(P), P >= alpha)):
            G.add_edge(*ij)
        cliques = list(nx.find_cliques(G)) # maximal cliques
        # TODO dominating?
        if return_names:
            names = []
            for c in cliques:
                names.append(list(self.treatment_names[c]))
            return names
        return cliques
