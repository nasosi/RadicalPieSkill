# Radical Pie skill

A skill for an LLM harness, such as Claude Code or Codex, that writes, validates and emits [Radical Pie](https://radicalpie.com) equations in the
editor's own `.pie` format. It covers the format's OpenDDL structure and roles, the SVG comment carrier Radical Pie and InkRadix pass equations
through, and the recipes that turn a LaTeX construct into the Radical Pie structure it becomes.

Version 0.10.0. Checked against Radical Pie 1.15 on Windows.

## What you need

- An LLM harness that loads skill folders, such as Claude Code or Codex: it reads `SKILL.md` and the references it names.
- Python 3.9 or later. The validator and the SVG carrier need nothing else.
- For the four pipelines, `python -m pip install -r requirements.txt` with the same interpreter you run the scripts with (`py` and `python` are often
  different versions on Windows, and a package installed under one is missing under the other), and the programs listed under "What the pipelines
  need" below.

## Installing it

Copy this folder into the directory your harness loads skills from, under the name `radical-pie` (for Claude Code that is `.claude/skills/radical-pie`
under your home directory), and run every command below from inside it, since `scripts/` and every path after it are relative to this folder. The
harness reads `SKILL.md` from there and offers the skill on any task that mentions Radical Pie, a `.pie` file, or an equation that has to reach Word,
PowerPoint, SVG, Inkscape or LaTeX through Radical Pie.

## Validating a file

```
python scripts/Validate.py MyEquation.pie
```

Prints `OK MyEquation.pie` when the file satisfies the format, or one line per violation naming the path through the structure tree, the message, and
the specification section the rule comes from.

## Producing an output

The four pipelines `references/OutputForms.md` describes ship in this folder, under `scripts/Tools`, as a script beside `Validate.py` each; the files
you name after them are your own paths, absolute or relative to the shell:

```
python -m pip install -r requirements.txt
python scripts/Render.py svg MyEquation.pie MyEquation.svg
python scripts/Word.py embed Draft.docx Final.docx intro=Intro.pie
python scripts/PowerPoint.py embed Draft.pptx Final.pptx maxwell=Maxwell.pie
python scripts/Latex.py build Draft.tex Out/ ratio=Ratio.pie
```

`Draft.tex` is ordinary LaTeX with `\usepackage{radicalpie}` in the preamble and one `\pie{key}` per `.pie` file where each equation goes, and the
build writes `Out/Main.tex` and the finished `Out/Main-pdflatex.pdf`, whatever the input was called, printing that path.

`python scripts/Word.py check Final.docx` and `python scripts/PowerPoint.py check Final.pptx` read a finished file and start nothing. Each pipeline
ends every program it starts, on success and on failure.

## What the pipelines need

- Windows, and Radical Pie 1.15 at `C:\Program Files\RadicalPie\RadicalPie.exe`. Every pipeline drives it, and the path is fixed in
  `scripts/Tools/Render/Svg.py`: an installation anywhere else means editing that line. Without the program the validator and the SVG carrier still
  work and nothing else does.
- Word with the Radical Pie add-in, for a Word document. PowerPoint with the add-in, for a deck.
- MiKTeX with `pdflatex` on the PATH, for a LaTeX document; `lualatex` as well for `--engine lualatex`.
- The Python packages in `requirements.txt`: pywin32, python-docx, lxml and olefile.

A missing program, or a missing Python package the pipelines import, is named in the one line the command
prints before it exits 1, the module and `requirements.txt` included.

## Layout

- `SKILL.md` — what the agent reads first: the format's mental model, the roles and styles table, and a map of every reference below.
- `references/` — every file `SKILL.md`'s own map names, plus `examples/*.pie`, ready-made files to copy from.
- `scripts/` — `Validate.py`, the validator, `WrapSvg.py`, the SVG carrier in both directions, and `Render.py`, `Word.py`, `PowerPoint.py` and
  `Latex.py`, the four pipelines; `ToolsPath.py` sits beside these six and tells each which of the two layouts it is running in, not a command of its
  own. `scripts/Tools/` is the Python behind all six, vendored here so the folder runs without the repository it is built in.
- `requirements.txt` — the third-party packages the pipelines import; the validator needs none of them.

## Feedback

`references/Feedback.md` has the full instructions for sending back what the skill got wrong or what would have saved time; an agent follows them
without asking, and a human passes the result on through the repository's "Skill feedback" issue form or, with the GitHub CLI signed in, `gh issue
create`. An empty file named `radicalpieskill.off` stops the feedback line, in a project folder for that project and in your home directory
everywhere. `CHANGELOG.md` lists every version.

## Licence

MIT. See `LICENSE` in this folder. Radical Pie itself, its file format, and its documentation are the property of Radical Pie's author and are not
covered by this licence; this skill only describes how to write files the editor reads. `references/TexSymbols.md` is the one file that reproduces
that documentation, regenerated from Radical Pie's own TeX command tables, and it stands outside this licence with them.

Radical Pie: https://radicalpie.com
