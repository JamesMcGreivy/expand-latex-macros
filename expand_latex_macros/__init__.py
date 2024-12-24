from .source import expand_latex_macros

def __call__(latex_source, *args):
    return expand_latex_macros(latex_source, args)