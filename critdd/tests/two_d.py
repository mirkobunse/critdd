import numpy as np
import pandas as pd
import os
from critdd import Diagrams
from unittest import TestCase

_URL = "https://raw.githubusercontent.com/hfawaz/cd-diagram/master/example.csv"

class Test2d(TestCase):
  def test_2d(self):
    df = pd.read_csv(_URL).pivot(
      index = "dataset_name",
      columns = "classifier_name",
      values = "accuracy"
    )
    diagrams = Diagrams(
      np.stack((df.to_numpy(), 1 - df.to_numpy())),
      treatment_names = df.columns,
      diagram_names = [ "accuracy", "1-accuracy" ],
      maximize_outcome = True
    )

    # check the content of the diagram
    expected_ranks = np.array([4.2, 3.75, 1.5, 3.5, 2.])
    self.assertTrue(np.all(diagrams[0].average_ranks - expected_ranks < 0.05))
    groups = diagrams[0].get_groups(return_names=True)
    self.assertTrue(["clf1", "clf2", "clf4"] in groups)
    self.assertTrue(["clf3", "clf5"] in groups)

    # check the tikz export
    output_path = "__2d_example__.pdf"
    if os.path.exists(output_path):
      os.remove(output_path) # make sure the file does not exist already
    diagrams.to_file(
        output_path,
        alpha = .05,
        adjustment = "holm",
        reverse_x = True,
        axis_options = {"title": "critdd"},
    )
    self.assertTrue(os.path.exists(output_path))
