from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from apps.properties.models import Property
from .models import SearchHistory, SavedSearch, AdvancedSearchFilter
from .serializers import PropertySerializer, SavedSearchSerializer

class PropertySearchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for advanced search and filtering of properties with search history tracking.
    """
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'area', 'property_type', 'status', 'furnished_type']
    search_fields = ['address', 'city', 'area']
    ordering_fields = ['rent_amount', 'size_sqft', 'created_at']
    
    def get_queryset(self):
        """
        Override get_queryset to apply advanced filters.
        """
        queryset = super().get_queryset()
        
        # Apply advanced filters if present
        advanced_filters = self.request.query_params.get('advanced_filters')
        if advanced_filters:
            try:
                import json
                filters_dict = json.loads(advanced_filters)
                
                # Apply rent_amount range filter
                if 'rent_amount' in filters_dict:
                    rent_filter = filters_dict['rent_amount']
                    if 'min' in rent_filter:
                        queryset = queryset.filter(rent_amount__gte=rent_filter['min'])
                    if 'max' in rent_filter:
                        queryset = queryset.filter(rent_amount__lte=rent_filter['max'])
                
                # Apply size_sqft range filter
                if 'size_sqft' in filters_dict:
                    size_filter = filters_dict['size_sqft']
                    if 'min' in size_filter:
                        queryset = queryset.filter(size_sqft__gte=size_filter['min'])
                    if 'max' in size_filter:
                        queryset = queryset.filter(size_sqft__lte=size_filter['max'])
                
                # Apply amenities filter
                if 'amenities' in filters_dict:
                    amenities = filters_dict['amenities']
                    if isinstance(amenities, list) and amenities:
                        # Create a complex query for amenities
                        q_objects = Q()
                        for amenity in amenities:
                            q_objects |= Q(amenities__contains=amenity)
                        queryset = queryset.filter(q_objects)
            except json.JSONDecodeError:
                pass
        
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Override list method to record search queries in history.
        """
        # Record search query if present
        search_query = request.query_params.get('search')
        if search_query and search_query.strip():
            # Check if the same query exists for this user in the last 24 hours
            from datetime import timedelta
            recent_search = SearchHistory.objects.filter(
                user=request.user,
                query__iexact=search_query.strip(),
                timestamp__gte=timezone.now() - timedelta(hours=24)
            ).first()
            
            if not recent_search:
                SearchHistory.objects.create(
                    user=request.user,
                    query=search_query.strip()
                )
            else:
                # Update timestamp of existing search
                recent_search.timestamp = timezone.now()
                recent_search.save()
        
        # Record filter-based searches as well
        filter_params = []
        for field in self.filterset_fields:
            value = request.query_params.get(field)
            if value:
                filter_params.append(f"{field}:{value}")
        
        if filter_params and not search_query:
            filter_query = " ".join(filter_params)
            recent_search = SearchHistory.objects.filter(
                user=request.user,
                query__iexact=filter_query,
                timestamp__gte=timezone.now() - timedelta(hours=24)
            ).first()
            
            if not recent_search:
                SearchHistory.objects.create(
                    user=request.user,
                    query=filter_query
                )
            else:
                recent_search.timestamp = timezone.now()
                recent_search.save()
        
        return super().list(request, *args, **kwargs)
        
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export search results to CSV.
        """
        import csv
        from django.http import HttpResponse
        
        # Get the queryset based on the current filters
        queryset = self.filter_queryset(self.get_queryset())
        
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="property_search_results.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        writer.writerow(['Property ID', 'Address', 'City', 'Area', 'Type', 'Size (sq ft)', 
                        'Rent Amount', 'Deposit', 'Status', 'Furnished Type'])
        
        # Add data rows
        for property in queryset:
            writer.writerow([
                property.property_id,
                property.address,
                property.city,
                property.area,
                property.property_type,
                property.size_sqft,
                property.rent_amount,
                property.deposit_amount,
                property.status,
                property.furnished_type
            ])
        
        return response
        
    @action(detail=False, methods=['get'])
    def load_saved_search(self, request):
        """
        Load a saved search by ID.
        """
        search_id = request.query_params.get('id')
        if not search_id:
            return Response({'error': 'No search ID provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            saved_search = SavedSearch.objects.get(id=search_id, user=request.user)
            
            # Update last_used timestamp
            saved_search.last_used = timezone.now()
            saved_search.save()
            
            # Return the saved search parameters
            return Response({
                'query_params': saved_search.query_params,
                'is_advanced': saved_search.is_advanced,
                'advanced_filters': saved_search.advanced_filters
            })
        except SavedSearch.DoesNotExist:
            return Response({'error': 'Saved search not found'}, status=status.HTTP_404_NOT_FOUND)
            
    @action(detail=False, methods=['post'])
    def save_search(self, request):
        """
        Save the current search parameters as a new saved search.
        """
        name = request.data.get('name')
        if not name:
            return Response({'error': 'Search name is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract query parameters
        query_params = {}
        for key, value in request.query_params.items():
            if key not in ['format', 'page', 'page_size']:
                query_params[key] = value
        
        # Check if this is an advanced search
        is_advanced = request.data.get('is_advanced', False)
        advanced_filters = {}
        
        if is_advanced:
            # Extract advanced filters from request data
            if 'price_range' in request.data:
                advanced_filters['price_range'] = request.data['price_range']
            if 'size_range' in request.data:
                advanced_filters['size_range'] = request.data['size_range']
            if 'amenities' in request.data:
                advanced_filters['amenities'] = request.data['amenities']
        
        # Create the saved search
        saved_search = SavedSearch.objects.create(
            user=request.user,
            name=name,
            query_params=query_params,
            is_advanced=is_advanced,
            advanced_filters=advanced_filters,
            last_used=timezone.now()
        )
        
        # Return the created saved search
        serializer = SavedSearchSerializer(saved_search)
        return Response(serializer.data, status=status.HTTP_201_CREATED)