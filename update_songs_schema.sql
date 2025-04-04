-- Update songs table to add missing columns
-- Execute this with: docker-compose exec db mysql -uroot -proot music_analyzer < update_songs_schema.sql

-- Add filename column if it doesn't exist
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = 'music_analyzer' AND table_name = 'songs' AND column_name = 'filename';

SET @add_filename = IF(@col_exists = 0, 
    'ALTER TABLE songs ADD COLUMN filename VARCHAR(255) NOT NULL DEFAULT ""', 
    'SELECT "filename column already exists"');
PREPARE stmt FROM @add_filename;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add original_name column if it doesn't exist
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = 'music_analyzer' AND table_name = 'songs' AND column_name = 'original_name';

SET @add_original_name = IF(@col_exists = 0, 
    'ALTER TABLE songs ADD COLUMN original_name VARCHAR(255) NOT NULL DEFAULT ""', 
    'SELECT "original_name column already exists"');
PREPARE stmt FROM @add_original_name;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add is_instrumental column if it doesn't exist
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = 'music_analyzer' AND table_name = 'songs' AND column_name = 'is_instrumental';

SET @add_is_instrumental = IF(@col_exists = 0, 
    'ALTER TABLE songs ADD COLUMN is_instrumental BOOLEAN DEFAULT FALSE', 
    'SELECT "is_instrumental column already exists"');
PREPARE stmt FROM @add_is_instrumental;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add analysis_json column if it doesn't exist
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = 'music_analyzer' AND table_name = 'songs' AND column_name = 'analysis_json';

SET @add_analysis_json = IF(@col_exists = 0, 
    'ALTER TABLE songs ADD COLUMN analysis_json LONGTEXT', 
    'SELECT "analysis_json column already exists"');
PREPARE stmt FROM @add_analysis_json;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Ensure file_hash has UNIQUE constraint
SELECT COUNT(*) INTO @index_exists FROM information_schema.statistics
WHERE table_schema = 'music_analyzer' AND table_name = 'songs' AND index_name = 'file_hash' AND non_unique = 0;

SET @add_unique = IF(@index_exists = 0, 
    'ALTER TABLE songs ADD UNIQUE KEY file_hash (file_hash)', 
    'SELECT "file_hash already has UNIQUE constraint"');
PREPARE stmt FROM @add_unique;
EXECUTE stmt;
DEALLOCATE PREPARE stmt; 