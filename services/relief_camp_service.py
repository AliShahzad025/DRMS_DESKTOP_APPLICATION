class ReliefCampService:

    def __init__(self, repo):
        self.repo = repo

    def add_camp(self, name, location, capacity, incharge_name, contact):
        if capacity < 0:
            raise ValueError("Capacity cannot be negative.")
        return self.repo.create(name, location, capacity, incharge_name, contact)

    def get_camp(self, camp_id):
        return self.repo.get_by_id(camp_id)

    def list_camps(self):
        return self.repo.get_all()

    def update_camp(self, camp_id, **data):
        return self.repo.update(camp_id, **data)

    def delete_camp(self, camp_id):
        return self.repo.delete(camp_id)
