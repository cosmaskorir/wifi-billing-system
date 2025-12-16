from rest_framework import viewsets, permissions
from .models import Ticket
from .serializers import TicketSerializer

class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users only see THEIR own tickets
        return Ticket.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        # Auto-assign the logged-in user to the ticket
        serializer.save(user=self.request.user)