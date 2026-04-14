from rest_framework import generics
from rest_framework.views import APIView 
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, logout
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta

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

# 🎯 YAHI FUNCTION MISSING THA JISKI WAJAH SE CRASH HUA
class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class CategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Hidden flag check for smart initialization
        is_initialized = UserCustomCategory.objects.filter(user=request.user, name="__INIT__").exists()

        if not is_initialized:
            default_cats = Category.objects.all()
            for cat in default_cats:
                UserCustomCategory.objects.get_or_create(
                    user=request.user,
                    name=cat.name,
                    defaults={'category_type': getattr(cat, 'category_type', 'EXPENSE')}
                )
            # Hidden flag save karo
            UserCustomCategory.objects.create(
                user=request.user, 
                name="__INIT__", 
                category_type="EXPENSE"
            )
            
        user_cats = UserCustomCategory.objects.filter(user=request.user).exclude(name="__INIT__")

        data = []
        for c in user_cats:
            data.append({
                'id': c.id,
                'name': c.name,
                'category_type': getattr(c, 'category_type', 'EXPENSE')
            })
        return Response(data)
    
    def post(self, request):
        name = request.data.get('name')
        cat_type = request.data.get('category_type', 'EXPENSE')
        
        if not name:
            return Response({"error": "Name is required"}, status=400)
        
        obj, created = UserCustomCategory.objects.get_or_create(
            user=request.user,
            name=name,
            defaults={'category_type': cat_type}
        )
        return Response({"id": obj.id, "name": obj.name, "category_type": obj.category_type})


class CategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            cat = UserCustomCategory.objects.get(id=pk, user=request.user)
            cat.name = request.data.get('name', cat.name)
            cat.save()
            return Response({"status": "success", "name": cat.name})
        except UserCustomCategory.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)

    def delete(self, request, pk):
        try:
            cat = UserCustomCategory.objects.get(id=pk, user=request.user)
            cat.delete()
            return Response({"status": "deleted"}, status=204)
        except UserCustomCategory.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)


# ==========================================
# 💻 WEB ADMIN PORTAL VIEWS 
# ==========================================

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

@staff_member_required(login_url='/admin/login/')
def user_transactions(request, user_id):
    if str(user_id) == '0':
        txs = Transaction.objects.all().order_by('-date')
        user_name = "All Users"
    else:
        user = get_object_or_404(User, id=user_id)
        txs = Transaction.objects.filter(user=user).order_by('-date')
        user_name = user.username
    
    period = request.GET.get('period', 'all')
    now = timezone.now() 
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if period == 'day':
        txs = txs.filter(date__gte=today_start)
    elif period == 'week':
        start_week = today_start - timedelta(days=7)
        txs = txs.filter(date__gte=start_week)
    elif period == 'month':
        start_month = today_start - timedelta(days=30)
        txs = txs.filter(date__gte=start_month)
    elif period == 'year':
        txs = txs.filter(date__year=now.year)
    elif period == 'custom':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and end_date:
            txs = txs.filter(date__range=[start_date, end_date + " 23:59:59"])

    data = []
    for tx in txs:
        data.append({
            'id': tx.id,
            'username': tx.user.username if tx.user else 'Unknown',
            'date': tx.date.strftime("%d %b %Y") if tx.date else "-",
            'category': str(tx.category),
            'type': tx.transaction_type,
            'amount': str(tx.amount),
            'note': tx.note if tx.note else '-'
        })
    
    return JsonResponse({
        'user': user_name, 
        'transactions': data,
        'total_count': txs.count()
    })

@staff_member_required(login_url='/admin/login/')
def global_transactions(request):
    txs = Transaction.objects.all().order_by('-date')
    
    period = request.GET.get('period', 'all')
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if period == 'day':
        txs = txs.filter(date__gte=today_start)
    elif period == 'week':
        start_week = today_start - timedelta(days=7)
        txs = txs.filter(date__gte=start_week)
    elif period == 'month':
        start_month = today_start - timedelta(days=30)
        txs = txs.filter(date__gte=start_month)
    elif period == 'year':
        txs = txs.filter(date__year=now.year)
    elif period == 'custom':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and end_date:
            txs = txs.filter(date__range=[start_date, end_date + " 23:59:59"])

    data = []
    for tx in txs:
        data.append({
            'id': tx.id,
            'username': tx.user.username if tx.user else 'Unknown',
            'date': tx.date.strftime("%d %b %Y") if tx.date else "-",
            'category': str(tx.category),
            'type': tx.transaction_type,
            'amount': str(tx.amount),
        })
    
    return JsonResponse({'transactions': data})

def portal_logout(request):
    logout(request)
    return redirect('/admin/login/')