from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    ModuleViewSet,
    LiveSessionViewSet,
    TrainerActivityView,
    UploadRecordingView,
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'modules', ModuleViewSet, basename='module')
router.register(r'live-sessions', LiveSessionViewSet, basename='livesession')

urlpatterns = [
    path('trainer-activities/', TrainerActivityView.as_view(), name='trainer-activities'),
    path('upload-recording/', UploadRecordingView.as_view(), name='upload-recording'),
    path('', include(router.urls)),
]
