from django import template
from math import floor

register = template.Library()


@register.filter(is_safe=True)
def dial_pad(mvs, width):
    return [cell for cell in range(floor((width-len(mvs))/2))]
