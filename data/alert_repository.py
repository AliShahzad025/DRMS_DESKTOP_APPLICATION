from .base_repository import BaseRepository

class AlertRepository(BaseRepository):

    def create(self, message, severity, location):
        query = """
            INSERT INTO alerts (message, severity, location)
            VALUES (%s, %s, %s)
        """
        self.execute(query, (message, severity, location))
        return True

    def get_by_id(self, alert_id):
        query = "SELECT * FROM alerts WHERE id = %s"
        return self.fetch_one(query, (alert_id,))

    def get_all(self):
        return self.fetch_all("SELECT * FROM alerts")

    def update(self, alert_id, **fields):
        query = """
            UPDATE alerts
            SET 
                message = COALESCE(%s, message),
                severity = COALESCE(%s, severity),
                location = COALESCE(%s, location)
            WHERE id = %s
        """
        values = (
            fields.get("message"),
            fields.get("severity"),
            fields.get("location"),
            alert_id
        )
        self.execute(query, values)
        return True

    def delete(self, alert_id):
        query = "DELETE FROM alerts WHERE id = %s"
        self.execute(query, (alert_id,))
        return True
