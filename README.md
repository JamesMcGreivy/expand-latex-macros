```bash
pip install expand-latex-macros
```

Exposes the function 
```python
latex_source = open("path/to/latex_source.tex").read()
expand_latex_macros(latex_source)
```
which removes all user-defined macros in latex_source.tex and substitutes back in their definitions. Helpful for pre-processing LaTeX source to train NLP models.

