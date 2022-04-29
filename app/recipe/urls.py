from django.urls import include
from django.urls import path
from recipe.views import IngredientViewSet
from recipe.views import RecipeViewSet
from recipe.views import TagViewSet
from rest_framework.routers import DefaultRouter


app_name = "recipe"


router = DefaultRouter()
router.register("tags", TagViewSet)
router.register("ingredients", IngredientViewSet)
router.register("recipes", RecipeViewSet)
urlpatterns = [path("", include(router.urls))]
