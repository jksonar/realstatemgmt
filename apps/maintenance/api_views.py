from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
import uuid

from .models import MaintenanceRequest
from .serializers import MaintenanceRequestSerializer, MaintenanceRequestDetailSerializer

class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing maintenance requests
    """
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property', 'tenant', 'issue_type', 'priority', 'status', 'assigned_to']
    search_fields = ['request_id', 'description', 'property__address', 'tenant__name']
    ordering_fields = ['reported_date', 'completed_date', 'priority']
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return MaintenanceRequestDetailSerializer
        return MaintenanceRequestSerializer
    
    def perform_create(self, serializer):
        # Generate a unique request ID if not provided
        if not serializer.validated_data.get('request_id'):
            request_id = f"MR-{uuid.uuid4().hex[:8].upper()}"
            serializer.save(request_id=request_id)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def open(self, request):
        """
        Return open maintenance requests (reported or in_progress)
        """
        open_requests = self.get_queryset().filter(
            status__in=['reported', 'in_progress']
        ).order_by('-priority', 'reported_date')
        
        page = self.paginate_queryset(open_requests)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(open_requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """
        Return urgent maintenance requests
        """
        urgent_requests = self.get_queryset().filter(
            priority='urgent',
            status__in=['reported', 'in_progress']
        ).order_by('reported_date')
        
        page = self.paginate_queryset(urgent_requests)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(urgent_requests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assign a maintenance request to someone
        """
        maintenance_request = self.get_object()
        
        # Validate required fields
        if 'assigned_to' not in request.data:
            return Response(
                {'error': 'Assigned to field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the maintenance request
        maintenance_request.assigned_to = request.data['assigned_to']
        if maintenance_request.status == 'reported':
            maintenance_request.status = 'in_progress'
        maintenance_request.save()
        
        serializer = self.get_serializer(maintenance_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark a maintenance request as completed
        """
        maintenance_request = self.get_object()
        
        if maintenance_request.status == 'completed':
            return Response(
                {'error': 'Maintenance request is already marked as completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the maintenance request
        maintenance_request.status = 'completed'
        maintenance_request.completed_date = request.data.get('completed_date', timezone.now())
        if 'cost' in request.data:
            maintenance_request.cost = request.data['cost']
        maintenance_request.save()
        
        serializer = self.get_serializer(maintenance_request)
        return Response(serializer.data)