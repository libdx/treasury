from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from project.apps.api.models import Attempt


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "is_staff"]
        extra_kwargs = {"password": {"write_only": True}}


class AttemptSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attempt
        fields = ["email", "latitude", "longitude", "created_at"]
