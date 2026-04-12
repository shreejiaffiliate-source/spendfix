from rest_framework import generics
from rest_framework.views import APIView # 🎯 Naya Import APIView ke liye
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response # 🎯 Naya Import Response ke liye
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, logout
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

# 🎯 NAYA FIX: UserCustomCategory ko import kiya
from .models import Category, Transaction, UserCustomCategory
from .serializers import TransactionSerializer

User = get_user_model()

# ==========================================
# 📱 FLUTTER APP API VIEWS
# ==========================================

class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 🎯 YAHAN SABSE BADA CHANGE HAI (Category List aur Add ek hi jagah)
class CategoryListView(APIView):
    permission_classes = [IsAuthenticated] # Token zaroori hai taaki user pata chale

    # GET: Flutter ko Default aur Custom categories mix karke bhejna
    def get(self, request):
        # 1. Main Static Categories
        default_cats = list(Category.objects.all().values('id', 'name', 'category_type'))
        
        # 2. Sirf is Login User ki Categories
        user_cats = list(UserCustomCategory.objects.filter(user=request.user).values('id', 'name', 'category_type'))
        
        # 3. Dono ko mila diya (Portal pe nahi jayega, sirf Flutter me jayega)
        all_categories = default_cats + user_cats
        return Response(all_categories)
    
    # POST: Flutter se aayi nayi category ko UserCustomCategory mein chup-chap save karna
    def post(self, request):
        name = request.data.get('name')
        cat_type = request.data.get('category_type', 'EXPENSE')
        
        if not name:
            return Response({"error": "Name is required"}, status=400)
        
        # Nayi table mein save karo
        obj, created = UserCustomCategory.objects.get_or_create(
            user=request.user,
            name=name,
            defaults={'category_type': cat_type}
        )
        return Response({
            "id": obj.id, 
            "name": obj.name, 
            "category_type": obj.category_type
        })


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


# ==========================================
# 💻 WEB ADMIN PORTAL VIEWS (Isme kuch change nahi karna)
# ==========================================

@staff_member_required(login_url='/admin/login/')
def custom_dashboard(request):
    users = User.objects.all().order_by('-date_joined')
    categories = Category.objects.all().order_by('id') # 🎯 Portal sirf Main Category dekhega
    total_tx = Transaction.objects.count()
    return render(request, 'tracker/dashboard.html', {
        'users_list': users,
        'categories_list': categories,
        'total_users': users.count(),
        'total_categories': categories.count(),
        'total_transactions': total_tx,  
    })

@staff_member_required(login_url='/admin/login/')
def toggle_user_status(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active 
        user.save()
        return JsonResponse({'status': 'success', 'is_active': user.is_active})

@staff_member_required(login_url='/admin/login/')
def add_category(request):
    if request.method == "POST":
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            return redirect('custom_dashboard')

@staff_member_required(login_url='/admin/login/')
def edit_category(request, cat_id):
    if request.method == "POST":
        category = get_object_or_404(Category, id=cat_id)
        name = request.POST.get('name')
        if name:
            category.name = name
            category.save()
    return redirect('custom_dashboard')

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
    now = timezone.now().date() 
    
    if period == 'day':
        txs = txs.filter(date=now) 
    elif period == 'week':
        start_week = now - timedelta(days=now.weekday())
        txs = txs.filter(date__gte=start_week)
    elif period == 'month':
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

def portal_logout(request):
    logout(request)
    return redirect('/admin/login/')