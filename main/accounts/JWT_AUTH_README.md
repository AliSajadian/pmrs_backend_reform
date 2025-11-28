# JWT Authentication with Redis - Implementation Guide

This document describes the new JWT-based authentication system implemented for the accounts app.

## Overview

A complete JWT authentication system with Redis-backed token storage has been implemented alongside the existing Knox authentication. The new system follows best practices with:

- **Fat Services, Thin Views**: Business logic in services, HTTP handling in views
- **JWT tokens with custom claims**: Includes user roles, permissions, and metadata
- **Redis token storage**: Secure token management with revocation support
- **Comprehensive tests**: Full test coverage for all components

## Architecture

### Service Layer (Fat Services)
All business logic is in `accounts/services.py`:

- **AuthService**: Login, logout, token refresh
- **UserService**: User creation, updates, password changes
- **TokenService**: JWT generation with custom claims, Redis storage
- **PermissionService**: Role and permission management

### API Layer (Thin Views)
HTTP request/response handling in `accounts/api1.py`:

- **LoginAPIView**: POST `/api/auth/login`
- **LogoutAPIView**: POST `/api/auth/logout`
- **TokenRefreshAPIView**: POST `/api/auth/refresh`
- **RegisterAPIView**: POST `/api/auth/register`
- **ChangePasswordAPIView**: PUT `/api/auth/changePassword`
- **UserProfileAPIView**: GET `/api/auth/profile`

### Serializers (Validation Only)
Data validation in `accounts/serializers1.py`:

- **LoginSerializer1**: Validate login credentials
- **RegisterSerializer1**: Validate registration data
- **TokenRefreshSerializer1**: Validate refresh tokens
- **ChangePasswordSerializer1**: Validate password changes
- **UserResponseSerializer**: Format user responses

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New packages added:
- `djangorestframework-simplejwt==5.2.2`
- `PyJWT==2.8.0`
- `redis==4.5.5`
- `django-redis==5.2.0`

### 2. Start Redis Server

On openSUSE Leap:

```bash
# Start Redis service
sudo systemctl start redis

# Enable Redis to start on boot
sudo systemctl enable redis

# Check Redis status
sudo systemctl status redis
```

### 3. Configure Settings

To use the new JWT authentication, you have two options:

**Option A: Use settings1.py (Recommended for testing)**

```bash
# Rename settings1.py to settings.py (backup the old one first)
cd main/main
cp settings.py settings_old.py
cp settings1.py settings.py
```

**Option B: Add configurations to existing settings.py**

Add the following to your `main/main/settings.py`:

```python
from datetime import timedelta

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps ...
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
]

# Update REST_FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'knox.auth.TokenAuthentication',  # Keep for backward compatibility
    ),
    # ... other settings ...
}

# Add SIMPLE_JWT configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'ALGORITHM': 'HS256',
}

# Add Redis cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
    'tokens': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 60 * 60 * 24 * 7,  # 7 days
    },
}
```

### 4. Run Migrations

```bash
python manage.py migrate
```

## API Endpoints

### 1. Login

**POST** `/api/auth/login`

Request:
```json
{
  "username": "user",
  "password": "pass"
}
```

Response:
```json
{
  "status": "success",
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "user",
    "email": "user@example.com",
    "full_name": "John Doe"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "access_expires_at": 1699999999,
  "refresh_expires_at": 1700000000,
  "roles": [
    {
      "role_id": 5,
      "role": "Project Manager",
      "project_id": 10,
      "project_name": "Project A",
      "all_projects": false,
      "permissions": ["Budget R/W", "Invoice R/W"]
    }
  ],
  "all_permissions": ["Budget R/W", "Invoice R/W"],
  "is_admin": true,
  "is_board": false
}
```

### 2. Logout

**POST** `/api/auth/logout`

Headers:
```
Authorization: Bearer <access_token>
```

Request:
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "logout_all": false
}
```

Response:
```json
{
  "status": "success",
  "message": "Logout successful"
}
```

### 3. Refresh Token

**POST** `/api/auth/refresh`

Request:
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Response:
```json
{
  "status": "success",
  "message": "Token refreshed successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer"
}
```

### 4. Register

**POST** `/api/auth/register`

Request:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "StrongPass123!",
  "password_confirm": "StrongPass123!",
  "first_name": "John",
  "last_name": "Doe",
  "personnel_code": 1234
}
```

Response: Same as login response

### 5. Change Password

**PUT** `/api/auth/changePassword`

Headers:
```
Authorization: Bearer <access_token>
```

Request:
```json
{
  "old_password": "OldPass123!",
  "new_password": "NewPass456!",
  "new_password_confirm": "NewPass456!"
}
```

Response:
```json
{
  "status": "success",
  "message": "Password changed successfully. Please login again with your new password."
}
```

### 6. Get Profile

**GET** `/api/auth/profile`

Headers:
```
Authorization: Bearer <access_token>
```

Response:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "username": "user",
    "email": "user@example.com",
    "full_name": "John Doe",
    "personnel_code": 1234,
    "is_active": true
  }
}
```

## JWT Token Structure

### Access Token Claims

```json
{
  "token_type": "access",
  "exp": 1699999999,
  "iat": 1699999000,
  "jti": "abc123...",
  "user_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "personnel_code": 1001,
  "roles": [
    {
      "role_id": 5,
      "role": "Project Manager",
      "project_id": 10,
      "project_name": "Project A",
      "all_projects": false,
      "permissions": ["Budget R/W", "Invoice R/W"]
    }
  ],
  "all_permissions": ["Budget R/W", "Invoice R/W"],
  "is_admin": true,
  "is_board": false
}
```

## Redis Token Storage

Tokens are stored in Redis with the following structure:

### Refresh Token Storage
- **Key**: `refresh_token:<user_id>:<token_jti>`
- **Value**: Token metadata (device info, IP, timestamps)
- **TTL**: 7 days

### User Tokens Set
- **Key**: `user_tokens:<user_id>`
- **Value**: Set of all active token JTIs for the user
- **TTL**: 7 days

### Blacklist
- **Key**: `blacklist:<user_id>:<token_jti>`
- **Value**: True
- **TTL**: 7 days

## Testing

### Run All Tests

```bash
python manage.py test accounts
```

### Run Specific Test Classes

```bash
# Test services
python manage.py test accounts.tests.TokenServiceTestCase
python manage.py test accounts.tests.AuthServiceTestCase
python manage.py test accounts.tests.UserServiceTestCase

# Test API endpoints
python manage.py test accounts.tests.AuthenticationAPITestCase

# Test Redis integration
python manage.py test accounts.tests.RedisIntegrationTestCase
```

### Test with Coverage

```bash
pip install coverage
coverage run --source='accounts' manage.py test accounts
coverage report
coverage html  # Generate HTML report
```

## Admin Interface

### Using Improved Admin (admin1.py)

To use the improved admin configuration, update `accounts/admin.py`:

```python
# At the top of admin.py
from accounts.admin1 import (
    PmrsUserAdmin1,
    RoleAdmin1,
    PermissionAdmin1,
    UserRoleAdmin1,
    RolePermissionAdmin1
)

# Replace existing admin registrations with:
# admin.site.register(PmrsUser, PmrsUserAdmin1)
# admin.site.register(Role, RoleAdmin1)
# etc.
```

Features of improved admin:
- Inline editing of user roles
- Bulk actions (activate/deactivate users, etc.)
- Better filtering and search
- Role/permission statistics
- Enhanced display fields

## Migration from Knox to JWT

The system is designed for gradual migration:

1. **Both systems active**: Knox and JWT endpoints coexist
   - Old Knox endpoints renamed (e.g., `/api/auth/loginOld`)
   - New JWT endpoints at original paths (e.g., `/api/auth/login`)

2. **Test JWT endpoints**: Verify functionality with test clients

3. **Update frontend**: Switch to JWT endpoints

4. **Remove Knox**: Once migration is complete, remove Knox code

## Troubleshooting

### Redis Connection Issues

```bash
# Check if Redis is running
sudo systemctl status redis

# Check Redis connectivity
redis-cli ping
# Should return: PONG

# Check Redis connection from Python
python manage.py shell
>>> from django.core.cache import caches
>>> cache = caches['tokens']
>>> cache.set('test', 'value')
>>> cache.get('test')
'value'
```

### Token Issues

```python
# Clear all tokens from Redis
python manage.py shell
>>> from django.core.cache import caches
>>> cache = caches['tokens']
>>> cache.clear()
```

### Debug Mode

Enable debug logging in `settings.py`:

```python
LOGGING = {
    # ...
    'loggers': {
        'accounts': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

## Security Considerations

1. **Token Lifetimes**: Access tokens expire in 15 minutes, refresh tokens in 7 days
2. **Token Rotation**: Refresh tokens are rotated on each refresh
3. **Token Revocation**: Logout revokes tokens immediately via Redis blacklist
4. **Password Changes**: All tokens are revoked on password change
5. **User Deactivation**: All tokens are revoked when user is deactivated

## Performance

- **Redis**: Sub-millisecond token lookups
- **Custom Claims**: No additional database queries needed for permissions
- **Connection Pooling**: Redis connection pool configured for high concurrency
- **Caching**: User permissions cached in JWT claims

## File Structure

```
accounts/
├── services.py          # NEW: Business logic (fat services)
├── api1.py             # NEW: Thin API views
├── serializers1.py     # NEW: Validation serializers
├── urls1.py            # NEW: JWT URL patterns
├── admin1.py           # NEW: Improved admin
├── tests.py            # UPDATED: Comprehensive tests
├── models.py           # UNCHANGED
├── api.py              # UNCHANGED (legacy Knox)
├── serializers.py      # UNCHANGED (legacy)
├── urls.py             # UPDATED (includes urls1.py)
└── admin.py            # UNCHANGED

main/
└── settings1.py        # NEW: Settings with JWT/Redis config
```

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Start Redis: `sudo systemctl start redis`
3. Configure settings (use settings1.py or update settings.py)
4. Run tests: `python manage.py test accounts`
5. Test endpoints with Postman/curl
6. Update frontend to use JWT endpoints
7. Monitor logs and Redis for issues

## Support

For issues or questions:
1. Check logs: `tail -f debug.log`
2. Review tests: `accounts/tests.py`
3. Check Redis: `redis-cli monitor`
4. Enable debug logging in settings

