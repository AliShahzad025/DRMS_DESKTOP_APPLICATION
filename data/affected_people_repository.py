from .base_repository import BaseRepository

class AffectedPeopleRepository(BaseRepository):

    def create(self, disaster_id, name, age, gender, injury_status, aid_required):
        query = """
            INSERT INTO affected_people (disaster_id, name, age, gender, injury_status, aid_required)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.execute(query, (disaster_id, name, age, gender, injury_status, aid_required))
        return True

    def get_by_id(self, person_id):
        query = "SELECT * FROM affected_people WHERE id = %s"
        return self.fetch_one(query, (person_id,))

    def get_all(self):
        return self.fetch_all("SELECT * FROM affected_people")

    def get_by_disaster(self, disaster_id):
        query = "SELECT * FROM affected_people WHERE disaster_id = %s"
        return self.fetch_all(query, (disaster_id,))

    def update(self, person_id, **fields):
        query = """
            UPDATE affected_people
            SET
                disaster_id = COALESCE(%s, disaster_id),
                name = COALESCE(%s, name),
                age = COALESCE(%s, age),
                gender = COALESCE(%s, gender),
                injury_status = COALESCE(%s, injury_status),
                aid_required = COALESCE(%s, aid_required)
            WHERE id = %s
        """
        values = (
            fields.get("disaster_id"),
            fields.get("name"),
            fields.get("age"),
            fields.get("gender"),
            fields.get("injury_status"),
            fields.get("aid_required"),
            person_id
        )
        self.execute(query, values)
        return True

    def delete(self, person_id):
        query = "DELETE FROM affected_people WHERE id = %s"
        self.execute(query, (person_id,))
        return True
