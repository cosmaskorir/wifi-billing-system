from django.db import models
from django.conf import settings

# --- TICKET MODEL ---
class Ticket(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    )

    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    )

    CATEGORY_CHOICES = (
        ('INTERNET', 'No Internet / Slow Speed'),
        ('BILLING', 'Billing Issue'),
        ('RELOCATION', 'Relocation Request'),
        ('OTHER', 'Other'),
    )

    # Fields that were missing and causing the errors
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='INTERNET')
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_response = models.TextField(blank=True, null=True, help_text="Reply visible to the user")

    def __str__(self):
        return f"[{self.status}] {self.subject} ({self.user.username})"

# --- TICKETUPDATE MODEL ---
class TicketUpdate(models.Model):
    """Stores progress updates, internal notes, or comments on a ticket."""
    
    TICKET_ACTION_CHOICES = (
        ('COMMENT', 'Comment'),
        ('STATUS_CHANGE', 'Status Change'),
        ('ASSIGNMENT', 'Assignment'),
    )

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='updates')
    # Who created the update (Admin user)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='ticket_updates')
    
    # The actual content of the progress note
    note = models.TextField()
    
    # Whether the customer should see this note (Admin control)
    is_public = models.BooleanField(default=True, help_text="Check to make this update visible to the customer on the portal.")
    
    # Optional field to log the type of action
    action = models.CharField(max_length=20, choices=TICKET_ACTION_CHOICES, default='COMMENT')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        visibility = 'PUBLIC' if self.is_public else 'PRIVATE'
        return f"Update on Ticket {self.ticket.id} by {self.updated_by}: {visibility}"

    class Meta:
        ordering = ['created_at']