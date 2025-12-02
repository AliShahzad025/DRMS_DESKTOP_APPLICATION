# # File: frontend/manage_resources.py

# import tkinter as tk
# from tkinter import ttk, messagebox, simpledialog
# from data.db_connection import DatabaseConnection
# import mysql.connector

# class ManageResourcesApp(tk.Tk):
#     def __init__(self, logged_in_user=None, db_connection=None, back_app=None):
#         super().__init__()
#         self.logged_in_user = logged_in_user
#         self.role = logged_in_user.get("role") if logged_in_user else "NGO"
#         self.connection = db_connection if db_connection else DatabaseConnection().connect()
#         self.back_app = back_app  # For Back button

#         self.title(f"Manage Resources - {self.role}")
#         self.geometry("900x500")
#         self.configure(bg="#f5f5f5")

#         # Check NGO authorization
#         if self.role == "NGO" and not self.logged_in_user.get("verified"):
#             messagebox.showerror("Unauthorized", "Your account is not authorized to manage resources.")
#             self.destroy()
#             return

#         self.create_widgets()
#         self.load_resources()

#     def create_widgets(self):
#         tk.Label(self, text="Manage Resources", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=10)

#         # Treeview
#         columns = ("ID", "Type", "Quantity", "Status", "Last Verified By", "Location")
#         self.tree = ttk.Treeview(self, columns=columns, show="headings")
#         for col in columns:
#             self.tree.heading(col, text=col)
#             self.tree.column(col, width=140)
#         self.tree.pack(fill="both", expand=True, padx=20, pady=10)

#         # Buttons
#         button_frame = tk.Frame(self, bg="#f5f5f5")
#         button_frame.pack(pady=10)

#         tk.Button(button_frame, text="Add Resource", bg="#4CAF50", fg="white",
#                   command=self.add_resource).grid(row=0, column=0, padx=5)
#         tk.Button(button_frame, text="Update Resource", bg="#2196F3", fg="white",
#                   command=self.update_resource).grid(row=0, column=1, padx=5)
#         tk.Button(button_frame, text="Transfer Resource", bg="#FF9800", fg="white",
#                   command=self.transfer_resource).grid(row=0, column=2, padx=5)
#         tk.Button(button_frame, text="Allocate Resource", bg="#9C27B0", fg="white",
#                   command=self.allocate_resource).grid(row=0, column=3, padx=5)
#         tk.Button(button_frame, text="Back", bg="#777", fg="white",
#                   command=self.go_back).grid(row=0, column=4, padx=5)

#     def go_back(self):
#         self.destroy()
#         if self.back_app:
#             self.back_app.deiconify()

#     def load_resources(self):
#         # Clear existing rows
#         for row in self.tree.get_children():
#             self.tree.delete(row)

#         try:
#             cursor = self.connection.cursor(dictionary=True)
#             cursor.execute("""
#                 SELECT r.resourceID, t.name AS resourceType, r.quantity, r.status, r.lastVerifiedBy, r.location
#                 FROM ResourceStock r
#                 JOIN ResourceType t ON r.resourceTypeID = t.resourceTypeID
#             """)
#             for row in cursor.fetchall():
#                 self.tree.insert("", "end", values=(
#                     row["resourceID"],
#                     row["resourceType"],
#                     row["quantity"],
#                     row["status"],
#                     row["lastVerifiedBy"],
#                     row["location"]
#                 ))
#             cursor.close()
#         except mysql.connector.Error as e:
#             messagebox.showerror("Database Error", f"Failed to load resources: {str(e)}")

#     def add_resource(self):
#         type_id = simpledialog.askinteger("Resource Type ID", "Enter Resource Type ID:")
#         quantity = simpledialog.askinteger("Quantity", "Enter Quantity:")
#         location = simpledialog.askstring("Location", "Enter Location:")
#         if not type_id or not quantity or not location:
#             messagebox.showwarning("Warning", "All fields are required!")
#             return

#         try:
#             cursor = self.connection.cursor()
#             donor_ngo = self.logged_in_user.get("id") if self.role == "NGO" else None
#             last_verified = self.logged_in_user.get("id") if self.role == "Admin" else None

#             cursor.execute("""
#                 INSERT INTO ResourceStock (resourceTypeID, donorNGO, quantity, status, lastVerifiedBy, location, latitude, longitude)
#                 VALUES (%s, %s, %s, 'available', %s, %s, 0.0, 0.0)
#             """, (type_id, donor_ngo, quantity, last_verified, location))
#             self.connection.commit()
#             cursor.close()
#             messagebox.showinfo("Success", "Resource added successfully!")
#             self.load_resources()
#         except mysql.connector.Error as e:
#             messagebox.showerror("Error", f"Failed to add resource: {str(e)}")

#     def update_resource(self):
#         selected = self.tree.selection()
#         if not selected:
#             messagebox.showwarning("Select Resource", "Please select a resource to update.")
#             return
#         resource_id = self.tree.item(selected[0])["values"][0]
#         new_qty = simpledialog.askinteger("Update Quantity", "Enter new quantity:")
#         if new_qty is None:
#             return

#         try:
#             cursor = self.connection.cursor()
#             cursor.execute("UPDATE ResourceStock SET quantity=%s WHERE resourceID=%s", (new_qty, resource_id))
#             self.connection.commit()
#             cursor.close()
#             messagebox.showinfo("Success", "Resource updated successfully!")
#             self.load_resources()
#         except mysql.connector.Error as e:
#             messagebox.showerror("Error", f"Failed to update resource: {str(e)}")

#     def transfer_resource(self):
#         selected = self.tree.selection()
#         if not selected:
#             messagebox.showwarning("Select Resource", "Please select a resource to transfer.")
#             return
#         resource_id = self.tree.item(selected[0])["values"][0]
#         to_ngo = simpledialog.askinteger("Transfer To NGO ID", "Enter target NGO ID:")
#         qty = simpledialog.askinteger("Quantity", "Enter quantity to transfer:")
#         if not to_ngo or not qty:
#             return

#         try:
#             cursor = self.connection.cursor()
#             cursor.execute("""
#                 INSERT INTO ResourceTransfer (resourceID, fromNGO, toNGO, fromLocation, toLocation, quantity, status, transferredBy)
#                 VALUES (%s, %s, %s, 'current', 'target', %s, 'pending', %s)
#             """, (resource_id, self.logged_in_user.get("id"), to_ngo, qty, self.logged_in_user.get("id")))
#             self.connection.commit()
#             cursor.close()
#             messagebox.showinfo("Success", "Resource transfer recorded!")
#             self.load_resources()
#         except mysql.connector.Error as e:
#             messagebox.showerror("Error", f"Failed to transfer resource: {str(e)}")

#     def allocate_resource(self):
#         selected = self.tree.selection()
#         if not selected:
#             messagebox.showwarning("Select Resource", "Please select a resource to allocate.")
#             return
#         resource_id = self.tree.item(selected[0])["values"][0]
#         allocated_to_type = simpledialog.askstring("Allocate To", "Enter type (Victim/Shelter/Volunteer):")
#         allocated_to_id = simpledialog.askinteger("Allocate To ID", "Enter target ID:")
#         qty = simpledialog.askinteger("Quantity", "Enter quantity to allocate:")
#         if not allocated_to_type or not allocated_to_id or not qty:
#             return

#         try:
#             cursor = self.connection.cursor()
#             cursor.execute("""
#                 INSERT INTO ResourceAllocation (resourceID, allocatedToType, allocatedToID, requestID, quantity, allocationStatus)
#                 VALUES (%s, %s, %s, NULL, %s, 'pending')
#             """, (resource_id, allocated_to_type, allocated_to_id, qty))
#             self.connection.commit()
#             cursor.close()
#             messagebox.showinfo("Success", "Resource allocated successfully!")
#             self.load_resources()
#         except mysql.connector.Error as e:
#             messagebox.showerror("Error", f"Failed to allocate resource: {str(e)}")
