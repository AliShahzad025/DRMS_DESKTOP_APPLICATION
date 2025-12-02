import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.db_connection import DatabaseConnection
import mysql.connector


class AddResourcesApp(tk.Tk):
    """
    Use Case UC-9f: Add Resources

    Admin / NGO can add new resources into the system.
    - Displays a form for type, quantity, location
    - Validates input
    - On success inserts into ResourceStock
    """

    def __init__(self, logged_in_user=None, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user or {}
        self.role = self.logged_in_user.get("role")

        # Permission check: Admin or verified NGO only
        if self.role not in ["Admin", "NGO"]:
            messagebox.showerror("Unauthorized", "You do not have rights to add resources.")
            self.destroy()
            return

        if self.role == "NGO" and not self.logged_in_user.get("verified"):
            messagebox.showerror("Unauthorized", "Your NGO must be verified to add resources.")
            self.destroy()
            return

        self.title("Add Resources - DRMS")
        self.geometry("600x450")
        self.configure(bg="#f5f5f5")

        # Database connection
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        if not self.connection:
            messagebox.showerror("Database Error", "Cannot connect to database!")
            self.destroy()
            return

        self.resource_types = []
        self.create_widgets()
        self.load_resource_types()

    def create_widgets(self):
        # Title
        tk.Label(
            self,
            text="Add New Resource",
            font=("Helvetica", 16, "bold"),
            bg="#f5f5f5",
        ).pack(pady=15)

        # Info
        tk.Label(
            self,
            text="Enter resource details. All fields are required.",
            font=("Helvetica", 10),
            bg="#f5f5f5",
            fg="#555",
        ).pack(pady=5)

        form_frame = tk.Frame(self, bg="#f5f5f5")
        form_frame.pack(pady=15, padx=30, fill="x")

        # Resource type
        tk.Label(form_frame, text="Resource Type:", font=("Helvetica", 11), bg="#f5f5f5").grid(
            row=0, column=0, padx=5, pady=10, sticky="w"
        )
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(form_frame, textvariable=self.type_var, state="readonly", width=30)
        self.type_combo.grid(row=0, column=1, padx=5, pady=10)

        # Quantity
        tk.Label(form_frame, text="Quantity:", font=("Helvetica", 11), bg="#f5f5f5").grid(
            row=1, column=0, padx=5, pady=10, sticky="w"
        )
        self.quantity_entry = tk.Entry(form_frame, font=("Helvetica", 11), width=15)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=10, sticky="w")

        # Location
        tk.Label(form_frame, text="Location:", font=("Helvetica", 11), bg="#f5f5f5").grid(
            row=2, column=0, padx=5, pady=10, sticky="w"
        )
        self.location_entry = tk.Entry(form_frame, font=("Helvetica", 11), width=30)
        self.location_entry.grid(row=2, column=1, padx=5, pady=10, sticky="w")

        # Optional: latitude / longitude
        tk.Label(form_frame, text="Latitude (optional):", font=("Helvetica", 11), bg="#f5f5f5").grid(
            row=3, column=0, padx=5, pady=10, sticky="w"
        )
        self.lat_entry = tk.Entry(form_frame, font=("Helvetica", 11), width=15)
        self.lat_entry.grid(row=3, column=1, padx=5, pady=10, sticky="w")

        tk.Label(form_frame, text="Longitude (optional):", font=("Helvetica", 11), bg="#f5f5f5").grid(
            row=4, column=0, padx=5, pady=10, sticky="w"
        )
        self.long_entry = tk.Entry(form_frame, font=("Helvetica", 11), width=15)
        self.long_entry.grid(row=4, column=1, padx=5, pady=10, sticky="w")

        # Buttons
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame,
            text="Save Resource",
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=14,
            command=self.save_resource,
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            btn_frame,
            text="Clear",
            font=("Helvetica", 12),
            bg="#FF9800",
            fg="white",
            width=10,
            command=self.clear_form,
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            btn_frame,
            text="Back",
            font=("Helvetica", 12),
            bg="#757575",
            fg="white",
            width=10,
            command=self.go_back,
        ).grid(row=0, column=2, padx=10)

    def load_resource_types(self):
        """Load all resource types into dropdown."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT resourceTypeID, name FROM ResourceType ORDER BY name")
            rows = cursor.fetchall()
            cursor.close()

            self.resource_types = rows
            names = [row["name"] for row in rows]
            self.type_combo["values"] = names

            if names:
                self.type_combo.current(0)

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to load resource types: {str(e)}")

    def clear_form(self):
        self.quantity_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)
        self.lat_entry.delete(0, tk.END)
        self.long_entry.delete(0, tk.END)
        if self.type_combo["values"]:
            self.type_combo.current(0)

    def save_resource(self):
        """Validate form and insert new resource."""
        resource_type_name = self.type_var.get().strip()
        quantity_text = self.quantity_entry.get().strip()
        location = self.location_entry.get().strip()
        lat_text = self.lat_entry.get().strip()
        long_text = self.long_entry.get().strip()

        # Basic validation
        if not resource_type_name or not quantity_text or not location:
            messagebox.showerror(
                "Invalid or missing details, please re-enter.",
                "Resource type, quantity, and location are required.",
            )
            return

        # Find resourceTypeID
        resource_type_id = None
        for rt in self.resource_types:
            if rt["name"] == resource_type_name:
                resource_type_id = rt["resourceTypeID"]
                break

        if resource_type_id is None:
            messagebox.showerror("Error", "Selected resource type is invalid.")
            return

        # Validate quantity
        try:
            quantity = int(quantity_text)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            messagebox.showerror(
                "Invalid or missing details, please re-enter.",
                "Quantity must be a positive integer.",
            )
            return

        # Optional lat/long
        latitude = None
        longitude = None
        try:
            if lat_text:
                latitude = float(lat_text)
            if long_text:
                longitude = float(long_text)
        except ValueError:
            messagebox.showerror(
                "Invalid or missing details, please re-enter.",
                "Latitude/Longitude must be numeric.",
            )
            return

        # Determine donor NGO and lastVerifiedBy
        donor_ngo = None
        last_verified_by = None

        if self.role == "NGO":
            donor_ngo = self.logged_in_user.get("id")
        elif self.role == "Admin":
            # Admin can be recorded as verifier
            last_verified_by = self.logged_in_user.get("id")

        # Insert into ResourceStock
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO ResourceStock (
                    resourceTypeID,
                    donorNGO,
                    quantity,
                    status,
                    lastVerifiedBy,
                    location,
                    latitude,
                    longitude
                )
                VALUES (%s, %s, %s, 'available', %s, %s, %s, %s)
                """,
                (
                    resource_type_id,
                    donor_ngo,
                    quantity,
                    last_verified_by,
                    location,
                    latitude if latitude is not None else 0.0,
                    longitude if longitude is not None else 0.0,
                ),
            )
            self.connection.commit()
            cursor.close()

            messagebox.showinfo("Success", "New resource added successfully!")
            self.clear_form()

        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to add resource. Please try again.\n{str(e)}")

    def go_back(self):
        """Return to previous screen."""
        self.destroy()
        if self.role == "Admin":
            from frontend.login import AdminOptionsApp

            app = AdminOptionsApp(logged_in_user=self.logged_in_user, db_connection=self.connection)
            app.mainloop()
        elif self.role == "NGO":
            from frontend.manage_resources import ManageResourcesApp

            app = ManageResourcesApp(logged_in_user=self.logged_in_user, db_connection=self.connection)
            app.mainloop()


if __name__ == "__main__":
    app = AddResourcesApp(logged_in_user={"role": "Admin", "id": 1, "name": "Admin", "verified": True})
    app.mainloop()


