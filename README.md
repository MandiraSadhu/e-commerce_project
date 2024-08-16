# E-Commerce Project

**Note:** The frontend for product and category CRUD operations is not implemented. You can test the APIs using tools like Postman.

## Features

- **Product CRUD**: Create, Read, Update, and Delete products.
- **Category CRUD**: Create, Read, Update, and Delete categories.
- **User Roles**: Admin, Staff, and End User roles with varying levels of access.
- **Token Authentication**: Secure endpoints with JWT authentication.
- **Background Tasks**: Use Celery and RabbitMQ to handle asynchronous tasks like generating dummy products.
- **CSV/Excel Export**: Export product data in CSV format.
- **Video Handling**: Manage video uploads with a size limit using Celery.

## Setup

### Prerequisites

- Python 3.8+
- Django 4.0+
- RabbitMQ
- Celery
- Django REST Framework
- JWT for authentication

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/MandiraSadhu/e-commerce_project
   cd e_commerce_project

2. **Create a Virtual Environment**

    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    
3. **Install Dependencies**

    pip install -r requirements.txt

4. **Set Up RabbitMQ**

    Ensure RabbitMQ is installed and running. The default configuration should work unless modified.

5. **Run Migrations**

    python manage.py migrate

6. **Run the Development Server**


    python manage.py runserver
    Start Celery Worker

        celery -A e_commerce_proj worker -l info