from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Lead, LeadSource, LeadActivity
from .serializers import LeadSerializer, LeadSourceSerializer, LeadActivitySerializer, LeadListSerializer

class LeadSourceViewSet(viewsets.ModelViewSet):
    queryset = LeadSource.objects.all()
    serializer_class = LeadSourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'source', 'assigned_to', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'notes']
    ordering_fields = ['inquiry_date', 'next_follow_up', 'score', 'last_name']
    ordering = ['-inquiry_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LeadListSerializer
        return LeadSerializer
    
    @action(detail=True, methods=['post'])
    def add_activity(self, request, pk=None):
        lead = self.get_object()
        serializer = LeadActivitySerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(lead=lead, performed_by=request.user)
            
            # Update the lead's last_contact_date
            lead.last_contact_date = timezone.now()
            lead.save(update_fields=['last_contact_date'])
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        lead = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status or new_status not in dict(Lead.LEAD_STATUS_CHOICES).keys():
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        # If converting the lead, set the converted_date
        if new_status == 'converted' and lead.status != 'converted':
            lead.converted_date = timezone.now()
        
        lead.status = new_status
        lead.save()
        
        # Create an activity for the status change
        LeadActivity.objects.create(
            lead=lead,
            activity_type='note',
            description=f"Status changed to {dict(Lead.LEAD_STATUS_CHOICES)[new_status]}",
            performed_by=request.user,
            activity_date=timezone.now()
        )
        
        return Response(LeadSerializer(lead).data)
    
    @action(detail=True, methods=['post'])
    def schedule_follow_up(self, request, pk=None):
        lead = self.get_object()
        follow_up_date = request.data.get('next_follow_up')
        
        if not follow_up_date:
            return Response({'error': 'Follow-up date is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        lead.next_follow_up = follow_up_date
        lead.save(update_fields=['next_follow_up'])
        
        # Create an activity for the follow-up scheduling
        LeadActivity.objects.create(
            lead=lead,
            activity_type='task',
            description=f"Follow-up scheduled for {follow_up_date}",
            performed_by=request.user,
            activity_date=timezone.now()
        )
        
        return Response(LeadSerializer(lead).data)

class LeadActivityViewSet(viewsets.ModelViewSet):
    queryset = LeadActivity.objects.all()
    serializer_class = LeadActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['lead', 'activity_type', 'performed_by']
    ordering_fields = ['activity_date', 'created_at']
    ordering = ['-activity_date']
    
    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)
