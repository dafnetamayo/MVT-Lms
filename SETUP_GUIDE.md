# Complete Setup and Run Guide

This guide will walk you through setting up and running the Django LMS application with all the new features.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Option A: Setup with Docker (Recommended)](#option-a-setup-with-docker-recommended)
3. [Option B: Setup without Docker](#option-b-setup-without-docker)
4. [Environment Variables Configuration](#environment-variables-configuration)
5. [Database Setup](#database-setup)
6. [OAuth2 (Google) Configuration](#oauth2-google-configuration)
7. [Email Configuration](#email-configuration)
8. [Running the Application](#running-the-application)
9. [Testing the Features](#testing-the-features)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Python 3.11 or higher
- PostgreSQL (or use Docker)
- Git
- Docker and Docker Compose (optional, for Docker setup)
- Google Cloud Console account (for OAuth2)

---

## Option A: Setup with Docker (Recommended)

### Step 1: Clone and Navigate to Project
```bash
cd /Users/daftamayo/Documents/WEB2/django_docker
```

### Step 2: Create Environment File
Create a `.env` file in the project root:

```bash
touch .env
```

Add the following content to `.env`:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Docker Compose will use these)
DATABASE_NAME=mydatabase
DATABASE_USER=user
DATABASE_PASSWORD=password
DATABASE_HOST=db
DATABASE_PORT=5432

# Site Configuration
SITE_URL=http://localhost:8500
SITE_ID=1

# Email Configuration (for development, use console backend)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Swagger
SWAGGER_SCHEMA_URL=http://localhost:8500
```

**Generate a Secret Key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and replace `your-secret-key-here` in the `.env` file.

### Step 3: Build and Start Docker Containers
```bash
docker-compose up -d --build
```

This will:
- Build the Docker image
- Start PostgreSQL database
- Start the Django application

### Step 4: Run Migrations
```bash
docker-compose exec web python manage.py migrate
```

### Step 5: Create Superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

Follow the prompts to create an admin user.

### Step 6: Access the Application
- **Web Application**: http://localhost:8500
- **Admin Panel**: http://localhost:8500/admin
- **API Documentation**: http://localhost:8500/swagger/
