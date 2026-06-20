from rest_framework import viewsets, permissions, decorators, response, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView

from .models import Course, Module, LiveSession, ActivityLog, Batch
from .serializers import (
    CourseListSerializer,
    CourseDetailSerializer,
    ModuleSerializer,
    LiveSessionSerializer,
    ActivityLogSerializer,
    BatchSerializer,
)
from users.permissions import IsAdminUser, IsAdminOrEnrolledStudent


class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrEnrolledStudent]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Course.objects.all()
        is_trainer_view = self.request.query_params.get('trainer') == 'true'

        if user.role == 'ADMIN' and not is_trainer_view:
            return queryset.order_by('-created_at')

        if user.role == 'TRAINER' or is_trainer_view:
            return queryset.filter(
                trainerassignment__trainer=user
            ).distinct().order_by('-created_at')

        return queryset.filter(enrollments__student=user).distinct().order_by('-created_at')

    def perform_create(self, serializer):
        if self.request.user.role != 'ADMIN':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins can create courses.")
        course = serializer.save()
        Batch.objects.create(course=course, name="Batch 1")

    def update(self, request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            return response.Response(
                {"detail": "Only admins can update courses."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            return response.Response(
                {"detail": "Only admins can update courses."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            return response.Response(
                {"detail": "Only admins can delete courses."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @decorators.action(detail=True, methods=['post'])
    def batches(self, request, pk=None):
        if request.user.role != 'ADMIN':
            return response.Response({"detail": "Only admins can create batches."}, status=403)
        course = self.get_object()
        name = request.data.get('name')
        if not name:
            return response.Response({"error": "Batch name is required"}, status=400)

        batch, created = Batch.objects.get_or_create(course=course, name=name)
        if not created:
            return response.Response({"error": "Batch already exists for this course"}, status=400)

        return response.Response(BatchSerializer(batch).data, status=201)

    @decorators.action(detail=True, methods=['post'])
    def assign_trainer(self, request, pk=None):
        if request.user.role != 'ADMIN':
            return response.Response({"detail": "Only admins can assign trainers."}, status=403)
        course = self.get_object()
        email = request.data.get('email')
        name = request.data.get('name')
        batch = request.data.get('batch', 'Batch 1')
        if not email:
            return response.Response({"error": "Email is required"}, status=400)

        from django.contrib.auth import get_user_model
        from .models import TrainerAssignment
        User = get_user_model()
        try:
            trainer = User.objects.get(email=email, role='TRAINER')
            if name:
                trainer.full_name = name
                trainer.save()
            TrainerAssignment.objects.get_or_create(course=course, trainer=trainer, batch=batch)
            return response.Response({
                "message": f"Trainer {trainer.full_name or trainer.username} assigned successfully to {batch}"
            })
        except User.DoesNotExist:
            if User.objects.filter(email=email).exists():
                return response.Response({"error": "User found but is not a trainer"}, status=400)
            return response.Response({"error": "Trainer with this email not found"}, status=404)

    @decorators.action(detail=True, methods=['post'])
    def toggle_trainer_activation(self, request, pk=None):
        if request.user.role != 'ADMIN':
            return response.Response({"error": "Only admins can change trainer status"}, status=403)

        course = self.get_object()
        user_id = request.data.get('user_id')
        is_active = request.data.get('is_active')
        batch = request.data.get('batch', 'Batch 1')

        if user_id is None or is_active is None:
            return response.Response({"error": "user_id and is_active are required"}, status=400)

        from .models import TrainerAssignment
        try:
            assignment = TrainerAssignment.objects.get(
                course=course, trainer_id=user_id, batch=batch
            )
            assignment.is_active = is_active
            assignment.save()
            return response.Response({
                "message": f"Trainer activation status updated to {'Active' if is_active else 'Inactive'}",
                "is_active": assignment.is_active,
            })
        except TrainerAssignment.DoesNotExist:
            return response.Response({"error": "Trainer assignment not found for this batch"}, status=404)

    @decorators.action(detail=True, methods=['post'])
    def unassign_trainer(self, request, pk=None):
        if request.user.role != 'ADMIN':
            return response.Response({"detail": "Only admins can unassign trainers."}, status=403)
        course = self.get_object()
        user_id = request.data.get('user_id')
        batch = request.data.get('batch', 'Batch 1')
        if not user_id:
            return response.Response({"error": "User ID is required"}, status=400)

        from .models import TrainerAssignment
        TrainerAssignment.objects.filter(course=course, trainer_id=user_id, batch=batch).delete()
        return response.Response({"message": "Trainer unassigned successfully from this batch"})


class ModuleViewSet(viewsets.ModelViewSet):
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrEnrolledStudent]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        queryset = Module.objects.all()

        if user.role == 'ADMIN':
            course_id = self.request.query_params.get('course')
            if course_id:
                queryset = queryset.filter(course_id=course_id)
            return queryset.order_by('order')

        if user.role == 'TRAINER':
            course_id = self.request.query_params.get('course')
            assignments = user.trainerassignment_set.all()
            if course_id:
                assignments = assignments.filter(course_id=course_id)
                queryset = queryset.filter(course_id=course_id)

            allowed_batches_by_course = {}
            for a in assignments:
                allowed_batches_by_course.setdefault(a.course_id, set()).add(a.batch)

            filtered_querysets = []
            for c_id, batches in allowed_batches_by_course.items():
                filtered_querysets.append(queryset.filter(course_id=c_id, batch__in=batches))

            if filtered_querysets:
                q = filtered_querysets[0]
                for other_q in filtered_querysets[1:]:
                    q = q | other_q
                return q.distinct().order_by('order')
            return queryset.none()

        if user.role == 'STUDENT':
            course_id = self.request.query_params.get('course')
            enrollments = user.enrollments.all()
            if course_id:
                enrollments = enrollments.filter(course_id=course_id)
                queryset = queryset.filter(course_id=course_id)

            allowed_batches_by_course = {}
            for e in enrollments:
                allowed_batches_by_course.setdefault(e.course_id, set()).add(e.batch)

            filtered_querysets = []
            for c_id, batches in allowed_batches_by_course.items():
                filtered_querysets.append(queryset.filter(course_id=c_id, batch__in=batches))

            if filtered_querysets:
                q = filtered_querysets[0]
                for other_q in filtered_querysets[1:]:
                    q = q | other_q
                return q.distinct().order_by('order')
            return queryset.none()

        return queryset.none()

    def perform_create(self, serializer):
        if self.request.user.role not in ['ADMIN', 'TRAINER']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins or trainers can add modules.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            return response.Response(
                {"detail": "Only admins can delete modules."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @decorators.action(detail=True, methods=['get'], url_path='download-notes')
    def download_notes(self, request, pk=None):
        module = self.get_object()
        if not module.notes_binary:
            return response.Response({"error": "No notes found for this module"}, status=404)

        from django.http import HttpResponse
        content_type = module.notes_content_type or 'application/octet-stream'
        filename = module.notes_filename or f"notes_{module.id}"
        resp = HttpResponse(module.notes_binary, content_type=content_type)
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp


class LiveSessionViewSet(viewsets.ModelViewSet):
    serializer_class = LiveSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = LiveSession.objects.all()
        is_trainer_query = self.request.query_params.get('trainer') == 'true'
        is_student_query = self.request.query_params.get('student') == 'true'
        course_id = self.request.query_params.get('course_id')

        if user.role == 'ADMIN' and not is_trainer_query:
            if course_id:
                queryset = queryset.filter(course_id=course_id)
            return queryset.order_by('scheduled_date', 'start_time')

        if user.role == 'TRAINER' or is_trainer_query:
            assignments = user.trainerassignment_set.filter(is_active=True)
            if course_id:
                assignments = assignments.filter(course_id=course_id)
                queryset = queryset.filter(course_id=course_id)

            allowed_batches_by_course = {}
            for a in assignments:
                allowed_batches_by_course.setdefault(a.course_id, set()).add(a.batch)

            filtered_querysets = []
            for c_id, batches in allowed_batches_by_course.items():
                filtered_querysets.append(queryset.filter(course_id=c_id, batch__in=batches))

            if filtered_querysets:
                q = filtered_querysets[0]
                for other_q in filtered_querysets[1:]:
                    q = q | other_q
                return q.distinct().order_by('scheduled_date', 'start_time')
            return queryset.none()

        if user.role == 'STUDENT' or is_student_query:
            enrollments = user.enrollments.all()
            if course_id:
                enrollments = enrollments.filter(course_id=course_id)
                queryset = queryset.filter(course_id=course_id)

            allowed_batches_by_course = {}
            for e in enrollments:
                allowed_batches_by_course.setdefault(e.course_id, set()).add(e.batch)

            filtered_querysets = []
            for c_id, batches in allowed_batches_by_course.items():
                filtered_querysets.append(queryset.filter(course_id=c_id, batch__in=batches))

            if filtered_querysets:
                q = filtered_querysets[0]
                for other_q in filtered_querysets[1:]:
                    q = q | other_q
                return q.distinct().order_by('scheduled_date', 'start_time')
            return queryset.none()

        return queryset.none()

    def perform_create(self, serializer):
        if self.request.user.role != 'ADMIN':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins can create live sessions.")
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        if self.request.user.role not in ['ADMIN', 'TRAINER']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins or trainers can update live sessions.")
        updated_instance = serializer.save()

        if updated_instance.recording_url:
            module = Module.objects.filter(
                course=updated_instance.course,
                video_url=updated_instance.recording_url,
            ).first()
            if not module:
                Module.objects.create(
                    course=updated_instance.course,
                    title=f"Recording: {updated_instance.title}",
                    video_url=updated_instance.recording_url,
                    batch=updated_instance.batch,
                    order=updated_instance.course.modules.count() + 1,
                )


from rest_framework.generics import ListAPIView


class TrainerActivityView(ListAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != 'TRAINER':
            return ActivityLog.objects.none()
        assigned_courses = Course.objects.filter(trainerassignment__trainer=user)
        return ActivityLog.objects.filter(related_course__in=assigned_courses).order_by('-created_at')[:10]


class UploadRecordingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if request.user.role != 'TRAINER':
            return response.Response(
                {"detail": "Only trainers can upload recordings."},
                status=status.HTTP_403_FORBIDDEN,
            )

        session_id = request.data.get('session_id')
        recording = request.FILES.get('recording')
        if not session_id:
            return response.Response({"session_id": ["This field is required."]}, status=400)
        if not recording:
            return response.Response({"recording": ["No file uploaded."]}, status=400)

        try:
            session = LiveSession.objects.get(pk=session_id)
        except LiveSession.DoesNotExist:
            return response.Response({"error": "Live session not found."}, status=404)

        import os
        from django.conf import settings
        recordings_dir = os.path.join(settings.MEDIA_ROOT, 'recordings')
        os.makedirs(recordings_dir, exist_ok=True)
        filename = f"session_{session_id}_{recording.name}"
        filepath = os.path.join(recordings_dir, filename)
        with open(filepath, 'wb+') as dest:
            for chunk in recording.chunks():
                dest.write(chunk)

        relative_url = f"{settings.MEDIA_URL}recordings/{filename}"
        session.recording_url = request.build_absolute_uri(relative_url)
        session.save()

        Module.objects.get_or_create(
            course=session.course,
            video_url=session.recording_url,
            defaults={
                'title': f"Recording: {session.title}",
                'batch': session.batch,
                'order': session.course.modules.count() + 1,
            },
        )

        return response.Response({
            "message": "Recording uploaded successfully.",
            "recording_url": session.recording_url,
        }, status=201)
