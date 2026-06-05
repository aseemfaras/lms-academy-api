from rest_framework import serializers
from .models import Enrollment
from users.serializers import UserSerializer
from trainers.serializers import CourseSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source='course.title')
    
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'course_title', 'batch', 'enrolled_at', 'status']
        read_only_fields = ['student', 'enrolled_at']

    def to_representation(self, instance):
        # HARD OVERRIDE
        from trainers.serializers import CourseSerializer
        from users.serializers import UserSerializer
        
        rep = super().to_representation(instance)
        rep['course'] = CourseSerializer(instance.course).data if instance.course else None
        rep['student'] = UserSerializer(instance.student).data if instance.student else None
        rep['NESTED_MARKER'] = True
        return rep
