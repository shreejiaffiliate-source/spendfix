from django.urls import path

from .views import (
    CategoryListView, 
    CategoryDetailView, # 🎯 NAYA: Ise import karna zaroori hai Edit/Delete ke liye
    TransactionDetailView, 
    TransactionListCreateView, 
    add_category, 
    custom_dashboard, 
    delete_category, 
    edit_category, 
    global_transactions, 
    portal_logout, 
    toggle_user_status, 
    user_transactions
)

urlpatterns = [
    # 📱 FLUTTER APP URLS
    path('transactions/', TransactionListCreateView.as_view(), name='transactions'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
    
    path('categories/', CategoryListView.as_view(), name='category-list'),
    # 🎯 NAYA: Flutter se Custom Category Edit aur Delete karne ke liye raasta
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),

    # 💻 WEB PORTAL URLS
    path('portal/', custom_dashboard, name='custom_dashboard'),
    path('portal/category/add/', add_category, name='add_category'),
    path('portal/category/edit/<int:cat_id>/', edit_category, name='edit_category'),
    path('portal/category/delete/<int:cat_id>/', delete_category, name='delete_category'),
    
    path('portal/user/toggle/<int:user_id>/', toggle_user_status, name='toggle_user'),
    path('portal/user/<int:user_id>/transactions/', user_transactions, name='user_transactions'),
    
    path('api/portal/global_transactions/', global_transactions, name='global_transactions'),
    path('portal/logout/', portal_logout, name='portal_logout'),
]