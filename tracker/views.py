from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, logout
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

from .models import Category, Transaction
from .serializers import CategorySerializer, TransactionSerializer

User = get_user_model()

# ==========================================
# 📱 FLUTTER APP API VIEWS
# ==========================================

class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    # 🔥 Ye line zaroori hai, iska matlab hai bina token ke no entry!
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


# 🟢 NAYA CLASS ADD KARO (Delete/Update ke liye)
class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    # Ye function ensure karega ki user sirf APNA hi data delete kar paye, kisi aur ka nahi
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


# ==========================================
# 💻 WEB ADMIN PORTAL VIEWS
# ==========================================

# 1. Dashboard View (🎯 YAHAN GUARD LAGA DIYA HAI)
@staff_member_required(login_url='/admin/login/')
def custom_dashboard(request):
    users = User.objects.all().order_by('-date_joined')
    categories = Category.objects.all().order_by('id')
    total_tx = Transaction.objects.count()
    return render(request, 'tracker/dashboard.html', {
        'users_list': users,
        'categories_list': categories,
        'total_users': users.count(),
        'total_categories': categories.count(),
        'total_transactions': total_tx,  
    })

# 2. Block/Unblock User
@staff_member_required(login_url='/admin/login/')
def toggle_user_status(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active # Toggle status
        user.save()
        return JsonResponse({'status': 'success', 'is_active': user.is_active})

# 3. Add Category
@staff_member_required(login_url='/admin/login/')
def add_category(request):
    if request.method == "POST":
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            return redirect('custom_dashboard')

# 4. Edit Category
@staff_member_required(login_url='/admin/login/')
def edit_category(request, cat_id):
    if request.method == "POST":
        category = get_object_or_404(Category, id=cat_id)
        name = request.POST.get('name')
        if name:
            category.name = name
            category.save()
    return redirect('custom_dashboard')

# 5. Delete Category
@staff_member_required(login_url='/admin/login/')
def delete_category(request, cat_id):
    if request.method == "POST":
        category = get_object_or_404(Category, id=cat_id)
        category.delete()
        return JsonResponse({'status': 'success'})

from django.utils import timezone
from datetime import timedelta

@staff_member_required(login_url='/admin/login/')
def user_transactions(request, user_id):
    user = get_object_or_404(User, id=user_id)
    txs = Transaction.objects.filter(user=user).order_by('-date')
    
    period = request.GET.get('period', 'all')
    now = timezone.now().date() # 🎯 Aaj ki date le li
    
    if period == 'day':
        # 🎯 FIX: 'date__date' ki jagah sirf 'date' use karo
        txs = txs.filter(date=now) 
    elif period == 'week':
        start_week = now - timedelta(days=now.weekday())
        txs = txs.filter(date__gte=start_week)
    elif period == 'month':
        # 🎯 DateField par year aur month lookup sahi kaam karte hain
        txs = txs.filter(date__month=now.month, date__year=now.year)
    elif period == 'year':
        txs = txs.filter(date__year=now.year)

    data = []
    for tx in txs:
        data.append({
            'id': tx.id,
            'date': tx.date.strftime("%d %b %Y") if tx.date else "-",
            'category': tx.category,
            'type': tx.transaction_type,
            'amount': str(tx.amount),
            'note': tx.note if tx.note else '-'
        })
    
    return JsonResponse({
        'user': user.username, 
        'transactions': data,
        'total_count': txs.count()
    })

# 🚪 Logout
def portal_logout(request):
    logout(request)
    return redirect('/admin/login/')