from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import (
    CustomUserViewSet, FollowViewSet, IngredientsViewSet,
    RecipesViewSet, TagsViewSet
)

app_name = "api"

router_v1 = DefaultRouter()

router_v1.register("tags", TagsViewSet, basename="tags")
router_v1.register("ingredients", IngredientsViewSet, basename="ingredients")
router_v1.register("recipes", RecipesViewSet, basename="recipes")
router_v1.register("users", CustomUserViewSet, basename="users")

urlpatterns = [
    path(
        "users/subscriptions/",
        FollowViewSet.as_view({"get": "subscriptions_list"}),
        name="user-subscriptions",
    ),
    re_path(
        r"^users/(?P<pk>[^/.]+)/subscribe/$",
        FollowViewSet.as_view(
            {"post": "follow_unfollow", "delete": "follow_unfollow"}
        ),
        name="follow-follow",
    ),
    path("", include(router_v1.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
