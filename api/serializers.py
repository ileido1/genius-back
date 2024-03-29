from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from .models import CsvData




class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email

        return token

class CsvDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CsvData
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    class Meta:
        model = User
        fields = ('username', 'password', )

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
    )
        user.set_password(validated_data['password'])
        user.save()
        
        return user
