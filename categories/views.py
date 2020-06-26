from django.shortcuts import render
from .models import Category
from me2ushop.models import Product
from django.views.generic import ListView, DetailView, View
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect


# from django.template import RequestContext
# from me2ushop.forms import CartAddProductForm
#
#
def categoriesHomePage(request):
    page_title = 'Categories'
    site_name = 'Me2U|Market'
    template_name = 'index.html'
    return render(request, template_name, locals())


class CategoryDetailedView(DetailView):
    model = Category
    paginate_by = 12
    template_name = 'category.html'
    query_pk_and_slug = True

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailedView, self).get_context_data(**kwargs)
        categories = Category.objects.all()
        context['categories'] = categories

        # page_title = c.category_name
        # meta_description = c.meta_description
        # meta_keywords = c.meta_keywords

        return context
