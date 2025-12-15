from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Sends an email with the token when a user requests a password reset.
    """
    # In a real app, send a link like: https://www.yourdomain.com/reset-password?token=...
    # For now, we just send the token code.
    
    email_plaintext_message = f"""
    Hi {reset_password_token.user.username},

    You requested a password reset for your ISP account.
    
    Here is your Reset Token: {reset_password_token.key}

    (If you did not request this, please ignore this email.)
    """

    send_mail(
        # Title:
        "Password Reset for {title}".format(title="ISP Portal"),
        # Message:
        email_plaintext_message,
        # From:
        "noreply@isp-portal.com",
        # To:
        [reset_password_token.user.email]
    )