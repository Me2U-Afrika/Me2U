from django import template
import locale

from categories.models import Category

register = template.Library()


@register.inclusion_tag("tags/product_list.html")
def product_list(products, header_text):
    return {
        'products': products,
        'header_text': header_text
    }


@register.inclusion_tag("tags/category_list.html")
def category_list(request_path):
    active_categories = Category.objects.filter(is_active=True)
    return {
        'active_categories': active_categories,
        'request_path': request_path
    }
