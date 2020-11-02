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


@register.inclusion_tag("tags/category_list.html")
def category_list(request_path):
    active_departments = Department.active.all()
    return {
        'departments': active_departments,
        'request_path': request_path
    }


@register.inclusion_tag("tags/department_list.html")
def department_list(request_path):
    active_departments = Department.objects.all().filter(is_active=True)
    return {
        'active_departments': active_departments,
        'request_path': request_path
    }


@register.inclusion_tag("me2ushop/footer.html")
def recently_viewed_list(request_path):
    recently_viewed = stats.get_recently_viewed(request)
    if recently_viewed:
        return {
            'recently_viewed': recently_viewed,
            'request': request
        }


@register.inclusion_tag("department_children.html")
def department_children(department):
    return {
        'object': department,
    }
