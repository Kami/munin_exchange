import os
import sys

# Put the Django project on system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../munin_exchange")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../configs/common")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps")))

os.environ['HOME'] = '/foo/domains/muninexchange.org/'
os.environ["DJANGO_SETTINGS_MODULE"] = "munin_exchange.configs.production.settings"
os.environ['JAVA_HOME'] = '/usr/local/'

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
