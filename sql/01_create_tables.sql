-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    storage_used BIGINT DEFAULT 0,
    storage_limit BIGINT DEFAULT 5368709120, -- 5GB default
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    CONSTRAINT users_email_key UNIQUE (email),
    CONSTRAINT users_storage_check CHECK (storage_used >= 0 AND storage_used <= storage_limit)
);

-- Create files table
CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    encrypted_filename TEXT NOT NULL,
    encrypted_metadata JSONB NOT NULL,
    file_size BIGINT NOT NULL,
    storage_path TEXT NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMP WITH TIME ZONE,
    encryption_algorithm VARCHAR(50) DEFAULT 'AES-256-GCM',
    
    -- Indexes
    CONSTRAINT files_file_size_check CHECK (file_size > 0)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

CREATE INDEX IF NOT EXISTS idx_files_user_id ON files(user_id);
CREATE INDEX IF NOT EXISTS idx_files_uploaded_at ON files(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_files_is_deleted ON files(is_deleted);
CREATE INDEX IF NOT EXISTS idx_files_user_id_is_deleted ON files(user_id, is_deleted);
CREATE INDEX IF NOT EXISTS idx_files_file_size ON files(file_size);

-- Create a function to update storage usage when files are inserted/deleted
CREATE OR REPLACE FUNCTION update_user_storage()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Increase storage when file is inserted
        UPDATE users 
        SET storage_used = storage_used + NEW.file_size
        WHERE id = NEW.user_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        -- Decrease storage when file is permanently deleted
        UPDATE users 
        SET storage_used = storage_used - OLD.file_size
        WHERE id = OLD.user_id;
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        -- Handle soft delete (is_deleted changed from false to true)
        IF OLD.is_deleted = false AND NEW.is_deleted = true THEN
            -- Don't change storage_used for soft delete
            RETURN NEW;
        -- Handle restore (is_deleted changed from true to false)
        ELSIF OLD.is_deleted = true AND NEW.is_deleted = false THEN
            -- Don't change storage_used for restore
            RETURN NEW;
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for storage management
-- Note: We'll handle storage updates manually in the application for better control
-- DROP TRIGGER IF EXISTS trigger_update_storage ON files;
-- CREATE TRIGGER trigger_update_storage
--     AFTER INSERT OR DELETE ON files
--     FOR EACH ROW EXECUTE FUNCTION update_user_storage();

-- Create a function to clean up soft-deleted files older than 30 days
CREATE OR REPLACE FUNCTION cleanup_deleted_files()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM files 
    WHERE is_deleted = true 
    AND deleted_at < NOW() - INTERVAL '30 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create a view for active user files
CREATE OR REPLACE VIEW active_user_files AS
SELECT 
    f.*,
    u.email as user_email
FROM files f
JOIN users u ON f.user_id = u.id
WHERE f.is_deleted = false
AND u.is_active = true;