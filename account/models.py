from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # 🎯 NAYA FIX 1: Django ke chhupay hue username ko override karke unique=False karo
    username = models.CharField(max_length=150, unique=False)
    
    phone = models.CharField(
        max_length=15, 
        unique=True,      
        null=True,        
        blank=True, 
        default=None      
    )
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)

    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # 🎯 NAYA FIX 2: Agar username unique nahi hai, toh Django ko batao ki login Email se hoga
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone'] # Admin panel se user banate waqt kya zaroori hai

    def __str__(self):
        return self.username
