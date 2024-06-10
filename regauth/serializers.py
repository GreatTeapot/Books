import re
from rest_framework import serializers
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email')


class UserRegisSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {
            'username': {'write_only': True},
            'email': {'write_only': True},
            'password': {'write_only': True},


        }

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long.")

        if not re.match("^[a-zA-Z0-9]+$", value):
            raise serializers.ValidationError("Password must contain only letters and digits.")

        return value

    def validate_username(self, value):
        if not re.match("^[a-zA-Z0-9_-]+$", value):
            raise serializers.ValidationError("Username can only contain letters, digits, '_', '-', '?'.")

        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data.get('email', ''),
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


# zalkar

