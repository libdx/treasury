from rest_framework import routers

from project.apps.api.views import AttemptViewSet, TreasureHuntViewSet, UserViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"treasure_hunt.json", TreasureHuntViewSet)
router.register(r"attemps", AttemptViewSet)
