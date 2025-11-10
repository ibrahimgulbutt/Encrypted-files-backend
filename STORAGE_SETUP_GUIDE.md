# Supabase Storage Setup Guide

This guide will help you configure your Supabase storage bucket for the encrypted file storage system.

## Step 1: Create Storage Bucket

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Navigate to your project: `nkfrqmduneknfmyqotpb`
3. Go to **Storage** in the left sidebar
4. Click **"New bucket"**
5. Create a bucket named: `Files` (exactly as shown)
6. Keep it **Private** for now

## Step 2: Configure Bucket Policies (Choose One Option)

### Option A: Make Bucket Public (Quick Setup - Development Only)
**⚠️ Warning: This makes all files publicly accessible. Only use for development!**

1. In Storage dashboard, find your `Files` bucket
2. Click the three dots (**⋯**) next to the bucket name
3. Select **"Make public"**
4. Confirm the action

### Option B: Set Up RLS Policies (Recommended for Production)

1. Go to **Authentication** → **Policies** in Supabase dashboard
2. Click **"New Policy"** 
3. Select table: `objects` (from `storage` schema)

Create these three policies:

#### Policy 1: Allow Authenticated Upload
- **Name:** `Allow authenticated users to upload files`
- **Allowed operation:** `INSERT`
- **Policy definition:**
```sql
(auth.role() = 'authenticated') AND (bucket_id = 'Files')
```

#### Policy 2: Allow Users to Read Their Files  
- **Name:** `Allow users to read their own files`
- **Allowed operation:** `SELECT`
- **Policy definition:**
```sql
(auth.role() = 'authenticated') AND (bucket_id = 'Files') AND ((storage.foldername(name))[1] = (auth.uid())::text)
```

#### Policy 3: Allow Users to Delete Their Files
- **Name:** `Allow users to delete their own files` 
- **Allowed operation:** `DELETE`
- **Policy definition:**
```sql
(auth.role() = 'authenticated') AND (bucket_id = 'Files') AND ((storage.foldername(name))[1] = (auth.uid())::text)
```

## Step 3: Test the Setup

Run the storage test script:
```bash
cd /home/ibrahim-butt/Desktop/General/My-Projects/Encrypted-Storage/backend
source venv/bin/activate
python setup_storage.py
```

## Step 4: Verify File Upload

Try uploading a file through your application. The error should now be resolved.

## Troubleshooting

### Error: "Unauthorized" or "RLS policy violation"
- Make sure the bucket is public OR RLS policies are correctly configured
- Verify the bucket name is exactly `Files`
- Check that your JWT tokens are valid

### Error: "Bucket not found"
- Ensure the bucket `Files` exists in your Supabase project
- Check the bucket name spelling

### Error: "Expected str, bytes or os.PathLike object"
- This is a backend code issue (now fixed)
- Make sure you've pulled the latest backend code

## Security Notes

- **Development:** Use public bucket for quick testing
- **Production:** Always use RLS policies with proper authentication
- **File Organization:** Files are stored as `{user_id}/{file_id}.enc`
- **Encryption:** All files are client-side encrypted before upload

## Next Steps

Once storage is configured:
1. Test file upload functionality
2. Test file download functionality  
3. Verify file deletion works
4. Check storage quota tracking
5. Set up monitoring and backups