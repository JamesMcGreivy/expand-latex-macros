Removes all user-defined macros -- \newcommand or \def -- in latex_source.tex and substitutes back in their raw definition. Helpful for pre-processing LaTeX source before training NLP models.

```bash
pip install expand-latex-macros
```

```python
import expand_latex_macros

# Load LaTeX source:
latex_source = open("path/to/latex_source.tex").read() # .tex source file in which macros need expanding

# Optional Argument 1:
extra_macro_source_files = [...] # .tex files containing additional \def and \newcommand macro definitions which should be used during macro expansion
extra_macro_sources = [open(file).read() for file in extra_macro_source_files]

# Optional Argument 2:
commands_dont_expand = ["\\mubar", "\\Bmumu"] # A list of possible macros which should NOT be expanded if they are encountered in the .tex source

# Returns a string of raw LaTeX with all macros expanded
expand_latex_macros.expand_latex_macros(latex_source, extra_macro_sources=extra_macro_sources, commands_dont_expand=commands_dont_expand)
```

