```bash
pip install expand-latex-macros
```

Exposes the function 
```python
expand_latex_macros(latex_source_path="/path/to/source.tex")
```
which removes all user-defined macros in source.tex and substitutes back in their definitions. Helpful for pre-processing LaTeX source to train NLP models.

