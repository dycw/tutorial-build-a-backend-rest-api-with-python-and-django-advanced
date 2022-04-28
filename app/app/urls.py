from django.contrib.admin import site
from django.urls import include
from django.urls import path


urlpatterns = [
    path("admin/", site.urls),
    path("api/user/", include("user.urls")),
    path("api/recipe/", include("recipe.urls")),
]
