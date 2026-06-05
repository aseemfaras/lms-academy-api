from rest_framework import serializers
from .models import Course, Module, LiveSession, TrainerAssignment, ActivityLog, Batch
from users.serializers import UserSerializer

class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ['id', 'name', 'created_at']

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'related_course', 'activity_type', 'message', 'created_at']
class LiveSessionSerializer(serializers.ModelSerializer):
    trainer_name = serializers.SerializerMethodField()
    course_title = serializers.ReadOnlyField(source='course.title')
    status = serializers.SerializerMethodField()


    class Meta:
        model = LiveSession
        fields = [
            'id', 'course', 'course_title', 'trainer_name', 'batch',
            'title', 'description', 'scheduled_date', 'start_time', 
            'end_time', 'status', 'meeting_link', 'recording_url', 'notes_url',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_trainer_name(self, obj):
        # Return the name of the active trainer(s)
        if not obj.course:
            return "No Course Assigned"
        active_trainers = obj.course.trainers.filter(trainerassignment__course=obj.course, trainerassignment__is_active=True)
        if active_trainers.exists():
            return ", ".join([t.full_name or t.username for t in active_trainers])
        return "No Active Trainer"

    def get_status(self, obj):

        from django.utils import timezone
        import datetime
        
        if obj.is_completed:
            return 'COMPLETED'
        
        now = timezone.now()
        start_dt = timezone.make_aware(datetime.datetime.combine(obj.scheduled_date, obj.start_time))
        
        if now < start_dt:
            return 'UPCOMING'
        else:
            return 'LIVE'




class ModuleSerializer(serializers.ModelSerializer):
    notes_file = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = [
            'id', 'course', 'title', 'video_url', 'notes_url', 
            'notes_file', 'batch', 'order', 'created_at'
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
        # Support both 'notes_file' and 'uploaded_notes' for backward compatibility
        # If notes_file is passed as a file object, we handle it specially
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
            # Handle possible lack of content_type attribute
            validated_data['notes_content_type'] = getattr(file_obj, 'content_type', 'application/octet-stream')
            
        return super().create(validated_data)

    def update(self, instance, validated_data):
        file_obj = validated_data.pop('_notes_file_obj', None)
        if file_obj:
            instance.notes_binary = file_obj.read()
            instance.notes_filename = file_obj.name
            instance.notes_content_type = getattr(file_obj, 'content_type', 'application/octet-stream')
            
        return super().update(instance, validated_data)

class TrainerAssignmentSerializer(serializers.ModelSerializer):
    trainer_details = UserSerializer(source='trainer', read_only=True)
    
    class Meta:
        model = TrainerAssignment
        fields = ['id', 'trainer', 'trainer_details', 'batch', 'is_active', 'assigned_at']

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    batches = BatchSerializer(many=True, read_only=True)
    # Return assignment details instead of just using UserSerializer
    trainers = serializers.SerializerMethodField()
    trainer_name = serializers.SerializerMethodField()
    instructor_name = serializers.SerializerMethodField()
    enrolled_students = serializers.SerializerMethodField()
    enrollment_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'image', 'trainers', 
            'trainer_name', 'instructor_name', 'created_at', 
            'updated_at', 'modules', 'batches', 'enrolled_students', 'enrollment_count'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_trainers(self, obj):
        assignments = TrainerAssignment.objects.filter(course=obj)
        return TrainerAssignmentSerializer(assignments, many=True).data

    def get_trainer_name(self, obj):
        # We'll show all assigned trainers here, but maybe filter by active if needed?
        # User requested "only the activate trainer be reflect" - likely means active trainers.
        active_trainers = obj.trainers.filter(trainerassignment__course=obj, trainerassignment__is_active=True)
        if active_trainers.exists():
            return ", ".join([t.full_name or t.username for t in active_trainers])
        return "No Active Trainer"

    def get_instructor_name(self, obj):
        return self.get_trainer_name(obj)

    def get_enrolled_students(self, obj):
        # Fetch students from the Enrollment model related to this course
        enrollments = obj.enrollments.all()
        # We need to return the student details but ALSO the batch they are enrolled in
        result = []
        for e in enrollments:
            student_data = UserSerializer(e.student).data
            student_data['batch'] = e.batch  # Inject batch into student data for frontend
            result.append(student_data)
        return result

    def get_enrollment_count(self, obj):
        return obj.enrollments.count()

