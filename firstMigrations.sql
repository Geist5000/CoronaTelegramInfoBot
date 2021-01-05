-- SQLite
ALTER TABLE `activeUsers` ADD region_type VARCHAR(20);
ALTER TABLE `activeUsers` ADD region_name VARCHAR(40);
UPDATE `activeUsers` SET `region_type`='Stadtkreis', `region_name`='Wilhelmshaven';