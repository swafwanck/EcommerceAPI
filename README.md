Ecommerce API

Overview

This project is an eCommerce API built with Django REST Framework. It supports role-based access control for different user types, including Vendors and Customers. Users can manage products, user accounts, and carts through various API endpoints.

API Endpoints

User Management

•	Endpoint: http://127.0.0.1:8000/api/shop/
•	Methods: GET, POST, PUT, DELETE
•	Description: Manage user accounts. Supports creating, updating, deleting, and viewing users. Users can have either a Vendor or Customer role.

Authentication

•	Endpoint: http://127.0.0.1:8000/api/login/
•	Methods: POST
•	Description: User login endpoint that provides JWT access and refresh tokens. Use this to authenticate users and manage sessions.

Product Management

•	Endpoint: http://127.0.0.1:8000/api/products/
•	Methods: GET, POST, PUT, DELETE
•	Description: Manage products in the eCommerce system. Only users with the Vendor role can create, update, or delete products. All authenticated users can view products.

Cart Management

•	Endpoint: http://127.0.0.1:8000/api/carts/
•	Methods: GET, POST, PUT, DELETE
•	Description: Manage products in the cart. Only users with the Customer role can create, update, or delete items in their cart. Vendors cannot modify the cart.

Role-Based Access Control

•	Vendor Role: Can create, update, and delete products. Can view user information but cannot modify carts.
•	Customer Role: Can add, update, and remove items from the cart. Cannot create, update, or delete products.

Setup Instructions

1.	Clone the Repository:
   
        git clone https://github.com/swafwanck/EcommerceAPI.git
        cd EcommerceAPI
  	
2.	Create a Virtual Environment:
           
         python -m venv venv
         venv/Scripts/activat.bat

3.	Install Dependencies: 

          pip install -r requirements.txt

4.	Apply Migrations:
	
         python manage.py makemigrations
         python manage.py migrate
  	
5.	Run the Development Server:
           
           python manage.py runserver
	

6.	Access the API:
   
         Visit http://127.0.0.1:8000 in your browser or use an API client like Postman to interact with the endpoints.

Testing

    To run tests, use the following command:
        python manage.py test
        
Assumptions and Decisions

    JWT authentication is used to handle user sessions and secure API access.
    Role-based permissions are enforced using Django REST Framework's permissions classes.
    Users are categorized into Vendor and Customer roles with specific permissions for each.
