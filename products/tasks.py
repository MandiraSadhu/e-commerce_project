from celery import shared_task
from .models import Product, Category
import os
import random
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_dummy_products(num_products):
    logger.info(f"Starting to generate {num_products} dummy products.")
    category_ids = Category.objects.values_list('id', flat=True)
    if not category_ids:
        logger.error("No categories found.")
        return
    
    for i in range(num_products):
        Product.objects.create(
            category_id=random.choice(category_ids),
            title=f"Dummy Product {i}",
            description="This is a dummy product.",
            price=random.uniform(5.00, 100.00),
            status="available"
        )
    logger.info(f"Finished generating {num_products} dummy products.")


@shared_task
def process_video(product_id, video_file_path):
    try:
        # Get the product instance
        product = Product.objects.get(id=product_id)

        # Check file size (20 MB limit)
        file_size = os.path.getsize(video_file_path)
        if file_size > 20 * 1024 * 1024:  # 20 MB
            product.video_status = 'failed'
            product.save()
            return 'File size exceeds 20 MB limit.'

        # Set video status to processing
        product.video_status = 'processing'
        product.save()

        # Process the video (e.g., encoding, compressing)
        # Simulating processing with a sleep
        import time
        for progress in range(0, 101, 10):  # Simulate progress from 0% to 100%
            time.sleep(1)  # Simulating processing delay
            product.video_progress = progress
            product.save()

        # Set video status to completed
        product.video_status = 'completed'
        product.video_progress = 100
        product.save()

        return 'Video processing completed successfully.'

    except Product.DoesNotExist:
        return 'Product not found.'

