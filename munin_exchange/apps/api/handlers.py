from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from piston.handler import BaseHandler, AnonymousBaseHandler

from plugins.models import Plugin, PluginVersion
from taxonomy.models import TaxonomyMap, TaxonomyTerm

class PluginsBaseHandler(AnonymousBaseHandler):
	allowed_methods = ('GET',)
	
	fields = {
					'title_slug': None,
					'title': None,
					'description': None,
					'get_category()': 'category',
					'get_platforms()': 'platforms',
					'get_tags()': 'tags',
					'language': None,
					'get_latest_version().version_number': 'latest_version_number',
					'rating_score': None,
					'downloads': None,
					'get_latest_version().get_download_url': 'download_url',
				}
	
	fields_version = {
						'version_number': None,
						'author': None,
						'submitted_by.username': 'submitted_by',
						'date_submitted': None,
						'notes': None,
						'get_download_url': 'download_url',
					}
	
	def _build_queryset(self, **kwargs):
		"""
		Builds queryset while using the supplied filters.
		"""
		fields = kwargs.get('fields', None)
		filters = kwargs.get('filters', None)
		limit = kwargs.get('limit', None)

		if filters:
			plugin_ids_list = []
			for filter_name, filter_values in filters.iteritems():
				
				filter_values = filter_values.split(',')
				
				# Taxonomy based filter
				if filter_name in ['category', 'platform', 'tag']:
					ids = TaxonomyMap.objects.filter(type__type__iexact = filter_name, \
											term__term__in = filter_values)\
											.values_list('object_id', flat = True)
				else:
					query_filter = {'%s__%s' % (filter_name, 'istartswith'): filter_values[0]}
					ids = Plugin.objects.filter(**query_filter).values_list('id', flat = True)
				
				plugin_ids_list.append(set(ids))
			
			# Only those values which are located in all the result sets (AND filter)
			plugin_ids = set.intersection(*plugin_ids_list)
			queryset = Plugin.objects.filter(id__in = plugin_ids, approved = True)[:limit]
		else:
			queryset = Plugin.objects.filter(approved = True)[:limit]

		queryset = self._format_queryset(queryset, fields)
		return queryset
	
	def _format_queryset(self, queryset, fields):
		"""
		Formats the supplied queryset using the fields dictionary.
		"""

		if not type(queryset) == QuerySet:
			# Single object instance
			queryset = [queryset]
			
		queryset_formatted = []
		for row in queryset:
			
			query_row = {}
			for key, value in fields.iteritems():
				field_key = key if not value else value
				
				callable = key.find('()')
				attribute_pos = key.find('.')
				
				if callable == -1:
					if attribute_pos == -1:
						field_value = getattr(row, key)
					else:
						attribute1 = key[:attribute_pos]
						attribute2 = key[attribute_pos + 1:]
						field_value = getattr(getattr(row, attribute1), attribute2)
				else:
					# Normal callable
					if attribute_pos == -1:
						# Normal callable
						field_value = getattr(row, key[:-2])()
					else:
						# Callable + attribute
						method = key[:attribute_pos - 2]
						attribute = key[attribute_pos + 1:]
						field_value = getattr(getattr(row, method)(), attribute)
						
				query_row[field_key] = field_value
			queryset_formatted.append(query_row)
		
		if not type(queryset) == QuerySet:
			queryset_formatted = queryset_formatted[0]
			
		return queryset_formatted
	
	def _get_response(self, data = None, single = False, status = ('success', None)):
		"""
		Returns a response dictionary which is sent to the client.
		"""
		response = {
					'data': data,
					'meta': self._get_meta(data, single, status[0], status[1])
					}
		
		return response
	
	def _get_meta(self, data = None, single = False, status = 'success', error_message = None):
		"""
		Returns a response meta dictionary.
		"""
		meta = {}
		meta['status'] =  status
		
		if data is not None:
			meta['count'] = len(data) if not single else 1
		
		if error_message:
			meta['error_message'] = error_message	
		
		return meta

class PluginsHandler(PluginsBaseHandler):
	def read(self, request):
		filters = {
					'title': 		request.GET.get('title', None),
					'category': 	request.GET.get('category', None),
					'platform': 	request.GET.get('platform', None),
					'language': 	request.GET.get('language', None),
					'tag': 			request.GET.get('tag', None),
				}
		
		limit = request.GET.get('limit', 50)
		
		filters = dict([(key, value) for key, value in filters.iteritems() if value])
		queryset = self._build_queryset(fields = self.fields, filters = filters, limit = limit)

		return self._get_response(queryset)
	
class PluginHandler(PluginsBaseHandler):
	def read(self, request, title_slug = None, version_number = None):
		
		if not version_number:
			try:
				plugin = Plugin.objects.get(title_slug = title_slug, approved = True)
			except ObjectDoesNotExist:
				return self._get_response(None, None, ('failure', 'Plugin with this title_slug does not exist'))
			
			queryset = self._format_queryset(plugin, self.fields)
			return self._get_response(queryset, True)
		else:
			try:
				plugin_version = PluginVersion.objects.get(plugin__title_slug = title_slug, \
															version_number = version_number)
			except ObjectDoesNotExist:
				return self._get_response(None, None, ('failure', 'Invalid title slug or version number'))
			
			queryset = self._format_queryset(plugin_version, self.fields_version)
			return self._get_response(queryset, True)
		
class PluginVersionsHandler(PluginsBaseHandler):
	def read(self, request, title_slug = None):
		
		try:
			plugin = Plugin.objects.get(title_slug = title_slug, approved = True)
		except ObjectDoesNotExist:
			return self._get_response(None, None, ('failure', 'Plugin with this title_slug does not exist'))
			
		queryset = self._format_queryset(plugin.pluginversion_set.all(), self.fields_version)
		return self._get_response(queryset)
	
class PluginRelativesHandler(PluginsBaseHandler):
	def read(self, request, title_slug = None):
		
		try:
			plugin = Plugin.objects.get(title_slug = title_slug, approved = True)
		except ObjectDoesNotExist:
			return self._get_response(None, None, ('failure', 'Plugin with this title_slug does not exist'))
			
		queryset = self._format_queryset(Plugin.taxonomy.get_plugin_relatives(plugin), self.fields)
		return self._get_response(queryset)