from .base_repository import BaseRepository

class UserRepository(BaseRepository):
    
    def add_user(self, name, email, phone, location, latitude, longitude, language, role, password_hash):
        """Add a new user to the useraccount table"""
        query = """
        INSERT INTO useraccount (name, email, phone, location, latitude, longitude, language, role, password_hash)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (name, email, phone, location, latitude, longitude, language, role, password_hash)
        cursor = self.execute(query, params)
        return cursor.lastrowid  # Returns the ID of the newly created user
    
    def get_all_users(self):
        """Get all users from the useraccount table"""
        query = "SELECT * FROM useraccount"
        return self.fetch_all(query)
    
    def get_user_by_id(self, user_id):
        """Get a user by their ID"""
        query = "SELECT * FROM useraccount WHERE userID = %s"
        return self.fetch_one(query, (user_id,))
    
    def get_user_by_email(self, email):
        """Get a user by their email"""
        query = "SELECT * FROM useraccount WHERE email = %s"
        return self.fetch_one(query, (email,))
    
    def update_user(self, user_id, **kwargs):
        """Update user fields"""
        fields = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        query = f"UPDATE useraccount SET {fields} WHERE userID = %s"
        params = tuple(kwargs.values()) + (user_id,)
        return self.execute(query, params)
    
    def delete_user(self, user_id):
        """Delete a user by their ID"""
        query = "DELETE FROM useraccount WHERE userID = %s"
        return self.execute(query, (user_id,))