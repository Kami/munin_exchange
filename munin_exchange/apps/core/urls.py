from django.conf.urls.defaults import *

urlpatterns = patterns('',
	url(r'^markdown-preview', 'core.views.markdown_preview', name = 'markdown_preview'),
)