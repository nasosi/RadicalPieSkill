# Radical Pie skill

A skill for an LLM harness, such as Claude Code or Codex, that writes, validates and emits [Radical Pie](https://radicalpie.com) equations
in the editor's own `.pie` format. It covers the format's OpenDDL structure and roles, the SVG comment
carrier Radical Pie and InkRadix pass equations through, and the recipes that turn a LaTeX construct
into the Radical Pie structure it becomes.

Version 0.9.0. Checked against Radical Pie 1.15 on Windows.

## What you need

- An LLM harness that loads skill folders, such as Claude Code or Codex: it reads `SKILL.md` and the references it names.
- Python 3.9 or later. The validator and the SVG carrier need nothing else.
- For the four pipelines, `pip install -r requirements.txt` and the programs listed under "What the
  pipelines need" below.

## Installing it

Copy this folder into the directory your harness loads skills from, under the name `radical-pie`
(for Claude Code that is `.claude/skills/radical-pie` under your home directory). The harness reads `SKILL.md`
from there and offers the skill on any task that mentions
Radical Pie, a `.pie` file, or an equation that has to reach Word, PowerPoint, SVG, Inkscape or LaTeX
through Radical Pie.

## Validating a file

```
python scripts/Validate.py MyEquation.pie
```

Prints `OK MyEquation.pie` when the file satisfies the format, or one line per violation naming the
path through the structure tree, the message, and the specification section the rule comes from.

## Producing an output

The four pipelines `references/OutputForms.md` describes ship in this folder, under `scripts/Tools`, and
each has a script beside `Validate.py`. Run them from this folder:

```
pip install -r requirements.txt
python scripts/Render.py svg MyEquation.pie MyEquation.svg
python scripts/Word.py embed Draft.docx Final.docx intro=Intro.pie
python scripts/PowerPoint.py embed Draft.pptx Final.pptx maxwell=Maxwell.pie
python scripts/Latex.py build Draft.tex Out/ ratio=Ratio.pie
```

`python scripts/Word.py check Final.docx` and `python scripts/PowerPoint.py check Final.pptx` read a
finished file and start nothing. Each pipeline ends every program it starts, on success and on failure.

## What the pipelines need

- Windows, and Radical Pie 1.15 at `C:\Program Files\RadicalPie\RadicalPie.exe`. Every pipeline drives it.
- Word with the Radical Pie add-in, for a Word document. PowerPoint with the add-in, for a deck.
- MiKTeX with `pdflatex` on the PATH, for a LaTeX document; `lualatex` as well for `--engine lualatex`.
- The Python packages in `requirements.txt`: pywin32, python-docx, lxml and olefile.

A missing program is named in the one line the command prints before it exits 1.

## Layout

- `SKILL.md` — what the agent reads first: the format's mental model, the roles and styles table, and a
  map of every reference below.
- `references/` — the structure catalogue, the LaTeX recipes, chemistry, worked examples, the anchor
  atlas for drawings, the TeX symbol table, the output forms, the pitfalls, and the editor's feature
  list, plus `examples/*.pie`, ready-made files to copy from.
- `scripts/` — `Validate.py`, the validator, `WrapSvg.py`, the SVG carrier in both directions, and
  `Render.py`, `Word.py`, `PowerPoint.py` and `Latex.py`, the four pipelines. `scripts/Tools/` is the
  Python behind all six, vendored here so the folder runs without the repository it is built in.
- `requirements.txt` — the third-party packages the pipelines import; the validator needs none of them.

## Licence

MIT. See `LICENSE` in this folder. Radical Pie itself, its file format, and its documentation are the
property of Radical Pie's author and are not covered by this licence; this skill only describes how to
write files the editor reads.

Radical Pie: https://radicalpie.com
