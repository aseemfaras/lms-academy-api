from rest_framework import viewsets, permissions, decorators, response

from .models import Course, Module, LiveSession, ActivityLog, Batch
from .serializers import CourseSerializer, ModuleSerializer, LiveSessionSerializer, ActivityLogSerializer, BatchSerializer
from users.permissions import IsAdminUser, IsAdminOrEnrolledStudent

class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrEnrolledStudent]

    def get_queryset(self):
        user = self.request.user
        queryset = Course.objects.all()
        
        # Determine if we should filter by trainer assignment
        # If user is a trainer, or if it's an admin explicitly looking for their trainer view
        is_trainer_view = self.request.query_params.get('trainer') == 'true'
        
        if user.role == 'ADMIN' and not is_trainer_view:
            return queryset.order_by('-created_at')
        
        if user.role == 'TRAINER' or is_trainer_view:
            # Return all courses where the trainer is assigned (active or inactive)
            # This ensures dashboard stats (counts) are accurate
            return queryset.filter(
                trainerassignment__trainer=user
            ).distinct().order_by('-created_at')
        
        # For students, only return courses they are enrolled in
        return queryset.filter(enrollments__student=user).distinct().order_by('-created_at')

    def perform_create(self, serializer):
        if self.request.user.role != 'ADMIN':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins can create courses.")
        # When creating, the admin isn't necessarily a trainer. 
        # But for now, we'll save without assigning a trainer automatically, 
        # or we can assign the creating admin if needed.
        course = serializer.save()
        Batch.objects.create(course=course, name="Batch 1")

    @decorators.action(detail=True, methods=['post'])
    def batches(self, request, pk=None):
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
            return response.Response({"message": f"Trainer {trainer.full_name or trainer.username} assigned successfully to {batch}"})

        except User.DoesNotExist:
            # Maybe the user exists but isn't a trainer?
            if User.objects.filter(email=email).exists():
                 return response.Response({"error": "User found but is not a trainer"}, status=400)
            return response.Response({"error": "Trainer with this email not found"}, status=404)

    @decorators.action(detail=True, methods=['post'])
    def toggle_trainer_activation(self, request, pk=None):
        if request.user.role != 'ADMIN':
            from rest_framework import response
            return response.Response({"error": "Only admins can change trainer status"}, status=403)
        
        course = self.get_object()
        user_id = request.data.get('user_id')
        is_active = request.data.get('is_active')
        batch = request.data.get('batch', 'Batch 1')
        
        if user_id is None or is_active is None:
            from rest_framework import response
            return response.Response({"error": "user_id and is_active are required"}, status=400)
            
        from .models import TrainerAssignment
        from rest_framework import response
        try:
            assignment = TrainerAssignment.objects.get(course=course, trainer_id=user_id, batch=batch)
            print(f"DEBUG Toggle: Found assignment for course {course.id}, trainer {user_id}, batch {batch}. Current is_active: {assignment.is_active}, New is_active: {is_active}")
            assignment.is_active = is_active
            assignment.save()
            print(f"DEBUG Toggle: Saved. New state: {assignment.is_active}")
            return response.Response({
                "message": f"Trainer activation status updated to {'Active' if is_active else 'Inactive'}",
                "is_active": assignment.is_active
            })
        except TrainerAssignment.DoesNotExist:
            return response.Response({"error": "Trainer assignment not found for this batch"}, status=404)

    @decorators.action(detail=True, methods=['post'])
    def unassign_trainer(self, request, pk=None):
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

    def get_queryset(self):
        user = self.request.user
        queryset = Module.objects.all()
        
        # Admin can see all
        if user.role == 'ADMIN':
            course_id = self.request.query_params.get('course')
            if course_id:
                queryset = queryset.filter(course_id=course_id)
            return queryset.order_by('order')
        
        # Trainers see modules for courses they are assigned to, optionally matching batch
        if user.role == 'TRAINER':
            course_id = self.request.query_params.get('course')
            # Important: Get assignments to know which batches trainer has access to
            assignments = user.trainerassignment_set.all()
            if course_id:
               assignments = assignments.filter(course_id=course_id)
               queryset = queryset.filter(course_id=course_id)
            
            # The trainer only sees modules that belong to a batch they are assigned to for that course
            allowed_batches_by_course = {}
            for a in assignments:
                allowed_batches_by_course.setdefault(a.course_id, set()).add(a.batch)
                
            filtered_querysets = []
            for c_id, batches in allowed_batches_by_course.items():
                filtered_querysets.append(queryset.filter(course_id=c_id, batch__in=batches))
                
            from django.db.models import Q
            if filtered_querysets:
                # Combine querysets
                q = filtered_querysets[0]
                for other_q in filtered_querysets[1:]:
                    q = q | other_q
                return q.distinct().order_by('order')
            else:
                return queryset.none()
        
        # Students only see modules for courses they are enrolled in and batches they are in
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
                
            from django.db.models import Q
            if filtered_querysets:
                q = filtered_querysets[0]
                for other_q in filtered_querysets[1:]:
                    q = q | other_q
                return q.distinct().order_by('order')
            else:
                return queryset.none()
            
        return queryset.none()

    def perform_create(self, serializer):
        if self.request.user.role not in ['ADMIN', 'TRAINER']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins or trainers can add modules.")
        serializer.save()

    @decorators.action(detail=True, methods=['get'], url_path='download-notes')
    def download_notes(self, request, pk=None):
        module = self.get_object()
        if not module.notes_binary:
            return response.Response({"error": "No notes found for this module"}, status=404)
        
        from django.http import HttpResponse
        import mimetypes
        
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

        # Handle explicit query parameters
        is_trainer_query = self.request.query_params.get('trainer') == 'true'
        is_student_query = self.request.query_params.get('student') == 'true'
        course_id = self.request.query_params.get('course_id')

        # Admin view
        if user.role == 'ADMIN' and not is_trainer_query:
            if course_id:
                queryset = queryset.filter(course_id=course_id)
            return queryset.order_by('scheduled_date', 'start_time')
        
        # Trainer view
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
                
            from django.db.models import Q
            if filtered_querysets:
                q = filtered_querysets[0]
                for other_q in filtered_querysets[1:]:
                    q = q | other_q
                return q.distinct().order_by('scheduled_date', 'start_time')
            else:
                return queryset.none()
        
        # Student view
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
                
            from django.db.models import Q
            if filtered_querysets:
                q = filtered_querysets[0]
                for other_q in filtered_querysets[1:]:
                    q = q | other_q
                return q.distinct().order_by('scheduled_date', 'start_time')
            else:
                return queryset.none()

        return queryset.none()

    def perform_create(self, serializer):
        if self.request.user.role != 'ADMIN':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins can create live sessions.")
        serializer.save(created_by=self.request.user)


    def perform_update(self, serializer):
        # Save the update without any timing restrictions
        updated_instance = serializer.save()
        
        # Module creation logic: Trigger when recording_url is added/updated
        if updated_instance.recording_url:
            # Try to find an existing module for this course with this specific video URL
            module = Module.objects.filter(course=updated_instance.course, video_url=updated_instance.recording_url).first()
            
            if not module:
                # Create if doesn't exist
                Module.objects.create(
                    course=updated_instance.course,
                    title=f"Recording: {updated_instance.title}",
                    video_url=updated_instance.recording_url,
                    order=updated_instance.course.modules.count() + 1
                )

from rest_framework.generics import ListAPIView

class TrainerActivityView(ListAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # Only trainers/admins should access this
        if user.role not in ['TRAINER', 'ADMIN']:
            return ActivityLog.objects.none()

        # Get courses assigned to this trainer
        assigned_courses = Course.objects.filter(trainerassignment__trainer=user)
        
        # Get latest 10 activities for these courses
        return ActivityLog.objects.filter(related_course__in=assigned_courses).order_by('-created_at')[:10]


