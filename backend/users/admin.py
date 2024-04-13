from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import Follow, User


class UserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "email",
    )
    search_fields = ("id", "username")
    list_filter = ("email", "username")


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "following",
    )
    search_fields = ("user", "following")
    list_filter = ("user__username",)


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
