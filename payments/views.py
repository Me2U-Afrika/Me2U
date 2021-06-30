from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from rave_python import Rave, RaveExceptions, Misc
import os

from me2ushop.models import Order

rave = ''


# Create your views here.

def visitor_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    print('ip:', ip)
    return ip


def rave_charge_card(request):
    print('we came to charge card')
    print('rave:', rave)
    print('requst.post:', request.POST)

    cardno = request.POST['cardno']
    expdate = request.POST['expdate']
    expdate = expdate.split('/')

    order_id = request.POST['order_id']
    order = get_object_or_404(Order, id=order_id)

    payload = {
        'cardno': cardno.replace(" ", ""),
        'cvv': request.POST['cvv'],
        'currency': 'KE',
        'country': order.billing_country,
        'expirymonth': expdate[0],
        'expiryyear': expdate[1],
        'amount': str(int(order.get_total())),
        'email': order.email,
        'phonenumber': order.phone,
        'firstname': order.name,
        'IP': visitor_ip_address(request),
    }

    try:
        res = rave.Card.charge(payload)
        print('response:', res)

        if res["suggestedAuth"]:
            print('yes suggested auth')
            arg = Misc.getTypeOfArgsRequired(res["suggestedAuth"])

            if arg == "pin":
                print('We need the Pin')
                Misc.updatePayload(res["suggestedAuth"], payload, pin=request.POST['pin'])
                print('updated payload:', payload)
            if arg == "address":
                Misc.updatePayload(res["suggestedAuth"], payload,
                                   address={"billingzip": "07205", "billingcity": "Hillside",
                                            "billingaddress": "470 Mundet PI", "billingstate": "NJ",
                                            "billingcountry": "US"})

            res = rave.Card.charge(payload)
            print('response-2:', res)

        if res["validationRequired"]:
            rave.Card.validate(res["flwRef"], "12345")

        res = rave.Card.verify(res["txRef"])
        print(res)

    except RaveExceptions.CardChargeError as e:
        print(e.err["errMsg"])
        print(e.err["flwRef"])

    except RaveExceptions.TransactionValidationError as e:
        print(e.err)
        print(e.err["flwRef"])

    except RaveExceptions.TransactionVerificationError as e:
        print(e.err["errMsg"])
        print(e.err["txRef"])

