from django.contrib import admin
from django.contrib.auth.models import Group 
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Group ko hata rahe hain clean look ke liye
admin.site.unregister(Group)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # Table list mein kya dikhega
    list_display = ['id', 'username', 'email', 'phone', 'is_active']
    
    # 🔥 EXACT VASTRAFIX LAYOUT 🔥
    fieldsets = (
        ('Account Info', {
            'fields': ('username', 'email', 'phone', 'password', 'fcm_token')
        }),
        ('Status', {
            'fields': ('is_active',)  # Yahan se staff status humesha ke liye hata diya
        }),
    )

# Ab apna CustomUser register kijiye
admin.site.register(CustomUser, CustomUserAdmin)