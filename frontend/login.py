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
        
        # Press Enter to login
        self.password_entry.bind('<Return>', lambda e: self.login())

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

        # Debug prints
        print(f"=== Login Attempt ===")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Password length: {len(password)}")

        # ---------- Authenticate user using the repository method ----------
        try:
            user = user_service.authenticate_user(email, password)
            
            if user:
                # Login success
                print(f"✓ Login successful for: {user}")
                
                # Extract user info based on how your database returns data
                # If user is a tuple: (userID, name, email, phone, location, lat, lng, lang, role, password_hash, ...)
                # If user is a dict: {'userID': 1, 'name': 'Alice', ...}
                
                if isinstance(user, dict):
                    user_name = user.get('name', 'User')
                    user_role = user.get('role', 'Unknown')
                else:
                    # Assuming tuple format: index 1 is name, index 8 is role
                    user_name = user[1] if len(user) > 1 else 'User'
                    user_role = user[8] if len(user) > 8 else 'Unknown'
                
                messagebox.showinfo("Login Success", f"Welcome, {user_name}!")
                self.destroy()  # Close login window

                # Open main DRMS GUI
                app = DRMSApp(logged_in_user=user)
                app.mainloop()
            else:
                # Login failed
                print(f"✗ Login failed - invalid credentials")
                messagebox.showerror("Login Failed", "Incorrect password.")
                
        except Exception as e:
            print(f"✗ Login error: {e}")
            messagebox.showerror("Login Error", f"An error occurred: {str(e)}")


# ---------- RUN LOGIN ----------
if __name__ == "__main__":
    login_app = LoginApp()
    login_app.mainloop()