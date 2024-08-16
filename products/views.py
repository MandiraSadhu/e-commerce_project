from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import Category, Product, UserProfile
from .serializers import CategorySerializer, ProductSerializer, GenerateProductsSerializer
from .permissions import IsAdminOrStaff, IsAdmin
# from .utils import encrypt_data, decrypt_data

from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, RedirectView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import UserRegistrationForm, UserLoginForm
from django.contrib import messages

from .utils import AESCipher
import os

from .tasks import generate_dummy_products, process_video
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import csv
from rest_framework import pagination

class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'products/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Registration successful!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print(form.errors) 
        messages.error(self.request, 'Registration failed!')
        return self.render_to_response(self.get_context_data(form=form))

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
            messages.success(self.request, 'Login successful!')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Login failed. Please check your username and password.')
            return self.form_invalid(form)

class LogoutView(RedirectView):
    url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(self.request, 'You have been logged out.')
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

class GenerateProductsView(generics.GenericAPIView):
    serializer_class = GenerateProductsSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        categories_data = [{"id": category.id, "name": category.name} for category in categories]
        return Response({"categories": categories_data})

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            num_products = serializer.validated_data['num_products']
            generate_dummy_products.delay(num_products)
            return Response(
                {"message": f"Task to generate {num_products} products has been initiated."},
                status=status.HTTP_202_ACCEPTED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def upload_video(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        video_file = request.FILES.get('video')
        if video_file:
            # Save the uploaded file to the model
            product.video.save(video_file.name, video_file)
            
            # Enqueue the video processing task
            process_video.delay(product_id=product.id, video_file_path=product.video.path)
            
            return Response({"message": "Video upload successful, processing started."}, status=status.HTTP_202_ACCEPTED)
        return Response({"error": "No video file provided."}, status=status.HTTP_400_BAD_REQUEST)
    

class ProductPagination(pagination.PageNumberPagination):
    page_size = 1000  

class ExportProductsCSV(generics.GenericAPIView):
    permission_classes = [IsAdmin]
    pagination_class = ProductPagination

    def get(self, request, *args, **kwargs):
        paginator = self.pagination_class()
        products = Product.objects.all()
        paginated_products = paginator.paginate_queryset(products, request)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Category', 'Title', 'Description', 'Price', 'Status', 'Created At', 'Updated At'])
        for product in paginated_products:
            writer.writerow([
                product.id,
                product.category.name,
                product.title,
                product.description,
                product.price,
                product.status,
                product.created_at,
                product.updated_at
            ])
        return response