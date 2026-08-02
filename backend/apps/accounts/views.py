import jwt
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import LoginSerializer, RefreshSerializer, UserAdminSerializer, UserSerializer
from .tokens import decode, issue_access, issue_pair
from apps.core.permissions import HasPerm
from rest_framework.viewsets import ModelViewSet


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_scope = "login"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response(
                {"error": {"code": 401, "type": "unauthenticated", "message": "نام کاربری یا گذرواژه نادرست است."}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        tokens = issue_pair(user)
        return Response({**tokens, "user": UserSerializer(user, context={"request": request}).data})


class RefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payload = decode(serializer.validated_data["refresh"])
        except jwt.InvalidTokenError:
            return Response(
                {"error": {"code": 401, "type": "unauthenticated", "message": "توکن نامعتبر است."}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if payload.get("typ") != "refresh":
            return Response(
                {"error": {"code": 401, "type": "unauthenticated", "message": "نوع توکن نامعتبر است."}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        user = User.objects.filter(id=payload.get("sub"), is_active=True).first()
        if user is None:
            return Response(
                {"error": {"code": 401, "type": "unauthenticated", "message": "کاربر یافت نشد."}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response({"access": issue_access(user)})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user, context={"request": request}).data)


class UserViewSet(ModelViewSet):
    serializer_class = UserAdminSerializer
    permission_classes = [HasPerm]
    required_perms = {
        "list": "users.list", "retrieve": "users.list", "create": "users.create",
        "update": "users.edit", "partial_update": "users.edit", "destroy": "users.block",
    }
    search_fields = ["name", "username", "email"]
    filterset_fields = ["is_active"]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return User.objects.filter(tenant=tenant).prefetch_related("role_assignments") if tenant else User.objects.none()

    def perform_create(self, serializer):
        serializer.save(tenant=getattr(self.request, "tenant", None))
