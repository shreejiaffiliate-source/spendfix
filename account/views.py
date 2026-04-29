import requests
import uuid
import random  # 🎯 OTP ke liye
import random  # 👈 Ye line honi chahiye
from django.core.mail import send_mail  # 🎯 Email bhejane ke liye
from django.conf import settings
from django.core.cache import cache # 🎯 NAYA IMPORT: Memory me data rakhne ke liye
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser 
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import UserSerializer, MyTokenObtainPairSerializer, ProfileUpdateSerializer
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import CustomUser
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model

# Custom User model fetch karne ke liye (agar file mein upar import nahi hai toh)
User = get_user_model()

# --- 1. SIGNUP VIEW (OTP LOGIC KE SAATH) ---
class SignupView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            email = request.data.get('email')
            
            # 🎯 OTP Generate karo (6 digits)
            otp = str(random.randint(100000, 999999))

            # 🎯 JADU YAHAN HAI: Data ko Database me nahi, CACHE (Memory) me save karo 15 minute ke liye
            cache_data = {
                'user_data': request.data,
                'otp': otp
            }
            cache.set(f"signup_{email}", cache_data, timeout=900) # 900 seconds = 15 mins

            # 🎯 NAYA ENGLISH MESSAGE
            subject = "SpendFix - Verify Your Account"
            username = request.data.get('name', 'User')
            message = f"Hello {username},\n\nWelcome to SpendFix! Please use the following OTP to verify your account:\n\n{otp}\n\nHappy Budgeting!"
            
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
                return Response({
                    "message": "OTP sent! Please check your email.",
                    "email": email
                }, status=status.HTTP_200_OK)
            except Exception as e:
                print(f"❌ Email Error: {e}")
                return Response({"error": "Failed to send email. Check configuration."}, status=500)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- 2. NAYA VERIFY OTP VIEW (YAHAN DATABASE MEIN SAVE HOGA) ---
class VerifyOTPView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({"error": "Email and OTP are required!"}, status=400)

        # 🎯 Cache se data nikalo
        cached_data = cache.get(f"signup_{email}")

        if not cached_data:
            return Response({"error": "Session expired or email not found! Please signup again."}, status=400)

        # 🎯 OTP Check karo
        if cached_data['otp'] == otp:
            # 🎯 OTP SAHI HAI! AB USER KO ASLI DATABASE (Admin Panel) MEIN SAVE KARENGE
            serializer = UserSerializer(data=cached_data['user_data'])
            if serializer.is_valid():
                user = serializer.save()
                user.is_active = True
                user.save()

                # Save hone ke baad cache kachra saaf kar do
                cache.delete(f"signup_{email}")

                # Login Token bhej do
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Account verified and created successfully!",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "username": user.username
                }, status=200)
            else:
                return Response(serializer.errors, status=400)
        else: 
            return Response({"error": "Galat OTP! Fir se check karein."}, status=400)
        

# --- 3. RESEND OTP VIEW ---
class ResendOTPView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email is required!"}, status=400)

        # 🎯 Cache se purana data nikalo
        cached_data = cache.get(f"signup_{email}")

        if not cached_data:
            return Response({"error": "Session expired! Please signup again."}, status=400)

        # Naya OTP generate karein
        otp = str(random.randint(100000, 999999))
        cached_data['otp'] = otp
        
        # Cache update kar do
        cache.set(f"signup_{email}", cached_data, timeout=900)

        # 🎯 NAYA ENGLISH MESSAGE
        subject = "SpendFix - Your New OTP"
        username = cached_data['user_data'].get('name', 'User')
        message = f"Hello {username},\n\nYour new verification OTP is:\n\n{otp}\n\nHappy Budgeting!"
        
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            return Response({"message": "New OTP sent successfully!"}, status=200)
        except Exception as e:
            return Response({"error": "Failed to send email."}, status=500)


# --- 3. LOGIN & PROFILE VIEWS (SAME AS BEFORE) ---
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserProfileView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser] 

    def get(self, request):
        serializer = ProfileUpdateSerializer(request.user)
        return Response(serializer.data)

    def post(self, request):
        user = request.user

        # 1. FCM Token Update Logic
        fcm = request.data.get('fcm_token')
        if fcm:
            user.fcm_token = fcm
            user.save()

        # 🛡️ Name/Username Duplication Check
        new_name = request.data.get('name')
        if new_name and new_name != user.username: # ya 'user.name' jo bhi field aapne rakhi ho
            if User.objects.filter(username=new_name).exists():
                return Response(
                    {"name": "This name is already taken! Please use a different name. 👤"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 2. 🛡️ Email Duplication Check
        new_email = request.data.get('email')
        if new_email and new_email != user.email:
            if User.objects.filter(email=new_email).exists():
                return Response(
                    {"email": "This email is already in use by another user! ❌"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 3. 🛡️ Phone Number Duplication Check (Naya logic jo tumne maanga)
        new_phone = request.data.get('phone')
        if new_phone and new_phone != user.phone:
            if User.objects.filter(phone=new_phone).exists():
                return Response(
                    {"phone": "This number is already in use! Please enter another number. ❌"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 4. Asli Update Logic
        serializer = ProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Profile updated successfully! ✅", "data": serializer.data}, 
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- 4. GOOGLE LOGIN VIEW (SAME AS BEFORE) ---
class GoogleLoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('access_token')
        fcm_token = request.data.get('fcm_token')

        if not token:
            return Response({"error": "Google token missing!"}, status=400)

        try:
            google_url = f'https://oauth2.googleapis.com/tokeninfo?id_token={token}'
            response = requests.get(google_url)
            user_data = response.json()

            if response.status_code != 200:
                return Response({"error": "Google Token invalid!"}, status=400)

            email = user_data.get('email')
            google_name = user_data.get('name', '') 
            
            if not email:
                return Response({"error": "Email not found!"}, status=400)

            user = CustomUser.objects.filter(email__iexact=email).first()

            if not user:
                base_username = google_name.replace(" ", "").lower() if google_name else email.split('@')[0]
                username = base_username
                
                counter = 1
                while CustomUser.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                random_password = get_random_string(24)

                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    phone='',
                    password=random_password,
                    first_name=google_name
                )

            # ===============================================
            # 🎯 NAYA FIX: GOOGLE USER BLOCK CHECK
            # ===============================================
            if not user.is_active:
                return Response({"error": "🚫 You have been BLOCKED by Admin!"}, status=403)
            # ===============================================
            
            # 🎯 YAHAN FCM TOKEN SAVE HOGA DATABASE MEIN
            if fcm_token:
                user.fcm_token = fcm_token
                user.save()
            
            display_name = user.first_name if user.first_name else user.username
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'id': user.id,
                'username': display_name,
                'email': user.email,
                'phone': user.phone,
            }, status=200)

        except Exception as e:
            print(f"CRITICAL ERROR: {str(e)}") 
            return Response({"error": f"Internal Error: {str(e)}"}, status=500)
        
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_direct(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    # 1. Basic Validation
    if new_password != confirm_password:
        return Response({"error": "Passwords do not match!"}, status=400)

    user = CustomUser.objects.filter(email=email).first()
    
    if user:
        # 2. OTP Check (Jo humne signup ke waqt banaya tha wahi logic)
        if user.otp == otp and otp is not None:
            user.password = make_password(new_password) # 🎯 Password encrypt ho raha hai
            user.otp = None # OTP use ho gaya
            user.is_active = True
            user.save()
            return Response({"success": "Password updated successfully! You can login now."}, status=200)
        else:
            return Response({"error": "Invalid or expired OTP!"}, status=400)
            
    return Response({"error": "User not found!"}, status=404)


# --- FORGOT PASSWORD LOGIC ---

class ForgotPasswordView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email')
            user = CustomUser.objects.filter(email=email).first()

            if not user:
                return Response({"error": "User not found!"}, status=404)

            # OTP Generate
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.save()

            # Email bhejte waqt error catch karo
            subject = "SpendFix - Reset OTP" 
            message = f"OTP: {otp}"
            
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
            
            return Response({"message": "OTP sent!"}, status=200)

        except Exception as e:
            print(f"❌ Error Detail: {str(e)}") # 👈 Ye terminal mein error print karega
            return Response({"error": f"Internal Server Error: {str(e)}"}, status=500)

# 2️⃣ Step: Verify Reset OTP
class VerifyResetOTPView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        user = CustomUser.objects.filter(email=email, otp=otp).first()

        if user:
            return Response({"message": "OTP verified! You can now set a new password."}, status=200)
        return Response({"error": "Invalid OTP!"}, status=400)

# 3️⃣ Step: Update Password
class UpdatePasswordView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        
        user = CustomUser.objects.filter(email=email).first()

        if not user:
            return Response({"error": "User not found!"}, status=404)

        # Password update aur OTP clear
        user.password = make_password(new_password)
        user.otp = None
        user.save()

        return Response({"message": "Password updated successfully!"}, status=200)