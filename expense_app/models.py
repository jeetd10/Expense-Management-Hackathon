# expense_app/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

# --- 1. Company and User Models ---

ROLE_CHOICES = (
    ('ADMIN', 'Admin'),
    ('MANAGER', 'Manager'),
    ('EMPLOYEE', 'Employee'),
)

class Company(models.Model):
    # Auto-created on first login/signup [cite: 11]
    name = models.CharField(max_length=100) 
    # Set to selected country's currency [cite: 11]
    default_currency = models.CharField(max_length=3) 

    def __str__(self):
        return self.name

class User(AbstractUser):
    # Custom User model replacing Django's default
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    # Assign and change roles: Employee, Manager, Admin [cite: 14]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='EMPLOYEE') 
    # Define manager relationships for employees 
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members') 
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# --- 2. Expense Models ---

class Expense(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    # Employee submits expense claims [cite: 17]
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    # Amount can be different from company's currency [cite: 18]
    amount_claimed = models.DecimalField(max_digits=10, decimal_places=2)
    currency_claimed = models.CharField(max_length=3) 
    # Amount converted to company's default currency
    amount_in_company_currency = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    # Category, Description, Date, etc. [cite: 19]
    category = models.CharField(max_length=50) 
    description = models.TextField() 
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING') 

    def __str__(self):
        return f"Expense #{self.id} by {self.user.username}"


# --- 3. Approval Workflow Models ---

class ApprovalRule(models.Model):
    # Admin can configure approval rules [cite: 44]
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    
    RULE_TYPE_CHOICES = (
        ('PERCENTAGE', 'Percentage Rule'),      # e.g., 60% of approvers approve [cite: 39]
        ('SPECIFIC', 'Specific Approver Rule'), # e.g., If CFO approves [cite: 40]
        ('HYBRID', 'Hybrid Rule'),              # Combine both [cite: 41]
    )
    
    # Check if IS MANAGER APPROVER field is checked [cite: 22]
    is_manager_first_approver = models.BooleanField(default=True)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES, null=True, blank=True) 
    threshold_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    specific_approver_role = models.CharField(max_length=20, null=True, blank=True) # e.g., 'CFO'
    
    def __str__(self):
        return f"Rules for {self.company.name}"

class ApprovalStep(models.Model):
    # Tracks multi-level approvals [cite: 6]
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    approver = models.ForeignKey(User, on_delete=models.CASCADE)
    # Admin can define their sequence [cite: 23]
    sequence = models.IntegerField() 
    status = models.CharField(max_length=10, default='PENDING') 
    # Approve/Reject with comments [cite: 35]
    comments = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['sequence'] # Ensure the correct order for workflow

    def __str__(self):
        return f"Step {self.sequence} for Expense #{self.expense.id}"