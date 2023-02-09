import critdd
import numpy as np
from unittest import TestCase

RNG = np.random.RandomState(876) # make tests reproducible

class TestReadMe(TestCase):
  def test_ReadMe(self):
    pass

class TestFriedman(TestCase):
  def test_random_rejection(self):
    X = RNG.rand(20, 3)
    r = critdd.friedman(X)
    self.assertTrue(r.pvalue > .05) # random data should lead to a rejection
