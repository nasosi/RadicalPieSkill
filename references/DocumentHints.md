# Document hints

A symbol the surrounding prose mentions is an equation as well. A chapter that sets its display
equations through Radical Pie and writes the letters of its sentences as `\textit{j}`, or as a Word
italic, puts two different fonts on one page. Write the symbol as a one-symbol `.pie` and place it with
an inline `\pie{key}` or `{{pie:key}}`; `references/OutputForms.md` has the sizes measured beside body
text.

Slide prose around an equation is written as prose: put `{{pie:key}}` in the sentence where the equation
belongs, with the spaces you would leave around a word, and let the pipeline open the paragraph. Keep the
sentence in one paragraph and give the shape a text area wider than the equation; an equation with no room
left on its own line moves to the next line, and only one wider than the whole text area is refused. One
equation to a line reads best, and a line that would be centred needs to be left-aligned first. The
comma or full stop after such an equation is written inside the equation, as its last symbol in the `'pnct'`
role, with a space and the next word after the placeholder; `references/OutputForms.md` has the rule and what
the pipeline does with a mark left in the text.
