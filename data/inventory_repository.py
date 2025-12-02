from .base_repository import BaseRepository

class InventoryRepository(BaseRepository):

    def create(self, item_name, quantity, category, camp_id):
        query = """
            INSERT INTO inventory (item_name, quantity, category, camp_id)
            VALUES (%s, %s, %s, %s)
        """
        self.execute(query, (item_name, quantity, category, camp_id))
        return True

    def get_by_id(self, item_id):
        query = "SELECT * FROM inventory WHERE id = %s"
        return self.fetch_one(query, (item_id,))

    def get_all(self):
        return self.fetch_all("SELECT * FROM inventory")

    def get_by_camp(self, camp_id):
        query = "SELECT * FROM inventory WHERE camp_id = %s"
        return self.fetch_all(query, (camp_id,))

    def update(self, item_id, **fields):
        query = """
            UPDATE inventory
            SET 
                item_name = COALESCE(%s, item_name),
                quantity = COALESCE(%s, quantity),
                category = COALESCE(%s, category),
                camp_id = COALESCE(%s, camp_id)
            WHERE id = %s
        """
        values = (
            fields.get("item_name"),
            fields.get("quantity"),
            fields.get("category"),
            fields.get("camp_id"),
            item_id
        )
        self.execute(query, values)
        return True

    def delete(self, item_id):
        query = "DELETE FROM inventory WHERE id = %s"
        self.execute(query, (item_id,))
        return True
