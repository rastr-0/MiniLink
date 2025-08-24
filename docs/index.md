# MiniLink API

Welcome to the **MiniLink API** documentation 👋

This project provides a simple **URL shortening service** backend with authentication, links management, and token-based
security.

---

# 🔑 Authentication & User Management

## 1. Register a New User

**POST** ```/api/v1/register```

Register a new user in the system.

**Request:**

```json
{
  "username": "daddy-o",
  "fullname": "John Doe",
  "password": "mypassword123"
}
```

**Response (200 OK):**

```json
{
  "id": "1",
  "username": "daddy-o",
  "created_at": "2025-08-20T14:22:10Z"
}
```

**Errors:**

- `409 Conflict` → User already exists
- `500 Internal Server Error` → Database or service failure

---

## 2. Login (Get Token)

**POST** ```/api/v1/register```

Authenticates a user and returns a JWT token for subsequent requests.

**Request (Form-encoded, not JSON!):**

```
username=daddy-o
password=mypassword123
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Errors:**

- `401 Unauthorized` → Wrong credentials given
- `404 Not Found` → User not found
- `500 Internal Server Error` → Database or service failure

---

## 3. Get Current User

**GET** ```/api/v1/me```

Returns the profile of the currently authenticated user.

**Headers:**

```
Authorization: Bearer <JWT_TOKEN>
```

**Resonse (200 OK):**

```json
{
  "id": "1",
  "username": "daddy-o",
  "created_at": "2025-08-20T14:22:10Z"
}
```

**Errors:**

- `401 Unauthorized` → Missing or invalid token

---

# ✅ URLs Management (private)

Endpoints for managing user short links: create, fetch statistics, list, and delete.

## 1. Create a Short URL

**POST** ```/api/v1/shorten```

Create a new short URL for an authenticated user.

**Request:**

```json
{
  "original_url": "https://example.com/very/long/url",
  "custom_alias": "myalias",
  "single_use": false
}
```

**Response (200 OK):**

```json
{
  "short_url": "http://localhost:8000/myalias",
  "short_code": "myalias",
  "created_at": "2025-08-20T14:30:00",
  "expiration_time": "2025-08-25T12:00:00",
  "created_by_user": "john"
}

```

**Errors:**

- `409 Conflict` → Alias already taken
- `500 Internal Server Error` → Service unavailable

---

## 2. Get Statistics for a Short URL

**GET** ```api/v1/stats/{short_code}```

Fetch statistics for a given short URL by its code.

**Response (200 OK):**

```json
{
  "original_url": "https://example.com/very/long/url",
  "short_code": "myalias",
  "clicks": 42
}
```

**Errors:**

- `404 Not Found` → Short URL is not present
- `403 Forbidden` → Permission denied

---

## 3. List User Short URLs

**GET** ```api/v1/my/urls```

Retrieve all short URLs created by the authenticated user.
Supports optional filters.

**Query parameters:**

- `limit` (int) → Maximum number of results
- `offset` (int) → Offset for pagination
- `max_clicks` (int) → Maximum required clicks
- `min_clicks` (int) → Minimum required clicks
- `active` (bool) → Filter active links only
- `one_time_only` (bool) → Filter single-use links
- `created_after` (str) → Filter by creation date (after)
- `created_before` (str) → Filter by creation date (before)

**Response (200 OK):**

```json
{
  "short_urls": [
    {
      "short_url": "http://localhost:8000/myalias",
      "short_code": "myalias",
      "created_at": "2025-08-20T14:30:00",
      "expiration_time": "2025-08-25T12:00:00",
      "created_by_user": "john"
    },
    {
      "short_url": "http://localhost:8000/abcd123",
      "short_code": "abcd123",
      "created_at": "2025-08-20T15:00:00",
      "expiration_time": "2025-08-21T15:00:00",
      "created_by_user": "john"
    }
  ]
}
```

**Errors:**

- `500 Internal Server Error` → Service unavailable

---

## 4. Delete a Short URL

**DELETE** `api/v1/{short_code}`

Delete a short URL owned by the authenticated user.

**Response (200 OK):**

```json
{
  "id": "4",
  "result": "successfully deleted"
}
```

**Errors:**

- `404 Not Found` → Short URL not found

---

# ✅ URLs Management (public)

Public endpoints for redirection.

## 1. Redirect User

GET ```/{short_code}```

Redirects the client from the short URL to the original destination.

**Response (307 Temporary Redirect)**: redirects to the original URL.

**Errors:**

- `404 Not Found` → Short URL not found
- `503 Service Unavailable` → Service unavailable

---