import os

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

from plugins.sitemap import PluginsSitemap
from django.contrib.sitemaps import FlatPageSitemap

admin.autodiscover()

sitemaps = {
    'plugins': PluginsSitemap,
    'flatpages': FlatPageSitemap
}

urlpatterns = patterns('',
	(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	(r'^admin/', include(admin.site.urls)),
	(r'^grappelli/', include('grappelli.urls')),
	(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
	
	# Apps
	url(r'^$', 'core.views.index', name = 'index'),
	(r'^core/', include('core.urls')),
	(r'^plugins/', include('plugins.urls')),
	
	# Account/Auth URLs not implemented by django_rpx_plus:
    url(r'^accounts/$', 'django.views.generic.simple.redirect_to', 
                        {'url': '/accounts/profile/', 'permanent': False},
                        name = 'auth_home'),
    url(r'^accounts/profile/$', 'core.views.profile', name = 'auth_profile'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', 
                      {'template_name': 'django_rpx_plus/logged_out.html'}, 
                      name = 'auth_logout'),
	(r'^accounts/', include('django_rpx_plus.urls')),
	(r'^api/1.0/', include('api.urls_10')),
	
	# Sitemap
	(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

site_media = os.path.join(settings.MEDIA_ROOT, '')
admin_media = os.path.join(settings.MEDIA_ROOT, 'admin_media')

if settings.DEBUG:
    urlpatterns += patterns('',
    # Media
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media}),
        (r'^admin_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': admin_media}),
    )