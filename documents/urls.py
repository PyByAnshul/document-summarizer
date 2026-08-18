
from rest_framework.routers import SimpleRouter

from .views import DocumentsViewSet

router = SimpleRouter()


router.register(
    r"documents",
    DocumentsViewSet,
    basename="documents",
)

urlpatterns = router.urls