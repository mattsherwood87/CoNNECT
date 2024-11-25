# Configuration file for the Sphinx documentation builder.

import sys, os
# import sphinx_adc_theme
import sphinx_rtd_theme


sys.path.append(os.path.abspath('ext'))
sys.path.append('.')
#sys.path.insert(0,os.abspath('support_tools'))


from links.link import *
from links import *

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../../'))
sys.path.insert(0, os.path.abspath('../../support_tools'))


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
    'sphinx.ext.napoleon',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.graphviz',
    'sphinxarg.ext',
    'sphinxcontrib.autoprogram'
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

exclude_patterns = ['_build','Thumbs.db','.DS_Store']



# -- Options for HTML output
# html_static_path = ['_static']
# html_context = {
#     'css_files': [
#         'css/custom.css',
#     ],
# }

# html_theme = 'sphinx_adc_theme'
# html_theme_path = [sphinx_adc_theme.get_html_theme_path()]
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_sidebars = {
    '**': ['globaltoc.html', 'sourcelink.html', 'searchbox.html'],
}
html_static_path = ['_static']
html_css_files = [
    'custom.css',
]

# -- Options for EPUB output
epub_show_urls = 'footnote'
numfig = True
