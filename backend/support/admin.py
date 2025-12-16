from django.contrib import admin
from .models import Ticket, TicketUpdate 

# 1. Define the Inline form for updates
class TicketUpdateInline(admin.TabularInline):
    model = TicketUpdate
    extra = 1 
    fields = ('note', 'is_public', 'updated_by') # Removed created_at from here as it is auto-set
    readonly_fields = ('created_at',)
    
    # Pre-populate the 'updated_by' field with the current Admin user
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if hasattr(formset.form.base_fields['updated_by'], 'initial'):
             formset.form.base_fields['updated_by'].initial = request.user.pk
        return formset


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'subject', 
        'user', 
        'category', 
        'status', 
        'priority', 
        'created_at',
    )
    
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('subject', 'description', 'user__username', 'admin_response')
    list_editable = ('status', 'priority')

    inlines = [
        TicketUpdateInline,
    ]
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'subject', 'category', 'priority', 'created_at'),
            'description': 'Details provided by the customer.'
        }),
        ('Issue Details', {
            'fields': ('description',),
            'description': 'The full description of the problem.'
        }),
        ('Final Resolution', {
            'fields': ('status', 'admin_response'),
            'description': 'Set FINAL status and send a summary response to the customer. Use the updates log below for progress notes.'
        }),
    )
    
    readonly_fields = ('user', 'created_at')