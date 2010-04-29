import os
import uuid
import urllib

from munin_exchange.lib.thumbs import ImageWithThumbsField

from django.db import models
from django.db.models import Q
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from markupfield.fields import MarkupField
from autoslug import AutoSlugField
from djangoratings.fields import RatingField
from django.contrib.sites.models import Site
from taxonomy.models import Taxonomy, TaxonomyTerm, TaxonomyMap

from settings import PLUGINS_PATH
from managers import PluginManager

from tasks import SendUpdateToTwitterTask

# Helper methods
def get_plugin_upload_path(instance, filename):
	"""
	Returns the file destination path.
	
	At this time, the instance has not yet been saved and the version_number
	has not been populated so we assign the file a random name (we will
	generate a "nicer" name on a download request)
	"""
	file_name = uuid.uuid1().get_hex()
	path = os.path.join('plugins', file_name)
		
	return path

# Models
class Plugin(models.Model):
	title = models.CharField(max_length = 120)
	title_slug = AutoSlugField(populate_from = 'title', unique = True)
	description = MarkupField(default_markup_type = 'markdown')
	screenshot = ImageWithThumbsField(upload_to = 'images/plugins', blank = True, sizes = ((430, 245),))
	language = models.CharField(max_length = 30)
	approved = models.BooleanField(default = False)
	downloads = models.IntegerField(default = 0)
	rating = RatingField(range = 5, allow_anonymous = True)
	
	objects = models.Manager()
	taxonomy = PluginManager()
	
	def __unicode__(self):
		return self.title
	
	@models.permalink
	def get_absolute_url(self):
		return ('plugins_details', (), {'title_slug': self.title_slug})
	
	def get_full_url(self):
		domain = Site.objects.get_current().domain
		url = 'http://%s%s' % (domain, reverse('plugins_details', args = (self.title_slug,)))
	
		return url
	
	def get_platforms(self):
		platforms = TaxonomyMap.objects.filter(object_id = self.pk, \
							content_type__name = 'plugin', \
							type = Plugin.taxonomy.get_platform_taxonomy()) \
							.values_list('term__term', flat = True)
						
		return platforms

	def get_platform_terms(self):
		platform_term_ids = TaxonomyMap.objects.filter(object_id = self.pk, \
							content_type__name = 'plugin', \
							type = Plugin.taxonomy.get_platform_taxonomy()) \
							.values_list('term__id', flat = True)
		platform_terms = TaxonomyTerm.objects.filter(id__in = platform_term_ids)
						
		return platform_terms
	
	def get_category(self):
		try:
			category = TaxonomyMap.objects.get(object_id = self.pk, \
								content_type__name = 'plugin', \
								type = Plugin.taxonomy.get_category_taxonomy())
		except MultipleObjectsReturned:
			return None
		except ObjectDoesNotExist:
			return None
		
		return category.term.term
	
	def get_category_term(self):
		try:
			category = TaxonomyMap.objects.get(object_id = self.pk, \
								content_type__name = 'plugin', \
								type = Plugin.taxonomy.get_category_taxonomy())
		except MultipleObjectsReturned:
			return None
		except ObjectDoesNotExist:
			return None
		
		return category.term
	
	def get_tags(self):
		tags = TaxonomyMap.objects.filter(object_id = self.pk, \
										content_type__name = 'plugin', \
										type = Plugin.taxonomy.get_tag_taxonomy()) \
										.values_list('term__term', flat = True)
		
		return tags
	
	def get_latest_version(self):
		""" Returns a latest version for this plugin. """
		try:
			plugin_version = self.pluginversion_set.order_by('-version_number')[0]
		except IndexError:
			# Should not happen, because each plugin must have at least one version
			return None
						
		return plugin_version
	
	def save(self, *args, **kwargs):
		"""
		If a new plugin is approved (approved = True), and a plugin version exists, add
		a task which will post status update to Twitter to the queue.
		"""
		
		if self.id:
			
			plugin_version = self.get_latest_version()
			if self.approved and not plugin_version.sent_to_twitter:
				domain = Site.objects.get_current().domain
				url = 'http://%s%s' % (domain, reverse('plugins_details', args = (self.title_slug,)))
				
				if plugin_version.version_number > 1:
					# Approving a plugin with an existing version and the status update
					# was not already posted to Twitter
					version = plugin_version.version_number
					try:
						SendUpdateToTwitterTask.delay(self.title, version, self.get_platforms(), \
													self.get_category(), self.get_tags(), url)
					except Exception:
						pass
				else:
					# Approving a plugin with a single version (aka new plugin)
					try:
						SendUpdateToTwitterTask.delay(self.title, None, self.get_platforms(), \
													 self.get_category(), self.get_tags(), url)
					except Exception:
						pass
					
				plugin_version.sent_to_twitter = True
				plugin_version.save()
			
		super(Plugin, self).save(*args, **kwargs)

class PluginVersion(models.Model):
	version_number = models.IntegerField() # aka version number
	plugin = models.ForeignKey(Plugin)
	author = models.CharField(max_length = 100)
	submitted_by = models.ForeignKey(User)
	date_submitted = models.DateTimeField(auto_now_add = True)
	notes = models.CharField(max_length = 250, blank = True)
	file = models.FileField(max_length = 250, upload_to = get_plugin_upload_path)
	sent_to_twitter = models.BooleanField(default = False)
	
	class Meta:
		ordering = ('-version_number',)
		
	@models.permalink
	def get_absolute_url(self):
		return ('plugins_version', (), {'title_slug': self.plugin.title_slug, \
										'version_number': self.version_number})
	
	@property
	def get_download_url(self):
		return reverse('plugins_download', args = (self.plugin.title_slug, \
												self.version_number,))
	
	def save(self, *args, **kwargs):
		"""
		Autoincrement the version id field.
		If a new plugin is saved (approved = True and send_to_twitter = True), add
		a task which will post status update to Twitter to the queue.
		"""
		
		send_to_twitter = kwargs.get('send_to_twitter', None)
		domain = Site.objects.get_current().domain
		url = 'http://%s%s' % (domain, reverse('plugins_details', args = (self.plugin.title_slug,)))
		
		if not self.id:
			try:
				top = PluginVersion.objects.filter(plugin = self.plugin) \
							.order_by('-version_number')[0]
				top_version = top.version_number
			except IndexError:
				# First version
				top_version = 0
					
			self.version_number = top_version + 1
			
		if self.plugin.approved and not self.sent_to_twitter:
			if self.version_number == 1:
				# Add task for a Twitter status update to the queue
				SendUpdateToTwitterTask.delay(self.plugin.title, None, \
											self.plugin.get_platforms(), self.plugin.get_category(), \
											self.plugin.get_tags(), url)
			else:
				SendUpdateToTwitterTask.delay(self.plugin.title, top_version + 1, \
											self.plugin.get_platforms(), self.plugin.get_category(), \
											self.plugin.get_tags(), url)
			self.sent_to_twitter = True
			
		if send_to_twitter is not None:
			del kwargs['send_to_twitter']
			
		super(PluginVersion, self).save(*args, **kwargs)