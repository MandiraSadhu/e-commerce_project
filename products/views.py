from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Product, UserProfile
from .serializers import CategorySerializer, ProductSerializer
from .permissions import IsAdminOrStaff, IsAdmin
# from .utils import encrypt_data, decrypt_data

from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, RedirectView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import UserRegistrationForm, UserLoginForm

from .utils import AESCipher
import os

class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'products/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print(form.errors) 
        return super().form_invalid(form)

class LoginView(FormView):
    form_class = UserLoginForm
    template_name = 'products/login.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class LogoutView(RedirectView):
    url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = ''

    def get_template_names(self):
        if self.request.user.role == 'admin':
            self.template_name = 'products/admin_dashboard.html'
        elif self.request.user.role == 'staff':
            self.template_name = 'products/staff_dashboard.html'
        elif self.request.user.role == 'agent':
            self.template_name = 'products/agent_dashboard.html'
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role == 'staff':
            context['products'] = Product.objects.filter(status='pending')
        elif self.request.user.role == 'agent':
            context['products'] = Product.objects.filter(created_by=self.request.user)
        return context


# Access the key from environment variable
AES_KEY = os.getenv('ENCRYPTION_KEY')

if not AES_KEY:
    raise ValueError("AES Encryption key not found in environment variables")
# print(AES_KEY)

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrStaff]

    def create(self, request, *args, **kwargs):
        cipher = AESCipher(AES_KEY)
        # Encrypt the name field before saving it
        if 'name' in request.data:
            request.data['name'] = cipher.encrypt(request.data['name'])
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        cipher = AESCipher(AES_KEY)
        for category in response.data:
            if 'name' in category:
                # Decrypt the name field before returning it
                category['name'] = cipher.decrypt(category['name'])
        return Response(response.data)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrStaff]

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        cipher = AESCipher(AES_KEY)
        if 'name' in response.data:
            response.data['name'] = cipher.decrypt(response.data['name'])
        return Response(response.data)

    def update(self, request, *args, **kwargs):
        cipher = AESCipher(AES_KEY)
        if 'name' in request.data:
            request.data['name'] = cipher.encrypt(request.data['name'])
        return super().update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.delete()


# Product Views
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrStaff]

    def create(self, request, *args, **kwargs):
        cipher = AESCipher(AES_KEY)
        if 'title' in request.data:
            request.data['title'] = cipher.encrypt(request.data['title'])
        if 'description' in request.data:
            request.data['description'] = cipher.encrypt(request.data['description'])
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        cipher = AESCipher(AES_KEY)
        for product in response.data:
            if 'title' in product:
                product['title'] = cipher.decrypt(product['title'])
            if 'description' in product:
                product['description'] = cipher.decrypt(product['description'])
        return Response(response.data)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrStaff]

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        cipher = AESCipher(AES_KEY)
        if 'title' in response.data:
            response.data['title'] = cipher.decrypt(response.data['title'])
        if 'description' in response.data:
            response.data['description'] = cipher.decrypt(response.data['description'])
        return Response(response.data)

    def update(self, request, *args, **kwargs):
        cipher = AESCipher(AES_KEY)
        if 'title' in request.data:
            request.data['title'] = cipher.encrypt(request.data['title'])
        if 'description' in request.data:
            request.data['description'] = cipher.encrypt(request.data['description'])
        return super().update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.delete()