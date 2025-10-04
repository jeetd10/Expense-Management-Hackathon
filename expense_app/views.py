# expense_app/views.py - ENHANCED FOR HACKATHON
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, F

# Import your models, serializers, and the currency utility
from .models import Expense, User, ApprovalStep, ApprovalRule
from .serializers import ExpenseSubmissionSerializer, ExpenseDetailSerializer
from .utils import convert_currency


# --- CONDITIONAL APPROVAL HELPER FUNCTION ---
def check_conditional_approval(expense, current_step):
    """Checks if the approval rules are met for auto-approval (Specific or Percentage)."""
    rule = ApprovalRule.objects.filter(company=expense.user.company).first()
    if not rule:
        return False
        
    # 1. Specific Approver Rule (If CFO/Director approves, it's auto-approved) [cite: 40]
    if rule.rule_type in ['SPECIFIC', 'HYBRID'] and rule.specific_approver_role:
        if current_step.approver.role == rule.specific_approver_role:
            print(f"Conditional Rule met: {rule.specific_approver_role} approved. Auto-approving.")
            return True

    # 2. Percentage Rule (If X% of assigned approvers approve) [cite: 39]
    if rule.rule_type in ['PERCENTAGE', 'HYBRID'] and rule.threshold_value:
        # NOTE: This simple version assumes ALL steps are required for the percentage.
        total_steps = expense.approvalstep_set.count()
        if total_steps > 0:
            approved_steps_count = expense.approvalstep_set.filter(status='APPROVED').count()
            
            # Since the current step just approved, count it even if it's not saved yet.
            if current_step.status == 'PENDING':
                 approved_steps_count += 1 

            percentage_approved = (approved_steps_count / total_steps) * 100
            
            if percentage_approved >= rule.threshold_value:
                print(f"Conditional Rule met: {percentage_approved:.0f}% approved ({approved_steps_count}/{total_steps}). Auto-approving.")
                return True
                
    return False


class ExpenseSubmissionViewSet(viewsets.ModelViewSet):
    """API endpoint for employees to submit and view their own expenses."""
    serializer_class = ExpenseDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    # ... (get_queryset and create methods remain the same) ...

    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'EMPLOYEE':
            return Expense.objects.filter(user=user).order_by('-date')
        
        if user.role == 'ADMIN':
            return Expense.objects.all().order_by('-date')
            
        if user.role == 'MANAGER':
            team_members = User.objects.filter(manager=user)
            return Expense.objects.filter(user__in=team_members).order_by('-date')
            
        return Expense.objects.none()

    def create(self, request, *args, **kwargs):
        if request.user.role != 'EMPLOYEE':
            return Response({"detail": "Only employees can submit expenses."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ExpenseSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount_claimed = serializer.validated_data['amount_claimed']
        currency_claimed = serializer.validated_data['currency_claimed']
        
        company = request.user.company
        target_currency = company.default_currency

        amount_converted = convert_currency(
            amount=amount_claimed,
            base_currency=currency_claimed,
            target_currency=target_currency
        )

        if amount_converted is None:
            return Response({"detail": "Failed to convert currency. Check currency code or external API access."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        expense = serializer.save(
            user=request.user, 
            amount_in_company_currency=amount_converted,
            status='PENDING'
        )

        self.initiate_approval_workflow(expense)

        headers = self.get_success_headers(serializer.data)
        return Response(ExpenseDetailSerializer(expense).data, status=status.HTTP_201_CREATED, headers=headers)


    def initiate_approval_workflow(self, expense):
        """Creates multi-level approval steps based on user hierarchy and expense amount."""
        approvers = []
        rule = ApprovalRule.objects.filter(company=expense.user.company).first()
        
        # 1. Manager Approval (Sequence 1) [cite: 22]
        if rule and rule.is_manager_first_approver and expense.user.manager:
            approvers.append(expense.user.manager)
        
        # 2. Secondary Approver based on expense threshold (Multi-level approval) [cite: 6]
        # Example: If expense is over 500 in company currency, require Admin approval (simulating Finance/Director)
        if expense.amount_in_company_currency > 500: 
            admin_user = User.objects.filter(company=expense.user.company, role='ADMIN').first()
            if admin_user:
                approvers.append(admin_user) # Admin/Director is the second approver
        
        # 3. Fallback: If no manager and no threshold met, assign to Admin if no approvers are set
        if not approvers:
            admin_user = User.objects.filter(company=expense.user.company, role='ADMIN').first()
            if admin_user:
                approvers.append(admin_user)
        
        # Create Approval Steps
        for sequence, approver in enumerate(approvers, start=1):
            ApprovalStep.objects.create(
                expense=expense,
                approver=approver,
                sequence=sequence,
                status='PENDING'
            )
        
        if not approvers:
            print(f"WARNING: No initial approver assigned for Expense #{expense.id}. Requires manual Admin assignment.")


class ExpenseApprovalViewSet(viewsets.ViewSet):
    """API endpoint for Managers/Admins to approve/reject expenses."""
    permission_classes = [permissions.IsAuthenticated]

    # ... (list method remains the same) ...

    def list(self, request):
        user = self.request.user
        if user.role not in ['MANAGER', 'ADMIN']:
            return Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        current_pending_steps = ApprovalStep.objects.filter(
            approver=user, 
            status='PENDING'
        ).select_related('expense').order_by('expense__date')
        
        pending_expenses = [step.expense for step in current_pending_steps]
        
        # Managers can view amounts in company's default currency [cite: 44]
        serializer = ExpenseDetailSerializer(pending_expenses, many=True)
        return Response(serializer.data)

    def update(self, request, pk=None):
        user = request.user
        action = request.data.get('action')
        comments = request.data.get('comments', '')

        if user.role not in ['MANAGER', 'ADMIN']:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        expense = get_object_or_404(Expense, pk=pk)
        
        # Find the specific pending step assigned to the current user
        current_step = expense.approvalstep_set.filter(approver=user, status='PENDING').first()

        if not current_step:
            return Response({"detail": "Expense not awaiting your approval or you already acted on it."}, status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'APPROVE':
            current_step.status = 'APPROVED'
            current_step.comments = comments
            current_step.save()
            
            # 1. Check Conditional Rules (Specific Approver/Percentage) [cite: 37]
            if check_conditional_approval(expense, current_step):
                expense.status = 'APPROVED' # Expense auto-approved regardless of remaining sequence
                expense.save()
                return Response(ExpenseDetailSerializer(expense).data)
                
            # 2. Check for Next Sequential Step [cite: 23]
            # Expense moves to the next approver only after the current one approves [cite: 32]
            next_step = ApprovalStep.objects.filter(expense=expense, sequence=current_step.sequence + 1).first()
            
            if next_step:
                # Next step exists: Expense remains 'PENDING' for the next approver
                pass
            else:
                # No more steps: Expense is fully approved
                expense.status = 'APPROVED'
                expense.save()

        elif action == 'REJECT':
            current_step.status = 'REJECTED'
            current_step.comments = comments
            current_step.save()
            expense.status = 'REJECTED' # Rejected at any step ends the workflow [cite: 35]
            expense.save()
            
        else:
            return Response({"detail": "Invalid action. Must be 'APPROVE' or 'REJECT'."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ExpenseDetailSerializer(expense).data)