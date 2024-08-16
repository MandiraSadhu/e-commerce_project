from rest_framework import serializers
from .models import Product, Category
from .tasks import process_video

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        product = super().create(validated_data)
        
        # Enqueue the video processing task if a video is uploaded
        if product.video:
            process_video.delay(product_id=product.id, video_file_path=product.video.path)
        
        return product

    def update(self, instance, validated_data):
        product = super().update(instance, validated_data)
        
         # Enqueue the video processing task if a new video is uploaded
        if 'video' in validated_data and validated_data['video']:
            process_video.delay(product_id=product.id, video_file_path=product.video.path)
        
        return product

class GenerateProductsSerializer(serializers.Serializer):
    num_products = serializers.IntegerField()
