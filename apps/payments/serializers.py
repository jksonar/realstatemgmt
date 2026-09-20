from rest_framework import serializers
from .models import Payment
from apps.leases.serializers import LeaseSerializer

class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for the Payment model"""
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def validate(self, data):
        """Validate payment data"""
        # Ensure amount is positive
        if data.get('amount') and data['amount'] <= 0:
            raise serializers.ValidationError({'amount': 'Payment amount must be greater than zero'})
        
        # Ensure payment date is not after due date
        if data.get('payment_date') and data.get('due_date') and data['payment_date'] > data['due_date']:
            raise serializers.ValidationError({'payment_date': 'Payment date cannot be after due date'})
        
        return data

class PaymentDetailSerializer(PaymentSerializer):
    """Detailed serializer for the Payment model with additional information"""
    lease_details = LeaseSerializer(source='lease', read_only=True)
    
    class Meta(PaymentSerializer.Meta):
        fields = '__all__'