# expense_app/serializers.py
from rest_framework import serializers
from .models import Expense, User

class ExpenseSubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer used by the Employee for submitting new expenses.
    """
    class Meta:
        model = Expense
        # These are the fields the Employee submits
        fields = (
            'amount_claimed', 
            'currency_claimed', 
            'category', 
            'description', 
            'date',
        )

    def validate_amount_claimed(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount claimed must be positive.")
        return value

class UserSerializer(serializers.ModelSerializer):
    """
    Used to show user details without exposing sensitive info.
    """
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'role')

class ExpenseDetailSerializer(serializers.ModelSerializer):
    """
    Used for viewing expense history and details by all roles.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Expense
        fields = (
            'id', 'user', 'amount_claimed', 'currency_claimed', 
            'amount_in_company_currency', 'category', 'description', 
            'date', 'status'
        )