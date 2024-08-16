from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from .tasks import process_video

@receiver(post_save, sender=Product)
def trigger_video_processing(sender, instance, **kwargs):
    if instance.video and instance.video_status == 'pending':
        process_video.delay(product_id=instance.id, video_file_path=instance.video.path)