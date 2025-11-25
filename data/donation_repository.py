from .base_repository import BaseRepository

class DonationRepository(BaseRepository):

    def create(self, donor_name, amount, donation_type, note):
        query = """
            INSERT INTO donations (donor_name, amount, donation_type, note)
            VALUES (%s, %s, %s, %s)
        """
        self.execute(query, (donor_name, amount, donation_type, note))
        return True

    def get_by_id(self, donation_id):
        query = "SELECT * FROM donations WHERE id = %s"
        return self.fetch_one(query, (donation_id,))

    def get_all(self):
        return self.fetch_all("SELECT * FROM donations")

    def update(self, donation_id, **fields):
        query = """
            UPDATE donations
            SET 
                donor_name = COALESCE(%s, donor_name),
                amount = COALESCE(%s, amount),
                donation_type = COALESCE(%s, donation_type),
                note = COALESCE(%s, note)
            WHERE id = %s
        """
        values = (
            fields.get("donor_name"),
            fields.get("amount"),
            fields.get("donation_type"),
            fields.get("note"),
            donation_id
        )
        self.execute(query, values)
        return True

    def delete(self, donation_id):
        query = "DELETE FROM donations WHERE id = %s"
        self.execute(query, (donation_id,))
        return True
