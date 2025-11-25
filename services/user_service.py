class UserService:
    def __init__(self, user_repository):
        self.user_repo = user_repository

    def add_user(self, name, email, phone, location, latitude, longitude, language, role, password_hash):
        return self.user_repo.add_user(name, email, phone, location, latitude, longitude, language, role, password_hash)

    def list_users(self):
        return self.user_repo.get_all_users()

    def get_user_by_id(self, user_id):
        return self.user_repo.get_user_by_id(user_id)