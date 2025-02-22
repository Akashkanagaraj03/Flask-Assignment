# FLASK APP

## Overview
This is a REST API built using Flask to manage user data, backed by a PostgreSQL database. The API supports CRUD operations, searching, sorting, and basic analytics.

## Features
- User management (Create, Read, Update, Delete)
- Pagination and search functionality
- OpenAPI documentation
- Logging for debugging
- Unit and functional tests
- Pre-commit hooks and code quality tools (ruff, black, poetry)

## Prerequisites
Make sure you have the following installed:
- Python 3.10+
- PostgreSQL
- `pip` or `poetry`
- `virtualenv` (if using `pip`)

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/nee23thu/flask-user-api.git
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
Run the following commands for linting and formatting:
```bash
ruff .  # Linting
black .  # Formatting
```

To use `pre-commit` hooks:
```bash
pre-commit install
pre-commit run --all-files
```

## Logging
The application logs meaningful messages for debugging in `app.log`.
