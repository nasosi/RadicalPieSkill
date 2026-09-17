# Changelog

## 1.0.0 — 2026-09-16

- First stable version. Checked on a fresh Python 3.14 environment installed from `requirements.txt`,
  and in cold sessions of Claude Code with Sonnet and Opus across SVG, Word, PowerPoint and LaTeX.
- The script command lines, the feedback line's five fields and the `radicalpieskill.off` switch, and the
  folder layout, are stable from here; a change to any of them is a new major version.
- The README names Codex, and any other harness that loads skill folders, as untested.

## 0.10.0 — 2026-09-15

- The reference catalogue is reorganised into `references/catalogue/`, one file per structure family
  (symbols, groups, brackets, fractions, operators, matrices, arrows, bonds, drawings, annotations and
  design), with short hint files for chemistry, annotations, layout and document output.
- Layout details that used to cost a retry are now written down: which side of a bond a partial bond's
  dashes fall on, the spacing a function name needs before a letter, the corner arithmetic that rules a
  matrix into blocks, and the phantom that keeps two bracket pairs the same size, among others.
- The feedback route is limited to what the skill actually fell short on, at most three lines a task,
  and can be turned off per project or everywhere with an empty `radicalpieskill.off` file;
  `references/KnownLimitations.md` lists what a feedback line would only repeat.
- The worked examples that used to be the editor's own sample files are replaced by the skill's own,
  validated and rendered equations.
- Every pipeline now refuses a file the format rejects before it opens anything, and ends only the
  programs it started.

## 0.9.2 — 2026-09-14

- Feedback route: `references/Feedback.md`, the issue form, the changelog.
- The documentation pull script lives in the development repository, not in this folder.
- A prime is the `Pr` structure, not a typed character; every worked example in `references/Examples.md`
  names the file it ships beside its heading.

## 0.9.1 — 2026-09-14

- The centred dot is U+00B7, reported by a user.

## 0.9.0 — 2026-09-13

- First public version, checked against Radical Pie 1.15.
- The four pipelines, render, Word, PowerPoint and LaTeX, ship inside the folder.
