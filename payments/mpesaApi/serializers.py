from rest_framework import serializers
from payments.models import *


class LNMOnlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = LNMOnline
        fields = ('id',)
