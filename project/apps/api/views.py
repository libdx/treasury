from django.contrib.auth.models import User
from rest_framework import mixins, routers, serializers, viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from project.apps.api.models import Attempt, Treasure
from project.apps.api.serializers import AttemptSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Represents 'users' endpoint."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegisterUserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer


register_user = RegisterUserViewSet.as_view({"post": "create"})


class TreasureHuntViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer

    def create(self, request):
        serializer = AttemptSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                status=400,
                data={"status": "error", "distance": -1, "error": serializer.errors},
            )

        try:
            attempt = serializer.save()
            distance = attempt.verify()
        except ValueError as error:
            return Response(
                status=500,
                data={
                    "status": "error",
                    "distance": -1,
                    "error": "No treasures were yet hidden",
                },
            )

        return Response(status=201, data={"status": "ok", "distance": distance})


class AttemptViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer
