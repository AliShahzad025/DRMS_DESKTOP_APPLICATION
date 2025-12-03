# File: frontend/transfer_resources.py
# Use Case UC-9b: Transfer Resources

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data.db_connection import DatabaseConnection
import mysql.connector

class TransferResourcesApp(tk.Tk):
    def __init__(self, logged_in_user=None, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user
        self.role = logged_in_user.get("role") if logged_in_user else None
        
        # Verify user has transfer rights (Admin or verified NGO)
        if self.role not in ["Admin", "NGO"]:
            messagebox.showerror("Unauthorized", "You do not have permission to transfer resources.")
            self.destroy()
            return
        
        if self.role == "NGO" and not logged_in_user.get("verified"):
            messagebox.showerror("Unauthorized", "Your NGO must be verified to transfer resources.")
            self.destroy()
            return
        
        self.title("Transfer Resources - DRMS")
        self.geometry("1000x600")
        self.configure(bg="#f5f5f5")
        
        # DB setup
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        if not self.connection:
            messagebox.showerror("Database Error", "Cannot connect to database!")
            self.destroy()
            return
        
        self.create_widgets()
        self.load_resources()

    def create_widgets(self):
        # Title
        tk.Label(self, text="Transfer Resources", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=15)
        
        # Info label
        tk.Label(self, text="Select resource(s) and target location/NGO for transfer", 
                font=("Helvetica", 10), bg="#f5f5f5", fg="#666").pack(pady=5)
        
        # Resources Table
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        columns = ("resourceID", "resourceType", "quantity", "status", "location", "donorNGO")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        self.tree.heading("resourceID", text="Resource ID")
        self.tree.heading("resourceType", text="Resource Type")
        self.tree.heading("quantity", text="Available Qty")
        self.tree.heading("status", text="Status")
        self.tree.heading("location", text="Current Location")
        self.tree.heading("donorNGO", text="Donor NGO")
        
        self.tree.column("resourceID", width=100)
        self.tree.column("resourceType", width=150)
        self.tree.column("quantity", width=120)
        self.tree.column("status", width=120)
        self.tree.column("location", width=200)
        self.tree.column("donorNGO", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Transfer form frame
        form_frame = tk.Frame(self, bg="#f5f5f5")
        form_frame.pack(pady=10, fill="x", padx=20)
        
        # Transfer details
        tk.Label(form_frame, text="Transfer Details:", font=("Helvetica", 12, "bold"), 
                bg="#f5f5f5").grid(row=0, column=0, columnspan=2, pady=5, sticky="w")
        
        tk.Label(form_frame, text="Transfer To (NGO ID):", font=("Helvetica", 10), 
                bg="#f5f5f5").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.target_ngo_entry = tk.Entry(form_frame, font=("Helvetica", 10), width=20)
        self.target_ngo_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Target Location:", font=("Helvetica", 10), 
                bg="#f5f5f5").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.target_location_entry = tk.Entry(form_frame, font=("Helvetica", 10), width=30)
        self.target_location_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Transfer Quantity:", font=("Helvetica", 10), 
                bg="#f5f5f5").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.quantity_entry = tk.Entry(form_frame, font=("Helvetica", 10), width=20)
        self.quantity_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Buttons frame
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="Transfer Resource", font=("Helvetica", 12, "bold"), 
                 bg="#4CAF50", fg="white", width=18, command=self.transfer_resource).grid(row=0, column=0, padx=5)
        
        tk.Button(btn_frame, text="View Available NGOs", font=("Helvetica", 12), 
                 bg="#2196F3", fg="white", width=18, command=self.view_ngos).grid(row=0, column=1, padx=5)
        
        tk.Button(btn_frame, text="Refresh", font=("Helvetica", 12), 
                 bg="#FF9800", fg="white", width=18, command=self.load_resources).grid(row=0, column=2, padx=5)
        
        tk.Button(btn_frame, text="Back", font=("Helvetica", 12), 
                 bg="#757575", fg="white", width=18, command=self.go_back).grid(row=0, column=3, padx=5)

    def load_resources(self):
        """Load available resources"""
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # If NGO user, only show their resources
            if self.role == "NGO":
                ngo_id = self.logged_in_user.get("id")
                query = """
                    SELECT r.resourceID, rt.name AS resourceType, r.quantity, r.status, 
                           r.location, n.orgName AS donorNGO, r.donorNGO as donorNGOID
                    FROM ResourceStock r
                    JOIN ResourceType rt ON r.resourceTypeID = rt.resourceTypeID
                    LEFT JOIN NGO n ON r.donorNGO = n.ngoID
                    WHERE r.donorNGO = %s AND r.status = 'available'
                """
                cursor.execute(query, (ngo_id,))
            else:
                # Admin sees all available resources
                query = """
                    SELECT r.resourceID, rt.name AS resourceType, r.quantity, r.status, 
                           r.location, n.orgName AS donorNGO, r.donorNGO as donorNGOID
                    FROM ResourceStock r
                    JOIN ResourceType rt ON r.resourceTypeID = rt.resourceTypeID
                    LEFT JOIN NGO n ON r.donorNGO = n.ngoID
                    WHERE r.status = 'available'
                """
                cursor.execute(query)
            
            resources = cursor.fetchall()
            
            for resource in resources:
                self.tree.insert("", "end", values=(
                    resource["resourceID"],
                    resource["resourceType"],
                    resource["quantity"],
                    resource["status"],
                    resource["location"] or "N/A",
                    resource["donorNGO"] or "N/A"
                ))
            
            cursor.close()
        
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to load resources: {str(e)}")

    def view_ngos(self):
        """Show list of available NGOs"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT ngoID, orgName, region, verified
                FROM NGO
                WHERE verified = TRUE
                ORDER BY orgName
            """)
            
            ngos = cursor.fetchall()
            cursor.close()
            
            if not ngos:
                messagebox.showinfo("Information", "No verified NGOs found.")
                return
            
            # Create popup window
            ngo_window = tk.Toplevel(self)
            ngo_window.title("Available NGOs")
            ngo_window.geometry("500x400")
            ngo_window.configure(bg="#f5f5f5")
            
            tk.Label(ngo_window, text="Available NGOs", font=("Helvetica", 14, "bold"), 
                    bg="#f5f5f5").pack(pady=10)
            
            # NGO list
            ngo_frame = tk.Frame(ngo_window, bg="white")
            ngo_frame.pack(padx=20, pady=10, fill="both", expand=True)
            
            ngo_columns = ("ngoID", "orgName", "region")
            ngo_tree = ttk.Treeview(ngo_frame, columns=ngo_columns, show="headings", height=10)
            
            ngo_tree.heading("ngoID", text="NGO ID")
            ngo_tree.heading("orgName", text="Organization Name")
            ngo_tree.heading("region", text="Region")
            
            ngo_tree.column("ngoID", width=100)
            ngo_tree.column("orgName", width=250)
            ngo_tree.column("region", width=150)
            
            for ngo in ngos:
                ngo_tree.insert("", "end", values=(
                    ngo["ngoID"],
                    ngo["orgName"],
                    ngo["region"] or "N/A"
                ))
            
            ngo_tree.pack(fill="both", expand=True)
            
            tk.Button(ngo_window, text="Close", font=("Helvetica", 12), 
                     bg="#757575", fg="white", command=ngo_window.destroy).pack(pady=10)
        
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to load NGOs: {str(e)}")

    def transfer_resource(self):
        """Process resource transfer"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a resource to transfer.")
            return
        
        resource_data = self.tree.item(selected[0])["values"]
        resource_id = resource_data[0]
        available_qty = resource_data[2]
        
        # Get transfer details
        target_ngo = self.target_ngo_entry.get().strip()
        target_location = self.target_location_entry.get().strip()
        transfer_qty = self.quantity_entry.get().strip()
        
        # Validation
        if not target_ngo or not target_location or not transfer_qty:
            messagebox.showwarning("Missing Information", "Please fill in all transfer details.")
            return
        
        try:
            transfer_qty = int(transfer_qty)
            if transfer_qty <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive quantity.")
            return
        
        # Check if sufficient quantity available
        if transfer_qty > available_qty:
            messagebox.showerror("Insufficient Resources", 
                               f"Insufficient resources for transfer.\n"
                               f"Available: {available_qty}, Requested: {transfer_qty}")
            return
        
        # Verify target NGO exists
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT ngoID, orgName, verified FROM NGO WHERE ngoID = %s", (target_ngo,))
            target_ngo_data = cursor.fetchone()
            
            if not target_ngo_data:
                messagebox.showerror("Invalid NGO", "Target NGO ID not found.")
                cursor.close()
                return
            
            if not target_ngo_data["verified"]:
                messagebox.showwarning("Unverified NGO", 
                                     f"NGO '{target_ngo_data['orgName']}' is not verified. "
                                     "Only verified NGOs can receive resources.")
                cursor.close()
                return
            
            # Get source NGO
            from_ngo = self.logged_in_user.get("id") if self.role == "NGO" else resource_data[5]
            source_location = resource_data[4]
            
            # Confirm transfer
            confirm = messagebox.askyesno("Confirm Transfer", 
                                        f"Transfer {transfer_qty} units of {resource_data[1]} "
                                        f"from {source_location} to {target_location} "
                                        f"(NGO: {target_ngo_data['orgName']})?")
            if not confirm:
                cursor.close()
                return
            
            # Create transfer record
            cursor.execute("""
                INSERT INTO ResourceTransfer (resourceID, fromNGO, toNGO, fromLocation, toLocation, 
                                            quantity, status, transferredBy)
                VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s)
            """, (resource_id, from_ngo, target_ngo, source_location, target_location, 
                  transfer_qty, self.logged_in_user.get("id")))
            
            # Update resource quantity
            new_qty = available_qty - transfer_qty
            cursor.execute("""
                UPDATE ResourceStock 
                SET quantity = %s, status = CASE WHEN %s <= 5 THEN 'low' ELSE status END
                WHERE resourceID = %s
            """, (new_qty, new_qty, resource_id))
            
            self.connection.commit()
            cursor.close()
            
            messagebox.showinfo("Success", 
                              f"Resource transfer recorded successfully!\n"
                              f"Transfer status: Pending")
            self.load_resources()
            # Clear form
            self.target_ngo_entry.delete(0, tk.END)
            self.target_location_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
        
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to transfer resource: {str(e)}")

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
    app = TransferResourcesApp(logged_in_user={"role": "Admin", "name": "Admin", "id": 1, "verified": True})
    app.mainloop()

