# File: frontend/allocate_resources.py
# Use Case UC-9c: Allocate Resources

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data.db_connection import DatabaseConnection
import mysql.connector

class AllocateResourcesApp(tk.Tk):
    def __init__(self, logged_in_user=None, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user
        self.role = logged_in_user.get("role") if logged_in_user else None
        
        # Verify user has allocation rights (Admin or verified NGO)
        if self.role not in ["Admin", "NGO"]:
            messagebox.showerror("Unauthorized", "You do not have permission to allocate resources.")
            self.destroy()
            return
        
        if self.role == "NGO" and not logged_in_user.get("verified"):
            messagebox.showerror("Unauthorized", "Your NGO must be verified to allocate resources.")
            self.destroy()
            return
        
        self.title("Allocate Resources - DRMS")
        self.geometry("1200x700")
        self.configure(bg="#f5f5f5")
        
        # DB setup
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        if not self.connection:
            messagebox.showerror("Database Error", "Cannot connect to database!")
            self.destroy()
            return
        
        self.create_widgets()
        self.load_pending_requests()
        self.load_available_resources()

    def create_widgets(self):
        # Title
        tk.Label(self, text="Allocate Resources", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=15)
        
        # Main container with two panes
        main_frame = tk.Frame(self, bg="#f5f5f5")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left pane - Pending Requests
        left_frame = tk.LabelFrame(main_frame, text="Pending SOS Requests", font=("Helvetica", 12, "bold"), 
                                   bg="#f5f5f5", padx=10, pady=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        request_columns = ("requestID", "victimName", "typeOfNeed", "urgencyLevel", "location")
        self.request_tree = ttk.Treeview(left_frame, columns=request_columns, show="headings", height=15)
        
        self.request_tree.heading("requestID", text="Request ID")
        self.request_tree.heading("victimName", text="Victim Name")
        self.request_tree.heading("typeOfNeed", text="Type of Need")
        self.request_tree.heading("urgencyLevel", text="Urgency")
        self.request_tree.heading("location", text="Location")
        
        self.request_tree.column("requestID", width=100)
        self.request_tree.column("victimName", width=150)
        self.request_tree.column("typeOfNeed", width=150)
        self.request_tree.column("urgencyLevel", width=100)
        self.request_tree.column("location", width=200)
        
        request_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.request_tree.yview)
        self.request_tree.configure(yscrollcommand=request_scrollbar.set)
        
        self.request_tree.pack(side="left", fill="both", expand=True)
        request_scrollbar.pack(side="right", fill="y")
        
        # Right pane - Available Resources
        right_frame = tk.LabelFrame(main_frame, text="Available Resources", font=("Helvetica", 12, "bold"), 
                                    bg="#f5f5f5", padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        resource_columns = ("resourceID", "resourceType", "quantity", "location")
        self.resource_tree = ttk.Treeview(right_frame, columns=resource_columns, show="headings", height=15)
        
        self.resource_tree.heading("resourceID", text="Resource ID")
        self.resource_tree.heading("resourceType", text="Resource Type")
        self.resource_tree.heading("quantity", text="Available Qty")
        self.resource_tree.heading("location", text="Location")
        
        self.resource_tree.column("resourceID", width=100)
        self.resource_tree.column("resourceType", width=200)
        self.resource_tree.column("quantity", width=120)
        self.resource_tree.column("location", width=200)
        
        resource_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.resource_tree.yview)
        self.resource_tree.configure(yscrollcommand=resource_scrollbar.set)
        
        self.resource_tree.pack(side="left", fill="both", expand=True)
        resource_scrollbar.pack(side="right", fill="y")
        
        # Allocation form
        form_frame = tk.Frame(self, bg="#f5f5f5")
        form_frame.pack(pady=10, fill="x", padx=20)
        
        tk.Label(form_frame, text="Allocation Quantity:", font=("Helvetica", 10), 
                bg="#f5f5f5").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.quantity_entry = tk.Entry(form_frame, font=("Helvetica", 10), width=15)
        self.quantity_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Allocate To Type:", font=("Helvetica", 10), 
                bg="#f5f5f5").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.allocate_type_var = tk.StringVar(value="Victim")
        allocate_type_menu = ttk.Combobox(form_frame, textvariable=self.allocate_type_var, 
                                         values=["Victim", "Shelter", "Volunteer", "NGO"], 
                                         state="readonly", width=15)
        allocate_type_menu.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(form_frame, text="Allocate To ID:", font=("Helvetica", 10), 
                bg="#f5f5f5").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.allocate_id_entry = tk.Entry(form_frame, font=("Helvetica", 10), width=15)
        self.allocate_id_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="Allocate Resource", font=("Helvetica", 12, "bold"), 
                 bg="#4CAF50", fg="white", width=18, command=self.allocate_resource).grid(row=0, column=0, padx=5)
        
        tk.Button(btn_frame, text="Refresh", font=("Helvetica", 12), 
                 bg="#FF9800", fg="white", width=18, command=self.refresh_data).grid(row=0, column=1, padx=5)
        
        tk.Button(btn_frame, text="Back", font=("Helvetica", 12), 
                 bg="#757575", fg="white", width=18, command=self.go_back).grid(row=0, column=2, padx=5)

    def load_pending_requests(self):
        """Load pending SOS requests"""
        for item in self.request_tree.get_children():
            self.request_tree.delete(item)
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.requestID, u.name AS victimName, r.typeOfNeed, r.urgencyLevel, r.location
                FROM SOSRequest r
                JOIN Victim v ON r.victimID = v.victimID
                JOIN UserAccount u ON v.victimID = u.userID
                WHERE r.status IN ('pending', 'in_process')
                ORDER BY r.urgencyLevel DESC, r.createdAt ASC
            """)
            
            requests = cursor.fetchall()
            
            for req in requests:
                self.request_tree.insert("", "end", values=(
                    req["requestID"],
                    req["victimName"],
                    req["typeOfNeed"] or "N/A",
                    req["urgencyLevel"],
                    req["location"] or "N/A"
                ))
            
            cursor.close()
        
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to load requests: {str(e)}")

    def load_available_resources(self):
        """Load available resources"""
        for item in self.resource_tree.get_children():
            self.resource_tree.delete(item)
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # If NGO user, only show their resources
            if self.role == "NGO":
                ngo_id = self.logged_in_user.get("id")
                query = """
                    SELECT r.resourceID, rt.name AS resourceType, r.quantity, r.location
                    FROM ResourceStock r
                    JOIN ResourceType rt ON r.resourceTypeID = rt.resourceTypeID
                    WHERE r.donorNGO = %s AND r.status = 'available' AND r.quantity > 0
                """
                cursor.execute(query, (ngo_id,))
            else:
                # Admin sees all available resources
                query = """
                    SELECT r.resourceID, rt.name AS resourceType, r.quantity, r.location
                    FROM ResourceStock r
                    JOIN ResourceType rt ON r.resourceTypeID = rt.resourceTypeID
                    WHERE r.status = 'available' AND r.quantity > 0
                """
                cursor.execute(query)
            
            resources = cursor.fetchall()
            
            for resource in resources:
                self.resource_tree.insert("", "end", values=(
                    resource["resourceID"],
                    resource["resourceType"],
                    resource["quantity"],
                    resource["location"] or "N/A"
                ))
            
            cursor.close()
        
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to load resources: {str(e)}")

    def allocate_resource(self):
        """Allocate resource to request or entity"""
        # Get selected request and resource
        selected_request = self.request_tree.selection()
        selected_resource = self.resource_tree.selection()
        
        if not selected_resource:
            messagebox.showwarning("No Selection", "Please select a resource to allocate.")
            return
        
        resource_data = self.resource_tree.item(selected_resource[0])["values"]
        resource_id = resource_data[0]
        available_qty = resource_data[2]
        
        # Get allocation details
        quantity = self.quantity_entry.get().strip()
        allocate_type = self.allocate_type_var.get()
        allocate_id = self.allocate_id_entry.get().strip()
        
        # Get request ID if selected
        request_id = None
        if selected_request:
            request_data = self.request_tree.item(selected_request[0])["values"]
            request_id = request_data[0]
            # Auto-fill allocate type and ID for requests
            if not allocate_id:
                allocate_type = "Victim"
                # Get victim ID from request
                try:
                    cursor = self.connection.cursor()
                    cursor.execute("SELECT victimID FROM SOSRequest WHERE requestID = %s", (request_id,))
                    result = cursor.fetchone()
                    if result:
                        allocate_id = str(result[0])
                    cursor.close()
                except:
                    pass
        
        # Validation
        if not quantity:
            messagebox.showwarning("Missing Information", "Please enter allocation quantity.")
            return
        
        if not allocate_id:
            messagebox.showwarning("Missing Information", "Please enter Allocate To ID.")
            return
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive quantity.")
            return
        
        # Check stock availability
        if quantity > available_qty:
            messagebox.showerror("Insufficient Resources", 
                               f"Insufficient resources available.\n"
                               f"Available: {available_qty}, Requested: {quantity}")
            return
        
        # Confirm allocation
        confirm_msg = f"Allocate {quantity} units of {resource_data[1]} to {allocate_type} (ID: {allocate_id})?"
        if request_id:
            confirm_msg += f"\nLinked to Request ID: {request_id}"
        
        confirm = messagebox.askyesno("Confirm Allocation", confirm_msg)
        if not confirm:
            return
        
        try:
            cursor = self.connection.cursor()
            
            # Create allocation record
            cursor.execute("""
                INSERT INTO ResourceAllocation (resourceID, allocatedToType, allocatedToID, requestID, 
                                              quantity, allocationStatus)
                VALUES (%s, %s, %s, %s, %s, 'pending')
            """, (resource_id, allocate_type, allocate_id, request_id, quantity))
            
            # Update resource quantity
            new_qty = available_qty - quantity
            cursor.execute("""
                UPDATE ResourceStock 
                SET quantity = %s, status = CASE WHEN %s <= 5 THEN 'low' ELSE status END
                WHERE resourceID = %s
            """, (new_qty, new_qty, resource_id))
            
            # Update request status if linked
            if request_id:
                cursor.execute("""
                    UPDATE SOSRequest 
                    SET status = 'in_process' 
                    WHERE requestID = %s AND status = 'pending'
                """, (request_id,))
            
            self.connection.commit()
            cursor.close()
            
            messagebox.showinfo("Success", 
                              f"Resource allocated successfully!\n"
                              f"Allocation status: Pending")
            
            # Refresh data
            self.refresh_data()
            # Clear form
            self.quantity_entry.delete(0, tk.END)
            self.allocate_id_entry.delete(0, tk.END)
        
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to allocate resource: {str(e)}")

    def refresh_data(self):
        """Refresh both tables"""
        self.load_pending_requests()
        self.load_available_resources()

    def go_back(self):
        """Return to previous screen"""
        self.destroy()
        if self.role == "Admin":
            from frontend.login import AdminOptionsApp
            app = AdminOptionsApp(logged_in_user=self.logged_in_user, db_connection=self.connection)
            app.mainloop()
        elif self.role == "NGO":
            from frontend.manage_resources import ManageResourcesApp
            app = ManageResourcesApp(logged_in_user=self.logged_in_user, db_connection=self.connection)
            app.mainloop()


# ---------- TEST ----------
if __name__ == "__main__":
    app = AllocateResourcesApp(logged_in_user={"role": "Admin", "name": "Admin", "id": 1, "verified": True})
    app.mainloop()

