"""
A module for Friedman hypothesis tests.

These hypothesis tests are implemented in analogy to the hypothesis tests that are implemented in ``scipy.stats``.
"""

import numpy as np
from scipy import stats
from scipy._lib._bunch import _make_tuple_bunch

def friedman(X, *, maximize_outcome=False):
    """Calculate the Friedman hypothesis test.

    The Friedman test tests the null hypothesis that ``n`` observations have the same distribution across all ``k`` treatments. This version of the test uses an F-distributed test statistic.

    Args:
        X: An ``(n, k)``-shaped matrix of observations.
        maximize_outcome: Whether the ranks represent a maximization (True) or a minimization (False) of the outcome. Defaults to False.

    Returns:
        r: An ``FDistributedFriedmanResult`` with properties ``pvalue`` (the p value), ``statistic`` (the test statistic), ``chi_square_result`` (a ``ChiSquareFriedmanResult``), ``n_df_1`` (first number of degrees of freedom), and ``n_df_2`` (second number of degrees of freedom). The ``chi_square_result`` has additional properties ``average_ranks`` (the average ranks of the treatments), ``n`` (the number of observations), and ``maximize_outcome``.
    """
    return f_distributed(X, maximize_outcome=maximize_outcome)

FDistributedFriedmanResult = _make_tuple_bunch(
    "FDistributedFriedmanResult",
    ["pvalue", "statistic", "chi_square_result", "n_df_1", "n_df_2"]
)

ChiSquareFriedmanResult = _make_tuple_bunch(
    "ChiSquareFriedmanResult",
    ["pvalue", "statistic", "n_df", "average_ranks", "n", "maximize_outcome"]
)

def f_distributed(X, *, maximize_outcome=False):
    """This version of the Friedman test uses an F-distributed test statistic."""
    r = chi_square_distributed(X, maximize_outcome=maximize_outcome)
    k = len(r.average_ranks) # number of treatments
    statistic = (r.n - 1) * r.statistic / (r.n * (k - 1) - r.statistic)
    n_df_1 = k-1
    n_df_2 = (k-1)*(r.n-1)
    return FDistributedFriedmanResult(
        _pvalue(stats.f(n_df_1, n_df_2), statistic, tail="right"),
        statistic,
        r,
        n_df_1,
        n_df_2
    )

def chi_square_distributed(X, *, maximize_outcome=False):
    """This version of the Friedman test uses a Chi-square-distributed test statistic."""
    n, k = X.shape
    if k < 3:
        raise ValueError("The Friedman test requires at least 3 treatments")
    average_ranks = np.mean(stats.rankdata(-X if maximize_outcome else X, axis=1), axis=0)
    statistic = 12*n/(k*(k+1)) * np.sum((average_ranks - (k+1)/2)**2)
    n_df = k-1
    return ChiSquareFriedmanResult(
        _pvalue(stats.chi2(n_df), statistic, tail="right"),
        statistic,
        n_df,
        average_ranks,
        n,
        maximize_outcome
    )

def _pvalue(rv, statistic, tail="both"):
    """Compute a p value from a random variable ``rv``."""
    cdf = rv.cdf(statistic)
    if tail == "both":
        return np.min(1, 2 * np.min(cdf, 1-cdf))
    elif tail == "left":
        return cdf
    elif tail == "right":
        return 1 - cdf
    else:
        raise ValueError(f"tail must be either \"both\", \"left\", or \"right\"")
