-- Fix for the missing is_instrumental column issue

-- Add is_instrumental column if it doesn't exist
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = DATABASE() AND table_name = 'songs' AND column_name = 'is_instrumental';

SET @add_column = IF(@col_exists = 0, 
    'ALTER TABLE songs ADD COLUMN is_instrumental BOOLEAN DEFAULT FALSE', 
    'SELECT "is_instrumental column already exists"');

PREPARE stmt FROM @add_column;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add file_path column with a default value if it doesn't exist (this field is used in save_song)
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = DATABASE() AND table_name = 'songs' AND column_name = 'file_path';

SET @add_file_path = IF(@col_exists = 0, 
    'ALTER TABLE songs ADD COLUMN file_path VARCHAR(255) NOT NULL DEFAULT ""', 
    'SELECT "file_path column already exists"');

PREPARE stmt FROM @add_file_path;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Update any rows that might have NULL in is_instrumental
UPDATE songs SET is_instrumental = FALSE WHERE is_instrumental IS NULL;

-- Update any rows that might have empty file_path
UPDATE songs SET file_path = CONCAT('/app/uploads/', filename) WHERE file_path = '';

-- Verify columns exist and report status
SELECT 
    (SELECT COUNT(*) FROM information_schema.columns 
     WHERE table_schema = DATABASE() AND table_name = 'songs' AND column_name = 'is_instrumental') as has_instrumental,
    (SELECT COUNT(*) FROM information_schema.columns 
     WHERE table_schema = DATABASE() AND table_name = 'songs' AND column_name = 'file_path') as has_file_path,
    'Fix applied successfully!' as message; 