from django.contrib.auth.models import User
from rest_framework import routers, serializers, validators, viewsets

from project.apps.api.models import Attempt


class UserSerializer(serializers.HyperlinkedModelSerializer):
    email = serializers.CharField(
        max_length=255,
        required=True,
        validators=[validators.UniqueValidator(queryset=User.objects.all())],
    )

    class Meta:
        model = User
        fields = ["url", "username", "email", "is_staff", "password"]
        extra_kwargs = {"password": {"write_only": True}}


class AttemptSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attempt
        fields = ["email", "latitude", "longitude", "created_at"]
        extra_kwargs = {
            "latitude": {"required": True},
            "longitude": {"required": True},
            "email": {"required": True},
        }
