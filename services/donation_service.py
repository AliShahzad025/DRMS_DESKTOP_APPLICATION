class DonationService:

    def __init__(self, repo):
        self.repo = repo

    def add_donation(self, donor_name, amount, donation_type, note):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        return self.repo.create(donor_name, amount, donation_type, note)

    def get_donation(self, donation_id):
        return self.repo.get_by_id(donation_id)

    def list_donations(self):
        return self.repo.get_all()

    def update_donation(self, donation_id, **data):
        return self.repo.update(donation_id, **data)

    def delete_donation(self, donation_id):
        return self.repo.delete(donation_id)
