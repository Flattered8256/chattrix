from __future__ import annotations
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, RefreshView, LogoutView, SearchUserView, UserProfileView, User_get_ProfileView, ChangePasswordView

router = DefaultRouter()
router.register(r'register', RegisterView, basename='register')


urlpatterns = [
    path('', include(router.urls)),
    
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("search/", SearchUserView.as_view(), name="search"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("getprofile/", User_get_ProfileView.as_view(), name="getprofile"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
]