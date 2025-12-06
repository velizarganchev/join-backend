from rest_framework import serializers
from django.contrib.auth.models import User

from todo_list.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name',
                  'username', 'email']
        extra_kwargs = {
            "username": {"read_only": True},
        }

    def validate_username(self, username):
        user = self.instance

        if User.objects.filter(username=username).exclude(pk=user.pk).exists():
            raise serializers.ValidationError(
                "This username is already taken.")
        return username

    def validate_email(self, email):
        user = self.instance

        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("This email is already in use.")
        return email


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'phone_number', 'color']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_instance = instance.user
            for attr, value in user_data.items():
                setattr(user_instance, attr, value)
            user_instance.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
