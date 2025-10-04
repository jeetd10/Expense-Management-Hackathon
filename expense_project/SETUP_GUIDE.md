# Expense Management System - Setup Guide

This project is a Python/Django API built for the hackathon, demonstrating multi-level and conditional expense approval workflows.

## Requirements

* Python 3.10+
* pip

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone [YOUR REPO URL HERE]
    cd expense_project
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(You must generate the `requirements.txt` file first - see Step 3 below.)*

3.  **Run Migrations:**
    ```bash
    python manage.py makemigrations expense_app
    python manage.py migrate
    ```

4.  **Create Admin User:**
    ```bash
    python manage.py createsuperuser
    # Use username: jeet
    ```

5.  **Run Server:**
    ```bash
    python manage.py runserver
    ```

## Post-Setup (Data Seeding)

Access the Django Admin at `http://127.0.0.1:8000/admin/` and log in with your Admin user (`jeet`). You must create the following data for the workflow to function:

1.  **Company:** Create one Company (`Acme Corp`) with a `default_currency` (e.g., USD).
2.  **Users:** Update `jeet` (Role: ADMIN) and create two new users:
    * **Manager:** `finance_mgr` (Role: MANAGER)
    * **Employee:** `Keval_ravani` (Role: EMPLOYEE), with `Manager` set to `finance_mgr`.
3.  **Approval Rule:** Create an `Approval Rule` for `Acme Corp`. Set `is_manager_first_approver` checked, `rule_type` to `SPECIFIC`, and `specific_approver_role` to `ADMIN` for the conditional approval feature.

## Testing the API

Use Insomnia/Postman with Basic Auth to test the workflow:

| Step | User | Method | URL | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Submission** | `Keval_ravani` | POST | `/api/expenses/submit/` | Use amount > 500 to trigger multi-level approval. |
| **Approval 1** | `finance_mgr` | PUT | `/api/expenses/approve/<ID>/` | Expense status remains PENDING. |
| **Approval 2** | `jeet` (Admin) | PUT | `/api/expenses/approve/<ID>/` | Expense status changes to APPROVED (due to Conditional Rule). |