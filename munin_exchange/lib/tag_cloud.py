import math

from django.utils.translation import ugettext as _
from django.db.models.aggregates import Count

from plugins.models import Plugin, PluginVersion
from taxonomy.models import TaxonomyMap, TaxonomyTerm

# Font size distribution algorithms
LOGARITHMIC, LINEAR = 1, 2

def get_tag_counts():
	tags = {}
	taxonomy_term_ids = TaxonomyMap.objects.filter(type__type__iexact = 'tag') \
						.values_list('term_id', 'term__term') \
						.annotate(count = Count('id'))
	
	for _, tag, count in taxonomy_term_ids:
		tags[tag] = { 'count': count }
		
	return tags

def _calculate_thresholds(min_weight, max_weight, steps):
	delta = (max_weight - min_weight) / float(steps)
	return [min_weight + i * delta for i in range(1, steps + 1)]

def _calculate_tag_weight(weight, max_weight, distribution):
	"""
	Logarithmic tag weight calculation is based on code from the
	`Tag Cloud`_ plugin for Mephisto, by Sven Fuchs.

		.. _`Tag Cloud`: http://www.artweb-design.de/projects/mephisto-plugin-tag-cloud
	"""
	if distribution == LINEAR or max_weight == 1:
		return weight
	elif distribution == LOGARITHMIC:
		return math.log(weight) * max_weight / math.log(max_weight)
	raise ValueError(_('Invalid distribution algorithm specified: %s.') % distribution)
	
def calculate_cloud(steps = 4, distribution = LOGARITHMIC, min_count = 5):
	"""
	Add a ``font_size`` attribute to each tag according to the
	frequency of its use, as indicated by its ``count``
	attribute.

	``steps`` defines the range of font sizes - ``font_size`` will
	be an integer between 1 and ``steps`` (inclusive).

	``distribution`` defines the type of font size distribution
	algorithm which will be used - logarithmic or linear. It must be
	one of ``tagging.utils.LOGARITHMIC`` or ``tagging.utils.LINEAR``.
	"""
	tag_counts = get_tag_counts()

	if len(tag_counts) > 0:
		counts = [i['count'] for i in tag_counts.values()]
		min_weight = float(min(counts))
		max_weight = float(max(counts))
		thresholds = _calculate_thresholds(min_weight, max_weight, steps)
		for tag in tag_counts.keys():
			font_set = False
			tag_weight = _calculate_tag_weight(tag_counts[tag]['count'], max_weight, distribution)
			for i in range(steps):
				if not font_set and tag_weight <= thresholds[i]:
					tag_counts[tag]['font_size'] = i + 1
					font_set = True

	# Cut off the data at the minimum count
	tag_list = [(k, v['font_size'], v['count']) for k,v in tag_counts.items() if v['count'] > min_count]
	
	# Sort by count
	tag_list.sort(lambda x,y:cmp(x[2], y[2]))
	
	# Reverse that
	tag_list.reverse()
	return tag_list