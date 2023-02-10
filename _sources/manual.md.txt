# Manual

This manual provides you with more background information on CD diagrams.


## Reading a CD diagram

Let's take a look at the treatments ``clf1`` to ``clf5``. Their position represents their mean ranks across all outcomes of the observations, where low ranks indicate that a treatment wins more often than its competitors with higher ranks. Two or more treatments are connected with each other if we can not tell their outcomes apart, in the sense of statistical significance. For the above example, we can not tell from the data whether ``clf3`` and ``clf5`` are actually different from each other. We can tell, however, that both of them are different from all of the other treatments. This example above is adapted from [github.com/hfawaz/cd-diagram](https://github.com/hfawaz/cd-diagram).

<img alt="example.svg" src="example.svg" width="480">


## Hypothesis testing

A diagram like the one above concisely represents multiple hypothesis tests that are conducted over the observed outcomes. Before anything is plotted at all, the *Friedman test* tells us whether there are significant differences at all. If this test fails, we have not sufficient data to tell any of the treatments apart and we must abort. If, however, the test sucessfully rejects this possibility we can proceed with the post-hoc analysis. In this second step, a *Wilcoxon signed-rank test* tells us whether each pair of treatments exhibits a significant difference.


## Multiple testing

Since we are testing multiple hypotheses, we must *adjust* the Wilcoxon test with Holm's method or with Bonferroni's method. For each group of treatments which we can not distinguish from the Holm-adjusted (or Bonferroni-adjusted) Wilcoxon test, we add a thick line to the diagram.

Whether we choose Holm's method or Bonferroni's method for the adjustment depends on our personal requirements. Holm's method has the advantage of a greater statistical power than Bonferroni's method, i.e., this adjustment is capable of rejecting more null hypotheses that indeed should be rejected. However, its disadvantage is that the rejection of each null hypothesis depends on the outcome of other null hypotheses. If this property is not desired, one should instead use Bonferroni's method, which ensures that each pair-wise hypothesis test is independent from all others.


## Cautions

The hypothesis tests underneath the CD diagram do not account for variances of the outcomes. It is therefore important that these outcomes are *reliable* in the sense that each of them is obtained from a sufficiently large sample. Ideally, they come from a cross validation or from a repeated stratified split. Moreover, all treatments must have been evaluated on the same set of observations.

The adjustments by Holm and Bonferroni can lead to different indistinguishable groups. For more information, see the [Multiple testing](#multiple-testing) section above.


## Citing

CD diagrams have originally been proposed in the following article:

```
@article{demsar2006statistical,
  title={Statistical comparisons of classifiers over multiple data sets},
  author={Dem{\v{s}}ar, Janez},
  journal={The Journal of Machine learning research},
  volume={7},
  number={1},
  pages={1--30},
  year={2006}
}
```

However, the above article favors Nemenyi's test for the post-hoc analysis.
It has later been argued that Wilcoxon's signed rank test (or the sign test)
are more appropriate for the post-hoc assessment of the pairwise differences:

```
@article{benavoli2016should,
  title={Should we really use post-hoc tests based on mean-ranks?},
  author={Benavoli, Alessio and Corani, Giorgio and Mangili, Francesca},
  journal={The Journal of Machine Learning Research},
  volume={17},
  number={1},
  pages={152--161},
  year={2016}
}
```
