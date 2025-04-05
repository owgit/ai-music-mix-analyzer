-- Fix for the title column issue

-- Check if title column exists and add default value if needed
SELECT COUNT(*) INTO @col_exists FROM information_schema.columns 
WHERE table_schema = DATABASE() AND table_name = 'songs' AND column_name = 'title';

-- If title exists, update it to have default value
SET @modify_title = IF(@col_exists > 0, 
    'ALTER TABLE songs MODIFY COLUMN title VARCHAR(255) NOT NULL DEFAULT ""', 
    'SELECT "title column does not exist - no modification needed"');

PREPARE stmt FROM @modify_title;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- If the title column doesn't exist, create it with a default value
SET @add_title = IF(@col_exists = 0, 
    'ALTER TABLE songs ADD COLUMN title VARCHAR(255) NOT NULL DEFAULT ""', 
    'SELECT "title column already exists"');

PREPARE stmt FROM @add_title;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Update empty title values with original_name or filename if available
UPDATE songs SET title = original_name WHERE title = '' AND original_name != '';
UPDATE songs SET title = filename WHERE title = '' AND filename != '' AND original_name = '';

-- Update filename and original_name from title if they are empty
UPDATE songs SET filename = title WHERE filename = '' AND title != '';
UPDATE songs SET original_name = title WHERE original_name = '' AND title != '';

-- Done
SELECT 'Title column fix completed successfully!' as message; 