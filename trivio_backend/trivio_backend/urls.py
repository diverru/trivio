from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from trivio_backend.core.views import auth, posts

urlpatterns = [
    path('api/v1/auth/enrich/', auth.enrich),
    path('api/v1/auth/signup/', auth.auth_signup),
    path('api/v1/auth/login/', jwt_views.TokenObtainPairView.as_view()),
    path('api/v1/auth/refresh/', jwt_views.TokenRefreshView.as_view()),
    path('api/v1/posts/', posts.PostItems.as_view()),
    path('api/v1/posts/<int:pk>/', posts.PostItemDetail.as_view()),
    path('api/v1/posts/<int:pk>/like/', posts.like_post),
    path('api/v1/posts/<int:pk>/unlike/', posts.unlike_post),
]
