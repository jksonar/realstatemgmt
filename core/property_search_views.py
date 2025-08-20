from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.response import Response
from django.utils import timezone
from .models import Property, SearchHistory
from .serializers import PropertySerializer

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