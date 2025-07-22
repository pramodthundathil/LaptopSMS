from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification, Service

@receiver(post_save, sender=Service)
def create_service_notification(sender, instance, created, **kwargs):
    if created and instance.serviceTechnician:
        # Create notification for the assigned technician
        Notification.objects.create(
            user=instance.serviceTechnician.user,
            title="New Service Assignment",
            message=f"You have been assigned to service {instance.service_id} for {instance.product.brand} {instance.product.model}. Serial No: {instance.product.serialNo}",
            service=instance
        )
    elif not created:
        # Handle case when technician is changed
        if instance.serviceTechnician:
            # Check if this is a new assignment (you might want to add more logic here)
            existing_notifications = Notification.objects.filter(
                service=instance,
                user=instance.serviceTechnician.user,
                is_read=False
            )
            if not existing_notifications.exists():
                Notification.objects.create(
                    user=instance.serviceTechnician.user,
                    title="Service Assignment Updated",
                    message=f"Service {instance.service_id} has been assigned to you. Product: {instance.product.brand} {instance.product.model}",
                    service=instance
                )