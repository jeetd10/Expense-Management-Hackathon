💰 Expense Management System - Odoo Hackathon Project
Project Overview
This is an API-first Expense Management System developed for the Odoo Hackathon. The goal was to replace time-consuming, manual reimbursement processes with a transparent, automated system that supports complex, multi-level approval workflows based on rules and thresholds.

The application is built using Python (Django/DRF) and features currency conversion via external APIs, multi-level sequential approval, and conditional auto-approval logic.

✨ Core Features Implemented
Authentication & Roles: Dedicated roles for Admin, Manager, and Employee.

Expense Submission: Employees can submit claims with amounts in different currencies.

Currency Conversion: Automatically converts claims to the company's default currency using external APIs.

Multi-Level Approval: Supports sequential, multi-step approval workflows (e.g., Manager → Admin).



Conditional Approval: Implements logic for conditional auto-approval (e.g., Specific Approver rule), overriding remaining workflow steps.


OCR Mockup: Includes a mock API endpoint to simulate automatic data extraction from receipt scans.

🛠️ Technology Stack
Backend: Python 3.10+

Framework: Django (5.x) & Django REST Framework (DRF)

Database: SQLite3 (default for development)

External APIs: exchangerate-api.com (Currency conversion) and restcountries.com (Country/Currency data).

🚀 Setup and Installation
Follow these steps to get the API running locally:

Clone the Repository:

Bash
git clone https://github.com/jeetd10/Expense-Management-Hackathon.git
cd Expense-Management-Hackathon/expense_project
Install Dependencies:

Bash
pip install -r requirements.txt
Run Migrations:

Bash
python manage.py makemigrations expense_app
python manage.py migrate
Create Admin User & Run Server:

Bash
python manage.py createsuperuser  # Create the 'jeet' Superuser
python manage.py runserver
The API will be available at http://127.0.0.1:8000/.

⚙️ Post-Setup and Testing
The application requires seed data (Company, Users, Rules) to function. Refer to the SETUP_GUIDE.md file for precise instructions on setting up the Admin, Manager, Employee, and the Conditional Approval Rule via the Django Admin interface.

Once setup is complete, use a client like Insomnia or Postman to test the workflow:

Feature	Method	Endpoint Example	Auth
Employee Submission	POST	/api/expenses/submit/	Employee (Keval_ravani)
Manager Approval	PUT	/api/expenses/approve/<ID>/	Manager (finance_mgr)
OCR Scan Mock	POST	/api/ocr/scan/	Any User