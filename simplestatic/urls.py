from django.conf.urls import patterns, url

from simplestatic import conf


def simplestatic_debug_urls():
    if not conf.SIMPLESTATIC_DEBUG:
        return patterns('')

    return patterns('', url(
        r'^%s(?P<path>.*)$' % conf.SIMPLESTATIC_DEBUG_PATH,
        'django.views.static.serve',
        {'show_indexes': True, 'document_root': conf.SIMPLESTATIC_DIR},
    ))
