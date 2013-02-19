django-simplestatic
===================

Django SimpleStatic is an opinionated Django app which makes it very simple to
deal with static media, with extremely minimal configuration, as long as:

* You store your static media in one directory, rather than alongside each app.
* You want your files served from S3, rather from your own servers.
* You want to use Google Closure Compiler to compress your JavaScript.
* You want to compress your javascript ahead of time, rather than during the
  request.
* You don't use any of those fancy CSS precompilers like LESS or SCSS. (This
  may change someday as my personal preferences change.)

If any of the above hold true, then this library probably won't work for you.
That said, if all of the above do hold true for you, then this app will likely
be the simplest and best way to handle your static media.


Installation
------------

1. pip install django-simplestatic

2. In your settings file, set the following values:

    SIMPLESTATIC_DIR = '/path/to/your/static/media/directory'

    AWS_ACCESS_KEY_ID = 'YOUR_ACCESS_KEY_HERE'

    AWS_SECRET_ACCESS_KEY = 'YOUR_SECRET_KEY_HERE'

    AWS_STORAGE_BUCKET_NAME = 'YOUR_STATIC_BUCKET_HERE'

3. In your urls.py, import the simplestatic_debug_urls function and execute it
   to the end of your urlpatterns:

.. code-block:: python

    from simplestatic.urls import simplestatic_debug_urls

    urlpatterns = patterns('',
        # ... all of your url patterns right here
    ) + simplestatic_debug_urls()

4. In your template (or templates) import and use the simplestatic template
   tags, which might look something like this:

.. code-block:: html+django

    {% load simplestatic_tags %}

    <head>
      <title>I love django-simplestatic!</title>

      {% simplestatic %}
        {% compress_css "css/bootstrap.css" %}
        {% compress_css "css/screen.css" %}
        {% compress_js "js/jquery-1.9.1.js" %}
        {% compress_js "js/global.js" %}
      {% endsimplestatic %}
    </head>

5. Before you push your code, run the static_sync management command to
   compress any CSS and JS and upload the whole directory to S3:

    python manage.py static_sync


Advanced Configuration
----------------------

Even though in the vast majority of cases, you'll only need to do what was
mentioned above, django-simplestatic offers a number of settings that you might
want to tweak.  Provided here is a reference of every setting


Required Settings
~~~~~~~~~~~~~~~~~

SIMPLESTATIC_DIR: REQUIRED
    The directory where you store all of your static media.

AWS_ACCESS_KEY_ID: REQUIRED
    Your Amazon Web Services access key.

AWS_SECRET_ACCESS_KEY: REQUIRED
    Your Amazon Web Services secret access key.

AWS_STORAGE_BUCKET_NAME: REQUIRED
    The S3 bucket in which to store and serve all of your static media.


Optional Settings
~~~~~~~~~~~~~~~~~

SIMPLESTATIC_DEBUG: (Defaults to DEBUG)
    A boolean determining whether to use the minimized, compressed versions of
    the files uploaded to S3.  If set to True, then the full development
    versions of the files will be served instead.  You shouldn't have to touch
    this, as by default it's set to the same value as your Django DEBUG value.

SIMPLESTATIC_DEBUG_PATH: (Defaults to 'static/')
    The URL path from which to serve static media during development. 

SIMPLESTATIC_COMPRESSED_DIR: (Defaults to 'compressed')
    The URL path in S3 to place the compressed and minified versions of the CSS
    and JS.

    For example, in the default case where this is set to 'compressed', your
    css and js might be located in a location like one of the following:

        http://example.s3.amazonaws.com/compressed/6bf0c67b74b26425832a17bbf27b9cb9.css
        http://example.s3.amazonaws.com/compressed/97a548fc6b62d5bb9f50e6a95b25d8db.js

CLOSURE_COMPILATION_LEVEL: (Defaults to 'SIMPLE_OPTIMIZATIONS')
    The Google Closure Compiler compilation level option.  See the following
    page for more information:

        https://developers.google.com/closure/compiler/docs/compilation_levels

CLOSURE_COMPILER_COMMAND: (Defaults to 'java -jar /path/to/supplied/closure.jar')
    The command required to run Google Closure Compiler.