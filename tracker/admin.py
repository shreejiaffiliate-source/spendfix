from django.contrib import admin
from .models import Category, Transaction

# 1. Category ke liye Custom Admin (ID dikhane ke liye)
class CategoryAdmin(admin.ModelAdmin):
    # 🎯 Ab yahan ID, Name aur Type teeno dikhenge
    list_display = ('id', 'name', 'category_type') 
    
    # Side mein filter bhi daal dete hain taaki Income/Expense alag se dekh sako
    list_filter = ('category_type',)
    search_fields = ('name',)
    ordering = ('id',)

admin.site.register(Category, CategoryAdmin)

class TransactionAdmin(admin.ModelAdmin):
    # Admin panel mein table ke columns kya-kya dikhenge
    list_display = ('id', 'user', 'transaction_type', 'amount', 'category', 'date')
    
    # Right side mein ek filter panel ban jayega (Income/Expense ya Date ke hisaab se filter karne ke liye)
    list_filter = ('transaction_type', 'category', 'date')
    
    # Upar ek search bar aayega jisme Category, Note ya User ka naam daal kar search kar sakte hain
    search_fields = ('category', 'note', 'user__first_name', 'user__email')
    
    # Data ko naye se purane ki taraf sort karke dikhayega
    ordering = ('-date', '-id')

# Apne Model ko Custom Admin ke sath register karein
admin.site.register(Transaction, TransactionAdmin)