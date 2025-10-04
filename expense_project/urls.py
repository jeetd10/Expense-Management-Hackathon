# expense_project/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from expense_app.views import ExpenseSubmissionViewSet, ExpenseApprovalViewSet

# Create a router for viewsets
router = DefaultRouter()
# The submission endpoint is registered with the router
router.register(r'expenses/submit', ExpenseSubmissionViewSet, basename='expense-submit')

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Employee/Admin view/submit expenses
    # This line includes all URLs registered with the router (like /api/expenses/submit/)
    path('api/', include(router.urls)), 

    # 2. Manager/Admin approval endpoint (PUT method for action)
    path('api/expenses/approve/<int:pk>/', ExpenseApprovalViewSet.as_view({'put': 'update'}), name='expense-approve'),

    # 3. Manager/Admin pending list endpoint (GET method for listing)
    path('api/expenses/pending/', ExpenseApprovalViewSet.as_view({'get': 'list'}), name='expense-pending'),
]