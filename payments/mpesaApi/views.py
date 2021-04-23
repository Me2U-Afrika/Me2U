from django.contrib.auth.models import User
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response

from payments.mpesaApi.serializers import LNMOnlineSerializer
from rest_framework.generics import CreateAPIView

from payments.models import LNMOnline


class LNMCallbackAPIView(CreateAPIView):
    queryset = LNMOnline.objects.all()
    serializer_class = LNMOnlineSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        print(request.data, "request data")

        # Requested data
        {'Body': {
            'stkCallback': {
                'MerchantRequestID': '4815-7950460-1',
                'CheckoutRequestID': 'ws_CO_230420211641334548',
                'ResultCode': 0,
                'ResultDesc': 'The service request is processed successfully.',
                'CallbackMetadata': {'Item':
                                         [{'Name': 'Amount', 'Value': 1.0},
                                          {'Name': 'MpesaReceiptNumber', 'Value': 'PDN25VFARY'},
                                          {'Name': 'Balance'},
                                          {'Name': 'TransactionDate', 'Value': 20210423164140},
                                          {'Name': 'PhoneNumber', 'Value': 254792585134}]
                                     }
            }
        }
        }

        merchant_request_id = request.data["Body"]["stkCallback"]["MerchantRequestID"]
        print("merchant_id:", merchant_request_id)
        checkout_request_id = request.data["Body"]["stkCallback"]["CheckoutRequestID"]
        result_code = request.data["Body"]["stkCallback"]["ResultCode"]
        result_description = request.data["Body"]["stkCallback"]["ResultDesc"]
        amount = request.data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][0]["Value"]
        print("amount:", amount)
        mpesa_receipt_number = request.data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][1]["Value"]
        transaction_date = request.data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][3]["Value"]
        phone_number = request.data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][4]["Value"]
        print(phone_number)

        from datetime import datetime
        import pytz

        str_transaction_date = str(transaction_date)

        print(str_transaction_date)

        transaction_datetime = datetime.strptime(str_transaction_date, "%Y%m%d%H%M%S")
        print(transaction_datetime)

        aware_transaction_datetime = pytz.utc.localize(transaction_datetime)
        print("aware time:", aware_transaction_datetime)

        our_model = LNMOnline.objects.create(
            CheckoutRequestID=checkout_request_id,
            MerchantRequestID=merchant_request_id,
            ResultCode=result_code,
            ResultDesc=result_description,
            Amount=amount,
            MpesaReceiptNumber=mpesa_receipt_number,
            TransactionDate=aware_transaction_datetime,
            PhoneNumber=phone_number
        )
        our_model.save()

        return Response({"OurResultDesc": "Congratulations!! It Worked!"})
