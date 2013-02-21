import mimetypes
import os

from threading import local, RLock

from multiprocessing.pool import ThreadPool

from boto.s3.connection import S3Connection

from django.template import Template, Context
from django.core.management.base import NoArgsCommand
from django.conf import settings

from simplestatic.compress import compress_css, compress_js, hash_for_paths
from simplestatic import conf
from simplestatic.templatetags.simplestatic_tags import SimpleStaticNode


def s3_bucket(local=local()):
    bucket = getattr(local, 'bucket', None)
    if bucket is not None:
        return bucket
    conn = S3Connection(
        conf.AWS_ACCESS_KEY_ID,
        conf.AWS_SECRET_ACCESS_KEY
    )
    local.bucket = conn.get_bucket(conf.AWS_STORAGE_BUCKET_NAME)
    return local.bucket


def locked_print(s, lock=RLock()):
    with lock:
        print s


def set_content_type(key):
    _, ext = os.path.splitext(key.name)
    if ext:
        content_type = mimetypes.types_map.get(ext)
        if content_type:
            key.content_type = content_type


class Command(NoArgsCommand):
    help = ('Syncs the contents of your SIMPLESTATIC_DIR to S3, compressing '
        + 'any assets as needed')

    def compress_and_upload(self, template, paths, compress, ext):
        bucket = s3_bucket()
        name = '%s/%s.%s' % (
            conf.SIMPLESTATIC_COMPRESSED_DIR,
            hash_for_paths(paths),
            ext,
        )
        key = bucket.get_key(name)
        if key is None:
            locked_print('Compressing %s from %s' % (ext, template))
            compressed = compress(paths)
            locked_print('Uploading %s from %s' % (name, template))
            key = bucket.new_key(name)
            set_content_type(key)
            key.set_contents_from_string(compressed, policy='public-read',
                replace=True)

    def sync_file(self, base, filename):
        name = filename[len(base) + 1:]
        bucket = s3_bucket()
        key = bucket.get_key(name)
        if key:
            etag = key.etag.lstrip('"').rstrip('"')
            with open(filename) as f:
                md5 = key.compute_md5(f)[0]
            if etag != md5:
                locked_print('Syncing %s' % (name,))
                set_content_type(key)
                key.set_contents_from_filename(filename, policy='public-read',
                    md5=md5, replace=True)
        else:
            locked_print('Syncing %s' % (name,))
            key = bucket.new_key(name)
            set_content_type(key)
            key.set_contents_from_filename(filename, policy='public-read',
                replace=True)

    def handle_template(self, base, filename):
        with open(filename, 'r') as f:
            tmpl = Template(f.read())
        template = filename[len(base) + 1:]
        nodes = tmpl.nodelist.get_nodes_by_type(SimpleStaticNode)
        for node in nodes:
            css, js = node.get_css_js_paths(Context())
            if css:
                self.compress_and_upload(template, css, compress_css, 'css')
            if js:
                self.compress_and_upload(template, js, compress_js, 'js')

    def walk_tree(self, paths, func):
        while len(paths):
            popped = paths.pop()
            try:
                base, current_path = popped
            except (ValueError, TypeError):
                base = current_path = popped

            for root, dirs, files in os.walk(current_path):
                for d in dirs:
                    normdir = os.path.join(root, d)
                    if os.path.islink(normdir):
                        paths.append((base, normdir))
                for fn in files:
                    if fn.startswith('.'):
                        continue
                    func(base, os.path.join(root, fn))

    def handle_noargs(self, **options):
        mimetypes.init()

        locked_print('===> Syncing static directory')
        pool = ThreadPool(20)

        # Sync every file in the static media dir with S3
        def pooled_sync_file(base, filename):
            pool.apply_async(self.sync_file, args=[base, filename])

        self.walk_tree([conf.SIMPLESTATIC_DIR], pooled_sync_file)
        pool.close()
        pool.join()
        locked_print('===> Static directory syncing complete')

        locked_print('===> Compressing and uploading CSS and JS')
        pool = ThreadPool(20)

        # Iterate over every template, looking for SimpleStaticNode
        def pooled_handle_template(base, filename):
            pool.apply_async(self.handle_template, args=[base, filename])

        self.walk_tree(list(settings.TEMPLATE_DIRS), pooled_handle_template)
        pool.close()
        pool.join()
        locked_print('===> Finished compressing and uploading CSS and JS')
