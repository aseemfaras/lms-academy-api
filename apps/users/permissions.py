from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to users with the ADMIN role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ADMIN')

class IsAdminOrEnrolledStudent(permissions.BasePermission):
    """
    Allows Admins full access.
    Allows Trainers access to courses/modules they are assigned to.
    Allows Students to view course details only if they are enrolled.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if request.user.role in ['ADMIN', 'TRAINER']:
            return True
            
        # For students, only allow GET/HEAD/OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'ADMIN':
            return True
        
        from trainers.models import Course, Module
        
        if user.role == 'TRAINER':
            if isinstance(obj, Course):
                return obj.trainers.filter(id=user.id).exists()
            if isinstance(obj, Module):
                return obj.course.trainers.filter(id=user.id).exists()
            return False

        if user.role == 'STUDENT':
            if isinstance(obj, Course):
                return obj.enrollments.filter(student=user).exists()
            if isinstance(obj, Module):
                return obj.course.enrollments.filter(student=user).exists()
            
        return False

