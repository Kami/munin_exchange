from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from dajax.core import Dajax

from views import get_pagination_page, get_filtered_queryset, \
				parse_filters, parse_sorts
from models import Plugin, PluginVersion

def pagination_index(request, p, query_string = None):
	try:
		page = int(p)
	except:
		page = 1
	
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
	plugins = get_pagination_page(page, queryset)
	render = render_to_string('plugins/index_page.html', \
							{'plugins': plugins})

	dajax = Dajax()
	dajax.assign('#pagination', 'innerHTML', render)
	dajax.script('$("a.title").tipTip({ delay: 100 });');
	return dajax.json()

@login_required
def pagination_uploaded(request, p, query_string = None):
	try:
		page = int(p)
	except:
		page = 1
		
	plugin_version_ids = PluginVersion.objects.filter(submitted_by = request.user, \
													  version_number = 1) \
											.distinct('plugin') \
											.values_list('plugin_id', flat = True)
	plugins = Plugin.objects.filter(id__in = plugin_version_ids) \
					.order_by('-id') \
					.distinct('id')
	plugins = get_pagination_page(page, plugins)
	
	render = render_to_string('plugins/uploaded_page.html', \
							{'plugins': plugins})
	
	dajax = Dajax()
	dajax.assign('#pagination', 'innerHTML', render)
	dajax.script('$("a.title").tipTip({ delay: 100 });');
	return dajax.json()

def get_download_count(request, plugin_id):
	try:
		plugin = Plugin.objects.get(id = int(plugin_id))
	except ObjectDoesNotExist:
		return None
	
	dajax = Dajax()
	dajax.assign('#downloads_value', 'innerHTML', plugin.downloads)
	return dajax.json()

def rating(request, plugin_id, score):
	success = True
	try:
		plugin_id = int(plugin_id)
		score = int(score)
	except:
		message = 'Invalid plugin or score'
		success = False
	
	try:
		plugin = Plugin.objects.get(id = plugin_id)
	except ObjectDoesNotExist:
		message = 'Invalid plugin ID'
		success = False
		
	if score not in range(1,6):
		message = 'Invalid score'
		success = False
	
	dajax = Dajax()
	
	if success:
		try:
			plugin.rating.add(score = score, user = None, ip_address = request.META['REMOTE_ADDR'])
			message = 'Thank you for your vote'
		except:
			message = 'Your have already casted your vote for this plugin'
			success = False
	
	if success:
		dajax.add_css_class('#rate_tip', 'success')
		dajax.assign('#rate_result', 'innerHTML', '%s (%d votes total)'% (plugin.rating.get_rating(), \
																		 plugin.rating.get_ratings().count()))
	else:
		dajax.add_css_class('#rate_tip', 'error')

	dajax.assign('#rate_tip', 'innerHTML', message)
	return dajax.json()