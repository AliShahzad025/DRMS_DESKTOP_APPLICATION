-- Select the database
USE drms;

-- Disable foreign key checks temporarily to allow insertion of interdependent data
SET FOREIGN_KEY_CHECKS = 0;

-- 1. USER & ROLES
-- Note: UserAccount IDs (1-7, 8-12) will be used as foreign keys in role-specific tables.

INSERT INTO UserAccount (userID, name, email, phone, location, latitude, longitude, role, password_hash) VALUES
(1, 'Alice Johnson', 'alice@example.com', '+1234567890', 'Admin Office', 34.0522, -118.2437, 'Admin', '$2a$10$hash1...'),
(2, 'Bob''s Relief', 'bob.ngo@org.net', '+1122334455', 'Community Center A', 34.0530, -118.2450, 'NGO', '$2a$10$hash2...'),
(3, 'Carol Day', 'carol@volunteer.net', '+9988776655', 'Downtown Area', 34.0540, -118.2460, 'Volunteer', '$2a$10$hash3...'),
(4, 'David Smith', 'david@victim.com', '+1555666777', 'East Side Home', 34.0550, -118.2470, 'Victim', '$2a$10$hash4...'),
(5, 'Eve Green', 'eve@volunteer.net', '+9988776644', 'North Side', 34.0600, -118.2500, 'Volunteer', '$2a$10$hash5...'),
(6, 'Foster Care', 'foster@ngo.org', '+1444555666', 'Shelter B Hub', 34.0650, -118.2550, 'NGO', '$2a$10$hash6...'),
(7, 'Grace Lee', 'grace@victim.com', '+1333222111', 'South Side Apt', 34.0700, -118.2600, 'Victim', '$2a$10$hash7...'),
(8, 'Admin Two', 'admintwo@org.net', '+1112223333', 'Regional Office', 34.0000, -118.0000, 'Admin', '$2a$10$hash8...'),
(9, 'Admin Three', 'adminthree@org.net', '+1112224444', 'Field Office', 34.0100, -118.0100, 'Admin', '$2a$10$hash9...'),
(10, 'Helping Hands', 'helping@hands.org', '+1000111222', 'North Sector', 34.0200, -118.0200, 'NGO', '$2a$10$hash10...'),
(11, 'Vol One', 'volone@vol.com', '+1000333444', 'Volunteer Base 1', 34.0300, -118.0300, 'Volunteer', '$2a$10$hash11...'),
(12, 'Victim Two', 'victwo@vic.com', '+1000555666', 'Bridge Street', 34.0400, -118.0400, 'Victim', '$2a$10$hash12...');

-- Reset AUTO_INCREMENT to ensure future inserts (if any) start after the manually set IDs
ALTER TABLE UserAccount AUTO_INCREMENT = 13;

-- Admin
INSERT INTO Admin (adminID, office) VALUES
(1, 'Central Disaster Mgmt'),
(8, 'Regional Ops Center'),
(9, 'Field Command Post');

-- NGO
INSERT INTO NGO (ngoID, orgName, verified, registration_doc, region, contact_person) VALUES
(2, 'Bob''s Relief Effort', TRUE, 'doc_br001.pdf', 'Metro Region', 'Bob K.'),
(6, 'Foster Care Alliance', TRUE, 'doc_fc002.pdf', 'South West Zone', 'Maria L.'),
(10, 'Helping Hands', FALSE, 'doc_hh003.pdf', 'North Sector', 'Peter J.');

-- Volunteer
INSERT INTO Volunteer (volunteerID, roles, verified, status, last_active) VALUES
(3, 'Medical, Transport', TRUE, 'available', '2025-11-19 12:00:00'),
(5, 'Search & Rescue', TRUE, 'busy', '2025-11-19 12:45:00'),
(11, 'General Support', FALSE, 'available', '2025-11-18 10:00:00');

-- Victim
INSERT INTO Victim (victimID, verified_contact, vulnerability_notes) VALUES
(4, TRUE, 'elderly, needs medication'),
(7, FALSE, 'single mother, 2 children'),
(12, TRUE, 'injured leg, no shelter');


-- 2. ZONES & SHELTERS

-- PriorityZone
INSERT INTO PriorityZone (name, description, centerLat, centerLong, radius_km, priority_level) VALUES
('Flood Risk Area', 'Low-lying residential zone', 34.0600, -118.2500, 5.50, 'high'),
('Hillside Evacuation', 'Area prone to landslides', 34.1000, -118.3000, 3.00, 'medium'),
('Commercial District', 'Moderate impact, mainly property damage', 34.0400, -118.2300, 2.50, 'low');

-- Shelter
INSERT INTO Shelter (name, latitude, longitude, capacity, current_occupancy, contact) VALUES
('Central High School', 34.0500, -118.2400, 500, 450, 'shelter1@contact.org'),
('Park Community Hall', 34.0650, -118.2600, 150, 80, '+1-800-SHELTER'),
('Old Library Annex', 34.0450, -118.2250, 75, 75, 'annexe@shelter.net');


-- 3. SOS REQUESTS

INSERT INTO SOSRequest (requestID, victimID, location, latitude, longitude, typeOfNeed, description, urgencyLevel, status, assignedVolunteerID, assignedNGO) VALUES
(1, 4, 'East Side Home', 34.0550, -118.2470, 'Medical', 'Needs insulin urgently', 'critical', 'assigned', 3, 2),
(2, 7, 'South Side Apt', 34.0700, -118.2600, 'Food', 'Basic food/water for family', 'high', 'in_process', 5, 6),
(3, 12, 'Near Bridge St', 34.0400, -118.2300, 'Rescue', 'Trapped in debris, injured leg', 'critical', 'pending', NULL, NULL),
(4, 12, 'Bridge St Shelter', 34.0400, -118.0400, 'Shelter', 'Need immediate shelter access', 'medium', 'pending', NULL, NULL);

-- Reset AUTO_INCREMENT
ALTER TABLE SOSRequest AUTO_INCREMENT = 5;


-- 4. RESOURCE MANAGEMENT

-- ResourceType
INSERT INTO ResourceType (resourceTypeID, name, unit, description) VALUES
(1, 'Bottled Water', 'bottle', 'Clean drinking water'),
(2, 'Blanket', 'unit', 'Thermal blankets for warmth'),
(3, 'First Aid Kit', 'kit', 'Standard emergency medical kit');

-- ResourceStock
INSERT INTO ResourceStock (resourceID, resourceTypeID, donorNGO, quantity, status, lastVerifiedBy, location, latitude, longitude) VALUES
(1, 1, 2, 500, 'available', 1, 'Warehouse A', 34.0500, -118.2000),
(2, 2, 6, 150, 'reserved', 8, 'Shelter 2 Storage', 34.0650, -118.2600),
(3, 3, 2, 10, 'low', 1, 'Mobile Unit 1', 34.0550, -118.2470);

-- ResourceAdd
INSERT INTO ResourceAdd (resourceID, addedBy, quantity, note) VALUES
(1, 2, 200, 'Initial stock'),
(2, 10, 50, 'New donation'),
(1, 6, 300, 'Transfer from another branch');

-- ResourceUpdate
INSERT INTO ResourceUpdate (resourceID, updatedBy, previousQuantity, newQuantity, note) VALUES
(1, 1, 550, 500, 'Allocation for Request 1'),
(3, 8, 20, 10, 'Used in field operations'),
(2, 6, 100, 150, 'Quantity verification');

-- ResourceTransfer
INSERT INTO ResourceTransfer (resourceID, fromNGO, toNGO, fromLocation, toLocation, quantity, status, transferredBy) VALUES
(1, 2, 6, 'Warehouse A', 'Shelter 2', 50, 'completed', 8),
(3, 2, 10, 'Warehouse A', 'North Sector Hub', 5, 'pending', 1),
(2, 6, 2, 'Shelter 2', 'Warehouse A', 100, 'in_transit', 9);

-- ResourceAllocation
INSERT INTO ResourceAllocation (resourceID, allocatedToType, allocatedToID, requestID, quantity, allocationStatus) VALUES
(1, 'Victim', 4, 1, 5, 'delivered'),
(2, 'Shelter', 1, NULL, 100, 'sent'),
(3, 'Volunteer', 3, 1, 1, 'pending');


-- 5. TASKS

-- Task
INSERT INTO Task (taskID, title, description, taskType, status, assignedVolunteerID, createdBy, relatedRequestID) VALUES
(1, 'Deliver Insulin', 'Deliver insulin to David Smith', 'delivery', 'completed', 3, 1, 1),
(2, 'Water & Food Drop', 'Deliver supplies to Grace Lee', 'delivery', 'in_progress', 5, 8, 2),
(3, 'Structural Assessment', 'Assess damage at Zone 1', 'assessment', 'unassigned', NULL, 1, NULL);

-- TaskHistory
INSERT INTO TaskHistory (taskID, volunteerID, previousStatus, newStatus, note) VALUES
(1, 3, 'unassigned', 'assigned', 'Volunteer accepted'),
(2, 5, 'unassigned', 'in_progress', 'On the way to location'),
(1, 3, 'assigned', 'completed', 'Delivery confirmed by victim');


-- 6. NOTIFICATIONS

-- Notification
INSERT INTO Notification (message, channel, recipientUserID, recipientRole, status) VALUES
('New critical SOS request assigned.', 'in_app', 3, 'Volunteer', 'read'),
('Resource stock for Water is low.', 'email', 1, 'Admin', 'sent'),
('Your food request is in process.', 'sms', 7, 'Victim', 'delivered');


-- 7. REPORTING & AUDIT

-- Report
INSERT INTO Report (reportID, reportType, parameters, generatedBy, filePath) VALUES
(1, 'SOS Summary', '{"startDate": "2025-11-01", "endDate": "2025-11-30"}', 1, '/reports/sos_nov.pdf'),
(2, 'Inventory Check', '{"resourceTypeID": 1, "status": "low"}', 8, '/reports/water_low.csv'),
(3, 'Volunteer Activity', '{"volunteerID": 3, "period": "week"}', 1, '/reports/vol_3_wk.json');

-- AuditLog
INSERT INTO AuditLog (actorUserID, action, targetTable, targetID, details) VALUES
(1, 'UPDATE', 'SOSRequest', '1', '{"oldStatus": "pending", "newStatus": "assigned"}'),
(3, 'READ', 'SOSRequest', '1', '{"access": "granted"}'),
(2, 'INSERT', 'ResourceStock', '1', '{"resourceTypeID": 1, "quantity": 200}');


-- 8. FEEDBACK

-- Feedback
INSERT INTO Feedback (requestID, victimID, rating, comments) VALUES
(1, 4, 5, 'Very fast and courteous delivery!'),
(2, 7, 4, 'Supplies were exactly what we needed.'),
(4, 12, 3, 'Volunteer took a long time to arrive.');


-- 9. URGENCY WEIGHT

-- UrgencyWeight
INSERT INTO UrgencyWeight (urgencyLevel, weight) VALUES
('low', 10),
('medium', 30),
('high', 60),
('critical', 100);


-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- Confirmation query to show the number of rows in UserAccount
SELECT 'Data Insertion Complete' AS Status, COUNT(*) AS TotalUsers FROM UserAccount;