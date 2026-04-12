from django.db import models

from django.db import models
from django.conf import settings
from django.utils import timezone


#category 
class Category(models.Model):
    # Do hi option honge
    TYPE_CHOICES = (
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    )
    
    name = models.CharField(max_length=50, unique=True)
    category_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='EXPENSE') # 🎯 Naya field
    keywords = models.TextField(blank=True, null=True, help_text="Comma separated keywords for scanner")
    
    def __str__(self):
        return f"{self.name} ({self.category_type})"


# 🎯 2. NAYI TABLE: SIRF USER KI CUSTOM CATEGORIES KE LIYE
class UserCustomCategory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="custom_categories")
    name = models.CharField(max_length=50)
    category_type = models.CharField(max_length=10, choices=Category.TYPE_CHOICES, default='EXPENSE')
    
    class Meta:
        unique_together = ('user', 'name') # Ek user 2 same naam wali category nahi bana sakta

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.category_type})"
    
    
# trabsaction 
class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='EXPENSE')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    note = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField(default=timezone.localdate)
    bill_image = models.ImageField(upload_to='bills/', blank=True, null=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.user.first_name} | {self.transaction_type} | ₹{self.amount}"