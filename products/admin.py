from django.contrib import admin
from .models import UserProfile, Product, Category

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Product)
admin.site.register(Category)