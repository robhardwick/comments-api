from django.conf.urls import url, include
from rest_framework import routers

from .views import CommentViewSet

router = routers.DefaultRouter()
router.register(r'', CommentViewSet)

urlpatterns = [
    url(r'^', include(router.urls, namespace='api')),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
]
