from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnrollmentViewSetNew

router = DefaultRouter()
router.register(r'enrollments', EnrollmentViewSetNew, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
]
