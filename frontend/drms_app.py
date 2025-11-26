import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tkinter as tk
from tkinter import ttk, messagebox
from services.user_service import UserService
from data.db_connection import DatabaseConnection
from data.user_repository import UserRepository

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
            self.tree.insert("", "end", values=(u[0], u[1], u[2], u[3], u[4], u[5]))
