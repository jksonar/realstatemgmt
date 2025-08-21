from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Property, FavoriteProperty
from .serializers import PropertySerializer, PropertyDetailSerializer, FavoritePropertySerializer
from .filters import PropertyFilter

class PropertyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing properties
    """
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PropertyFilter
    search_fields = ['property_id', 'address', 'city', 'area']
    ordering_fields = ['rent_amount', 'size_sqft', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PropertyDetailSerializer
        return PropertySerializer
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Return only available properties"""
        available_properties = Property.objects.filter(status='available')
        serializer = self.get_serializer(available_properties, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_city(self, request):
        """Group properties by city"""
        city = request.query_params.get('city', None)
        if city:
            properties = Property.objects.filter(city=city)
            serializer = self.get_serializer(properties, many=True)
            return Response(serializer.data)
        return Response({"error": "City parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """Toggle property status between available, occupied, and maintenance"""
        property_obj = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in [choice[0] for choice in Property.STATUS_CHOICES]:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        
        property_obj.status = new_status
        property_obj.save()
        serializer = self.get_serializer(property_obj)
        return Response(serializer.data)

class FavoritePropertyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing favorite properties
    """
    serializer_class = FavoritePropertySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FavoriteProperty.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)