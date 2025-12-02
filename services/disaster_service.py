class DisasterService:

    def __init__(self, repo):
        self.repo = repo

    def add_disaster(self, name, type, location, severity, status):
        return self.repo.create(name, type, location, severity, status)

    def get_disaster(self, disaster_id):
        return self.repo.get_by_id(disaster_id)

    def list_disasters(self):
        return self.repo.get_all()

    def update_disaster(self, disaster_id, **data):
        return self.repo.update(disaster_id, **data)

    def delete_disaster(self, disaster_id):
        return self.repo.delete(disaster_id)
