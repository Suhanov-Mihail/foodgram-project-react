from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngridientViewSet, RecipeViewSet, TagViewSet, CastomUserViewSet

app_name = 'api'

router = DefaultRouter()

router.register('users', CastomUserViewSet)
router.register('ingredients', IngridientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
