class RoleService:
    """
    Business logic for role operations.
    """

    def __init__(self, repo):
        self.repo = repo

    def add_role(self, name):
        if not name:
            raise ValueError("Role name required.")

        return self.repo.create(name)

    def get_role(self, role_id):
        return self.repo.get_by_id(role_id)

    def list_roles(self):
        return self.repo.get_all()

    def update_role(self, role_id, name=None):
        return self.repo.update(role_id, name)

    def delete_role(self, role_id):
        return self.repo.delete(role_id)
