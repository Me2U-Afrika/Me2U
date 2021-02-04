import tempfile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import user_logged_in
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.dispatch import receiver
from django.template.loader import render_to_string
# from django.utils import simplejson as json
import json

from weasyprint import HTML

from search.search import _prepare_words
from .forms import *
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from categories.models import Category, Department
from marketing.models import *

from .models import *

from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView, FormView
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse, Http404

# from django.contrib.auth.models import User
from django.template import RequestContext

from stats import stats
from stats.models import ProductView

from Me2U.settings import PRODUCTS_PER_ROW, PRODUCTS_PER_PAGE

from django.contrib.auth.mixins import (LoginRequiredMixin, UserPassesTestMixin)
from django import forms as django_forms
from django.db import models as django_models
import django_filters
from django_filters.views import FilterView
from django.views.decorators.cache import cache_page

import random
import string
import stripe
import tagging
from tagging.models import Tag, TaggedItem
from users.models import User

from users.models import Profile

from marketing.models import Slider

from users.models import EmailConfirmed

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


# chat room view
def room(request, order_id):
    return render(request, 'chat_room.html', {'room_name_json': str(order_id)}, )


class DateInput(django_forms.DateInput):
    input_type = 'date'


class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = {
            'user__email': ['icontains'],
            'cart_id__id': ['icontains'],
            'start_date': ['gt', 'lt'],
            'order_date': ['gt', 'lt'],
            'ordered': ['exact']
        }
        filter_overrides = {
            django_models.DateTimeField: {
                'filter_class': django_filters.DateFilter,
                'extra': lambda f: {
                    'widget': DateInput
                }
            }
        }


class OrderView(UserPassesTestMixin, FilterView):
    filterset_class = OrderFilter
    template_name = 'order_filter.html'
    login_url = reverse_lazy("login")

    def test_func(self):
        return self.request.user.is_staff is True


class SellerView(ListView):
    model = Product
    # template_name = 'seller-page.html'
    template_name = 'home/seller_page.html'
    paginate_by = 20

    def get_queryset(self):
        # user = get_object_or_404(User, id=self.kwargs.get('id'))
        brand = get_object_or_404(Brand, id=self.kwargs.get('id'))
        # print('user:', self.kwargs)
        if brand:
            return Product.active.filter(brand_name=brand).order_by('-created_at')

    def get_context_data(self, *, object_list=None, **kwargs):
        super(SellerView, self).get_context_data(**kwargs)

        # user = get_object_or_404(User, id=self.kwargs.get('id'))
        store = get_object_or_404(Brand, id=self.kwargs.get('id'))
        brand = Brand.objects.get(title=store)
        if brand:
            # other brands
            brands = Brand.objects.filter(active=True).exclude(title=store)

            # products = Product.active.filter(seller=user).order_by('-created_at')
            products = Product.active.filter(brand_name=store).order_by('-created_at')
            context = {
                'page_title': str(brand),
                'site_name': 'Me2U|Seller',
                'products': products,
                'brand': brand,
                'brands': brands,

            }

            return context


class HomeView(ListView):
    model = Product
    site_name = 'Me2U|Market'
    # template_name = 'trialTemplates/home.html'
    template_name = 'home/home.html'
    paginate_by = 4

    def get_context_data(self, *, object_list=None, **kwargs):
        super(HomeView, self).get_context_data(**kwargs)

        from utils import context_processors
        context = {}

        active_products = Product.active.all()
        bestselling = active_products.filter(is_bestseller=True)
        bestrated = active_products.filter(is_bestrated=True)
        categories = context_processors.me2u(self.request)['active_departments']
        if categories:
            rand_department = random.choices(categories, k=3)
            context.update({
                'rand_department_1': rand_department[0],
                'rand_department_2': rand_department[1],
                'rand_department_3': rand_department[2]
            })

        if bestselling:
            context.update({'bestselling': bestselling})

        if bestrated:
            context.update({'bestrated': bestrated})

        bestselling_banner = Banner.objects.bestselling()
        # print('banner:', bestselling_banner)

        if bestselling_banner:
            context.update({'best_seller_banner': bestselling_banner[0]})

        featuring = active_products.filter(is_featured=True)
        if featuring:
            # print('featuring:', featuring)
            context.update({'featuring': featuring})

        marketing_messages = MarketingMessage.objects.get_featured_item()
        if marketing_messages:
            # print('markting mss:', marketing_messages)
            context.update({'marketing_messages': marketing_messages})

        recent_products = active_products.order_by('-created_at')
        if recent_products:
            print('recent_products:', recent_products)
            context.update({'recent_products': recent_products[:20]})

        # recently_viewed = stats.get_recently_viewed(self.request)
        # if recently_viewed:
        #     context.update({'recently_viewed': recently_viewed})

        search_recored = stats.recommended_from_search(self.request)
        # print('search:', search_recored)

        if search_recored:
            context.update({'search_recomms': search_recored})

        sliders = Slider.objects.featured()
        if sliders:
            context.update({'sliders': sliders, })

        # trends = Trend.objects.all()
        trend_info = TrendInfo.objects.all()
        # print('trend_info:', trend_info)
        if trend_info:
            context.update({'trend_info': trend_info})

        # if trends:
        #     # print('trending:', trending_banner)
        #     context.update({'trends': trends})

        top_banner = Banner.objects.filter(top_display=True)

        if top_banner:
            # print('top banner:', top_banner)
            context.update({'top_banner': top_banner[0]})

        view_recommendation = stats.recommended_from_views(self.request)
        if view_recommendation:
            context.update({'view_recomms': view_recommendation})

        return context


# class HomeView(ListView):
#     model = Product
#     site_name = 'Me2U|Market'
#     template_name = 'home-page.html'
#     # template_name = 'home/home.html'
#     paginate_by = 4
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         super(HomeView, self).get_context_data(**kwargs)
#
#         context = {}
#
#         search_recored = stats.recommended_from_search(self.request)
#         featuring = Product.featured.all()
#         bestselling = Product.bestseller.all()
#         recently_viewed = stats.get_recently_viewed(self.request)
#         view_recommendation = stats.recommended_from_views(self.request)
#         marketing_messages = MarketingMessage.objects.get_featured_item()
#         departments = Department.active.all()
#         # print('markting mss:', marketing_messages)
#         sliders = Slider.objects.featured()
#         context.update({'sliders': sliders, })
#         context.update({
#             'departments': departments,
#
#                         })
#         if marketing_messages:
#             marketing_message = marketing_messages
#             context.update({'marketing_message': marketing_message, })
#
#         if search_recored:
#             try:
#                 page = int(self.request.GET.get('page', 1))
#
#             except ValueError:
#                 page = 1
#             paginator = Paginator(search_recored, settings.PRODUCTS_PER_PAGE)
#             try:
#                 search_recored = paginator.page(page).object_list
#                 context.update({'search_recs': search_recored,
#                                 'paginator': paginator
#                                 })
#
#             except (InvalidPage, EmptyPage):
#                 results = paginator.page(1).object_list
#                 context.update({'search_recs': results})
#
#         if featuring:
#             try:
#                 page = int(self.request.GET.get('page', 1))
#
#             except ValueError:
#                 page = 1
#             paginator = Paginator(featuring, settings.PRODUCTS_PER_PAGE)
#             try:
#                 featuring = paginator.page(page).object_list
#                 context.update({'featured': featuring,
#                                 'paginator': paginator
#                                 })
#
#             except (InvalidPage, EmptyPage):
#                 results = paginator.page(1).object_list
#                 context.update({'featured': results})
#
#         if recently_viewed:
#
#             # Recently viewed
#             try:
#                 page = int(self.request.GET.get('page', 1))
#
#             except ValueError:
#                 page = 1
#             paginator = Paginator(recently_viewed, 6)
#             try:
#                 view_recently = paginator.page(page).object_list
#                 context.update({'recently_viewed': view_recently,
#                                 'paginator': paginator
#                                 })
#
#             except (InvalidPage, EmptyPage):
#                 results = paginator.page(1).object_list
#                 context.update({'recently_viewed': results})
#
#                 # Recommended
#         if view_recommendation:
#             try:
#                 page = int(self.request.GET.get('page', 1))
#
#             except ValueError:
#                 page = 1
#             paginator = Paginator(view_recommendation, settings.PRODUCTS_PER_PAGE)
#             try:
#                 view_recommendation = paginator.page(page).object_list
#                 context.update({'view_recs': view_recommendation,
#                                 'paginator': paginator
#                                 })
#
#             except (InvalidPage, EmptyPage):
#                 results = paginator.page(1).object_list
#                 context.update({'view_recs': results})
#
#         if bestselling:
#             try:
#                 page = int(self.request.GET.get('page', 1))
#
#             except ValueError:
#                 page = 1
#             paginator = Paginator(bestselling, settings.PRODUCTS_PER_PAGE)
#             try:
#                 bestselling = paginator.page(page).object_list
#                 context.update({'bestseller': bestselling,
#                                 'paginator': paginator
#                                 })
#
#             except (InvalidPage, EmptyPage):
#                 results = paginator.page(1).object_list
#                 context.update({'bestseller': results})
#
#         return context


# def homeView(request):
#     site_name = 'Me2U|Market'
#     # template_name = 'home-page.html'
#     template_name = 'home/home.html'
#
#     search_recored = stats.recommended_from_search(request)
#     # print('search:', search_recored)
#
#     if search_recored:
#         for record in search_recored:
#             search_recs = record
#             # print('search:', search_recs)
#             top_search = search_recored[0]
#
#     featuring = Product.featured.all()
#     bestselling = Product.bestseller.all()
#     recently_viewed = stats.get_recently_viewed(request)
#     view_recored = stats.recommended_from_views(request)
#     if view_recored:
#         view_recs = view_recored[0:PRODUCTS_PER_ROW]
#
#     if featuring or bestselling:
#         featured = featuring[0:PRODUCTS_PER_ROW]
#         bestseller = bestselling[0:PRODUCTS_PER_ROW]
#         if bestseller:
#             top_bestseller = [bestseller[0]]
#
#     # print('view recs:', view_recs)
#     return render(request, template_name, locals())
#     # model = Product
#     # paginate_by = 8
#     # template_name = 'home-page.html'
#     #
#     # def get_context_data(self, **kwargs):
#     #     context = super(HomeView, self).get_context_data(**kwargs)
#     #     categories = Category.objects.all()
#     #     context['categories'] = categories
#     #
#     #     return context


class ProductListView(ListView):
    model = Product
    # template_name = 'trialTemplates/home.html'
    template_name = 'home/full_catalog.html'
    paginate_by = 4

    def get_context_data(self, *, object_list=None, **kwargs):
        super(ProductListView, self).get_context_data(**kwargs)

        context = {}

        active_products = Product.active.all()
        if active_products:
            context.update({'active_products': active_products})

        return context


# PRODUCT DETAILED CREATE, UPDATE, DELETE VIEWS

class ProductDetailedView(DetailView):
    model = Product
    # template_name = 'home/products_detailed_page.html'
    template_name = 'home/product_detail.html'
    # template_name = 'home/product_page_test.html'
    query_pk_and_slug = False

    def get_context_data(self, **kwargs):
        context = super(ProductDetailedView, self).get_context_data(**kwargs)
        # cart_product_form = CartAddProductForm()
        formset = CartAddFormSet()

        product = Product.objects.filter(title=kwargs['object'])[0]
        pending_item = product.orderitem_set.filter(status=10)

        if product.brand_name:
            brand_id = product.brand_name.id
            # print('brand_id:', brand_id)
            context.update({'brand_id': brand_id})

        product_image = ProductImage.displayed.filter(item=product)

        # print('product_image:', product.productimage_set.all())
        # print('product_image:', product_image)
        from stats import stats

        # recently_viewed = stats.get_recently_viewed(self.request)
        # if recently_viewed:
        #     context.update({'recently_viewed': recently_viewed})

        product_reviews = ProductReview.approved.filter(product=product).order_by('-date')
        # print('productreviews:', product_reviews)

        review_form = ProductReviewForm()

        if self.request.user.is_authenticated:
            try:
                approved = OrderItem.objects.filter(user=self.request.user, ordered=True, item=product)
                context.update({'approved': approved})

            except Exception:
                return 0
        # tags_product =
        context.update({
            'object': product,
            'pending_item': pending_item,
            'review_form': review_form,
            'product_reviews': product_reviews,
            'page_title': str(self.get_object()),
            'formset': formset,
            'product_image': product_image
        })
        from stats import stats

        stats.log_product_view(self.request, product)

        return context

    # def get(self, *args, **kwargs):
    #     from stats import stats
    #     product = Product.objects.filter(slug=kwargs['slug'])[0]
    #
    #     stats.log_product_view(self.request, product)
    #
    #     return render(self.request, template_name='product-page.html')


class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'sellers/product_form.html'

    def get_success_url(self):
        # Assuming there is a ForeignKey from Productattribute to Product in your model
        return reverse_lazy('me2ushop:product_image_create', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super(ProductCreateView, self).get_context_data(**kwargs)

        context.update({

            'page_title': 'Add New Product',
        })
        return context

    def form_valid(self, form):
        form.instance.seller = self.request.user
        obj = form.save(commit=False)
        stock = obj.stock
        brand = Brand.objects.get(user__user=self.request.user)
        if brand:
            obj.brand_name = brand
        if stock > 0:
            obj.is_active = True
        obj.save()
        return super(ProductCreateView, self).form_valid(form)

    def test_func(self):
        if self.request.user.is_active and self.request.user.is_seller:
            return True
        return False


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'sellers/product_form.html'

    def get_context_data(self, **kwargs):
        context = super(ProductUpdateView, self).get_context_data(**kwargs)

        context.update({

            'page_title': 'Update Product',
        })
        return context

    def form_valid(self, form):
        form.instance.seller = self.request.user
        obj = form.save(commit=False)
        stock = obj.stock
        # print('stock:', stock)
        if stock >= 1:
            obj.is_active = True
        else:
            obj.is_active = False

        brand = Brand.objects.get(user__user=self.request.user)
        if brand:
            obj.brand_name = brand

        obj.save()
        return super(ProductUpdateView, self).form_valid(form)

    def test_func(self):
        product_posted = self.get_object()
        if self.request.user == product_posted.brand_name.user.user:
            return True
        return False


class ProductUpdateAdditionalInforView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product

    fields = [
        'additional_information',
        'meta_keywords',
        'meta_description',
    ]
    template_name = 'sellers/product_form.html'

    def get_context_data(self, **kwargs):
        context = super(ProductUpdateAdditionalInforView, self).get_context_data(**kwargs)

        context.update({

            'page_title': 'Additional Info',
        })
        return context

    def form_valid(self, form):
        form.instance.seller = self.request.user
        obj = form.save(commit=False)

        obj.save()
        return super(ProductUpdateAdditionalInforView, self).form_valid(form)

    def test_func(self):
        product_posted = self.get_object()
        if self.request.user == product_posted.brand_name.user.user:
            return True
        return False


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'sellers/product_confirm_delete.html'
    success_url = reverse_lazy('sellers:seller_products')

    def get_context_data(self, **kwargs):
        context = super(ProductDeleteView, self).get_context_data(**kwargs)

        context.update({

            'page_title': 'Delete Product',
        })
        return context

    def test_func(self):
        product_posted = self.get_object()
        if self.request.user == product_posted.brand_name.user.user:
            return True
        return False


# PRODUCT ATTRIBUTES CREATE, UPDATE, DELETE

class ProductAttributesCreateView(LoginRequiredMixin, CreateView):
    model = ProductDetail
    form_class = ProductAttributeCreate
    template_name = 'sellers/product_form.html'

    def get_context_data(self, **kwargs):
        context = super(ProductAttributesCreateView, self).get_context_data(**kwargs)

        context.update({

            'page_title': 'Product attributes',
        })
        return context

    def form_valid(self, form):
        form.instance.seller = self.request.user
        obj = form.save(commit=False)

        obj.save()
        return super(ProductAttributesCreateView, self).form_valid(form)

    # def get_context_data(self, **kwargs):
    #     context = super(ProductAttributesCreateView, self).get_context_data(**kwargs)
    #     context['slug'] = self.kwargs['slug']
    #     return context

    def get_form_kwargs(self):
        kwargs = super(ProductAttributesCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['slug'] = self.kwargs['slug']

        return kwargs

    # def test_func(self):
    #     product_posted = self.get_object()
    #     if self.request.user == product_posted.product.brand_name.user.user:
    #         return True
    #     return False


class ProductAttributeUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductDetail
    fields = '__all__'
    template_name = 'sellers/product_form.html'

    def get_context_data(self, **kwargs):
        context = super(ProductAttributeUpdateView, self).get_context_data(**kwargs)

        context.update({

            'page_title': 'Attribute Update',
        })
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()

        return super(ProductAttributeUpdateView, self).form_valid(form)


class ProductAttributeDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductDetail
    template_name = 'sellers/product_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super(ProductAttributeDeleteView, self).get_context_data(**kwargs)

        context.update({

            'page_title': 'Delete Attribute',
        })
        return context

    def get_success_url(self):
        # Assuming there is a ForeignKey from Productattribute to Product in your model
        product = self.object.product
        return reverse_lazy('me2ushop:product', kwargs={'slug': product.slug})


@login_required
def show_product_image(request, slug):
    # print('person:', request.user)
    product = get_object_or_404(Product, slug=slug)
    # print('product:', product)
    # product_reviews = ProductReview.approved.filter(product=product).order_by('-date')[0:PRODUCTS_PER_ROW]
    # print('productreviews:', product_reviews)
    # review_form = ProductReviewForm()
    product_image = ProductImage.objects.filter(item__brand_name__user__user=request.user, item=product)

    context = {
        'object': product,
        'product_image': product_image,
        'page_title': 'ImageList-' + str(product)
    }

    return render(request, 'sellers/product_images_list.html', context)


# PRODUCT IMAGE CREATE UPDATE DELETE VIEWS

def product_image_create(request, slug):
    product = get_object_or_404(Product, slug=slug)
    # print('slug:', slug)

    product_image = ProductImage.objects.filter(item__brand_name__user__user=request.user, item=product)
    if request.method == 'POST':
        # print('we came to post')
        form = ProductImageCreate(request.POST, request.FILES, instance=request.user)
        # print('form', form)
        if form.is_valid():
            print(form.is_valid())
            # obj = form.save(commit=False)
            in_display = form.cleaned_data.get('in_display')
            image = form.cleaned_data.get('image')
            item = form.cleaned_data.get('item')
            # print('item:', item)
            # print('indisplay', in_display)
            # print('image:', image)

            if product.brand_name.user.user == request.user:

                current_saved_default = ProductImage.displayed.filter(item__brand_name__user__user=request.user,
                                                                      item=product)
                # print('current', current_saved_default)
                if current_saved_default.exists():
                    if in_display:
                        current_saved = current_saved_default[0]
                        current_saved.in_display = False
                        current_saved.save()
                        # print('current', current_saved.default)

                # obj.user = user
                # obj.save()
            # obj.save()
            form.save()
        return redirect('me2ushop:product', slug)
    else:
        form = ProductImageCreate(slug)
        # form.fields['item'].widget.attrs['value'] = product
        context = {
            'object': product,
            'product_image': product_image,
            'form': form,
        }

        return render(request, 'sellers/product_image_form.html', context)


class ProductImageCreateView(LoginRequiredMixin, CreateView):
    model = ProductImage
    template_name = 'sellers/product_image_form.html'
    # fields = ["item", "image", "in_display"]
    form_class = ProductImageCreate

    # success_url = reverse_lazy("sellers:seller_products")

    def get_success_url(self):
        # Assuming there is a ForeignKey from Productattribute to Product in your model
        product = self.object.item
        return reverse_lazy('me2ushop:product', kwargs={'slug': product.slug})

    def get_context_data(self, **kwargs):
        context = super(ProductImageCreateView, self).get_context_data(**kwargs)

        context.update({

            'page_title': 'Image Create',
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(ProductImageCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['slug'] = self.kwargs['slug']
        return kwargs

    def form_valid(self, form):
        # print(form)
        obj = form.save(commit=False)
        print('obj:', obj)
        item = form.cleaned_data.get('item')
        image = form.cleaned_data.get('image')
        # print('item:', item)
        # print('image:', image)
        # print(item.brand_name)
        user = self.request.user
        # print(user)

        default_image = obj.in_display

        if item.brand_name.user.user == self.request.user:

            current_saved_default = ProductImage.displayed.filter(item__brand_name__user__user=user, item=item)
            # print('current', current_saved_default)

            if default_image:
                if current_saved_default.exists():
                    current_saved = current_saved_default[0]
                    current_saved.in_display = False
                    current_saved.save()
                    # print('current', current_saved.default)

            # obj.user = user
            obj.save()
        return super().form_valid(form)
        # return redirect("me2ushop:home")


class ProductImageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ProductImage
    template_name = 'sellers/product_image_update_form.html'
    fields = ["image", "in_display"]

    def get_context_data(self, **kwargs):
        context = super(ProductImageUpdateView, self).get_context_data(**kwargs)

        context.update({

            'page_title': 'Update Image-' + str(self.get_object()) ,
        })
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        # print('obj', obj)

        item = obj.item
        # print('item:', item)
        user = self.request.user
        default_image = obj.in_display
        print('set as default', default_image)

        current_saved_default = ProductImage.displayed.filter(item__brand_name__user__user=user, item=item,
                                                              in_display=True)
        print('current', current_saved_default)

        if default_image:
            if current_saved_default.exists():
                print('we came to change the default image in display')
                current_saved = current_saved_default[0]
                current_saved.in_display = False
                current_saved.save()

        obj.save()
        # print('default', default)

        return super().form_valid(form)

    def test_func(self):
        image_posted = self.get_object()
        print(image_posted)
        if self.request.user == image_posted.item.brand_name.user.user:
            return True
        return False


class ProductImageDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductImage
    template_name = 'sellers/product_image_delete.html'

    # success_url = reverse_lazy("sellers:seller_products")

    def get_context_data(self, **kwargs):
        context = super(ProductImageDeleteView, self).get_context_data(**kwargs)

        context.update({

            'page_title': 'Delete Product',
        })
        return context

    def get_success_url(self):
        # Assuming there is a ForeignKey from Comment to Post in your model
        product = self.object.item

        # check if image delete was in display to set another one on display or create new if none.
        current_saved_default = ProductImage.displayed.filter(item=product, in_display=True).exclude(id=self.object.id)
        print('current', current_saved_default)

        if not current_saved_default.exists():
            print('we came to add picture')
            image = ProductImage.objects.filter(item=product)
            if image:
                image = image[0]
                image.in_display = True
                image.save()

            messages.warning(self.request, 'You have 0 Images, please add a new image')
            return reverse_lazy('me2ushop:product_image_create', kwargs={'slug': product.slug})

        return reverse_lazy('me2ushop:product', kwargs={'slug': product.slug})

    # def get_queryset(self):
    #     return self.model.objects.filter(item__seller=self.request.user)


# PRODUCT ADD TO CART

@login_required
def add_tag(request):
    print("we came to add the tag")
    tags = request.POST.get('tag', '')
    slug = request.POST.get('slug', '')

    if len(tags) > 2:
        product = Product.active.get(slug=slug)
        html = u''
        template = 'tags/tag_link.html'

        for tags in tags.split():
            print('tag_split', tags)
            tags.strip(',')

            print([tags])
            if len(tags) > 2:
                print(tags)
                Tag.objects.add_tag(product, tags)

        for tags in product.tags:
            html += render_to_string(template, {'tag': tags})
            response = json.dumps({'success': 'True', 'html': html})
    else:
        response = json.dumps({'success': 'False'})
    return HttpResponse(response, content_type='Application/javascript, charset=utf8')


def tag_cloud(request, template_name='home/product_tags_cloud.html'):
    product_tags = Tag.objects.cloud_for_model(Product, steps=9, distribution=tagging.utils.LOGARITHMIC,
                                               filters={'is_active': True})
    page_title = 'Product Tag Cloud'
    return render(request, template_name, locals())


def tag(request, tag, template_name='home/product_tag_list.html'):
    products = TaggedItem.objects.get_by_model(Product.active, tag)

    page_title = 'tag'

    return render(request, template_name, locals())


# def show_product_image(request, slug):
#     # print('person:', request.user)
#     product = get_object_or_404(Product, slug=slug)
#     # print('product:', product)
#     # product_reviews = ProductReview.approved.filter(product=product).order_by('-date')[0:PRODUCTS_PER_ROW]
#     # print('productreviews:', product_reviews)
#     # review_form = ProductReviewForm()
#     product_image = ProductImage.objects.filter(item__seller=request.user, item=product)
#
#     context = {
#         'object': product,
#         'product_image': product_image
#     }
#
#     return render(request, 'product_images_list.html', context)


@login_required
def add_review(request):
    # print('request sent:', request)
    form = ProductReviewForm(request.POST)
    # print('form_data:', form)
    if form.is_valid():
        review = form.save(commit=False)

        slug = request.POST.get('slug')
        country = request.POST.get('country')
        # print('slug:', slug)
        product = Product.active.get(slug=slug)
        # ordered_by_user = Order.objects.filter(user=request.user, ordered=True)
        review.user = request.user
        # print('user:', review.user)
        review.product = product
        review.country = country
        # review.ordered_by_user = ordered_by_user
        review.save()
        # print('reviewed_form:', review)

        template = "tags/product_review.html"
        html = render_to_string(template, {'review': review})
        response = json.dumps({'success': 'True', 'html': html})
        # print('response:', response)

    else:
        html = form.errors.as_ul()
        response = json.dumps({'success': 'False', 'html': html})

    return HttpResponse(response, content_type='application/javascript; charset=utf-8')


def cart_basket(request):
    if request.method == "POST":
        print(request.POST)
        formset = CartAddFormSet(request.POST)
        if formset.is_valid():
            formset.save()
        else:
            formset = CartAddFormSet(instance=request)

        return render(request, "product-page.html", {"formset": formset})


def add_cart(request, slug):
    print('in add_cart')
    # print(request.cart)
    # print(request.cart.id)
    item = get_object_or_404(Product, slug=slug)
    stats.log_product_view(request, item)

    cart = request.cart
    if not request.cart:
        if request.user.is_authenticated:
            user = request.user
            order_date = timezone.now()
            carts = Order.objects.filter(user=user, ordered=False)
            if carts.exists():
                cart = carts[0]
            else:
                cart = Order.objects.create(user=user, order_date=order_date)
        else:
            user = None
            order_date = timezone.now()
            cart = Order.objects.create(user=user, order_date=order_date)

        request.session['cart_id'] = cart.id
    if request.method == "POST":
        print('we came to post')
        form = CartAddFormSet(request.POST or None)
        if form.is_valid():
            try:
                # Get quantity from useronline
                quantity = form.cleaned_data.get('quantity')
                print("qty:", quantity)
                item = get_object_or_404(Product, slug=slug)
                print("item we found:", item)

                order_item, created = OrderItem.objects.get_or_create(
                    customer_order=cart,
                    item=item,
                    ordered=False
                )
                # print("order_item:", order_item)
                # print("created:", created)
                # print("order id:", order_item.customer_order)
                status = StatusCode.objects.get(short_name=10)
                # print('status:', status)
                order_item.status_code = status
                order_item.save()
                # print(order_item.status_code)

                order_query_set = Order.objects.filter(id=cart.id, ordered=False)
                print("cart_id found:", order_query_set)

                if order_query_set.exists():
                    order = order_query_set[0]
                    # print('order user:', order)

                    # check if the order item is in the order
                    if order.items.filter(item__slug=item.slug).exists():
                        if quantity > 1:
                            order_item.quantity = quantity
                        else:
                            order_item.quantity = 1
                        # print('updated item:', order_item)
                        # print('cartid:', cart_id)
                        if request.user.is_authenticated:
                            order_item.user = request.user

                        order_item.save()

                        messages.info(request, 'This item quantity was updated.')
                        return redirect("me2ushop:order_summary")
                    else:
                        messages.info(request, 'This item has been added to your cart.')
                        order.items.add(order_item)
                        if quantity > 1:
                            order_item.quantity = quantity
                        else:
                            order_item.quantity = 1

                        if request.user.is_authenticated:
                            order_item.user = request.user

                        order_item.save()
                        print(order_item.quantity)
                        return redirect("me2ushop:order_summary")
            except Exception:
                messages.info(request, 'ERROR.')
                return redirect("me2ushop:product", slug=slug)
    else:
        print("user adding qty without form")
        # user is logged in but not using form to add quantity
        try:
            item = get_object_or_404(Product, slug=slug)

            order_item, created = OrderItem.objects.get_or_create(
                customer_order=cart,
                item=item,
                ordered=False
            )
            # print("order_item:", order_item)
            # print("created:", created)
            status = StatusCode.objects.get(short_name=10)
            # print('status:', status)
            order_item.status_code = status
            order_item.save()
            # print(order_item.status_code)

            order_query_set = Order.objects.filter(id=cart.id, ordered=False)
            # print("cart_id found:", order_query_set)

            if order_query_set.exists():
                order = order_query_set[0]
                # print('order user:', order)

                # check if the order item is in the order
                if order.items.filter(item__slug=item.slug).exists():
                    order_item.quantity += 1
                    # print('updated item:', order_item)
                    # print('cartid:', cart_id)
                    if request.user.is_authenticated:
                        order_item.user = request.user
                    order_item.save()
                    messages.info(request, 'This item quantity was updated.')
                    return redirect("me2ushop:order_summary")
                else:
                    messages.info(request, 'This item has been added to your cart.')
                    order.items.add(order_item)
                    order_item.quantity = 1

                    if request.user.is_authenticated:
                        order_item.user = request.user

                    order_item.save()
                    # print(order_item.quantity)
                    return redirect("me2ushop:order_summary")
        except Exception:
            messages.info(request, 'ERROR.')
            return redirect("me2ushop:product", slug=slug)

    # if request.user.is_authenticated:
    #     # print('checking out this function')
    #     if request.method == "POST":
    #         form = CartAddFormSet(request.POST or None)
    #         if form.is_valid():
    #             # print('form:', form.is_valid())
    #             try:
    #                 # Get quantity from useronline
    #                 quantity = form.cleaned_data.get('quantity')
    #                 # print("qty:", quantity)
    #                 item = get_object_or_404(Product, slug=slug)
    #                 # print("item:", item)
    #
    #                 order_item, created = OrderItem.objects.get_or_create(
    #                     item=item,
    #                     user=request.user,
    #                     ordered=False
    #                 )
    #                 # print("order_item:", order_item)
    #                 # print("created:", created)
    #
    #                 order_query_set = Order.objects.filter(user=request.user, ordered=False)
    #                 # print("user:", order_query_set)
    #
    #                 # This code returns the user who ordered an item
    #                 if order_query_set.exists():
    #                     order = order_query_set[0]
    #                     # print('order user:', order)
    #
    #                     # check if the order item is in the order
    #                     if order.items.filter(item__slug=item.slug).exists():
    #                         if quantity > 1:
    #                             order_item.quantity = quantity
    #                         else:
    #                             order_item.quantity += 1
    #                         # print('updated item:', order_item)
    #                         # print('cartid:', cart_id)
    #                         order_item.save()
    #                         # print(order.cart_id)
    #
    #                         messages.info(request, 'This item quantity was updated.')
    #                         return redirect("me2ushop:order_summary")
    #                     else:
    #                         messages.info(request, 'This item has been added to your cart.')
    #                         order.items.add(order_item)
    #                         # order.items.add =order_item
    #                         if quantity > 1:
    #
    #                             order_item.quantity = quantity
    #                         else:
    #                             order_item.quantity = 1
    #                         order_item.save()
    #                         return redirect("me2ushop:order_summary")
    #                 else:
    #                     # print("order not in cart")
    #                     order_date = timezone.now()
    #                     order = Order.objects.create(user=request.user, order_date=order_date)
    #                     order.items.add(order_item)
    #                     if quantity > 1:
    #                         order_item.quantity = quantity
    #                     else:
    #                         order_item.quantity = 1
    #
    #                     order_item.save()
    #                     messages.info(request, 'This item has been added to your cart.')
    #                     return redirect("me2ushop:order_summary")
    #
    #             except Exception:
    #                 messages.warning(request, 'error:')
    #                 # add_cart_product(request, slug)
    #                 return redirect("me2ushop:product", slug=slug)
    #
    #         messages.info(request, 'Invalid form')
    #         return redirect("me2ushop:product", slug=slug)
    #     else:
    #         # print("user logged in adding qty without form")
    #         # user is logged in but not using form to add quantity
    #         try:
    #             item = get_object_or_404(Product, slug=slug)
    #             # print('item:', item)
    #
    #             order_item, created = OrderItem.objects.get_or_create(
    #                 item=item,
    #                 user=request.user,
    #                 ordered=False
    #             )
    #             # print('order_item returned', order_item)
    #             order_query_set = Order.objects.filter(user=request.user, ordered=False)
    #             # print('qs:', order_query_set)
    #
    #             # This code returns the user who ordered an item
    #             if order_query_set.exists():
    #                 order = order_query_set[0]
    #
    #                 # check if the order item is in the order
    #                 if order.items.filter(item__slug=item.slug).exists():
    #                     order_item.quantity += 1
    #                     order_item.save()
    #                     messages.info(request, 'This item quantity was updated.')
    #                     return redirect("me2ushop:order_summary")
    #                 else:
    #                     messages.info(request, 'This item has been added to your cart.')
    #                     order.items.add(order_item)
    #                     order_item.quantity = 1
    #                     order_item.save()
    #                     return redirect("me2ushop:order_summary")
    #             else:
    #                 print("order not in cart")
    #                 order_date = timezone.now()
    #                 # print('cart_id', cart_id)
    #                 order = Order.objects.create(user=request.user, order_date=order_date)
    #                 # print('order:', order)
    #                 order.items.add(order_item)
    #                 order_item.quantity = 1
    #                 order_item.save()
    #                 messages.info(request, 'This item has been added to your cart.')
    #                 return redirect("me2ushop:order_summary")
    #
    #         except Exception:
    #             messages.warning(request, 'error:')
    #             return redirect("me2ushop:product", slug=slug)
    # else:
    #     print('user is anonymous')
    #     if request.method == "POST":
    #         form = CartAddFormSet(request.POST or None)
    #         if form.is_valid():
    #             try:
    #                 # Get quantity from useronline
    #                 quantity = form.cleaned_data.get('quantity')
    #                 print("qty:", quantity)
    #                 item = get_object_or_404(Product, slug=slug)
    #                 print("item we found:", item)
    #                 cart = request.cart
    #                 print(cart)
    #                 if not request.cart:
    #                     print('true')
    #                     if request.user.is_authenticated:
    #                         user = request.user
    #                     else:
    #                         user = None
    #
    #                     order_date = timezone.now()
    #                     cart = Order.objects.create(user=user, order_date=order_date)
    #                     print('cart::', cart)
    #                     print('cart Idz:', cart.id)
    #                     request.session['cart_id'] = cart.id
    #
    #                 order_item, created = OrderItem.objects.get_or_create(
    #                     order=cart,
    #                     item=item,
    #                     ordered=False
    #                     )
    #                 print("order_item:", order_item)
    #                 print("created:", created)
    #
    #                 order_query_set = Order.objects.filter(id=cart.id)
    #                 print("cart_id found:", order_query_set)
    #
    #                 if order_query_set.exists():
    #                     order = order_query_set[0]
    #                     # print('order user:', order)
    #
    #                     # check if the order item is in the order
    #                     if order.items.filter(item__slug=item.slug).exists():
    #                         if quantity > 1:
    #                             order_item.quantity = quantity
    #                         else:
    #                             order_item.quantity = 1
    #                         print('updated item:', order_item)
    #                         # print('cartid:', cart_id)
    #                         order_item.save()
    #
    #                         messages.info(request, 'This item quantity was updated.')
    #                         return redirect("me2ushop:home")
    #                     else:
    #                         messages.info(request, 'This item has been added to your cart.')
    #                         order.items.add(order_item)
    #                         if quantity > 1:
    #                             order_item.quantity = quantity
    #                         else:
    #                             order_item.quantity = 1
    #                         order_item.save()
    #                         print(order_item.quantity)
    #                         return redirect("me2ushop:home")
    #
    #
    #
    #
    #
    #
    #
    #                 # if request.cart_id:
    #                 #     cart_id = request.cart_id
    #                 #
    #                 #     order_item, created = OrderItem.objects.get_or_create(
    #                 #         item=item,
    #                 #         cart_id=cart_id,
    #                 #         ordered=False
    #                 #     )
    #                 #     print("order_item:", order_item)
    #                 #     print("created:", created)
    #                 #
    #                 #     # if not created:
    #                 #     #     order_item.quantity += 1
    #                 #     #     order_item.save()
    #                 #     #     return redirect("me2ushop:order_summary")
    #                 #
    #                 #     order_query_set = Order.objects.filter(cart_id=cart_id)
    #                 #     # print("cart_id found:", order_query_set)
    #                 #
    #                 #     # This code returns the user who ordered an item
    #                 #     if order_query_set.exists():
    #                 #         order = order_query_set[0]
    #                 #         # print('order user:', order)
    #                 #
    #                 #         # check if the order item is in the order
    #                 #         if order.items.filter(item__slug=item.slug).exists():
    #                 #             if quantity > 1:
    #                 #                 order_item.quantity = quantity
    #                 #             else:
    #                 #                 order_item.quantity = 1
    #                 #             # print('updated item:', order_item)
    #                 #             # print('cartid:', cart_id)
    #                 #             order_item.save()
    #                 #
    #                 #             messages.info(request, 'This item quantity was updated.')
    #                 #             return redirect("me2ushop:order_summary")
    #                 #         else:
    #                 #             messages.info(request, 'This item has been added to your cart.')
    #                 #             order.items.add(order_item)
    #                 #             if quantity > 1:
    #                 #                 order_item.quantity = quantity
    #                 #             else:
    #                 #                 order_item.quantity = 1
    #                 #             order_item.save()
    #                 #             return redirect("me2ushop:order_summary")
    #                 #     else:
    #                 #         print("order not in cart")
    #                 #         order_date = timezone.now()
    #                 #         order = Order.objects.create(cart_id=cart_id, order_date=order_date)
    #                 #         # print('order:', order)
    #                 #         order.items.add(order_item)
    #                 #         if quantity > 1:
    #                 #             order_item.quantity = quantity
    #                 #         else:
    #                 #             order_item.quantity = 1
    #                 #
    #                 #         order_item.save()
    #                 #         messages.info(request, 'This item has been added to your cart.')
    #                 #         return redirect("me2ushop:order_summary")
    #             except Exception:
    #                 messages.info(request, 'ERROR.')
    #                 return redirect("me2ushop:product", slug=slug)
    #
    #     else:
    #         if request.cart_id:
    #             cart_id = request.cart_id
    #             print('User is adding qty without form')
    #             try:
    #                 item = get_object_or_404(Product, slug=slug)
    #                 # print("item we found:", item)
    #
    #                 order_item, created = OrderItem.objects.get_or_create(
    #                     item=item,
    #                     cart_id=cart_id,
    #                     ordered=False
    #                 )
    #                 # print("order_item:", order_item)
    #
    #                 order_query_set = Order.objects.filter(cart_id=cart_id, ordered=False)
    #                 # print("cart_id found:", order_query_set)
    #
    #                 # This code returns the user who ordered an item
    #                 if order_query_set.exists():
    #                     order = order_query_set[0]
    #                     # print('order user:', order)
    #
    #                     # check if the order item is in the order
    #                     if order.items.filter(item__slug=item.slug).exists():
    #                         if order_item.quantity >= 1:
    #                             order_item.quantity += 1
    #                         else:
    #                             order_item.quantity = 1
    #                         # print('updated item:', order_item)
    #                         # print('cartid:', cart_id)
    #                         order_item.save()
    #
    #                         messages.info(request, 'This item quantity was updated.')
    #                         return redirect("me2ushop:order_summary")
    #                     else:
    #                         messages.info(request, 'This item has been added to your cart.')
    #                         order.items.add(order_item)
    #                         order_item.quantity = 1
    #                         order_item.save()
    #                         return redirect("me2ushop:order_summary")
    #                 else:
    #                     print("order not in cart")
    #                     order_date = timezone.now()
    #                     order = Order.objects.create(cart_id=cart_id, order_date=order_date)
    #                     print('order:', order)
    #                     order.items.add(order_item)
    #                     order_item.quantity = 1
    #                     order_item.save()
    #                     messages.info(request, 'This item has been added to your cart.')
    #                     return redirect("me2ushop:order_summary")
    #
    #             except Exception:
    #                 messages.warning(request, 'error:')
    #                 return redirect("me2ushop:product", slug=slug)
    #
    #     messages.warning(request, "We unable to add item for some reason")
    #     return redirect("me2ushop:product", slug=slug)


@login_required()
def add_wishlist(request, slug):
    print('in add_wishlist')

    item = get_object_or_404(Product, slug=slug)
    print('item to add to wishlist:', item)

    wish_item, created = WishList.objects.get_or_create(
        product=item,
        user=request.user,
    )
    print('wish_item:', wish_item)
    if created:
        print('we came to create wish')
        wish_item.save()
    else:
        wish_item.delete()

    return redirect("me2ushop:wish_list")


class WishListView(LoginRequiredMixin, ListView):
    model = WishList
    template_name = 'home/wish_list.html'
    paginate_by = 20

    def get_context_data(self, *, object_list=None, **kwargs):
        super(WishListView, self).get_context_data(**kwargs)

        wishlist = WishList.objects.filter(user=self.request.user)

        if wishlist.exists():
            print('wishlist:', wishlist)
        page_title = 'MyWishList'

        context = {
            'page_title': page_title,
        }

        return context


@receiver(user_logged_in)
def merge_cart(sender, user, request, **kwargs):
    cart = getattr(request, 'cart', None)
    print("we came here to merge")
    # print('user merge:', user)
    # print('cart:', cart)
    # print('cart:', request.cart)

    qs = Order.objects.filter(user=user, ordered=False)

    if cart:
        cart_id = cart
        if qs.exists():
            # print("before:", request.cart.id)
            order = qs[0]
            if cart_id.id != order.id:
                # order = Order.objects.filter(id=cart_id.id, ordered=False)
                # print(order)
                order_items = OrderItem.objects.filter(order=cart_id, ordered=False)

                print('order_items:', order_items)

                for order_item in order_items:
                    if order_item.user is None:
                        # print('item_cart_id:', order_item.cart_id)
                        quantity = order_item.quantity

                        # Get product instances for each
                        product = Product.active.all()
                        item = get_object_or_404(product, slug=order_item.item.slug)

                        # Delete and create a new instance of the product
                        order_item.delete()
                        order_anonymous_delete = Order.objects.filter(id=cart_id.id, ordered=False)
                        # # print("anonymous_id:", order_anonymous_delete)
                        order_anonymous_delete.delete()
                        # # print("anonymous_id:", order_anonymous_delete)

                        # # Add new product being ordered to database
                        order_item, created = OrderItem.objects.get_or_create(
                            item=item,
                            user=user,
                            ordered=False
                        )
                        # print('created item:', created)

                        if qs[0].items.filter(item__slug=item.slug).exists():
                            if quantity > 1:
                                order_item.quantity = quantity
                            else:
                                order_item.quantity += quantity
                            # print('order saved:', order_item)
                            order_item.save()
                        else:
                            qs[0].items.add(order_item)
                            order_item.quantity = quantity
                            qs[0].save()
                        # print('order saved:', order_item)
                        order_item.save()
                    request.session['cart_id'] = qs[0].id
        else:
            print('qs does not exist')
            order_items = OrderItem.objects.filter(order=cart_id, ordered=False)

            print('order_items:', order_items)

            for order_item in order_items:
                print('order user:', order_item.user)
                if order_item.user is None:
                    # print('item_cart_id:', order_item.cart_id)
                    quantity = order_item.quantity

                    # Get product instances for each
                    product = Product.active.all()
                    item = get_object_or_404(product, slug=order_item.item.slug)

                    # Delete and create a new instance of the product
                    order_item.delete()
                    order_anonymous_delete = Order.objects.filter(id=cart_id.id, ordered=False)
                    # # print("anonymous_id:", order_anonymous_delete)
                    order_anonymous_delete.delete()
                    # # print("anonymous_id:", order_anonymous_delete)

                    # # Add new product being ordered to database
                    order_item, created = OrderItem.objects.get_or_create(
                        item=item,
                        user=user,
                        ordered=False
                    )
                    # print('orderItem created:', order_item)

                    order_date = timezone.now()
                    order = Order.objects.create(user=user, order_date=order_date)
                    order.items.add(order_item)
                    order_item.quantity = quantity
                    order_item.save()
                    order.save()
                    request.session['cart_id'] = order.id
    elif qs.exists():
        request.session['cart_id'] = qs[0].id


def remove_cart(request, slug):
    print('in remove cart:', request.scope.get('headers'))
    try:
        # Authenticated user
        if request.user.is_authenticated:
            item = get_object_or_404(Product, slug=slug)

            order_query_set = Order.objects.filter(
                user=request.user,
                ordered=False)

            if order_query_set.exists():
                order = order_query_set[0]
                #         check if the order item is in the order
                if order.items.filter(item__slug=item.slug).exists():
                    order_item = OrderItem.objects.filter(
                        item=item,
                        user=request.user,
                        ordered=False
                    )[0]
                    # while order_item.quantity > 0:
                    #     order_item.quantity -= 1
                    #
                    #     if order_item.quantity == 0:
                    order.items.remove(order_item)
                    messages.info(request, 'This item was removed from your cart.')
                    order_item.delete()
                    print(order.total_items())
                    if order.total_items() == 0:
                        order.delete()
                    return redirect("me2ushop:product", slug=slug)
                return redirect("me2ushop:product", slug=slug)

            else:
                # add message saying no order for user
                messages.info(request, 'This item is not in your cart.')
                return redirect("me2ushop:product", slug=slug)

        else:
            # user is anonymous
            if request.cart:
                cart_id = request.cart.id

                item = get_object_or_404(Product, slug=slug)

                order_query_set = Order.objects.filter(
                    id=cart_id,
                    ordered=False)

                if order_query_set.exists():
                    order = order_query_set[0]
                    #         check if the order item is in the order
                    if order.items.filter(item__slug=item.slug).exists():
                        order_item = OrderItem.objects.filter(
                            item=item,
                            order=request.cart,
                            ordered=False
                        )[0]

                        order.items.remove(order_item)
                        messages.info(request, 'This item was removed from your cart.')
                        order_item.delete()
                        print(order.total_items())
                        if order.total_items() == 0:
                            order.delete()
                        return redirect("me2ushop:product", slug=slug)

    except Exception:
        messages.info(request, 'You do not have an active order.')
        return redirect("me2ushop:product", slug=slug)


def remove_single_item_cart(request, slug):
    if request.user.is_authenticated:
        item = get_object_or_404(Product, slug=slug)

        order_query_set = Order.objects.filter(
            user=request.user,
            ordered=False)

        if order_query_set.exists():
            order = order_query_set[0]

            #         check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]
                # print('order_item:', order_item)

                if order_item.quantity >= 1:
                    order_item.quantity -= 1
                    order_item.save()
                    messages.info(request, 'This item quantity has been reduced.')
                    # redirect("me2ushop:order_summary")

                    if order_item.quantity == 0:
                        remove_cart(request, slug)
                        messages.info(request, 'This item has been deleted from your cart.')
                        return redirect("me2ushop:product", slug=slug)

                return redirect("me2ushop:order_summary")

        return redirect("me2ushop:product", slug=slug)
    else:
        item = get_object_or_404(Product, slug=slug)
        if request.cart:
            cart_id = request.cart.id

            order_query_set = Order.objects.filter(
                id=cart_id,
                ordered=False
            )
            # print('order_qs:', order_query_set[0])

            if order_query_set.exists():
                order = order_query_set[0]

                # check if the order item is in the order
                if order.items.filter(item__slug=item.slug).exists():
                    order_item = OrderItem.objects.filter(
                        item=item,
                        order=cart_id,
                        ordered=False
                    )[0]
                    # print('order_item:', order_item)

                    if order_item.quantity > 1:
                        order_item.quantity -= 1
                        order_item.save()
                        messages.info(request, 'This item quantity has been reduced.')
                    else:
                        remove_cart(request, slug)
                        messages.info(request, 'This item has been deleted from your cart.')
                        return redirect("me2ushop:product", slug=slug)

                    return redirect("me2ushop:order_summary")

            return redirect("me2ushop:product", slug=slug)


class Order_summary_view(View):
    def get(self, *args, **kwargs):
        try:
            if self.request.user.is_authenticated:

                order = Order.objects.get(user=self.request.user, ordered=False)

                context = {
                    'object': order,
                    'page_title': 'Order Summary'
                }
                return render(self.request, 'home/order_summary.html', context)

            else:
                print('anonymous checkout')
                if self.request.cart:
                    cart_id = self.request.cart.id

                    order = Order.objects.get(id=cart_id, ordered=False)
                    print(order)

                    context = {
                        'object': order,
                    }
                    return render(self.request, 'home/order_summary.html', context)
            return render(self.request, 'home/order_summary.html')
        except ObjectDoesNotExist:
            messages.error(self.request, "YOU DO NOT HAVE ANY ACTIVE ORDER")
            return redirect("me2ushop:home")


class WishList_Summary(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            try:
                wish_list = WishList.objects.filter(user=self.request.user)
                page_title = str(str(self.request.user.username) + '\'s WishList')
                return render(self.request, 'home/wish_list.html', locals())

            except ObjectDoesNotExist:
                messages.error(self.request, "YOU DO NOT HAVE ANY ACTIVE WISH")
                return redirect("me2ushop:home")
        else:
            return redirect("login")


import logging

logger = logging.getLogger(__name__)


def create_order(cart_id, billing_address, shipping_address):
    order = Order.objects.get(id=cart_id.id)
    print(order)
    logger.info(
        "Creating order"
    )
    order.name = shipping_address.name
    order.phone = shipping_address.phone
    order.email = shipping_address.email
    order.shipping_address1 = shipping_address.street_address
    order.shipping_address2 = shipping_address.apartment_address
    order.shipping_zip_code = shipping_address.zip
    order.shipping_country = shipping_address.country

    order.billing_address1 = billing_address.street_address
    order.billing_address2 = billing_address.apartment_address
    order.billing_zip_code = billing_address.zip
    order.billing_country = billing_address.country
    order.save()


class AddressSelectionView(LoginRequiredMixin, FormView):
    template_name = "home/address_selection.html"
    form_class = AddressSelectionForm
    success_url = reverse_lazy('me2ushop:checkout')

    def get_form_kwargs(self):
        kwargs = super(AddressSelectionView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        billing_address = form.cleaned_data['billing_address']
        shipping_address = form.cleaned_data['shipping_address']
        cart = self.request.cart
        payment_option = form.cleaned_data.get('payment_option')

        # print(cart)
        create_order(cart, billing_address, shipping_address)

        # print(billing_address, shipping_address)
        # print(billing_address.street_address)
        return super().form_valid(form)


def is_valid_form(values):
    valid = True
    print('value:', values)
    for field in values:
        if field == '':
            print('value:', values)
            valid = False

    return valid


class Checkout_page(View):
    def get(self, *args, **kwargs):
        #     form we made for checkout

        form = CheckoutForm()
        # form_address = AddressSelectionForm(self.request.user)

        try:
            if self.request.user.is_authenticated:

                order = Order.objects.get(user=self.request.user, ordered=False)
                print('order:', order)
                # print('order.biling:', order.billing_address1)

                order_query_set = Order.objects.filter(user=self.request.user, ordered=False)
                # print('order_qs:', order_query_set)

                order_items = order.total_items()

                if order_query_set.exists():
                    if order_items > 0:

                        context = {
                            'form': form,
                            'order': order,
                            'couponform': CouponForm,
                            'DISPLAY_COUPON_FORM': True,
                        }

                        shipping_address_qs = Address.objects.filter(
                            user=self.request.user,
                            address_type='S',
                            default=True
                        )

                        if shipping_address_qs.exists():
                            context.update({'default_shipping_address': shipping_address_qs[0]})

                        billing_address_qs = Address.objects.filter(
                            user=self.request.user,
                            address_type='B',
                            default=True
                        )

                        if billing_address_qs.exists():
                            context.update({'default_billing_address': billing_address_qs[0]})

                        return render(self.request, 'home/checkout_page.html', context)

                    else:
                        messages.info(self.request, "Your Cart is Empty, Continue shopping before checkout ")
                        return redirect("me2ushop:order_summary")
                else:
                    messages.info(self.request, "YOU DO NOT HAVE ANY ACTIVE ORDER")
                    return redirect("me2ushop:home")
            else:
                print('User is anonymous')
                if self.request.cart:
                    cart_id = self.request.cart.id

                    order = Order.objects.get(id=cart_id, ordered=False)
                    print('order:', order)

                    order_query_set = Order.objects.filter(id=cart_id, ordered=False)

                    order_items = order.total_items()

                    if order_query_set.exists():
                        if order_items > 0:
                            context = {
                                'order': order,
                                'form': form,
                                'couponform': CouponForm,
                                'DISPLAY_COUPON_FORM': False,
                            }
                            return render(self.request, 'home/checkout_page.html', context)

                        else:
                            messages.info(self.request, "Your Cart is Empty, Continue shopping before checkout ")
                            return redirect("me2ushop:order_summary")

                return redirect("me2ushop:home")

        except Exception:
            messages.info(self.request, "YOU DO NOT HAVE ANY ACTIVE ORDER")
            return redirect("me2ushop:home")

    def post(self, *args, **kwargs):
        # print('request:', self.request.POST)
        # print('shipping_add:', self.request.POST['shipping_address'])
        form = CheckoutForm(self.request.POST or None)
        # form_address = AddressSelectionForm(self.request.POST or None)
        # print('form_address:', form_address)
        # print(form_address.is_valid())
        try:
            if self.request.user.is_authenticated:
                order = Order.objects.get(user=self.request.user, ordered=False)
                # if form_address.is_valid():
                #     print('true it\'s valid')
                #     use_shipping = form.cleaned_data.get('shipping_address')
                #     use_billing = form.cleaned_data.get('billing_address')
                #     print('shipping:', use_shipping)
                if form.is_valid():
                    print(form.is_valid())
                    # if not order.billing_address1:
                    use_default_shipping = form.cleaned_data.get('use_default_shipping')

                    use_default_billing = form.cleaned_data.get('use_default_billing')
                    payment_option = form.cleaned_data.get('payment_option')

                    if use_default_shipping:

                        shipping_address_qs = Address.objects.filter(
                            user=self.request.user,
                            address_type='S',
                            default=True
                        )

                        if shipping_address_qs.exists():
                            shipping_address = shipping_address_qs[0]
                            # order.shipping_address = shipping_address
                            order.name = shipping_address.name
                            order.phone = shipping_address.phone
                            order.email = shipping_address.email
                            order.shipping_address1 = shipping_address.street_address
                            order.shipping_address2 = shipping_address.apartment_address
                            order.shipping_zip_code = shipping_address.zip
                            order.shipping_country = shipping_address.country
                            order.shipping_city = shipping_address.city
                            order.payment = payment_option
                            order.save()
                            messages.info(self.request, "default shipping address in use!")

                        else:
                            messages.info(self.request, "No default shipping address saved!")
                            return redirect("me2ushop:checkout")

                    else:
                        print('we adding new address')
                        name = form.cleaned_data.get('name')
                        email = form.cleaned_data.get('email')
                        phone = form.cleaned_data.get('phone')
                        city = form.cleaned_data.get('shipping_city')
                        print('city:', city)
                        shipping_address1 = form.cleaned_data.get('shipping_address')
                        shipping_address2 = form.cleaned_data.get('shipping_address2')
                        shipping_country = form.cleaned_data.get('shipping_country')
                        shipping_zip = form.cleaned_data.get('shipping_zip')

                        if is_valid_form(
                                [shipping_address1, shipping_country, shipping_zip, city, name, phone, email]):
                            print('form is valid')

                            shipping_address = Address(
                                user=self.request.user,
                                name=name,
                                email=email,
                                phone=phone,
                                city=city,
                                street_address=shipping_address1,
                                apartment_address=shipping_address2,
                                country=shipping_country,
                                zip=shipping_zip,
                                address_type='S',
                                payment_option=payment_option

                            )
                            print('form is valid print', shipping_address.phone)

                            shipping_address.save()
                            order.name = shipping_address.name
                            order.phone = shipping_address.phone
                            order.email = shipping_address.email
                            order.shipping_address1 = shipping_address.street_address
                            order.shipping_address2 = shipping_address.apartment_address
                            order.shipping_zip_code = shipping_address.zip
                            order.shipping_country = shipping_address.country
                            order.payment = payment_option
                            order.save()

                            set_default_shipping = form.cleaned_data.get('set_default_shipping')
                            if set_default_shipping:
                                # print('default is:', set_default_shipping)
                                shipping_address.default = True
                                shipping_address.save()
                                messages.info(self.request, "Information saved successfully")

                        else:
                            messages.info(self.request, "Please fill in the required fields")

                    # same billing address as shipping
                    same_billing_address = form.cleaned_data.get('same_billing_address')

                    if same_billing_address:
                        print('We were sent here')
                        billing_address = shipping_address
                        billing_address.pk = None
                        billing_address.address_type = 'B'
                        billing_address.default = False
                        billing_address.save()

                        # order.billing_address = billing_address
                        order.billing_address1 = billing_address.street_address
                        order.billing_address2 = billing_address.apartment_address
                        order.billing_zip_code = billing_address.zip
                        order.billing_country = billing_address.country
                        order.billing_city = billing_address.city
                        order.save()

                    elif use_default_billing:

                        billing_address_qs = Address.objects.filter(
                            user=self.request.user,
                            address_type='B',
                            default=True
                        )

                        if billing_address_qs.exists():
                            billing_address = billing_address_qs[0]
                            # order.billing_address = billing_address
                            order.billing_address1 = billing_address.street_address
                            order.billing_address2 = billing_address.apartment_address
                            order.billing_zip_code = billing_address.zip
                            order.billing_country = billing_address.country
                            order.billing_city = billing_address.city
                            order.save()
                            messages.info(self.request, "default billing address under use!")

                        else:
                            messages.info(self.request, "No default billing address saved!")
                            return redirect("me2ushop:checkout")

                    else:

                        billing_address1 = form.cleaned_data.get('billing_address')
                        billing_address2 = form.cleaned_data.get('billing_address2')
                        billing_country = form.cleaned_data.get('billing_country')
                        billing_zip = form.cleaned_data.get('billing_zip')

                        if is_valid_form([billing_address1, billing_country, billing_zip]):

                            billing_address = Address(
                                user=self.request.user,
                                street_address=billing_address1,
                                apartment_address=billing_address2,
                                country=billing_country,
                                zip=billing_zip,
                                address_type='B'
                            )

                            billing_address.save()
                            # order.billing_address = billing_address
                            order.billing_address1 = billing_address.street_address
                            order.billing_address2 = billing_address.apartment_address
                            order.billing_zip_code = billing_address.zip
                            order.billing_country = billing_address.country
                            order.save()

                            # print("new bill address saved.")

                            messages.info(self.request, "New billing address saved!")

                            set_default_billing = form.cleaned_data.get('set_default_billing')

                            if set_default_billing:
                                # print("save billing is set to true.")
                                billing_address.default = True
                                billing_address.save()

                        else:
                            messages.info(self.request, "Please fill in the required BILLING FIELDS")
                            return redirect("me2ushop:checkout")

                    # TODO: add a redirect to the selected payment option
                    if payment_option == 'S':
                        return redirect("me2ushop:payment", payment_option='stripe')
                    elif payment_option == 'P':
                        return redirect("me2ushop:payment", payment_option='paypal')
                    elif payment_option == 'DC':
                        return redirect("me2ushop:payment", payment_option='stripe')
                    elif payment_option == 'M':
                        return redirect("me2ushop:payment", payment_option='mpesa')
                    elif payment_option == 'C':
                        return redirect("me2ushop:payment", payment_option='cash_on_delivery')
                    else:
                        messages.warning(self.request, 'Invalid Payment Option. Select mode of payment to continue')
                        return redirect("me2ushop:checkout")

                messages.warning(self.request, 'Invalid form')
                return redirect("me2ushop:checkout")
            else:
                if self.request.cart:

                    order = Order.objects.get(id=self.request.cart.id, ordered=False)

                    if form.is_valid():
                        print('valid checkout anonymous form')
                        name = form.cleaned_data.get('name')
                        email = form.cleaned_data.get('email')
                        phone = form.cleaned_data.get('phone')
                        city = form.cleaned_data.get('shipping_city')
                        shipping_address1 = form.cleaned_data.get('shipping_address')
                        shipping_address2 = form.cleaned_data.get('shipping_address2')
                        shipping_country = form.cleaned_data.get('shipping_country')
                        shipping_zip = form.cleaned_data.get('shipping_zip')
                        payment_option = form.cleaned_data.get('payment_option')

                        if is_valid_form([shipping_address1, shipping_country, city, shipping_zip, name, phone, email]):
                            print('valid details')
                            shipping_address = Address(
                                # cart_id=self.request.cart_id,
                                name=name,
                                email=email,
                                phone=phone,
                                city=city,
                                street_address=shipping_address1,
                                apartment_address=shipping_address2,
                                country=shipping_country,
                                zip=shipping_zip,
                                address_type='S',
                                payment_option=payment_option
                            )

                            shipping_address.save()
                            # order.shipping_address = shipping_address
                            order.name = shipping_address.name
                            order.phone = shipping_address.phone
                            order.email = shipping_address.email
                            order.shipping_city = shipping_address.city
                            order.shipping_address1 = shipping_address.street_address
                            order.shipping_address2 = shipping_address.apartment_address
                            order.shipping_zip_code = shipping_address.zip
                            order.shipping_country = shipping_address.country
                            order.payment = payment_option
                            order.save()

                        else:
                            messages.info(self.request, "Please fill in the required fields")

                        # same billing address as shipping
                        same_billing_address = form.cleaned_data.get('same_billing_address')

                        if same_billing_address:
                            billing_address = shipping_address
                            billing_address.pk = None
                            billing_address.address_type = 'B'
                            billing_address.default = False
                            billing_address.save()

                            # order.billing_address = billing_address
                            order.billing_address1 = billing_address.street_address
                            order.billing_address2 = billing_address.apartment_address
                            order.billing_zip_code = billing_address.zip
                            order.billing_country = billing_address.country
                            order.billing_city = billing_address.city

                            order.save()

                        else:

                            billing_address1 = form.cleaned_data.get('billing_address')
                            billing_address2 = form.cleaned_data.get('billing_address2')
                            billing_country = form.cleaned_data.get('billing_country')
                            billing_city = form.cleaned_data.get('billing_city')
                            billing_zip = form.cleaned_data.get('billing_zip')

                            if is_valid_form([billing_address1, billing_country, billing_zip]):

                                billing_address = Address(
                                    # cart_id=self.request.cart_id,
                                    street_address=billing_address1,
                                    apartment_address=billing_address2,
                                    country=billing_country,
                                    city=billing_city,
                                    zip=billing_zip,
                                    address_type='B'
                                )

                                billing_address.save()
                                order.billing_address1 = billing_address.street_address
                                order.billing_address2 = billing_address.apartment_address
                                order.billing_zip_code = billing_address.zip
                                order.billing_country = billing_address.country
                                order.billing_city = billing_address.city
                                order.save()

                                # print("new bill address saved.")
                            else:
                                messages.info(self.request, "Please fill in the required BILLING FIELDS")
                                return redirect("me2ushop:checkout")

                        # TODO: add a redirect to the selected payment option
                        if payment_option == 'S':
                            return redirect("me2ushop:payment", payment_option='stripe')
                        elif payment_option == 'P':
                            return redirect("me2ushop:payment", payment_option='paypal')
                        elif payment_option == 'M':
                            return redirect("me2ushop:payment", payment_option='mpesa')
                        elif payment_option == 'C':
                            return redirect("me2ushop:payment", payment_option='cash_on_delivery')
                        else:
                            messages.warning(self.request, 'Invalid Payment Option. Select mode of payment to continue')
                            return redirect("me2ushop:checkout")

                    messages.warning(self.request, 'Invalid form')
                    return redirect("me2ushop:checkout")

        except ObjectDoesNotExist:
            messages.error(self.request, "YOU DO NOT HAVE ANY ACTIVE ORDER!")
            return redirect("me2ushop:home")
        except Exception:
            messages.error(self.request, "Error occured")
            return redirect("me2ushop:checkout")


def get_coupon(request, code):
    try:
        # we take the online provided code and run it through our available coupons in order to determine it's value
        coupon = Coupon.objects.get(code=code)

        if coupon.valid:
            return coupon
        else:
            messages.info(request, 'This coupon is already depleted. Tafuta ingine')
            return redirect('me2ushop:checkout')

    except ObjectDoesNotExist:
        return redirect('me2ushop:checkout')


def add_coupon(request):
    if request.method == "POST":
        form = CouponForm(request.POST or None)
        if form.is_valid():
            try:
                # get the order
                order = Order.objects.get(user=request.user, ordered=False)

                if order.total_items() > 0:

                    code = form.cleaned_data.get('code')

                    coupon_id = get_coupon(request, code)
                    # print('id:', str(coupon_id))
                    if str(coupon_id) == 'FIRST_TIME':
                        # print('yeah true')
                        used_before = Order.objects.filter(user=request.user, coupon=coupon_id)
                        # print('used before:', used_before)
                        if used_before:
                            # print('we in here')
                            messages.warning(request, 'You have already benefited through this offer')
                            return redirect('me2ushop:checkout')
                        else:
                            # print('not used yet')
                            order.coupon = coupon_id
                            order.coupon.valid = False
                            order.coupon.save()
                            messages.success(request,
                                             'Coupon was successful, thank you for joining Me2U Africa. KARIBU')
                            order.save()

                    else:
                        order.coupon = coupon_id
                        order.coupon.valid = False
                        order.coupon.save()
                        messages.success(request,
                                         'Coupon was successful, Asante Kwa kuchagua Me2U Africa. KARIBU')
                        order.save()
                    return redirect('me2ushop:checkout')

                else:
                    messages.info(request, 'You don\'t have an active order')
                    return redirect('me2ushop:order_summary')

            except Exception:
                messages.warning(request, 'Ticket not available or no order provided')
                return redirect('me2ushop:checkout')


class PaymentView(View):

    def get(self, *args, **kwargs):

        try:
            order = None
            if self.request.user.is_authenticated:
                order = Order.objects.get(user=self.request.user, ordered=False)
            elif self.request.cart:
                order = Order.objects.get(id=self.request.cart.id, ordered=False)

            # print('order:', order)
            if order is not None:
                if order.billing_country:
                    context = {
                        'order': order,
                        'DISPLAY_COUPON_FORM': False

                    }
                    if order.payment == 'S':
                        return render(self.request, 'home/payment.html', context)
                    elif order.payment == 'P':
                        return render(self.request, 'home/paypal_payment.html', context)
                    elif order.payment == 'FW':
                        return render(self.request, 'home/flutterwave_payment.html', context)
                    elif order.payment == 'M':
                        return render(self.request, 'home/mpesa_payment.html', context)
                    elif order.payment == 'MO':
                        return render(self.request, 'home/momo_payment.html', context)
                    else:
                        return render(self.request, 'home/payment.html', context)

            else:
                messages.warning(self.request, "Please fill in your valid delivery address prior to payment")
                return redirect("me2ushop:checkout")
        except Exception:
            return redirect("me2ushop:home")

    def post(self, *args, **kwargs):
        # `source` is obtained with Stripe.js; see
        # https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token

        try:

            order = None
            if self.request.user.is_authenticated:
                order = Order.objects.get(user=self.request.user, ordered=False)

            else:
                if self.request.cart:
                    order = Order.objects.get(id=self.request.cart.id, ordered=False)

            form = PaymentForm(self.request.POST)
            # userprofile = UserProfile.objects.get(user=self.request.user)

            if form.is_valid():
                print('valid payment form')
                print('order:', order)
                token = self.request.POST['stripeToken']

                amount = int(order.get_total() * 100)  # get in ksh

                # try:
                charge = stripe.Charge.create(
                    amount=amount,
                    currency="usd",
                    source=token,
                )

                # print(charge)
                # create payment
                payment = StripePayment()
                payment.stripe_charge_id = charge['id']
                print(payment.stripe_charge_id)

                if self.request.user.is_authenticated:
                    payment.user = self.request.user
                else:
                    payment.user = None
                payment.amount = amount
                payment.save()

                order.ordered = True
                print(order.ordered)
                status = StatusCode.objects.get(short_name=20)
                order.status_code = status
                print(order.status_code)
                # Assigning the order a ref code during checkout payment
                order.ref_code = create_ref_code()

                # Changing order_items in cart to ordered
                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.save()
                del self.request.session['cart_id']
                messages.success(self.request, " CONGRATULATIONS YOUR ORDER WAS SUCCESSFUL")
                print(order.id)
                return redirect("me2ushop:checkout-done")
                #
                # except stripe.error.CardError as e:
                #     # Since it's a decline, stripe.error.CardError will be caught
                #     body = e.json_body
                #     err = body.get('error', {})
                #     messages.error(self.request, f"{err.get('message')}")
                #     return redirect("me2ushop:home")
                #
                # except stripe.error.RateLimitError as e:
                #     messages.error(self.request, "Rate Limit Error ")
                #     return redirect("me2ushop:home")
                #
                # except stripe.error.InvalidRequestError as e:
                #     # Invalid parameters were supplied to Stripe's API
                #     messages.error(self.request, "Invalid parameters")
                #     return redirect("me2ushop:home")
                #
                # except stripe.error.AuthenticationError as e:
                #     # Authentication with Stripe's API failed
                #     # (maybe you changed API keys recently)
                #     messages.error(self.request, "Not authenticated")
                #     return redirect("me2ushop:home")
                #
                # except stripe.error.APIConnectionError as e:
                #     # Network communication with Stripe failed
                #     messages.error(self.request, "Network error ")
                #     return redirect("me2ushop:home")
                #
                # except stripe.error.StripeError as e:
                #     # Display a very generic error to the user, and maybe send
                #     # yourself an email
                #     messages.error(self.request,
                #                    "Something went wrong. You were not charged. Please try again or contact us")
                #     return redirect("me2ushop:home")
                #
                # except Exception:
                #     # Something else happened, completely unrelated to Stripe
                #     print("unkown error")
                #     messages.error(self.request,
                #                    "Order recorded,  we have been notified. You will receive a call for order confirmation ")
                #     return redirect("me2ushop:home")

            else:
                messages.error(self.request, "Invalid form ")
                return redirect("me2ushop:home")
        except Exception:
            return redirect("me2ushop:home")


@login_required()
def checkout_done(request):
    # order = Order.objects.get(pk=order_id)
    orders = Order.objects.filter(user=request.user, ordered=True)
    if orders.exists():
        order = orders[0]

        context = {
            'order': order,

        }
        if order.user == request.user:
            return render(request, 'home/checkout_done.html', context)
        else:
            messages.warning(request, "Not Authorized to view this order")
            return redirect('me2ushop:home')
    else:
        messages.warning(request, "No active orders")
        return redirect('me2ushop:home')


def invoice_for_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    # print('order', order)
    if request.GET.get("format") == "pdf":
        html_string = render_to_string("invoice.html", {"order": order})
        html = HTML(string=html_string, base_url=request.build_absolute_uri(), )
        result = html.write_pdf()

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = "inline; filename=invoice.pdf"
        response["Content-Transfer-Encoding"] = "binary"

        with tempfile.NamedTemporaryFile(delete=True) as output:
            output.write(result)
            output.flush()
            output.seek(0)
            binary_pdf = output.read()
            response.write(binary_pdf)
        return response
    return render(request, "invoice.html", {"order": order})


class RefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()

        context = {
            'RefundForm': form
        }
        return render(self.request, "Me2U_home.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')

            # assign refund request to order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                #         record the refund

                refund = RequestRefund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.ref_code = ref_code
                refund.save()

                messages.info(self.request, " Your Request has been recoreded succcessfully.")
                return redirect("me2ushop:home")

            except ObjectDoesNotExist:
                messages.info(self.request,
                              "We were unable to find the order for the refund requested, please call customer care "
                              "toll free number for clarification.")
                messages.info(self.request,
                              "Asante kwa kuchagua mtandao wetu. Samahani tumekosa ombi lako. Tafadhali pigia "
                              "wahuduma wetu kupata usaidizi.")

                return redirect("me2ushop:request_refund")

# def get_cartID(request):
#     # we take the online provided code and run it through our available coupons in order to determine it's value
#     cart_id = CartID.objects.get_or_create(cart_id=_cart_id(request))
#
#     print("cart_id from get method:", cart_id)
#
#     return cart_id
# CART_ID_SESSION_KEY = 'cart_id'
#
#
# def _generate_cart_id():
#     return ''.join(random.choices(string.ascii_lowercase + string.digits, k=50))
#
#
# def _cart_id(request):
#     if request.session.get(CART_ID_SESSION_KEY, '') == '':
#         request.session['CART_ID_SESSION_KEY'] = _generate_cart_id()
#     return request.session['CART_ID_SESSION_KEY']


# def add_cart_product(request, slug):
#     if request.POST or None:
#
#         # add to cart…create the bound form
#         postdata = request.POST.copy()
#
#         # form instance
#         form = ProductAddToCartForm(request, postdata)
#
#         print('form is valid:', form.is_valid())
#         print('form is bound:', form.is_bound)
#
#         # check if posted data is valid
#         if form.is_valid():
#             # add to cart and redirect to cart page
#             print("got to this method")
#
#             cart.add_cart_qty(request)
#
#             print("trynaa get out of it to this method")
#             # if test cookie worked, get rid of it
#             if request.session.test_cookie_worked():
#                 request.session.delete_test_cookie()
#             url = reverse('cart:show_cart')
#             return HttpResponseRedirect(url)
#
#     else:
#         object = get_object_or_404(Product, slug=slug)
#         categories = object.product_categories.all()
#         print("product collected:", object)
#
#         # it’s a GET, create the unbound form. Note request as a kwarg
#         form = ProductAddToCartForm(request=request, label_suffix=':')
#         form.fields['product_slug'].widget.attrs['value'] = slug
#         request.session.set_test_cookie()
#
#         return render(request, 'product-page.html', locals())
# def add_cart_qty(request, slug):
#     if request.method == "POST":
#
#         form = CartAddProductForm(request.POST or None)
#         if form.is_valid():
#
#             try:
#                 # Get quantity from useronline
#                 qty = form.cleaned_data.get('quantity')
#                 print("qty:", qty)
#
#                 # Determine the item and assign quantity provieded by user to their cart.
#                 item = get_object_or_404(Product, slug=slug)
#                 order_item, created = OrderItem.objects.get_or_create(
#                     item=item,
#                     user=request.user,
#                     ordered=False,
#                 )
#
#                 order_query_set = Order.objects.filter(user=request.user, ordered=False)
#                 if order_query_set.exists():
#                     order = order_query_set[0]
#
#                     # check if this specific order item is in the order in order to increment it or update it
#
#                     if order.items.filter(item__slug=item.slug).exists():
#                         order_item.quantity = qty
#                         order_item.save()
#                         messages.info(request, 'This item quantity has been updated.')
#                         return redirect("me2ushop:order_summary")
#                     else:
#                         messages.info(request, 'This item has been added to your cart.')
#                         order.items.add(order_item)
#                         order_item.quantity = qty
#                         order_item.save()
#                         return redirect("me2ushop:order_summary")
#                 else:
#                     order_date = timezone.now()
#                     order = Order.objects.create(user=request.user, order_date=order_date)
#                     order.items.add(order_item)
#                     order_item.quantity = qty
#                     order_item.save()
#                     messages.info(request, 'This item has been added to your cart.')
#                     return redirect("me2ushop:order_summary")
#
#             except Exception:
#                 messages.warning(request, 'no data yet')
#                 return redirect('me2ushop.order_summary')
#
#     messages.warning(request, "Something is a miss here!")
#     return redirect('me2ushop:home')
#
#     # form = CartAddProductForm(request.POST or None)
#     # if form.is_valid():
#     #
#     #     try:
#     #
#     #         # Get quantity from useronline
#     #         qty = form.cleaned_data.get('code')
#     #         print("qty:", qty)
#     #
#     #         # post to our database
#     #         recored_qty = post_cart_qty(request, qty)
#     #         print("recorded_qty:", recored_qty)
#     #
#     #         item = get_object_or_404(Item, slug=slug)
#     #         order_item, created = OrderItem.objects.get_or_create(
#     #             item=item,
#     #             user=request.user,
#     #             ordered=False
#     #         )
#     #         order_query_set = Order.objects.filter(user=request.user, ordered=False)
#     #
#     #         if order_query_set.exists():
#     #             order = order_query_set[0]
#     #
#     #             # check if the order item is in the order
#     #
#     #             if order.items.filter(item__slug=item.slug).exists():
#     #                 order_item.quantity += recored_qty
#     #                 order_item.save()
#     #                 messages.info(request, 'This item quantity was updated.')
#     #                 return redirect("me2ushop:order_summary")
#     #             else:
#     #                 messages.info(request, 'This item has been added to your cart.')
#     #                 order.items.add(order_item)
#     #                 order_item.quantity = recored_qty
#     #                 order_item.save()
#     #                 return redirect("me2ushop:order_summary")
#     #         else:
#     #             order_date = timezone.now()
#     #             order = Order.objects.create(user=request.user, order_date=order_date)
#     #             order.items.add(order_item)
#     #             order_item.quantity = recored_qty
#     #             order_item.save()
#     #             messages.info(request, 'This item has been added to your cart.')
#     #             return redirect("me2ushop:order_summary")
#     #
#     #     except Exception:
#     #         messages.warning(request, 'no data yet')
#     #         return redirect('me2ushop.order_summary')
#     #

# def add_cart_product(request, slug):
#     if request.method == "POST":
#         messages.info(request, "we in the add_cart_product page function, working so far")
#
#         item = get_object_or_404(Item, slug=slug)
#
#         form = CartAddProductForm(request.POST or None)
#         if form.is_valid():
#
#             # Get quantity of the item ordered so far
#             qty = form.cleaned_data.get('quantity')
#             print("qty:", qty)
#
#             new_qty = qty + 3
#             form.quantity = new_qty
#             update = form.cleaned_data.get('quantity')
#             print("update:", update)
#             return redirect("me2ushop:product", slug=slug)
#         return redirect("me2ushop:product", slug=slug)
#     return redirect("me2ushop:product", slug=slug)


#     order_item, created = OrderItem.objects.get_or_create(
#         item=item,
#         ordered=False)
#     order_query_set = Order.objects.filter(ordered=False)
#
#     if order_query_set.exists():
#         order = order_query_set[0]
#
#         # check if the order item is in the order
#         if order.items.filter(item__slug=item.slug).exists():
#             order_item.quantity += 1
#             order_item.save()
#             messages.info(request, 'Your Order quantity was updated.')
#             return redirect("me2ushop:product", slug=slug)
#         else:
#             messages.info(request, 'This item has been added to your cart.')
#             order.items.add(order_item)
#             order_item.quantity = 1
#             order_item.save()
#             return redirect("me2ushop:product", slug=slug)
#
#     else:
#         order_date = timezone.now()
#         order = Order.objects.create(order_date=order_date)
#         order.items.add(order_item)
#         order_item.quantity = 1
#         order_item.save()
#         messages.info(request, 'This item has been added to your cart.')
#         return redirect("me2ushop:product", slug=slug)


# def remove_single_item_cart_product(request, slug):
#     item = get_object_or_404(Item, slug=slug)
#
#     order_query_set = Order.objects.filter(
#         user=request.user,
#         ordered=False)
#
#     if order_query_set.exists():
#         order = order_query_set[0]
#         print('order:', order)
#
#         #         check if the order item is in the order
#         if order.items.filter(item__slug=item.slug).exists():
#             order_item = OrderItem.objects.filter(
#                 item=item,
#                 user=request.user,
#                 ordered=False
#             )[0]
#
#             if order_item.quantity >= 1:
#                 order_item.quantity -= 1
#                 order_item.save()
#                 messages.info(request, 'This item was reduced.')
#
#                 if order_item.quantity == 0:
#                     order.items.remove(order_item)
#                     messages.info(request, 'Note that the item has been removed from your cart.')
#                     return redirect("me2ushop:product", slug=slug)
#         else:
#             messages.info(request, 'You do not have an active order.')
#             return redirect("me2ushop:product", slug=slug)
#     messages.warning(request, 'You need to be logged in')
#     return redirect("me2ushop:product", slug=slug)

#
# def cart_item_count(user):
#     if user.is_authenticated:
#         query_set = Order.objects.filter(user=user, ordered=False)
#         if query_set.exists():
#             return query_set[0].items.count()
#
#     return 0
