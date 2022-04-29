from django.conf import settings
from django.conf.urls.static import static
from django.contrib.admin import site
from django.urls import URLPattern
from django.urls import URLResolver
from django.urls import include
from django.urls import path


urlpatterns: list[URLResolver | URLPattern] = [
    path("admin/", site.urls),
    path("api/user/", include("user.urls")),
    path("api/recipe/", include("recipe.urls")),
]
urlpatterns.extend(
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
