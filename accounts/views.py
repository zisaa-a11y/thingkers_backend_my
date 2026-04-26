from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .security import clear_failed_logins, is_login_locked, record_failed_login
from .serializers import (
    ForgotPasswordRequestSerializer,
    LoginSerializer,
    RefreshSerializer,
    RegisterSerializer,
    ResetPasswordConfirmSerializer,
    UserResponseSerializer,
)
from .throttles import AuthBurstRateThrottle, LoginRateThrottle


def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def build_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def set_refresh_cookie(response, refresh_token, remember_me=False):
    cookie_max_age = int(settings.AUTH_REFRESH_COOKIE_MAX_AGE)
    if not remember_me:
        cookie_max_age = int(settings.AUTH_SESSION_REFRESH_COOKIE_MAX_AGE)

    response.set_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=cookie_max_age,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
    )


def clear_refresh_cookie(response):
    response.delete_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthBurstRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            payload = UserResponseSerializer(user).data
            tokens = build_tokens(user)
            response = Response(
                {
                    "message": "User registered successfully",
                    "user": payload,
                    "accessToken": tokens["access"],
                    "token": tokens["access"],
                },
                status=status.HTTP_201_CREATED,
            )
            set_refresh_cookie(
                response,
                tokens["refresh"],
                bool(request.data.get("rememberMe", False)),
            )
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthBurstRateThrottle, LoginRateThrottle]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        ip_address = get_client_ip(request)

        if is_login_locked(email, ip_address):
            return Response(
                {"message": "Too many failed attempts. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        serializer = LoginSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            remember_me = serializer.validated_data.get("rememberMe", False)
            clear_failed_logins(email, ip_address)
            payload = UserResponseSerializer(user).data
            tokens = build_tokens(user)
            response = Response(
                {
                    "message": "Login successful",
                    "user": payload,
                    "accessToken": tokens["access"],
                    "token": tokens["access"],
                },
                status=status.HTTP_200_OK,
            )
            set_refresh_cookie(response, tokens["refresh"], remember_me)
            return response

        record_failed_login(email, ip_address)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthBurstRateThrottle]

    def post(self, request):
        refresh = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)
        if not refresh:
            return Response({"message": "Refresh token missing"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = RefreshSerializer(data={"refresh": refresh})
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)

            response = Response(
                {
                    "accessToken": access_token,
                    "token": access_token,
                },
                status=status.HTTP_200_OK,
            )

            if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS"):
                token.blacklist()
                user = User.objects.filter(pk=token.get("user_id")).first()
                if user:
                    new_refresh = RefreshToken.for_user(user)
                    set_refresh_cookie(response, str(new_refresh), remember_me=True)

            return response
        except TokenError:
            response = Response(
                {"message": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            clear_refresh_cookie(response)
            return response


class LogoutView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthBurstRateThrottle]

    def post(self, request):
        refresh = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME)
        response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        clear_refresh_cookie(response)

        if refresh:
            try:
                token = RefreshToken(refresh)
                token.blacklist()
            except TokenError:
                pass

        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payload = UserResponseSerializer(request.user).data
        return Response({"user": payload}, status=status.HTTP_200_OK)


class ForgotPasswordRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthBurstRateThrottle]

    def post(self, request):
        serializer = ForgotPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        # Always return success to prevent user enumeration.
        user = User.objects.filter(email__iexact=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            frontend_url = settings.AUTH_FRONTEND_RESET_PASSWORD_URL.rstrip("/")
            reset_link = f"{frontend_url}?uid={uid}&token={token}"

            send_mail(
                subject="Reset your password",
                message=(
                    "Use the link below to reset your password:\n"
                    f"{reset_link}\n\n"
                    "If you did not request this, you can safely ignore this email."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )

        return Response(
            {"message": "If an account exists for this email, a reset link has been sent."},
            status=status.HTTP_200_OK,
        )


class ResetPasswordConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthBurstRateThrottle]

    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.set_password(serializer.validated_data["password"])
        user.save(update_fields=["password", "updated_at"])
        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
