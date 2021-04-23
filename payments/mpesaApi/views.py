from django.contrib.auth.models import User
from rest_framework.permissions import IsAdminUser, AllowAny
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

        merchant_request_id = request.data["Body"]["stkCallback"]["MerchantID"]
        print("merchant_id:", merchant_request_id)
        checkout_request_id = request.data["Body"]["stkCallback"]["CheckoutRequestID"]
        result_code = request.data["Body"]["stkCallback"]["ResultCode"]
        result_description = request.data["Body"]["stkCallback"]["ResultDesc"]
        amount = request.data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][0]["value"]
        print("amount:", amount)
        mpesa_receipt_number = request.data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][1]["value"]
        transaction_date = request.data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][3]["value"]
        phone_number = request.data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][4]["value"]
        print(phone_number)

        transaction_date = request.data["Body"]
        from datetime import datetime
        str_transaction_date = str(transaction_date)

        print(str_transaction_date)

        transaction_datetime = datetime.strptime(str_transaction_date, "%Y%m%d%H%M%S")
        print(transaction_datetime)

        our_model = LNMOnline.objects.create(
            CheckoutRequestID=checkout_request_id,
            MerchantRequestID=merchant_request_id,
            ResultCode=result_code,
            ResultDesc=result_description,
            Amount=amount,
            MpesaReceiptNumber=mpesa_receipt_number,
            TransactionDate=transaction_datetime,
            PhoneNumber=phone_number
        )
        our_model.save()
