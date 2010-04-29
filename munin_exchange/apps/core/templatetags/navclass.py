from django.template import Library, Node, resolve_variable, TemplateSyntaxError
from django.core.urlresolvers import reverse

register = Library()
   
@register.simple_tag
def active(request, pattern):
    import re

    if re.search(pattern, request.get_full_path()):
        return 'active'
    return ''