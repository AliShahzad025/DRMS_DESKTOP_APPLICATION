USE drms;

-- Disable safe mode temporarily
SET SQL_SAFE_UPDATES = 0;


UPDATE UserAccount 
SET password_hash = 'password123'
WHERE userID IN (1,2,3,4,5,6,7,8,9,10,11,12);

SET SQL_SAFE_UPDATES = 1;

SELECT userID, name, email, role, password_hash AS password
FROM UserAccount
ORDER BY userID;
