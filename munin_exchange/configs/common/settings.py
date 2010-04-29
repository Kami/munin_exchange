import logging
import os

import django

# Base paths
DJANGO_ROOT = os.path.dirname(os.path.realpath(django.__file__))
SITE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Debugging
DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Tomaz Muraus', 'kami@k5-storitve.net'),
)

MANAGERS = ADMINS

# Bitly settings
BITLY_USERNAME = ''
BITLY_APIKEY = ''

# Twitter settings
TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
TWITTER_ACCESS_TOKEN = '';
TWITTER_ACCESS_SECRET = '';

# Celery queue
CARROT_BACKEND = "ghettoq.taproot.Redis"

BROKER_HOST = "localhost"		# Maps to redis host.
BROKER_PORT = 6379				# Maps to redis port.
BROKER_VHOST = "celery_mex"		# Maps to database name. - must be integer for redis...

CELERYD_CONCURRENCY = 10	    # Maximum of 8 concurrent workers

# messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

# Local time
TIME_ZONE = 'Europe/Ljubljana'

# Local language
LANGUAGE_CODE = 'en-us'

# Site framework
SITE_ID = 1

DATETIME_FORMAT = "'N j, Y, H:i"

# Internationalization
USE_I18N = False

# Absolute path to the directory that holds media.
MEDIA_ROOT = os.path.join(SITE_ROOT, 'assets/site_media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# Django-ajax
DAJAXICE_MEDIA_PREFIX = "dajaxice"
#DAJAXICE_XMLHTTPREQUEST_JS_IMPORT= False
#DAJAXICE_JSON2_JS_IMPORT = False

DAJAXICE_FUNCTIONS = (
	'plugins.ajax.pagination_index',
	'plugins.ajax.pagination_uploaded',
	'plugins.ajax.get_download_count',
	'plugins.ajax.rating',
)

# django-rating
RATINGS_VOTES_PER_IP = 3

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+1@s))fb255yz3h2uzougp7@(4dcpw$8_1y9uauc)4o8o1y=8'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.core.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'munin_exchange.lib.context_processors.plugins_tag_cloud',
    'munin_exchange.lib.context_processors.plugins_stats_footer',
)

MIDDLEWARE_CLASSES = (
	'johnny.middleware.LocalStoreClearMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.csrf.middleware.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'johnny.middleware.QueryCacheMiddleware',
)

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

ROOT_URLCONF = 'munin_exchange.configs.common.urls'

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates')
)

INSTALLED_APPS = (
	'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.markup',
    'django.contrib.comments',
    'django.contrib.flatpages',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.sitemaps',

    # Applications
    'core',
    'plugins',

    # Third-party
    'celery',
    'johnny',
    'django_assets',
    'django_rpx_plus',
    'dajaxice',
    'dajax',
    'taxonomy',
    'djangoratings',
    'debug_toolbar',
    'django_extensions',
    'clippy',
    'django_notifications',
)

# Valid content types for source code files
VALID_SOURCE_CODE_FILE_TYPES = ('text/plain', 'application/x-perl', 'text/x-python',
								'application/x-shellscript', 'application/x-gzip',
								'application/zip',)

# Auth backend config tuple does not appear in settings file by default. So we
# specify both the RpxBackend and the default ModelBackend:
AUTHENTICATION_BACKENDS = (
	'django_rpx_plus.backends.RpxBackend',
	'django.contrib.auth.backends.ModelBackend', #default django auth
)

# Predefined domain
MY_SITE_DOMAIN = 'localhost:8000'

# Email
# run "python -m smtpd -n -c DebuggingServer localhost:1025" to see outgoing
# messages dumped to the terminal
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

# Caching
CACHE_MIDDLEWARE_KEY_PREFIX='munin_exchange'
CACHE_MIDDLEWARE_SECONDS=90 * 60 # 90 minutes

# Django notifications
NOTIFICATIONS = {
	'sms_mobitel': {
		'USERNAME': '',
		'PASSWORD': '',
	},

	'xmpp': {
		'JID': '',
		'PASSWORD': '',
		'TYPE': 'chat',
	},
}

############################
#django_rpx_plus settings: #
############################
RPXNOW_API_KEY = ''

# The realm is the subdomain of rpxnow.com that you signed up under. It handles
# your HTTP callback. (eg. http://mysite.rpxnow.com implies that RPXNOW_REALM  is
# 'mysite'.
RPXNOW_REALM = ''

# If it is the first time a user logs into your site through RPX, we will send
# them to a page so that they can register on your site. The purpose is to
# let the user choose a username (the one that RPX returns isn't always suitable)
# and confirm their email address (RPX doesn't always return the user's email).
REGISTER_URL = '/accounts/register/'

PLUGINS_PATH = os.path.join(SITE_ROOT, 'assets/site_media/plugins')

# Logging
logging.basicConfig(
    level=logging.DEBUG,
)

# Allow for local (per-user) override
try:
	from local_settings import *
except ImportError:
	pass
