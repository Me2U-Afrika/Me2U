from django.conf.urls import url
from django.contrib import admin
# from .models import Item, OrderItem, Order, Address, StripePayment, Coupon, RequestRefund
from django.utils.html import format_html
from datetime import datetime, timedelta
import logging
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html
from django.db.models.functions import TruncDay
from django.db.models import Avg, Count, Min, Sum
from django.urls import path
from django.template.response import TemplateResponse
from django import forms

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile

logger = logging.getLogger(__name__)

from .models import *
from users.models import User


# This mixin will be used for the invoice functionality, which is
# only available to owners and employees, but not dispatchers


# Viewing the most bought products
class PeriodsSelectForm(forms.Form):
    PERIODS = ((30, "30 Days"),
               (60, "60 Days"),
               (90, "90 Days"))
    period = forms.TypedChoiceField(choices=PERIODS, coerce=int, required=True)


class Payment(admin.ModelAdmin):
    list_display = ('user', 'stripe_charge_id', 'amount', 'timestamp')


def make_refund_accepted(modelAdmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update order to refund granted'


def being_delivered(modelAdmin, request, queryset):
    queryset.update(being_delivered=True)


being_delivered.short_description = 'Update order to being delivered'


def make_coupon_accepted(modelAdmin, request, queryset):
    queryset.update(valid=True)


make_coupon_accepted.short_description = 'Update coupon to valid'


def make_active(modelAdmin, request, queryset):
    queryset.update(is_active=True)


make_active.short_description = "Mark selected items as active"


def make_inactive(modelAdmin, request, queryset):
    queryset.update(is_active=False)


make_inactive.short_description = "Mark selected items as inactive"


class OrderItemInline(admin.TabularInline):
    # list_display = ('user', 'item', 'quantity', 'ordered')
    model = OrderItem
    raw_id_fields = ('item',)


# class OrderInline(admin.TabularInline):
#     model = Order
#     raw_id_fields = ('items',)


class ProductAdmin(admin.ModelAdmin):
    # form = ProductAdminForm()
    list_display = ('title', 'price', 'in_stock', 'stock', 'is_active', 'made_in_africa', 'created_at', 'updated_at',)
    list_display_links = ('title',)
    list_per_page = 50
    ordering = ['-created_at']
    list_editable = ('in_stock',)

    search_fields = ['title', 'description', 'meta_keywords', 'meta_description', 'made_in_africa']
    exclude = ('created_at', 'updated_at',)

    prepopulated_fields = {'slug': ('title',)}
    # autocomplete_fields = ('product_categories',)

    inlines = (OrderItemInline,)
    actions = [make_active, make_inactive]

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser or request.user.is_seller:
            return self.readonly_fields
        return list(self.readonly_fields) + ['slug', 'title']

    def get_prepopulated_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.prepopulated_fields
        else:
            return {}


class DispatchersProductAdmin(ProductAdmin):
    readonly_fields = ('title', 'seller',
                       'description',
                       'slug',
                       'brand',
                       'is_bestseller',
                       'is_featured',
                       'additional_information',
                       'category_choice',
                       'label',
                       'discount_price',
                       "price", 'made_in_africa', 'created_at', 'updated_at', 'meta_keywords',
                       'meta_description',
                       'product_categories')
    list_editable = ('in_stock', 'stock',)
    prepopulated_fields = {}
    autocomplete_fields = ()


class SellersProductAdmin(ProductAdmin):
    list_display = ['title',
                    'slug',
                    'brand',
                    'in_stock',
                    'stock',
                    'is_bestseller',
                    'is_featured',
                    'category_choice',
                    'discount_price',
                    "price", 'created_at', 'updated_at', 'meta_keywords',
                    'meta_description',
                    ]
    list_editable = ('in_stock', 'stock',)
    readonly_fields = ("is_bestseller", "is_featured")
    prepopulated_fields = {}
    autocomplete_fields = ()

    # Dispatchers are only allowed to see order that# are ready to be shipped
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # print('qs:',qs)
        return qs.filter(seller=request.user)

    def has_add_permission(self, request):
        print(request)


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('item', 'thumbnail_tag',)
    search_fields = ('item__title',)

    def thumbnail_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="%s"/>' % obj.image.thumbnail.url
            )
        return "-"

    thumbnail_tag.short_description = "Thumbnail"

    # def item_title(self, obj):
    #     return obj.item.title


class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'user',
        'title',
        'date',

        'rating',
        'is_approved'
    )
    list_display_links = [
        'user']
    list_filter = ['user', 'rating']

    search_fields = [
        'user',
        'product'
    ]


class Items_Ordered(admin.ModelAdmin):
    list_display = ('user', 'item', 'quantity', 'status', 'ordered')
    search_fields = ['item', ]
    list_editable = ('status',)
    list_filter = ("status",)

    # inlines = (OrderInline,)


class Ordered(admin.ModelAdmin):
    list_display = (
        'user',
        'order_date',
        'ordered',
        'payment',
        'coupon',
        'ref_code',
        'shipping_country',
        'being_delivered',
        'received', 'refund_requested', 'refund_granted')
    list_display_links = [
        'user',
        'shipping_country',
        'payment',
        'coupon',
    ]
    list_filter = ['ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted']
    list_editable = ['being_delivered', 'refund_granted']

    search_fields = [
        'user__username',
        'user__email',
        'ref_code',
    ]
    fieldsets = (
        (None, {"fields": ("user", 'ordered', "status", "items")}),
        ("Shipping info",
         {"fields": (
             "name",
             "email",
             "phone",
             "shipping_address1",
             "shipping_address2",
             "shipping_zip_code",
             "shipping_city",
             "shipping_country",
         )},
         ),
        ("Billing info",
         {"fields": (
             "billing_address1",
             "billing_address2",
             "billing_zip_code",
             "billing_city",
             "billing_country",
         )},
         ),
    )
    autocomplete_fields = ('items',)

    actions = [make_refund_accepted, being_delivered]


class CentralOfficeOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status')
    list_editable = ('status',)
    readonly_fields = ('user',)
    list_filter = ("status", "shipping_country", "order_date")
    fieldsets = (
        (None, {"fields": ("user", "status", "items")}),
        ("Shipping info",
         {"fields": (
             "name",
             "email",
             "phone",
             "shipping_address1",
             "shipping_address2",
             "shipping_zip_code",
             "shipping_city",
             "shipping_country",
         )},
         ),
        ("Billing info",
         {"fields": (
             "billing_address1",
             "billing_address2",
             "billing_zip_code",
             "billing_city",
             "billing_country",
         )},
         ),
    )


class SellersOrderAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'order_date',
        'status',
        'being_delivered',
        'received',
    )
    list_editable = ['being_delivered', 'received']

    list_filter = ("status", "shipping_country", "order_date",)
    fieldsets = (
        (None, {"fields": ("user", "status", "items")}),
        ("Shipping info",
         {"fields": (
             "name",
             "email",
             "phone",
             "shipping_address1",
             "shipping_address2",
             "shipping_zip_code",
             "shipping_city",
             "shipping_country",
         )},
         ),
        ("Billing info",
         {"fields": (
             "billing_address1",
             "billing_address2",
             "billing_zip_code",
             "billing_city",
             "billing_country",
         )},
         ),
    )

    # Dispatchers are only allowed to see order that# are ready to be shipped
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user=request.user)


class DispatchersOrderAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'order_date',
        'status',
        'being_delivered',
        'received',
    )
    list_editable = ['being_delivered', 'received']

    list_filter = ("status", "shipping_country", "order_date",)
    fieldsets = (
        (None, {"fields": ("user", "status", "items")}),
        ("Shipping info",
         {"fields": (
             "name",
             "email",
             "phone",
             "shipping_address1",
             "shipping_address2",
             "shipping_zip_code",
             "shipping_city",
             "shipping_country",
         )},
         ),
        ("Billing info",
         {"fields": (
             "billing_address1",
             "billing_address2",
             "billing_zip_code",
             "billing_city",
             "billing_country",
         )},
         ),
    )

    # Dispatchers are only allowed to see order that# are ready to be shipped
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status=Order.PAID).filter(ordered=True)


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'cart_id',
        'name',
        'street_address',
        'apartment_address',
        'country',
        'city',
        'zip',
        'address_type',
        'default'
    ]

    list_filter = ['default', 'address_type']
    search_fields = [
        'user',
        'cart_id',
        'country',
        'zip'
    ]
    readonly_fields = ("user",)


class CouponDisplay(admin.ModelAdmin):
    list_display = ('code', 'valid')
    list_filter = ['valid']
    actions = [make_coupon_accepted]


class RefundDisplay(admin.ModelAdmin):
    list_display = ('order', 'reason', 'accepted', 'ref_code')
    list_filter = ['accepted']
    list_display_links = ['order', 'ref_code']


# The class below will pass to the Django admin templates a couple
# of extra values that represent colors of headings

class ColoredAdminSite(admin.sites.AdminSite):
    def each_context(self, request):
        context = super(ColoredAdminSite, self).each_context(request)
        context['site_header_color'] = getattr(self, 'site_header_color', None)
        context['module_caption_color'] = getattr(self, 'module_caption_color', None)
        return context


# The following will add reporting views to the list of
# available urls and will list them from the index page
class InvoiceMixin:
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url("invoice/(?P<order_id>[-\w]+)/$", self.admin_view(self.invoice_for_order), name="invoice", )
        ]
        return my_urls + urls

    def invoice_for_order(self, request, order_id):
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
        # This mixin will be used for the invoice functionality, which is
        # only available to owners and employees, but not dispatchers


class ReportingColoredAdminSite(ColoredAdminSite):
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'orders_per_day/', self.admin_view(self.orders_per_day), ),
            url(r'most_bought_products/', self.admin_view(self.most_bought_products),
                name='most_bought_products', ),

        ]
        return my_urls + urls

    def orders_per_day(self, request):
        starting_day = datetime.now() - timedelta(days=180)
        order_data = (
            Order.objects.filter(order_date__gt=starting_day)
        ).annotate(
            day=TruncDay('order_date')
        ).values('day').annotate(c=Count('id'))

        print('order', order_data)
        labels = [
            x["day"].strftime("%Y-%m-%d") for x in order_data
        ]
        values = [x['c'] for x in order_data]
        context = dict(self.each_context(request),
                       title="Orders Per Day",
                       labels=labels,
                       values=values,
                       )
        return TemplateResponse(request, 'orders_per_day.html', context)

    # def index(self, request, extra_context=None):
    #     reporting_pages = [
    #         {
    #             "name": "Orders per day",
    #             "link": "orders_per_day/",
    #             "name": "Most bought products",
    #             "link": "Most bought products",
    #
    #         }
    #     ]
    #     if not extra_context:
    #         extra_context = {}
    #     extra_context = {"reporting_pages": reporting_pages}
    #     return super().index(request, extra_context)

    def most_bought_products(self, request):
        labels = None
        values = None
        if request.method == "POST":
            form = PeriodsSelectForm(request.POST)

            if form.is_valid():
                days = form.cleaned_data['period']
                starting_day = datetime.now() - timedelta(days=days)
                data_set = (OrderItem.objects.filter(date_added__gt=starting_day)
                            .filter(ordered=True).values("item__title"))
                data = (Order.objects.filter(items__date_added__gt=starting_day)
                        .filter(ordered=True).values_list("items__item__title", "items__quantity"))
                print('data', data)
                # print(data_set)
                data = []
                for dict in data_set:
                    for title, value in dict.items():
                        # print('product', value)
                        data.append(value)

                c = collections.Counter(data)
                print('c', c)

                logger.info("most_bought_products query:")
                labels = [x for x in c.keys()]
                # print('data_labels', labels)

                values = [x for x in c.values()]
                # print('data_values', values)

        else:
            form = PeriodsSelectForm()
            labels = None
            values = None

        # print('data_labels', labels)
        # print('data_values', values)

        context = {
            "title": "Most Bought Products",
            'form': form,
            'labels': labels,
            'values': values,
        }
        return TemplateResponse(request, "most_bought_products.html", context)

    def index(self, request, extra_context=None):
        reporting_pages = [
            {
                "name": "Orders per day",
                "link": "orders_per_day/",

            },
            {

                "name": "Most bought products",
                "link": "most_bought_products/",

            }
        ]
        if not extra_context:
            extra_context = {}
        extra_context = {"reporting_pages": reporting_pages}
        return super().index(request, extra_context)


# Finally we define 3 instances of AdminSite, each with their own
# set of required permissions and colors

class OwnersAdminSite(InvoiceMixin, ReportingColoredAdminSite):
    site_header = "Me2U|Africa owners administration"
    site_header_color = "black"
    module_caption_color = "grey"

    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser


class CentralOfficeAdminSite(InvoiceMixin, ColoredAdminSite):
    site_header = "Me2U|Africa Central Office administration"
    site_header_color = "Purple"
    module_caption_color = "pink"

    def has_permission(self, request):
        return request.user.is_active and request.user.is_employee


class DispatchersAdminSite(ColoredAdminSite):
    site_header = "Me2U|Africa dispatch administration"
    site_header_color = "green"
    module_caption_color = "lightgreen"

    def has_permission(self, request):
        return request.user.is_active and request.user.is_dispatcher


class SellersAdminSite(ColoredAdminSite):
    site_header = "Me2U|Africa sellers administration"
    site_header_color = "green"
    module_caption_color = "lightgreen"

    def has_permission(self, request):
        return request.user.is_active and request.user.is_seller


main_admin = OwnersAdminSite()

admin.site.register(Product, ProductAdmin)
main_admin.register(Product, ProductAdmin)

admin.site.register(ProductImage, ProductImageAdmin)
main_admin.register(ProductImage, ProductImageAdmin)

# admin.site.register(ProductReview, ProductReviewAdmin)
main_admin.register(ProductReview, ProductReviewAdmin)

# admin.site.register(OrderItem, Items_Ordered)
main_admin.register(OrderItem, Items_Ordered)

# admin.site.register(Order, Ordered)
main_admin.register(Order, Ordered)

# admin.site.register(OrderAnonymous, Ordered_Anonymous)
# admin.site.register(StripePayment, Payment)
main_admin.register(StripePayment, Payment)

# admin.site.register(Coupon, CouponDisplay)
main_admin.register(Coupon, CouponDisplay)

main_admin.register(RequestRefund, RefundDisplay)
# admin.site.register(RequestRefund, RefundDisplay)

# admin.site.register(Address, AddressAdmin)
main_admin.register(Address, AddressAdmin)

central_office_admin = CentralOfficeAdminSite("central-office-admin")
central_office_admin.register(Product, ProductAdmin)
# central_office_admin.register(models.ProductTag, ProductTagAdmin)
central_office_admin.register(ProductImage, ProductImageAdmin)
central_office_admin.register(Address, AddressAdmin)
central_office_admin.register(Order, CentralOfficeOrderAdmin)

dispatchers_admin = DispatchersAdminSite("dispatchers-admin")
dispatchers_admin.register(Product, DispatchersProductAdmin)
# dispatchers_admin.register(models.ProductTag, ProductTagAdmin)
dispatchers_admin.register(Order, DispatchersOrderAdmin)

sellers_admin = SellersAdminSite("seller-admin")
sellers_admin.register(Product, SellersProductAdmin)
sellers_admin.register(Order, SellersOrderAdmin)
