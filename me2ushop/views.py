from django.conf import settings
from django.contrib import messages
from django.contrib.auth import user_logged_in
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.dispatch import receiver
from django.template.loader import render_to_string
# from django.utils import simplejson as json
import json
from .forms import *
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from categories.models import Category

from .models import *

from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView, FormView
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse

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

import random
import string
import stripe
import tagging
from tagging.models import Tag, TaggedItem
from users.models import User

from users.models import Profile

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
    site_name = 'Me2U|Seller'
    template_name = 'seller-page.html'
    paginate_by = 8

    def get_queryset(self):
        user = get_object_or_404(User, id=self.kwargs.get('id'))
        print('user:', self.kwargs)

        return Product.active.filter(seller=user).order_by('-created_at')


class HomeView(ListView):
    model = Product
    site_name = 'Me2U|Market'
    template_name = 'home-page.html'
    paginate_by = 4

    def get_context_data(self, *, object_list=None, **kwargs):
        super(HomeView, self).get_context_data(**kwargs)

        context = {}

        search_recored = stats.recommended_from_search(self.request)
        featuring = Product.featured.all()
        bestselling = Product.bestseller.all()
        recently_viewed = stats.get_recently_viewed(self.request)
        view_recommendation = stats.recommended_from_views(self.request)

        if search_recored:
            try:
                page = int(self.request.GET.get('page', 1))

            except ValueError:
                page = 1
            paginator = Paginator(search_recored, settings.PRODUCTS_PER_PAGE)
            try:
                search_recored = paginator.page(page).object_list
                context.update({'search_recs': search_recored,
                                'paginator': paginator
                                })

            except (InvalidPage, EmptyPage):
                results = paginator.page(1).object_list
                context.update({'search_recs': results})

        if featuring:
            try:
                page = int(self.request.GET.get('page', 1))

            except ValueError:
                page = 1
            paginator = Paginator(featuring, settings.PRODUCTS_PER_PAGE)
            try:
                featuring = paginator.page(page).object_list
                context.update({'featured': featuring,
                                'paginator': paginator
                                })

            except (InvalidPage, EmptyPage):
                results = paginator.page(1).object_list
                context.update({'featured': results})

        if recently_viewed:

            # Recently viewed
            try:
                page = int(self.request.GET.get('page', 1))

            except ValueError:
                page = 1
            paginator = Paginator(recently_viewed, 6)
            try:
                view_recently = paginator.page(page).object_list
                context.update({'recently_viewed': view_recently,
                                'paginator': paginator
                                })

            except (InvalidPage, EmptyPage):
                results = paginator.page(1).object_list
                context.update({'recently_viewed': results})

                # Recommended
        if view_recommendation:
            try:
                page = int(self.request.GET.get('page', 1))

            except ValueError:
                page = 1
            paginator = Paginator(view_recommendation, settings.PRODUCTS_PER_PAGE)
            try:
                view_recommendation = paginator.page(page).object_list
                context.update({'view_recs': view_recommendation,
                                'paginator': paginator
                                })

            except (InvalidPage, EmptyPage):
                results = paginator.page(1).object_list
                context.update({'view_recs': results})

        if bestselling:
            try:
                page = int(self.request.GET.get('page', 1))

            except ValueError:
                page = 1
            paginator = Paginator(bestselling, settings.PRODUCTS_PER_PAGE)
            try:
                bestselling = paginator.page(page).object_list
                context.update({'bestseller': bestselling,
                                'paginator': paginator
                                })

            except (InvalidPage, EmptyPage):
                results = paginator.page(1).object_list
                context.update({'bestseller': results})

        return context


def homeView(request):
    site_name = 'Me2U|Market'
    template_name = 'home-page.html'

    search_recored = stats.recommended_from_search(request)
    if search_recored:
        for record in search_recored:
            search_recs = record
            top_search = [search_recs[0]]

    featuring = Product.featured.all()
    bestselling = Product.bestseller.all()[0:PRODUCTS_PER_ROW]
    recently_viewed = stats.get_recently_viewed(request)
    view_recored = stats.recommended_from_views(request)
    if view_recored:
        view_recs = view_recored[0:PRODUCTS_PER_ROW]

    if featuring or bestselling:
        featured = featuring[0:PRODUCTS_PER_ROW]
        bestseller = bestselling[0:PRODUCTS_PER_ROW]
        if bestseller:
            top_bestseller = [bestseller[0]]

    # print('view recs:', view_recs)

    return render(request, template_name, locals())
    # model = Product
    # paginate_by = 8
    # template_name = 'home-page.html'
    #
    # def get_context_data(self, **kwargs):
    #     context = super(HomeView, self).get_context_data(**kwargs)
    #     categories = Category.objects.all()
    #     context['categories'] = categories
    #
    #     return context


class ProductDetailedView(DetailView):
    model = Product
    template_name = 'product-page.html'
    query_pk_and_slug = True

    def get_context_data(self, **kwargs):
        context = super(ProductDetailedView, self).get_context_data(**kwargs)
        # cart_product_form = CartAddProductForm()
        formset = CartAddFormSet()

        product = Product.objects.filter(title=kwargs['object'])[0]
        product_image = ProductImage.displayed.filter(item=product)

        # print('product_image:', product.productimage_set.all())
        # print('product_image:', product_image)

        product_reviews = ProductReview.approved.filter(product=product).order_by('-date')[0:PRODUCTS_PER_ROW]
        # print('productreviews:', product_reviews)

        review_form = ProductReviewForm()

        # if not self.request.cart_id:
        #     return render(self.request, "product-page.html", {"formset": None})
        # formset = ''
        # if self.request.method == "POST":
        #     formset = CartAddFormSet(self.request.POST)
        #     if formset.is_valid():
        #         formset.save()
        #     else:
        #         formset = CartAddFormSet(instance=self.request)
        # # if self.request.cart_id.is_empty():
        # #     return render(self.request, "product-page.html", {"formset": None})
        # return render(self.request, "product-page.html", {"formset": formset})

        # cart_order_id = self.request.cart_order_id
        # # print('cat:', cart_order_id)
        #
        # if not self.request.cart_order_id:
        #     if self.request.user.is_authenticated:
        #         user = self.request.user
        #     else:
        #         user = None
        #     # cart_order_id = Basket.objects.create(user=user)
        #     cart_order_id = Order.objects.create(user=user)
        #
        #     # print('cart_items:', cart_order_id.id)
        #     self.request.session['cart_id'] = cart_order_id.id
        if self.request.user.is_authenticated:
            try:
                approved = OrderItem.objects.filter(user=self.request.user, ordered=True, item=product)
                context.update({'approved': approved})

            except Exception:
                return 0
        # tags_product =
        context.update({
            'object': product,
            'review_form': review_form,
            'product_reviews': product_reviews,
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
    fields = ['title', 'slug', 'brand', 'price', 'discount_price', 'stock', 'made_in_africa', 'description',
              'additional_information',
              'meta_keywords',
              'meta_description',
              'category_choice', 'product_categories']
    template_name = 'product_form.html'

    def form_valid(self, form):
        form.instance.seller = self.request.user
        obj = form.save(commit=False)
        stock = obj.stock
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
    fields = ['title', 'slug', 'brand', 'price', 'discount_price', 'stock', 'made_in_africa', 'description',
              'additional_information',
              'meta_keywords',
              'meta_description',
              'category_choice',
              'product_categories',
              ]
    template_name = 'product_form.html'

    def form_valid(self, form):
        form.instance.seller = self.request.user
        obj = form.save(commit=False)
        stock = obj.stock
        print('stock:', stock)
        if stock >= 1:
            obj.is_active = True
        else:
            obj.is_active = False

        obj.save()
        return super(ProductUpdateView, self).form_valid(form)

    def test_func(self):
        product_posted = self.get_object()
        if self.request.user == product_posted.seller:
            return True
        return False


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = '/me2ushop'

    def test_func(self):
        product_posted = self.get_object()
        if self.request.user == product_posted.seller:
            return True
        return False


def show_product_image(request, slug):
    # print('person:', request.user)
    product = get_object_or_404(Product, slug=slug)
    # print('product:', product)
    # product_reviews = ProductReview.approved.filter(product=product).order_by('-date')[0:PRODUCTS_PER_ROW]
    # print('productreviews:', product_reviews)
    # review_form = ProductReviewForm()
    product_image = ProductImage.objects.filter(item__seller=request.user, item=product)

    context = {
        'object': product,
        'product_image': product_image
    }

    return render(request, 'product_images_list.html', context)


def product_image_create(request, slug):
    product = get_object_or_404(Product, slug=slug)
    print('slug:', slug)

    product_image = ProductImage.objects.filter(item__seller=request.user, item=product)
    if request.method == 'POST':
        form = ProductImageCreate(request.POST or None, request.FILES or None, instance=request.user)
        print('form', form)
        if form.is_valid():
            print(form.is_valid())
            in_display = form.cleaned_data.get('in_display')
            image = form.cleaned_data.get('image')
            print('indisplay', in_display)
            print('image:', image)
            form.save()
        return redirect('me2ushop:product_images', slug)
    else:
        form = ProductImageCreate(slug)
        # form.fields['item'].widget.attrs['value'] = product
        context = {
            'object': product,
            'product_image': product_image,
            'form': form,
        }

        return render(request, 'tags/product_image_create_form.html', context)


# class ProductImageCreateView(LoginRequiredMixin, CreateView):
#     model = ProductImage
#     template_name = 'tags/product_images_form.html'
#     fields = ["image", "in_display"]
#     # form_class = ProductImageCreate
#
#     # success_url = redirect("me2ushop:product_images")
#
#     # def get_context_data(self, slug, **kwargs):
#     #     kwargs['item'] = Product.objects.filter(slug=slug)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         self.object = self.get_object()
#         item = Product.objects.get(slug=self.object.slug)
#         context['item'] = item
#         return context
#
#     def form_valid(self, form):
#         obj = form.save(commit=False)
#         print('obj:', obj)
#         slug = self.get_object().slug
#         obj.item = get_object_or_404(Product, slug=slug)
#         item = obj.item
#         print('item:', item)
#         print(item.seller)
#         user = self.request.user
#         print(user)
#
#         default_image = obj.in_display
#
#         if item.seller == user:
#
#             current_saved_default = ProductImage.displayed.filter(item__seller=user, item=item)
#             print('current', current_saved_default)
#
#             if default_image:
#                 if current_saved_default.exists():
#                     current_saved = current_saved_default[0]
#                     current_saved.in_display = False
#                     current_saved.save()
#                     # print('current', current_saved.default)
#
#             # obj.user = user
#             obj.save()
#         return super().form_valid(form)
#         # return redirect("me2ushop:home")


class ProductImageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ProductImage
    template_name = 'tags/product_image_update_form.html'
    fields = ["image", "in_display"]

    def form_valid(self, form):
        obj = form.save(commit=False)
        print('obj', obj)

        item = obj.item
        print('item:', item)
        user = self.request.user
        default_image = obj.in_display

        current_saved_default = ProductImage.displayed.filter(item__seller=user, item=item)
        print('current', current_saved_default)

        if default_image:
            if current_saved_default.exists():
                current_saved = current_saved_default[0]
                current_saved.in_display = False
                current_saved.save()

        obj.save()
        # print('default', default)

        return super().form_valid(form)

    def test_func(self):
        image_posted = self.get_object()
        print(image_posted)
        if self.request.user == image_posted.item.seller:
            return True
        return False


class ProductImageDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductImage
    template_name = 'tags/product_images_confirm_delete.html'
    success_url = reverse_lazy("me2ushop:home")

    # def get_queryset(self):
    #     return self.model.objects.filter(item__seller=self.request.user)


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
            Tag.objects.add_tag(product, tags)

        for tags in product.tags:
            html += render_to_string(template, {'tag': tags})
            response = json.dumps({'success': 'True', 'html': html})
    else:
        response = json.dumps({'success': 'False'})
    return HttpResponse(response, content_type='Application/javascript, charset=utf8')


def tag_cloud(request, template_name='tags/tag_cloud.html'):
    product_tags = Tag.objects.cloud_for_model(Product, steps=9, distribution=tagging.utils.LOGARITHMIC,
                                               filters={'is_active': True})
    page_title = 'Product Tag Cloud'
    return render(request, template_name, locals())


def tag(request, tag, template_name='tags/tag.html'):
    products = TaggedItem.objects.get_by_model(Product.active, tag)

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
        form = CartAddFormSet(request.POST or None)
        if form.is_valid():
            try:
                # Get quantity from useronline
                quantity = form.cleaned_data.get('quantity')
                # print("qty:", quantity)
                item = get_object_or_404(Product, slug=slug)
                # print("item we found:", item)

                order_item, created = OrderItem.objects.get_or_create(
                    order=cart,
                    item=item,
                    ordered=False
                )
                # print("order_item:", order_item)
                # print("created:", created)

                order_query_set = Order.objects.filter(id=cart.id, ordered=False)
                # print("cart_id found:", order_query_set)

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
        # print("user logged in adding qty without form")
        # user is logged in but not using form to add quantity
        try:
            item = get_object_or_404(Product, slug=slug)

            order_item, created = OrderItem.objects.get_or_create(
                order=cart,
                item=item,
                ordered=False
            )
            # print("order_item:", order_item)
            # print("created:", created)

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


@receiver(user_logged_in)
def merge_cart(sender, user, request, **kwargs):
    cart = getattr(request, 'cart', None)
    # print("we came here to merge")
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

                order_items = OrderItem.objects.filter(order=cart_id, ordered=False)

                # print('order_items:', order_items)

                for order_item in order_items:
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

                    if order.items.filter(item__slug=item.slug).exists():
                        if quantity > 1:
                            order_item.quantity = quantity
                        else:
                            order_item.quantity += 1
                        # print('order saved:', order_item)
                        order_item.save()
                    else:
                        order.items.add(order_item)
                        order_item.quantity = quantity
                    # print('order saved:', order_item)
                    order_item.save()
                del request.session['cart_id']
                request.session['cart_id'] = order.id
        else:
            order_items = OrderItem.objects.filter(order=cart_id, ordered=False)

            # print('order_items:', order_items)

            for order_item in order_items:
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
                del request.session['cart_id']
                request.session['cart_id'] = order.id
    elif qs.exists():
        request.session['cart_id'] = qs[0].id


def remove_cart(request, slug):
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
                }
                return render(self.request, 'order_summary.html', context)

            else:
                if self.request.cart:
                    cart_id = self.request.cart.id

                    order = Order.objects.get(id=cart_id, ordered=False)
                    # print(order)

                    context = {
                        'object': order,
                    }
                    return render(self.request, 'order_summary.html', context)
            return render(self.request, 'order_summary.html')
        except ObjectDoesNotExist:
            messages.error(self.request, "YOU DO NOT HAVE ANY ACTIVE ORDER")
            return redirect("me2ushop:home")


class AddressSelectionView(LoginRequiredMixin, FormView):
    template_name = "tags/address_select.html"
    form_class = AddressSelectionForm
    success_url = reverse_lazy('me2ushop:checkout')

    def get_form_kwargs(self):
        kwargs = super(AddressSelectionView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
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

                order_query_set = Order.objects.filter(user=self.request.user, ordered=False)
                # print('order_qs:', order_query_set)

                order_items = order.total_items()

                if order_query_set.exists():
                    if order_items > 0:

                        context = {
                            'object': order,
                            'form': form,
                            # 'form_address': form_address,
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

                        return render(self.request, 'checkout-page.html', context)

                    else:
                        messages.info(self.request, "Your Cart is Empty, Continue shopping before checkout ")
                        return redirect("me2ushop:order_summary")
                else:
                    messages.info(self.request, "YOU DO NOT HAVE ANY ACTIVE ORDER")
                    return redirect("me2ushop:home")
            else:
                # User is anonymous
                if self.request.cart:
                    cart_id = self.request.cart.id

                    order = Order.objects.get(id=cart_id, ordered=False)

                    order_query_set = Order.objects.filter(id=cart_id, ordered=False)

                    order_items = order.total_items()

                    if order_query_set.exists():
                        if order_items > 0:
                            context = {
                                'object': order,
                                'form': form,
                                'couponform': CouponForm,
                                'DISPLAY_COUPON_FORM': False,
                            }
                            return render(self.request, 'checkout-page.html', context)

                        else:
                            messages.info(self.request, "Your Cart is Empty, Continue shopping before checkout ")
                            return redirect("me2ushop:order_summary")

        except ObjectDoesNotExist:
            messages.info(self.request, "YOU DO NOT HAVE ANY ACTIVE ORDER")
            return redirect("me2ushop:home")

    def post(self, *args, **kwargs):

        form = CheckoutForm(self.request.POST or None)
        # form_address = AddressSelectionForm
        print('we got here')
        try:
            if self.request.user.is_authenticated:
                order = Order.objects.get(user=self.request.user, ordered=False)
                # if form_address.is_valid():
                #     print('true it\'s valid')
                #     use_shipping = form.cleaned_data.get('shipping_address')
                #     use_billing = form.cleaned_data.get('billing_address')
                #     print('shipping:', use_shipping)

                if form.is_valid():

                    use_default_shipping = form.cleaned_data.get('use_default_shipping')

                    use_default_billing = form.cleaned_data.get('use_default_billing')

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
                        city = form.cleaned_data.get('city')
                        shipping_address1 = form.cleaned_data.get('shipping_address')
                        shipping_address2 = form.cleaned_data.get('shipping_address2')
                        shipping_country = form.cleaned_data.get('shipping_country')
                        shipping_zip = form.cleaned_data.get('shipping_zip')

                        if is_valid_form([shipping_address1, shipping_country, shipping_zip, name, phone, email]):
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
                                address_type='S'

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

                    payment_option = form.cleaned_data.get('payment_option')

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
            else:
                if self.request.cart:

                    order = Order.objects.get(id=self.request.cart.id, ordered=False)

                    if form.is_valid():
                        print('valid checkout anonymous form')
                        name = form.cleaned_data.get('name')
                        email = form.cleaned_data.get('email')
                        phone = form.cleaned_data.get('phone')
                        city = form.cleaned_data.get('city')
                        shipping_address1 = form.cleaned_data.get('shipping_address')
                        shipping_address2 = form.cleaned_data.get('shipping_address2')
                        shipping_country = form.cleaned_data.get('shipping_country')
                        shipping_zip = form.cleaned_data.get('shipping_zip')

                        if is_valid_form([shipping_address1, shipping_country, shipping_zip, name, phone, email]):
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
                                address_type='S'
                            )

                            shipping_address.save()
                            # order.shipping_address = shipping_address
                            order.name = shipping_address.name
                            order.phone = shipping_address.phone
                            order.email = shipping_address.email
                            order.shipping_address1 = shipping_address.street_address
                            order.shipping_address2 = shipping_address.apartment_address
                            order.shipping_zip_code = shipping_address.zip
                            order.shipping_country = shipping_address.country
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
                            order.save()


                        else:

                            billing_address1 = form.cleaned_data.get('billing_address')
                            billing_address2 = form.cleaned_data.get('billing_address2')
                            billing_country = form.cleaned_data.get('billing_country')
                            billing_zip = form.cleaned_data.get('billing_zip')

                            if is_valid_form([billing_address1, billing_country, billing_zip]):

                                billing_address = Address(
                                    # cart_id=self.request.cart_id,
                                    street_address=billing_address1,
                                    apartment_address=billing_address2,
                                    country=billing_country,
                                    zip=billing_zip,
                                    address_type='B'
                                )

                                billing_address.save()
                                order.billing_address1 = billing_address.street_address
                                order.billing_address2 = billing_address.apartment_address
                                order.billing_zip_code = billing_address.zip
                                order.billing_country = billing_address.country
                                order.save()

                                # print("new bill address saved.")
                            else:
                                messages.info(self.request, "Please fill in the required BILLING FIELDS")
                                return redirect("me2ushop:checkout")

                        payment_option = form.cleaned_data.get('payment_option')

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
        order = ''
        if self.request.user.is_authenticated:
            order = Order.objects.get(user=self.request.user, ordered=False)
        elif self.request.cart:
            order = Order.objects.get(id=self.request.cart.id, ordered=False)

        # print('order:', order)
        if order.billing_country:
            context = {
                'object': order,
                'DISPLAY_COUPON_FORM': False

            }

            return render(self.request, 'payment.html', context)

        else:
            messages.warning(self.request, "Please fill in your valid delivery address prior to payment")
            return redirect("me2ushop:checkout")

    def post(self, *args, **kwargs):
        # `source` is obtained with Stripe.js; see
        # https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token

        order = ''
        if self.request.user.is_authenticated:
            order = Order.objects.get(user=self.request.user, ordered=False)
        else:
            if self.request.cart:
                order = Order.objects.get(id=self.request.cart.id, ordered=False)

        form = PaymentForm(self.request.POST)
        # userprofile = UserProfile.objects.get(user=self.request.user)

        if form.is_valid():
            print('valid payment form')
            token = self.request.POST['stripeToken']

            use_default = form.cleaned_data.get('use_default')
            save = form.cleaned_data.get('save')

            amount = int(order.get_total() * 100)  # get in ksh

            try:

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
                # else:
                #     payment.cart_id = self.request.cart_id
                payment.amount = amount
                payment.save()

                # Assign payment to user
                order.payment = payment
                if order.payment:
                    order.ordered = True
                    order.status = 20
                    # Assigning the order a ref code during checkout payment
                    order.ref_code = create_ref_code()
                    order.save()
                    del self.request.session['cart_id']

                    # Changing order_items in cart to ordered
                    order_items = order.items.all()
                    order_items.update(ordered=True)
                    for item in order_items:
                        item.save()

                    # if order.ordered:
                    #     if order.coupon:
                    #         order.coupon.valid = False
                    #         order.coupon.save()
                    #         messages.success(self.request, "Coupon was SUCCESSFUL")

                    messages.success(self.request, " CONGRATULATIONS YOUR ORDER WAS SUCCESSFUL")
                return redirect("me2ushop:home")

            except stripe.error.CardError as e:
                # Since it's a decline, stripe.error.CardError will be caught
                body = e.json_body
                err = body.get('error', {})
                messages.error(self.request, f"{err.get('message')}")
                return redirect("me2ushop:home")

            except stripe.error.RateLimitError as e:
                messages.error(self.request, "Rate Limit Error ")
                return redirect("me2ushop:home")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                messages.error(self.request, "Invalid parameters")
                return redirect("me2ushop:home")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.error(self.request, "Not authenticated")
                return redirect("me2ushop:home")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.error(self.request, "Network error ")
                return redirect("me2ushop:home")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.error(self.request,
                               "Something went wrong. You were not charged. Please try again or contact us")
                return redirect("me2ushop:home")

            except Exception:
                # Something else happened, completely unrelated to Stripe
                messages.error(self.request,
                               "Order recorded,  we have been notified. You will receive a call for order confirmation ")
                return redirect("me2ushop:home")

        else:
            messages.error(self.request, "Invalid form ")
            return redirect("me2ushop:home")


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
