from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .utils import send_welcome_email

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['role'] = user.role
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'full_name': self.user.full_name,
            'role': self.user.role,
        }
        return data

class UserSerializer(serializers.ModelSerializer):
    enrollment_count = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'role', 'is_active', 'date_joined', 'enrollment_count', 'courses']

    def get_enrollment_count(self, obj):
        return obj.enrollments.count()

    def get_courses(self, obj):
        # Get course titles from actual enrollment records
        enrolled_titles = list(
            obj.enrollments.select_related('course')
               .filter(course__isnull=False)
               .values_list('course__title', flat=True)
        )
        if enrolled_titles:
            return enrolled_titles
        # Fallback: use the stored course_name field on the user
        if obj.course_name:
            return [obj.course_name]
        return []

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'portal_link', 'course_name']

    def create(self, validated_data):
        role = validated_data.get('role', 'STUDENT').upper()
        
        # Map common frontend role names to backend Role choices
        role_map = {
            'INSTRUCTOR': User.Role.TRAINER,
            'TRAINER': User.Role.TRAINER,
            'STUDENT': User.Role.STUDENT,
            'SUPPORTER': User.Role.SUPPORTER,
            'ADMIN': User.Role.ADMIN
        }
        
        mapped_role = role_map.get(role, User.Role.STUDENT)

        email = validated_data['email'].lower()
        user = User.objects.create_user(
            username=email, # Use email as username for reliability
            email=email,
            password=validated_data['password'],
            role=mapped_role,
            full_name=validated_data['username'], # Map the name from frontend to full_name
            portal_link=validated_data.get('portal_link', ''),
            course_name=validated_data.get('course_name', '')
        )

        # Send welcome email for students
        if mapped_role == User.Role.STUDENT:
            try:
                send_welcome_email(
                    user, 
                    validated_data['password'], 
                    user.course_name, 
                    user.portal_link
                )
            except Exception as e:
                # Log the error but don't fail the registration
                print(f"Failed to send welcome email to {user.email}: {e}")

        return user
