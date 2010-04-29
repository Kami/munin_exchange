import os
import sys
import re

root_path = os.path.abspath(os.path.dirname(__file__) + '/../')
config_path = os.path.join(
	os.path.realpath(os.path.dirname(__file__)), 'configs/common/'
)

python_path = os.path.join(
	os.path.realpath(os.path.dirname(__file__)), '../'
)

apps_path = os.path.join(
	os.path.realpath(os.path.dirname(__file__)), 'apps'
)

sys.path.insert(0, config_path)
sys.path.insert(0, python_path)
sys.path.insert(0, apps_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'munin_exchange.configs.common.settings'

from django.core.files import File
from django.core.files.base import ContentFile
from django.core.management import setup_environ
from django.db import connections, connection, transaction
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.utils.html import strip_tags

from configs.common import settings
setup_environ(settings)

from pygments.lexers import guess_lexer, guess_lexer_for_filename

from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from apps.plugins.models import Plugin, PluginVersion
from apps.plugins.forms import SubmitPluginForm, SubmitPluginVersionForm, get_tags_from_string
from taxonomy.models import TaxonomyMap, TaxonomyTerm

def import_plugins():
	cursor = connections['postgres'].cursor()
	cursor.execute("""SELECT p.plugin_name, p.description, ph.author, c.class_name,
	p.timestamp, ph.filename, ph.graph_sample_1, ph.phid
	FROM plugins p
	INNER JOIN classes c ON p.cid = c.cid
	INNER JOIN plugin_history ph ON p.pid = ph.pid
	""")
	rows = cursor.fetchall()

	# Pre defined stuff
	user = User.objects.get(id = 1)
	platforms = [9] # platform independent
	category = 17 # other

	# Other pre-fetched stuff
	category_taxonomy_id = Plugin.taxonomy.get_category_taxonomy().id
	platform_type_id = Plugin.taxonomy.get_platform_taxonomy().id
	platform_taxonomy_terms = Plugin.taxonomy.get_taxonomy_term_objects_from_platform_ids(platforms)
	tag_type_id = Plugin.taxonomy.get_tag_taxonomy().id

	plugins_path = 'plugins/'
	screenshots_path = 'screenshots/'

	for index, row in enumerate(rows):
		plugin_name = row[0]
		description = strip_tags(row[1])
		author = row[2]
		tags_string = row[3].lower()

		date_submitted = row[4]
		filename = row[5]
		screenshot = row[6]
		phid = row[7]
		approved = True

		# Missing plugin file
		if not filename:
			continue

		if screenshot:
			sf = open(os.path.join(screenshots_path, screenshot), 'r')
			screenshot_file = ContentFile(sf.read())

		pf = open(os.path.join(plugins_path, filename), 'r')
		pf_content = pf.read()
		plugin_file = ContentFile(pf_content)
		plugin_size = plugin_file.size

		if plugin_size == 0:
			# Empty file, skip this plugin
			continue

		# Try to detect the plugin language using Pygments
		lexer = str(guess_lexer(pf_content))
		match = re.match(r'<pygments.*\.(.*?)Lexer>', lexer)

		if match:
			language = match.group(1)

			if language == 'SourcesList':
				language = 'Unknown'
		else:
			language = 'Unknown'

		if tags_string:
			tags = get_tags_from_string(tags_string)

		# Add a plugin
		plugin = Plugin(title = plugin_name, language = language, description = description)

		approved = True

		plugin.approved = approved

		if screenshot:
			plugin.screenshot.save(screenshot, screenshot_file)

		plugin.save()

		# Add a first version to the plugin
		version = PluginVersion(plugin = plugin, author = author, submitted_by = user)

		version.file.save(filename, plugin_file)
		version.save(send_to_twitter = False)

		# Assign category this plugin
		taxonomy_category = TaxonomyMap(object = plugin, term_id = category, type_id = \
									category_taxonomy_id)
		taxonomy_category.save()

		# Assign platforms to the plugin (taxonomy mapping)
		for term in platform_taxonomy_terms:
			# Create mappings (TaxonomyTerm [tag] -> Plugin)
			mapping = TaxonomyMap(object = plugin, term = term, type_id = platform_type_id)
			mapping.save()

		# Assigns tags to the plugin (taxonomy mappings)
		tag_taxonomy_terms = Plugin.taxonomy.get_taxonomy_term_objects_from_tags(tags)
		for term in tag_taxonomy_terms:
			# Create mappings (TaxonomyTerm [tag] -> Plugin)
			mapping = TaxonomyMap(object = plugin, term = term, type_id = tag_type_id)
			mapping.save()

		pf.close()
		sf.close()

		print 'Imported %d' % (index + 1)

def import_comments():
	cursor = connections['postgres'].cursor()

	plugins = Plugin.objects.all()
	site = Site.objects.get(id = 1)

	for plugin in plugins:
		plugin_id = plugin.id
		cursor.execute("""SELECT name, comment, timestamp
		FROM plugin_comments
		WHERE phid = %s
		ORDER BY timestamp ASC
		""", (plugin_id,))
		rows = cursor.fetchall()

		plugin_id = plugin.id
		content_type_id = 18 # plugin

		for row in rows:
			author = row[0]
			comment = row[1]
			submit_date = row[2]

			c = Comment(name = author, comment = comment, content_type_id = content_type_id, \
					object_pk = plugin_id, submit_date = submit_date, site = site, is_public = True)
			c.save()

			print 'Imported comment for plugin %d' % (plugin_id)

def get_plugins_submission_dates():

	cursor = connections['postgres'].cursor()
	cursor.execute("""SELECT plugin_name, description, timestamp FROM plugins""")
	rows = cursor.fetchall()

	with open('plugin_version_dates.py', 'w') as file:
		for index, row in enumerate(rows):
			plugin_name = row[0]
			description = row[1]
			timestamp = row[2]
			title_slug = plugin_name

			string = """# Plugin %d
try:
	pv = PluginVersion.objects.get(plugin__title_slug = '%s', plugin__description = '''%s''')
	pv.date_submitted = '%s'
except Exception:
	pv = None

if pv is not None:
	pv.save()\n\n""" % (index, title_slug, description, timestamp)
			file.write(string)

if __name__ == '__main__':
	get_plugins_submission_dates()
