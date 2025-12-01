import sys
import os
import tkinter as tk
from tkinter import messagebox, simpledialog

# Add parent folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.user_service import UserService
from data.db_connection import DatabaseConnection
from data.user_repository import UserRepository

from frontend.generate_reports import GenerateReportsApp
from frontend.language import LanguageManager

# Database connection
db = DatabaseConnection()
connection = db.connect()
if not connection:
    raise Exception("Cannot connect to database!")

user_repo = UserRepository(connection)
user_service = UserService(user_repo)

# Helper: normalize user object
def normalize_user(user):
    if isinstance(user, dict):
        return user
    elif isinstance(user, tuple):
        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "phone": user[3],
            "location": user[4],
            "lat": user[5],
            "lng": user[6],
            "lang": user[7],
            "role": user[8]
        }
    else:
        return {}

# ---------- Base App ----------
class BaseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()

    def change_language(self):
        lang = simpledialog.askstring(
            self.lang_manager.get("select_language_title"),
            self.lang_manager.get("select_language_prompt"),
            parent=self
        )
        if lang:
            success = self.lang_manager.set_language(lang.lower())
            if success:
                messagebox.showinfo(
                    self.lang_manager.get("language_changed_title"),
                    self.lang_manager.get("language_changed_message")
                )
                self.refresh_language()
            else:
                messagebox.showerror(
                    self.lang_manager.get("language_error_title"),
                    self.lang_manager.get("language_error_message")
                )

# ---------- Admin Options App ----------
class AdminOptionsApp(BaseApp):
    def __init__(self, logged_in_user, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user

        # Use passed DB connection or create new
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        self.geometry("400x650")
        self.configure(bg="#f5f5f5")
        self.create_widgets()

    def create_widgets(self):
        self.welcome_label = tk.Label(self, font=("Helvetica", 14, "bold"), bg="#f5f5f5")
        self.welcome_label.pack(pady=20)

        # Generate Reports Button
        self.generate_button = tk.Button(
            self, font=("Helvetica", 12), bg="#4CAF50", fg="white",
            command=self.open_generate_reports
        )
        self.generate_button.pack(pady=10, fill="x", padx=50)

        # Notify Stakeholders Button
        self.notify_button = tk.Button(
            self, font=("Helvetica", 12), bg="#2196F3", fg="white",
            command=self.open_notify_stakeholders
        )
        self.notify_button.pack(pady=10, fill="x", padx=50)

        # Language Settings Button
        self.language_button = tk.Button(
            self, font=("Helvetica", 12), bg="#FFC107", fg="white",
            command=self.change_language
        )
        self.language_button.pack(pady=10, fill="x", padx=50)

        # Prioritize Requests Button
        self.prioritize_button = tk.Button(
            self, font=("Helvetica", 12), bg="#9C27B0", fg="white",
            command=self.open_prioritize_requests
        )
        self.prioritize_button.pack(pady=10, fill="x", padx=50)

        # Verify Volunteer Button
        self.verify_volunteer_button = tk.Button(
            self, font=("Helvetica", 12), bg="#FF5722", fg="white",
            command=self.open_verify_volunteer
        )
        self.verify_volunteer_button.pack(pady=10, fill="x", padx=50)

        # Verify NGO Button
        self.verify_ngo_button = tk.Button(
            self, font=("Helvetica", 12), bg="#3F51B5", fg="white",
            command=self.open_verify_ngo
        )
        self.verify_ngo_button.pack(pady=10, fill="x", padx=50)

        self.refresh_language()

    def refresh_language(self):
        self.title(self.lang_manager.get("admin_options"))
        self.welcome_label.config(
            text=f"{self.lang_manager.get('welcome')}, {self.logged_in_user.get('name','Admin')}"
        )
        self.generate_button.config(text=self.lang_manager.get("generate_reports"))
        self.notify_button.config(text=self.lang_manager.get("notify_stakeholders"))
        self.language_button.config(text=self.lang_manager.get("language_settings"))
        self.prioritize_button.config(text="Prioritize Requests")
        self.verify_volunteer_button.config(text="Verify Volunteer")
        self.verify_ngo_button.config(text="Verify NGO")

    # ---------------- Button Actions ----------------
    def open_generate_reports(self):
        self.destroy()
        reports_app = GenerateReportsApp(logged_in_user=self.logged_in_user)
        reports_app.mainloop()

    def open_notify_stakeholders(self):
        self.destroy()
        from frontend.notify_stakeholders import NotifyStakeholdersApp
        notify_app = NotifyStakeholdersApp(logged_in_user=self.logged_in_user)
        notify_app.mainloop()

    def open_prioritize_requests(self):
        self.destroy()
        from frontend.prioritize_requests import PrioritizeRequestsApp
        app = PrioritizeRequestsApp(logged_in_user=self.logged_in_user, db_connection=self.connection)
        app.mainloop()

    def open_verify_volunteer(self):
        self.destroy()
        from frontend.verify_volunteer import VerifyVolunteerApp
        app = VerifyVolunteerApp(logged_in_user=self.logged_in_user, db_connection=self.connection)
        app.mainloop()

    def open_verify_ngo(self):
        self.destroy()
        from frontend.verify_ngo import VerifyNGOApp
        app = VerifyNGOApp(db_connection=self.connection)
        app.mainloop()

# ---------- Volunteer App ----------
class VolunteerApp(BaseApp):
    def __init__(self, logged_in_user):
        super().__init__()
        self.logged_in_user = logged_in_user
        self.geometry("400x250")
        self.configure(bg="#f5f5f5")
        self.create_widgets()

    def create_widgets(self):
        self.welcome_label = tk.Label(self, font=("Helvetica", 14, "bold"), bg="#f5f5f5")
        self.welcome_label.pack(pady=20)
        self.language_button = tk.Button(self, font=("Helvetica", 12), bg="#FFC107", fg="white",
                                         command=self.change_language)
        self.language_button.pack(pady=10, fill="x", padx=50)
        self.refresh_language()

    def refresh_language(self):
        self.title(f"Volunteer - {self.lang_manager.get('system_name')}")
        self.welcome_label.config(
            text=f"{self.lang_manager.get('welcome')}, {self.logged_in_user.get('name','Volunteer')}"
        )
        self.language_button.config(text=self.lang_manager.get("language_settings"))

# ---------- Login App ----------
class LoginApp(BaseApp):
    def __init__(self):
        super().__init__()
        self.geometry("400x450")
        self.resizable(False, False)
        self.configure(bg="#f5f5f5")
        self.create_widgets()

    def create_widgets(self):
        self.system_label = tk.Label(self, font=("Helvetica", 16, "bold"), bg="#f5f5f5", fg="#333")
        self.system_label.pack(pady=20)

        frame = tk.Frame(self, bg="white", bd=2, relief="groove")
        frame.pack(pady=20, padx=30, fill="both", expand=True)

        # Email
        self.email_label = tk.Label(frame, font=("Helvetica", 12), bg="white")
        self.email_label.pack(pady=(20,5))
        self.email_entry = tk.Entry(frame, font=("Helvetica", 12))
        self.email_entry.pack(pady=5, padx=20, fill="x")

        # Password
        self.password_label = tk.Label(frame, font=("Helvetica", 12), bg="white")
        self.password_label.pack(pady=(10,5))
        self.password_entry = tk.Entry(frame, font=("Helvetica", 12), show="*")
        self.password_entry.pack(pady=5, padx=20, fill="x")
        self.password_entry.bind('<Return>', lambda e: self.login())

        # Role
        self.role_label = tk.Label(frame, font=("Helvetica", 12), bg="white")
        self.role_label.pack(pady=(10,5))
        self.role_var = tk.StringVar(value="Admin")
        self.role_menu = tk.OptionMenu(frame, self.role_var, "Admin", "Volunteer", "NGO", "Victim")
        self.role_menu.pack(pady=5, padx=20, fill="x")

        # Login button
        self.login_button = tk.Button(frame, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white",
                                      activebackground="#45a049", command=self.login)
        self.login_button.pack(pady=(20,30), padx=20, fill="x")

        self.refresh_language()

    def refresh_language(self):
        self.title(self.lang_manager.get("login_title"))
        self.system_label.config(text=self.lang_manager.get("system_name"))
        self.email_label.config(text=self.lang_manager.get("email"))
        self.password_label.config(text=self.lang_manager.get("password"))
        self.role_label.config(text=self.lang_manager.get("role"))
        self.login_button.config(text=self.lang_manager.get("login_button"))

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()

        if not email or not password:
            messagebox.showwarning(self.lang_manager.get("login_failed_title"),
                                   self.lang_manager.get("login_missing_fields"))
            return

        try:
            user = user_service.authenticate_user(email, password)
            user = normalize_user(user)

            if user and user.get("role") == role:
                user_name = user.get('name', 'User')
                messagebox.showinfo(self.lang_manager.get("login_success_title"),
                                    f"{self.lang_manager.get('welcome')}, {user_name}!")
                self.destroy()

                if role == "Admin":
                    app = AdminOptionsApp(logged_in_user=user, db_connection=connection)
                    app.mainloop()
                elif role == "Volunteer":
                    app = VolunteerApp(logged_in_user=user)
                    app.mainloop()
                elif role == "NGO":
                    from frontend.manage_resources import ManageResourcesApp
                    app = ManageResourcesApp(logged_in_user=user, db_connection=connection)
                    app.mainloop()
                elif role == "Victim":
                    messagebox.showinfo("Info", "Victim window not implemented yet!")
                else:
                    messagebox.showerror("Error", "Unknown role!")
            else:
                messagebox.showerror(self.lang_manager.get("login_failed_title"),
                                     self.lang_manager.get("login_invalid"))
        except Exception as e:
            messagebox.showerror(self.lang_manager.get("login_error_title"),
                                 f"{self.lang_manager.get('login_error_message')} {str(e)}")

# Run the login
if __name__ == "__main__":
    login_app = LoginApp()
    login_app.mainloop()
