from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User

# admin.site.register(User)


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
    )
    fieldsets = (
        (None, {"fields": ('username', "email", "password")}),
        (("Личные данные"), {"fields": ("first_name", "last_name")}),
        (("Полномочия"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        },
         ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
