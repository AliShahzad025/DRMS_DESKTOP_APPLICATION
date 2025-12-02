class InventoryService:

    def __init__(self, repo):
        self.repo = repo

    def add_item(self, item_name, quantity, category, camp_id):
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        return self.repo.create(item_name, quantity, category, camp_id)

    def get_item(self, item_id):
        return self.repo.get_by_id(item_id)

    def list_items(self):
        return self.repo.get_all()

    def list_items_by_camp(self, camp_id):
        return self.repo.get_by_camp(camp_id)

    def update_item(self, item_id, **data):
        return self.repo.update(item_id, **data)

    def delete_item(self, item_id):
        return self.repo.delete(item_id)
