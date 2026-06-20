from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from .serializers import CustomTokenObtainPairSerializer, UserSerializer, RegisterSerializer
from .permissions import IsAdminUser

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        return Response(
            {"detail": 'Method "GET" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def post(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)

        if 'email' in data:
            data['email'] = str(data['email']).lower()
        elif 'username' in data:
            data['email'] = str(data['username']).lower()

        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            from rest_framework.exceptions import APIException, ValidationError
            if isinstance(e, ValidationError):
                detail = e.detail
                if isinstance(detail, dict) and 'non_field_errors' in detail:
                    return Response(
                        {"error": "Invalid credentials"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
                return Response(detail, status=status.HTTP_400_BAD_REQUEST)
            if isinstance(e, APIException):
                if e.status_code == status.HTTP_401_UNAUTHORIZED:
                    return Response(
                        {"error": "Invalid credentials"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
                return Response(e.detail, status=e.status_code)
            raise

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
