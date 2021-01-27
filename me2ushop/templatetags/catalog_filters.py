from urllib import request

from django import template
from decimal import Decimal
import locale

from categories.models import Category, Department

from stats import stats

register = template.Library()


# @register.filter(name='currency')
# def currency(value):
#     try:
#         locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
#     except:
#         locale.setlocale(locale.LC_ALL, '')
#     if value != '':
#         value = Decimal(value)
#         loc = locale.localeconv()
#         return locale.currency(abs(int(value)), loc['currency_symbol'], grouping=True)
#     return value


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
