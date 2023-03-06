"""A module for the Tikz export."""

import numpy as np
import os, re, subprocess, warnings

class ExportException(Exception):
    def __init__(self, path):
        super().__init__(f"Failed to produce {path}")

TIKZPICTURE_OPTIONS = { # general styling
    "treatment line/.style": "rounded corners=1.5pt, line cap=round, shorten >=1pt",
    "treatment label/.style": "font=\\small",
    "group line/.style": "ultra thick",
}

AXIS_OPTIONS = { # basic axis options, which don't depend on the diagram values
    "clip": "false",
    "axis x line": "center",
    "axis y line": "none",
    "axis line style": "line cap=round",
    "xmin": "1",
    "ymax": "0",
    "scale only axis": "true",
    "width": "\\axisdefaultwidth",
    "ticklabel style": "anchor=south, yshift=1.3*\\pgfkeysvalueof{/pgfplots/major tick length}, font=\\small",
    "every tick/.style": "draw=black",
    "major tick style": "yshift=.5*\\pgfkeysvalueof{/pgfplots/major tick length}",
    "minor tick style": "yshift=.5*\\pgfkeysvalueof{/pgfplots/minor tick length}",
    "axis line style": "-",
    "title style": "yshift=\\baselineskip",
}

def to_file(path, tikz_code):
    """Export the tikz_code to a file."""
    root, ext = os.path.splitext(path)
    if ext not in [ ".tex", ".tikz", ".pdf", ".svg", ".png" ]:
        raise ValueError("Unknown file path extension")
    if ext in [ ".pdf", ".svg", ".png" ]:
        path = root + ".tex"
    with open(path, "w") as f: # store the Tikz code in a .tex or .tikz file
        f.write(tikz_code)
    if ext in [ ".tex", ".tikz" ]:
        return None # we are done here
    pdflatex = subprocess.Popen(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", path],
        stdout = subprocess.PIPE
    )
    (out, err) = pdflatex.communicate() # convert to PDF
    if pdflatex.returncode:
        print(out.decode())
        raise ExportException(root + ".pdf")
    if ext == ".svg":
        pdf_to_svg = subprocess.Popen(
            ["pdf2svg", root + ".pdf", root + ".svg"],
            stdout = subprocess.PIPE
        )
        (out, err) = pdf_to_svg.communicate() # convert to SVG
        if pdf_to_svg.returncode:
            print(out.decode())
            raise ExportException(root + ".svg")
    elif ext == ".png":
        raise NotImplementedError(f"{ext} export is not yet implemented")

def requires_document(path):
    """Determine whether an export requires as_document=True."""
    return os.path.splitext(path)[1] in [ ".pdf", ".svg", ".png" ]

def to_str(average_ranks, groups, treatment_names, *, reverse_x=False, as_document=False, tikzpicture_options=dict(), axis_options=dict(), preamble=None, title=None):
    """Return a string with Tikz code."""
    if title is not None:
        axis_options |= {"title": title} # set the title
        warnings.warn(
            "to_str(..., title=x) will be retired in v0.1, please use to_str(..., axis_options={\"title\": title}) instead.",
            DeprecationWarning
        )
    k = len(average_ranks)
    changepoint = int(np.floor(k/2)) # index for breaking left and right treatments
    axis_defaults = AXIS_OPTIONS | { # diagram-dependent axis options
        "xmax": str(k),
        "ymin": str(-(changepoint+1.5)),
        "height": f"{changepoint+2}\\baselineskip", # ceil(k/2) + 1 extra \\baselikeskip
    }
    if k <= 8:
        axis_defaults["xtick"] = ",".join((np.arange(k)+1).astype(str))
        if k <= 6:
            axis_defaults["minor x tick num"] = "3"
        else:
            axis_defaults["minor x tick num"] = "1"
    elif k == 10: # [1,2.5,4,5.5,...,k] for k == 10
        axis_defaults["xtick"] = ",".join((np.arange(1,k+1,1.5)).astype(str))
        axis_defaults["minor x tick num"] = "2"
    elif k >= 10 and (k-1) % 3 == 0: # [1,4,7,...,k] for k >= 13
        axis_defaults["xtick"] = ",".join((np.arange(1,k+1,3)).astype(str))
        axis_defaults["minor x tick num"] = "1"
    elif k % 2 == 1: # [1,3,5,...,k] for k >= 7
        axis_defaults["xtick"] = ",".join((np.arange(1,k+1,2)).astype(str))
        axis_defaults["minor x tick num"] = "1"
    if reverse_x:
        axis_defaults["x dir"] = "reverse"
    sortperm = np.argsort(average_ranks) # add treatments in their ranking order
    is_high = np.empty(len(average_ranks), bool)
    is_high[sortperm] = np.concatenate((
        np.zeros(changepoint),
        np.ones(k-changepoint),
    ))
    x_pos = np.ones(k) * np.min(average_ranks) -k/12
    x_pos[is_high] = np.max(average_ranks) + k/12
    y_pos = np.empty(len(average_ranks))
    y_pos[sortperm] = np.concatenate((
        2 + np.arange(changepoint) + (.5 if k % 2 else 0),
        1 + np.arange(k-changepoint, 0, -1),
    ))
    anchors = np.array(["west", "east"])[(is_high if reverse_x else ~is_high).astype(int)]
    y_group_pos = np.array([ np.min(y_pos[g]) for g in groups ]) * 2/3
    y_group_order = np.argsort(y_group_pos)
    for i in range(len(y_group_pos)-1):
        if len(np.intersect1d(groups[y_group_order[i+1]], groups[y_group_order[i]])) > 0:
            y_group_pos[y_group_order[i+1]] = np.maximum(
                y_group_pos[y_group_order[i+1]],
                y_group_pos[y_group_order[i]] + .2
            ) # ensure a minimum distance between vertically adjacent, overlapping groups
    commands = []
    for i in np.arange(k)[sortperm]:
        commands.append(_treatment(
            treatment_names[i],
            average_ranks[i],
            x_pos[i],
            y_pos[i],
            anchors[i],
            reverse_x
        ))
    for i in range(len(groups)):
        commands.append(_group(
            np.min(average_ranks[groups[i]]),
            np.max(average_ranks[groups[i]]),
            y_group_pos[i]
        ))
    tikz_str = _tikzpicture(
        _axis(*commands, options=axis_defaults | axis_options),
        options = TIKZPICTURE_OPTIONS | tikzpicture_options
    )
    if as_document:
        tikz_str = _document(tikz_str, preamble=preamble)
    return tikz_str

def _indent(content):
    return re.sub("^", "  ", content, flags=re.MULTILINE)
def _environment(name, *contents, options=dict()):
    options_str = ""
    if len(options) > 0:
        options_str = "".join([
            "[\n",
            _indent(",\n".join([ f"{k}={{{options[k]}}}" for k in options.keys() ])),
            ",\n]\n"
        ])
    return "\n".join([
        f"\\begin{{{name}}}" + options_str,
        *contents,
        f"\\end{{{name}}}"
    ])
def _document(*contents, preamble=None):
    return "\n".join([
        "\\documentclass[tikz,margin=.1in]{standalone}",
        "\\usepackage{pgfplots,lmodern}",
        "\\pgfplotsset{compat=newest}",
        "" if preamble is None else "\n" + preamble + "\n",
        _environment("document", *contents),
        ""
    ])
def _tikzpicture(*contents, options=[]):
    return _environment("tikzpicture", *contents, options=options)
def _axis(*contents, options=[]):
    return _environment("axis", *contents, "", options=options)
def _treatment(label, rank, xpos, ypos, anchor, reverse_x):
    return f"\\draw[treatment line] ([yshift=-2pt] axis cs:{rank}, 0) |- (axis cs:{xpos}, {-ypos})\n  node[treatment label, anchor={anchor}] {{{_label(label)}}};"
def _label(label):
    return re.sub("(?<!\\\\)_", "\\\\_", label) # replace "_", but not "\_", with "\_"
def _group(minrank, maxrank, ypos):
    return f"\\draw[group line] (axis cs:{minrank}, {-ypos}) -- (axis cs:{maxrank}, {-ypos});"
