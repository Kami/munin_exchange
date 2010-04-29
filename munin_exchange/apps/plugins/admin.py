from django.contrib import admin
from django.contrib.contenttypes import generic

from models import Plugin, PluginVersion
from taxonomy.models import TaxonomyMap
	
class ExtraInline(generic.GenericTabularInline):
	model = TaxonomyMap
	verbose_name = 'extra'
	verbose_name_plural = 'Extras'
	max_num = 10
	
class PluginVersionInline(admin.StackedInline):
	model = PluginVersion
	max_num = 1

class PluginAdmin(admin.ModelAdmin):
	list_display = ('title', 'category', 'platforms', 'tags', 'approved')
	list_filter = ('approved',)
	search_fields = ['title']
	
	inlines = [ExtraInline, PluginVersionInline]
	exclude = ('downloads',)
	
	def tags(self, obj):
		tags = obj.get_tags()
		return ', ' . join(tags)
	
	def category(self, obj):
		return obj.get_category()
	
	def platforms(self, obj):
		platforms = obj.get_platforms()
		return ', ' . join(platforms)
	
	tags.short_description = 'Tags'
	category.short_description = 'Category'
	platforms.short_description = 'Platforms'
	
class PluginVersionAdmin(admin.ModelAdmin):
	list_display = ('plugin', 'version_number', 'author', 'submitted_by', \
					'date_submitted', 'sent_to_twitter')
	search_fields = ['plugin']
	
	date_hierarchy = 'date_submitted'
	ordering = ('date_submitted',)
	
	exclude = ('sent_to_twitter',)

admin.site.register(Plugin, PluginAdmin)
admin.site.register(PluginVersion, PluginVersionAdmin)