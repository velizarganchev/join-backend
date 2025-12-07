from django.conf import settings
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.response import Response

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from user_auth_app.models import UserProfile
from user_auth_app.utils import clear_jwt_cookies, set_jwt_cookies
from .serializers import UserProfileSerializer


class UserProfileList_View(generics.ListCreateAPIView):
    """
    List all user profiles or create a new user profile.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]


class UserProfileDetail_View(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user profile.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        """
        Delete the related user as well when deleting a profile.
        """
        if instance.user != self.request.user:
            raise PermissionDenied("You can only delete your own profile.")
        user = instance.user
        user.delete()


class UserRegister_View(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get('username')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name') or ''
        email = request.data.get('email')
        password = request.data.get('password')
        phone_number = request.data.get('phone_number', '')
        color = request.data.get('color', 'green')

        if not username or not email or not password:
            return Response({'status': 'error', 'message': 'Username, email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'status': 'error', 'message': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'status': 'error', 'message': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        user.userprofile.phone_number = phone_number
        user.userprofile.color = color
        user.userprofile.save()

        return Response({
            'status': 'success',
            'message': 'User registered successfully.',
            'user_id': user.pk,
            'username': user.username
        }, status=status.HTTP_201_CREATED)


class UserRefreshToken_View(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'status': 'error', 'message': 'Refresh token not provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
        except TokenError:
            return Response({'status': 'error', 'message': 'Invalid or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response({
            'status': 'success',
        }, status=status.HTTP_200_OK)

        set_jwt_cookies(response, access_token,
                        refresh_token, debug=settings.DEBUG)
        return response


class UserLogin_View(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'status': 'error', 'message': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_exist = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'User with this email does not exist.'},
                status=status.HTTP_404_NOT_FOUND
            )

        user = authenticate(username=user_exist.username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            response = Response({
                'user_id': user.pk,
                'username': user.username,
            }, status=status.HTTP_200_OK)

            set_jwt_cookies(response, str(access), str(
                refresh), debug=settings.DEBUG)
            return response
        else:
            return Response(
                {'status': 'error', 'message': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserLogout_View(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        response = Response({
            'status': 'success',
            'message': 'User logged out successfully.'
        })
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        clear_jwt_cookies(response)
        return response
