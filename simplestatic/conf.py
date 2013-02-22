import os
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

SIMPLESTATIC_DIR = getattr(settings, 'SIMPLESTATIC_DIR', None)
if not SIMPLESTATIC_DIR:
    raise ImproperlyConfigured('You must set SIMPLESTATIC_DIR in settings.')

SIMPLESTATIC_DEBUG = getattr(settings, 'SIMPLESTATIC_DEBUG',
    settings.DEBUG)

SIMPLESTATIC_DEBUG_PATH = getattr(settings, 'SIMPLESTATIC_DEBUG_PATH',
    'static/')

SIMPLESTATIC_COMPRESSED_DIR = getattr(settings,
    'SIMPLESTATIC_COMPRESSED_DIR', 'compressed')

AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
if not AWS_ACCESS_KEY_ID:
    raise ImproperlyConfigured('You must set AWS_ACCESS_KEY_ID in settings.')

AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
if not AWS_SECRET_ACCESS_KEY:
    raise ImproperlyConfigured(
        'You must set AWS_SECRET_ACCESS_KEY in settings.')

AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
if not AWS_STORAGE_BUCKET_NAME:
    raise ImproperlyConfigured(
        'You must set AWS_STORAGE_BUCKET_NAME in settings.')

SIMPLESTATIC_CUSTOM_DOMAIN = getattr(settings, 'SIMPLESTATIC_CUSTOM_DOMAIN',
    '%s.s3.amazonaws.com' % (AWS_STORAGE_BUCKET_NAME,))

CLOSURE_COMPILER_JAR = getattr(settings, 'CLOSURE_COMPILER_JAR', None)
if not CLOSURE_COMPILER_JAR:
    CLOSURE_COMPILER_JAR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'compiler.jar')
    )

CLOSURE_COMPILATION_LEVEL = getattr(settings, 'CLOSURE_COMPILATION_LEVEL',
    'SIMPLE_OPTIMIZATIONS')

CLOSURE_COMPILER_COMMAND = getattr(settings, 'CLOSURE_COMPILER_COMMAND', None)
if not CLOSURE_COMPILER_COMMAND:
    CLOSURE_COMPILER_COMMAND = 'java -jar %s' % (CLOSURE_COMPILER_JAR,)
