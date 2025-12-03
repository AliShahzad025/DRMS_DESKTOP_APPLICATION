from .base_repository import BaseRepository

class ResourceRepository(BaseRepository):

    def add_resource(self, resource_type_id, donor_ngo_id, quantity, last_verified_by, location, latitude=0.0, longitude=0.0):
        query = """
            INSERT INTO ResourceStock (resourceTypeID, donorNGO, quantity, status, lastVerifiedBy, location, latitude, longitude)
            VALUES (%s, %s, %s, 'available', %s, %s, %s, %s)
        """
        self.execute(query, (resource_type_id, donor_ngo_id, quantity, last_verified_by, location, latitude, longitude))
        return True

    def get_resource_by_id(self, resource_id):
        query = "SELECT rs.resourceID, rt.name AS resourceType, rs.quantity, rs.status, rs.lastVerifiedBy, rs.location, rs.latitude, rs.longitude, rs.donorNGO FROM ResourceStock rs JOIN ResourceType rt ON rs.resourceTypeID = rt.resourceTypeID WHERE rs.resourceID = %s"
        return self.fetch_one(query, (resource_id,))

    def get_all_resources(self):
        query = "SELECT rs.resourceID, rt.name AS resourceType, rs.quantity, rs.status, rs.lastVerifiedBy, rs.location, rs.latitude, rs.longitude, rs.donorNGO FROM ResourceStock rs JOIN ResourceType rt ON rs.resourceTypeID = rt.resourceTypeID"
        return self.fetch_all(query)

    def update_resource(self, resource_id, **fields):
        # Dynamically build the update query based on provided fields
        set_clauses = []
        values = []
        for key, value in fields.items():
            set_clauses.append(f"{key} = %s")
            values.append(value)
        
        if not set_clauses:
            return False # No fields to update

        query = f"UPDATE ResourceStock SET {', '.join(set_clauses)} WHERE resourceID = %s"
        values.append(resource_id)
        self.execute(query, tuple(values))
        return True

    def delete_resource(self, resource_id):
        query = "DELETE FROM ResourceStock WHERE resourceID = %s"
        self.execute(query, (resource_id,))
        return True

    def get_resource_type_id_by_name(self, name):
        query = "SELECT resourceTypeID FROM ResourceType WHERE name = %s"
        result = self.fetch_one(query, (name,))
        return result['resourceTypeID'] if result else None

    def get_resource_type_name_by_id(self, type_id):
        query = "SELECT name FROM ResourceType WHERE resourceTypeID = %s"
        result = self.fetch_one(query, (type_id,))
        return result['name'] if result else None

    def get_all_resource_types(self):
        query = "SELECT resourceTypeID, name FROM ResourceType"
        return self.fetch_all(query)

    def get_resource_quantity(self, resource_id):
        query = "SELECT quantity FROM ResourceStock WHERE resourceID = %s"
        result = self.fetch_one(query, (resource_id,))
        return result['quantity'] if result else 0

    def transfer_resource_record(self, resource_id, from_ngo_id, to_ngo_id, from_location, to_location, quantity, transferred_by):
        query = """
            INSERT INTO ResourceTransfer (resourceID, fromNGO, toNGO, fromLocation, toLocation, quantity, status, transferredBy)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s)
        """
        self.execute(query, (resource_id, from_ngo_id, to_ngo_id, from_location, to_location, quantity, transferred_by))
        return True

    def allocate_resource_record(self, resource_id, allocated_to_type, allocated_to_id, request_id, quantity, allocation_status='pending'):
        query = """
            INSERT INTO ResourceAllocation (resourceID, allocatedToType, allocatedToID, requestID, quantity, allocationStatus)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.execute(query, (resource_id, allocated_to_type, allocated_to_id, request_id, quantity, allocation_status))
        return True
