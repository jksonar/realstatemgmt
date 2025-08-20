from django.views import generic as django_generic
from .models import Property
from .filters import PropertyFilter

from .forms import PropertyForm, BulkUpdatePropertiesForm
from django.shortcuts import render, redirect
from django.views import View

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
from django.http import HttpResponse

class PropertyCompareView(View):
    def get(self, request):
        ids = request.GET.get('ids')
        if ids:
            properties = Property.objects.filter(pk__in=ids.split(','))
        else:
            properties = []
        return render(request, 'properties/property_compare.html', {'properties': properties})


class CSVImportExportView(View):
    def get(self, request):
        return render(request, 'properties/csv_import_export.html')

    def post(self, request):
        if 'import' in request.POST:
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                Property.objects.update_or_create(
                    property_id=row['property_id'],
                    defaults=row
                )
            return redirect('properties:property_list')
        elif 'export' in request.POST:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="properties.csv"'

            writer = csv.writer(response)
            writer.writerow(['property_id', 'address', 'city', 'area', 'property_type', 'size_sqft', 'rent_amount', 'deposit_amount', 'status', 'furnished_type', 'amenities'])

            for property in Property.objects.all():
                writer.writerow([property.property_id, property.address, property.city, property.area, property.property_type, property.size_sqft, property.rent_amount, property.deposit_amount, property.status, property.furnished_type, property.amenities])

            return response
