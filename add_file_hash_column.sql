-- Add file_hash column to songs table if it doesn't exist
ALTER TABLE `songs` 
ADD COLUMN IF NOT EXISTS `file_hash` varchar(255) DEFAULT NULL,
ADD INDEX IF NOT EXISTS `file_hash_idx` (`file_hash`);

-- If your MySQL version doesn't support ADD COLUMN IF NOT EXISTS, use this instead:
-- ALTER TABLE `songs` ADD COLUMN `file_hash` varchar(255) DEFAULT NULL;
-- ALTER TABLE `songs` ADD INDEX `file_hash_idx` (`file_hash`); 