# File: notify_stakeholders.py

import sys
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Add parent folder to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Backend services
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

# ---------- Notify Stakeholders App ----------
class NotifyStakeholdersApp(tk.Tk):
    def __init__(self, logged_in_user):
        super().__init__()
        self.title("Notify Stakeholders - DRMS")
        self.geometry("600x500")
        self.logged_in_user = logged_in_user
        self.configure(bg="#f5f5f5")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Notify Stakeholders", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=20)

        # Stakeholder type
        tk.Label(self, text="Select Stakeholder Type:", font=("Helvetica", 12), bg="#f5f5f5").pack(pady=(10,5))
        self.stakeholder_var = tk.StringVar(value="volunteer")
        tk.OptionMenu(self, self.stakeholder_var, "volunteer", "ngo", "victim").pack(pady=5)

        # Message area
        tk.Label(self, text="Message:", font=("Helvetica", 12), bg="#f5f5f5").pack(pady=(10,5))
        self.message_text = scrolledtext.ScrolledText(self, width=60, height=10, font=("Helvetica", 12))
        self.message_text.pack(pady=5)

        # Send button
        tk.Button(self, text="Send Notification", font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white",
                  activebackground="#45a049", command=self.send_notification).pack(pady=20)

        # Back button
        tk.Button(self, text="Back", font=("Helvetica", 12), bg="#2196F3", fg="white",
                  command=self.go_back).pack(pady=10)

    def send_notification(self):
        stakeholder_type = self.stakeholder_var.get()
        message_content = self.message_text.get("1.0", "end").strip()

        if not message_content:
            messagebox.showwarning("Empty Message", "Please enter a message before sending.")
            return

        try:
            stakeholders = user_service.get_users_by_role(stakeholder_type)
            if not stakeholders:
                messagebox.showinfo("No Stakeholders", f"No {stakeholder_type} found to notify.")
                return

            # Simulate sending notification (replace with real email/SMS later)
            for user in stakeholders:
                user_name = user[1] if isinstance(user, tuple) else user.get('name', 'User')
                print(f"Sent message to {user_name}: {message_content}")

            messagebox.showinfo("Success", f"Message sent to all {stakeholder_type}s successfully!")
            self.message_text.delete("1.0", "end")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send notification: {str(e)}")

    def go_back(self):
        """Return to Admin Options"""
        self.destroy()
        from frontend.login import AdminOptionsApp  # import here to avoid circular import
        app = AdminOptionsApp(logged_in_user=self.logged_in_user)
        app.mainloop()


# ---------- TEST ----------
if __name__ == "__main__":
    app = NotifyStakeholdersApp(logged_in_user={"role": "admin", "name": "Admin"})
    app.mainloop()
