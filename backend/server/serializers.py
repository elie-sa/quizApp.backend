import re
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Course, Major, Profile, Notebook, Team

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone_number']

    def validate_phone_number(self, value):
        if Profile.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(f"The phone number {value} is already in use.")
        return value
    

class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'email', 'phone_number']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'username': {'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not any(char in re.escape('!@#$%^&*()_+-=[]{},.<>?;:/|') for char in value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number', None)
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        
        Profile.objects.create(user=user, phone_number=phone_number)
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['phone_number'] = (
            instance.profile.phone_number if hasattr(instance, 'profile') else None
        )
        return representation

# Forgot Password feature
class PasswordChangeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        user_serializer = UserSerializer()
        return user_serializer.validate_password(value)
       
#General Serializers

class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = ['id', 'name', 'code']

class CourseSerializer(serializers.ModelSerializer):
    major = MajorSerializer()
    
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'major']

class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ['name', 'creation_date', 'members']

class NotebookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notebook
        fields = ['id', 'title', 'color', 'rating', 'creation_date', 'user_creator', 'team_creator', 'bookmark_users', 'courses']

class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ['id', 'name', 'creation_date', 'members']

    def __str__(self):
        return self.name