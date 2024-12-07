from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from .models import Booking  # Import your Booking model here
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

@receiver(post_save, sender=Booking)
def send_approval_notification(sender, instance, created, **kwargs):
    if not created:
        booking_user = instance.User
        booking_id = instance.BookingID
        status = instance.Status

        if status == 'approved':
            subject = 'Booking Approved'

            message = render_to_string('booking_approved.html', {
                'booking_id': booking_id,
                'status': status,
                'user_name': booking_user.Name,
                'email': booking_user.Email,
            })


            print(f"Sending approval notification for booking ID: {booking_id} to {booking_user.Email}")
            print(f"Subject: {subject}")
            print(f"Message: {message}")


            send_mail(subject, message, settings.EMAIL_HOST_USER, [booking_user.Email])

        elif status == 'rejected':
            subject = 'Booking Rejected'

            message = render_to_string('booking_rejected.html', {
                'booking_id': booking_id,
                'status': status,
                'user_name': booking_user.Name,
                'email': booking_user.Email,
            })


            print(f"Sending rejection notification for booking ID: {booking_id} to {booking_user.Email}")
            print(f"Subject: {subject}")
            print(f"Message: {message}")

            email = EmailMultiAlternatives(subject, '', settings.EMAIL_HOST_USER, [booking_user.Email])
            email.attach_alternative(message, "text/html")
            email.send()
