from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q # 🔥 Teeno cheezein check karne ke liye ye zaroori hai
from django.contrib.auth import get_user_model
User = get_user_model()

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 🎯 NAYA FIX: SimpleJWT ki zidd todne ke liye! 
        # Ab wo automatically kisi field ko zaroori (required) nahi manega.
        self.fields[self.username_field] = serializers.CharField(required=False)

    def validate(self, attrs):
        # Request object se data nikalenge taaki chahe 'username', 'email' ya 'phone' aaye, sab pakad lein
        request = self.context.get('request')
        identifier = request.data.get('username') or request.data.get('email') or request.data.get('phone')
        password = request.data.get('password')

        if not identifier:
             raise serializers.ValidationError({"error": "Please enter Email or Phone number."})
             
        if not password:
             raise serializers.ValidationError({"error": "Please enter your password."})

        # Database mein teeno jagah dhoondho (Aapka logic)
        user = User.objects.filter(
            Q(username__iexact=identifier) | 
            Q(email__iexact=identifier) | 
            Q(phone__iexact=identifier)
        ).first()
        
        # 1. Agar Database mein user ka Email/Phone/ID mila hi nahi:
        if not user:
            raise serializers.ValidationError({"error": "Invalid Email or Phone please check!"})

        # 2. Agar User mil gaya, par usne Password galat daala hai:
        if not user.check_password(password):
            raise serializers.ValidationError({"error": "Incorrect password!"})

        # 3. Agar User sahi hai par Admin ne Block kiya hua hai:
        if not user.is_active:
            raise serializers.ValidationError({"error": "🚫 You have been BLOCKED by Admin!"})

        # Agar sab theek hai toh Token generate karo
        refresh = self.get_token(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'id': user.id,
            'username': user.username if user.username else user.first_name,
            'email': user.email,
            'phone': user.phone,
        } 


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
