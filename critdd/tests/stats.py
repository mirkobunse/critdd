import numpy as np
from critdd import stats
from unittest import TestCase

class TestFriedman(TestCase):
  def test_catalysts_example(self):
    X_catalysts = np.array([
      [84.5, 78.4, 83.1],
      [82.8, 79.1, 79.9],
      [79.1, 78.0, 77.8],
      [80.2, 76.0, 77.9],
    ]) # http://calcscience.uwe.ac.uk/w2/am/Ch12/12_5_KWFriedman.pdf

    r = stats.chi_square_distributed(X_catalysts) # example 12.12
    self.assertAlmostEqual(r.statistic, 6.5)
    self.assertLess(r.pvalue, 0.05) # reject that all are equal
    self.assertEqual(r.n_df, 2)
    self.assertEqual(len(r.average_ranks), 3)
    self.assertEqual(r.n, 4)

    r = stats.chi_square_distributed(X_catalysts.transpose()) # example 12.13
    self.assertAlmostEqual(r.statistic, 7.4)
    self.assertGreaterEqual(r.pvalue, 0.05)
    self.assertEqual(r.n_df, 3)
    self.assertEqual(len(r.average_ranks), 4)
    self.assertEqual(r.n, 3)

  def test_trees_example(self):
    X_trees = np.array([
      [6, 4, 3, 3], # tree 1
      [4, 3, 3, 2], # tree 2
      [4, 2, 1, 1], # tree 3
      [2, 1, 2, 1], # tree 4
    ]).transpose()
    r = stats.chi_square_distributed(X_trees) # assignment Q12.8
    self.assertAlmostEqual(r.statistic, 9.525)
    self.assertLess(r.pvalue, 0.05)
    self.assertEqual(r.n_df, 3)
    self.assertEqual(len(r.average_ranks), 4)
    self.assertEqual(r.n, 4)

    r_f = stats.f_distributed(X_trees)
    self.assertLessEqual(r_f.pvalue, r.pvalue) # Chi square is more conservative than F
    self.assertTrue(np.all(r_f.chi_square_result.average_ranks == r.average_ranks))

  def test_random_rejection(self):
    X = np.random.RandomState(0).rand(20, 3)
    r = stats.friedman(X)
    self.assertGreaterEqual(r.pvalue, .05) # random data should not lead to a rejection
