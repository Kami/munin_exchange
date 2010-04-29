import re

from settings import VALID_SOURCE_CODE_FILE_TYPES 
from django import forms
from django.forms.util import ErrorList
from django.core.exceptions import ObjectDoesNotExist

from taxonomy.models import TaxonomyTerm
from models import Plugin

class CategoryField(forms.ChoiceField):
	def clean(self, value):
		""" Checks that the field contains a valid category (taxonomy). """
		try:
			value = int(value)
		except:
			raise forms.ValidationError('Invalid category was specified')
		
		try:
			TaxonomyTerm.objects.get(id = value, type__type__iexact = 'category')
		except ObjectDoesNotExist:
			raise forms.ValidationError('Invalid category was specified')
		
		return value
	
class PlatformField(forms.MultipleChoiceField):
	def clean(self, value):
		if not value:
			raise forms.ValidationError('Invalid platform was specified')
		
		# At least one platform must be selected
		count = TaxonomyTerm.objects.filter(id__in = value, type__type__iexact = 'platform').count()
		
		if count != len(value):
			raise forms.ValidationError('You need to select a valid platform')
		
		return value

class SubmitPluginForm(forms.Form):
	required_css_class = 'required'
	
	title = forms.CharField(max_length = 120, label = 'Title')
	language = forms.CharField(max_length = 30, label = 'Language', help_text = 'e.g.'\
													'Python, Bash, Ruby, ...')
	category = CategoryField(choices = Plugin.taxonomy.get_available_categories())
	platform = PlatformField(choices = Plugin.taxonomy.get_available_platforms(), \
										widget = forms.CheckboxSelectMultiple(attrs = {'class': 'choices'}), label= 'Platform(s)', help_text = 'Check "platform independent" if a plugin is platform independent')
	description = forms.CharField(widget = forms.Textarea, label = 'Description', \
												help_text = '<a href="http://warpedvisions.org/projects/markdown-cheat-sheet/" target="_blank">Markdown</a> is enabled')
	screenshot = forms.ImageField(required = False, label = 'Screenshot', help_text = 'optional (if provided, thumbnail will be automatically created)')
	tags = forms.CharField(label = 'Tags', help_text = 'Separate multiple tags with a comma')
	author = forms.CharField(max_length = 100, label = 'Author')
	file = forms.FileField(label = 'File', \
			help_text = 'Actual file containing the source code (<a href="javascript:void(0);" title="The following MIME types are allowed: %s">valid mimes</a>)' % (', ' . join(VALID_SOURCE_CODE_FILE_TYPES)))		
	
	def clean_file(self):
		cleaned_data = self.cleaned_data
		file = cleaned_data['file']
		content_type = file.content_type
		
		#if content_type not in VALID_SOURCE_CODE_FILE_TYPES :
		#	raise forms.ValidationError('Only the following MIME types are allowed: %s' % (', ' . join(VALID_SOURCE_CODE_FILE_TYPES)))
	
		return file
	
	def clean(self):
		cleaned_data = self.cleaned_data
		title = cleaned_data.get('title')
		platforms = cleaned_data.get('platform')
		
		if title and platforms:
			platforms = [int(id) for id in platforms]
			
			# Only one plugin with the same title can exist in each category
			plugins = Plugin.objects.filter(title = title)
			
			if plugins:
				plugin_platform_terms = [list(plugin.get_platform_terms()) for plugin in plugins]
				plugin_platform_terms = sum(plugin_platform_terms, [])
				plugin_platform_term_ids = set([term.id for term in plugin_platform_terms])
	
				if set(platforms).intersection(plugin_platform_term_ids):
					error = 'Plugin with the same name and platform already exists. \
					Please upload a new version to an existing plugin.'

					self._errors['platform'] = ErrorList([error])
					del cleaned_data['platform']
		
		return cleaned_data
	
class SubmitPluginVersionForm(forms.Form):
	required_css_class = 'required'
	
	author = forms.CharField(max_length = 100, label = 'Author', help_text = 'who made this version (probably you?)')
	notes = forms.CharField(max_length = 250, label = 'Notes', help_text = 'e.g. what is different from the original version')
	file = forms.FileField(label = 'File', help_text = 'Actual file containing the source code')

class EditPluginForm(forms.Form):
	required_css_class = 'required'

	language = forms.CharField(max_length = 30, label = 'Language', help_text = 'e.g.'\
													'Python, Bash, Ruby, ...')
	category = CategoryField(choices = Plugin.taxonomy.get_available_categories())
	platform = PlatformField(choices = Plugin.taxonomy.get_available_platforms(), \
										widget = forms.CheckboxSelectMultiple(attrs = {'class': 'choices'}), label= 'Platform(s)', help_text = 'Check "platform independent" if a plugin is platform independent')
	description = forms.CharField(widget = forms.Textarea, label = 'Description', \
												help_text = '<a href="http://warpedvisions.org/projects/markdown-cheat-sheet/" target="_blank">Markdown</a> is enabled')
	screenshot = forms.ImageField(required = False, label = 'Screenshot', help_text = 'optional (if provided, thumbnail will be automatically created)')
	tags = forms.CharField(label = 'Tags', help_text = 'Separate multiple tags with a comma')

def get_tags_from_string(string):
	""" Returns a list of tags in string splitted by a comma. """
	string = string.replace(', ', ',')
	tags = string.split(',')
	
	return tags