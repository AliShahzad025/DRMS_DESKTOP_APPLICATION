USE drms;

-- 1. USER & ROLES
CREATE TABLE UserAccount (
    userID INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE,
    phone VARCHAR(30),
    location VARCHAR(255),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    language VARCHAR(10) DEFAULT 'en',
    role ENUM('Admin','NGO','Volunteer','Victim') NOT NULL,
    password_hash VARCHAR(255),
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE Admin (
    adminID INT PRIMARY KEY,
    office VARCHAR(150),
    FOREIGN KEY (adminID) REFERENCES UserAccount(userID) ON DELETE CASCADE
);

CREATE TABLE NGO (
    ngoID INT PRIMARY KEY,
    orgName VARCHAR(200) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    registration_doc VARCHAR(255),
    region VARCHAR(150),
    contact_person VARCHAR(150),
    FOREIGN KEY (ngoID) REFERENCES UserAccount(userID) ON DELETE CASCADE
);

CREATE TABLE Volunteer (
    volunteerID INT PRIMARY KEY,
    roles VARCHAR(200),
    verified BOOLEAN DEFAULT FALSE,
    status ENUM('available','busy','inactive') DEFAULT 'available',
    last_active DATETIME,
    FOREIGN KEY (volunteerID) REFERENCES UserAccount(userID) ON DELETE CASCADE
);

CREATE TABLE Victim (
    victimID INT PRIMARY KEY,
    verified_contact BOOLEAN DEFAULT FALSE,
    vulnerability_notes TEXT,
    FOREIGN KEY (victimID) REFERENCES UserAccount(userID) ON DELETE CASCADE
);

-- 2. ZONES & SHELTERS
CREATE TABLE PriorityZone (
    zoneID INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150),
    description TEXT,
    centerLat DECIMAL(10,7),
    centerLong DECIMAL(10,7),
    radius_km DECIMAL(6,2),
    priority_level ENUM('low','medium','high') DEFAULT 'medium'
);

CREATE TABLE Shelter (
    shelterID INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    capacity INT DEFAULT 0,
    current_occupancy INT DEFAULT 0,
    contact VARCHAR(100)
);

-- 3. SOS REQUESTS
CREATE TABLE SOSRequest (
    requestID INT AUTO_INCREMENT PRIMARY KEY,
    victimID INT NOT NULL,
    location VARCHAR(255),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    typeOfNeed VARCHAR(100),
    description TEXT,
    urgencyLevel ENUM('low','medium','high','critical') DEFAULT 'low',
    status ENUM('pending','in_process','assigned','delivered','cancelled') DEFAULT 'pending',
    priorityScore INT DEFAULT 0,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    assignedVolunteerID INT,
    assignedNGO INT,
    FOREIGN KEY (victimID) REFERENCES Victim(victimID) ON DELETE CASCADE,
    FOREIGN KEY (assignedVolunteerID) REFERENCES Volunteer(volunteerID) ON DELETE SET NULL,
    FOREIGN KEY (assignedNGO) REFERENCES NGO(ngoID) ON DELETE SET NULL
);

-- 4. RESOURCE MANAGEMENT
CREATE TABLE ResourceType (
    resourceTypeID INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    unit VARCHAR(50) DEFAULT 'unit',
    description TEXT
);

CREATE TABLE ResourceStock (
    resourceID INT AUTO_INCREMENT PRIMARY KEY,
    resourceTypeID INT NOT NULL,
    donorNGO INT,
    quantity INT NOT NULL DEFAULT 0,
    status ENUM('available','reserved','low','out_of_stock') DEFAULT 'available',
    lastVerifiedBy INT,
    lastUpdated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    location VARCHAR(255),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    FOREIGN KEY (resourceTypeID) REFERENCES ResourceType(resourceTypeID) ON DELETE CASCADE,
    FOREIGN KEY (donorNGO) REFERENCES NGO(ngoID) ON DELETE SET NULL,
    FOREIGN KEY (lastVerifiedBy) REFERENCES Admin(adminID) ON DELETE SET NULL
);

CREATE TABLE ResourceAdd (
    addID INT AUTO_INCREMENT PRIMARY KEY,
    resourceID INT NOT NULL,
    addedBy INT,
    quantity INT NOT NULL,
    note VARCHAR(255),
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resourceID) REFERENCES ResourceStock(resourceID) ON DELETE CASCADE
);

CREATE TABLE ResourceUpdate (
    updateID INT AUTO_INCREMENT PRIMARY KEY,
    resourceID INT NOT NULL,
    updatedBy INT,
    previousQuantity INT,
    newQuantity INT,
    note VARCHAR(255),
    dateUpdated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resourceID) REFERENCES ResourceStock(resourceID) ON DELETE CASCADE
);

CREATE TABLE ResourceTransfer (
    transferID INT AUTO_INCREMENT PRIMARY KEY,
    resourceID INT NOT NULL,
    fromNGO INT,
    toNGO INT,
    fromLocation VARCHAR(255),
    toLocation VARCHAR(255),
    quantity INT NOT NULL,
    transferDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending','in_transit','completed','cancelled') DEFAULT 'pending',
    transferredBy INT,
    FOREIGN KEY (resourceID) REFERENCES ResourceStock(resourceID) ON DELETE CASCADE,
    FOREIGN KEY (fromNGO) REFERENCES NGO(ngoID) ON DELETE SET NULL,
    FOREIGN KEY (toNGO) REFERENCES NGO(ngoID) ON DELETE SET NULL
);

CREATE TABLE ResourceAllocation (
    allocationID INT AUTO_INCREMENT PRIMARY KEY,
    resourceID INT NOT NULL,
    allocatedToType ENUM('Volunteer','NGO','Victim','Shelter') NOT NULL,
    allocatedToID INT,
    requestID INT,
    quantity INT NOT NULL,
    allocationDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    allocationStatus ENUM('pending','sent','delivered','cancelled') DEFAULT 'pending',
    FOREIGN KEY (resourceID) REFERENCES ResourceStock(resourceID) ON DELETE CASCADE,
    FOREIGN KEY (requestID) REFERENCES SOSRequest(requestID) ON DELETE SET NULL
);

-- 5. TASKS
CREATE TABLE Task (
    taskID INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    taskType ENUM('delivery','rescue','medical','assessment','other') DEFAULT 'other',
    status ENUM('unassigned','assigned','in_progress','completed','cancelled') DEFAULT 'unassigned',
    assignedVolunteerID INT,
    createdBy INT,
    relatedRequestID INT,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (assignedVolunteerID) REFERENCES Volunteer(volunteerID),
    FOREIGN KEY (relatedRequestID) REFERENCES SOSRequest(requestID)
);

CREATE TABLE TaskHistory (
    historyID INT AUTO_INCREMENT PRIMARY KEY,
    taskID INT NOT NULL,
    volunteerID INT,
    previousStatus VARCHAR(50),
    newStatus VARCHAR(50),
    note VARCHAR(255),
    updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (taskID) REFERENCES Task(taskID) ON DELETE CASCADE
);

-- 6. NOTIFICATIONS
CREATE TABLE Notification (
    notificationID INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT NOT NULL,
    channel ENUM('in_app','email','sms') DEFAULT 'in_app',
    recipientUserID INT,
    recipientRole ENUM('Admin','NGO','Volunteer','Victim'),
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    deliveredAt DATETIME,
    status ENUM('pending','sent','delivered','read','failed') DEFAULT 'pending',
    meta JSON,
    FOREIGN KEY (recipientUserID) REFERENCES UserAccount(userID)
);

-- 7. REPORTING & AUDIT
CREATE TABLE Report (
    reportID INT AUTO_INCREMENT PRIMARY KEY,
    reportType VARCHAR(100),
    parameters JSON,
    generatedBy INT,
    generatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    filePath VARCHAR(255)
);

CREATE TABLE AuditLog (
    logID INT AUTO_INCREMENT PRIMARY KEY,
    actorUserID INT,
    action VARCHAR(150),
    targetTable VARCHAR(100),
    targetID VARCHAR(50),
    details JSON,
    loggedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (actorUserID) REFERENCES UserAccount(userID)
);

-- 8. FEEDBACK
CREATE TABLE Feedback (
    feedbackID INT AUTO_INCREMENT PRIMARY KEY,
    requestID INT,
    victimID INT,
    rating TINYINT,
    comments TEXT,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requestID) REFERENCES SOSRequest(requestID),
    FOREIGN KEY (victimID) REFERENCES Victim(victimID)
);

-- 9. URGENCY WEIGHT
CREATE TABLE UrgencyWeight (
    urgencyLevel ENUM('low','medium','high','critical') PRIMARY KEY,
    weight INT NOT NULL
);
