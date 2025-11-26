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
    from .base_repository import BaseRepository

class UserRepository(BaseRepository):
    
    def add_user(self, name, email, phone, location, latitude, longitude, language, role, password):
        """Add a new user to the useraccount table with plain text password"""
        query = """
        INSERT INTO useraccount (name, email, phone, location, latitude, longitude, language, role, password_hash)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Store plain text password in password_hash field
        params = (name, email, phone, location, latitude, longitude, language, role, password)
        cursor = self.execute(query, params)
        return cursor.lastrowid  # Returns the ID of the newly created user
    
    def authenticate_user(self, email, password):
        """
        Authenticate user with email and plain text password
        Returns user data if successful, None if authentication fails
        """
        query = "SELECT * FROM useraccount WHERE email = %s AND password_hash = %s"
        user = self.fetch_one(query, (email, password))
        return user
    
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
    
    def get_users_by_role(self, role):
        """Get all users with a specific role"""
        query = "SELECT * FROM useraccount WHERE role = %s"
        return self.fetch_all(query, (role,))
    
    def update_user(self, user_id, **kwargs):
        """Update user fields"""
        fields = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        query = f"UPDATE useraccount SET {fields} WHERE userID = %s"
        params = tuple(kwargs.values()) + (user_id,)
        return self.execute(query, params)
    
    def update_password(self, user_id, new_password):
        """Update user password (plain text)"""
        query = "UPDATE useraccount SET password_hash = %s WHERE userID = %s"
        return self.execute(query, (new_password, user_id))
    
    def delete_user(self, user_id):
        """Delete a user by their ID"""
        query = "DELETE FROM useraccount WHERE userID = %s"
        return self.execute(query, (user_id,))
    
    def check_email_exists(self, email):
        """Check if an email already exists in the database"""
        query = "SELECT COUNT(*) as count FROM useraccount WHERE email = %s"
        result = self.fetch_one(query, (email,))
        return result['count'] > 0 if result else False
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