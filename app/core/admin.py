from core.models import Ingredient
from core.models import Tag
from core.models import User
from django.contrib.admin import site
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext


class UserAdmin(BaseUserAdmin):
    ordering = ["id"]
    list_display = ["email", "name"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        (gettext("Personal Info"), {"fields": ["name"]}),
        (
            gettext("Permissions"),
            {"fields": ["is_active", "is_staff", "is_superuser"]},
        ),
        (gettext("Important dates"), {"fields": ["last_login"]}),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "password1", "password2"],
            },
        )
    ]


site.register(User, UserAdmin)
site.register(Tag)
site.register(Ingredient)
