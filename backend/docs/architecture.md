# 🏗 System Architecture Documentation

## 1. High-Level Overview

The **ISP & WiFi Billing System** follows a **Headless / Decoupled Architecture**. The backend (Django) acts as a standalone REST API provider, while the frontend (React) consumes these APIs to render the user interface.

This separation allows for:
- Scalability (Backend and Frontend can be hosted on separate servers).
- Flexibility (Mobile apps can consume the same API later).
- Security (Database is completely hidden from the client).

### System Diagram
The system is composed of three main layers:

1.  **Client Layer**: React Admin Dashboard & User Portal.
2.  **Service Layer**: Django API, Authentication, and Payment Logic.
3.  **Data Layer**: PostgreSQL (Persistent Data) & Redis (Caching/Tasks).



---

## 2. Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | **Django 5.0 + DRF** | Core business logic, ORM, and API endpoints. |
| **Frontend Framework** | **React.js + Tailwind** | User Interface for Admin and Customers. |
| **Database** | **PostgreSQL** | Relational data storage (Users, Payments, Plans). |
| **Authentication** | **JWT (SimpleJWT)** | Stateless security tokens for API access. |
| **Task Queue** | **Celery + Redis** | Background tasks (e.g., auto-disconnecting expired users). |
| **Payments** | **Safaricom Daraja API** | Handling M-Pesa STK Pushes and Callbacks. |
| **Web Server** | **Gunicorn / Nginx** | Production serving and reverse proxy. |

---

## 3. Core Data Flows

### A. Authentication Flow (JWT)
We use JSON Web Tokens (JWT) to secure the API.

1.  **Login**: User sends `username` + `password` to `/api/auth/login/`.
2.  **Token Generation**: If credentials are valid, Server returns an `access` token (short-lived) and `refresh` token (long-lived).
3.  **Authorized Requests**: Frontend attaches the `access` token to the HTTP Header (`Authorization: Bearer <token>`) for every request (e.g., fetching users).
4.  **Token Refresh**: When the access token expires, Frontend uses the `refresh` token to get a new one without logging the user out.

### B. M-Pesa Payment Flow (STK Push)
This is the most critical business logic flow.



1.  **Initiation**: User selects a package and enters their phone number in the Frontend.
2.  **API Call**: Frontend hits `POST /api/payments/initiate/`.
3.  **Daraja Request**: Django connects to Safaricom's API using the Consumer Key/Secret.
4.  **User Action**: A popup appears on the user's phone asking for MPIN.
5.  **Pending State**: Django records a `Payment` with status `PENDING`.
6.  **Callback (Webhook)**:
    * Safaricom processes the transaction.
    * Safaricom sends a JSON `POST` request to our `MPESA_CALLBACK_URL`.
7.  **Processing**:
    * Django validates the callback.
    * If successful, `Payment` status updates to `COMPLETED`.
    * **Signal Trigger**: A Django Signal creates/activates a `Subscription` for the user.

---

## 4. Database Schema Design (ERD)

The database is normalized to ensure data integrity.

* **CustomUser**: Extends Django Auth. Stores `role` (Admin/Customer) and `phone_number`.
* **WifiPackage**: Defines the product catalog (Speed, Price, Duration).
* **Subscription**: The "link" table. Links a `User` to a `WifiPackage` with `start_date` and `end_date`.
* **Payment**: Stores transaction logs, M-Pesa Receipt numbers, and raw JSON logs from callbacks.

---

## 5. Background Tasks (Automation)

To ensure users are disconnected exactly when their plan expires, we do not rely on a human checking dates.

**Tool:** Celery + Redis

1.  **Task**: `check_expired_subscriptions()`
2.  **Frequency**: Runs every hour (configured in `celery.py` beat schedule).
3.  **Logic**:
    ```sql
    UPDATE billing_subscription
    SET is_active = False
    WHERE end_date < NOW() AND is_active = True;
    ```
4.  **Outcome**: The user is marked inactive in the DB. (Future integration: Use Mikrotik API to cut off actual internet access).

---

## 6. Directory Structure

```text
wifi_billing_system/
├── backend/                # Django Project
│   ├── config/             # Settings & URLs
│   ├── users/              # Auth & Roles
│   ├── plans/              # WiFi Packages
│   ├── billing/            # Payments & Subscriptions
│   ├── mpesa/              # Daraja API Integration
│   └── dashboard/          # Admin Stats API
├── frontend/               # React Project
│   ├── src/
│   │   ├── components/     # Reusable UI (Cards, Tables)
│   │   ├── pages/          # Full Screens
│   │   └── services/       # API Connectors (Axios)
└── docs/                   # Documentation