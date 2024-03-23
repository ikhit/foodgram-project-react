from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientsViewSet,
    TagsViewSet,
    RecipesViewSet,
    FollowViewSet,
)

app_name = "api"

router_v1 = DefaultRouter()

router_v1.register("tags", TagsViewSet, basename="tags")
router_v1.register("ingredients", IngredientsViewSet, basename="ingredients")
router_v1.register("recipes", RecipesViewSet, basename="recipes")
router_v1.register("users", FollowViewSet, basename="follow")

urlpatterns = [
    path(
        "users/subscriptions/",
        FollowViewSet.as_view({"get": "subscribers_list"}),
        name="user-subscriptions",
    ),
    path("", include("djoser.urls")),
    path("", include(router_v1.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
