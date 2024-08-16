from rest_framework import serializers
from .models import Product, Category


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
        
        
        
        return product

    def update(self, instance, validated_data):
        product = super().update(instance, validated_data)
        
        
        
        return product
