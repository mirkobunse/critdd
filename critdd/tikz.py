"""A module for the Tikz export."""

import os

def to_str(average_ranks, cliques):
    """Return a string with Tikz code."""
    return "TODO\n...\n" # TODO

def to_file(path, average_ranks, cliques):
    """Store the Tikz code in a file."""
    root, ext = os.path.splitext(path)
    if ext in [ ".tex", ".tikz" ]:
        _to_tikz_file(path, average_ranks, cliques)
    elif ext in [ ".pdf", ".svg", ".png" ]:
        # _to_tikz_file(root + ".tex", average_ranks, cliques) # first export to .tex
        raise NotImplementedError(f"{ext} export is not yet implemented")
    else:
        raise ValueError("Unknown file path extension")

def _to_tikz_file(path, average_ranks, cliques):
    """Store the Tikz code in a .tex or .tikz file."""
    with open(path, "w") as f:
        f.write(to_str(average_ranks, cliques))
