# Configuration file for the Sphinx documentation builder.

import sys, os


sys.path.append(os.path.abspath('ext'))
sys.path.append('.')


from links.link import *
from links import *

sys.path.insert(0, os.path.abspath('../../'))
sys.path.insert(0, os.path.abspath('.'))

# -- Project information

project = 'CoNNECT'
copyright = '2023, Matthew Sherwood'
author = 'Matthew Sherwood'

release = '0.1'
version = '0.1.0'

# -- General configuration

extensions = [
 #   'xref', 
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx'
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output
html_static_path = ['_static']
html_context = {
    'css_files': [
        'css/custom.css',
    ],
}

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'
numfig = True
