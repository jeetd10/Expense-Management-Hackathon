# expense_app/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Company, User, Expense, ApprovalRule, ApprovalStep

# Register the User model with the Admin
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    # Customize fields visible in the Admin list and form
    # Note: 'company', 'role', and 'manager' are fields on your custom User model
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('company', 'role', 'manager')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role', 'company', 'manager')
    list_filter = ('role', 'company')

# Register other Expense Management System models
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_currency')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount_claimed', 'currency_claimed', 'amount_in_company_currency', 'status', 'date')
    list_filter = ('status', 'category', 'user__company')
    search_fields = ('user__username', 'description')

@admin.register(ApprovalRule)
class ApprovalRuleAdmin(admin.ModelAdmin):
    list_display = ('company', 'is_manager_first_approver', 'rule_type', 'threshold_value')

@admin.register(ApprovalStep)
class ApprovalStepAdmin(admin.ModelAdmin):
    list_display = ('expense', 'approver', 'sequence', 'status')
    list_filter = ('status', 'approver')