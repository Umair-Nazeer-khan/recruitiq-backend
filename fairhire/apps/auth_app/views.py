# fairhire/apps/auth_app/views.py
# ─────────────────────────────────────────────────────────────────
#  Authentication views.
#  All responses match exactly what the Flutter ViewModels expect.
# ─────────────────────────────────────────────────────────────────

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import HRUser
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


def get_tokens(user):
    """Generate JWT access + refresh tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
    }


# ──────────────────────────────────────────────
#  POST /api/v1/auth/register/
# ──────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Create new HR Manager account.

    Flutter sends:
        { "name": "Umair", "email": "umair@company.com", "password": "pass123" }

    Returns:
        { "user": {...}, "access": "...", "refresh": "..." }
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user   = serializer.save()
        tokens = get_tokens(user)
        return Response({
            'user':    UserSerializer(user).data,
            'access':  tokens['access'],
            'refresh': tokens['refresh'],
            'message': 'Account created successfully.',
        }, status=status.HTTP_201_CREATED)

    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────
#  POST /api/v1/auth/login/
# ──────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login with email + password.
    Also saves FCM token so we can send push notifications.

    Flutter sends:
        { "email": "...", "password": "...", "fcm_token": "device_token" }

    Returns:
        { "user": {...}, "access": "...", "refresh": "..." }
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user      = serializer.validated_data['user']
        fcm_token = serializer.validated_data.get('fcm_token', '')

        # Save the device FCM token for push notifications
        if fcm_token:
            user.fcm_token = fcm_token
            user.save(update_fields=['fcm_token'])

        tokens = get_tokens(user)
        return Response({
            'user':    UserSerializer(user).data,
            'access':  tokens['access'],
            'refresh': tokens['refresh'],
            'message': 'Login successful.',
        })

    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────
#  POST /api/v1/auth/logout/
# ──────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout — blacklists the refresh token and clears FCM token.

    Flutter sends:
        { "refresh": "refresh_token_here" }
    """
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()

        # Clear FCM token so device stops receiving notifications
        request.user.fcm_token = None
        request.user.save(update_fields=['fcm_token'])

        return Response({'message': 'Logged out successfully.'})
    except Exception:
        return Response({'message': 'Logged out.'})


# ──────────────────────────────────────────────
#  GET /api/v1/auth/profile/
# ──────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Returns the logged-in user's profile."""
    return Response(UserSerializer(request.user).data)


# ──────────────────────────────────────────────
#  PATCH /api/v1/auth/update-fcm/
# ──────────────────────────────────────────────
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_fcm(request):
    """
    Update FCM token when it refreshes on the device.

    Flutter sends:
        { "fcm_token": "new_device_token" }
    """
    token = request.data.get('fcm_token')
    if token:
        request.user.fcm_token = token
        request.user.save(update_fields=['fcm_token'])
        return Response({'message': 'FCM token updated.'})
    return Response({'error': 'No token provided.'}, status=400)
