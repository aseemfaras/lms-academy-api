from rest_framework import viewsets, permissions
from .models import Enrollment
from .serializers import EnrollmentSerializer

class EnrollmentViewSetNew(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        from rest_framework import serializers
        from .models import Enrollment
        from trainers.serializers import CourseSerializer
        from users.serializers import UserSerializer

        class InlineEnrollmentSerializer(serializers.ModelSerializer):
            course_title = serializers.ReadOnlyField(source='course.title')
            
            class Meta:
                model = Enrollment
                fields = ['id', 'student', 'course', 'course_title', 'enrolled_at', 'status']
                read_only_fields = ['student', 'enrolled_at']
                
            def to_representation(self, instance):
                data = super().to_representation(instance)
                if instance.course:
                    # CourseSerializer already provides trainer_name/instructor_name
                    data['course'] = CourseSerializer(instance.course).data
                return data
        
        return InlineEnrollmentSerializer

    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'ADMIN':
            return Enrollment.objects.filter(course__isnull=False).select_related('course', 'student')
        
        # Simple and direct: get enrollments for the logged-in student
        return Enrollment.objects.filter(
            student=user,
            course__isnull=False
        ).select_related('course', 'student')


    def perform_create(self, serializer):
        from users.models import User
        course_id = self.request.data.get('course')
        email = self.request.data.get('email')
        batch = self.request.data.get('batch', 'Batch 1')
        
        if self.request.user.role == 'ADMIN' and email:
            try:
                student = User.objects.get(email=email)
                serializer.save(student=student, batch=batch)
                return
            except User.DoesNotExist:
                # If user doesn't exist, we might want to create a guest account or error
                # For now, let's assume we need to handle this. 
                # Raise error if student not found
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"email": "User with this email does not exist."})
        
        serializer.save(student=self.request.user, batch=batch)
