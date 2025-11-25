USE drms;

CREATE INDEX idx_user_role ON UserAccount(role);
CREATE INDEX idx_user_location ON UserAccount(latitude, longitude);

CREATE INDEX idx_ngo_verified ON NGO(verified);

CREATE INDEX idx_volunteer_status ON Volunteer(status);

CREATE INDEX idx_sos_status ON SOSRequest(status);
CREATE INDEX idx_sos_urgency ON SOSRequest(urgencyLevel);
CREATE INDEX idx_sos_priority ON SOSRequest(priorityScore DESC);

CREATE INDEX idx_resource_type ON ResourceStock(resourceTypeID);
CREATE INDEX idx_resource_status ON ResourceStock(status);

CREATE INDEX idx_task_status ON Task(status);

CREATE INDEX idx_notification_recipient ON Notification(recipientUserID);
