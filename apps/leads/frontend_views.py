from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Count, Avg, F, ExpressionWrapper, fields, Q
from django.db.models.functions import TruncDate
from datetime import timedelta, datetime

from .models import Lead, LeadSource, LeadActivity
from .forms import LeadForm, LeadSourceForm, LeadActivityForm


class LeadReportView(LoginRequiredMixin, TemplateView):
    template_name = 'leads/lead_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from request or default to last 30 days
        end_date = timezone.now().date()
        start_date = self.request.GET.get('start_date')
        end_date_param = self.request.GET.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = end_date - timedelta(days=30)
            
        if end_date_param:
            end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
        
        # Get leads created in the date range
        leads_in_period = Lead.objects.filter(inquiry_date__gte=start_date, inquiry_date__lte=end_date)
        
        # Lead source distribution
        source_distribution = leads_in_period.values('source__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Lead status distribution
        status_distribution = leads_in_period.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Conversion rate
        total_leads = leads_in_period.count()
        converted_leads = leads_in_period.filter(status='converted').count()
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
        
        # Daily lead creation trend
        daily_leads = leads_in_period.annotate(
            date=TruncDate('inquiry_date')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Average time to conversion
        converted_with_dates = leads_in_period.filter(
            status='converted',
            converted_date__isnull=False
        )
        
        if converted_with_dates.exists():
            conversion_time = ExpressionWrapper(
                F('converted_date') - F('inquiry_date'),
                output_field=fields.DurationField()
            )
            avg_days_to_convert = converted_with_dates.annotate(
                conversion_time=conversion_time
            ).aggregate(avg=Avg('conversion_time'))['avg']
            avg_days_to_convert = avg_days_to_convert.days if avg_days_to_convert else 0
        else:
            avg_days_to_convert = 0
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'total_leads': total_leads,
            'converted_leads': converted_leads,
            'conversion_rate': round(conversion_rate, 2),
            'source_distribution': source_distribution,
            'status_distribution': status_distribution,
            'daily_leads': daily_leads,
            'avg_days_to_convert': avg_days_to_convert,
        })
        
        return context


class LeadListView(LoginRequiredMixin, ListView):
    model = Lead
    template_name = 'leads/lead_list.html'
    context_object_name = 'leads'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Lead.objects.all()
        
        # Apply filters
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        source = self.request.GET.get('source')
        priority = self.request.GET.get('priority')
        budget_range = self.request.GET.get('budget_range')
        
        if search:
            queryset = queryset.filter(
                first_name__icontains=search) | queryset.filter(
                last_name__icontains=search) | queryset.filter(
                email__icontains=search) | queryset.filter(
                phone__icontains=search) | queryset.filter(
                notes__icontains=search
            )
        
        if status:
            queryset = queryset.filter(status=status)
            
        if source:
            queryset = queryset.filter(source_id=source)
            
        if priority:
            queryset = queryset.filter(priority=priority)
            
        if budget_range:
            queryset = queryset.filter(budget_range=budget_range)
            
        return queryset.order_by('-inquiry_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lead_sources'] = LeadSource.objects.all()
        return context


class LeadDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    template_name = 'leads/lead_detail.html'
    context_object_name = 'lead'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lead = self.get_object()
        
        # Get all activities for this lead
        activities = LeadActivity.objects.filter(lead=lead).order_by('-activity_date')
        
        # Get notes (activities of type 'note')
        notes = activities.filter(activity_type='note')
        
        context['activities'] = activities
        context['notes'] = notes
        return context


class LeadCreateView(LoginRequiredMixin, CreateView):
    model = Lead
    template_name = 'leads/lead_form.html'
    form_class = LeadForm
    
    def get_success_url(self):
        return reverse_lazy('leads:lead-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # Set the inquiry date to today if not provided
        if not form.cleaned_data.get('inquiry_date'):
            form.instance.inquiry_date = timezone.now().date()
        
        # Create the lead
        response = super().form_valid(form)
        
        # Create an activity for the lead creation
        LeadActivity.objects.create(
            lead=self.object,
            activity_type='note',
            description=f"Lead created",
            performed_by=self.request.user,
            activity_date=timezone.now()
        )
        
        messages.success(self.request, 'Lead created successfully.')
        return response


class LeadUpdateView(LoginRequiredMixin, UpdateView):
    model = Lead
    template_name = 'leads/lead_form.html'
    form_class = LeadForm
    
    def get_success_url(self):
        return reverse_lazy('leads:lead-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # Check if status has changed
        if self.object.status != form.cleaned_data.get('status'):
            old_status = self.object.get_status_display()
            new_status = dict(Lead.LEAD_STATUS_CHOICES)[form.cleaned_data.get('status')]
            
            # Create an activity for the status change
            LeadActivity.objects.create(
                lead=self.object,
                activity_type='note',
                description=f"Status changed from {old_status} to {new_status}",
                performed_by=self.request.user,
                activity_date=timezone.now()
            )
            
            # If converting the lead, set the converted_date
            if form.cleaned_data.get('status') == 'converted' and self.object.status != 'converted':
                form.instance.converted_date = timezone.now()
        
        response = super().form_valid(form)
        messages.success(self.request, 'Lead updated successfully.')
        return response


class LeadDeleteView(LoginRequiredMixin, DeleteView):
    model = Lead
    template_name = 'leads/lead_confirm_delete.html'
    success_url = reverse_lazy('leads_frontend:lead-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Lead deleted successfully.')
        return super().delete(request, *args, **kwargs)


class LeadSourceListView(LoginRequiredMixin, ListView):
    model = LeadSource
    template_name = 'leads/lead_source_list.html'
    context_object_name = 'sources'
    
    def get_queryset(self):
        # Annotate each source with the count of leads
        return LeadSource.objects.annotate(lead_count=Count('leads'))


def add_lead_activity(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    if request.method == 'POST':
        form = LeadActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.lead = lead
            activity.performed_by = request.user
            activity.save()
            
            # Update the lead's last_contact_date
            lead.last_contact_date = timezone.now()
            lead.save(update_fields=['last_contact_date'])
            
            messages.success(request, 'Activity added successfully.')
            return redirect('leads_frontend:lead-detail', pk=lead.pk)
    
    return redirect('leads_frontend:lead-detail', pk=lead.pk)


def add_lead_note(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    if request.method == 'POST':
        description = request.POST.get('description')
        if description:
            LeadActivity.objects.create(
                lead=lead,
                activity_type='note',
                description=description,
                performed_by=request.user,
                activity_date=timezone.now()
            )
            messages.success(request, 'Note added successfully.')
    
    return redirect('leads_frontend:lead-detail', pk=lead.pk)


def schedule_follow_up(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    if request.method == 'POST':
        next_follow_up = request.POST.get('next_follow_up')
        description = request.POST.get('description', '')
        
        if next_follow_up:
            lead.next_follow_up = next_follow_up
            lead.save(update_fields=['next_follow_up'])
            
            # Create an activity for the follow-up scheduling
            LeadActivity.objects.create(
                lead=lead,
                activity_type='task',
                description=f"Follow-up scheduled for {next_follow_up}" + (f": {description}" if description else ""),
                performed_by=request.user,
                activity_date=timezone.now()
            )
            
            messages.success(request, 'Follow-up scheduled successfully.')
    
    return redirect('leads_frontend:lead-detail', pk=lead.pk)


def update_lead_status(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status and new_status in dict(Lead.LEAD_STATUS_CHOICES).keys():
            old_status = lead.get_status_display()
            
            # If converting the lead, set the converted_date
            if new_status == 'converted' and lead.status != 'converted':
                lead.converted_date = timezone.now()
            
            lead.status = new_status
            lead.save()
            
            # Create an activity for the status change
            description = f"Status changed from {old_status} to {dict(Lead.LEAD_STATUS_CHOICES)[new_status]}"
            if notes:
                description += f": {notes}"
                
            LeadActivity.objects.create(
                lead=lead,
                activity_type='note',
                description=description,
                performed_by=request.user,
                activity_date=timezone.now()
            )
            
            messages.success(request, 'Lead status updated successfully.')
    
    return redirect('leads_frontend:lead-detail', pk=lead.pk)


def create_lead_source(request):
    if request.method == 'POST':
        form = LeadSourceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lead source created successfully.')
    
    return redirect('leads_frontend:lead-source-list')


def update_lead_source(request, pk):
    source = get_object_or_404(LeadSource, pk=pk)
    
    if request.method == 'POST':
        form = LeadSourceForm(request.POST, instance=source)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lead source updated successfully.')
    
    return redirect('leads_frontend:lead-source-list')


class LeadSourceDeleteView(LoginRequiredMixin, DeleteView):
    model = LeadSource
    template_name = 'leads/lead_source_confirm_delete.html'
    success_url = reverse_lazy('leads_frontend:lead-source-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add lead count to context to show warning if leads are associated
        context['lead_count'] = Lead.objects.filter(source=self.object).count()
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Lead source deleted successfully.')
        return super().delete(request, *args, **kwargs)


def delete_lead_source(request, pk):
    source = get_object_or_404(LeadSource, pk=pk)
    
    if request.method == 'POST':
        source.delete()
        messages.success(request, 'Lead source deleted successfully.')
    
    return redirect('leads_frontend:lead-source-list')


def export_leads(request):
    import csv
    from django.http import HttpResponse
    from django.shortcuts import render
    
    # If this is not a direct download request, show the export options form
    if not any([request.GET.get('status'), request.GET.get('source'), 
                request.GET.get('start_date'), request.GET.get('end_date'),
                request.GET.get('search')]):
        sources = LeadSource.objects.all()
        return render(request, 'leads/lead_export.html', {'sources': sources})
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="leads_export.csv"'
    
    # Get filtered queryset if filters are applied
    leads = Lead.objects.all()
    if request.GET.get('search'):
        search_term = request.GET.get('search')
        leads = leads.filter(
            Q(first_name__icontains=search_term) | 
            Q(last_name__icontains=search_term) | 
            Q(email__icontains=search_term) | 
            Q(phone__icontains=search_term)
        )
    
    if request.GET.get('status'):
        leads = leads.filter(status=request.GET.get('status'))
        
    if request.GET.get('source'):
        leads = leads.filter(source_id=request.GET.get('source'))
        
    if request.GET.get('start_date'):
        try:
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
            leads = leads.filter(inquiry_date__gte=start_date)
        except ValueError:
            pass
            
    if request.GET.get('end_date'):
        try:
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
            leads = leads.filter(inquiry_date__lte=end_date)
        except ValueError:
            pass
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow([
        'First Name', 'Last Name', 'Email', 'Phone', 'Status', 
        'Source', 'Score', 'Inquiry Date', 'Next Follow-up', 'Property', 'Notes'
    ])
    
    # Write data rows
    for lead in leads:
        writer.writerow([
            lead.first_name,
            lead.last_name,
            lead.email,
            lead.phone,
            lead.get_status_display(),
            lead.source.name if lead.source else '',
            lead.score,
            lead.inquiry_date.strftime('%Y-%m-%d') if lead.inquiry_date else '',
            lead.next_follow_up.strftime('%Y-%m-%d') if lead.next_follow_up else '',
            lead.related_property.title if lead.related_property else '',
            lead.notes
        ])
    
    messages.success(request, f'{leads.count()} leads exported successfully.')
    return response


def import_leads(request):
    from django.shortcuts import render
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        import csv
        from io import TextIOWrapper
        
        csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
        reader = csv.DictReader(csv_file)
        
        success_count = 0
        error_count = 0
        errors = []
        
        for row in reader:
            try:
                # Get or create lead source
                source_name = row.get('Source', '').strip()
                source = None
                if source_name:
                    source, _ = LeadSource.objects.get_or_create(name=source_name)
                
                # Create lead
                lead = Lead(
                    first_name=row.get('First Name', '').strip(),
                    last_name=row.get('Last Name', '').strip(),
                    email=row.get('Email', '').strip(),
                    phone=row.get('Phone', '').strip(),
                    source=source,
                    notes=row.get('Notes', '').strip()
                )
                
                # Set status if valid
                status_display = row.get('Status', '').strip()
                for status_code, status_name in Lead.LEAD_STATUS_CHOICES:
                    if status_name == status_display:
                        lead.status = status_code
                        break
                
                # Set dates if provided
                inquiry_date = row.get('Inquiry Date', '').strip()
                if inquiry_date:
                    try:
                        lead.inquiry_date = datetime.strptime(inquiry_date, '%Y-%m-%d')
                    except ValueError:
                        pass
                
                next_follow_up = row.get('Next Follow-up', '').strip()
                if next_follow_up:
                    try:
                        lead.next_follow_up = datetime.strptime(next_follow_up, '%Y-%m-%d')
                    except ValueError:
                        pass
                
                lead.save()
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"Row {reader.line_num}: {str(e)}")
        
        if success_count > 0:
            messages.success(request, f'{success_count} leads imported successfully.')
        
        if error_count > 0:
            messages.error(request, f'{error_count} leads failed to import. See details below.')
            for error in errors[:10]:  # Show first 10 errors
                messages.error(request, error)
            
            if len(errors) > 10:
                messages.error(request, f'... and {len(errors) - 10} more errors.')
        
        return redirect('leads_frontend:lead-list')
    
    return render(request, 'leads/lead_import.html')