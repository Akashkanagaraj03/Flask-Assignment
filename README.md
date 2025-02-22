# FLASK APP

## Overview
This is a Flask Application that has API Endpoints to perform CRUD operations on User data that is stored locally.

## Features
- User management (Create, Read, Update, Delete)  # refer the User Model
- User search using partial names and cities with pages
- Get detailed summary of the users
- OpenAPI 3.0 Documentation for the end points
- Logging for debugging
- Functional Tests checking the APIs for code 200
- Pre-commit hooks and code quality tools (ruff, black)
- Self Contained dependencies with poetry
- Containerised for easy deployment.
- JWT Authentication using username and password.
- Rate-Limiters for end points.

## Prerequisites
Make sure you have the following installed:
- Docker

## Setup

### 1. Clone the Repository
```bash
git clone 
cd flask-user-api
```

### 2. Set Up Virtual Environment
#### Using `pip`:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Using `poetry`:
```bash
poetry install
poetry shell
```

### 3. Configure Database
Ensure PostgreSQL is running and create a database:
```sql
CREATE DATABASE user_db;
```

Modify `app.py` with your database credentials:
```python
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://<user>:<password>@localhost:5432/user_db"
```

### 4. Run Migrations
```bash
flask db upgrade
```

### 5. Start the Server
```bash
flask run
```

## API Documentation
Once running, access API documentation at:
```
http://127.0.0.1:5000/docs
```

## Testing
Run tests using:
```bash
pytest
```

## Code Quality Tools
graph TD;
  ID["ID"] -->|Unique Identifier| Person
  First_Name["First Name"] --> Person
  Last_Name["Last Name"] --> Person
  Company_Name["Company Name"] --> Person
  Age["Age"] --> Person
  City["City"] --> Address
  State["State"] --> Address
  Zip["Zip"] --> Address
  Email["Email"] --> Contact
  Web["Web"] --> Contact

  Person --> Address
  Person --> Contact


## Logging
The application logs meaningful messages for debugging in `app.log`.
