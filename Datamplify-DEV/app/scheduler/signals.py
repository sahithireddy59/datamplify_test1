from django.db.models.signals import post_save
from django.dispatch import receiver
from app.scheduler.models import Scheduler
from app.scheduler.services.publish import publish_scheduler

@receiver(post_save, sender=Scheduler)
def publish_on_save(sender, instance, **kwargs):
    publish_scheduler(instance)
