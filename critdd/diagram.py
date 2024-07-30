"""A module for assembling critical difference diagrams."""

import networkx as nx
import numpy as np
from abc import ABC, abstractmethod
from . import stats, tikz, tikz_2d

class AbstractDiagram(ABC):
    """Abstract base class for critical difference diagrams in Tikz."""
    @abstractmethod
    def to_str(self, alpha=.05, adjustment="holm", **kwargs):
        """Get a ``str`` object with the Tikz code for this diagram.

        Args:
            alpha (optional): The threshold for rejecting a p value. Defaults to 0.05.
            adjustment (optional): The multiple testing adjustment. Defaults to "holm". Another possible value is "bonferroni".
            reverse_x (optional): Whether to reverse the x direction. Defaults to False.
            as_document (optional): Whether to include a ``\\documentclass`` and a ``document`` environment. Defaults to False.
            tikzpicture_options (optional): A ``dict`` with options for the ``tikzpicture`` environment.
            axis_options (optional): A ``dict`` with options for the ``axis`` environment.
            preamble (optional): A ``str`` with LaTeX commands. Only used if ``as_document==True``. Defaults to None.

        Returns:
            A ``str`` object with the Tikz code for this diagram.
        """
        pass

    def to_file(self, path, *args, **kwargs):
        """Store this diagram in a file.

        Note:
            Storing Tikz code in a ".png" file or ".svg" file is not yet supported.

        Args:
            path: The file path where this diagram is to be stored. Has to be ending on ".tex", ".tikz", ".pdf", ".png", or ".svg".
            *args (optional): See ``to_str``.
            **kwargs (optional): See ``to_str``.
        """
        if tikz.requires_document(path):
            kwargs["as_document"] = True
        return tikz.to_file(path, self.to_str(*args, **kwargs))

class Diagram(AbstractDiagram):
    """A regular critical difference diagram.

    Args:
        X: An ``(n, k)``-shaped matrix of observations, where ``n`` is the number of observations and ``k`` is the number of treatments.
        treatment_names (optional): The names of the ``k`` treatments. Defaults to None.
        maximize_outcome (optional): Whether the ranks represent a maximization (True) or a minimization (False) of the outcome. Defaults to False.
    """
    def __init__(self, X, *, treatment_names=None, maximize_outcome=False):
        if treatment_names is None:
            treatment_names = [ f"treatment {i}" for i in range(X.shape[1]) ]
        elif len(treatment_names) != X.shape[1]:
            raise ValueError("len(treatment_names) != X.shape[1]")
        self.treatment_names = np.array(treatment_names)
        self.r = stats.friedman(X, maximize_outcome=maximize_outcome)
        self.P = stats.pairwise_tests(X)

    @property
    def maximize_outcome(self):
        return self.r.chi_square_result.maximize_outcome
    @property
    def average_ranks(self):
        return self.r.chi_square_result.average_ranks

    def to_str(self, alpha=.05, adjustment="holm", **kwargs):
        return tikz.to_str(
            self.average_ranks,
            self.get_groups(alpha, adjustment, return_singletons=False),
            self.treatment_names,
            **kwargs
        )

    def get_groups(self, alpha=.05, adjustment="holm", return_names=False, return_singletons=True):
        """Get the groups of indistinguishable treatments.

        Args:
            alpha (optional): The threshold for rejecting a p value. Defaults to 0.05.
            adjustment (optional): The multiple testing adjustment. Defaults to "holm". Another possible value is "bonferroni".
            return_names (optional): Whether to represent the treatments in the groups by their names (True) or by their indices (False). Defaults to False.
            return_singletons (optional): Whether to return groups with single elements. Defaults to True.

        Returns:
            A list of statistically indistinguishable groups.
        """
        if self.r.pvalue >= alpha: # does the Friedman test fail to reject?
            return [ np.arange(len(self.average_ranks)) ] # all treatments in a single group
        P = stats.adjust_pairwise_tests(self.P, adjustment)
        G = nx.Graph(np.logical_and(np.isfinite(P), P >= alpha))
        groups = list(nx.find_cliques(G)) # groups = maximal cliques
        r_min = np.empty(len(groups)) # minimum and maximum rank per group
        r_max = np.empty(len(groups))
        for i in range(len(groups)):
            r_g = self.average_ranks[groups[i]]
            r_min[i] = np.min(r_g)
            r_max[i] = np.max(r_g)
            groups[i] = np.unique(np.concatenate((
                groups[i],
                np.flatnonzero(np.logical_and(
                    self.average_ranks >= r_min[i],
                    self.average_ranks <= r_max[i]
                ))
            ))) # insert intermediate ranks: {r_n, r_{n+m}} -> {r_n, r_{n+1}, ..., r_{n+m}}
        is_maximal = np.empty(len(groups), bool)
        for i in range(len(groups)):
            is_maximal[i] = np.all(np.logical_and(
                np.logical_or(r_min > r_min[i], r_max <= r_max[i]),
                np.logical_or(r_min >= r_min[i], r_max < r_max[i])
            ))
        groups = [ g for (g, i) in zip(groups, is_maximal) if i ] # remove non-maximal groups
        groups = [ np.array(g) for g in set(tuple(g) for g in groups) ] # remove duplicates
        if not return_singletons:
            groups = list(filter(lambda g: len(g) > 1, groups))
        if return_names:
            names = []
            for g in groups:
                names.append(list(self.treatment_names[g]))
            return names
        return groups

class Diagrams(AbstractDiagram):
    """A sequence of critical difference diagrams, plotted on a single 2-dimensional axis.

    Args:
        Xs: Observations, given either as a list of length ``m`` of ``(n, k)``-shaped matrices or as an ``(m, n, k)``-shaped tensor, where ``m`` is the number of diagrams, ``n`` is the number of observations, and ``k`` is the number of treatments.
        diagram_names (optional): The names of the ``m`` diagrams. Defaults to None.
        treatment_names (optional): The names of the ``k`` treatments. Defaults to None.
        maximize_outcome (optional): Whether the ranks represent a maximization (True) or a minimization (False) of the outcome. Defaults to False.
    """
    def __init__(
            self,
            Xs,
            *,
            diagram_names = None,
            treatment_names = None,
            maximize_outcome = False,
            ):
        n_diagrams = len(Xs)
        n_treatments = Xs[0].shape[1]
        if not np.all([ X.shape[1] == n_treatments for X in Xs ]):
            raise ValueError("Xs has elements with different numbers of treatments")
        if diagram_names is None:
            diagram_names = [ f"diagram {i+1}" for i in range(n_diagrams) ]
        elif len(diagram_names) != n_diagrams:
            raise ValueError("len(diagram_names) != len(Xs)")
        if treatment_names is None:
            treatment_names = [ f"treatment {i+1}" for i in range(n_treatments) ]
        elif len(treatment_names) != n_treatments:
            raise ValueError("len(treatment_names) != Xs[i].shape[1]")
        self.diagram_names = diagram_names
        self.diagrams = [
            Diagram(X, treatment_names=treatment_names, maximize_outcome=maximize_outcome)
            for X in Xs
        ]

    def __getitem__(self, i):
        return self.diagrams[i]

    @property
    def maximize_outcome(self):
        return self.diagrams[0].maximize_outcome
    @property
    def treatment_names(self):
        return self.diagrams[0].treatment_names

    def to_str(self, alpha=.05, adjustment="holm", **kwargs):
        return tikz_2d.to_str(
            np.stack([ d.average_ranks for d in self.diagrams ]),
            [ d.get_groups(alpha, adjustment, return_singletons=False) for d in self.diagrams ],
            self.treatment_names,
            self.diagram_names,
            **kwargs
        )
