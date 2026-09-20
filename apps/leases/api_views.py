from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Lease
from .serializers import LeaseSerializer, LeaseDetailSerializer
from apps.core.permissions import IsOwnerOrStaff

class LeaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing leases
    """
    queryset = Lease.objects.all()
    serializer_class = LeaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property', 'tenant', 'status', 'start_date', 'end_date']
    search_fields = ['lease_id', 'property__address', 'tenant__name']
    ordering_fields = ['start_date', 'end_date', 'monthly_rent', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return LeaseDetailSerializer
        return LeaseSerializer
    
    def perform_create(self, serializer):
        # Generate a unique lease ID if not provided
        if not serializer.validated_data.get('lease_id'):
            import uuid
            lease_id = f"L-{uuid.uuid4().hex[:8].upper()}"
            serializer.save(lease_id=lease_id)
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Return only active leases
        """
        active_leases = self.get_queryset().filter(status='active')
        page = self.paginate_queryset(active_leases)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(active_leases, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """
        Return leases that are expiring within 30 days
        """
        from django.utils import timezone
        import datetime
        thirty_days_later = timezone.now().date() + datetime.timedelta(days=30)
        expiring_leases = self.get_queryset().filter(
            status='active',
            end_date__lte=thirty_days_later,
            end_date__gte=timezone.now().date()
        )
        page = self.paginate_queryset(expiring_leases)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(expiring_leases, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        """
        Renew a lease with new end date and potentially updated terms
        """
        lease = self.get_object()
        
        # Validate required fields
        if 'end_date' not in request.data:
            return Response(
                {'error': 'End date is required for renewal'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Create a new lease based on the current one
        new_data = {
            'property': lease.property.id,
            'tenant': lease.tenant.id,
            'start_date': lease.end_date,  # New lease starts when old one ends
            'end_date': request.data.get('end_date'),
            'monthly_rent': request.data.get('monthly_rent', lease.monthly_rent),
            'security_deposit': request.data.get('security_deposit', lease.security_deposit),
            'status': 'active'
        }
        
        # Mark the current lease as expired
        lease.status = 'expired'
        lease.save()
        
        # Create the new lease
        serializer = self.get_serializer(data=new_data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """
        Terminate a lease before its end date
        """
        lease = self.get_object()
        
        if lease.status != 'active':
            return Response(
                {'error': 'Only active leases can be terminated'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the lease status
        lease.status = 'terminated'
        lease.save()
        
        return Response({'status': 'Lease terminated successfully'})