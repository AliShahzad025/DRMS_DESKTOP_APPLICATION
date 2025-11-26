import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add parent folder to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import your app and services
from frontend.drms_app import DRMSApp
from services.user_service import UserService
from data.db_connection import DatabaseConnection
from data.user_repository import UserRepository

# ---------- Backend setup ----------
db = DatabaseConnection()
connection = db.connect()
if not connection:
    raise Exception("Cannot connect to database!")

user_repo = UserRepository(connection)
user_service = UserService(user_repo)

# ---------- Password verification ----------
# Plain-text comparison (since your SQL uses placeholders)
def check_password(plain_password, stored_password):
    return plain_password == stored_password  # Direct comparison

# ---------- Login App ----------
class LoginApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DRMS Login")
        self.geometry("400x350")
        self.resizable(False, False)
        self.configure(bg="#f5f5f5")
        self.create_widgets()

    def create_widgets(self):
        # Title
        tk.Label(self, text="Disaster Relief Management System", font=("Helvetica", 16, "bold"),
                 bg="#f5f5f5", fg="#333").pack(pady=20)

        # Input frame
        frame = tk.Frame(self, bg="white", bd=2, relief="groove")
        frame.pack(pady=20, padx=30, fill="both", expand=True)

        tk.Label(frame, text="Email", font=("Helvetica", 12), bg="white").pack(pady=(20,5))
        self.email_entry = tk.Entry(frame, font=("Helvetica", 12))
        self.email_entry.pack(pady=5, padx=20, fill="x")

        tk.Label(frame, text="Password", font=("Helvetica", 12), bg="white").pack(pady=(10,5))
        self.password_entry = tk.Entry(frame, font=("Helvetica", 12), show="*")
        self.password_entry.pack(pady=5, padx=20, fill="x")

        tk.Button(frame, text="Login", font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white",
                  activebackground="#45a049", command=self.login).pack(pady=20, padx=20, fill="x")

        tk.Label(self, text="© 2025 Disaster Relief Management System", font=("Helvetica", 8),
                 bg="#f5f5f5", fg="#888").pack(side="bottom", pady=10)

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showwarning("Login Failed", "Please enter both email and password.")
            return

        # ---------- Fetch user ----------
        users = user_service.list_users()
        user = None
        for u in users:
            if u[2] == email:  # Assuming u[2] is email
                user = u
                break

        if not user:
            messagebox.showerror("Login Failed", "User not found.")
            return

        # ---------- Check password ----------
        if not check_password(password, user[8]):  # Assuming password_hash is in u[8]
            messagebox.showerror("Login Failed", "Incorrect password.")
            return

        # ---------- Login success ----------
        messagebox.showinfo("Login Success", f"Welcome, {user[1]}!")
        self.destroy()  # Close login window

        # Open main DRMS GUI
        app = DRMSApp(logged_in_user=user)
        app.mainloop()


# ---------- RUN LOGIN ----------
if __name__ == "__main__":
    login_app = LoginApp()
    login_app.mainloop()
