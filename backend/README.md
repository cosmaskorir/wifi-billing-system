# 📡 ISP & WiFi Billing Management System

A full-stack ISP management solution designed to automate user subscriptions, billing, and WiFi package management. The system features a **Django REST Framework** backend, **React** frontend, and fully integrated **M-Pesa (Daraja API)** payments with STK Push functionality.

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0-green.svg)
![React](https://img.shields.io/badge/React-18-blue)

---

## 🚀 Features

- **User Management**: Register customers, technicians, and cashiers with Role-Based Access Control (RBAC).
- **Package Management**: Create and manage WiFi plans (e.g., 5Mbps, 10Mbps) with specific billing cycles (Daily, Weekly, Monthly).
- **Automated Billing**:
  - Auto-generate invoices.
  - **M-Pesa Integration**: Automatic STK Push requests to customer phones.
  - Payment tracking and receipt generation.
- **Subscription Control**: Auto-disconnect users when subscriptions expire (via Celery/Redis).
- **Admin Dashboard**: Real-time visualization of revenue, active users, and pending payments.
- **Reporting**: Export financial reports to PDF/Excel.

---

## 🛠 Tech Stack

### Backend
- **Framework**: Django & Django REST Framework (DRF)
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Task Queue**: Celery & Redis (for background tasks like expiration checks)
- **Payment Gateway**: Safaricom Daraja API

### Frontend
- **Framework**: React.js
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js & npm
- PostgreSQL
- Redis Server

### 1. Backend Setup (Django)

```bash
# Clone the repository
git clone [https://github.com/your-username/wifi-billing-system.git](https://github.com/your-username/wifi-billing-system.git)
cd wifi-billing-system/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Environment Variables
# (Create a .env file in backend/config/ based on the example below)

# Run Migrations
python manage.py makemigrations
python manage.py migrate

# Create Admin User
python manage.py createsuperuser

# Start the Server
python manage.py runserver