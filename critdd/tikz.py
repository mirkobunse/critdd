"""A module for the Tikz export."""

import os, re

def to_str(average_ranks, cliques):
    """Return a string with Tikz code."""
    return _tikzpicture(_axis("TODO", ["title={foo}", "axis x line=center"])) # TODO

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

def _tikzpicture(content):
    return "\n".join(["\\begin{tikzpicture}[]", content, "\\end{tikzpicture}\n"])
def _axis(content, options):
    return "\n".join([
        "\\begin{axis}[",
        _indent(",\n".join(options)) + ",",
        "]\n",
        content,
        "\n\\end{axis}"
    ])
def _indent(content):
    return re.sub("^", "  ", content, flags=re.MULTILINE)
