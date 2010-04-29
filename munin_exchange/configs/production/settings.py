from munin_exchange.configs.common.settings import *

# Debugging
DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': 'localhost',
        'PORT': '3306',
    },
}

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# Predefined domain
MY_SITE_DOMAIN = 'exchange.munin-monitoring.org'

# Email
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25

# Caching
CACHE_BACKEND = 'redis_cache.cache://127.0.0.1:6379/?timeout=2'
JOHNNY_MIDDLEWARE_KEY_PREFIX = 'jc_mex'
JOHNNY_TABLE_BLACKLIST = ('plugins_pluginversion', )

# django-assets
ASSETS_AUTO_CREATE = True
ASSETS_DEBUG = False
ASSETS_EXPIRE = 'querystring'
YUI_COMPRESSOR_PATH = '/usr/local/bin/yuicompressor-2.4.2/build/yuicompressor-2.4.2.jar'

# logging
import logging.config
LOG_FILENAME = os.path.join(os.path.dirname(__file__), 'logging.conf')
logging.config.fileConfig(LOG_FILENAME)
