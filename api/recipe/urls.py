from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe import views, apps


router = DefaultRouter()


app_name = apps.RecipeConfig.name
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)


urlpatterns = [
    path('', include(router.urls))
]
