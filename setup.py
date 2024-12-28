from setuptools import setup, find_packages

VERSION = '1.0.2' 
DESCRIPTION = 'Removes all user-defined macros in a .tex file and substitutes their definitions back in.'
LONG_DESCRIPTION = 'Provides the function expand_latex_macros(latex_source). Removes all user-defined macros in latex_source -- which should be a latex.tex file read into python using open(latex_source_path).read() -- and substitutes back in their definitions. Helpful for pre-processing LaTeX source to train NLP models.'
# Setting up
setup(
        name="expand_latex_macros", 
        version=VERSION,
        author="James McGreivy",
        author_email="mcgreivy@mit.edu",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['regex'], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        keywords=['latex', 'LaTeX', 'macros', '\\def', '\\newcommand'],
        classifiers= [
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)