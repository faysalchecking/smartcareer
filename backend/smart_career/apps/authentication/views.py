from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from smart_career.apps.common.audit import record_audit_event
from .models import UserProfile
from .serializers import LoginSerializer, UserSerializer

GENERIC_LOGIN_ERROR = 'Invalid email or password.'


class AuthenticationViewSet(viewsets.ViewSet):
    """Authentication endpoints"""

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except (ValidationError, AuthenticationFailed):
            # Failed attempts are recorded without the password. The generic message
            # avoids revealing whether the account exists.
            record_audit_event(
                request=request,
                action='LOGIN',
                entity_type='USER',
                entity_id='anonymous',
                status_code=status.HTTP_401_UNAUTHORIZED,
                description='Failed login attempt',
                details={'attempted_identifier': str(request.data.get('email', ''))[:254]},
            )
            return Response({'error': GENERIC_LOGIN_ERROR}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        record_audit_event(
            request=request,
            user=user,
            action='LOGIN',
            entity_type='USER',
            entity_id=user.id,
            status_code=status.HTTP_200_OK,
            description='Successful login',
        )

        return Response(
            {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                # Only the owner may revoke a token, so a user cannot revoke someone else's session.
                if str(token.get('user_id')) == str(request.user.id):
                    token.blacklist()
            except TokenError:
                # Already expired or revoked. The client is logged out either way.
                pass

        record_audit_event(
            request=request,
            user=request.user,
            action='LOGOUT',
            entity_type='USER',
            entity_id=request.user.id,
            status_code=status.HTTP_200_OK,
            description='Logout',
        )
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                'user': UserSerializer(request.user).data,
                'role': profile.role,
                'phone': profile.phone,
                'address': profile.address,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def refresh(self, request):
        # AllowAny on purpose: the access token is expired when this endpoint is needed.
        serializer = TokenRefreshSerializer(data={'refresh': request.data.get('refresh_token', '')})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as error:
            raise InvalidToken(error.args[0] if error.args else 'Token is invalid or expired.')

        validated = serializer.validated_data
        return Response(
            {
                'access_token': validated['access'],
                'refresh_token': validated.get('refresh', request.data.get('refresh_token')),
            },
            status=status.HTTP_200_OK,
        )