# Notification API Documentation

## Base URL
```
/notifications/
```

## Authentication
All endpoints require user authentication via Django session or token.

---

## Endpoints

### 1. List Notifications
Get paginated list of user's notifications.

**Endpoint:** `GET /notifications/`

**Authentication:** Required

**Query Parameters:**
- `page` (optional): Page number (default: 1)

**Response:**
```html
HTML page with notification list
```

**Example:**
```bash
curl -X GET http://localhost:8000/notifications/ \
  -H "Cookie: sessionid=xxx"
```

---

### 2. Get Notification Detail
View a single notification (marks as read automatically).

**Endpoint:** `GET /notifications/<notification_id>/`

**Authentication:** Required

**URL Parameters:**
- `notification_id` (UUID): Notification ID

**Response:**
```html
HTML page with notification details
```

**Example:**
```bash
curl -X GET http://localhost:8000/notifications/123e4567-e89b-12d3-a456-426614174000/ \
  -H "Cookie: sessionid=xxx"
```

---

### 3. Mark Notification as Read
Mark a specific notification as read.

**Endpoint:** `POST /notifications/<notification_id>/mark-read/`

**Authentication:** Required

**URL Parameters:**
- `notification_id` (UUID): Notification ID

**Headers (for AJAX):**
```
X-Requested-With: XMLHttpRequest
X-CSRFToken: <csrf_token>
```

**Response (AJAX):**
```json
{
  "success": true,
  "message": "Notification marquée comme lue"
}
```

**Response (Regular):**
Redirect to notification list

**Example (AJAX):**
```javascript
fetch('/notifications/123e4567-e89b-12d3-a456-426614174000/mark-read/', {
  method: 'POST',
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
    'X-CSRFToken': getCookie('csrftoken')
  }
})
.then(response => response.json())
.then(data => console.log(data.message));
```

---

### 4. Mark All as Read
Mark all user's notifications as read.

**Endpoint:** `POST /notifications/mark-all-read/`

**Authentication:** Required

**Headers (for AJAX):**
```
X-Requested-With: XMLHttpRequest
X-CSRFToken: <csrf_token>
```

**Response (AJAX):**
```json
{
  "success": true,
  "message": "5 notifications marquées comme lues",
  "count": 5
}
```

**Response (Regular):**
Redirect to notification list

**Example (AJAX):**
```javascript
fetch('/notifications/mark-all-read/', {
  method: 'POST',
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
    'X-CSRFToken': getCookie('csrftoken')
  }
})
.then(response => response.json())
.then(data => console.log(`${data.count} notifications marked as read`));
```

---

### 5. Get Unread Count (API)
Get the count of unread notifications.

**Endpoint:** `GET /notifications/api/unread-count/`

**Authentication:** Required

**Response:**
```json
{
  "count": 3
}
```

**Example:**
```javascript
fetch('/notifications/api/unread-count/')
  .then(response => response.json())
  .then(data => {
    document.getElementById('notif-badge').textContent = data.count;
  });
```

**Example (cURL):**
```bash
curl -X GET http://localhost:8000/notifications/api/unread-count/ \
  -H "Cookie: sessionid=xxx"
```

---

### 6. Get Recent Notifications (API)
Get recent notifications for the user.

**Endpoint:** `GET /notifications/api/recent/`

**Authentication:** Required

**Query Parameters:**
- `limit` (optional): Number of notifications to return (default: 10, max: 50)

**Response:**
```json
{
  "notifications": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "titre": "Véhicule ajouté",
      "contenu": "Le véhicule ABC-123 a été ajouté avec succès à votre compte.",
      "type": "system",
      "est_lue": false,
      "date_envoi": "2025-11-01T10:30:00Z"
    },
    {
      "id": "223e4567-e89b-12d3-a456-426614174001",
      "titre": "Paiement confirmé",
      "contenu": "Votre paiement pour le véhicule ABC-123 a été confirmé. Montant payé: 50,000 Ar",
      "type": "system",
      "est_lue": true,
      "date_envoi": "2025-11-01T09:15:00Z"
    }
  ],
  "unread_count": 1
}
```

**Example:**
```javascript
fetch('/notifications/api/recent/?limit=5')
  .then(response => response.json())
  .then(data => {
    console.log(`${data.unread_count} unread notifications`);
    data.notifications.forEach(notif => {
      console.log(`${notif.titre}: ${notif.contenu}`);
    });
  });
```

**Example (cURL):**
```bash
curl -X GET "http://localhost:8000/notifications/api/recent/?limit=5" \
  -H "Cookie: sessionid=xxx"
```

---

## Notification Object Structure

### Notification Model
```json
{
  "id": "UUID",
  "user": "User ID",
  "type_notification": "email|sms|push|system",
  "titre": "Notification title",
  "contenu": "Notification content",
  "langue": "fr|mg",
  "est_lue": false,
  "date_envoi": "2025-11-01T10:30:00Z",
  "date_lecture": null,
  "metadata": {
    "event": "vehicle_added",
    "vehicle_id": "123",
    "additional_data": "..."
  }
}
```

### Field Descriptions
- `id`: Unique notification identifier (UUID)
- `user`: User who receives the notification
- `type_notification`: Type of notification (system, email, sms, push)
- `titre`: Notification title/subject
- `contenu`: Notification content/message
- `langue`: Language code (fr=French, mg=Malagasy)
- `est_lue`: Read status (true/false)
- `date_envoi`: When notification was created
- `date_lecture`: When notification was read (null if unread)
- `metadata`: Additional data in JSON format

---

## Integration Examples

### React/Vue.js Integration

#### Fetch Unread Count
```javascript
// React Hook
import { useState, useEffect } from 'react';

function useNotificationCount() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const fetchCount = async () => {
      const response = await fetch('/notifications/api/unread-count/');
      const data = await response.json();
      setCount(data.count);
    };
    
    fetchCount();
    const interval = setInterval(fetchCount, 30000); // Poll every 30s
    
    return () => clearInterval(interval);
  }, []);
  
  return count;
}

// Usage
function NotificationBadge() {
  const count = useNotificationCount();
  
  return count > 0 ? (
    <span className="badge">{count}</span>
  ) : null;
}
```

#### Display Recent Notifications
```javascript
// Vue.js Component
export default {
  data() {
    return {
      notifications: [],
      unreadCount: 0
    }
  },
  mounted() {
    this.fetchNotifications();
  },
  methods: {
    async fetchNotifications() {
      const response = await fetch('/notifications/api/recent/?limit=10');
      const data = await response.json();
      this.notifications = data.notifications;
      this.unreadCount = data.unread_count;
    },
    async markAsRead(notificationId) {
      await fetch(`/notifications/${notificationId}/mark-read/`, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': this.getCsrfToken()
        }
      });
      this.fetchNotifications(); // Refresh
    }
  }
}
```

### jQuery Integration
```javascript
// Notification dropdown
$(document).ready(function() {
  // Load notifications
  function loadNotifications() {
    $.get('/notifications/api/recent/?limit=5', function(data) {
      $('#notif-count').text(data.unread_count);
      
      const $list = $('#notif-list').empty();
      data.notifications.forEach(function(notif) {
        const $item = $('<li>')
          .addClass(notif.est_lue ? 'read' : 'unread')
          .html(`
            <strong>${notif.titre}</strong>
            <p>${notif.contenu}</p>
            <small>${new Date(notif.date_envoi).toLocaleString()}</small>
          `)
          .data('id', notif.id);
        
        $list.append($item);
      });
    });
  }
  
  // Mark as read on click
  $(document).on('click', '#notif-list li', function() {
    const notifId = $(this).data('id');
    $.post(`/notifications/${notifId}/mark-read/`, {
      csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
    }, function() {
      loadNotifications();
    });
  });
  
  // Load on page load and every 30 seconds
  loadNotifications();
  setInterval(loadNotifications, 30000);
});
```

### Vanilla JavaScript Integration
```javascript
// Simple notification system
class NotificationManager {
  constructor() {
    this.updateInterval = null;
  }
  
  async getUnreadCount() {
    const response = await fetch('/notifications/api/unread-count/');
    const data = await response.json();
    return data.count;
  }
  
  async getRecent(limit = 10) {
    const response = await fetch(`/notifications/api/recent/?limit=${limit}`);
    const data = await response.json();
    return data;
  }
  
  async markAsRead(notificationId) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    const response = await fetch(`/notifications/${notificationId}/mark-read/`, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrfToken
      }
    });
    
    return await response.json();
  }
  
  async markAllAsRead() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    const response = await fetch('/notifications/mark-all-read/', {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrfToken
      }
    });
    
    return await response.json();
  }
  
  startPolling(interval = 30000) {
    this.updateInterval = setInterval(async () => {
      const count = await this.getUnreadCount();
      this.updateBadge(count);
    }, interval);
  }
  
  stopPolling() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }
  }
  
  updateBadge(count) {
    const badge = document.getElementById('notification-badge');
    if (badge) {
      badge.textContent = count;
      badge.style.display = count > 0 ? 'inline' : 'none';
    }
  }
}

// Usage
const notificationManager = new NotificationManager();
notificationManager.startPolling();
```

---

## WebSocket Integration (Future)

### Real-time Notifications
```javascript
// Future implementation with Django Channels
const notificationSocket = new WebSocket(
  'ws://localhost:8000/ws/notifications/'
);

notificationSocket.onmessage = function(e) {
  const data = JSON.parse(e.data);
  
  if (data.type === 'notification') {
    showNotification(data.notification);
    updateBadge(data.unread_count);
  }
};

function showNotification(notification) {
  // Display notification toast/popup
  console.log(`New notification: ${notification.titre}`);
}
```

---

## Error Handling

### HTTP Status Codes
- `200 OK`: Request successful
- `302 Found`: Redirect (for non-AJAX requests)
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not authorized to access this notification
- `404 Not Found`: Notification not found
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "error": "Error message",
  "detail": "Detailed error description"
}
```

### Example Error Handling
```javascript
async function markNotificationAsRead(notificationId) {
  try {
    const response = await fetch(`/notifications/${notificationId}/mark-read/`, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCsrfToken()
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log(data.message);
  } catch (error) {
    console.error('Error marking notification as read:', error);
    alert('Failed to mark notification as read. Please try again.');
  }
}
```

---

## Rate Limiting

### Current Limits
- No rate limiting currently implemented
- Future: 100 requests per minute per user

### Best Practices
- Poll unread count every 30-60 seconds (not more frequently)
- Use WebSocket for real-time updates (when available)
- Cache notification data on client side
- Batch mark-as-read operations when possible

---

## Security Considerations

### CSRF Protection
All POST requests must include CSRF token:
```javascript
function getCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
}
```

### Authentication
- Session-based authentication (cookies)
- Token-based authentication (future: JWT)

### Authorization
- Users can only access their own notifications
- Attempting to access another user's notification returns 403

---

## Testing

### cURL Examples

#### Get unread count
```bash
curl -X GET http://localhost:8000/notifications/api/unread-count/ \
  -H "Cookie: sessionid=your_session_id"
```

#### Get recent notifications
```bash
curl -X GET "http://localhost:8000/notifications/api/recent/?limit=5" \
  -H "Cookie: sessionid=your_session_id"
```

#### Mark as read
```bash
curl -X POST http://localhost:8000/notifications/123e4567-e89b-12d3-a456-426614174000/mark-read/ \
  -H "Cookie: sessionid=your_session_id" \
  -H "X-CSRFToken: your_csrf_token" \
  -H "X-Requested-With: XMLHttpRequest"
```

---

## Changelog

### Version 1.0 (2025-11-01)
- Initial API release
- Basic CRUD operations
- Unread count endpoint
- Recent notifications endpoint
- Mark as read functionality

---

**Last Updated:** November 1, 2025  
**API Version:** 1.0  
**Maintained By:** Development Team
