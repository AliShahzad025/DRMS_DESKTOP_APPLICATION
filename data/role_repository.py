from .base_repository import BaseRepository

class RoleRepository(BaseRepository):
    """
    Repository for roles table
    """

    def create(self, name):
        query = "INSERT INTO roles (name) VALUES (%s)"
        self.execute(query, (name,))
        return True

    def get_by_id(self, role_id):
        query = "SELECT * FROM roles WHERE id = %s"
        return self.fetch_one(query, (role_id,))

    def get_all(self):
        query = "SELECT * FROM roles"
        return self.fetch_all(query)

    def update(self, role_id, name=None):
        query = """
            UPDATE roles
            SET name = COALESCE(%s, name)
            WHERE id = %s
        """
        self.execute(query, (name, role_id))
        return True

    def delete(self, role_id):
        query = "DELETE FROM roles WHERE id = %s"
        self.execute(query, (role_id,))
        return True
