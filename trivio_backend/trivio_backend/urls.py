from django.urls import path

from trivio_backend.core import views
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('api/v1/auth/signup/', views.auth_signup),
    path('api/v1/auth/login/', jwt_views.TokenObtainPairView.as_view()),
    path('api/v1/auth/refresh/', jwt_views.TokenRefreshView.as_view()),
    path('api/v1/posts/', views.PostItems.as_view()),
    path('api/v1/posts/<int:pk>/', views.PostItemDetail.as_view()),
    path('api/v1/posts/<int:pk>/like/', views.like_post),
    path('api/v1/posts/<int:pk>/unlike/', views.unlike_post),
]


