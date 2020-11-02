from django import forms
from django.forms import inlineformset_factory, formset_factory, modelform_factory
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import OrderItem, Order, Address, ProductImage, Product
from .models import ProductReview
from . import widgets
from utils.fields import MultipleChoiceTreeField
from django.utils.translation import ugettext_lazy as _
from categories.models import Department
from crispy_forms.helper import FormHelper
from crispy_forms import layout, bootstrap
from mptt.forms import TreeNodeMultipleChoiceField, TreeNodePositionField

PAYMENT_CHOICES = {

    ('M', "M-Pesa"),
    ('P', "Paypal"),
    ('S', "Stripe"),
    ('DC', "Debit Card/Credit Card"),
    ('C', "Cash On Delivery"),
    ('FW', "FlutterWave"),

}


class ProductForm(forms.ModelForm):
    product_categories = TreeNodeMultipleChoiceField(label=_("Categories"), required=False,
                                                     queryset=Department.objects.all(),
                                                     widget=forms.CheckboxSelectMultiple,
                                                     level_indicator=u'+--')

    class Meta:
        model = Product
        fields = ['title', 'slug', 'price', 'discount_price', 'stock', 'made_in_africa', 'description',
                  'additional_information',
                  'meta_keywords',
                  'meta_description',
                  'category_choice', 'product_categories']

    def __int__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = ""
        self.helper.form_method = "POST"
        self.helper.layout = layout.Layout(
            layout.Field('category_name'),
            layout.Field(
                "categories",
                template='utils/checkbox_select_multiple_tree.html'
            ),
            bootstrap.FormActions(
                layout.Submit('submit', _('Save'))
            )
        )


class CheckoutForm(forms.Form):
    name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)
    shipping_city = forms.CharField(required=False)
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_zip = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100'
        }))

    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_city = forms.CharField(required=False)
    billing_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100'
        }))

    billing_zip = forms.CharField(required=False)

    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)


class AddressSelectionForm(forms.Form):
    billing_address = forms.ModelChoiceField(queryset=None)
    shipping_address = forms.ModelChoiceField(queryset=None)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset_billing = Address.objects.filter(user=user, address_type='B')
        queryset_shipping = Address.objects.filter(user=user, address_type='S')

        self.fields['billing_address'].queryset = queryset_billing
        self.fields['shipping_address'].queryset = queryset_shipping


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter Coupon',
        'class': 'form-control',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Qty',
        'value': '1',
        'class': 'form-control',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean(self):
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError('Cookies must be enabled')

            return self.cleaned_data


CartAddFormSet = modelform_factory(
    OrderItem,
    fields=('quantity',),
    widgets={'quantity': widgets.PlusMinusNumber()},
)


# override the default __init__ so we can set the request
# def __init__(self, request=None, *args, **kwargs):
#     self.request = request
#     super(CartAddProductForm, self).__init__(*args, **kwargs)
#
# # custom validation to check for cookie
# def clean(self):
#     if self.request:
#         if not self.request.session.test_cookie_worked():
#             raise forms.ValidationError("Cookies Must be Enabled")
#     return self.cleaned_data


class ProductReviewForm(forms.ModelForm):
    # reviewer_country = CountryField(blank_label='(select country)').formfield(
    #     required=False,
    #     widget=CountrySelectWidget(attrs={
    #         'class': 'custom-select d-block w-100'
    #     }))

    class Meta:
        model = ProductReview
        exclude = ('user', 'product', 'is_approved')


class RefundForm(forms.Form):
    ref_code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control col-md-12 mb-4"'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control col-md-12 mb-4"'
    }))
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'class': 'form-control col-md-12 mb-4"'
    }))


class PaymentForm(forms.Form):
    use_default = forms.BooleanField(required=False)
    save = forms.BooleanField(required=False)


# class ProductImageCreate(forms.ModelForm):
#     item = forms.CharField(widget=forms.HiddenInput())
#     # image = forms.ImageField()
#     # in_display = forms.BooleanField(required=False)
#
#     class Meta:
#         model = ProductImage
#         fields = ('item', 'image', 'in_display',)

# def __init__(self, *args, **kwargs):
#     super(ProductImageCreate, self).__init__(*args, **kwargs)

# self.fields['item'].widget.attrs['type'] = 'hidden'

# class ProductImageCreate(forms.ModelForm):
#     class Meta:
#         model = ProductImage
#         fields = ['item', 'image', 'in_display']
#
#     def __init__(self, slug, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         queryset_item = Product.objects.filter(slug=slug)
#
#         self.fields['item'].queryset = queryset_item

class ProductImageCreate(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['item', 'image', 'in_display']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset_item = Product.objects.filter(brand_name__user=user)

        self.fields['item'].queryset = queryset_item

# class ProductAddToCartForm(forms.Form):
#     quantity = forms.IntegerField(widget=forms.TextInput(attrs={
#         'placeholder': 'Qty',
#         'value': '1',
#         'size': '3',
#         'class': 'quantity',
#         'max_length': '5'}),
#         error_messages={'invalid': 'Please enter a valid quantity.'}, min_value=1)
#
#     product_slug = forms.CharField(widget=forms.HiddenInput())
#
#     #
#     # override the default __init__ so we can set the request
#     def __init__(self, request=None, *args, **kwargs):
#         self.request = request
#         super(ProductAddToCartForm, self).__init__(*args, **kwargs)
#
#     # custom validation to check for cookie
#     def clean(self):
#         if self.request:
#             if not self.request.session.test_cookie_worked():
#                 raise forms.ValidationError("Cookies Must be Enabled")
#         return self.cleaned_data
