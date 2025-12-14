# 🧾 Inventory Management System (IMS)

## 📦 About the Project
The **Inventory Management System (IMS)** is a desktop application built with Python to help small and medium-sized businesses manage their inventory efficiently. It works offline using a local SQLite database, with optional cloud backup for data safety.

---

## 🎯 Purpose
Manual inventory tracking can be slow, error-prone, and hard to scale. IMS solves this by:
- Automating stock updates
- Securing user access
- Tracking sales and purchases
- Alerting users when stock is low

---

## 👥 Who It's For
IMS is ideal for:
- Retail stores
- Supermarkets
- Pharmacies
- Warehouses
- Any shop managing physical goods

---

## 🌟 Main Features

### 🔐 User Login & Roles
- Secure login with encrypted passwords
- Role-based access:
  - **Admin**: Full control
  - **Cashier**: Handles transactions
  - **Client**: View-only access

### 📋 Inventory Management
- Add, update, or remove products
- Track item name, barcode, category, quantity, prices, and supplier
- Sort and filter items easily

### 💸 Sales & Purchases
- Sales reduce stock and generate receipts
- Purchases increase stock and log supplier info
- All transactions are saved with timestamps

### 🚨 Low Stock Alerts
- Alerts when items fall below set limits
- Visual and sound notifications
- Admins can customize thresholds

### 🔍 Smart Search
- Search by name, category, barcode, or supplier
- Supports partial matches (e.g., "sham" finds "Shampoo")
- Sort and filter results

### ☁️ Cloud Backup (Optional)
- Local database with optional cloud backup
- Supports Google Drive, Firebase, or AWS S3
- Restore data anytime if needed

### 👀 Client View Mode
- Clients can check product availability and prices
- No editing or transactions allowed

---

## 📊 Extra Features

### 📈 Reports & Analytics
- Generate sales, purchase, and stock reports
- Export to PDF or Excel
- Charts and graphs planned for future updates

### 🧾 Barcode Integration
- Scan barcodes to find products fast
- Generate and print barcodes for new items

---

## 🧰 Tech Stack

| Component   | Technology        | Why It’s Used                 |
|-------------|-------------------|-------------------------------|
| Frontend    | Custom Tkinter    | Simple, built-in Python GUI   |
| Backend     | Python            | Clean, powerful, and flexible |
| Database    | SQLite3           | Lightweight and reliable      |
| Language    | Python            | Great for both GUI and logic  |

---
