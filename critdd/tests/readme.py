import numpy as np
import pandas as pd
import os
from critdd import Diagram
from unittest import TestCase

_URL = "https://raw.githubusercontent.com/hfawaz/cd-diagram/master/example.csv"

class TestReadMe(TestCase):
  def test_readme(self):
    df = pd.read_csv(_URL).pivot(
      index = "dataset_name",
      columns = "classifier_name",
      values = "accuracy"
    )
    diagram = Diagram(
      df.to_numpy(),
      treatment_names = df.columns,
      maximize_outcome = True
    )

    # check the content of the diagram
    expected_ranks = np.array([4.2, 3.75, 1.5, 3.5, 2.])
    self.assertTrue(np.all(diagram.average_ranks - expected_ranks < 0.05))
    groups = diagram.get_groups(return_names=True)
    self.assertTrue(["clf1", "clf2", "clf4"] in groups)
    self.assertTrue(["clf3", "clf5"] in groups)

    # check the tikz export
    output_path = "__example__.tex"
    if os.path.exists(output_path):
      os.remove(output_path) # make sure the file does not exist already
    diagram.to_file(output_path, title="critdd", reverse_x=True)
    self.assertTrue(os.path.exists(output_path))
    with open(output_path, "r") as f: # print the file contents
      print("\n"+"-"*32, f.read(), "-"*32+"\n", sep="\n")
