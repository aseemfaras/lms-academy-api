from rest_framework import serializers
from .models import Course, Module, LiveSession, TrainerAssignment, ActivityLog, Batch


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ['id', 'name']


class ActivityLogSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='message', read_only=True)

    class Meta:
        model = ActivityLog
        fields = ['id', 'title', 'created_at']


class LiveSessionSerializer(serializers.ModelSerializer):
    trainer_name = serializers.SerializerMethodField()
    course_title = serializers.ReadOnlyField(source='course.title')
    batch_name = serializers.CharField(source='batch', read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = LiveSession
        fields = [
            'id', 'course', 'course_title', 'trainer_name', 'batch', 'batch_name',
            'title', 'description', 'scheduled_date', 'start_time',
            'end_time', 'status', 'meeting_link', 'recording_url', 'notes_url',
            'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_trainer_name(self, obj):
        if not obj.course:
            return "No Course Assigned"
        active_trainers = obj.course.trainers.filter(
            trainerassignment__course=obj.course,
            trainerassignment__is_active=True,
        )
        if active_trainers.exists():
            return ", ".join([t.full_name or t.username for t in active_trainers])
        return "No Active Trainer"

    def get_status(self, obj):
        from django.utils import timezone
        import datetime

        if obj.is_completed:
            return 'COMPLETED'

        now = timezone.now()
        start_dt = timezone.make_aware(
            datetime.datetime.combine(obj.scheduled_date, obj.start_time)
        )
        if now < start_dt:
            return 'UPCOMING'
        return 'LIVE'


class ModuleSerializer(serializers.ModelSerializer):
    notes_file = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = [
            'id', 'course', 'title', 'video_url', 'notes_url',
            'notes_file', 'batch', 'order', 'created_at',
        ]

    def get_notes_file(self, obj):
        if obj.notes_binary:
            request = self.context.get('request')
            if request:
                from django.urls import reverse
                return request.build_absolute_uri(
                    reverse('module-download-notes', kwargs={'pk': obj.pk})
                )
        return None

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        file_obj = data.get('notes_file') or data.get('uploaded_notes')
        if file_obj and hasattr(file_obj, 'read'):
            ret['_notes_file_obj'] = file_obj
        return ret

    def create(self, validated_data):
        file_obj = validated_data.pop('_notes_file_obj', None)
        if file_obj:
            validated_data['notes_binary'] = file_obj.read()
            validated_data['notes_filename'] = file_obj.name
            validated_data['notes_content_type'] = getattr(
                file_obj, 'content_type', 'application/octet-stream'
            )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        file_obj = validated_data.pop('_notes_file_obj', None)
        if file_obj:
            instance.notes_binary = file_obj.read()
            instance.notes_filename = file_obj.name
            instance.notes_content_type = getattr(
                file_obj, 'content_type', 'application/octet-stream'
            )
        return super().update(instance, validated_data)


class CourseListSerializer(serializers.ModelSerializer):
    trainer_name = serializers.SerializerMethodField()
    enrollment_count = serializers.SerializerMethodField()
    batches = BatchSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'category', 'image', 'trainer_name',
            'enrollment_count', 'created_at', 'batches',
        ]

    def get_trainer_name(self, obj):
        active_trainers = obj.trainers.filter(
            trainerassignment__course=obj,
            trainerassignment__is_active=True,
        )
        if active_trainers.exists():
            return ", ".join([t.full_name or t.username for t in active_trainers])
        return "No Active Trainer"

    def get_enrollment_count(self, obj):
        return obj.enrollments.count()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['image'] = instance.image.name if instance.image else None
        return data


class CourseDetailSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    batches = BatchSerializer(many=True, read_only=True)
    trainers = serializers.SerializerMethodField()
    enrolled_students = serializers.SerializerMethodField()
    enrollment_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'category', 'image', 'batches',
            'modules', 'enrolled_students', 'trainers', 'enrollment_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_trainers(self, obj):
        assignments = TrainerAssignment.objects.filter(course=obj).select_related('trainer')
        return [
            {
                'trainer': a.trainer_id,
                'name': a.trainer.full_name or a.trainer.username,
                'email': a.trainer.email,
                'batch': a.batch,
                'is_active': a.is_active,
            }
            for a in assignments
        ]

    def get_enrolled_students(self, obj):
        return [
            {
                'id': e.student_id,
                'email': e.student.email,
                'name': e.student.full_name or e.student.username,
                'batch': e.batch,
            }
            for e in obj.enrollments.select_related('student')
        ]

    def get_enrollment_count(self, obj):
        return obj.enrollments.count()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['image'] = instance.image.name if instance.image else None
        return data
