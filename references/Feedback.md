# Feedback

The route back to whoever maintains this skill, for the lessons a task turns up along the way: a reference
that was wrong, a rule the references left out, a recipe that cost more than one render to get right, a
validator message that named the fault but not the fix, or a workaround the agent had to invent because
nothing here named one.

## When to write it

Once the task is finished, not before: a reference proved wrong partway through, a rule was missing and had
to be worked out from the specification or from a render, a recipe took more than one attempt, a validator
message left the fix unclear, or the agent ended up doing something none of the references suggested.
Getting the task right the first time, from what is already written here, is not feedback.

Three checks before a line is written. A limitation `references/KnownLimitations.md` already records
is not feedback; read that file first and drop the lesson if it is there. A lesson already in the
`RadicalPieFeedback.md` of that directory is not written a second time, however differently it would
be worded. At most three lines go in for one task; where a task turns up more, keep the three that
would change the skill most.

## Where it goes

Append one line to `RadicalPieFeedback.md` in the directory the output goes to, next to the finished `.pie`
file, SVG, Word document or LaTeX build, never inside this skill's own folder. Create the file with that
name if the directory does not have one yet. One line per lesson, appended to the end, never overwritten.

## The line

Five fields, in order, separated by ` | `:

```
0.10.0 | 1.15 | what was asked | what the skill said or lacked | what worked
```

The skill version, from this folder's `README.md`. The Radical Pie version, from the same place a pipeline
run reported it, or `unknown` when nothing drove the executable. Then, in plain prose: what the caller
asked for, what the skill's references said or left unsaid that cost the extra time, and what worked once
found.

## Writing it

Write the line silently, as the last part of finishing the task, the same way the skill takes a convention
for an unstated placement rather than asking about it: no question to the user about whether to write it or
what to put in it. The equation itself is not attached; a caller who wants the `.pie` file alongside the
report attaches it themselves.

The first time a line is written into a project, and only that first time, the reply says in one
sentence that a feedback line went into `RadicalPieFeedback.md` there and that asking to turn
Radical Pie feedback off stops it. Every later line in the same project is written without a word.

## Turning it off

A file named `radicalpieskill.off` in the project folder stops the feedback line for that project,
and one in the home directory stops it everywhere. Check for both before writing; an empty file is
enough.

When the user asks to turn feedback off, create `radicalpieskill.off` in the project folder and ask
whether to turn it off everywhere as well, which is the one question this skill asks without being
invited to. Put the file in the home directory too if the answer is yes.

## Sending it on

A human closes the loop by one of two routes: paste the accumulated lines into the repository's "Skill
feedback" issue form, at https://github.com/nasosi/RadicalPieSkill/issues/new/choose, or, with the GitHub
CLI signed in, run it straight from the output directory:

```
gh issue create --repo nasosi/RadicalPieSkill --title "Skill feedback" --body-file RadicalPieFeedback.md
```
