import logging

import jwt
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.auth.jwt_utils import generate_token_pair, refresh_access_token
from apps.core.auth.serializers import LoginSerializer, RefreshSerializer
from apps.core.auth.token_store import TokenStore
from apps.core.throttles import AuthRateThrottle

logger = logging.getLogger(__name__)
User = get_user_model()


class LoginView(APIView):
    """POST /api/v1/auth/login -- email + password -> token pair"""

    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            User().check_password(password)
            raise AuthenticationFailed("이메일 또는 비밀번호가 올바르지 않습니다.") from None

        if not user.check_password(password):
            raise AuthenticationFailed("이메일 또는 비밀번호가 올바르지 않습니다.")

        if user.status != User.Status.ACTIVE:
            raise PermissionDenied("비활성화된 계정입니다.")

        tokens = generate_token_pair(user)
        return Response(tokens)


class RefreshView(APIView):
    """POST /api/v1/auth/refresh -- refresh token -> new token pair (with rotation)"""

    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tokens = refresh_access_token(serializer.validated_data["refresh"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Refresh token has expired.") from None
        except (jwt.InvalidTokenError, ValueError) as e:
            raise AuthenticationFailed(str(e)) from None

        return Response(tokens)


class LogoutView(APIView):
    """POST /api/v1/auth/logout -- revoke current access token and optional refresh token"""

    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]

    def post(self, request):
        payload = request.auth
        if payload and "jti" in payload:
            TokenStore.revoke_token(payload["jti"])

        # Also revoke refresh token if provided in body
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                from apps.core.auth.jwt_utils import decode_token

                refresh_payload = decode_token(refresh_token, expected_type="refresh")
                TokenStore.revoke_token(refresh_payload["jti"])
            except Exception:
                pass  # Best-effort; access token already revoked

        return Response(status=204)


class LogoutAllView(APIView):
    """POST /api/v1/auth/logout-all -- revoke all user sessions"""

    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]

    def post(self, request):
        TokenStore.revoke_all_user_tokens(request.user.id)
        return Response(status=204)
