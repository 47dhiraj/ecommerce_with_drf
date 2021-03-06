from django.urls import path

from ecom_api.views import user_views as views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns = [

    path('', views.getUsers, name="users"),
    
    path('register/', views.registerUser, name='register'),
    
    path('login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('profile/', views.getUserProfile, name="users-profile"),

    path('profile/update/', views.updateUserProfile, name="user-profile-update"),

]

