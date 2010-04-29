from django.db import models
from django.db.models import Q
from django.db.models.aggregates import Count
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from taxonomy.models import Taxonomy, TaxonomyTerm, TaxonomyMap

class PluginManager(models.Manager):
	def get_plugin_relatives(self, plugin):
		""" Returns all the plugins with the same title. """
		plugins = super(PluginManager, self).get_query_set() \
			.filter(~Q(id = plugin.id) & Q(title = plugin.title))
				
		return plugins
	
	def get_plugin_by_title_and_platforms(self, title_slug, platform_names):
		"""
		Returns a plugin for a provided plugin and platform titles.
		"""
		
		plugins = super(PluginManager, self).get_query_set().filter(title_slug = title_slug) \
					.values_list('id', flat = True)
					
		if not plugins:
			return None
		
		platform_term_ids = [platform.id for platform \
							in self.get_taxonomy_term_objects_from_platforms(platform_names)]
		
		if len(platform_term_ids) != len(platform_names):
			return None

		plugin_ids = set(TaxonomyMap.objects.filter(term__id__in = platform_term_ids) \
						.values_list('object_id', flat = True))
		
		for plugin_id in plugin_ids:
			if plugin_id in plugins:
				return super(PluginManager, self).get_query_set().get(id = plugin_id)
			
		return None

	def get_available_categories(self):
		categories = TaxonomyTerm.objects.filter(type__type__iexact = 'category') \
						.values_list('id', 'term')
		
		return categories		
	
	def get_available_platforms(self):
		platforms = TaxonomyTerm.objects.filter(type__type__iexact = 'platform') \
						.values_list('id', 'term')
						
		return platforms
	
	def get_available_tags(self):
		tags = TaxonomyMap.objects.filter(type__type__iexact = 'tag').values_list('term_id', flat = True) \
			.annotate(count = Count('id'))
		
		TaxonomyTerm.objects.filter(type__type__iexact = 'tag') \
						.values_list('id', 'term')
						
		return tags
	
	def get_taxonomy_term_objects_from_platform_ids(self, platform_ids):
		""" Returns TaxonomyTerm objects for all the platform ids in the given list.
		"""
		
		platform_taxonomy = self.get_platform_taxonomy()
		taxonomy_terms = TaxonomyTerm.objects.filter(id__in = platform_ids, type = platform_taxonomy)
		
		return taxonomy_terms
	
	def get_taxonomy_term_objects_from_platforms(self, platforms):
		"""
		Returns TaxonomyTerm objects for all the platforms in the given list.
		"""
		
		platform_taxonomy = self.get_platform_taxonomy()
		taxonomy_terms = []
		for platform in platforms:
			try:
				term = TaxonomyTerm.objects.get(term = platform, type = platform_taxonomy)
			except ObjectDoesNotExist:
				continue
			taxonomy_terms.append(term)
			
		return taxonomy_terms
	
	def get_taxonomy_term_objects_from_tags(self, tags):
		"""
		Returns TaxonomyTerm objects for all the tags in the given list.
		If the tag exists, it returns an existing object and if it does not
		it creates it.
		"""
		
		tag_taxonomy = self.get_tag_taxonomy()
		taxonomy_terms = []
		for tag in tags:
			try:
				term = TaxonomyTerm.objects.get(term = tag, type = tag_taxonomy)
			except ObjectDoesNotExist:
				term = TaxonomyTerm(term = tag, type = tag_taxonomy)
				term.save()
			taxonomy_terms.append(term)
			
		return taxonomy_terms
						
	def get_category_taxonomy(self):
		taxonomy = Taxonomy.objects.get(type__iexact = 'category')
		return taxonomy
	
	def get_platform_taxonomy(self):
		taxonomy = Taxonomy.objects.get(type__iexact = 'platform')
		return taxonomy
	
	def get_tag_taxonomy(self):
		taxonomy = Taxonomy.objects.get(type__iexact = 'tag')
		return taxonomy