from django.contrib.auth.models import User
from payments.mpesaApi.serializers import LNMOnlineSerializer
from rest_framework.generics import CreateAPIView

from payments.models import LNMOnline


class LNMCallbackAPIView(CreateAPIView):
    queryset = LNMOnline.objects.all()
    serializer_class = LNMOnlineSerializer

    # permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        print(request.data, "request data")
