import os

from django.conf import settings
from django.conf.urls.defaults import *
from piston.resource import Resource

from handlers import PluginsHandler, PluginHandler, \
	PluginVersionsHandler, PluginRelativesHandler

plugins_handler = Resource(PluginsHandler)
plugin_handler = Resource(PluginHandler)
plugin_versions_handler = Resource(PluginVersionsHandler)
plugin_relatives_handler = Resource(PluginRelativesHandler)

urlpatterns = patterns('',
	url(r'^plugins', plugins_handler),
	url(r'^plugin/(?P<title_slug>[a-zA-Z0-9_.-]+)/version/(?P<version_number>\d+)', plugin_handler),
	url(r'^plugin/(?P<title_slug>[a-zA-Z0-9_.-]+)/details', plugin_handler),
	url(r'^plugin/(?P<title_slug>[a-zA-Z0-9_.-]+)/versions', plugin_versions_handler),
	url(r'^plugin/(?P<title_slug>[a-zA-Z0-9_.-]+)/relatives', plugin_relatives_handler),
)
