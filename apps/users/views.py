from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
import os
from django.conf import settings
from .serializers import CustomTokenObtainPairSerializer, UserSerializer, RegisterSerializer
from .permissions import IsAdminUser

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    # Use our custom serializer
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        debug_log_path = os.path.join(settings.BASE_DIR, 'debug_login.txt')
        
        with open(debug_log_path, 'a') as f:
            f.write(f"\n--- Login Attempt ---\n")
            f.write(f"Request data: {request.data}\n")
            f.write(f"Content Type: {request.content_type}\n")

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        # frontend sends 'username' but our USERNAME_FIELD is 'email'
        if 'username' in data:
            data['email'] = data['username'].lower()
            with open(debug_log_path, 'a') as f:
                f.write(f"Normalized email to lowercase: {data['email']}\n")
        elif 'email' in data:
            data['email'] = data['email'].lower()
            with open(debug_log_path, 'a') as f:
                f.write(f"Normalized email to lowercase: {data['email']}\n")
            
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            with open(debug_log_path, 'a') as f:
                f.write(f"Login Crash or Validation Error:\n{tb}\n")
            
            # Handle standard DRF exceptions (like AuthenticationFailed, ValidationError)
            from rest_framework.exceptions import APIException
            if isinstance(e, APIException):
                return Response(e.detail, status=e.status_code)
            
            return Response({"detail": "Internal server error during login", "traceback": tb if settings.DEBUG else None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # USE OS.WRITE OR DIRECT PRINT TO ENSURE CAPTURE
            error_details = f"Registration validation failed: {serializer.errors}"
            print(error_details)
            with open(os.path.join(settings.BASE_DIR, 'error_registration.txt'), 'a') as f:
                f.write(f"\n--- Registration Failure ---\nData: {request.data}\nErrors: {serializer.errors}\n")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)

class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            print(f"Deleting user: {instance.email} (ID: {instance.id})") # Debug log
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            import traceback
            traceback.print_exc() # Print full stack trace to console
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

