from typing import Any
from typing import cast

from django.urls import path
from user.views import CreateTokenView
from user.views import CreateUserView


app_name = "user"


urlpatterns = [
    path("create/", cast(Any, CreateUserView.as_view()), name="create"),
    path("token/", cast(Any, CreateTokenView.as_view()), name="token"),
]
