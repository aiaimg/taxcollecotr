# Tax Collector RESTful API Documentation

## Overview

The Tax Collector API is a comprehensive, secure, and professional RESTful API service that serves multiple client platforms including web frontend and mobile scanning applications.

**Base URL:** `http://localhost:8000/api/v1/`

**API Version:** 1.0.0

**Documentation:** `http://localhost:8000/api/schema/swagger-ui/`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. All protected endpoints require a valid JWT token in the Authorization header.

### Getting an Access Token

**Endpoint:** `POST /api/v1/auth/login/`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "username": "user",
      "email": "user@example.com",
      "full_name": "John Doe"
    }
  }
}
```

### Using the Access Token

Include the token in the Authorization header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Refreshing Tokens

**Endpoint:** `POST /api/v1/auth/refresh/`

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Anonymous users:** 20 requests/minute, 100 requests/hour
- **Authenticated users:** 60 requests/minute, 1000 requests/hour
- **Authentication endpoints:** 5 requests/minute
- **Payment endpoints:** 10 requests/minute

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets

## Error Handling

All errors follow a consistent format:

```json
{
  "success": false,
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {}
  },
  "status_code": 400
}
```

### Common Error Codes

- `validation_error`: Input validation failed
- `authentication_failed`: Authentication failed
- `permission_denied`: User doesn't have permission
- `not_found`: Resource not found
- `internal_error`: Server error

## Endpoints

### Health Check

**GET** `/api/v1/health/`

Check API health status.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0",
    "checks": {
      "database": "ok",
      "cache": "ok"
    }
  }
}
```

### Vehicles

#### List Vehicles

**GET** `/api/v1/vehicles/`

List all vehicles for the authenticated user.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "plaque_immatriculation": "1234 TAA",
      "puissance_fiscale_cv": 10,
      "cylindree_cm3": 1500,
      "source_energie": "Essence",
      "date_premiere_circulation": "2020-01-01",
      "categorie_vehicule": "Personnel",
      "type_vehicule": {
        "id": 1,
        "nom": "Voiture"
      },
      "age_annees": 4,
      "est_exonere": false
    }
  ],
  "pagination": {
    "count": 1,
    "next": null,
    "previous": null,
    "page_size": 20,
    "current_page": 1,
    "total_pages": 1
  }
}
```

#### Get Vehicle Detail

**GET** `/api/v1/vehicles/{plaque_immatriculation}/`

Get detailed information about a specific vehicle.

#### Create Vehicle

**POST** `/api/v1/vehicles/`

Create a new vehicle.

**Request:**
```json
{
  "plaque_immatriculation": "5678 TBB",
  "puissance_fiscale_cv": 8,
  "cylindree_cm3": 1200,
  "source_energie": "Diesel",
  "date_premiere_circulation": "2021-01-01",
  "categorie_vehicule": "Personnel",
  "type_vehicule_id": 1
}
```

#### Get Vehicle Tax Information

**GET** `/api/v1/vehicles/{plaque_immatriculation}/tax_info/`

Get tax calculation information for a vehicle.

**Query Parameters:**
- `year`: Tax year (default: current year)

**Response:**
```json
{
  "success": true,
  "data": {
    "vehicule": {...},
    "tax_info": {
      "is_exempt": false,
      "amount": "50000.00",
      "year": 2024,
      "grid": {...}
    }
  }
}
```

### Tax Calculations

#### Calculate Tax

**POST** `/api/v1/tax-calculations/calculate/`

Calculate tax for vehicle data.

**Request:**
```json
{
  "plaque_immatriculation": "1234 TAA",
  "puissance_fiscale_cv": 10,
  "cylindree_cm3": 1500,
  "source_energie": "Essence",
  "date_premiere_circulation": "2020-01-01",
  "categorie_vehicule": "Personnel",
  "annee_fiscale": 2024
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "montant_du_ariary": 50000.00,
    "annee_fiscale": 2024,
    "est_exonere": false,
    "grille_tarifaire": {...},
    "details": {}
  }
}
```

### Payments

#### List Payments

**GET** `/api/v1/payments/`

List all payments for the authenticated user.

#### Get Payment Detail

**GET** `/api/v1/payments/{id}/`

Get detailed information about a specific payment.

### Notifications

#### List Notifications

**GET** `/api/v1/notifications/`

List all notifications for the authenticated user.

#### Mark Notification as Read

**POST** `/api/v1/notifications/{id}/mark_read/`

Mark a notification as read.

#### Mark All Notifications as Read

**POST** `/api/v1/notifications/mark_all_read/`

Mark all notifications as read.

#### Get Unread Count

**GET** `/api/v1/notifications/unread_count/`

Get count of unread notifications.

### Dashboard

#### Get Dashboard Statistics

**GET** `/api/v1/dashboard/stats/`

Get dashboard statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "vehicles": {
      "total": 10,
      "user_total": 10
    },
    "payments": {
      "total": 5,
      "pending": 2,
      "total_amount": 250000.00
    },
    "notifications": {
      "unread": 3
    }
  }
}
```

### Utility Endpoints

#### Convert Cylindree to CV

**POST** `/api/v1/convert-cylindree/`

Convert engine displacement (cylindree) to fiscal power (CV).

**Request:**
```json
{
  "cylindree": 1500
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "cylindree": 1500,
    "cv_min": 10,
    "cv_max": 12,
    "cv_suggere": 10,
    "plage_description": "De 10 à 12 CV",
    "message": "Pour 1500cm³, la puissance fiscale est généralement De 10 à 12 CV"
  }
}
```

## Pagination

All list endpoints support pagination:

- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

Pagination information is included in the response:

```json
{
  "pagination": {
    "count": 100,
    "next": "http://localhost:8000/api/v1/vehicles/?page=2",
    "previous": null,
    "page_size": 20,
    "current_page": 1,
    "total_pages": 5
  }
}
```

## Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Best Practices

1. **Always use HTTPS in production**
2. **Store tokens securely** - Never expose tokens in client-side code
3. **Handle token expiration** - Implement token refresh logic
4. **Respect rate limits** - Implement exponential backoff
5. **Validate input** - Always validate data before sending
6. **Handle errors gracefully** - Check response status and error codes
7. **Use pagination** - Don't request all data at once
8. **Cache when appropriate** - Cache static data to reduce API calls

## Support

For API support, please contact the development team or refer to the Swagger documentation at `/api/schema/swagger-ui/`.

