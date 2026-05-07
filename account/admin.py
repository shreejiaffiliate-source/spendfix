from django.contrib import admin
from django.contrib.auth.models import Group 
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Group ko hata rahe hain clean look ke liye
admin.site.unregister(Group)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # Table mein kaunse columns dikhane hain
    list_display = ('id', 'get_full_name_label', 'email', 'phone', 'is_active')

    # 🎯 NAYA FIX: Username column ka header badalne ke liye
    def get_full_name_label(self, obj):
        return obj.username
    get_full_name_label.short_description = 'Full Name' # Yahan header badlega
    
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