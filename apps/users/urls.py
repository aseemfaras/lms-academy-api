from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomTokenObtainPairView, UserListView, RegisterView, UserDeleteView

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', UserListView.as_view(), name='user-list'),
    path('register/', RegisterView.as_view(), name='user-register'),
    path('<int:pk>/', UserDeleteView.as_view(), name='user-delete'),
]
