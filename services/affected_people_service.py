class AffectedPeopleService:

    def __init__(self, repo):
        self.repo = repo

    def add_person(self, disaster_id, name, age, gender, injury_status, aid_required):
        if not name:
            raise ValueError("Name is required.")
        return self.repo.create(disaster_id, name, age, gender, injury_status, aid_required)

    def get_person(self, person_id):
        return self.repo.get_by_id(person_id)

    def list_all(self):
        return self.repo.get_all()

    def list_by_disaster(self, disaster_id):
        return self.repo.get_by_disaster(disaster_id)

    def update_person(self, person_id, **data):
        return self.repo.update(person_id, **data)

    def delete_person(self, person_id):
        return self.repo.delete(person_id)
