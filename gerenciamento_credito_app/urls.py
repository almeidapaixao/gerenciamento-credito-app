from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from .app.views import ContratoViewSet, TokenObtainFor30DaysView


router = DefaultRouter()
router.register(r'contratos', ContratoViewSet)


urlpatterns = [
    path('api', include(router.urls)),
    path('admin', admin.site.urls),
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/30days', TokenObtainFor30DaysView.as_view(), name='token_obtain_30days'),
]