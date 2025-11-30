# 📊 Project Management & Reporting System (PMRS)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-3.1%2B-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive enterprise-grade Django REST Framework application for managing construction project reports, tracking progress, and generating executive dashboards. This system provides real-time monitoring and reporting capabilities for multi-project portfolio management.

## 🌟 Key Features

### 📁 Project Management
- **Multi-project tracking** with hierarchical organization
- **Contract management** with complete lifecycle tracking
- **Company and stakeholder** information management
- **Zone-based project breakdown** for detailed monitoring

### 📈 Progress Monitoring
- **Real-time progress tracking** (planned vs. actual)
- **Financial monitoring** with multi-currency support (Rials & Foreign Currency)
- **Invoice management** with approval workflows
- **Budget tracking** and variance analysis
- **Work volume calculations** and reporting

### 📸 Visual Documentation
- **Zone-based image management** with up to 3 images per zone
- **Monthly photographic progress reports**
- **Before/after comparison** capabilities
- **Automated image report generation**

### 📋 Comprehensive Reporting
- **Monthly dashboard reports** aggregating all project metrics
- **HSE (Health, Safety & Environment) reports**
- **Financial reports** with detailed breakdowns
- **Executive summaries** for board presentations
- **Custom report generation** based on date ranges

### 🔐 Security & Access Control
- **JWT-based authentication** for secure API access
- **Role-based access control** (RBAC)
- **User activity tracking** and audit logs
- **Report visit tracking** for compliance

### 🚀 Performance & Scalability
- **Redis caching** for optimized performance
- **Efficient database queries** with ORM optimization
- **RESTful API architecture** for easy integration
- **Comprehensive test coverage** ensuring reliability

## 🏗️ Architecture

### Application Structure

```
pmrs/
├── accounts/          # User management, authentication & authorization
├── contracts/         # Contract and company management
├── projects/          # Project tracking and reporting
├── projects_files/    # Document and image management
└── main/             # Project configuration and settings
```

### Technology Stack

**Backend Framework:**
- Django 3.1+ (Web framework)
- Django REST Framework (API development)
- Django CORS Headers (Cross-origin resource sharing)

**Authentication & Security:**
- Simple JWT (JSON Web Token authentication)
- Django REST Framework Simple JWT

**Database:**
- PostgreSQL (Primary database)
- Redis (Caching layer)

**API Documentation:**
- drf-spectacular (OpenAPI 3.0 schema generation)
- Swagger UI integration

**Additional Libraries:**
- python-decouple (Environment variable management)
- Pillow (Image processing)
- jdatetime (Persian/Jalali date support)

## 📦 Installation

### Prerequisites

```bash
Python 3.8 or higher
PostgreSQL 12+
Redis 6+
pip (Python package installer)
```

### Step-by-Step Setup

1. **Clone the repository**

```bash
git clone https://github.com/AliSajadian/track_and_trace_api.git
cd track_and_trace_api
```

2. **Create and activate virtual environment**

```bash
# On Linux/Mac
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:

```env
# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=pmrs_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=1440  # minutes (24 hours)
```

5. **Set up PostgreSQL database**

```bash
# Access PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE pmrs_db;
CREATE USER pmrs_user WITH PASSWORD 'your_password';
ALTER ROLE pmrs_user SET client_encoding TO 'utf8';
ALTER ROLE pmrs_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pmrs_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE pmrs_db TO pmrs_user;
\q
```

6. **Run migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Create superuser**

```bash
python manage.py createsuperuser
```

8. **Start Redis server**

```bash
# On Linux/Mac
redis-server

# On Windows (if installed via WSL or native)
redis-server.exe
```

9. **Run development server**

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## 🔧 Configuration

### Cache Configuration

For production, update your `settings.py`:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### JWT Configuration

Customize JWT settings in `settings.py`:

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

## 📚 API Documentation

### Interactive API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI:** `http://localhost:8000/api/schema/swagger-ui/`
- **ReDoc:** `http://localhost:8000/api/schema/redoc/`
- **OpenAPI Schema:** `http://localhost:8000/api/schema/`

### Authentication

All API endpoints require JWT authentication. Obtain tokens via:

```bash
POST /api/token/
{
    "username": "your_username",
    "password": "your_password"
}
```

Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Include the access token in subsequent requests:
```bash
Authorization: Bearer <access_token>
```

### Core Endpoints

#### Projects
- `GET /api/projects/` - List all projects
- `POST /api/projects/` - Create new project
- `GET /api/projects/{id}/` - Retrieve project details
- `PUT /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project

#### Contracts
- `GET /api/contracts/` - List all contracts
- `POST /api/contracts/` - Create new contract
- `GET /api/contracts/{id}/` - Retrieve contract details

#### Zone Images
- `GET /api/zone-images/` - List zone images
- `POST /api/zone-images/` - Upload zone image
- `PUT /api/zone-images/{id}/` - Update zone image

#### Reports
- `GET /api/reports/dashboard/{date_id}/` - Get dashboard report
- `GET /api/reports/images/{date_id}/` - Get image report
- `GET /api/reports/financial/{contract_id}/{date_id}/` - Get financial report

## 🧪 Testing

The project includes comprehensive test coverage across all applications.

### Run all tests

```bash
python manage.py test
```

### Run tests for specific app

```bash
python manage.py test accounts
python manage.py test contracts
python manage.py test projects
python manage.py test projects_files
```

### Run with coverage report

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
# Open htmlcov/index.html in browser
```

### Test Structure

```
app_name/
├── tests/
│   ├── test_models.py      # Model tests
│   ├── test_serializers.py # Serializer tests
│   ├── test_services.py    # Business logic tests
│   └── test_api.py         # API endpoint tests
```

## 📊 Project Structure

```
track_and_trace_api/
├── accounts/
│   ├── models.py           # User, Role, UserRole models
│   ├── serializers.py      # DRF serializers
│   ├── api.py             # API viewsets
│   ├── services.py        # Business logic
│   └── tests/             # Test suite
├── contracts/
│   ├── models.py          # Contract, Company models
│   ├── serializers.py
│   ├── api.py
│   ├── services.py
│   └── tests/
├── projects/
│   ├── models.py          # Project progress, budget, invoice models
│   ├── serializers.py
│   ├── api.py
│   ├── services.py
│   └── tests/
├── projects_files/
│   ├── models.py          # Document and image models
│   ├── serializers.py
│   ├── api.py
│   ├── services.py
│   └── tests/
├── main/
│   ├── settings.py        # Project settings
│   ├── urls.py           # URL configuration
│   └── wsgi.py           # WSGI configuration
├── requirements.txt       # Python dependencies
├── manage.py             # Django management script
└── README.md            # This file
```

## 🚀 Deployment

### Production Considerations

1. **Environment Variables:** Never commit sensitive data. Use environment variables or secure vaults.

2. **Static Files:** Configure static file serving:
```bash
python manage.py collectstatic
```

3. **Database:** Use production-grade database settings with connection pooling.

4. **Web Server:** Deploy with Gunicorn/uWSGI behind Nginx/Apache.

5. **HTTPS:** Always use SSL/TLS certificates in production.

6. **Monitoring:** Implement logging, error tracking (Sentry), and performance monitoring.

### Example Gunicorn Configuration

```bash
gunicorn main.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guide
- Write descriptive commit messages
- Include tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Ali Sajadian**

- GitHub: [@AliSajadian](https://github.com/AliSajadian)
- LinkedIn: [Ali Sajadian](https://www.linkedin.com/in/alisajadian)

## 🙏 Acknowledgments

- Django and Django REST Framework communities
- All contributors and testers
- Open source libraries used in this project

## 📧 Contact & Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Email: [your-email@example.com]

---

**⭐ If you find this project useful, please consider giving it a star!**
