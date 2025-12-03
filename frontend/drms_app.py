import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tkinter as tk
from tkinter import ttk, messagebox
from services.user_service import UserService
from data.db_connection import DatabaseConnection
from data.user_repository import UserRepository
from frontend.manage_resources import ManageResourcesApp

# ---------- DRMS Main GUI ----------
class DRMSApp(tk.Tk):
    def __init__(self, logged_in_user=None):
        super().__init__()
        self.title("Disaster Relief Management System")
        self.geometry("900x500")
        self.logged_in_user = logged_in_user  # tuple: (id, name, email, phone, location, role, password_hash)

        # Initialize backend
        self.db = DatabaseConnection()
        self.connection = self.db.connect()
        if not self.connection:
            messagebox.showerror("Error", "Cannot connect to database!")
            self.destroy()
            return

        self.user_repo = UserRepository(self.connection)
        self.user_service = UserService(self.user_repo)

        self.create_widgets()

    def create_widgets(self):
        # Top frame with logged-in user info
        top_frame = tk.Frame(self, bg="#f5f5f5")
        top_frame.pack(fill="x")

        if self.logged_in_user:
            name = self.logged_in_user[1]
            role = self.logged_in_user[5]
            tk.Label(top_frame, text=f"Logged in as: {name} ({role})", font=("Helvetica", 12, "bold"), bg="#f5f5f5", fg="#333").pack(pady=10, padx=10, anchor="w")

        # Buttons frame
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack(fill="x", pady=5)

        tk.Button(btn_frame, text="Refresh Users", font=("Helvetica", 11, "bold"), bg="#4CAF50", fg="white", command=self.load_users).pack(side="left", padx=10)
        
        # Add Manage Resources Button
        if self.logged_in_user and (self.logged_in_user[5] == "Admin" or self.logged_in_user[5] == "NGO"):
            tk.Button(btn_frame, text="Manage Resources", font=("Helvetica", 11, "bold"), bg="#007BFF", fg="white", command=self.open_manage_resources).pack(side="left", padx=10)

        tk.Button(btn_frame, text="Exit", font=("Helvetica", 11, "bold"), bg="#f44336", fg="white", command=self.destroy).pack(side="right", padx=10)

        # Users table
        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Email", "Phone", "Location", "Role"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Location", text="Location")
        self.tree.heading("Role", text="Role")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Initial load
        self.load_users()

    def load_users(self):
        # Clear table
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Fetch users from backend
        users = self.user_service.list_users()
        for u in users:
            self.tree.insert("", "end", values=(u['userID'], u['name'], u['email'], u['phone'], u['location'], u['role']))

    def open_manage_resources(self):
        self.withdraw()  # Hide the main window
        # Pass the logged_in_user as a dictionary
        user_dict = {
            "id": self.logged_in_user[0],
            "name": self.logged_in_user[1],
            "email": self.logged_in_user[2],
            "phone": self.logged_in_user[3],
            "location": self.logged_in_user[4],
            "role": self.logged_in_user[5],
            "password_hash": self.logged_in_user[6] if len(self.logged_in_user) > 6 else None,
            "verified": self.logged_in_user[10] if self.logged_in_user[5] == "NGO" and len(self.logged_in_user) > 10 else False
        }
        manage_app = ManageResourcesApp(logged_in_user=user_dict, db_connection=self.connection, on_close_callback=self.deiconify)
        # The manage_app.mainloop() is not needed here as it will block the main app.
        # The Toplevel window will be managed by the main Tkinter event loop.

    def on_manage_resources_close(self, manage_app):
        manage_app.destroy()
        self.deiconify() # Show the main window again
#done