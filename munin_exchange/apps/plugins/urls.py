from django.conf.urls.defaults import *

from feeds import LatestPluginsFeed, LatestPluginVersionsFeed

urlpatterns = patterns('',
	url(r'^$', 'plugins.views.index', name = 'plugins_index'),
	url(r'^uploaded', 'plugins.views.uploaded_plugins', name = 'plugins_uploaded_plugins'),
	url(r'^(?P<title_slug>[a-zA-Z0-9_.-]+)/feed', LatestPluginVersionsFeed(), name = 'plugins_versions_feed'),
	url(r'^(?P<title_slug>[a-zA-Z0-9_.-]+)/diff/(?P<version_number_1>\d)/(?P<version_number_2>\d)', 'plugins.views.diff', name = 'plugins_versions_diff'),
	url(r'^(?P<title_slug>[a-zA-Z0-9_.-]+)/version/(?P<version_number>\d)/download', 'plugins.views.download', name = 'plugins_download'),
	url(r'^(?P<title_slug>[a-zA-Z0-9_.-]+)/version/(?P<version_number>\d)/raw', 'plugins.views.raw', name = 'plugins_raw'),
	url(r'^(?P<title_slug>[a-zA-Z0-9_.-]+)/version/(?P<version_number>\d)/notes', 'plugins.views.version_notes', name = 'plugins_version_notes'),
	url(r'^(?P<title_slug>[a-zA-Z0-9_.-]+)/version/(?P<version_number>\d)', 'plugins.views.version', name = 'plugins_version'),
	url(r'^(?P<title_slug>[a-zA-Z0-9_.-]+)/versions', 'plugins.views.versions', name = 'plugins_versions'),
	url(r'^(?P<title_slug>[a-zA-Z0-9_.-]+)/details', 'plugins.views.details', name = 'plugins_details'),
    url(r'^(?P<title_slug>[a-zA-Z0-9_.-]+)/relatives', 'plugins.views.relatives', name = 'plugins_relatives'),
    url(r'^(?P<title_slug>[a-zA-Z0-9_.-]+)/submit', 'plugins.views.submit_version', name = 'plugins_submit_version'),
    url(r'^(?P<title_slug>[a-zA-Z0-9_.-]+)/edit', 'plugins.views.edit_plugin', name = 'plugins_edit_plugin'),
    
    # Comments
    url(r'^comments/post/$', 'plugins.views.comment_post_wrapper', name = 'plugins_comments_post'),
    url(r'^comments/posted/$', 'plugins.views.comment_posted', name = 'plugins_comments_posted'),
    (r'^comments/', include('django.contrib.comments.urls')),
    
    url(r'^feed/', LatestPluginsFeed(), name = 'plugins_feed'),
    url(r'^submit', 'plugins.views.submit_plugin', name = 'plugins_submit_plugin'),
    url(r'^search_lookup', 'plugins.views.search_lookup', name = 'plugins_search_lookup'),
    url(r'^search', 'plugins.views.search', name = 'plugins_search'),
    url(r'^top', 'plugins.views.top', name = 'plugins_top'),
     url(r'^statistics', 'plugins.views.statistics', name = 'plugins_statistics'),
    
    url(r'^(?P<title_slug>[a-zA-Z0-9_.-]+)/?$', 'django.views.generic.simple.redirect_to', {'url': '/plugins/%(title_slug)s/details', 'permanent': True}),
)
