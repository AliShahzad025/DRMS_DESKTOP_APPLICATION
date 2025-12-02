from .base_repository import BaseRepository

class ReliefCampRepository(BaseRepository):

    def create(self, name, location, capacity, incharge_name, contact):
        query = """
            INSERT INTO relief_camps (name, location, capacity, incharge_name, contact)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.execute(query, (name, location, capacity, incharge_name, contact))
        return True

    def get_by_id(self, camp_id):
        query = "SELECT * FROM relief_camps WHERE id = %s"
        return self.fetch_one(query, (camp_id,))

    def get_all(self):
        return self.fetch_all("SELECT * FROM relief_camps")

    def update(self, camp_id, **fields):
        query = """
            UPDATE relief_camps
            SET 
                name = COALESCE(%s, name),
                location = COALESCE(%s, location),
                capacity = COALESCE(%s, capacity),
                incharge_name = COALESCE(%s, incharge_name),
                contact = COALESCE(%s, contact)
            WHERE id = %s
        """
        values = (
            fields.get("name"),
            fields.get("location"),
            fields.get("capacity"),
            fields.get("incharge_name"),
            fields.get("contact"),
            camp_id
        )
        self.execute(query, values)
        return True

    def delete(self, camp_id):
        query = "DELETE FROM relief_camps WHERE id = %s"
        self.execute(query, (camp_id,))
        return True
