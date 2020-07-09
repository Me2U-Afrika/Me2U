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
        # c = Category.active.all()
        # print('c:', c)
        # category_list = {'c': []}
        # for c in c:
        #     p = c.product_set.all()
        #     for item in p:
        #         if item.made_in_africa:
        #             pass
                    # category = item.product_categories.order_by('category_name').distinct()
                    # print('categories:', category)
                    # african_category = list(set(category))

                    # print('cat:', african_category)

                    # context['category '] = category
                    # return context
                    # print('category:', category)

        # print('category_list:', category_list)



                    # context['c'] = category
                # print('c:', c)

        # page_title = c.category_name
        # meta_description = c.meta_description
        # meta_keywords = c.meta_keywords

        return context


class CategoryDetailedView_africa_made(DetailView):
    model = Category
    paginate_by = 12
    template_name = 'category_africa_made.html'
    query_pk_and_slug = True

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailedView_africa_made, self).get_context_data(**kwargs)
        # categories = Category.active.all()
        # print('all:', categories)
        # made_in_africa = Product.active.all()
        # print('made:', made_in_africa)
        # for category in categories:
        #     products = category.product_set.all()
        #     print('products:', products)
        #
        #     # context['products'] = products
        #
        #     for item in products:
        #         print('item:', item)
        #         if item in made_in_africa:
        #             africa_category = category
        #             print('africa category:', africa_category)

                # if item.made_in_africa:
                #     african_category = category
                #     print('african_category:', category)

        #
        #             context['african_category'] = african_category
        #             print('item:', item)

        return context
