import json
import random
import string
import tempfile

import django_filters
import requests
import stripe
import tagging
from django import forms as django_forms
from django.contrib import messages
from django.contrib.auth import user_logged_in
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (LoginRequiredMixin, UserPassesTestMixin)
from django.core.exceptions import ObjectDoesNotExist
from django.db import models as django_models
from django.dispatch import receiver
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import ListView, View, CreateView, UpdateView, DeleteView, FormView, TemplateView
from django_filters.views import FilterView
from djangorave.models import DRPaymentTypeModel, DRTransactionModel
from tagging.models import TaggedItem, Tag
from weasyprint import HTML

from marketing.models import *
from marketing.models import Slider
from payments.models import DRCTransactionModel
from stats import stats
from users.models import User
from .forms import *
from .models import *
import datetime
from django.utils.timezone import utc

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


# ___BRAND CREATE VIEWS___
class BrandCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Brand
    template_name = 'modelforms/brand_create_form.html'
    fields = ['title', 'business_type', 'business_description', 'business_email', 'business_phone', 'shipping_status',
              'country', 'subscription_plan', 'logo']

    def get_success_url(self):
        return reverse_lazy('me2ushop:brand_payment', kwargs={'brand_id': self.object.id})

    def form_valid(self, form):
        print('registering brand')

        from django.contrib.auth.models import Group

        try:
            seller_group = Group.objects.get(name='Sellers')

        except ObjectDoesNotExist:
            seller_group = Group.objects.create(name='Sellers')
            seller_group.save()

        obj = form.save(commit=False)
        user = self.request.user
        if seller_group:
            seller_group.user_set.add(self.request.user)
            user.is_staff = True
            obj.application_status = 20
            user.save()

        obj.profile = user
        obj.save()
        return super().form_valid(form)

    def test_func(self):
        print('We came to check if the current user is eligible to create a brand. None of his brands should be set '
              'as inactive')
        current_app = Brand.objects.filter(profile=self.request.user)
        if current_app.exists():
            for brand in current_app:
                if not brand.active:
                    return False
                return True
        return True


def brand_subscription(request, brand_id):
    from djangorave.models import DRTransactionModel, DRPaymentTypeModel
    context = {}
    brand = get_object_or_404(Brand, id=brand_id)
    plan = brand.subscription_plan
    print('prlan:', plan)

    plan_type = 'Basic'

    if brand.subscription_reference:
        transaction = DRTransactionModel.objects.get(
            user=request.user,
            reference=brand.subscription_reference)
        now = datetime.datetime.now().replace(tzinfo=utc)
        print("now", now)
        timediff = now - transaction.created_datetime
        timediff = timediff.total_seconds()
        days = timediff // 86400

        if days > 0:
            brand.subscription_status = False
            brand.save()

    elif plan.description == 'Free':
        print('New brand being added or a it\'s under free plan')
        # Format: "Apr 11 2021 14:19:23"
        now = datetime.datetime.now().replace(tzinfo=utc)
        print("now", now)
        timediff = now - brand.created
        print("time diff", timediff.total_seconds())

        days = timediff.total_seconds() // 86400
        if days < 0:
            print('still a new client updating their brand')
            brand.subscription_status = True
            brand.save()
            context.update({'free_plan': True})

        else:
            print('new client sticking to old ways')
            brand.subscription_status = False
            brand.save()
            context.update({'free_plan': False})
    else:
        plan_type = plan.description

    payment_type = DRPaymentTypeModel.objects.get(description=plan_type)

    context.update({
        'brand': brand,
        'payment_type': payment_type
    })

    return render(request, 'me2ushop/brand_payment.html', context)


class TransactionDetailView(LoginRequiredMixin, TemplateView):
    """Returns a transaction template"""

    template_name = "djangorave/transaction.html"

    def get_context_data(self, **kwargs):
        """Add plan to context data"""
        kwargs = super().get_context_data(**kwargs)
        brand = None
        try:
            brand = get_object_or_404(Brand, id=self.kwargs["reference"].split('__')[3])
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)

        if brand:
            print('id', brand.slug)
            kwargs['brand'] = brand

        try:
            transaction = DRTransactionModel.objects.get(
                user=self.request.user,
                reference=self.kwargs["reference"])

            kwargs["transaction"] = transaction

        except DRTransactionModel.DoesNotExist:
            print('Transaction does not exist creating another')

            # checking if the passed transaction is valid

            def callback_function(response):
                # confirm that the response for the transaction is successful
                if response.body['data']['status'] == 'success':
                    print('success')

                # confirm that the amount for that transaction is the amount you wanted to charge
                if response.body['data']['chargecode'] == '00':
                    print('chargecode= 00')

                if response.body['data']['amount'] == 8:
                    print("Payment successful then give value")

            data = {
                "txref": kwargs["reference"],
                # this is the reference from the payment button response after customer paid.
                "SECKEY": settings.RAVE_SANDBOX_SECRET_KEY
            }

            # this is the url of the staging server. Please make sure to change to that of production server when you
            # are ready to go live.
            url = "https://ravesandboxapi.flutterwave.com/flwv3-pug/getpaidx/api/v2/verify"
            headers = {"Authorization": "Bearer %s" % settings.RAVE_SANDBOX_SECRET_KEY}

            # make the http post request to our server with the parameters
            response = requests.post(url, json=data, headers=headers)

            # print(response.json())
            response = response.json()

            transaction = DRTransactionModel.objects.get_or_create(
                user=self.request.user,
                reference=self.kwargs["reference"],
                flutterwave_reference=response['data']['flwref'],
                order_reference=response['data']['orderref'],
                amount=response['data']['amount'],
                charged_amount=response['data']['chargedamount'],
                status=response['data']['status'],
                payment_type_id=kwargs['reference'].split("__")[0]

            )
            kwargs["transaction"] = transaction

            tran = DRTransactionModel.objects.get(
                user=self.request.user,
                reference=self.kwargs["reference"])
            plan = DRPaymentTypeModel.objects.get(id=tran.payment_type_id)
            print('plan:', plan)
            print('plan:', plan.description)

            brand.subscription_plan = plan
            brand.subscription_status = True
            for product in brand.product_set.all():
                print('product', product.is_active)
                product.save()
            brand.subscription_reference = tran.reference
            brand.save()

        return kwargs


class BrandUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Brand
    form_class = BrandForm
    template_name = 'modelforms/brand_create_form.html'

    def get_success_url(self):
        brand = get_object_or_404(Brand, id=self.object.id)
        print(brand.subscription_status)

        return reverse_lazy('me2ushop:brand_payment', kwargs={'brand_id': self.object.id})

    def get_context_data(self, **kwargs):
        context = super(BrandUpdateView, self).get_context_data(**kwargs)

        context.update({

            'page_title': 'Brand Update',
            'brand_id': self.get_object().id
        })
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()

        return super(BrandUpdateView, self).form_valid(form)

    def test_func(self):
        brand = self.get_object()
        if self.request.user == brand.profile:
            return True
        return False


# ___CHAT ROOM VIEWS___
def room(request, order_id):
    return render(request, 'chat_room.html', {'room_name_json': str(order_id)}, )


# ___ORDER VIEW___
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


# ___SELLER VIEW___
class SellerView(ListView):
    model = Product
    # template_name = 'seller-page.html'
    template_name = 'home/seller_page.html'
    paginate_by = 20

    def get_queryset(self):
        # user = get_object_or_404(User, id=self.kwargs.get('id'))
        brand = get_object_or_404(Brand, slug=self.kwargs.get('slug'))
        # print('user:', self.kwargs)
        if brand:
            return Product.active.filter(brand_name=brand).order_by('-created')

    def get_context_data(self, *, object_list=None, **kwargs):
        super(SellerView, self).get_context_data(**kwargs)

        # user = get_object_or_404(User, id=self.kwargs.get('id'))
        store = get_object_or_404(Brand, slug=self.kwargs.get('slug'))
        brand = Brand.objects.get(title=store)
        if brand:
            # other brands
            brands = Brand.objects.filter(active=True).exclude(title=store)

            # products = Product.active.filter(seller=user).order_by('-created')
            products = Product.active.filter(brand_name=store).order_by('-created')
            context = {
                'page_title': str(brand),
                'site_name': 'Me2U|Seller',
                'products': products,
                'brand': brand,
                'brands': brands,

            }

            return context


# ___HOME VIEW___
class HomeView(ListView):
    model = Product
    site_name = 'Me2U|Market'
    # template_name = 'trialTemplates/home.html'
    template_name = 'home/home.html'
    paginate_by = 4

    def get_context_data(self, *, object_list=None, **kwargs):
        super(HomeView, self).get_context_data(**kwargs)

        context = {}

        active_products = Product.active.all()

        try:
            # TOP BANNER
            top_banner = Banner.objects.filter(top_display=True)
            context.update({'top_banner': top_banner[0]})

        except:
            pass

        try:
            # FEATURING PRODUCTS
            featuring = active_products.filter(is_featured=True)
            context.update({'featuring': featuring})

        except:
            pass

        try:
            # BESTSELLING BANNER
            bestselling_banner = Banner.objects.bestselling()
            context.update({'best_seller_banner': bestselling_banner[0]})

        except:
            pass

        try:
            # BESTRATED
            bestrated = active_products.filter(is_bestrated=True)
            context.update({'bestrated': bestrated})

        except:
            pass

        try:
            # MARKETING MESSAGES
            marketing_messages = MarketingMessage.objects.get_featured_item()
            context.update({'marketing_messages': marketing_messages})

        except:
            pass

        try:
            # RECENT PRODUCTS
            recent_products = active_products.order_by('-created').exclude(is_featured=True, is_bestseller=True,
                                                                           is_bestrated=True)
            context.update({'recent_products': recent_products[:20]})

        except:
            pass

        try:
            # BESTSELLING PRODUCTS
            bestselling = active_products.filter(is_bestseller=True)
            context.update({'bestselling': bestselling})

        except:
            pass

        try:
            # CATEGORIES RANDOM
            categories = Department.objects.filter(is_active=True)
            # categories = context_processors.me2u(self.request)['active_departments'].prefetch_related("product_set")

            rand_department = random.choices(categories, k=3)
            context.update({
                'rand_department_1': rand_department[0],
                'rand_department_2': rand_department[1],
                'rand_department_3': rand_department[2]
            })
        except:
            pass

        try:
            # SLIDERS
            sliders = Slider.objects.featured().select_related('product')
            context.update({'sliders': sliders, })

        except:
            pass

        try:
            # TRENDS INFORMATION
            trend_info = TrendInfo.objects.all()
            context.update({'trend_info': trend_info})

        except:
            pass

        try:
            # RECOMMENDATION FROM VIEWS
            view_recommendation = stats.recommended_from_views(self.request)
            context.update({'view_recomms': view_recommendation})

        except:
            pass

        try:
            # SEARCH RECOMMENDATIONS
            search_recored = stats.recommended_from_search(self.request)
            context.update({'search_recomms': search_recored})

        except:
            pass

        return context


class HomeViewTemplateView(TemplateView):
    site_name = 'Me2U|Market'
    # template_name = 'trialTemplates/home.html'
    template_name = 'home/home.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        super(HomeViewTemplateView, self).get_context_data(**kwargs)

        context = {}

        active_products = Product.active.all().select_related()
        RAVE_SANDBOX = getattr(settings, "RAVE_SANDBOX", True)
        print('sandbox', RAVE_SANDBOX)

        try:
            # TOP BANNER
            top_banner = Banner.objects.filter(top_display=True).select_related()
            context.update({'top_banner': top_banner[0]})

        except:
            pass

        try:
            # FEATURING PRODUCTS
            featuring = active_products.filter(is_featured=True)
            context.update({'featuring': featuring})

        except:
            pass

        try:
            # BESTSELLING BANNER
            bestselling_banner = Banner.objects.bestselling()
            context.update({'best_seller_banner': bestselling_banner[0]})

        except:
            pass

        try:
            # BESTRATED
            bestrated = active_products.filter(is_bestrated=True)
            context.update({'bestrated': bestrated})

        except:
            pass

        try:
            # MARKETING MESSAGES
            marketing_messages = MarketingMessage.objects.get_featured_item()
            context.update({'marketing_messages': marketing_messages})

        except:
            pass

        try:
            # RECENT PRODUCTS
            recent_products = active_products.order_by('-created').exclude(is_featured=True, is_bestseller=True,
                                                                           is_bestrated=True)
            context.update({'recent_products': recent_products[:20]})

        except:
            pass

        try:
            # BESTSELLING PRODUCTS
            bestselling = active_products.filter(is_bestseller=True)
            context.update({'bestselling': bestselling})

        except:
            pass

        try:
            # CATEGORIES RANDOM
            categories = Department.objects.filter(is_active=True)
            # categories = context_processors.me2u(self.request)['active_departments']
            # categories = context_processors.me2u(self.request)['active_departments'].prefetch_related("product_set")

            rand_department = random.choices(categories, k=3)
            context.update({
                'rand_department_1': rand_department[0],
                'rand_department_2': rand_department[1],
                'rand_department_3': rand_department[2]
            })
        except:
            pass

        try:
            # SLIDERS
            sliders = Slider.objects.featured().select_related('product')
            context.update({'sliders': sliders, })

        except:
            pass

        try:
            # TRENDS INFORMATION
            trend_info = TrendInfo.objects.all()
            context.update({'trend_info': trend_info})

        except:
            pass

        try:
            # RECOMMENDATION FROM VIEWS
            view_recommendation = stats.recommended_from_views(self.request)
            context.update({'view_recomms': view_recommendation})

        except:
            pass

        try:
            # SEARCH RECOMMENDATIONS
            search_recored = stats.recommended_from_search(self.request)
            context.update({'search_recomms': search_recored})

        except:
            pass

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

# ___DEPARTMENT LIST PRODUCT VIEW___
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


# ___PRODUCT DETAILED CREATE, UPDATE, DELETE VIEWS___
from utils.views import CachedDetailView


class ProductDetailedView(CachedDetailView):
    model = Product
    # template_name = 'home/products_detailed_page.html'
    template_name = 'home/product_detail.html'
    # template_name = 'home/product_page_test.html'
    query_pk_and_slug = False

    def get_context_data(self, **kwargs):
        context = super(ProductDetailedView, self).get_context_data(**kwargs)
        # cart_product_form = CartAddProductForm()
        formset = CartAddFormSet()

        product = Product.objects.filter(title=kwargs['object']).select_related('brand_name')[0]
        pending_item = product.orderitem_set.filter(status=10)

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
            'product': product,
            'pending_item': pending_item,
            'review_form': review_form,
            'product_reviews': product_reviews,
            'page_title': str(self.get_object()),
            'formset': formset,
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
    template_name = 'modelforms/product_form.html'

    def get_success_url(self):
        # Assuming there is a ForeignKey from Productattribute to Product in your model
        return reverse_lazy('me2ushop:product_image_create', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super(ProductCreateView, self).get_context_data(**kwargs)
        print("pk:", self.kwargs.get('pk'))
        store = get_object_or_404(Brand, id=self.kwargs.get('pk'))

        context.update({

            'page_title': 'Add New Product',
            'brand_id': store.id

        })
        return context

    def form_valid(self, form):
        form.instance.seller = self.request.user
        obj = form.save(commit=False)
        brand_id = self.request.POST.get('brand_id', None)
        print('id:', brand_id)
        stock = obj.stock
        brand = Brand.objects.get(id=brand_id)
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
    template_name = 'modelforms/product_form.html'

    def get_context_data(self, **kwargs):
        context = super(ProductUpdateView, self).get_context_data(**kwargs)

        product = get_object_or_404(Product, slug=self.kwargs.get('slug'))
        context.update({

            'page_title': 'Update Product',
            'brand_id': product.brand_name.id
        })
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        stock = obj.stock
        # print('stock:', stock)
        if stock >= 1:
            obj.is_active = True
        else:
            obj.is_active = False

        product = self.get_object()

        if product:
            obj.brand_name = product.brand_name

        obj.save()
        return super(ProductUpdateView, self).form_valid(form)

    def test_func(self):
        product_posted = self.get_object()
        if self.request.user == product_posted.brand_name.profile:
            return True
        return False


class ProductUpdateAdditionalInforView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product

    fields = [
        'additional_information',
        'meta_keywords',
        'meta_description',
    ]
    template_name = 'modelforms/product_form.html'

    def get_context_data(self, **kwargs):
        context = super(ProductUpdateAdditionalInforView, self).get_context_data(**kwargs)

        product = get_object_or_404(Product, slug=self.kwargs.get('slug'))

        context.update({

            'page_title': 'Additional Info',
            'brand_id': product.brand_name.id
        })
        return context

    def form_valid(self, form):
        form.instance.seller = self.request.user
        obj = form.save(commit=False)

        obj.save()
        return super(ProductUpdateAdditionalInforView, self).form_valid(form)

    def test_func(self):
        product_posted = self.get_object()
        if self.request.user == product_posted.brand_name.profile:
            return True
        return False


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'modelforms/product_confirm_delete.html'

    # success_url = reverse_lazy('sellers:seller_products' )

    def get_success_url(self):
        # Assuming there is a ForeignKey from Productattribute to Product in your model
        return reverse_lazy('sellers:seller_products', kwargs={'brand_id': self.object.brand_name.id})

    def get_context_data(self, **kwargs):
        context = super(ProductDeleteView, self).get_context_data(**kwargs)

        context.update({

            'page_title': 'Delete Product',
        })
        return context

    def test_func(self):
        product_posted = self.get_object()
        if self.request.user == product_posted.brand_name.profile:
            return True
        return False


# ___PRODUCT ATTRIBUTES CREATE, UPDATE, DELETE___
class ProductAttributesCreateView(LoginRequiredMixin, CreateView):
    model = ProductDetail
    form_class = ProductAttributeCreate
    template_name = 'modelforms/product_form.html'

    def get_context_data(self, **kwargs):
        context = super(ProductAttributesCreateView, self).get_context_data(**kwargs)

        product = get_object_or_404(Product, slug=self.kwargs.get('slug'))

        context.update({

            'page_title': 'Product attributes',
            'brand_id': product.brand_name.id
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
    #     if self.request.user == product_posted.product.brand_name.profile:
    #         return True
    #     return False


class ProductAttributeUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductDetail
    fields = '__all__'
    template_name = 'modelforms/product_form.html'

    def get_context_data(self, **kwargs):
        context = super(ProductAttributeUpdateView, self).get_context_data(**kwargs)

        product_detail = ProductDetail.objects.filter(id=self.kwargs.get('pk')).select_related('product__brand_name')[0]
        print('productdetail:', product_detail)

        context.update({

            'page_title': 'Attribute Update',
            'brand_id': product_detail.product.brand_name.id
        })
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()

        return super(ProductAttributeUpdateView, self).form_valid(form)


class ProductAttributeDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductDetail
    template_name = 'modelforms/product_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super(ProductAttributeDeleteView, self).get_context_data(**kwargs)

        product_detail = ProductDetail.objects.filter(id=self.kwargs.get('pk')).select_related('product__brand_name')[0]

        context.update({

            'page_title': 'Delete Attribute',
            'brand_id': product_detail.product.brand_name.id
        })
        return context

    def get_success_url(self):
        # Assuming there is a ForeignKey from Productattribute to Product in your model
        product = self.object.product
        return reverse_lazy('me2ushop:product', kwargs={'slug': product.slug})


@login_required
def show_product_image(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product_image = ProductImage.objects.filter(item=product)
    context = {
        'object': product,
        'brand_id': product.brand_name.id,
        'product_image': product_image,
        'page_title': 'ImageList-' + str(product)
    }

    return render(request, 'modelforms/product_images_list.html', context)


# ___PRODUCT IMAGE CREATE UPDATE DELETE VIEWS___
def product_image_create(request, slug):
    product = get_object_or_404(Product, slug=slug)
    # print('slug:', slug)

    product_image = ProductImage.objects.filter(item__brand_name__user=request.user, item=product)
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

            if product.brand_name.profile == request.user:

                current_saved_default = ProductImage.displayed.filter(item__brand_name__user=request.user,
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

        return render(request, 'modelforms/product_image_form.html', context)


class ProductImageCreateView(LoginRequiredMixin, CreateView):
    model = ProductImage
    template_name = 'modelforms/product_image_form.html'
    form_class = ProductImageCreate

    # success_url = reverse_lazy("sellers:seller_products")

    def get_success_url(self):
        # Assuming there is a ForeignKey from Productattribute to Product in your model
        product = self.object.item
        return reverse_lazy('me2ushop:product', kwargs={'slug': product.slug})

    def get_context_data(self, **kwargs):
        context = super(ProductImageCreateView, self).get_context_data(**kwargs)

        product = Product.objects.filter(slug=self.kwargs.get('slug')).select_related('brand_name')[0]

        context.update({

            'page_title': 'Image Create',
            'brand_id': product.brand_name.id,
            'product': product

        })
        return context

    def get_form_kwargs(self):
        kwargs = super(ProductImageCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['slug'] = self.kwargs['slug']
        return kwargs

    def form_valid(self, form):
        print('In Add Image Form')
        obj = form.save(commit=False)
        print('obj:', obj)
        item = form.cleaned_data.get('item')
        image = form.cleaned_data.get('image')

        user = self.request.user

        default_image = obj.in_display

        if item.brand_name.profile == self.request.user:

            current_saved_default = ProductImage.displayed.filter(item__brand_name__profile=user, item=item)
            # print('current', current_saved_default)

            if default_image:
                if current_saved_default.exists():
                    current_saved = current_saved_default[0]
                    current_saved.in_display = False
                    current_saved.save()

            obj.save()
        return super().form_valid(form)


class ProductImageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ProductImage
    template_name = 'modelforms/product_image_update_form.html'
    fields = ["image", "in_display"]

    def get_context_data(self, **kwargs):
        context = super(ProductImageUpdateView, self).get_context_data(**kwargs)
        image_posted = self.get_object()
        # print('image posted:', image_posted)

        context.update({

            'page_title': 'Update Image-' + str(self.get_object()),
            'brand_id': image_posted.item.brand_name.id,
            'object': image_posted
        })
        return context

    def form_valid(self, form):
        print('In Update Image Form')

        obj = form.save(commit=False)
        # print('obj', obj)

        item = obj.item
        # print('item:', item)
        user = self.request.user
        default_image = obj.in_display

        current_saved_default = ProductImage.displayed.filter(item=item, in_display=True)

        if default_image:
            if current_saved_default.exists():
                print('we came to change the default image in display')

                current_saved = current_saved_default[0]
                current_saved.in_display = False
                current_saved.save()

        obj.save()

        return super().form_valid(form)

    def test_func(self):
        image_posted = self.get_object()
        if self.request.user == image_posted.item.brand_name.profile:
            return True
        return False


class ProductImageDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductImage
    template_name = 'modelforms/product_image_delete.html'

    # success_url = reverse_lazy("sellers:seller_products")

    def get_success_url(self):
        product = self.object.item

        return reverse_lazy('me2ushop:product', kwargs={'slug': product.slug})

    def get_context_data(self, **kwargs):
        context = super(ProductImageDeleteView, self).get_context_data(**kwargs)

        # image = ProductImage.objects.filter(id=self.kwargs.get('pk')).select_related('item__brand_name')[0]
        image_posted = self.get_object()

        context.update({

            'page_title': 'Delete Product',
            'brand_id': image_posted.item.brand_name.id
        })
        return context


def delete_image(request, pk):
    print('using delete image function')
    image = ProductImage.objects.filter(id=pk)
    print('image:', image)
    if image:
        slug = image[0].item.slug
        print('slug:', slug)

        if not image[0].in_display:
            image.delete()
            return redirect('me2ushop:product', slug=slug)

        else:
            image.delete()

            product = Product.objects.get(slug=slug)
            print('product:', product)
            current = product.productimage_set.all()
            print('images:', current)
            if current.exists():
                print('we setting the new image on display')
                new_image = current[0]
                new_image.in_display = True
                # delete old image
                new_image.save()
                return redirect('me2ushop:product', slug=slug)
            else:
                product = Product.objects.get(slug=slug)
                product.save()
                return redirect('me2ushop:product_image_create', slug=slug)
    else:
        messages.warning(request, "An Error Occured: Clear Cache")
        return redirect('me2ushop:home')


# ___PRODUCT ADD TO CART, TAG, REVIEWS___
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
                Tag.objects.add_tag(product, tags.lower())

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

    page_title = str(tag)

    return render(request, template_name, locals())


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

    item = get_object_or_404(Product, slug=slug)

    cart = request.cart
    print('cart1:', cart)
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
            # print("is valid:", form.is_valid())
            try:
                # Get quantity from useronline
                quantity = form.cleaned_data.get('quantity')
                # print("qty:", quantity)
                item = get_object_or_404(Product, slug=slug)
                # print("item we found:", item)

                order_item, created = OrderItem.objects.get_or_create(
                    customer_order=cart,
                    item=item,
                    ordered=False
                )
                print("order_item:", order_item)
                # print("created:", created)

                # check if the order item is in the order
                if cart.items.filter(item__slug=item.slug).exists():
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
                else:
                    messages.info(request, 'This item has been added to your cart.')
                    cart.items.add(order_item)
                    if quantity > 1:
                        order_item.quantity = quantity
                    else:
                        order_item.quantity = 1

                    if request.user.is_authenticated:
                        order_item.user = request.user

                order_item.save()
                # print(order_item.quantity)
                return redirect("me2ushop:order_summary")
            except Exception:
                messages.info(request, 'ERROR.')
                return redirect("me2ushop:product", slug=slug)
    else:
        print("user adding qty without form")
        stats.log_product_view(request, item)

        # user is logged in but not using form to add quantity
        try:

            order_item, created = OrderItem.objects.get_or_create(
                customer_order=cart,
                item=item,
                ordered=False
            )

            # check if the order item is in the order
            if cart.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                # print('updated item:', order_item)
                # print('cartid:', cart_id)
                if request.user.is_authenticated:
                    order_item.user = request.user
                order_item.save()
                messages.info(request, 'This item quantity was updated.')
            else:
                messages.info(request, 'This item has been added to your cart.')
                cart.items.add(order_item)
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


class Order_summary_view(View):
    # print('we came here Order summary')
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
                print('anonymous cart_summary')
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

                order_items = order.total_items()

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
                print('Trying to checkout someone not signed in.')
                print("cart_to_checkout:", self.request.cart)

                if self.request.cart:
                    print("cart_to_checkout_id:", self.request.cart.id)
                    print("cart_items:", self.request.cart.items.all())

                    cart = self.request.cart

                    order_items = cart.total_items()

                    if order_items > 0:
                        print("total Ordered:", order_items)

                        context = {
                            'order': cart,
                            'form': form,
                            'couponform': CouponForm,
                            'DISPLAY_COUPON_FORM': False,
                        }
                        return render(self.request, 'home/checkout_page.html', context)

                    else:
                        messages.info(self.request, "Your Cart is Empty, Continue shopping before checkout ")
                        return redirect("me2ushop:order_summary")

                messages.info(self.request, "YOU DO NOT HAVE ANY ACTIVE ORDER")
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

                if form.is_valid():
                    print(form.is_valid())
                    # if not order.billing_address1:
                    use_default_shipping = form.cleaned_data.get('use_default_shipping')

                    use_default_billing = form.cleaned_data.get('use_default_billing')
                    payment_option = form.cleaned_data.get('payment_option')
                    print('payment_option:', payment_option)

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
                        city = form.cleaned_data.get('shipping_city')
                        shipping_address1 = form.cleaned_data.get('shipping_address')
                        shipping_address2 = form.cleaned_data.get('shipping_address2')
                        shipping_country = form.cleaned_data.get('shipping_country')
                        shipping_zip = form.cleaned_data.get('shipping_zip')

                        if is_valid_form([shipping_address1, shipping_country, shipping_zip, city]):
                            print('form is valid')
                            print('phone:', self.request.user.profile.phone)

                            shipping_address = Address(
                                user=self.request.user,
                                name=self.request.user.username,
                                email=self.request.user.email,
                                phone=self.request.user.profile.phone,
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
                    elif payment_option == 'Fw':
                        return redirect("me2ushop:payment", payment_option='flutterwave')
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
                        print('po:', payment_option)

                        if is_valid_form([shipping_address1, shipping_country, city, shipping_zip, name, phone, email]):
                            print('valid details')
                            shipping_address = Address(
                                # cart_id=order.id,
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

                            # print("saved Sa:", shipping_address)
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
                            print("user checked same address")
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
                        print("payment option:", payment_option)
                        if payment_option == 'S':
                            return redirect("me2ushop:payment", payment_option='stripe')
                        elif payment_option == 'P':
                            return redirect("me2ushop:payment", payment_option='paypal')
                        elif payment_option == 'M':
                            return redirect("me2ushop:payment", payment_option='mpesa')
                        elif payment_option == 'C':
                            return redirect("me2ushop:payment", payment_option='cash_on_delivery')
                        elif payment_option == 'Fw':
                            return redirect("me2ushop:payment", payment_option='flutterwave')
                        else:
                            messages.warning(self.request, 'Invalid Payment Option. Select mode of payment to continue')
                            return redirect("me2ushop:checkout")

                    messages.warning(self.request, 'Invalid form')
                    return redirect("me2ushop:checkout")

        except ObjectDoesNotExist:
            messages.error(self.request, "YOU DO NOT HAVE ANY ACTIVE ORDER!")
            return redirect("me2ushop:home")
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
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
                print('authenticated user:', self.request.cart)
                order = Order.objects.get(user=self.request.user, ordered=False)
            elif self.request.cart:
                order = self.request.cart

            print('order to paid for:', order)
            if order is not None:
                if order.billing_country:
                    context = {
                        'order': order,
                        'DISPLAY_COUPON_FORM': False,
                        'payment': order.payment,
                        'public_key': settings.RAVE_SANDBOX_PUBLIC_KEY

                    }

                    return render(self.request, 'home/payment.html', context)

                else:
                    messages.warning(self.request, "Please fill in your valid delivery address prior to payment")
                    return redirect("me2ushop:checkout")

            messages.warning(self.request, "You have no active orders")
            return redirect("me2ushop:home")

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            return redirect("me2ushop:home")

    def post(self, *args, **kwargs):
        print('We came to post payment')
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
                print('order:', self.request.POST)

                token = self.request.POST.get('stripeToken', False)
                print('token', token)

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

                # Assigning the order a ref code during checkout payment
                order.ref_code = create_ref_code()
                order.status = 20

                # Changing order_items in cart to ordered
                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.save()
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
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            return redirect("me2ushop:home")


def paypal_payment_complete(request):
    body = json.loads(request.body)
    # print("body:", body)

    cart = None
    if not cart:
        user = None
        order_date = timezone.now()
        cart = Order.objects.create(user=user, order_date=order_date, ordered=True, status=20)
        cart.ref_code = create_ref_code()
        cart.save()

        request.session['cart_id'] = cart.id
        # print('cart2:', cart)

    item = Product.objects.get(id=body['productId'])
    # print(item)
    order_item, created = OrderItem.objects.get_or_create(
        customer_order=cart,
        item=item,
        ordered=True,
        quantity=1,
    )
    # print("order_item:", order_item)
    # print("created:", created)

    if request.user.is_authenticated:
        order_item.user = request.user
        cart.user = request.user
        order_item.save()

    cart.items.add(order_item)
    cart.save()

    return JsonResponse("payment successful", safe=False)


def paypal_payment_complete_cart(request):
    print('we came to post payment', request)
    body = json.loads(request.body)
    print("body:", body)

    order = Order.objects.get(id=body['orderId'])
    # print(order)
    order.ordered = True
    order.ref_code = create_ref_code()
    order.status = 20
    order_items = order.items.all()
    order_items.update(ordered=True)
    for item in order_items:
        item.save()
    order.save()

    return JsonResponse("payment successful", safe=False)


def flutterCompleteTrans(request, reference):

    order = get_object_or_404(Order, id=reference.split('__')[0])
    print('Order we paying for:', order)

    data = {
        "txref": reference,
        # this is the reference from the payment button response after customer paid.
        "SECKEY": settings.RAVE_SANDBOX_SECRET_KEY
    }

    # this is the url of the staging server. Please make sure to change to that of production server when you
    # are ready to go live.
    url = "https://ravesandboxapi.flutterwave.com/flwv3-pug/getpaidx/api/v2/verify"
    headers = {"Authorization": "Bearer %s" % settings.RAVE_SANDBOX_SECRET_KEY}

    # make the http post request to our server with the parameters
    response = requests.post(url, json=data, headers=headers)

    # print(response.json())
    if response:
        response = response.json()

        transaction = DRCTransactionModel.objects.get_or_create(
            order=order,
            reference=reference,
            flutterwave_reference=response['data']['flwref'],
            order_reference=response['data']['orderref'],
            amount=response['data']['amount'],
            charged_amount=response['data']['chargedamount'],
            status=response['data']['status'],

        )
        print('transaction:', transaction)

        if request.user.is_authenticated:
            transaction = DRCTransactionModel.objects.get(
                order=order,
                reference=reference)
            user = User.objects.get(id=request.user.id)
            transaction.user = user
            transaction.save()

        order.ordered = True
        order.ref_code = reference
        order.status = 20
        order_items = order.items.all()
        order_items.update(ordered=True)
        for item in order_items:
            item.save()
        order.save()

        return checkout_done(request)


class FlutterTransactionDetailView(LoginRequiredMixin, TemplateView):
    """Returns a transaction template"""

    template_name = "home/checkout_done.html"

    def get_context_data(self, **kwargs):
        """Add plan to context data"""
        kwargs = super().get_context_data(**kwargs)

        order = get_object_or_404(Order, id=self.kwargs["reference"].split('__')[0])
        print('Order we paying for:', order)

        try:
            transaction = DRCTransactionModel.objects.get(
                user=self.request.user,
                reference=self.kwargs["reference"])

            kwargs["transaction"] = transaction

        except DRCTransactionModel.DoesNotExist:
            print('Transaction does not exist creating another')

            # checking if the passed transaction is valid

            data = {
                "txref": kwargs["reference"],
                # this is the reference from the payment button response after customer paid.
                "SECKEY": settings.RAVE_SANDBOX_SECRET_KEY
            }

            # this is the url of the staging server. Please make sure to change to that of production server when you
            # are ready to go live.
            url = "https://ravesandboxapi.flutterwave.com/flwv3-pug/getpaidx/api/v2/verify"
            headers = {"Authorization": "Bearer %s" % settings.RAVE_SANDBOX_SECRET_KEY}

            # make the http post request to our server with the parameters
            response = requests.post(url, json=data, headers=headers)

            # print(response.json())
            if response:
                response = response.json()

                transaction = DRCTransactionModel.objects.get_or_create(
                    user=self.request.user,
                    order=order,
                    reference=self.kwargs["reference"],
                    flutterwave_reference=response['data']['flwref'],
                    order_reference=response['data']['orderref'],
                    amount=response['data']['amount'],
                    charged_amount=response['data']['chargedamount'],
                    status=response['data']['status'],

                )
                print('transaction:', transaction)

                order.ordered = True
                order.ref_code = self.kwargs["reference"]
                order.status = 20
                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()
                order.save()
                del self.request.session['cart_id']

        kwargs["order"] = order

        return kwargs


def checkout_done(request):
    print('In checkoutdone')
    print('request:', request)

    print('request cart Start:', request.cart)
    try:
        order_id = request.cart.id
        print(order_id)

        order = Order.objects.get(id=order_id)
        print(order.ordered)

        context = {
            'order': order,
        }

        del request.session['cart_id']

        return render(request, 'home/checkout_done.html', locals())

    except Exception:
        messages.warning(request, "No active orders")
        return redirect('me2ushop:home')


def invoice_for_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    # print('order', order)
    if request.GET.get("format") == "pdf":
        html_string = render_to_string("home/invoice.html", {"order": order})
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
    return render(request, "home/invoice.html", {"order": order})


class RefundView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = RefundForm()

        context = {
            'RefundForm': form
        }
        return render(self.request, "home/returns.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            # email = self.request.user.email

            # assign refund request to order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                if not order.user:
                    order.user = self.request.user
                order.save()

                # record the refund

                refund = RequestRefund()
                refund.order = order
                refund.reason = message
                # refund.email = email
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


@login_required()
def refund_status(request, order_id):
    print('In refund status')
    print('ref:', order_id)
    try:
        request = RequestRefund.objects.get(order__id=order_id)
        print("request found", request.accepted)

        context = {
            'status': request.accepted,

        }
        return render(request, 'home/refund_status.html', context)

    except Exception:
        messages.warning(request, "No active requests found")
        return redirect('me2ushop:home')
