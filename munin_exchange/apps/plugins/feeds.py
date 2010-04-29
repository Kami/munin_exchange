from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from models import Plugin, PluginVersion
from taxonomy.models import TaxonomyMap

class LatestPluginsFeed(Feed):
	title = 'Latest plugins'
	link = '/plugins/'
	description = 'Latest Munin plugins'
	
	def items(self):
		return PluginVersion.objects.filter(plugin__approved = True).order_by('-date_submitted')[:10]
	
	def item_title(self, item):
		return '%s v%s' % (item.plugin.title, item.version_number)
	
	def item_description(self, item):
		return item.plugin.description
	
	def item_author_name(self, item):
		return item.submitted_by.username
	
	def item_pubdate(self, item):
		return item.date_submitted
	
	def item_categories(self, item):
		return item.plugin.get_category()

class LatestPluginVersionsFeed(Feed):
	def get_object(self, request, title_slug = None, platform = None):
		return get_object_or_404(Plugin, title_slug = title_slug, approved = True)
	
	def title(self, obj):
		return '%s plugin versions' % (obj.title)
	
	def link(self, obj):
		return obj.get_absolute_url()
	
	def description(self, obj):
		return 'Latest versions for plugin %s' % (obj.title)
	
	def items(self, obj):
		return PluginVersion.objects.filter(plugin = obj).order_by('-date_submitted')[:10]
	
	def item_title(self, item):
		return '%s v%s' % (item.plugin.title, item.version_number)
	
	def item_link(self, item):
		return item.get_absolute_url()
	
	def item_description(self, item):
		return item.plugin.description
	
	def item_author_name(self, item):
		return item.submitted_by.username
	
	def item_pubdate(self, item):
		return item.date_submitted
	
	def item_categories(self, item):
		return item.plugin.get_category()