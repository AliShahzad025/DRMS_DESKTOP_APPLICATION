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

    def authenticate_user(self, email, password):
        """
        Authenticate user with email and plain text password
        Returns user data if successful, None if authentication fails
        """
        query = """
            SELECT ua.*, 
                   CASE WHEN ua.role = 'NGO' THEN n.verified ELSE NULL END as verified
            FROM useraccount ua
            LEFT JOIN NGO n ON ua.userID = n.ngoID
            WHERE ua.email = %s AND ua.password_hash = %s
        """
        user = self.fetch_one(query, (email, password))
        return user
    
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
    
    def get_ngo_details(self, ngo_id):
        """Get NGO details including resource management permission"""
        query = "SELECT N.orgName, N.verified, N.can_manage_resources, N.registration_doc, N.region, N.contact_person FROM NGO N WHERE N.ngoID = %s"
        return self.fetch_one(query, (ngo_id,))

    def get_all_ngos(self):
        """Get all NGOs with their resource management permission status"""
        query = "SELECT UA.userID, UA.name, N.orgName, N.verified, N.can_manage_resources FROM UserAccount UA JOIN NGO N ON UA.userID = N.ngoID"
        return self.fetch_all(query)

    def update_ngo_resource_permission(self, ngo_id, can_manage_resources):
        """Update an NGO's resource management permission"""
        query = "UPDATE NGO SET can_manage_resources = %s WHERE ngoID = %s"
        params = (can_manage_resources, ngo_id)
        return self.execute(query, params)