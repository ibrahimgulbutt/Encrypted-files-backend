# Zero-Knowledge Encrypted Storage API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000/api/v1`  
**Environment:** Development  

## 🔐 Authentication

All endpoints except registration, login, and health checks require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## 📋 Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Response data here
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      // Additional error context
    }
  }
}
```

## 🔑 Authentication Endpoints

### 1. Register User
**POST** `/auth/register`

Register a new user with client-side hashed credentials.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password_hash": "client-side-hashed-password-32-chars-min",
  "salt": "random-salt-16-chars-min"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2025-11-08T18:30:00Z"
  }
}
```

**Rate Limit:** 3 requests per hour per IP

**Error Responses:**
- `409 Conflict` - Email already registered
- `422 Validation Error` - Invalid email format or weak credentials

---

### 2. User Login
**POST** `/auth/login`

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password_hash": "client-side-hashed-password"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "storage_used": 1048576,
      "storage_limit": 5368709120
    }
  }
}
```

**Rate Limit:** 5 requests per 15 minutes per IP

**Error Responses:**
- `401 Unauthorized` - Invalid credentials
- `403 Forbidden` - Account not active

---

### 3. Logout
**POST** `/auth/logout`

Invalidate current session (client-side token removal).

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### 4. Refresh Token
**POST** `/auth/refresh`

Get a new JWT token using existing valid token.

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "new-jwt-token-here",
    "expires_in": 3600
  }
}
```

---

### 5. Verify Token
**GET** `/auth/verify`

Verify if current token is valid.

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "expires_at": "2025-11-08T19:30:00Z"
  }
}
```

## 📁 File Management Endpoints

### 1. Upload File
**POST** `/files/upload`

Upload an encrypted file with metadata.

**Headers:** 
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Request Body (Form Data):**
```
file: <encrypted-binary-blob>
encrypted_filename: "base64-encrypted-filename-string"
encrypted_metadata: {
  "encrypted_size": "encrypted-value",
  "encrypted_type": "encrypted-value", 
  "encrypted_original_name": "encrypted-value"
}
file_size: 2048576  // actual bytes for quota check
```

**JavaScript Example:**
```javascript
const formData = new FormData();
formData.append('file', encryptedFileBlob);
formData.append('encrypted_filename', 'base64EncryptedName');
formData.append('encrypted_metadata', JSON.stringify({
  encrypted_size: 'encryptedSizeValue',
  encrypted_type: 'encryptedTypeValue',
  encrypted_original_name: 'encryptedNameValue'
}));
formData.append('file_size', actualFileSize);

fetch('/api/v1/files/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "data": {
    "file_id": "550e8400-e29b-41d4-a716-446655440000",
    "uploaded_at": "2025-11-08T18:30:00Z",
    "storage_path": "user-id/file-id.enc",
    "file_size": 2048576
  }
}
```

**Rate Limit:** 20 requests per hour per user

**Error Responses:**
- `402 Payment Required` - Storage quota exceeded
- `413 Payload Too Large` - File size exceeds 50MB limit
- `422 Validation Error` - Invalid metadata format

---

### 2. List Files
**GET** `/files`

Get paginated list of user's files.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)
- `sort_by` (optional): Sort field - `uploaded_at`, `file_size`, `encrypted_filename` (default: `uploaded_at`)
- `order` (optional): Sort order - `asc` or `desc` (default: `desc`)

**Example:** `/files?page=1&limit=10&sort_by=uploaded_at&order=desc`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "files": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "encrypted_filename": "base64-encrypted-name",
        "encrypted_metadata": {
          "encrypted_size": "encrypted-value",
          "encrypted_type": "encrypted-value",
          "encrypted_original_name": "encrypted-value"
        },
        "file_size": 2048576,
        "uploaded_at": "2025-11-08T18:30:00Z",
        "last_accessed": "2025-11-08T19:00:00Z"
      }
    ],
    "pagination": {
      "total": 45,
      "page": 1,
      "limit": 20,
      "total_pages": 3
    }
  }
}
```

**Rate Limit:** 1000 requests per hour per user

---

### 3. Get File Metadata
**GET** `/files/{file_id}`

Get detailed metadata for a specific file.

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "encrypted_filename": "base64-encrypted-name",
    "encrypted_metadata": {
      "encrypted_size": "encrypted-value",
      "encrypted_type": "encrypted-value",
      "encrypted_original_name": "encrypted-value"
    },
    "file_size": 2048576,
    "uploaded_at": "2025-11-08T18:30:00Z",
    "encryption_algorithm": "AES-256-GCM"
  }
}
```

**Error Responses:**
- `404 Not Found` - File not found or access denied

---

### 4. Download File
**GET** `/files/{file_id}/download`

Get a pre-signed URL for downloading the encrypted file.

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "download_url": "https://supabase-storage-url/signed-url",
    "expires_in": 300
  }
}
```

**Rate Limit:** 100 requests per hour per user

**Usage:**
```javascript
// Get download URL
const response = await fetch(`/api/v1/files/${fileId}/download`, {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { data } = await response.json();

// Download the encrypted file
const fileResponse = await fetch(data.download_url);
const encryptedBlob = await fileResponse.blob();
```

**Error Responses:**
- `404 Not Found` - File not found
- `410 Gone` - File has been deleted

---

### 5. Delete File (Soft)
**DELETE** `/files/{file_id}`

Mark file as deleted (can be recovered).

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "File deleted successfully",
  "data": {
    "file_id": "550e8400-e29b-41d4-a716-446655440000",
    "deleted_at": "2025-11-08T18:30:00Z"
  }
}
```

---

### 6. Delete File (Permanent)
**DELETE** `/files/{file_id}/permanent`

Permanently delete file from storage (cannot be recovered).

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "File permanently deleted"
}
```

## 👤 User Profile Endpoints

### 1. Get User Profile
**GET** `/user/profile`

Get complete user profile information.

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2025-01-01T00:00:00Z",
    "storage_used": 1048576,
    "storage_limit": 5368709120,
    "storage_percentage": 0.02,
    "total_files": 12,
    "last_login": "2025-11-08T18:00:00Z"
  }
}
```

---

### 2. Get Storage Statistics
**GET** `/user/storage`

Get detailed storage usage statistics.

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "used": 1048576,
    "limit": 5368709120,
    "available": 5367660544,
    "percentage": 0.02,
    "file_count": 12,
    "largest_file": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "encrypted_filename": "base64-encrypted-name",
      "size": 524288
    }
  }
}
```

---

### 3. Change Password
**PATCH** `/user/password`

Change user password (requires old password verification).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "old_password_hash": "client-hashed-old-password",
  "new_password_hash": "client-hashed-new-password", 
  "new_salt": "new-random-salt"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password updated successfully"
}
```

**⚠️ Warning:** Changing password requires re-encrypting all files with new master key (handled client-side).

**Error Responses:**
- `401 Unauthorized` - Current password is incorrect
- `422 Validation Error` - Invalid password format

## 🏥 System Health Endpoints

### 1. Health Check
**GET** `/health`

Check API and system health status.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-11-08T18:30:00Z",
    "version": "1.0.0",
    "database": "connected",
    "storage": "connected"
  }
}
```

---

### 2. System Statistics
**GET** `/stats`

Get system-wide statistics (future admin endpoint).

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "total_users": 1250,
    "total_files": 45000,
    "total_storage_used": 536870912000,
    "active_sessions": 234
  }
}
```

## 🔒 Security Guidelines

### Client-Side Encryption
- **All files must be encrypted client-side** before upload
- **Server never sees unencrypted data or encryption keys**
- Use strong encryption (AES-256-GCM recommended)
- Generate unique salts for each user

### Password Security
- Hash passwords client-side before sending to server
- Use minimum 32-character hash length
- Include 16+ character random salt
- Never send plaintext passwords

### Token Management
- Store JWT tokens securely (httpOnly cookies recommended)
- Tokens expire after 1 hour - implement refresh logic
- Remove tokens on logout
- Validate token expiry client-side

## 🚦 Rate Limits

| Endpoint Type | Limit |
|---------------|-------|
| Login attempts | 5 per 15 minutes per IP |
| Registration | 3 per hour per IP |
| File uploads | 20 per hour per user |
| File downloads | 100 per hour per user |
| General API requests | 1000 per hour per user |

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in window
- `X-RateLimit-Reset`: Window reset time

## 📊 HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | Success (GET, PATCH, DELETE) |
| `201` | Created (POST) |
| `400` | Bad Request (validation errors) |
| `401` | Unauthorized (missing/invalid token) |
| `402` | Payment Required (quota exceeded) |
| `403` | Forbidden (insufficient permissions) |
| `404` | Not Found |
| `409` | Conflict (duplicate resource) |
| `413` | Payload Too Large |
| `422` | Unprocessable Entity (validation error) |
| `429` | Too Many Requests (rate limited) |
| `500` | Internal Server Error |

## 🛠️ Frontend Integration Examples

### Authentication Flow
```javascript
class ApiClient {
  constructor(baseURL = 'http://localhost:8000/api/v1') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('auth_token');
  }

  async register(email, passwordHash, salt) {
    const response = await fetch(`${this.baseURL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password_hash: passwordHash, salt })
    });
    return await response.json();
  }

  async login(email, passwordHash) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password_hash: passwordHash })
    });
    const result = await response.json();
    
    if (result.success) {
      this.token = result.data.access_token;
      localStorage.setItem('auth_token', this.token);
    }
    
    return result;
  }

  async uploadFile(encryptedFile, encryptedFilename, encryptedMetadata, fileSize) {
    const formData = new FormData();
    formData.append('file', encryptedFile);
    formData.append('encrypted_filename', encryptedFilename);
    formData.append('encrypted_metadata', JSON.stringify(encryptedMetadata));
    formData.append('file_size', fileSize);

    const response = await fetch(`${this.baseURL}/files/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.token}` },
      body: formData
    });
    
    return await response.json();
  }

  async getFiles(page = 1, limit = 20) {
    const response = await fetch(
      `${this.baseURL}/files?page=${page}&limit=${limit}`,
      { headers: { 'Authorization': `Bearer ${this.token}` } }
    );
    return await response.json();
  }
}
```

### File Upload with Progress
```javascript
async function uploadFileWithProgress(file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    
    // Encrypt file first (your encryption logic)
    const encryptedFile = encryptFile(file);
    
    formData.append('file', encryptedFile.blob);
    formData.append('encrypted_filename', encryptedFile.filename);
    formData.append('encrypted_metadata', JSON.stringify(encryptedFile.metadata));
    formData.append('file_size', encryptedFile.size);

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        onProgress((e.loaded / e.total) * 100);
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status === 201) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error(`Upload failed: ${xhr.status}`));
      }
    });

    xhr.open('POST', '/api/v1/files/upload');
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    xhr.send(formData);
  });
}
```

## 🔧 Error Handling

Always check the `success` field in responses:

```javascript
async function handleApiResponse(response) {
  const data = await response.json();
  
  if (!data.success) {
    switch (data.error.code) {
      case 'UNAUTHORIZED':
        // Redirect to login
        window.location.href = '/login';
        break;
      case 'STORAGE_QUOTA_EXCEEDED':
        // Show upgrade prompt
        showUpgradeDialog();
        break;
      case 'RATE_LIMITED':
        // Show rate limit message
        showRateLimitMessage(data.error.details.retry_after);
        break;
      default:
        // Show generic error
        showErrorMessage(data.error.message);
    }
    throw new Error(data.error.message);
  }
  
  return data.data;
}
```

## 🚀 Development Notes

- **Base URL:** `http://localhost:8000/api/v1` (development)
- **API Documentation:** `http://localhost:8000/docs` (Swagger UI)
- **Content Type:** Use `application/json` for JSON payloads, `multipart/form-data` for file uploads
- **CORS:** Configured for `http://localhost:3000` (React dev server)
- **File Size Limit:** 50MB maximum per file
- **Default Storage Quota:** 5GB per user

---

**Need help?** Check the interactive API docs at `http://localhost:8000/docs` when the server is running.