from data.resource_repository import ResourceRepository

class ResourceService:
    def __init__(self, db_connection):
        self.resource_repo = ResourceRepository(db_connection)

    def add_resource(self, resource_type_id, donor_ngo_id, quantity, last_verified_by, location, latitude=0.0, longitude=0.0):
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        return self.resource_repo.add_resource(resource_type_id, donor_ngo_id, quantity, last_verified_by, location, latitude, longitude)

    def get_resource(self, resource_id):
        return self.resource_repo.get_resource_by_id(resource_id)

    def list_resources(self):
        return self.resource_repo.get_all_resources()

    def update_resource(self, resource_id, **data):
        if "quantity" in data and data["quantity"] <= 0:
            raise ValueError("Quantity must be positive.")
        return self.resource_repo.update_resource(resource_id, **data)

    def delete_resource(self, resource_id):
        return self.resource_repo.delete_resource(resource_id)

    def get_resource_type_id_by_name(self, name):
        return self.resource_repo.get_resource_type_id_by_name(name)

    def get_resource_type_name_by_id(self, type_id):
        return self.resource_repo.get_resource_type_name_by_id(type_id)

    def list_resource_types(self):
        return self.resource_repo.get_all_resource_types()

    def transfer_resource(self, resource_id, from_ngo_id, to_ngo_id, from_location, to_location, quantity, transferred_by):
        current_quantity = self.resource_repo.get_resource_quantity(resource_id)
        if current_quantity < quantity:
            raise ValueError("Insufficient resources for transfer.")
        
        # Deduct from source
        self.resource_repo.update_resource(resource_id, quantity=(current_quantity - quantity))
        
        # Record transfer
        return self.resource_repo.transfer_resource_record(resource_id, from_ngo_id, to_ngo_id, from_location, to_location, quantity, transferred_by)

    def allocate_resource(self, resource_id, allocated_to_type, allocated_to_id, request_id, quantity):
        current_quantity = self.resource_repo.get_resource_quantity(resource_id)
        if current_quantity < quantity:
            raise ValueError("Insufficient resources available for allocation.")
        
        # Deduct from stock
        self.resource_repo.update_resource(resource_id, quantity=(current_quantity - quantity))
        
        # Record allocation
        return self.resource_repo.allocate_resource_record(resource_id, allocated_to_type, allocated_to_id, request_id, quantity)

    def track_resource(self, resource_id):
        return self.resource_repo.get_resource_by_id(resource_id)
