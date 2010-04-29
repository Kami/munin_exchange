from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter()
def htmlentities(s):
    return mark_safe(escape(s).encode('ascii', 'xmlcharrefreplace'))