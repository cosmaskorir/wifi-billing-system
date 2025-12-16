from rest_framework import serializers
from .models import Ticket, TicketUpdate # Import both models

# 1. Serializer for the history/progress updates
class TicketUpdateSerializer(serializers.ModelSerializer):
    # This reads the username from the User model linked by updated_by
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = TicketUpdate
        fields = ['note', 'is_public', 'created_at', 'updated_by_username']
        # Note: 'updated_by' is handled by the admin form/logic

# 2. Main Ticket Serializer
class TicketSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    # NEW: Include the list of TicketUpdates (history)
    # The 'updates' name comes from the related_name='updates' on the ForeignKey in models.py
    updates = TicketUpdateSerializer(many=True, read_only=True) 

    class Meta:
        model = Ticket
        fields = [
            'id', 'subject', 'category', 'category_display', 
            'description', 'priority', 'status', 'status_display', 
            'created_at', 'admin_response', 'updates' # Include 'updates'
        ]
        read_only_fields = ['status', 'admin_response', 'updates']