import jsonpointer
from pkg_resources import (Requirement,
                           resource_filename,
                           resource_stream)
from lxml import (etree,
                  cssselect)
import logging

class SVGTemplate (object):
    log = logging.getLogger(__name__)

    def __init__(self, template_file, namespaces=None):
        self.template_file = template_file
        self.load_template()
        self.namespaces = {}

        if namespaces is not None:
            self.namespaces.update(namespaces)

    def register_ns(self, prefix, ns):
        self.namespaces[prefix] = ns

    def load_template(self):
        logging.debug('parsing svg template')
        svg_template = resource_stream(__name__,
                                       self.template_file)
        self.template = etree.parse(svg_template)
        svg_template.close()

    def render(self, data, spec, constants):
        '''Parameters:
        
        - data is an arbitrary dictionary
        - spec is a mapping of css selectors to
          jsonpointer selectors
        - constants is a mapping of css selectors to
          constant values
        '''

        self.update_constants(constants)
        self.update_data(data, spec)

        return etree.tostring(self.template)

    def find_element(self, selector):
        '''Locate an element in the template with a CSS selector.  Returns
        the element, or None.'''

        sel = cssselect.CSSSelector(selector,
                                    namespaces=self.namespaces)
        ele = sel(self.template)
        if len(ele) == 0:
            self.log.warn('selector %s failed to locate an element',
                          selector)
            return
        if len(ele) > 1:
            self.log.warn('selector %s resulted in multiple matches',
                           selector)
            return

        return ele[0]

    def update_data(self, data, spec):
        for jp, spec in spec.items():
            val = jsonpointer.resolve_pointer(data, jp)
            val = spec['format'](val)

            ele = self.find_element(spec['selector'])
            if ele is None:
                continue

            if 'attr' in spec:
                ele.set(spec['attr'], val)
            else:
                ele.text = val

    def update_constants(self, constants):
        for selector,spec in constants.items():
            ele = self.find_element(selector)
            if ele is None:
                continue

            if 'attr' in spec:
                ele.set(spec['attr'], spec['value'])
            else:
                ele.text = spec['value']
