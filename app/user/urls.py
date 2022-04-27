from typing import Any
from typing import cast

from django.urls import path
from user.views import CreateTokenView
from user.views import CreateUserView
from user.views import ManageUserView


app_name = "user"


urlpatterns = [
    path("create/", cast(Any, CreateUserView.as_view()), name="create"),
    path("token/", cast(Any, CreateTokenView.as_view()), name="token"),
    path("me/", cast(Any, ManageUserView.as_view()), name="me"),
]
