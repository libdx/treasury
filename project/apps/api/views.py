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

        attempt = serializer.save()
        treasure = Treasure.objects.first()
        distance = attempt.distance_to(treasure)

        return Response(status=201, data={"status": "ok", "distance": distance})


class AttemptViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer


class TreasureHuntQueryParamsView(APIView):
    """Represents 'treasure_hunt.json' endpoint with handling query params."""

    permission_classes = [AllowAny]

    def post(self, request, format=None):
        loc = request.query_params.getlist("loc[]")
        data = {
            "user": str(request.user),
            "auth": str(request.auth),
            "loc": loc,
            "request.data": request.data,
        }

        if len(loc) < 2:
            data = {
                "status": "error",
                "message": "loc[] query params requires 2 elements",
            }
            return Response(
                status=400,
                data=data,
            )

        return Response(data)
