from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import SearchHistory, SavedSearch, AdvancedSearchFilter
from apps.properties.models import Property
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate sample search history and saved searches for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Number of users to create search history for'
        )
        parser.add_argument(
            '--searches',
            type=int,
            default=50,
            help='Number of search history entries to create'
        )

    def create_advanced_search_filters(self):
        # Define the advanced search filters
        filters = [
            {'name': 'Price Range', 'field_name': 'rent_amount', 'filter_type': 'range', 'display_order': 1},
            {'name': 'Size (sq ft)', 'field_name': 'size_sqft', 'filter_type': 'range', 'display_order': 2},
            {'name': 'Property Type', 'field_name': 'property_type', 'filter_type': 'exact', 'display_order': 3},
            {'name': 'City', 'field_name': 'city', 'filter_type': 'exact', 'display_order': 4},
            {'name': 'Area', 'field_name': 'area', 'filter_type': 'contains', 'display_order': 5},
            {'name': 'Status', 'field_name': 'status', 'filter_type': 'exact', 'display_order': 6},
            {'name': 'Furnished Type', 'field_name': 'furnished_type', 'filter_type': 'exact', 'display_order': 7},
            {'name': 'Amenities', 'field_name': 'amenities', 'filter_type': 'contains', 'display_order': 8},
        ]
        
        # Create or update filters
        for filter_data in filters:
            obj, created = AdvancedSearchFilter.objects.update_or_create(
                field_name=filter_data['field_name'],
                defaults={
                    'name': filter_data['name'],
                    'filter_type': filter_data['filter_type'],
                    'display_order': filter_data['display_order'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f"Created filter: {obj.name}")
            else:
                self.stdout.write(f"Updated filter: {obj.name}")
    
    def handle(self, *args, **options):
        users_count = options['users']
        searches_count = options['searches']
        
        # Create advanced search filters
        self.create_advanced_search_filters()
        
        # Sample search queries
        sample_queries = [
            'Mumbai 2BHK',
            'Delhi furnished apartment',
            'Bangalore IT park',
            'Pune Baner area',
            'Chennai OMR',
            'Hyderabad Gachibowli',
            '3BHK available',
            'furnished flat',
            'semi-furnished',
            'unfurnished apartment',
            'luxury villa',
            'budget apartment',
            'near metro station',
            'parking available',
            'gym facility',
            'swimming pool',
            'security guard',
            'power backup',
            'water supply',
            'internet connection',
            'Andheri West',
            'Koramangala',
            'Whitefield',
            'Electronic City',
            'Sector 62',
            'Golf Course Road',
            'MG Road',
            'Brigade Road',
            'Connaught Place',
            'Karol Bagh'
        ]
        
        # Get or create users
        users = []
        for i in range(users_count):
            username = f'testuser{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': f'Test',
                    'last_name': f'User {i+1}'
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(f'Created user: {username}')
            users.append(user)
        
        # Create search history entries
        search_history_created = 0
        for _ in range(searches_count):
            user = random.choice(users)
            query = random.choice(sample_queries)
            
            # Create timestamp within last 30 days
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            timestamp = timezone.now() - timedelta(days=days_ago, hours=hours_ago)
            
            # Check if similar search exists for this user recently
            existing = SearchHistory.objects.filter(
                user=user,
                query__iexact=query,
                timestamp__gte=timestamp - timedelta(hours=24)
            ).first()
            
            if not existing:
                SearchHistory.objects.create(
                    user=user,
                    query=query,
                    timestamp=timestamp
                )
                search_history_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {search_history_created} search history entries')
        )
        
        # Create some saved searches
        saved_searches_data = [
            {
                'name': 'Mumbai 2BHK Furnished',
                'query_params': {
                    'city': 'Mumbai',
                    'property_type': '2BHK',
                    'furnished_type': 'furnished',
                    'status': 'available'
                },
                'is_advanced': True,
                'advanced_filters': {
                    'rent_amount': {'min': 15000, 'max': 30000},
                    'size_sqft': {'min': 750, 'max': 1200},
                    'amenities': ['parking', 'security']
                }
            },
            {
                'name': 'Bangalore IT Corridor',
                'query_params': {
                    'city': 'Bangalore',
                    'area': 'Electronic City',
                    'status': 'available'
                },
                'is_advanced': True,
                'advanced_filters': {
                    'rent_amount': {'min': 20000, 'max': 40000},
                    'size_sqft': {'min': 900, 'max': 1500},
                    'amenities': ['gym', 'power_backup', 'swimming_pool']
                }
            },
            {
                'name': 'Budget Apartments',
                'query_params': {
                    'rent_amount__lte': '25000',
                    'status': 'available',
                    'ordering': 'rent_amount'
                },
                'is_advanced': False,
                'advanced_filters': {}
            },
            {
                'name': 'Luxury 3BHK',
                'query_params': {
                    'property_type': '3BHK',
                    'rent_amount__gte': '50000',
                    'furnished_type': 'furnished'
                },
                'is_advanced': True,
                'advanced_filters': {
                    'rent_amount': {'min': 50000, 'max': 100000},
                    'size_sqft': {'min': 1500, 'max': 2500},
                    'amenities': ['gym', 'swimming_pool', 'security']
                }
            }
        ]
        
        saved_searches_created = 0
        for user in users[:3]:  # Create saved searches for first 3 users
            for search_data in saved_searches_data:
                saved_search, created = SavedSearch.objects.get_or_create(
                    user=user,
                    name=search_data['name'],
                    defaults={
                        'query_params': search_data['query_params'],
                        'is_advanced': search_data['is_advanced'],
                        'advanced_filters': search_data['advanced_filters']
                    }
                )
                if created:
                    saved_searches_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {saved_searches_created} saved searches')
        )
        
        # Display summary
        total_search_history = SearchHistory.objects.count()
        total_saved_searches = SavedSearch.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary:\n'
                f'Total users: {User.objects.count()}\n'
                f'Total search history entries: {total_search_history}\n'
                f'Total saved searches: {total_saved_searches}\n'
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS('Sample search data populated successfully!')
        )