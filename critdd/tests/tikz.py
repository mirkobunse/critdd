from critdd import tikz
from unittest import TestCase

class TestTikz(TestCase):
  def test_tikz(self):
    self.assertEqual(tikz._label("with_underscore"), "with\\_underscore")
    self.assertEqual(tikz._label("with\\_underscore"), "with\\_underscore")
