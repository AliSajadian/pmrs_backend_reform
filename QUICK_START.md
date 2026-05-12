# Quick Start Guide - JWT Authentication

## 5-Minute Setup

### 1. Install Dependencies (1 minute)

```bash
cd /home/ali/projects/cost_control/cost-control-backend
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Redis (1 minute)

```bash
sudo systemctl start redis
sudo systemctl enable redis
redis-cli ping  # Should return: PONG
```

### 3. Configure Settings (1 minute)

**Option A: Quick (use settings1.py)**
```bash
cd main/main
cp settings.py settings_backup.py
cp settings1.py settings.py
```

**Option B: Manual (keep settings.py)**
See `JWT_AUTH_README.md` for configuration to add to your settings.py

### 4. Run Migrations (30 seconds)

```bash
cd /home/ali/projects/cost_control/cost-control-backend/main
python manage.py migrate
```

### 5. Test the System (1.5 minutes)

**Run Tests:**
```bash
python manage.py test accounts
```

**Test Endpoints:**
```bash
cd /home/ali/projects/cost_control/cost-control-backend
python test_jwt_auth.py
```

**Or manually with curl:**
```bash
# Start the server
python main/manage.py runserver

# In another terminal, test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'
```

## What You Get

✅ JWT authentication with custom claims (roles, permissions)
✅ Redis-backed token storage with revocation
✅ Fat services (business logic) + Thin views (HTTP only)
✅ Complete test suite (44 tests)
✅ Improved admin interface
✅ Full documentation

## Files Created

| File | Purpose |
|------|---------|
| `main/accounts/services.py` | Business logic (AuthService, UserService, TokenService, PermissionService) |
| `main/accounts/api1.py` | Thin API views for JWT endpoints |
| `main/accounts/serializers1.py` | Validation serializers |
| `main/accounts/urls1.py` | URL patterns for JWT endpoints |
| `main/accounts/admin1.py` | Enhanced admin interface |
| `main/accounts/tests.py` | Comprehensive test suite |
| `main/main/settings1.py` | Settings with JWT/Redis config |
| `main/accounts/JWT_AUTH_README.md` | Complete documentation |
| `test_jwt_auth.py` | Quick test script |
| `IMPLEMENTATION_SUMMARY.md` | Detailed implementation summary |

## New Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login and get JWT tokens |
| POST | `/api/auth/logout` | Logout and revoke tokens |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/register` | Register new user |
| PUT | `/api/auth/changePassword` | Change password |
| GET | `/api/auth/profile` | Get current user profile |

## Example Usage

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

### Use Access Token
```bash
curl -X GET http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Refresh Token
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

## Troubleshooting

### Redis not running
```bash
sudo systemctl status redis
sudo systemctl start redis
```

### Connection errors
```bash
# Check Redis
redis-cli ping

# Check Django can connect
python manage.py shell
>>> from django.core.cache import caches
>>> caches['tokens'].set('test', 'ok')
>>> caches['tokens'].get('test')
'ok'
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## Next Steps

1. ✅ System is installed and tested
2. 📝 Read full documentation: `main/accounts/JWT_AUTH_README.md`
3. 🧪 Run comprehensive tests: `python manage.py test accounts`
4. 🌐 Test with your frontend
5. 📊 Check admin interface improvements (optional: use admin1.py classes)

## Support Files

- **Full Documentation**: `main/accounts/JWT_AUTH_README.md`
- **Implementation Details**: `IMPLEMENTATION_SUMMARY.md`
- **Test Script**: `test_jwt_auth.py`
- **Logs**: `main/debug.log`

## Architecture

```
Request → View (HTTP) → Service (Business Logic) → Model (Data)
                ↓
           Serializer (Validation)
                ↓
           Response (JSON)
```

**Thin Views**: Handle HTTP only
**Fat Services**: All business logic
**Serializers**: Validation only
**Models**: Data layer (unchanged)

---

**Ready to go!** 🚀

For detailed information, see `JWT_AUTH_README.md`

