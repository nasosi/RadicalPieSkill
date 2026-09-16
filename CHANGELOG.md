# Changelog

## 0.10.0 — 2026-09-15

- Nine facts the showcase agents had to find by probing are now written down: the eight `'rdcl'` design
  names and what each draws, which side of a bond `'prd1'` and `'prd2'` dash, the spacer a function name
  needs before a letter, the blank slot an empty `It` iterand reserves, the `'cell'` corner arithmetic
  that rules a matrix into blocks, the rails an annotation group owns, the phantom that makes two
  bracket pairs the same size, where a slanted line's `'anno'` 1 sits, and the private use character a
  file-writing tool can drop.
- The catalogue of structures is split into `references/catalogue/`, one file per family
  (`Overview.md`, `Symbols.md`, `Groups.md`, `Brackets.md`, `Fractions.md`, `Operators.md`,
  `Matrices.md`, `Arrows.md`, `Bonds.md`, `Drawings.md`, `Annotations.md`, `Design.md`), and the
  edge cases of a domain live in `ChemistryHints.md`, `AnnotationHints.md`, `LayoutHints.md` and
  `DocumentHints.md`; `references/Pitfalls.md` keeps only the general ones. No sentence was lost
  in the split.
- Eight worked examples that were the site's own files are replaced by the skill's own equations,
  validated and rendered.
- Measured corrections: the orbital phantom needs `Sp (s=0.0) {}` beside it, two `Sc` in a row do not
  stack, `mb` moves a matrix 0.83 pt, `ca` centres the bracket and not its content, `al` on a one-line
  neighbour group changes nothing, a boxed 11 by 9 pt expression comes out 20.04 pt wide, a zero-width
  space is worth the pair's own kern, and seven measurement blocks now name the factory 11 point design
  they were taken at.
- Corrections against the executable: Radical Pie keeps 21 style maps and drops `M (t='grek')`, and the
  Radical font covers the asteroid range in part rather than not at all.
- `references/KnownLimitations.md`, new: what cannot be fixed on the skill's side.
- The feedback line is written only when the skill fell short, never twice for one lesson, at most three
  to a task, never for a known limitation, and `radicalpieskill.off` turns it off per project or for
  every project.
- Guidance: the workflow renders a PDF, the form an agent can look at, and says what its commands are
  relative to; recipes for floor, ceiling, norm, `\mathrm`, colour and a thousands separator; the charge
  sign is `'unry'` in every file that names it; `references/TexSymbols.md` says that a bracket, prime,
  accent or wide mark listed as a character is written as its structure.
- Consistency: the PowerPoint pipeline is named where the editor's feature list denied it, the bond
  exception and the validator's reach are in `references/Pitfalls.md`, the anchor table's nesting note
  matches the validator, three duplicated recipe rows became one each, and no shipped path names the
  development repository.

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
