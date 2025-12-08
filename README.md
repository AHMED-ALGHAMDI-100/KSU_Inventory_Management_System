# KSU Inventory Management System

## 🌟 Project Overview

This project implements a three-tier Inventory Management System using **Python (CustomTkinter)** for the user interface and **PostgreSQL** for the database. The system enables KSU Colleges to request items (Chairs, Desks, PCs, Printers, TVs, etc.) from a central KSU Inventory. It manages three user roles: **College User**, **Courier**, and **Inventory Manager** (Admin).

### Key Features
* **Secure Authentication:** User registration and login utilize password hashing (using `bcrypt`) to secure credentials.
* **Role-Based Access:** Users are redirected to specialized windows upon successful login: College Window, Manager Window, or Courier Window.
* **Request & Return Lifecycle:** Supports item requests, manager approval/rejection, courier pickup/delivery, and college return initiation.
* **Stock Tracking:** Maintains central inventory balances and per-college custody balances in real-time.
* **Dashboard & Backup:** Provides low-stock alerts based on Reorder Level and exports the entire database to a CSV backup file.

***

## 🛠️ Prerequisites and Setup

### 1. Database Setup (`.env` File)

Create a hidden file named **`.env`** in the root directory to store your database credentials. **Do not** upload this file to GitHub.

```text
# Replace the placeholder URL with your actual PostgreSQL connection string.
DATABASE_URL=postgres://YOUR_USERNAME:YOUR_PASSWORD@YOUR_HOST:YOUR_PORT/YOUR_DATABASE
### 2. Install Dependencies
Ensure you have Python installed. Then, install the required libraries using pip:

```bash
pip install -r requirements.txt
### 3. Initialize the Database
Run the `schema.sql` script included in the `database` folder to set up the necessary tables and user roles in your PostgreSQL instance.
## 🚀 How to Run
Once the database is connected and dependencies are installed, start the application:

```bash
python main.py
