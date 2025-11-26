USE drms;

CREATE VIEW vw_pending_requests AS
SELECT r.requestID, u.name AS victimName, r.location, 
       r.typeOfNeed, r.urgencyLevel, r.priorityScore, 
       r.status, r.createdAt
FROM SOSRequest r
JOIN Victim v ON r.victimID = v.victimID
JOIN UserAccount u ON v.victimID = u.userID
WHERE r.status IN ('pending','in_process')
ORDER BY r.priorityScore DESC;

CREATE VIEW vw_resource_summary AS
SELECT rs.resourceID, rt.name AS resourceType,
       rs.quantity, rs.status, rs.location
FROM ResourceStock rs
JOIN ResourceType rt ON rs.resourceTypeID = rt.resourceTypeID;
