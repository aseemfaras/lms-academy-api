from rest_framework import serializers
from .models import Enrollment
from trainers.serializers import CourseListSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'batch', 'enrolled_at', 'status']
        read_only_fields = ['student', 'enrolled_at']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.course:
            rep['course'] = CourseListSerializer(instance.course, context=self.context).data
        return rep
