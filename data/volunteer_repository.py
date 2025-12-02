from .base_repository import BaseRepository

class VolunteerRepository(BaseRepository):

    def create(self, name, phone, skills, availability, location):
        query = """
            INSERT INTO volunteers (name, phone, skills, availability, location)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.execute(query, (name, phone, skills, availability, location))
        return True

    def get_by_id(self, volunteer_id):
        query = "SELECT * FROM volunteers WHERE id = %s"
        return self.fetch_one(query, (volunteer_id,))

    def get_all(self):
        return self.fetch_all("SELECT * FROM volunteers")

    def update(self, volunteer_id, **fields):
        query = """
            UPDATE volunteers
            SET 
                name = COALESCE(%s, name),
                phone = COALESCE(%s, phone),
                skills = COALESCE(%s, skills),
                availability = COALESCE(%s, availability),
                location = COALESCE(%s, location)
            WHERE id = %s
        """
        values = (
            fields.get("name"),
            fields.get("phone"),
            fields.get("skills"),
            fields.get("availability"),
            fields.get("location"),
            volunteer_id
        )
        self.execute(query, values)
        return True

    def delete(self, volunteer_id):
        query = "DELETE FROM volunteers WHERE id = %s"
        self.execute(query, (volunteer_id,))
        return True
