from celery import shared_task
from django.utils import timezone
from .models import Subscription

@shared_task
def check_expired_subscriptions():
    """
    Runs periodically to deactivate expired users.
    """
    now = timezone.now()
    expired_subs = Subscription.objects.filter(end_date__lt=now, is_active=True)
    count = expired_subs.update(is_active=False)
    return f"Deactivated {count} expired subscriptions."