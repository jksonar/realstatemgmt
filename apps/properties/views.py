from django.views import generic as django_generic
from .models import Property
from .filters import PropertyFilter

from .forms import PropertyForm, BulkUpdatePropertiesForm
from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone
from apps.core.models import AdvancedSearchFilter

class PropertyListView(django_generic.ListView):
    model = Property
    template_name = 'properties/property_list.html'
    context_object_name = 'properties'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter = PropertyFilter(self.request.GET, queryset=queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        return context


class PropertyDetailView(django_generic.DetailView):
    model = Property
    template_name = 'properties/property_detail.html'
    context_object_name = 'property'


class PropertyCreateView(django_generic.CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    success_url = '/properties/'


class PropertyUpdateView(django_generic.UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = 'properties/property_form.html'
    success_url = '/properties/'


class AdvancedSearchView(View):
    def get(self, request):
        # Get all active advanced search filters for the form
        amenities = AdvancedSearchFilter.objects.filter(filter_type='amenities', is_active=True).order_by('display_order')
        property_types = AdvancedSearchFilter.objects.filter(filter_type='property_type', is_active=True).order_by('display_order')
        cities = AdvancedSearchFilter.objects.filter(filter_type='city', is_active=True).order_by('display_order')
        areas = AdvancedSearchFilter.objects.filter(filter_type='area', is_active=True).order_by('display_order')
        statuses = AdvancedSearchFilter.objects.filter(filter_type='status', is_active=True).order_by('display_order')
        furnished_types = AdvancedSearchFilter.objects.filter(filter_type='furnished_type', is_active=True).order_by('display_order')
        
        # Check if we're loading a saved search
        saved_search_id = request.GET.get('saved_search_id')
        saved_search_data = None
        
        if saved_search_id and request.user.is_authenticated:
            from apps.core.models import SavedSearch
            try:
                saved_search = SavedSearch.objects.get(id=saved_search_id, user=request.user)
                saved_search_data = {
                    'id': saved_search.id,
                    'name': saved_search.name,
                    'query_params': saved_search.query_params,
                    'is_advanced': saved_search.is_advanced,
                    'advanced_filters': saved_search.advanced_filters
                }
                
                # Update last_used timestamp
                saved_search.last_used = timezone.now()
                saved_search.save()
            except SavedSearch.DoesNotExist:
                pass
        
        context = {
            'amenities': amenities,
            'property_types': property_types,
            'cities': cities,
            'areas': areas,
            'statuses': statuses,
            'furnished_types': furnished_types,
            'saved_search_data': saved_search_data
        }
        
        return render(request, 'properties/advanced_search.html', context)


class SavedSearchesView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
            
        return render(request, 'properties/saved_searches.html')


class BulkUpdatePropertiesView(View):
    def post(self, request):
        form = BulkUpdatePropertiesForm(request.POST)
        if form.is_valid():
            properties = form.cleaned_data['properties']
            status = form.cleaned_data['status']
            if status:
                properties.update(status=status)
        return redirect('properties:property_list')


import csv
import json
import pandas as pd
from django.http import HttpResponse
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError

class PropertyCompareView(View):
    def get(self, request):
        ids = request.GET.get('ids')
        export_format = request.GET.get('export')
        
        if ids:
            # Limit to maximum 4 properties for comparison
            property_ids = ids.split(',')
            if len(property_ids) > 4:
                messages.warning(request, 'Maximum 4 properties can be compared at once. Showing first 4 selected properties.')
                property_ids = property_ids[:4]
                
            properties = Property.objects.filter(pk__in=property_ids)
            
            # If export parameter is provided, export the comparison
            if export_format == 'excel' and properties.exists():
                return self.export_to_excel(properties)
        else:
            properties = []
            
        return render(request, 'properties/property_compare.html', {'properties': properties})
    
    def export_to_excel(self, properties):
        """Export property comparison data to Excel"""
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="property_comparison.xlsx"'
        
        # Create a pandas DataFrame with property data
        data = {
            'Property ID': [p.property_id for p in properties],
            'Address': [p.address for p in properties],
            'City': [p.city for p in properties],
            'Area': [p.area for p in properties],
            'Property Type': [p.property_type for p in properties],
            'Size (sqft)': [p.size_sqft for p in properties],
            'Rent Amount': [float(p.rent_amount) for p in properties],
            'Deposit Amount': [float(p.deposit_amount) for p in properties],
            'Status': [p.status for p in properties],
            'Furnished Type': [p.furnished_type for p in properties],
            'Amenities': [', '.join(p.amenities) if p.amenities else '' for p in properties]
        }
        
        # Create DataFrame and transpose it for better comparison view
        df = pd.DataFrame(data).T
        
        # Set column names to property addresses for better identification
        df.columns = [f'Property {i+1}: {p.address[:30]}' for i, p in enumerate(properties)]
        
        # Write to Excel
        df.to_excel(response)
        return response


class CSVImportExportView(View):
    def get(self, request):
        return render(request, 'properties/csv_import_export.html')

    def post(self, request):
        if 'import' in request.POST:
            file = request.FILES.get('import_file')
            if not file:
                messages.error(request, 'Please select a file to import.')
                return redirect('properties:property_csv_import_export')
            
            file_ext = file.name.split('.')[-1].lower()
            
            try:
                # Process based on file type
                if file_ext == 'csv':
                    df = pd.read_csv(file)
                elif file_ext in ['xlsx', 'xls']:
                    df = pd.read_excel(file)
                else:
                    messages.error(request, 'Unsupported file format. Please upload a CSV or Excel file.')
                    return redirect('properties:property_csv_import_export')
                
                # Convert DataFrame to dict records
                records = df.to_dict('records')
                
                # Validate required fields
                required_fields = ['property_id', 'address', 'city', 'area', 'property_type', 'size_sqft', 'rent_amount', 'deposit_amount', 'status', 'furnished_type']
                missing_fields = [field for field in required_fields if field not in df.columns]
                
                if missing_fields:
                    messages.error(request, f'Missing required fields: {", ".join(missing_fields)}')
                    return redirect('properties:property_csv_import_export')
                
                # Track import statistics
                stats = {
                    'created': 0,
                    'updated': 0,
                    'failed': 0,
                    'errors': []
                }
                
                # Use transaction to ensure data integrity
                with transaction.atomic():
                    for row in records:
                        try:
                            # Clean data
                            for field in row:
                                if pd.isna(row[field]):
                                    row[field] = None
                            
                            # Handle amenities as JSON
                            if 'amenities' in row and row['amenities']:
                                if isinstance(row['amenities'], str):
                                    try:
                                        # Try to parse as JSON if it's a string
                                        row['amenities'] = json.loads(row['amenities'])
                                    except json.JSONDecodeError:
                                        # If not valid JSON, treat as comma-separated list
                                        row['amenities'] = [item.strip() for item in row['amenities'].split(',')]
                            
                            # Update or create property
                            obj, created = Property.objects.update_or_create(
                                property_id=row['property_id'],
                                defaults={k: v for k, v in row.items() if k != 'property_id'}
                            )
                            
                            if created:
                                stats['created'] += 1
                            else:
                                stats['updated'] += 1
                                
                        except Exception as e:
                            stats['failed'] += 1
                            stats['errors'].append(f"Row with property_id '{row.get('property_id', 'unknown')}': {str(e)}")
                
                # Show success message with stats
                if stats['failed'] == 0:
                    messages.success(request, f"Successfully imported {stats['created']} new properties and updated {stats['updated']} existing properties.")
                else:
                    messages.warning(request, f"Imported {stats['created']} new properties and updated {stats['updated']} existing properties with {stats['failed']} failures.")
                    for error in stats['errors'][:5]:  # Show first 5 errors
                        messages.error(request, error)
                    if len(stats['errors']) > 5:
                        messages.error(request, f"... and {len(stats['errors']) - 5} more errors.")
                
                return redirect('properties:property_list')
                
            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
                return redirect('properties:property_csv_import_export')
                
        elif 'export' in request.POST:
            export_format = request.POST.get('export_format', 'csv')
            
            # Get all properties
            properties = Property.objects.all()
            
            # Create DataFrame
            data = [{
                'property_id': p.property_id,
                'address': p.address,
                'city': p.city,
                'area': p.area,
                'property_type': p.property_type,
                'size_sqft': p.size_sqft,
                'rent_amount': p.rent_amount,
                'deposit_amount': p.deposit_amount,
                'status': p.status,
                'furnished_type': p.furnished_type,
                'amenities': json.dumps(p.amenities) if p.amenities else None
            } for p in properties]
            
            df = pd.DataFrame(data)
            
            # Export based on format
            if export_format == 'excel':
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename="properties.xlsx"'
                df.to_excel(response, index=False)
                return response
            else:  # Default to CSV
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="properties.csv"'
                df.to_csv(response, index=False)
                return response
