from django.contrib.sitemaps import Sitemap
from plugins.models import Plugin

class PluginsSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5
    
    def items(self):
        return Plugin.objects.filter(approved = True)
    
    def lastmod(self, obj):
        return obj.get_latest_version().date_submitted