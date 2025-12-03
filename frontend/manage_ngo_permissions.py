import sys
import os
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import sv_ttk

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.db_connection import DatabaseConnection
from services.user_service import UserService
from data.user_repository import UserRepository
from frontend.login import BaseApp, ModernCardFrame, apply_windows11_theme, LoginApp # Import LoginApp for returning

class ManageNGOPermissionsApp(BaseApp):
    def __init__(self, master, logged_in_user, db_connection):
        super().__init__()
        self.master = master # Store the master window (AdminOptionsApp)
        self.logged_in_user = logged_in_user
        self.db_connection = db_connection
        self.connection = self.db_connection.connect()

        if not self.connection:
            messagebox.showerror("Database Error", "Failed to connect to the database.")
            self.master.destroy()
            return

        self.user_repo = UserRepository(self.connection)
        self.user_service = UserService(self.user_repo)

        self.title("DRMS - Manage NGO Resource Permissions")
        self.geometry("1200x800")
        self.resizable(True, True)

        self.colors = apply_windows11_theme(self)
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.winfo_screenheight() // 2) - (800 // 2)
        self.geometry(f"+{x}+{y}")

        self.create_widgets()
        self.create_status_bar()
        self.load_ngos()

    def create_widgets(self):
        self.create_header(
            title="⚙️ MANAGE NGO RESOURCE PERMISSIONS",
            subtitle="Grant or revoke resource management access for NGOs",
            show_back_button=True,
            back_command=self.go_back_to_admin_dashboard
        )

        main_container = tk.Frame(self, bg=self.colors["background"])
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        card = ModernCardFrame(main_container, padding=20)
        card.pack(fill="both", expand=True)

        # NGO List Treeview
        self.tree = ttk.Treeview(
            card,
            columns=("ID", "NGO Name", "Organization Name", "Verified", "Can Manage Resources"),
            show="headings",
            selectmode="browse"
        )
        self.tree.heading("ID", text="User ID")
        self.tree.heading("NGO Name", text="User Name")
        self.tree.heading("Organization Name", text="Organization Name")
        self.tree.heading("Verified", text="Verified")
        self.tree.heading("Can Manage Resources", text="Can Manage Resources")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("NGO Name", width=150)
        self.tree.column("Organization Name", width=200)
        self.tree.column("Verified", width=100, anchor="center")
        self.tree.column("Can Manage Resources", width=150, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Action Buttons
        button_frame = tk.Frame(card, bg="white")
        button_frame.pack(fill="x", pady=10)

        grant_btn = tk.Button(
            button_frame,
            text="Grant Permission",
            command=self.grant_permission,
            font=("Segoe UI", 12, "bold"),
            bg="#10B981", fg="white", activebackground="#059669", activeforeground="white",
            relief="flat", padx=15, pady=8, cursor="hand2"
        )
        grant_btn.pack(side="left", padx=5)

        revoke_btn = tk.Button(
            button_frame,
            text="Revoke Permission",
            command=self.revoke_permission,
            font=("Segoe UI", 12, "bold"),
            bg="#EF4444", fg="white", activebackground="#DC2626", activeforeground="white",
            relief="flat", padx=15, pady=8, cursor="hand2"
        )
        revoke_btn.pack(side="left", padx=5)

    def load_ngos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            ngos = self.user_service.get_all_ngos_with_permission()
            if ngos:
                for ngo in ngos:
                    # Assuming ngo is a dictionary or an object with attributes
                    self.tree.insert("", "end", values=(
                        ngo['userID'],
                        ngo['name'],
                        ngo['orgName'],
                        "Yes" if ngo['verified'] else "No",
                        "Yes" if ngo['can_manage_resources'] else "No"
                    ))
            self.status_label.config(text="NGO list loaded.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load NGOs: {e}", parent=self)
            self.status_label.config(text=f"Error: {e}")

    def grant_permission(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an NGO from the list.", parent=self)
            return

        ngo_id = self.tree.item(selected_item, "values")[0] # Assuming NGO ID is the first column
        try:
            self.user_service.update_ngo_resource_permission(ngo_id, True)
            messagebox.showinfo("Success", f"Permission granted for NGO ID: {ngo_id}", parent=self)
            self.load_ngos() # Reload list to reflect changes
            self.status_label.config(text=f"Permission granted for NGO ID: {ngo_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to grant permission: {e}", parent=self)
            self.status_label.config(text=f"Error: {e}")

    def revoke_permission(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an NGO from the list.", parent=self)
            return

        ngo_id = self.tree.item(selected_item, "values")[0]
        try:
            self.user_service.update_ngo_resource_permission(ngo_id, False)
            messagebox.showinfo("Success", f"Permission revoked for NGO ID: {ngo_id}", parent=self)
            self.load_ngos()
            self.status_label.config(text=f"Permission revoked for NGO ID: {ngo_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to revoke permission: {e}", parent=self)
            self.status_label.config(text=f"Error: {e}")

    def go_back_to_admin_dashboard(self):
        if messagebox.askyesno("Confirm", "Return to Admin Dashboard?"):
            self.destroy()
            # Re-instantiate AdminOptionsApp - assuming it takes logged_in_user and db_connection
            from frontend.login import AdminOptionsApp
            admin_app = AdminOptionsApp(logged_in_user=self.logged_in_user, db_connection=self.db_connection)
            admin_app.mainloop()

    def on_closing(self):
        if self.connection:
            self.db_connection.close()
        self.master.destroy()

if __name__ == "__main__":
    # This part is for testing the UI independently
    # In the actual application, this will be called from AdminOptionsApp
    root = tk.Tk()
    db = DatabaseConnection()
    conn = db.connect()

    # Mock logged_in_user for testing purposes
    mock_user = {
        "userID": 1,
        "name": "Test Admin",
        "email": "admin@example.com",
        "role": "Admin"
    }

    app = ManageNGOPermissionsApp(root, logged_in_user=mock_user, db_connection=db)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
    if conn:
        db.close()
