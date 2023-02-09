import critdd
import numpy as np
from unittest import TestCase

RNG = np.random.RandomState(876) # make tests reproducible

class TestReadMe(TestCase):
  def test_ReadMe(self):
    self.assertTrue(critdd.friedman()) # TODO
