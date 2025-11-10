"""
Temporary RLS Disable Guide for Storage

Since the RLS policies are causing issues, here's how to temporarily disable them
for development purposes:

1. Go to Supabase Dashboard: https://supabase.com/dashboard
2. Go to your project: nkfrqmduneknfmyqotpb
3. Navigate to "SQL Editor" in the left sidebar
4. Run this SQL command to disable RLS on storage.objects:

```sql
ALTER TABLE storage.objects DISABLE ROW LEVEL SECURITY;
```

This will temporarily disable all RLS policies on the storage.objects table,
allowing your file uploads to work.

IMPORTANT: This is for development only!
For production, you should properly configure RLS policies with authentication.

To re-enable RLS later (for production):
```sql
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;
```

Then set up proper policies that work with your authentication system.
"""

def show_rls_disable_instructions():
    print("🔧 Temporary Fix: Disable Storage RLS")
    print("=" * 50)
    print("The storage upload is failing due to RLS policies.")
    print("Here's a temporary fix for development:")
    print()
    print("1. Go to Supabase Dashboard SQL Editor")
    print("2. Run this command:")
    print()
    print("   ALTER TABLE storage.objects DISABLE ROW LEVEL SECURITY;")
    print()
    print("⚠️  WARNING: This disables security for development only!")
    print("   For production, configure proper RLS policies.")
    print()
    print("After running this, try your file upload again.")

if __name__ == "__main__":
    show_rls_disable_instructions()