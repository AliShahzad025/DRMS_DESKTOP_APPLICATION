from .base_repository import BaseRepository

class DisasterRepository(BaseRepository):

    def create(self, name, type, location, severity, status):
        query = """
            INSERT INTO disasters (name, type, location, severity, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.execute(query, (name, type, location, severity, status))
        return True

    def get_by_id(self, disaster_id):
        query = "SELECT * FROM disasters WHERE id = %s"
        return self.fetch_one(query, (disaster_id,))

    def get_all(self):
        return self.fetch_all("SELECT * FROM disasters")

    def update(self, disaster_id, name=None, type=None, location=None, severity=None, status=None):
        query = """
            UPDATE disasters
            SET name = COALESCE(%s, name),
                type = COALESCE(%s, type),
                location = COALESCE(%s, location),
                severity = COALESCE(%s, severity),
                status = COALESCE(%s, status)
            WHERE id = %s
        """
        self.execute(query, (name, type, location, severity, status, disaster_id))
        return True

    def delete(self, disaster_id):
        query = "DELETE FROM disasters WHERE id = %s"
        self.execute(query, (disaster_id,))
        return True
