Removes all user-defined macros -- \newcommand or \def -- in latex_source.tex and substitutes back in their raw definition. Helpful for pre-processing LaTeX source before training NLP models.

```bash
pip install expand-latex-macros
```

```python
import expand_latex_macros

latex_source = open("path/to/latex_source.tex").read()
expand_latex_macros(latex_source)
```

