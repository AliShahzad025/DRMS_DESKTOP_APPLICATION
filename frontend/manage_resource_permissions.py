# File: frontend/manage_resource_permissions.py
# Use Case UC-9a: Manage Resources with Permission

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data.db_connection import DatabaseConnection
import mysql.connector

class ManageResourcePermissionsApp(tk.Tk):
    def __init__(self, logged_in_user=None, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user
        
        # Verify admin role
        if not logged_in_user or logged_in_user.get("role") != "Admin":
            messagebox.showerror("Unauthorized", "Only Admin can manage resource permissions.")
            self.destroy()
            return
        
        self.title("Manage Resource Permissions - DRMS")
        self.geometry("900x600")
        self.configure(bg="#f5f5f5")
        
        # DB setup
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        if not self.connection:
            messagebox.showerror("Database Error", "Cannot connect to database!")
            self.destroy()
            return
        
        self.create_widgets()
        self.load_ngos()

    def create_widgets(self):
        # Title
        tk.Label(self, text="Manage Resource Permissions", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=15)
        
        # Info label
        tk.Label(self, text="Select an NGO to review and manage resource permissions", 
                font=("Helvetica", 10), bg="#f5f5f5", fg="#666").pack(pady=5)
        
        # NGO Table
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        columns = ("ngoID", "orgName", "verified", "region", "contact_person", "permission_status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("ngoID", text="NGO ID")
        self.tree.heading("orgName", text="Organization Name")
        self.tree.heading("verified", text="Verified")
        self.tree.heading("region", text="Region")
        self.tree.heading("contact_person", text="Contact Person")
        self.tree.heading("permission_status", text="Permission Status")
        
        self.tree.column("ngoID", width=80)
        self.tree.column("orgName", width=200)
        self.tree.column("verified", width=100)
        self.tree.column("region", width=120)
        self.tree.column("contact_person", width=150)
        self.tree.column("permission_status", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons frame
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="View NGO Details", font=("Helvetica", 12), 
                 bg="#2196F3", fg="white", width=18, command=self.view_ngo_details).grid(row=0, column=0, padx=5)
        
        tk.Button(btn_frame, text="Grant Permission", font=("Helvetica", 12), 
                 bg="#4CAF50", fg="white", width=18, command=self.grant_permission).grid(row=0, column=1, padx=5)
        
        tk.Button(btn_frame, text="Revoke Permission", font=("Helvetica", 12), 
                 bg="#F44336", fg="white", width=18, command=self.revoke_permission).grid(row=0, column=2, padx=5)
        
        tk.Button(btn_frame, text="Refresh", font=("Helvetica", 12), 
                 bg="#FF9800", fg="white", width=18, command=self.load_ngos).grid(row=0, column=3, padx=5)
        
        tk.Button(btn_frame, text="Back", font=("Helvetica", 12), 
                 bg="#757575", fg="white", width=18, command=self.go_back).grid(row=0, column=4, padx=5)

    def load_ngos(self):
        """Load all NGOs with their permission status"""
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT n.ngoID, n.orgName, n.verified, n.region, n.contact_person, n.registration_doc
                FROM NGO n
                JOIN UserAccount u ON n.ngoID = u.userID
                ORDER BY n.orgName
            """)
            
            ngos = cursor.fetchall()
            
            for ngo in ngos:
                # Permission status is based on verified field
                permission_status = "Granted" if ngo["verified"] else "Pending"
                
                self.tree.insert("", "end", values=(
                    ngo["ngoID"],
                    ngo["orgName"],
                    "Yes" if ngo["verified"] else "No",
                    ngo["region"] or "N/A",
                    ngo["contact_person"] or "N/A",
                    permission_status
                ))
            
            cursor.close()
            
            if not ngos:
                messagebox.showinfo("Information", "No NGOs found in the system.")
        
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to load NGOs: {str(e)}")

    def view_ngo_details(self):
        """Display detailed NGO information"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an NGO first.")
            return
        
        ngo_data = self.tree.item(selected[0])["values"]
        ngo_id = ngo_data[0]
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT n.*, u.name, u.email, u.phone, u.location
                FROM NGO n
                JOIN UserAccount u ON n.ngoID = u.userID
                WHERE n.ngoID = %s
            """, (ngo_id,))
            
            ngo = cursor.fetchone()
            cursor.close()
            
            if not ngo:
                messagebox.showerror("Error", "NGO details not found.")
                return
            
            # Create details window
            details_window = tk.Toplevel(self)
            details_window.title("NGO Details")
            details_window.geometry("500x500")
            details_window.configure(bg="#f5f5f5")
            
            tk.Label(details_window, text="NGO Details", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=15)
            
            # Details frame
            details_frame = tk.Frame(details_window, bg="white", bd=2, relief="groove")
            details_frame.pack(padx=20, pady=10, fill="both", expand=True)
            
            info_text = f"""
Organization Name: {ngo['orgName']}

Verified Status: {'Yes' if ngo['verified'] else 'No'}
Permission Status: {'Granted' if ngo['verified'] else 'Pending'}

Region: {ngo['region'] or 'N/A'}
Contact Person: {ngo['contact_person'] or 'N/A'}

Registration Document: {ngo['registration_doc'] or 'Not provided'}

Contact Information:
  Name: {ngo['name']}
  Email: {ngo['email']}
  Phone: {ngo['phone'] or 'N/A'}
  Location: {ngo['location'] or 'N/A'}
            """
            
            tk.Label(details_frame, text=info_text, justify="left", bg="white",
                    font=("Helvetica", 11), anchor="nw").pack(padx=20, pady=20, fill="both", expand=True)
            
            # Check if request is incomplete
            if not ngo['registration_doc']:
                tk.Label(details_frame, text="⚠ Permission request incomplete: Missing registration document", 
                        bg="white", fg="#F44336", font=("Helvetica", 10, "bold")).pack(pady=10)
            
            tk.Button(details_window, text="Close", font=("Helvetica", 12), 
                     bg="#757575", fg="white", command=details_window.destroy).pack(pady=10)
        
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to load NGO details: {str(e)}")

    def grant_permission(self):
        """Grant resource management permission to NGO"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an NGO first.")
            return
        
        ngo_data = self.tree.item(selected[0])["values"]
        ngo_id = ngo_data[0]
        org_name = ngo_data[1]
        
        # Confirm action
        confirm = messagebox.askyesno("Confirm Permission", 
                                     f"Grant resource management permission to {org_name}?")
        if not confirm:
            return
        
        try:
            cursor = self.connection.cursor()
            
            # Check if registration document exists
            cursor.execute("SELECT registration_doc FROM NGO WHERE ngoID = %s", (ngo_id,))
            result = cursor.fetchone()
            
            if not result or not result[0]:
                messagebox.showwarning("Incomplete Request", 
                                     "Permission request incomplete: Missing registration document.\n"
                                     "Please ensure the NGO has provided all required documents.")
                cursor.close()
                return
            
            # Update verified status
            cursor.execute("UPDATE NGO SET verified = TRUE WHERE ngoID = %s", (ngo_id,))
            self.connection.commit()
            cursor.close()
            
            messagebox.showinfo("Success", f"Resource management permission granted to {org_name}!")
            self.load_ngos()
        
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", 
                                f"Error updating permissions. Try again later.\n{str(e)}")

    def revoke_permission(self):
        """Revoke resource management permission from NGO"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an NGO first.")
            return
        
        ngo_data = self.tree.item(selected[0])["values"]
        ngo_id = ngo_data[0]
        org_name = ngo_data[1]
        
        # Confirm action
        confirm = messagebox.askyesno("Confirm Revocation", 
                                     f"Revoke resource management permission from {org_name}?")
        if not confirm:
            return
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE NGO SET verified = FALSE WHERE ngoID = %s", (ngo_id,))
            self.connection.commit()
            cursor.close()
            
            messagebox.showinfo("Success", f"Resource management permission revoked from {org_name}!")
            self.load_ngos()
        
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", 
                                f"Error updating permissions. Try again later.\n{str(e)}")

    def go_back(self):
        """Return to Admin Options"""
        self.destroy()
        from frontend.login import AdminOptionsApp
        app = AdminOptionsApp(logged_in_user=self.logged_in_user, db_connection=self.connection)
        app.mainloop()


# ---------- TEST ----------
if __name__ == "__main__":
    app = ManageResourcePermissionsApp(logged_in_user={"role": "Admin", "name": "Admin", "id": 1})
    app.mainloop()

