from rest_framework import serializers
from .models import Property, FavoriteProperty

class PropertySerializer(serializers.ModelSerializer):
    """Serializer for the Property model"""
    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, data):
        """Validate that rent and deposit amounts are positive"""
        if 'rent_amount' in data and data['rent_amount'] <= 0:
            raise serializers.ValidationError({'rent_amount': 'Rent amount must be positive'})
        if 'deposit_amount' in data and data['deposit_amount'] <= 0:
            raise serializers.ValidationError({'deposit_amount': 'Deposit amount must be positive'})
        return data

class PropertyDetailSerializer(PropertySerializer):
    """Detailed serializer for the Property model with additional information"""
    class Meta(PropertySerializer.Meta):
        fields = '__all__'
        depth = 1  # Include related objects one level deep

class FavoritePropertySerializer(serializers.ModelSerializer):
    """Serializer for the FavoriteProperty model"""
    property_details = PropertySerializer(source='property', read_only=True)
    
    class Meta:
        model = FavoriteProperty
        fields = ('id', 'user', 'property', 'property_details', 'created_at')
        read_only_fields = ('created_at',)