from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .utils import send_welcome_email

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role.lower(),
        }
        return data


class UserSerializer(serializers.ModelSerializer):
    enrollment_count = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'role', 'is_active',
            'date_joined', 'enrollment_count', 'courses',
        ]

    def get_enrollment_count(self, obj):
        return obj.enrollments.count()

    def get_courses(self, obj):
        enrolled_titles = list(
            obj.enrollments.select_related('course')
            .filter(course__isnull=False)
            .values_list('course__title', flat=True)
        )
        if enrolled_titles:
            return enrolled_titles
        if obj.course_name:
            return [obj.course_name]
        return []


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'username', 'full_name', 'email', 'password', 'role',
            'portal_link', 'course_name',
        ]

    def create(self, validated_data):
        role = validated_data.get('role', 'student').upper()

        role_map = {
            'INSTRUCTOR': User.Role.TRAINER,
            'TRAINER': User.Role.TRAINER,
            'STUDENT': User.Role.STUDENT,
            'SUPPORTER': User.Role.SUPPORTER,
            'ADMIN': User.Role.ADMIN,
        }

        mapped_role = role_map.get(role, User.Role.STUDENT)
        email = validated_data['email'].lower()
        display_name = validated_data.get('full_name') or validated_data.get('username', email)

        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data['password'],
            role=mapped_role,
            full_name=display_name,
            portal_link=validated_data.get('portal_link', ''),
            course_name=validated_data.get('course_name', ''),
        )

        if mapped_role == User.Role.STUDENT:
            try:
                send_welcome_email(
                    user,
                    validated_data['password'],
                    user.course_name,
                    user.portal_link,
                )
            except Exception as e:
                print(f"Failed to send welcome email to {user.email}: {e}")

        return user
