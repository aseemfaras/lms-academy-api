from rest_framework import viewsets, permissions
from .models import Enrollment
from trainers.serializers import CourseListSerializer


class EnrollmentViewSetNew(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        from rest_framework import serializers
        from .models import Enrollment

        class InlineEnrollmentSerializer(serializers.ModelSerializer):
            class Meta:
                model = Enrollment
                fields = ['id', 'student', 'course', 'batch', 'enrolled_at', 'status']
                read_only_fields = ['student', 'enrolled_at']

            def to_representation(self, instance):
                data = super().to_representation(instance)
                if instance.course:
                    data['course'] = CourseListSerializer(
                        instance.course,
                        context=self.context,
                    ).data
                return data

        return InlineEnrollmentSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Enrollment.objects.filter(course__isnull=False).select_related('course', 'student')

        student_id = self.request.query_params.get('student')
        if student_id and user.role == 'ADMIN':
            return queryset.filter(student_id=student_id)

        if user.role == 'ADMIN':
            return queryset

        return queryset.filter(student=user)

    def perform_create(self, serializer):
        from users.models import User
        from rest_framework.exceptions import ValidationError

        email = self.request.data.get('email')
        batch = self.request.data.get('batch', 'Batch 1')

        if self.request.user.role == 'ADMIN' and email:
            try:
                student = User.objects.get(email=email)
            except User.DoesNotExist:
                raise ValidationError({"email": "User with this email does not exist."})
            serializer.save(student=student, batch=batch)
            return

        serializer.save(student=self.request.user, batch=batch)
