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
