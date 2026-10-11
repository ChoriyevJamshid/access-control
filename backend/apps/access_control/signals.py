from django.dispatch import receiver
from django.db.models.signals import post_save

from apps.access_control import tasks
from apps.access_control.models import AccessEvent


@receiver(post_save, sender=AccessEvent)
def on_create_access_event(sender, instance, created, **kwargs):
    if created:
        tasks.processing_work_session.delay(access_event_id=instance.id)
