from django.urls import path, include
from rest_framework import routers

from theater_service.views import (
    TicketViewSet,
    ReservationViewSet,
    PerformanceViewSet,
    TheaterHallViewSet,
    PlayViewSet,
    ActorViewSet,
    GenreViewSet,
)


router = routers.DefaultRouter()

router.register("ticket", TicketViewSet)
router.register("reservation", ReservationViewSet)
router.register("performance", PerformanceViewSet)
router.register("theater_hall", TheaterHallViewSet)
router.register("play", PlayViewSet)
router.register("actor", ActorViewSet)
router.register("genre", GenreViewSet)


urlpatterns = [path("", include(router.urls))]

app_name = "theater_service"
