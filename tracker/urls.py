from django.urls import path

from .views import CategoryListView, TransactionDetailView, TransactionListCreateView, add_category, custom_dashboard, delete_category, edit_category, portal_logout, toggle_user_status, user_transactions

urlpatterns = [
    path('transactions/', TransactionListCreateView.as_view(), name='transactions'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
    path('portal/', custom_dashboard, name='custom_dashboard'),
    path('portal/category/add/', add_category, name='add_category'), # 👈 YE LINE CHECK KARO
    path('portal/category/edit/<int:cat_id>/', edit_category, name='edit_category'),
    path('portal/user/toggle/<int:user_id>/', toggle_user_status, name='toggle_user'),
    path('portal/category/delete/<int:cat_id>/', delete_category, name='delete_category'),
    path('portal/logout/', portal_logout, name='portal_logout'),
    path('portal/user/<int:user_id>/transactions/', user_transactions, name='user_transactions'),
]