USE drms;
DELIMITER //

CREATE TRIGGER trg_after_insert_sos
AFTER INSERT ON SOSRequest
FOR EACH ROW
BEGIN
    DECLARE v_message TEXT;

    SET v_message = CONCAT('New SOS Request: ', NEW.typeOfNeed,
                           ' | Urgency: ', NEW.urgencyLevel,
                           ' | Location: ', COALESCE(NEW.location,'unknown'));

    INSERT INTO Notification (message, channel, recipientRole)
    VALUES (v_message, 'in_app', 'Admin'),
           (v_message, 'in_app', 'NGO'),
           (v_message, 'in_app', 'Volunteer');
END //
 
CREATE TRIGGER trg_after_update_resource
AFTER UPDATE ON ResourceStock
FOR EACH ROW
BEGIN
    IF NEW.quantity <= 5 AND OLD.quantity > 5 THEN
        INSERT INTO Notification (message, channel, recipientRole)
        VALUES (CONCAT('Low stock alert: ', NEW.resourceID, ' Qty: ', NEW.quantity),
                'in_app', 'NGO');
    END IF;
END //
DELIMITER ;
