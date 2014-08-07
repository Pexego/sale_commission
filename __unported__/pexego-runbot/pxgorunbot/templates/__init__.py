from mako.lookup import TemplateLookup
import os

here = os.path.normpath(os.path.dirname(__file__))

lookup = TemplateLookup(directories=[here], output_encoding='utf-8', encoding_errors='replace')

def render_template(template_name, **kwargs):
    t = lookup.get_template(template_name)
    return t.render(**kwargs)

