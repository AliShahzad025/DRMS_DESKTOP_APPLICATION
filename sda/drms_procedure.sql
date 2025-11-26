USE drms;

DELIMITER //
CREATE PROCEDURE compute_priorities()
BEGIN
    UPDATE SOSRequest r
    JOIN UrgencyWeight u ON r.urgencyLevel = u.urgencyLevel
    SET r.priorityScore =
        (u.weight * 100)
        + GREATEST(0, TIMESTAMPDIFF(MINUTE, r.createdAt, NOW()) DIV 30);
END //
DELIMITER ;

CALL compute_priorities();
