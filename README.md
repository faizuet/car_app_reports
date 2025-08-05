# 🚗 Car Registration Reporting System

A Flask backend system to manage and sync car registration data from Back4App to a local SQLite database, with secure JWT authentication, background syncing using Celery, and full CRUD functionality.

---

## 🔥 Features

- ✅ **User Authentication**
  - Secure JWT login/signup
  - Password hashing

- 🔁 **Data Sync from Back4App**
  - Fetch car data for years 2012–2022
  - Periodic background syncing using Celery + Redis
  - Avoids duplicates by updating existing entries

- 📦 **SQLite Storage**
  - Local persistent database using SQLAlchemy ORM

- 🔍 **Search & Filter**
  - Filter cars by make, model, year, or date
  - Pagination support for large datasets

- 📡 **RESTful API**
  - Clean endpoints using Flask Blueprints
  - Marshmallow schema validation
test test 


