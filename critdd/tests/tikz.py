from critdd import tikz
from unittest import TestCase

class TestTikz(TestCase):
  def test_tikz(self):
    self.assertEqual(tikz._label("with_under_score"), "with\\_under\\_score")
    self.assertEqual(tikz._label("with\\_under_score"), "with\\_under\\_score")
    self.assertEqual(
      tikz._label("with_equations $n_i$ and $m_j$"),
      "with\\_equations $n_i$ and $m_j$"
    )
    self.assertEqual(
      tikz._label("$\\mathrm{full}_\\text{equation}$"),
      "$\\mathrm{full}_\\text{equation}$"
    )
