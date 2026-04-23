from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q # 🔥 Teeno cheezein check karne ke liye ye zaroori hai

# 1. Signup ke liye Serializer (Ekdum perfect hai)
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )
        return user

# 2. Login ke liye Super Smart Serializer (🔥 YAHAN MAGIC HAI)
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # User ne jo daala hai (Email, Phone, ya Username) wo nikalo
        identifier = attrs.get('username')
        password = attrs.get('password')

        # Database mein teeno jagah dhoondho
        user = CustomUser.objects.filter(
            Q(username__iexact=identifier) | 
            Q(email__iexact=identifier) | 
            Q(phone__iexact=identifier)
        ).first()

        # Agar user mil gaya aur password match ho gaya
        if user and user.check_password(password):

            # ===============================================
            # 🎯 NAYA FIX: BLOCK CHECK YAHAN AAYEGA
            # ===============================================
            if not user.is_active:
                raise serializers.ValidationError({
                    "detail": "🚫 You have been BLOCKED by Admin!"
                })
            # ===============================================
            
            # Khud se Token banao aur bhejo (SimpleJWT ki zidd khatam)
            refresh = self.get_token(user)

            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
            }
            return data
        else:
            # Agar match nahi hua toh error bhejo
            raise serializers.ValidationError({"detail": "Email/Phone ya Password galat hai!"})


# 3. 📝 Edit Profile ke liye Naya Serializer
class ProfileUpdateSerializer(serializers.ModelSerializer):
    # Flutter se 'name' aayega, use hum 'username' field mein map karenge
    name = serializers.CharField(source='username', required=False) 

    class Meta:
        model = CustomUser
        # Phone aur Email ko explicitly include karo
        fields = ['id', 'username', 'name', 'email', 'phone', 'profile_pic']
        # Read only sirf ID ko rakho, username ko nahi warna update nahi hoga
        read_only_fields = ['id'] 

    def update(self, instance, validated_data):
        # Data ko update karne ka makkhan logic
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        
        if 'profile_pic' in validated_data:
            instance.profile_pic = validated_data.get('profile_pic', instance.profile_pic)
            
        instance.save()
        return instance