# Supabase Database Setup Instructions

Follow these steps to set up your Supabase database for the Encrypted Storage backend:

## 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Choose your organization and project name
3. Set a strong database password
4. Select your preferred region
5. Wait for the project to be created

## 2. Get Your Credentials

From your Supabase project dashboard:

1. Go to Settings > API
2. Copy the following values:
   - **Project URL** (e.g., `https://your-project.supabase.co`)
   - **anon public key** (for `SUPABASE_KEY`)
   - **service_role secret key** (for `SUPABASE_SERVICE_KEY`)

## 3. Run Database Setup Scripts

Execute the SQL scripts in order using the SQL Editor in your Supabase dashboard:

### Step 1: Create Tables and Indexes
```sql
-- Run: sql/01_create_tables.sql
-- This creates the users and files tables with proper indexes
```

### Step 2: Set Up Row Level Security
```sql
-- Run: sql/02_rls_policies.sql  
-- This creates RLS policies for data security
```

### Step 3: Set Up Storage Bucket
```sql
-- Run: sql/03_storage_setup.sql
-- This creates the storage bucket and policies
```

## 4. Create Storage Bucket (Alternative Method)

If the SQL method doesn't work, create the bucket manually:

1. Go to Storage in your Supabase dashboard
2. Click "Create Bucket"
3. Name: `Files`
4. Set as Private (not public)
5. Click "Create Bucket"

## 5. Configure Storage Policies

In Storage > Files > Policies, add these policies:

### Policy 1: "Users can upload their own files"
- **Type**: INSERT
- **Target roles**: authenticated
- **Policy**: 
  ```sql
  bucket_id = 'Files' AND 
  (storage.foldername(name))[1] = auth.uid()::text
  ```

### Policy 2: "Users can view their own files"
- **Type**: SELECT
- **Target roles**: authenticated
- **Policy**:
  ```sql
  bucket_id = 'Files' AND 
  (storage.foldername(name))[1] = auth.uid()::text
  ```

### Policy 3: "Users can update their own files"
- **Type**: UPDATE
- **Target roles**: authenticated
- **Policy**:
  ```sql
  bucket_id = 'Files' AND 
  (storage.foldername(name))[1] = auth.uid()::text
  ```

### Policy 4: "Users can delete their own files"
- **Type**: DELETE
- **Target roles**: authenticated
- **Policy**:
  ```sql
  bucket_id = 'Files' AND 
  (storage.foldername(name))[1] = auth.uid()::text
  ```

## 6. Update Environment Variables

Copy `.env.example` to `.env` and update with your Supabase credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key
SUPABASE_SERVICE_KEY=your-service-role-secret-key
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-chars
```

## 7. Verify Setup

Run a quick test to verify everything is working:

1. Install dependencies: `pip install -r requirements.txt`
2. Start the server: `python main.py`
3. Check health endpoint: `GET http://localhost:8000/api/v1/health`

The response should show:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": "connected",
    "storage": "connected"
  }
}
```

## 8. Optional: Enable Database Webhooks

For real-time features, you can set up webhooks:

1. Go to Database > Webhooks
2. Create webhooks for `users` and `files` tables
3. Configure your application to handle webhook events

## Security Notes

- Never commit your `.env` file to version control
- Use strong, unique passwords for your database
- Regularly rotate your service role key
- Monitor your Supabase logs for suspicious activity
- Set up proper backup and recovery procedures

## Troubleshooting

### Common Issues:

1. **Storage bucket not found**: Ensure the bucket name matches exactly (`Files`)
2. **RLS policies not working**: Double-check the policy syntax and target roles
3. **Connection failed**: Verify your credentials and network connection
4. **Permission denied**: Make sure you're using the service role key for admin operations

For more help, check the [Supabase documentation](https://supabase.com/docs) or contact support.