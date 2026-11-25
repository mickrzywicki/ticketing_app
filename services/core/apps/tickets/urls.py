from rest_framework.routers import DefaultRouter

from .views import TicketViewSet

# Rails: resources :tickets
router = DefaultRouter()
router.register("tickets", TicketViewSet, basename="ticket")

urlpatterns = router.urls
