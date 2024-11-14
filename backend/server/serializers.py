import re
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Course, Major, Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone_number']

    def validate_phone_number(self, value):
        if Profile.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(f"The phone number {value} is already in use.")
        return value
    

class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()

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

    def validate(self, data):
        required_fields = ['username', 'email', 'first_name', 'last_name', 'password']

        for field in required_fields:
            if field not in data or not data[field].strip():
                raise serializers.ValidationError({field: f"{field.capitalize()} is required."})
        
        return data

    def validate_username(self, value):
        if ' ' in value:
            raise serializers.ValidationError("Username should not contain spaces.")
        return value
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not any(char in re.escape('!@#$%^&*()_+-=[]{},.<>?;:/|') for char in value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value


    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        
        Profile.objects.create(user=user, **profile_data)
        return user
    
    def get_phone_number(self, obj):
        phone_number = obj.profile.phone_number
        if phone_number:
            return phone_number
        return None
    

# Forgot Password feature
class PasswordChangeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        user_serializer = UserSerializer()
        return user_serializer.validate_password(value)
       
class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = ['id', 'name', 'code']

class CourseSerializer(serializers.ModelSerializer):
    major = MajorSerializer()
    
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'major']

        