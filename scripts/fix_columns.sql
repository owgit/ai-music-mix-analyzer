-- Fix columns script for Music Mix Analyzer
-- Adds missing required columns to the songs table

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

-- Add analysis_json column if it doesn't exist
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = 'music_analyzer' AND table_name = 'songs' AND column_name = 'analysis_json';

SET @add_analysis_json = IF(@col_exists = 0, 
    'ALTER TABLE songs ADD COLUMN analysis_json LONGTEXT NULL', 
    'SELECT "analysis_json column already exists"');
PREPARE stmt FROM @add_analysis_json;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Migrate data from title column if needed
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = 'music_analyzer' AND table_name = 'songs' AND column_name = 'title';

SET @migrate_title = IF(@col_exists > 0, 
    'UPDATE songs SET filename = title WHERE title IS NOT NULL AND (filename IS NULL OR filename = "")', 
    'SELECT "No title column to migrate from"');
PREPARE stmt FROM @migrate_title;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @migrate_title2 = IF(@col_exists > 0, 
    'UPDATE songs SET original_name = title WHERE title IS NOT NULL AND (original_name IS NULL OR original_name = "")', 
    'SELECT "No title column to migrate from"');
PREPARE stmt FROM @migrate_title2;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Migrate data from analysis_data column if needed
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = 'music_analyzer' AND table_name = 'songs' AND column_name = 'analysis_data';

SET @migrate_analysis = IF(@col_exists > 0, 
    'UPDATE songs SET analysis_json = analysis_data WHERE analysis_data IS NOT NULL AND analysis_json IS NULL', 
    'SELECT "No analysis_data column to migrate from"');
PREPARE stmt FROM @migrate_analysis;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Done
SELECT 'Schema fix completed successfully!' as message; 