# Tax Collector API Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/v1/`

## Docker Setup

### Build and Run with Docker Compose

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis cache
- Django web server
- Celery worker
- Celery beat scheduler

### Access Services

- **API:** http://localhost:8000/api/v1/
- **Swagger UI:** http://localhost:8000/api/schema/swagger-ui/
- **ReDoc:** http://localhost:8000/api/schema/redoc/
- **Health Check:** http://localhost:8000/api/v1/health/

## Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/taxcollector

# Redis
REDIS_URL=redis://localhost:6379/0

# Stripe (Optional)
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
STRIPE_CURRENCY=MGA
```

## API Testing

### Using curl

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Get vehicles (with token)
curl -X GET http://localhost:8000/api/v1/vehicles/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using Python requests

```python
import requests

# Login
response = requests.post('http://localhost:8000/api/v1/auth/login/', json={
    'email': 'user@example.com',
    'password': 'password123'
})
data = response.json()
access_token = data['data']['access']

# Get vehicles
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get('http://localhost:8000/api/v1/vehicles/', headers=headers)
print(response.json())
```

## Running Tests

```bash
# Run all API tests
pytest api/tests/

# Run with coverage
pytest api/tests/ --cov=api --cov-report=html

# Run specific test file
pytest api/tests/test_authentication.py
```

## Production Deployment

### Using Gunicorn

```bash
gunicorn --bind 0.0.0.0:8000 --workers 4 taxcollector_project.wsgi:application
```

### Using Docker

```bash
docker build -t taxcollector-api .
docker run -p 8000:8000 taxcollector-api
```

### Environment-Specific Settings

For production, ensure:
- `DEBUG=False`
- `SECRET_KEY` is set and secure
- `ALLOWED_HOSTS` includes your domain
- Database is properly configured
- HTTPS is enabled
- CORS is configured for your frontend domain

## API Documentation

- **Swagger UI:** http://localhost:8000/api/schema/swagger-ui/
- **ReDoc:** http://localhost:8000/api/schema/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

## Security Checklist

- [ ] HTTPS is enabled in production
- [ ] SECRET_KEY is secure and not committed
- [ ] CORS is properly configured
- [ ] Rate limiting is enabled
- [ ] JWT tokens have appropriate expiration times
- [ ] Database credentials are secure
- [ ] Environment variables are not exposed
- [ ] API keys are stored securely

## Troubleshooting

### Database Connection Issues

```bash
# Check database is running
docker-compose ps

# Check database connection
python manage.py dbshell
```

### Redis Connection Issues

```bash
# Check Redis is running
redis-cli ping
```

### Token Issues

- Ensure JWT settings are correct in `settings.py`
- Check token expiration times
- Verify token format in Authorization header

## Support

For issues or questions, refer to:
- API Documentation: `API_DOCUMENTATION.md`
- Swagger UI: `/api/schema/swagger-ui/`
- Project README: `README.md`

