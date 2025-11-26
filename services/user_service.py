class UserService:
    def __init__(self, user_repository):
        self.user_repo = user_repository

    def add_user(self, name, email, phone, location, latitude, longitude, language, role, password):
        """Add a new user with plain text password"""
        return self.user_repo.add_user(name, email, phone, location, latitude, longitude, language, role, password)

    def authenticate_user(self, email, password):
        """
        Authenticate user with email and plain text password
        Returns user tuple/dict if successful, None if failed
        """
        return self.user_repo.authenticate_user(email, password)

    def list_users(self):
        """Get all users"""
        return self.user_repo.get_all_users()

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self.user_repo.get_user_by_id(user_id)
    
    def get_user_by_email(self, email):
        """Get user by email"""
        return self.user_repo.get_user_by_email(email)
    
    def get_users_by_role(self, role):
        """Get users by role"""
        return self.user_repo.get_users_by_role(role)
    
    def update_password(self, user_id, new_password):
        """Update user password"""
        return self.user_repo.update_password(user_id, new_password)