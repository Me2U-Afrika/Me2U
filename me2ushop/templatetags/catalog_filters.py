from urllib import request

from django import template
import locale

from categories.models import Category, Department

from stats import stats

register = template.Library()


@register.filter(name='currency')
def currency(value):
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        locale.setlocale(locale.LC_ALL, '')

    loc = locale.localeconv()
    return locale.currency(value, loc['currency_symbol'], grouping=True)


@register.inclusion_tag("tags/product_list.html")
def product_list(products, header_text):
    return {
        'products': products,
        'header_text': header_text
    }


@register.inclusion_tag("department_children.html")
def department_children(department):
    return {
        'object': department,
    }
