# # File: frontend/manage_resources.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
# from data.db_connection import DatabaseConnection # Removed
# import mysql.connector # Removed
from services.resource_service import ResourceService

class ManageResourcesApp(tk.Toplevel):
    def __init__(self, logged_in_user=None, db_connection=None, on_close_callback=None):
        super().__init__()
        self.logged_in_user = logged_in_user
        self.role = logged_in_user.get("role") if logged_in_user else "NGO"
        self.connection = db_connection  # Use the passed connection directly
        self.resource_service = ResourceService(self.connection)
        self.on_close_callback = on_close_callback

        self.title(f"Manage Resources - {self.role}")
        self.geometry("900x500")
        self.configure(bg="#f5f5f5")

        # Check NGO authorization
        if self.role == "NGO" and not self.logged_in_user.get("verified"):
            messagebox.showerror("Unauthorized", "Your account is not authorized to manage resources.")
            self.destroy()
            if self.on_close_callback:
                self.on_close_callback()
            return

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_widgets()
        self.load_resources()

    def on_closing(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()

    def create_widgets(self):
        tk.Label(self, text="Manage Resources", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=10)

        # Treeview
        columns = ("ID", "Type", "Quantity", "Status", "Last Verified By", "Location", "Donor NGO")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Buttons
        button_frame = tk.Frame(self, bg="#f5f5f5")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add Resource", bg="#4CAF50", fg="white",
                  command=self.add_resource).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Update Resource", bg="#2196F3", fg="white",
                  command=self.update_resource).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Transfer Resource", bg="#FF9800", fg="white",
                  command=self.transfer_resource).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Allocate Resource", bg="#9C27B0", fg="white",
                  command=self.allocate_resource).grid(row=0, column=3, padx=5)
        tk.Button(button_frame, text="Track Resource", bg="#607D8B", fg="white",
                  command=self.track_resource).grid(row=0, column=4, padx=5)
        tk.Button(button_frame, text="Back", bg="#777", fg="white",
                  command=self.go_back).grid(row=0, column=5, padx=5)

    def go_back(self):
        self.on_closing()

    def load_resources(self):
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)
        print("DEBUG: load_resources - Treeview cleared.")

        try:
            resources = self.resource_service.list_resources()
            print(f"DEBUG: load_resources - Resources fetched: {resources}")
            for row in resources:
                self.tree.insert("", "end", values=(
                    row["resourceID"],
                    row["resourceType"],
                    row["quantity"],
                    row["status"],
                    row["lastVerifiedBy"],
                    row["location"],
                    row["donorNGO"]
                ))
            print(f"DEBUG: load_resources - {len(resources)} resources inserted into treeview.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load resources: {str(e)}")

    def add_resource(self):
        resource_types = self.resource_service.list_resource_types()
        if not resource_types:
            messagebox.showwarning("Warning", "No resource types available. Please add resource types first.")
            return

        type_names = [rt['name'] for rt in resource_types]
        type_name = simpledialog.askstring("Resource Type", "Enter Resource Type (e.g., Food, Water, Shelter):")
        
        if type_name not in type_names:
            messagebox.showwarning("Invalid Resource Type", "Please enter a valid resource type from the list.")
            return
            
        type_id = self.resource_service.get_resource_type_id_by_name(type_name)
        
        quantity = simpledialog.askinteger("Quantity", "Enter Quantity:")
        location = simpledialog.askstring("Location", "Enter Location:")
        if not type_id or not quantity or not location:
            messagebox.showwarning("Warning", "All fields are required!")
            return
        print(f"DEBUG: add_resource - Type ID: {type_id}, Quantity: {quantity}, Location: {location}")

        try:
            donor_ngo = self.logged_in_user.get("id") if self.role == "NGO" else None
            last_verified = self.logged_in_user.get("id") if self.role == "Admin" else None
            print(f"DEBUG: add_resource - Donor NGO: {donor_ngo}, Last Verified By: {last_verified}")

            self.resource_service.add_resource(type_id, donor_ngo, quantity, last_verified, location)
            messagebox.showinfo("Success", "Resource added successfully!")
            self.load_resources()
        except ValueError as ve:
            messagebox.showwarning("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add resource: {str(e)}")

    def update_resource(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Resource", "Please select a resource to update.")
            return
        resource_id = self.tree.item(selected[0])["values"][0]
        new_qty = simpledialog.askinteger("Update Quantity", "Enter new quantity:")
        if new_qty is None:
            return

        try:
            self.resource_service.update_resource(resource_id, quantity=new_qty)
            messagebox.showinfo("Success", "Resource updated successfully!")
            self.load_resources()
        except ValueError as ve:
            messagebox.showwarning("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update resource: {str(e)}")

    def transfer_resource(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Resource", "Please select a resource to transfer.")
            return
        resource_id = self.tree.item(selected[0])["values"][0]
        from_ngo_id = self.logged_in_user.get("id")

        to_ngo = simpledialog.askinteger("Transfer To NGO ID", "Enter target NGO ID:")
        qty = simpledialog.askinteger("Quantity", "Enter quantity to transfer:")
        from_location = simpledialog.askstring("From Location", "Enter current location:")
        to_location = simpledialog.askstring("To Location", "Enter target location:")
        
        if not to_ngo or not qty or not from_location or not to_location:
            messagebox.showwarning("Warning", "All fields are required!")
            return

        try:
            self.resource_service.transfer_resource(resource_id, from_ngo_id, to_ngo, from_location, to_location, qty, self.logged_in_user.get("id"))
            messagebox.showinfo("Success", "Resource transfer recorded!")
            self.load_resources()
        except ValueError as ve:
            messagebox.showwarning("Transfer Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to transfer resource: {str(e)}")

    def allocate_resource(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Resource", "Please select a resource to allocate.")
            return
        resource_id = self.tree.item(selected[0])["values"][0]
        allocated_to_type = simpledialog.askstring("Allocate To", "Enter type (Victim/Shelter/Volunteer):")
        allocated_to_id = simpledialog.askinteger("Allocate To ID", "Enter target ID:")
        qty = simpledialog.askinteger("Quantity", "Enter quantity to allocate:")
        if not allocated_to_type or not allocated_to_id or not qty:
            messagebox.showwarning("Warning", "All fields are required!")
            return

        try:
            self.resource_service.allocate_resource(resource_id, allocated_to_type, allocated_to_id, None, qty)
            messagebox.showinfo("Success", "Resource allocated successfully!")
            self.load_resources()
        except ValueError as ve:
            messagebox.showwarning("Allocation Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to allocate resource: {str(e)}")

    def track_resource(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Resource", "Please select a resource to track.")
            return
        resource_id = self.tree.item(selected[0])["values"][0]

        try:
            resource = self.resource_service.track_resource(resource_id)
            if resource:
                details = f"ID: {resource['resourceID']}\nType: {resource['resourceType']}\nQuantity: {resource['quantity']}\nStatus: {resource['status']}\nLocation: {resource['location']}"
                messagebox.showinfo("Resource Status", details)
            else:
                messagebox.showinfo("Resource Status", "Resource not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to track resource: {str(e)}")
