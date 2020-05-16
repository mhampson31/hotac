from django import template
from django.utils.safestring import mark_safe


import re

register = template.Library()

rgx = re.compile(r'\[([\w\s]+?)\]')

icon_text = {
    'Barrel Roll':'barrelroll',
    'Bank Left':'bankleft',
    'Bank Right':'bankright',
    'Boost': 'boost',
    'Bullseye Arc':'bullseyearc',
    'Single Turret Arc':'singleturretarc',
    'Double Turret Arc':'doubleturretarc',
    'Configuration':'config',
    'Critical Hit':'crit',
    'Front Arc':'frontarc',
    'Force Power':'forcepower',
    'Force Charge':'forcecharge',
    'Force': 'forcecharge',
    'Rear Arc':'reararc',
    'Rotate Arc':'rotatearc',
    'Stationary':'stop',
    'Tallon Roll Left':'trollleft',
    'Tallon Roll Right':'trollright',
    'Turn Left':'turnleft',
    'Turn Right':'turnright',
}


def regex_icon(m):
    return get_icon(m[1])


@register.filter(is_safe=True)
def get_icon(iname, css=''):
    iname = icon_text.get(iname, iname.lower())
    if iname == 'pilot':
        iname = 'helmet-rebel'
    elif iname == 'initiative':
        iname = 'rebel'
    """Returns the <i> block that inserts an icon from the xwing font css. Doesn't work for ship icons."""
    return mark_safe('<i class="xwf xwf-{} {}"></i>'.format(iname, css))


@register.filter(is_safe=True)
def iconize(text):
    return mark_safe(re.sub(rgx, regex_icon, text))


@register.filter(is_safe=True)
def threatbar(threat):
    colors = ('green', 'yellow', 'orange', 'red', 'magenta', 'purple')
    return '<span class="threat-{}">{}{}</span>'.format(threat, '▰' * threat, '▱' * (6-threat))

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)