import hashlib
import os
import subprocess

from StringIO import StringIO

from django.core.urlresolvers import reverse
from django.core.cache.backends.locmem import LocMemCache

from simplestatic import conf


CACHE = LocMemCache('simplestatic', {})
CHUNK_SIZE = 8192


def uncached_hash_for_paths(paths):
    hsh = hashlib.md5()

    for path in paths:
        full_path = os.path.join(conf.SIMPLESTATIC_DIR, path)
        if not os.path.exists(full_path):
            # TODO: Log some kind of warning here
            continue

        with open(full_path, 'r') as f:
            while 1:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                hsh.update(data)

    return hsh.hexdigest()


def cached_hash_for_paths(paths):
    cache_key = hashlib.md5('!'.join(sorted(paths))).hexdigest()
    hsh = CACHE.get(cache_key)
    if hsh is not None:
        return hsh
    hsh = uncached_hash_for_paths(paths)
    CACHE.set(cache_key, hsh, 3600)
    return hsh


hash_for_paths = (uncached_hash_for_paths if conf.SIMPLESTATIC_DEBUG else
    cached_hash_for_paths)


def debug_url(path):
    hsh = hash_for_paths([path])
    url = reverse('django.views.static.serve', kwargs={'path': path})
    return '%s?devcachebuster=%s' % (url, hsh)


def prod_url(paths, ext):
    hsh = hash_for_paths(paths)
    return '//%s.s3.amazonaws.com/%s/%s.%s' % (
        conf.AWS_STORAGE_BUCKET_NAME,
        conf.SIMPLESTATIC_COMPRESSED_DIR,
        hsh,
        ext,
    )


def css_url(paths):
    return prod_url(paths, 'css')


def js_url(paths):
    return prod_url(paths, 'js')


def compress_css(paths):
    output = StringIO()
    for path in paths:
        with open(path, 'r') as in_file:
            while 1:
                data = in_file.read(CHUNK_SIZE)
                if not data:
                    break
                output.write(data)
        output.write('\n')
    return output.getvalue()


def compress_js(paths):
    cmd = '%s %s' % (
        conf.CLOSURE_COMPILER_COMMAND,
        ' '.join(['--js %s' % (path,) for path in paths]),
    )
    output = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE
    ).communicate()[0]
    return output
