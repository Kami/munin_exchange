import re

import urllib
import markdown
import pygments
import difflib
import mimetypes

from django.shortcuts import render_to_response, get_object_or_404, HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.comments.views.comments import post_comment
from django.utils import simplejson
from django.core.servers.basehttp import FileWrapper
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Count
from django.utils.html import escape, linebreaks
from django.views.decorators.cache import cache_page

from forms import SubmitPluginForm, SubmitPluginVersionForm, \
	EditPluginForm, get_tags_from_string

from django.contrib.comments.models import Comment
from models import Plugin, PluginVersion
from taxonomy.models import TaxonomyMap, TaxonomyTerm

def index(request):
	query_string = request.META['QUERY_STRING']
	
	# Filters
	filters = parse_filters(query_string)

	# Sorts
	sorts = parse_sorts(query_string)
	
	if sorts:
		for key,value in sorts.iteritems():
			sort_field = key
			sort_direction = value
	else:
		sorts, sort_field, sort_direction = None, None, None
	
	queryset = get_filtered_queryset(filters, sorts)
	plugins = get_pagination_page(1, queryset)
	
	return render_to_response('plugins/index.html', {'plugins': plugins, 'filters': filters, \
													'sorts': sorts, 'sort_field': sort_field, \
													'sort_direction': sort_direction}, \
													context_instance = RequestContext(request))

@login_required
def uploaded_plugins(request):
	plugin_version_ids = PluginVersion.objects.filter(submitted_by = request.user, \
													  version_number = 1) \
											.distinct('plugin') \
											.values_list('plugin_id', flat = True)
	plugins = Plugin.objects.filter(id__in = plugin_version_ids) \
					.order_by('-id') \
					.distinct('id')
	plugins = get_pagination_page(1, plugins)
	
	return render_to_response('plugins/uploaded.html', {'plugins': plugins}, \
													context_instance = RequestContext(request))
	
def search(request):
	keyword = request.GET.get('keyword', None)
	
	if not keyword:
		return HttpResponseRedirect(reverse('plugins_index'))
	
	queryset = Plugin.objects.filter(title__icontains = keyword, approved = True) \
				.order_by('-downloads')
	plugins = get_pagination_page(1, queryset)
			
	return render_to_response('plugins/search.html', {'plugins': plugins, 'keyword': keyword}, \
							context_instance = RequestContext(request))

def top(request):
	top_rated_plugins = get_top_rated_plugins(10)
	most_downloaded_plugins = get_most_downloaded_plugins(10)
	most_commented_plugins = get_most_commented_plugins(10)
	
	return render_to_response('plugins/top.html',
							{
								'top_rated': top_rated_plugins,
								'most_downloaded': most_downloaded_plugins,
								'most_commented': most_commented_plugins,
							},
							context_instance = RequestContext(request))
	
def statistics(request):
	plugins_by_category = TaxonomyMap.objects.filter(type__type = 'category') \
						.values('term__term') \
						.annotate(count = Count('id'))
	plugins_by_category_sorted = sorted(plugins_by_category, key = lambda x: x['count'], \
										reverse = True)[:4]
						
	plugins_by_language = Plugin.objects.filter(approved = True) \
						.values('language') \
						.annotate(count = Count('id'))
	plugins_by_language_sorted = sorted(plugins_by_language, key = lambda x: x['count'], \
										reverse = True)[:5]

	plugins_by_platform = TaxonomyMap.objects.filter(type__type = 'platform') \
						.values('term__term') \
						.annotate(count = Count('id'))
	plugins_by_platform_sorted = sorted(plugins_by_platform, key = lambda x: x['count'], \
										reverse = True)[:2]
										
	select_data = {"date": """DATE_FORMAT(date_submitted, '%%Y-%%m')"""}					
	submissions_by_month = list(PluginVersion.objects.extra(select = select_data).values('date').annotate(count = Count('id')).order_by('date').reverse()[:6])				
	submissions_by_month.reverse()					
	
	select_data = {"date": """DATE_FORMAT(submit_date, '%%Y-%%m')"""}					
	comments_by_month = list(Comment.objects.extra(select = select_data).values('date').annotate(count = Count('id')).order_by('date').reverse()[:6])
	comments_by_month.reverse()
	
	return render_to_response('plugins/statistics.html',
							{
								'plugins_by_category': plugins_by_category,
								'plugins_by_category_sorted': plugins_by_category_sorted,
								'plugins_by_platform': plugins_by_platform,
								'plugins_by_platform_sorted': plugins_by_platform_sorted,
								'plugins_by_language': plugins_by_language,
								'plugins_by_language_sorted': plugins_by_language_sorted,
								'submissions_by_month': submissions_by_month,
								'comments_by_month': comments_by_month,
							},
							context_instance = RequestContext(request))

def details(request, title_slug = None):
	plugin = get_object_or_404(Plugin, title_slug = title_slug)
	relatives = Plugin.taxonomy.get_plugin_relatives(plugin)
	
	return render_to_response('plugins/details.html', {'plugin': plugin, 'relatives': relatives}, \
							context_instance = RequestContext(request))
	
def relatives(request, title_slug = None):
	plugin = get_object_or_404(Plugin, title_slug = title_slug)
	relatives = Plugin.taxonomy.get_plugin_relatives(plugin)
	
	return render_to_response('plugins/relatives.html', { 'plugin': plugin, 'relatives': relatives }, \
							context_instance = RequestContext(request))
	
def versions(request, title_slug = None):
	plugin = get_object_or_404(Plugin, title_slug = title_slug)
	
	return render_to_response('plugins/versions.html', {'plugin': plugin}, \
							context_instance = RequestContext(request))
	
def version(request, title_slug = None, version_number = None):
	version = get_object_or_404(PluginVersion, plugin__title_slug = title_slug, version_number = version_number)
	
	file = version.file
	file.seek(0)
	source_code_raw = file.read()
	source_code = get_source_code_for_highlighthing(source_code_raw)
	source_code_raw = source_code_raw.decode('utf-8', 'ignore')

	try:
		source_code_highlighted = markdown.markdown(source_code, ['codehilite(force_linenos=True)'])
	except Exception:
		# Probably unicode problems, try decoding the content
		try:
			source_code_highlighted = markdown.markdown(source_code.decode('utf-8', 'ignore'), ['codehilite(force_linenos=True)'])
		except Exception:
			# Probably a packed / gziped file
			source_code_highlighted = None

	return render_to_response('plugins/version.html', {'version': version, 'source_code': source_code_highlighted, \
													 'source_code_raw': source_code_raw}, context_instance = RequestContext(request))
	
def version_notes(request, title_slug = None, version_number = None):
	version = get_object_or_404(PluginVersion, plugin__title_slug = title_slug, version_number = version_number)
	
	return render_to_response('plugins/version_notes.html', {'version': version}, \
							context_instance = RequestContext(request))
	
def diff(request, title_slug = None, version_number_1 = None, version_number_2 = None):
	version1 = get_object_or_404(PluginVersion, plugin__title_slug = title_slug, version_number = version_number_1)
	version2 = get_object_or_404(PluginVersion, plugin__title_slug = title_slug, version_number = version_number_2)
	
	file1 = version1.file
	file2 = version2.file
	
	formatted_lines1 = get_formatted_lines(file1)
	formatted_lines2 = get_formatted_lines(file2)

	matcher = difflib.SequenceMatcher(None, formatted_lines1, formatted_lines2)

	# This list goes to the Django template.  It contains a list of
	# dictionaries that contain the actual data to display.
	snippets = []

	for (tag, i1, i2, j1, j2) in matcher.get_opcodes():
		if tag == 'equal':
			# Both sequences have this set of lines.
			snippets.append({'tag':tag,
				'file1_linenums' : '\n'.join([str(n+1) for n in range(i1, i2)]),
				'file1_code' : ''.join(formatted_lines1[i1:i2]),
				'file2_linenums' : '\n'.join([str(n+1) for n in range(j1, j2)]),
				'file2_code' : ''.join(formatted_lines2[j1:j2])})

		elif tag == 'delete':
			# Only the left sequence has this set of lines.
			snippets.append({'tag':tag,
				'file1_linenums' : '\n'.join([str(n+1) for n in range(i1, i2)]),
				'file1_code' : ''.join(formatted_lines1[i1:i2])})

		elif tag == 'insert':
			# Only the right sequence has this set of lines.
			snippets.append({'tag':tag,
				'file2_linenums' : '\n'.join([str(n+1) for n in range(j1, j2)]),
				'file2_code' : ''.join(formatted_lines2[j1:j2])})

		else:
			assert(tag == 'replace')
			# The right and left sequences have conflicting sets of lines.
			snippets.append({'tag':tag,
				'file1_linenums' : '\n'.join([str(n+1) for n in range(i1, i2)]),
				'file1_code' : ''.join(formatted_lines1[i1:i2]),
				'file2_linenums' : '\n'.join([str(n+1) for n in range(j1, j2)]),
				'file2_code' : ''.join(formatted_lines2[j1:j2])})
	
	return render_to_response('plugins/diff.html', {'version1': version1, 'version2': version2, 'snippets': snippets}, \
							context_instance = RequestContext(request))

def download(request, title_slug = None, version_number = None):
	version = get_object_or_404(PluginVersion, plugin__title_slug = title_slug, version_number = version_number)
	file_name = get_download_file_name(version.plugin.title, version.version_number)

	# Increase download count
	version.plugin.downloads += 1
	version.plugin.save()
	
	file = version.file
	file.seek(0)
	content = file.read()

	# Serv user a plugin download
	response = HttpResponse(content, content_type = 'text/plain')
	response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
	response['Content-Length'] = file.size

	return response

def raw(request, title_slug = None, version_number = None):
	version = get_object_or_404(PluginVersion, plugin__title_slug = title_slug, version_number = version_number)
	
	file = version.file
	source_code = file.read()
	
	if not source_code:
		raise Http404()
	
	response = HttpResponse(source_code)
	response['Content-Type'] = 'text/plain; charset=utf-8'
	response['Content-Disposition'] = 'inline'
		
	return response

@login_required
def submit_plugin(request):
	if request.method == 'POST':
		form = SubmitPluginForm(request.POST, request.FILES)
		if form.is_valid():
			clean_data = form.cleaned_data
			title 		= clean_data['title']
			language	= clean_data['language']
			category	= clean_data['category']
			platforms	= clean_data['platform']
			author		= clean_data['author']
			user 		= request.user
			description	= clean_data['description']
			tags_string	= clean_data['tags']
			file		= request.FILES['file']
			
			try:
				screenshot	= request.FILES['screenshot']
			except Exception:
				screenshot = None
			
			if tags_string:
				tags = get_tags_from_string(tags_string)

			# Add a plugin
			plugin = Plugin(title = title, language = language,	description = description, \
						screenshot = screenshot)
			
			if user.is_staff:
				# Plugins by staff don't need to be approved
				approved = True
			else:
				approved = False
				
			plugin.approved = approved
			plugin.save()

			# Assign category, platform(s) and tag(s)
			assign_category(plugin, category)
			assign_platforms(plugin, platforms)
			assign_tags(plugin, tags, plugin.get_tags())
			
			# Add a first version to the plugin
			version = PluginVersion(plugin = plugin, author = author, submitted_by = user, \
								file = file)
			version.save(send_to_twitter = True)
				
			messages.add_message(request, messages.SUCCESS, 'Your plugin has been successfully' \
								' uploaded.<br /><br />Thank you for your contribution.')
			return HttpResponseRedirect(reverse('plugins_submit_plugin'))
	else:
		form = SubmitPluginForm()
	
	platform_independent_id = TaxonomyTerm.objects.get(term = 'platform independent', \
													type__type = 'platform').id
	
	return render_to_response('plugins/submit.html', {'form': form, 'platform_independent_id': \
											platform_independent_id}, context_instance = RequestContext(request))

@login_required
def submit_version(request, title_slug = None):
	plugin = get_object_or_404(Plugin, title_slug = title_slug)
	
	if request.method == 'POST':
		form = SubmitPluginVersionForm(request.POST, request.FILES)
		if form.is_valid():
			clean_data = form.cleaned_data
			author		= clean_data['author']
			user 		= request.user
			notes		= clean_data['notes']
			file		= request.FILES['file']

			# Add a first version to the plugin
			version = PluginVersion(plugin = plugin, author = author, submitted_by = user, \
								notes = notes, file = file)
			version.save(send_to_twitter = True, force_insert = True)
				
			messages.add_message(request, messages.SUCCESS, 'Your plugin version has been successfully' \
								' uploaded.<br /><br />Thank you for your contribution.')
			return HttpResponseRedirect(reverse('plugins_submit_version', args = (title_slug,)))
	else:
		form = SubmitPluginVersionForm()
	
	return render_to_response('plugins/submit_version.html', {'plugin': plugin, 'form': form}, \
							context_instance = RequestContext(request))

@login_required
def edit_plugin(request, title_slug = None):
	plugin = get_object_or_404(Plugin, title_slug = title_slug, \
							pluginversion__version_number = 1, \
							pluginversion__submitted_by = request.user)

	if request.method == 'POST':
		form = EditPluginForm(request.POST, request.FILES)
		
		if form.is_valid():
			clean_data = form.cleaned_data
			language	= clean_data['language']
			category	= clean_data['category']
			platforms	= clean_data['platform']
			description	= clean_data['description']
			tags_string	= clean_data['tags']
			
			if tags_string:
				tags = get_tags_from_string(tags_string)

			try:
				screenshot	= request.FILES['screenshot']
			except Exception:
				# No screenshot is provided
				
				if plugin.screenshot:
					# Screenshot already exists, use this one
					screenshot = plugin.screenshot
				else:
					screenshot = None

			plugin.language = language
			plugin.description = description
			plugin.screenshot = screenshot
			
			# Assign category, platform(s) and tag(s)
			assign_category(plugin, category)
			assign_platforms(plugin, platforms)
			assign_tags(plugin, tags, plugin.get_tags())
				
			plugin.save()
			
			messages.add_message(request, messages.SUCCESS, 'Your plugin has been successfully' \
								' edited.')
			return HttpResponseRedirect(reverse('plugins_uploaded_plugins'))
	else:
		data = {
			'language': plugin.language,
			'category': plugin.get_category_term().id,
			'description': plugin.description.raw,
			'platform': [p.id for p in plugin.get_platform_terms()],
			'screenshot': plugin.screenshot,
			'tags': ', ' . join(plugin.get_tags()),
		}
		form = EditPluginForm(initial = data)
	
	platform_independent_id = TaxonomyTerm.objects.get(term = 'platform independent', \
													type__type = 'platform').id
													
	return render_to_response('plugins/edit_plugin.html', {'plugin': plugin, 'form': form,
														'platform_independent_id': platform_independent_id}, \
							context_instance = RequestContext(request))

def comment_post_wrapper(request):
	if request.user.is_authenticated():
		if not (request.user.username == request.POST['name'] and \
			   request.user.email == request.POST['email']):
			return HttpResponse("You registered user...trying to spoof a form...eh?")
	return post_comment(request)
	return HttpResponse("You anonymous cheater...trying to spoof a form?")

def comment_posted(request):
	try:
		comment_id = request.GET['c']
		comment = get_object_or_404(Comment, pk = comment_id)
		plugin = Plugin.objects.get(pk = comment.content_object.pk)

		if plugin:
			messages.success(request, 'Thank you for your comment.')
			
			return HttpResponseRedirect('%s#c%s' % (plugin.get_absolute_url(), comment_id))
	except KeyError:
		pass
	
	return HttpResponseRedirect('/')  	
	
def search_lookup(request):
	""" Returns a string of plugins which match the search query (used with autocomplete plugin). """
	result = ''
	if request.method == 'GET':
		if request.GET.has_key('q'):
			value = request.GET['q']
			
			if len(value) >= 2:
				result = Plugin.objects.filter(title__icontains = value, approved = True) \
							.values_list('title', flat = True)
				result = '\n' . join(set(result))
				
	return HttpResponse(result)
	
# Helper functions
def get_pagination_page(page = 1, queryset = False):
	if queryset is not False:
		plugin_list = queryset
	else:
		plugin_list = Plugin.objects.filter(approved = True).order_by('-id')
	
	paginator = Paginator(plugin_list, 30)
	
	try:
		page = int(page)
	except ValueError:
		page = 1
		
	try:
		plugins = paginator.page(page)
	except (EmptyPage, InvalidPage):
		plugins = paginator.page(paginator.num_pages)
		
	return plugins
	
def get_download_file_name(plugin_title, version_number):
	""" Returns a 'friendly' file name for the given plugin version. """
	plugin_title = plugin_title.replace(' ', '_')
	file_name = '%s-v%s' % (plugin_title, version_number)
	
	return file_name

def get_formatted_lines(file_obj):
	'''
	This function takes either a SubmittedFile or GradedFile object, and returns
	a list of HTML-formatted lines from the input file's data.
	'''

	file_obj.seek(0)
	file_data = str(file_obj.read())

	# Guess the lexer to use, since submissions could be in any of a dozen or so
	# different programming languages that we teach.  If we can't identify it,
	# use the plain ol' TextLexer.
	try:
		lexer = pygments.lexers.guess_lexer(file_data)
	except pygments.util.ClassNotFound:
		lexer = pygments.lexers.TextLexer()

	# Generate a list of HTML-formatted lines from the source file, and
	# return that list!
	formatter = pygments.formatters.HtmlFormatter()
	formatted_lines = [t for (_, t) in formatter._format_lines(lexer.get_tokens(file_data))]
	return formatted_lines

def get_source_code_for_highlighthing(source_code):
	""" Adds for spaces before each line so markdown codehilite filter
	for syntax highlighithing can be applied on it.
	"""
	
	source_code_splitted = source_code.split('\n')
	source_code = '' . join(['	%s\n' % v for v in source_code_splitted])
	
	return source_code

def parse_filters(query_string):
	""" Parses the filter names and values from the query string. """
	
	if query_string.find('filter=') == -1:
		return None
	
	valid_filters = ('category', 'platform', 'language', 'tag', 'date')

	filters = re.findall('.?filter=(.*?)(&|$)', query_string)
	
	try:
		filters = dict([filter[0].split(':') for filter in filters 
						if filter[0].split(':')[0] in valid_filters])
	except Exception:
		# Probably a malformed filter query string
		return None
	
	for key in filters.keys():
		filters[key] = [urllib.unquote(value) for value in filters[key].split(',')]

	if not filters:
		return None

	return filters

def parse_sorts(query_string):
	""" Parses the sorts names and values from the query string. """
	
	if query_string.find('sort=') == -1:
		return None
	
	valid_sorts = {
					'title': 'title',
					'language': 'language',
					 'date_submitted': 'pluginversion__date_submitted'
				  }
	valid_directions = ('asc', 'desc')
	
	sorts = re.findall('.?sort=(.*?)(&|$)', query_string)
	try:
		sorts = [(valid_sorts[sort[0].split(':')[0]], sort[0].split(':')[1])
					for sort in sorts 
					if sort[0].split(':')[0] in valid_sorts
					and sort[0].split(':')[1] in valid_directions]
	except Exception:
		# Probably a malformed sort query string
		return None

	sorts = dict(sorts[:1]) # Only single sort is allowed

	if not sorts:
		return None

	return sorts

def get_filtered_queryset(filters = None, sorts = None):
	""" Returns a filtered Plugin QuerySet object. """

	if not filters and not sorts:
		return False

	plugin_ids_list = []
	if filters:
		plugin_ids_list = []
		for filter_name, filter_values in filters.iteritems():
			if filter_name in ['category', 'platform', 'tag']:
				# Taxonomy based filters
				ids = TaxonomyMap.objects.filter(type__type__iexact = filter_name, \
										term__term__in = filter_values).values_list('object_id', flat = True)
				plugin_ids_list.append(set(ids))
			elif filter_name in ['date']:
				year, month, day = (filter_values[0].split('-') + [None, None, None])[:3]
				
				query_filter = {}
				if year:
					query_filter.update({'pluginversion__date_submitted__year': year})
				if month:
					query_filter.update({'pluginversion__date_submitted__month': month})
				if day:
					query_filter.update({'pluginversion__date_submitted__day': day})
				
				ids = Plugin.objects.filter(**query_filter).values_list('id', flat = True)
				plugin_ids_list.append(set(ids))
			else:
				# Normal filter based on model field
				query_filter = {'%s__in' % (filter_name): filter_values}
				ids = Plugin.objects.filter(**query_filter).values_list('id', flat = True)
				plugin_ids_list.append(set(ids))
			
			# Only those values which are located in all the result sets (AND filter)
			plugin_ids = list(set.intersection(*plugin_ids_list))
		
	if sorts:
		plugin_ids_list = []
		for sort_name, sort_value in sorts.iteritems():
			if sort_value == 'asc':
				order_by = sort_name
			elif sort_value == 'desc':
				order_by = '-%s' % (sort_name)
	else:
		order_by = '-pluginversion__date_submitted'
	
	if filters:	
		plugins = Plugin.objects.filter(id__in = plugin_ids, approved = True).distinct().order_by(order_by)
	else:
		plugins = Plugin.objects.filter(approved = True).distinct().order_by(order_by)
			
	return plugins

def get_latest_plugins(count = 4):
	""" Returns count number of latest plugins. """
	plugins = Plugin.objects.filter(approved = True).order_by('-id')[:count]
	
	return plugins

def get_most_downloaded_plugins(count = 4):
	""" Returns count number of most downloaded plugins. """
	plugins = Plugin.objects.filter(approved = True).order_by('-downloads')[:count]
	
	return plugins

def get_top_rated_plugins(count = 4):
	""" Returns count number of top rated plugins. """
	plugins = Plugin.objects.filter(approved = True) \
				.order_by('-rating_score', '-rating_votes')[:count]
	
	return plugins

def get_most_commented_plugins(count = 4):
	""" Returns the count number of plugins with most comments. """
	plugin_ids = Comment.objects.values_list('object_pk', flat = True) \
		.annotate(count = Count('id')).order_by('-count')[:10]
	plugin_ids = [int(id) for id in plugin_ids]
	plugins = Plugin.objects.filter(approved = True, id__in = plugin_ids)
	
	plugins_sorted = [p for plugin_id in plugin_ids
						for p in plugins
						if p.id == plugin_id]

	return plugins_sorted

def assign_category(plugin, category):
	""" Assigns a category to the plugin. """
	category_taxonomy_id = Plugin.taxonomy.get_category_taxonomy().id
	
	# Delete the old assignment
	TaxonomyMap.objects.filter(object_id = plugin.id, type__id = category_taxonomy_id) \
						.delete()
	
	# Create a new assignment
	taxonomy_category = TaxonomyMap(object = plugin, term_id = category, type_id = \
									category_taxonomy_id)
	taxonomy_category.save()

def assign_platforms(plugin, platforms):
	""" Assigns platform(s) to the plugin. """
	# Check if a plugin is platform independent
	# If it is, delete rest of the platforms (if any selected)
	platform_taxonomy_id = TaxonomyTerm.objects.get(term = 'platform independent', type__type__iexact = 'platform').id
	platform_taxonomy_id = str(platform_taxonomy_id)
	if platform_taxonomy_id in platforms:
		platforms = [platform_taxonomy_id]
		
	platform_type_id = Plugin.taxonomy.get_platform_taxonomy().id
	taxonomy_terms = Plugin.taxonomy.get_taxonomy_term_objects_from_platform_ids(platforms)
	
	# Delete the old assignments
	TaxonomyMap.objects.filter(object_id = plugin.id, type__id = platform_type_id).delete()
	
	# Assign new platforms to the plugin (taxonomy mapping)
	for term in taxonomy_terms:
		# Create mappings (TaxonomyTerm [tag] -> Plugin)
		mapping = TaxonomyMap(object = plugin, term = term, type_id = platform_type_id)
		mapping.save()

def assign_tags(plugin, new_tags, old_tags = None):
	""" Assigns tags to the plugin (taxonomy mappings) """
	tag_type_id = Plugin.taxonomy.get_tag_taxonomy().id
	taxonomy_terms = Plugin.taxonomy.get_taxonomy_term_objects_from_tags(new_tags)
			
	if old_tags:
		# 1. Delete all the old mappings
		TaxonomyMap.objects.filter(object_id = plugin.id, type__id = tag_type_id).delete()

	# 2. Assign new mappings
	for term in taxonomy_terms:
		# Create mappings (TaxonomyTerm [tag] -> Plugin)
		mapping = TaxonomyMap(object = plugin, term = term, type_id = tag_type_id)
		mapping.save()