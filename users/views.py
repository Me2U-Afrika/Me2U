from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView

from .forms import UserRegisterForm
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from me2ushop.models import Order, OrderItem, Product, Brand
from .profile import retrieve_profile, set_profile, set_personal, set_pic
from .forms import AddressForm, PersonalInfoForm, ProfilePicForm
from .models import Profile, User, SellerProfile, AutomobileProfile, EmailConfirmed
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import (FormView, CreateView, UpdateView, DeleteView, )
import logging
import re
from me2ushop import models

logger = logging.getLogger(__name__)


# we going to create a view for register page using existing classes in django. The classes are converted to html.

def register(request):
    # create an instance of form
    if request.method == 'POST':

        form = UserRegisterForm(request.POST)
        # Checking for validity
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            # email = form.cleaned_data.get('email')
            # raw_password = form.cleaned_data.get('password1')
            # account = authenticate(email=email, password=raw_password)
            # login(request, account)
            # form.send_mail()
            messages.success(request, f'Account created for {username}! Check your email to confirm before login')
            return redirect('login')
        else:
            messages.warning(request, 'Invalid details, please try again')
            form = UserRegisterForm(request.POST)
    else:

        form = UserRegisterForm

    context = {
        'form': form,
        'page_title': 'User Registration'
    }
    return render(request, 'users/register.html', context)


SHA1_RE = re.compile('^[a-f0-9]{40}$')


def activation_view(request, activationKey):
    if SHA1_RE.search(activationKey):
        print('real')
        try:
            instance = EmailConfirmed.objects.get(activationKey=activationKey)
        except EmailConfirmed.DoesNotExist:
            instance = None
            raise Http404
        if instance is not None and not instance.confirmed:
            page_message = 'Confirmation Successful! Welcome'
            instance.confirmed = True
            # instance.activationKey = 'Confirmed'
            instance.save()
        elif instance is not None and instance.confirmed:
            page_message = "Already Confirmed"
        else:
            page_message = ''
        context = {
            'page_message': page_message
        }
        return render(request, 'users/activation_complete.html', context)
    else:
        raise Http404


def register_seller(request, template_name="users/seller_register.html"):
    pass
    # create an instance of form
    # if request.method == 'POST':
    #     form = SellerRegisterForm(request.POST)
    #     # Checking for validity
    #     if form.is_valid():
    #         form.save()
    #         username = form.cleaned_data.get('username')
    #         messages.success(request, f'Account created for {username}!. You can now login!')
    #         return redirect('login_seller')
    #     return redirect('login_seller')
    #
    # else:
    #     form_seller = SellerRegisterForm
    #
    #     page_title = 'seller Registration'
    #     context = {
    #         'form': form_seller,
    #         'page_title': page_title
    #     }
    #     # context_instance = RequestContext(request)
    #     # print('contxt inst:', context_instance)
    #     return render(request, template_name, context)


@login_required()
def profile(request):
    page_title = 'My Account'
    orders = Order.objects.filter(user=request.user, ordered=True)
    user = User.objects.filter(email=request.user.email).first()
    profile_user = Profile.objects.get(user=request.user)
    print('profile:', profile_user)
    # set = user.emailconfirmed_set.all()
    # if set:
    #     if not set[0].confirmed:
    #         set[0].activate_user_email()
    # order_items = OrderItem.objects.filter(user=request.user, ordered=True)
    # print('order:', order)
    # print('order_items:', items)

    name = request.user.username
    # context_instance = RequestContext(request)
    # print('contxt inst profile:', context_instance)
    return render(request, 'users/profile.html', locals())


@login_required
def order_details(request, order_id, template_name="users/order-details.html"):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # print('order:', order)
    page_title = 'Order Details for Order #' + order_id
    order_items = OrderItem.objects.filter(user=request.user, order=order)
    seller_items = OrderItem.objects.filter(order=order, item__seller=request.user)

    print('seller_items:', order_items)
    # for order_item in order_items:
    # print('item:', order_item.item.slug)

    # context_instance = RequestContext(request)
    return render(request, template_name, locals())


@login_required
def re_order(request, order_id):
    # print("we in the re-order")
    # print('order id:', order_id)
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # print('order:', order)

    order_items = OrderItem.objects.filter(user=request.user, order=order)
    # print('order_items:', order_items)

    for order_item in order_items:
        # print('item:', item.quantity)
        quantity = order_item.quantity
        product = Product.active.all()
        item = get_object_or_404(product, slug=order_item.item.slug)
        # print("item found:", item)
        #
        # Add new product being ordered to database
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False
        )
        # print("order_item:", order_item)

        # Check if current user has products in cart
        order_query_set = Order.objects.filter(user=request.user, ordered=False)
        # print("user:", order_query_set)

        # This code returns the user who ordered an item
        if order_query_set.exists():
            order = order_query_set[0]

            order.items.add(order_item)
            if quantity > 1:
                order_item.quantity = quantity
            else:
                order_item.quantity = 1
            order_item.save()

        else:
            # print("order not in cart")
            order_date = timezone.now()
            order = Order.objects.create(user=request.user, order_date=order_date)
            order.items.add(order_item)
            if quantity > 1:
                order_item.quantity = quantity
            else:
                order_item.quantity = 1
        order_item.save()
    messages.info(request, 'Your re-order cart has been updated!')
    return redirect("me2ushop:order_summary")


class AddressListView(LoginRequiredMixin, ListView):
    model = models.Address
    template_name = 'users/addresses/address_list.html'

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = models.Address
    template_name = 'users/addresses/address_form.html'
    fields = ["name", "email", "phone", "street_address", "apartment_address", "zip", "city", "country", "address_type",
              "default"]
    success_url = reverse_lazy("users:address_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        user = self.request.user
        default_add = obj.default
        add_type = obj.address_type

        current_saved = models.Address.objects.filter(user=user, address_type=add_type, default=True)
        print('current', current_saved)

        if default_add:
            if current_saved.exists():
                current_saved = current_saved[0]
                current_saved.default = False
                current_saved.save()
                print('current', current_saved.default)

            obj.user = user
            obj.save()

        obj.user = user
        obj.save()
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Address
    template_name = 'users/addresses/address_form.html'
    fields = ["name", "email", "phone", "street_address", "apartment_address", "zip", "city", "country", "address_type",
              "default"]
    success_url = reverse_lazy("users:address_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        user = self.request.user
        default_add = obj.default
        add_type = obj.address_type
        print('add_type:', obj)

        current_saved = models.Address.objects.filter(user=user, address_type=add_type, default=True)
        print('current', current_saved)
        # current_orders_open_orders = models.Order.objects.filter(user=user, ordered=True)

        if default_add:
            if current_saved.exists():
                current_saved = current_saved[0]
                current_saved.default = False
                current_saved.save()
        # for already_ordered in current_orders_open_orders:
        #     billing_address = already_ordered.billing_address
        #     print('already ordered', already_ordered.billing_address)
        #
        #     # shipping_address = billing_address
        #     # print('already ordered', already_ordered.shipping_address)
        #     #
        #     # if add_type == 'B':
        #     #     if obj.country != billing_address.country:
        #     #         already_ordered.billing_address = billing_address
        #     #         print('already ordered', already_ordered.billing_address)
        #     #
        #     #         already_ordered.save()
        #     # elif add_type == 'S':
        #     #     if obj.country != shipping_address.country:
        #     #         already_ordered.shipping_address = shipping_address
        #     #         print('already ordered', already_ordered.shipping_address)
        #     #
        #     #         already_ordered.save()

        # obj.user = user
        # obj.save()

        obj.user = user
        obj.save()
        # print('default', default)

        return super().form_valid(form)

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Address
    template_name = 'users/addresses/address_confirm_delete.html'
    success_url = reverse_lazy("users:address_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


def order_info(request, template_name="users/order-info.html"):
    pass
    # if request.method == 'POST':
    #     postdata = request.POST.copy()
    #     form = AddressForm(postdata)
    #     if form.is_valid():
    #         set_profile(request)
    #         return redirect('users:profile')
    #
    # else:
    #     user_profile = retrieve_profile(request)
    #     # print('user_profile:', user_profile)
    #     form = AddressForm(instance=user_profile)
    #     # print('form',form)
    #     page_title = 'Edit Order Information'
    #     context = {
    #         'form': form,
    #         'page_title': page_title
    #     }
    #     return render(request, template_name, context)


def personal_info(request, template_name="users/personal-info.html"):
    if request.method == 'POST':
        postdata = request.POST.copy()
        form = PersonalInfoForm(postdata, instance=request.user)
        form_pic = ProfilePicForm(request.POST or None, request.FILES or None, instance=request.user)

        if form.is_valid() and form_pic.is_valid():
            form.save()
            form_pic.save()
            print('form_pic:', form_pic)
            # print('form:', form)

            # set_personal(request)
            set_pic(request)
            messages.success(request, f'Your account information has been updated')
        return redirect('users:profile')

    else:
        user_profile = retrieve_profile(request)
        print('user_profile:', user_profile)
        form = PersonalInfoForm(instance=request.user)
        form_pic = ProfilePicForm(instance=user_profile)
        # print('form',form)
        page_title = 'Edit Personal Information'
        context = {
            'form': form,
            'form_pic': form_pic,
            'page_title': page_title
        }
        return render(request, template_name, context)


class SellerCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = SellerProfile
    template_name = 'users/service_providers/seller_form.html'
    fields = ['first_name', 'last_name', 'business_type', 'tax_country', 'subscription_type']
    success_url = reverse_lazy("users:brand_create")

    def get_queryset(self):
        print('we got here')
        current_app = SellerProfile.objects.filter(user=self.request.user, application_status__lt=20)
        if current_app:
            print('current_app available:', current_app[0].application_status)

    def form_valid(self, form):
        print('registering business')
        obj = form.save(commit=False)
        print('obj:', obj)
        user = self.request.user

        obj.user = user
        obj.save()
        # form.save()
        return super().form_valid(form)

    def test_func(self):
        if not self.request.user.is_seller:
            return True


class BrandCreateView(LoginRequiredMixin, CreateView):
    model = Brand
    template_name = 'users/service_providers/brand_create_form.html'
    fields = ['title', 'image', 'logo']
    success_url = reverse_lazy("users:seller_confirm")

    def form_valid(self, form):
        print('registering brand')
        from django.contrib.auth.models import Group
        obj = form.save(commit=False)
        print('obj:', obj)

        from django.contrib.auth.models import Group
        seller_group = Group.objects.get(name='Sellers')
        obj = form.save(commit=False)
        print('obj:', obj)
        user = self.request.user
        # user_instance = User.objects.get(email=user)
        print(seller_group)
        # print(user_instance)
        seller_group.user_set.add(user)
        user.is_staff = True
        user.save()
        print(user.is_seller)

        obj.user = user
        obj.save()
        # form.save()
        return super().form_valid(form)


class AutomobileCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = AutomobileProfile
    template_name = 'users/service_providers/automobile_profile_form.html'
    fields = ['first_name', 'last_name', 'passport_no', 'automobile_type', 'country', 'city_of_operation']
    success_url = reverse_lazy("users:automobile_confirm")

    def form_valid(self, form):
        # form.save()
        obj = form.save(commit=False)
        user = self.request.user
        # user.is_dispatcher = True
        obj.user = user
        obj.save()
        return super().form_valid(form)

    def test_func(self):
        if not self.request.user.is_dispatcher:
            try:
                print('we got here')
                current_app = AutomobileProfile.objects.filter(user=self.request.user, application_status__lt=20)
                if current_app:
                    print('current_app available:', current_app[0].application_status)
                    return False
            except Exception:
                return True
            return True
