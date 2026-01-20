"""
Authentication views for JWT token management and user registration.

Includes:
- User registration endpoint
- User login endpoint
- Token refresh endpoint
- Current user profile endpoint
- User role management (researcher, admin, viewer)
"""
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from .models import Researcher


# ==================== Serializers ====================


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
        read_only_fields = ['id', 'is_staff']


class ResearcherProfileSerializer(serializers.ModelSerializer):
    """Serializer for Researcher profile with user info."""
    
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Researcher
        fields = [
            'id', 'user', 'full_name', 'department', 
            'research_interests', 'google_scholar_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else None


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']
    
    def validate(self, data):
        """Validate passwords match."""
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                'password': 'Passwords do not match.'
            })
        
        # Validate email uniqueness
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({
                'email': 'Email already in use.'
            })
        
        # Validate username uniqueness
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({
                'username': 'Username already in use.'
            })
        
        return data
    
    def create(self, validated_data):
        """Create user and researcher profile."""
        validated_data.pop('password2')
        
        with transaction.atomic():
            # Create user
            user = User.objects.create_user(**validated_data)
            
            # Create researcher profile
            Researcher.objects.create(user=user)
        
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with user data."""
    
    def get_token(self, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_staff'] = user.is_staff
        
        return token
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add user info to token
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_staff'] = user.is_staff
        
        return token


# ==================== API Views ====================


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register a new user.
    
    POST /api/auth/register/
    
    Request body:
    {
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "secure_password_123",
        "password2": "secure_password_123"
    }
    
    Response:
    {
        "user": {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe"
        },
        "message": "User registered successfully"
    }
    """
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'user': UserSerializer(user).data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    Get current authenticated user profile.
    
    GET /api/auth/me/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_staff": false,
        "researcher_profile": {...}
    }
    """
    user = request.user
    
    # Try to get researcher profile
    researcher_profile = None
    if hasattr(user, 'researcher_profile'):
        researcher_profile = ResearcherProfileSerializer(
            user.researcher_profile
        ).data
    
    return Response({
        'user': UserSerializer(user).data,
        'researcher_profile': researcher_profile
    }, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with user data."""
    
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user (client-side token deletion recommended).
    
    POST /api/auth/logout/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "message": "Logged out successfully"
    }
    """
    # Note: JWT tokens are stateless, so logout is handled on the client side
    # by deleting the token. This endpoint is mainly for consistency.
    return Response({
        'message': 'Logged out successfully'
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Update user profile.
    
    PUT /api/auth/profile/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Request body:
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
    }
    
    Response:
    {
        "user": {...},
        "researcher_profile": {...}
    }
    """
    user = request.user
    
    # Update user fields
    if 'first_name' in request.data:
        user.first_name = request.data['first_name']
    if 'last_name' in request.data:
        user.last_name = request.data['last_name']
    if 'email' in request.data:
        # Check email uniqueness
        if User.objects.filter(email=request.data['email']).exclude(id=user.id).exists():
            return Response({
                'errors': {'email': 'Email already in use.'}
            }, status=status.HTTP_400_BAD_REQUEST)
        user.email = request.data['email']
    
    user.save()
    
    # Update researcher profile if provided
    if hasattr(user, 'researcher_profile'):
        researcher = user.researcher_profile
        if 'department' in request.data:
            researcher.department = request.data['department']
        if 'research_interests' in request.data:
            researcher.research_interests = request.data['research_interests']
        if 'google_scholar_id' in request.data:
            researcher.google_scholar_id = request.data['google_scholar_id']
        researcher.save()
    
    return Response({
        'user': UserSerializer(user).data,
        'researcher_profile': ResearcherProfileSerializer(
            user.researcher_profile
        ).data if hasattr(user, 'researcher_profile') else None
    }, status=status.HTTP_200_OK)
