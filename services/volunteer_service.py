class VolunteerService:

    def __init__(self, repo):
        self.repo = repo

    def register_volunteer(self, name, phone, skills, availability, location):
        return self.repo.create(name, phone, skills, availability, location)

    def get_volunteer(self, volunteer_id):
        return self.repo.get_by_id(volunteer_id)

    def list_volunteers(self):
        return self.repo.get_all()

    def update_volunteer(self, volunteer_id, **data):
        return self.repo.update(volunteer_id, **data)

    def delete_volunteer(self, volunteer_id):
        return self.repo.delete(volunteer_id)
