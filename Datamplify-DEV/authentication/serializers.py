from rest_framework import serializers
from authentication.models  import UserProfile
import re
    
class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    # role = serializers.CharField(allow_null=True, default='Admin', allow_blank=True)

    def validate_username(self, value):
        if len(value) > 30:
            raise serializers.ValidationError("Username allows up to 30 characters only")
        if UserProfile.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if UserProfile.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_password(self, value):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Password is invalid. Min 8 characters. Must include: "
                "one lowercase letter, one uppercase letter, one digit, and one special character."
            )
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password did not match."})
        return data


class ActivationSerializer(serializers.Serializer):
    otp = serializers.IntegerField()


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
    
class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ConfirmPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255)
    confirmPassword = serializers.CharField(max_length=255)