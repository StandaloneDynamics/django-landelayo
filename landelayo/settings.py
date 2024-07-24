from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string

from rest_framework.serializers import ModelSerializer


class UserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email')


def get_user_serializer():
    serializer = UserSerializer
    SETTINGS = getattr(settings, 'LANDELAYO_USER_SERIALIZER', None)
    if SETTINGS:
        serializer = import_string(SETTINGS)
    return serializer
