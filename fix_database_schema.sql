-- Fix database schema for Music Mix Analyzer
-- This script adds missing columns required for the application to work

-- Check and add the filename column if it doesn't exist
SET @column_exists = 0;
SELECT COUNT(*) INTO @column_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'music_analyzer' 
AND TABLE_NAME = 'songs' 
AND COLUMN_NAME = 'filename';

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE songs ADD COLUMN filename VARCHAR(255) NOT NULL DEFAULT "unknown_filename"',
    'SELECT "filename column already exists"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Check and add the original_name column if it doesn't exist
SET @column_exists = 0;
SELECT COUNT(*) INTO @column_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'music_analyzer' 
AND TABLE_NAME = 'songs' 
AND COLUMN_NAME = 'original_name';

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE songs ADD COLUMN original_name VARCHAR(255) NOT NULL DEFAULT "unknown_original_name"',
    'SELECT "original_name column already exists"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Check and add the analysis_json column if it doesn't exist
SET @column_exists = 0;
SELECT COUNT(*) INTO @column_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'music_analyzer' 
AND TABLE_NAME = 'songs' 
AND COLUMN_NAME = 'analysis_json';

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE songs ADD COLUMN analysis_json LONGTEXT NULL',
    'SELECT "analysis_json column already exists"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Check and add the file_hash column if it doesn't exist
SET @column_exists = 0;
SELECT COUNT(*) INTO @column_exists 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'music_analyzer' 
AND TABLE_NAME = 'songs' 
AND COLUMN_NAME = 'file_hash';

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE songs ADD COLUMN file_hash VARCHAR(64) NULL, ADD INDEX(file_hash)',
    'SELECT "file_hash column already exists"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Confirm the schema after changes
DESCRIBE songs; 