from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from .models import SavedSearch, SearchHistory, AdvancedSearchFilter
from apps.properties.models import FavoriteProperty, Property
from .serializers import SavedSearchSerializer, FavoritePropertySerializer, SearchHistorySerializer, AdvancedSearchFilterSerializer

class AdvancedSearchFilterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for retrieving available advanced search filters.
    """
    queryset = AdvancedSearchFilter.objects.filter(is_active=True).order_by('display_order')
    serializer_class = AdvancedSearchFilterSerializer
    permission_classes = [IsAuthenticated]

class SavedSearchViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing saved searches.
    """
    serializer_class = SavedSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedSearch.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """
        Mark a saved search as used and update its last_used timestamp.
        """
        saved_search = self.get_object()
        saved_search.last_used = timezone.now()
        saved_search.save()
        return Response({'status': 'saved search marked as used'})

class FavoritePropertyViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing favorite properties.
    """
    serializer_class = FavoritePropertySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FavoriteProperty.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SearchHistoryViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing search history with suggestions.
    """
    serializer_class = SearchHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SearchHistory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Check if the same query exists for this user in the last 24 hours
        query = serializer.validated_data['query']
        recent_search = SearchHistory.objects.filter(
            user=self.request.user,
            query__iexact=query,
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).first()
        
        if not recent_search:
            serializer.save(user=self.request.user)
        else:
            # Update timestamp of existing search
            recent_search.timestamp = timezone.now()
            recent_search.save()

    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """
        Get search suggestions based on user's search history and popular searches.
        """
        query = request.query_params.get('q', '').strip()
        suggestions = []
        
        if query:
            # Get user's previous searches that match the query
            user_searches = SearchHistory.objects.filter(
                user=request.user,
                query__icontains=query
            ).values_list('query', flat=True).distinct()[:5]
            
            # Get popular searches from all users that match the query
            popular_searches = SearchHistory.objects.filter(
                query__icontains=query
            ).values('query').annotate(
                count=Count('query')
            ).order_by('-count')[:5]
            
            # Combine and deduplicate suggestions
            suggestions.extend(list(user_searches))
            for search in popular_searches:
                if search['query'] not in suggestions:
                    suggestions.append(search['query'])
            
            # Limit to 10 suggestions
            suggestions = suggestions[:10]
        
        return Response({'suggestions': suggestions})
        
    @action(detail=True, methods=['delete'])
    def delete(self, request, pk=None):
        """
        Delete a specific search history entry.
        """
        try:
            history_entry = self.get_object()
            history_entry.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """
        Clear all search history for the current user.
        """
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get user's recent search history.
        """
        limit = int(request.query_params.get('limit', 10))
        recent_searches = self.get_queryset()[:limit]
        serializer = self.get_serializer(recent_searches, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def popular_terms(self, request):
        """
        Get popular search terms across all users.
        """
        # Get popular search terms from the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        popular_terms = SearchHistory.objects.filter(
            timestamp__gte=thirty_days_ago
        ).values('query').annotate(
            count=Count('query')
        ).order_by('-count')[:20]
        
        return Response({'popular_terms': list(popular_terms)})

    @action(detail=False, methods=['get'])
    def autocomplete(self, request):
        """
        Get autocomplete suggestions based on property data and search history.
        """
        query = request.query_params.get('q', '').strip().lower()
        suggestions = set()
        
        if query and len(query) >= 2:
            # Get suggestions from property cities
            cities = Property.objects.filter(
                city__icontains=query
            ).values_list('city', flat=True).distinct()[:5]
            suggestions.update(cities)
            
            # Get suggestions from property areas
            areas = Property.objects.filter(
                area__icontains=query
            ).values_list('area', flat=True).distinct()[:5]
            suggestions.update(areas)
            
            # Get suggestions from property types
            property_types = Property.objects.filter(
                property_type__icontains=query
            ).values_list('property_type', flat=True).distinct()[:5]
            suggestions.update(property_types)
            
            # Get suggestions from search history
            history_queries = SearchHistory.objects.filter(
                query__icontains=query
            ).values_list('query', flat=True).distinct()[:5]
            suggestions.update(history_queries)
        
        return Response({'autocomplete': sorted(list(suggestions))[:15]})