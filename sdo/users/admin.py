from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from tasks.models import UserTaskCaseRelation, UserTaskRelation, Variant
from users.models import User

# admin.site.register(User)

class UserTaskCaseRelationInline(admin.TabularInline):
    model = UserTaskCaseRelation
    extra = 1


class UserTaskRelationInline(admin.TabularInline):
    model = UserTaskRelation
    extra = 1


# class VariantInline(admin.TabularInline):
#     model = Variant
#     extra = 1

@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
    )
    inlines = (UserTaskCaseRelationInline, UserTaskRelationInline)
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
        (None, {"fields": ('variants',)}),
    )
