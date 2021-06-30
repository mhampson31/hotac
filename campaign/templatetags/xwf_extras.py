from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

import re

register = template.Library()

rgx = re.compile(r'\[([\w\s\#]+?)\]')

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
    'Reverse Bank Left': 'reversebankleft',
    'Reverse Bank Right': 'reversebankright',
    'Sloop Left': 'sloopleft',
    'Sloop Right': 'sloopright',
    'Straight':'straight',
    'K-Turn':'kturn',
    'Ordnance':'rangebonusindicator'
}


def regex_icon(m):
    return get_icon(m[1])


@register.filter(is_safe=True)
@stringfilter
def get_icon(istring, css=''):
    """
    The get_icon filter add css like .hard or .easy in two ways:
    adding the class as the css parameter if calling get_icon directly, or including
    it in the format 'icon_name#css' when using the iconize template filter.
    """
    istring = istring.split('#', 1)
    iname = istring[0].strip()
    if len(istring) > 1:
        css = '{} {}'.format(css, istring[1])
    iname = icon_text.get(iname, iname.lower())
    if iname == 'pilot':
        iname = 'helmet-rebel'
    elif iname == 'initiative':
        iname = 'rebel'
    """Returns the <i> block that inserts an icon from the xwing font css. Doesn't work for ship icons."""
    return mark_safe('<i class="xwing-miniatures-font xwing-miniatures-font-{} {}"></i>'.format(iname, css))


@register.filter(is_safe=True)
@stringfilter
def iconize(text):
    return mark_safe(re.sub(rgx, regex_icon, text))


@register.filter(is_safe=True)
def threatbar(threat):
    colors = ('green', 'yellow', 'orange', 'red', 'magenta', 'purple')
    return '<span class="threat-{}">{}{}</span>'.format(threat, '▰' * threat, '▱' * (6-threat))

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def hotac_crit():
    """
    Not a real function. I just needed to write this down somewhere.
    """
    from random import choice
    return choice(
        ('weapons disabled',
         'ion',
         'stress',
         'stress',
         'damage'
         'damage'
        )
    )

@register.filter
def get_cost(upgrade, logic):
    return upgrade.campaign_cost(logic)

@register.filter(is_safe=True)
def repeat(icon, charges):
    return icon * charges
