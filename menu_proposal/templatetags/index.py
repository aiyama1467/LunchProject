from django import template
from menu_proposal.models import Menu
register = template.Library()


@register.filter
def index(indexable, i):
    return indexable[i]


@register.filter
def get_items(indexable, i):
    return indexable[i].items()


@register.filter
def get_menuname(i, j):
    querySet = Menu.objects.filter(pk=j)
    if querySet.first() is None:
        return "null"
    else:
        return querySet.first().menu_name
