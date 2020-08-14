from django import forms
from django.forms import inlineformset_factory, formset_factory, modelform_factory
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import OrderItem, Order, Address
from .models import ProductReview
from . import widgets

PAYMENT_CHOICES = {

    ('M', "M-Pesa"),
    ('P', "Paypal"),
    ('S', "Stripe"),
    ('D', "Debit Card"),
    ('C', "Cash On Delivery"),

}


class CheckoutForm(forms.Form):
    name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)
    city = forms.CharField(required=False)
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
