import os

from django import template

from simplestatic import conf
from simplestatic.compress import debug_url, css_url, js_url, url

register = template.Library()

CSS_TMPL = '<link rel="stylesheet" href="%s" type="text/css" charset="utf-8">'
JS_TMPL = '<script src="%s" type="text/javascript" charset="utf-8"></script>'


class MediaNode(template.Node):
    def __init__(self, path):
        self.path = template.Variable(path)

    def resolve(self, context):
        return self.path.resolve(context)

    def render(self, context):
        return self.TMPL % (debug_url(self.path.resolve(context)),)


class CSSNode(MediaNode):
    TMPL = CSS_TMPL


class JSNode(MediaNode):
    TMPL = JS_TMPL


class URLNode(template.Node):
    def __init__(self, path):
        self.path = template.Variable(path)

    def render(self, context):
        return url(self.path.resolve(context))


class SimpleStaticNode(template.Node):
    def __init__(self, nodes):
        self.nodes = nodes

    def render(self, context):
        if conf.SIMPLESTATIC_DEBUG:
            return self.render_debug(context)
        else:
            return self.render_prod(context)

    def render_debug(self, context):
        return '\n'.join((n.render(context) for n in self.nodes))

    def render_prod(self, context):
        css, js = self.get_css_js_paths(context)

        resp = []
        if css:
            resp.append(CSS_TMPL % (css_url(css),))
        if js:
            resp.append(JS_TMPL % (js_url(js),))

        return '\n'.join(resp)

    def get_css_js_paths(self, context):
        pre = conf.SIMPLESTATIC_DIR
        css, js = [], []
        for node in self.nodes:
            if isinstance(node, CSSNode):
                css.append(os.path.join(pre, node.resolve(context)))
            elif isinstance(node, JSNode):
                js.append(os.path.join(pre, node.resolve(context)))
        return css, js


@register.tag
def simplestatic(parser, token):
    tag_name = token.split_contents()[0]
    nodes = parser.parse('end%s' % (tag_name,))
    parser.delete_first_token()
    return SimpleStaticNode(nodes)


@register.tag
def compress_css(parser, token):
    path = token.split_contents()[1]
    return CSSNode(path)


@register.tag
def compress_js(parser, token):
    path = token.split_contents()[1]
    return JSNode(path)


@register.tag
def simplestatic_url(parser, token):
    path = token.split_contents()[1]
    return URLNode(path)
