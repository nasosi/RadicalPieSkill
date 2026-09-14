"""The LaTeX pipeline: a document whose equations are Radical Pie renderings.

The author writes ordinary LaTeX, loads `\\usepackage{radicalpie}` and puts `\\pie{<key>}` where an equation
goes, inline in a sentence or alone inside `equation`, `align` or `\\[ \\]`, so LaTeX numbers and references
the display equations itself.

`Build.BuildDocument` is the whole of it. Import it as `from Tools.Latex.Build import BuildDocument`;
`python -m Tools.Latex build <input.tex> <output directory> <key>=<file.pie> ...` is the command line over
the same function. Both need Radical Pie and MiKTeX installed.
"""
