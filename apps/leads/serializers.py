from rest_framework import serializers
from .models import Lead, LeadSource, LeadActivity
from apps.accounts.serializers import UserSerializer
from apps.properties.serializers import PropertySerializer

class LeadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadSource
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']

class LeadActivitySerializer(serializers.ModelSerializer):
    performed_by = UserSerializer(read_only=True)
    performed_by_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = LeadActivity
        fields = ['id', 'lead', 'activity_type', 'description', 'performed_by', 
                  'performed_by_id', 'activity_date', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class LeadSerializer(serializers.ModelSerializer):
    source = LeadSourceSerializer(read_only=True)
    source_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    related_property = PropertySerializer(read_only=True)
    related_property_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    full_name = serializers.CharField(read_only=True)
    activities = LeadActivitySerializer(many=True, read_only=True)
    
    class Meta:
        model = Lead
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email', 'phone', 
                  'related_property', 'related_property_id', 'source', 'source_id', 'assigned_to', 
                  'assigned_to_id', 'status', 'score', 'notes', 'inquiry_date', 
                  'last_contact_date', 'next_follow_up', 'converted_date', 
                  'is_active', 'created_at', 'updated_at', 'activities']
        read_only_fields = ['inquiry_date', 'created_at', 'updated_at']

class LeadListSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    property_address = serializers.CharField(source='related_property.address', read_only=True)
    
    class Meta:
        model = Lead
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 
                  'source_name', 'assigned_to_name', 'property_address', 
                  'status', 'score', 'inquiry_date', 'next_follow_up']
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None