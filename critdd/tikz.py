"""A module for the Tikz export."""

import numpy as np
import os, re, subprocess

def to_file(path, average_ranks, groups, treatment_names, **kwargs):
    """Store the Tikz code in a file."""
    root, ext = os.path.splitext(path)
    if ext not in [ ".tex", ".tikz", ".pdf", ".svg", ".png" ]:
        raise ValueError("Unknown file path extension")
    if ext in [ ".pdf", ".svg", ".png" ]:
        kwargs["as_document"] = True # export an entire document, not only a tikzpicture
        path = root + ".tex"
    with open(path, "w") as f: # store the Tikz code in a .tex or .tikz file
        f.write(to_str(average_ranks, groups, treatment_names, **kwargs))
    if ext in [ ".tex", ".tikz" ]:
        return None # we are done here
    pdflatex = subprocess.Popen(["pdflatex", path], stdout=subprocess.PIPE)
    (out, err) = pdflatex.communicate() # convert to PDF
    if ext in [ ".svg", ".png" ]:
        raise NotImplementedError(f"{ext} export is not yet implemented")

def to_str(average_ranks, groups, treatment_names, *, title=None, reverse_x=False, as_document=False):
    """Return a string with Tikz code."""
    tikzpicture_options = [ # general styling
        "treatment line/.style={semithick, rounded corners=1pt}",
        "treatment label/.style={font=\\small, fill=white, text=black, inner xsep=5pt, outer xsep=-5pt}",
        "group line/.style={ultra thick, line cap=round}",
    ]
    k = len(average_ranks)
    changepoint = np.ceil(k/2)
    axis_options = [
        "clip=false",
        "axis x line=center",
        "axis y line=none",
        "xmin=1",
        f"xmax={k}",
        f"ymin={-(changepoint+1.5)}",
        "ymax=0",
        "scale only axis",
        f"height={changepoint+2}\\baselineskip",
        "width=\\axisdefaultwidth",
        "ticklabel style={anchor=south, yshift=1.3*\\pgfkeysvalueof{/pgfplots/major tick length}, font=\\small}",
        "every tick/.style={yshift=.5*\\pgfkeysvalueof{/pgfplots/major tick length}}",
        "axis line style={-}",
        "title style={yshift=\\baselineskip}",
    ]
    if k <= 5:
        axis_options.append(f"xtick={{{','.join((np.arange(k)+1).astype(str))}}}")
    if reverse_x:
        axis_options.append("x dir=reverse")
    if title is not None:
        axis_options.append(f"title={{{title}}}")
    if not reverse_x and k % 2: # if k is odd
        changepoint -= 1
    changepoint -= 1
    commands = []
    for (i, j) in enumerate(np.argsort(average_ranks)): # add treatment commands
        xpos = 1 if i < changepoint else k
        if reverse_x:
            ypos = 2 + (i if i < changepoint else (k - i - (1.5 if k % 2 else 1)))
        else:
            ypos = (.5 if k % 2 else .0) + (i + .5 if i < changepoint else k - i + (1 if k % 2 else 1.5))
        commands.append(_treatment(
            treatment_names[j],
            average_ranks[j],
            xpos,
            ypos,
            reverse_x
        ))
    for i in range(len(groups)):
        commands.append(_group(
            np.min(average_ranks[groups[i]]),
            np.max(average_ranks[groups[i]]),
            1.5 * (i+1) / (len(groups)+1)
        ))
    tikz_str = _tikzpicture(
        _axis(*commands, options=axis_options),
        options = tikzpicture_options
    )
    if as_document:
        tikz_str = _document(tikz_str)
    return tikz_str

def _indent(content):
    return re.sub("^", "  ", content, flags=re.MULTILINE)
def _environment(name, *contents, options=[]):
    options_str = ""
    if len(options) > 0:
        options_str = "[\n" + _indent(",\n".join(options)) + ",\n]\n"
    return "\n".join([
        f"\\begin{{{name}}}" + options_str,
        *contents,
        f"\n\\end{{{name}}}"
    ])
def _document(*contents):
    return "\n".join([
        "\\documentclass[tikz,margin=.1in]{standalone}",
        "\\usepackage{pgfplots,lmodern}",
        "\\pgfplotsset{compat=newest}\n",
        _environment("document", *contents)
    ])
def _tikzpicture(*contents, options=[]):
    return _environment("tikzpicture", *contents, options=options)
def _axis(*contents, options=[]):
    return _environment("axis", *contents, options=options)
def _treatment(label, rank, xpos, ypos, reverse_x):
    anchor = "west" if (int(xpos == 1) + int(reverse_x)) % 2 == 0 else "east"
    return f"\\draw[treatment line] (axis cs:{rank}, 0) |- (axis cs:{xpos}, {-ypos})\n  node[treatment label, anchor={anchor}] {{{label}}};"
def _group(minrank, maxrank, ypos):
    return f"\\draw[group line] (axis cs:{minrank}, {-ypos}) -- (axis cs:{maxrank}, {-ypos});"
