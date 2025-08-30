# django_API_Pos

A Django-based API for Point of Sale (POS) systems.

## Overview

This project provides a backend API for POS applications, leveraging Django and Django REST Framework (DRF). It is designed to handle sales transactions, product management, customer data, and reporting functionalities needed in modern POS environments.

## Features

- **Sales Management**: Create, update, and track sales transactions.
- **Product Catalog**: Add, update, and organize products and categories.
- **Inventory Tracking**: Manage stock levels and receive notifications for low inventory.
- **Customer Management**: Register customers, track their purchases, and view analytics.
- **Authentication & Permissions**: Secure endpoints using JWT or token authentication.
- **RESTful API**: All resources are exposed via RESTful endpoints for easy integration.

## Technologies Used

- Python
- Django
- Django REST Framework
- SQLite (default, can be switched to PostgreSQL/MySQL)
- Docker (optional for containerization)

## Getting Started

Follow these steps to start the app locally:

1. **Clone the repository**
   ```bash
   git clone https://github.com/lycheang/django_API_Pos.git
   cd django_API_Pos
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional, for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the app**
   - API endpoints: [http://localhost:8000/api/](http://localhost:8000/api/)
   - Admin panel: [http://localhost:8000/admin/](http://localhost:8000/admin/)

## API Documentation

API endpoints are available under `/api/`. You can use tools like [Postman](https://www.postman.com/) or [Swagger UI](https://swagger.io/tools/swagger-ui/) to interact with the API.

- **Authentication**: `/api/auth/`
- **Products**: `/api/products/`
- **Sales**: `/api/sales/`
- **Customers**: `/api/customers/`

Refer to the codebase for serializers, views, and detailed endpoint information.


## License

This project is licensed under the MIT License.

## Contact

For issues, suggestions, or contributions, open a GitHub issue or contact [lycheang](https://github.com/lycheang).
