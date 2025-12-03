import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.db_connection import DatabaseConnection
import mysql.connector


class UpdateResourcesApp(tk.Tk):
    """
    Use Case UC-9e: Update Resources

    Admin / NGO can update resource info (quantity, status, location).
    - Shows list of resources
    - Allows editing selected fields
    - Validates input (e.g. non-negative quantity)
    """

    def __init__(self, logged_in_user=None, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user or {}
        self.role = self.logged_in_user.get("role")

        # Permission check: Admin or verified NGO only
        if self.role not in ["Admin", "NGO"]:
            messagebox.showerror("Unauthorized", "You do not have rights to update resources.")
            self.destroy()
            return

        if self.role == "NGO" and not self.logged_in_user.get("verified"):
            messagebox.showerror("Unauthorized", "Your NGO must be verified to update resources.")
            self.destroy()
            return

        self.title("Update Resources - DRMS")
        self.geometry("1000x600")
        self.configure(bg="#f5f5f5")

        # Database connection
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        if not self.connection:
            messagebox.showerror("Database Error", "Cannot connect to database!")
            self.destroy()
            return

        self.create_widgets()
        self.load_resources()

    def create_widgets(self):
        # Title
        tk.Label(
            self,
            text="Update Resources",
            font=("Helvetica", 16, "bold"),
            bg="#f5f5f5",
        ).pack(pady=15)

        # Info
        tk.Label(
            self,
            text="Select a resource from the list and edit its details. Quantity must be zero or positive.",
            font=("Helvetica", 10),
            bg="#f5f5f5",
            fg="#555",
        ).pack(pady=5)

        # Table
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        columns = ("resourceID", "resourceType", "quantity", "status", "location")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        self.tree.heading("resourceID", text="Resource ID")
        self.tree.heading("resourceType", text="Resource Type")
        self.tree.heading("quantity", text="Quantity")
        self.tree.heading("status", text="Status")
        self.tree.heading("location", text="Location")

        self.tree.column("resourceID", width=100)
        self.tree.column("resourceType", width=200)
        self.tree.column("quantity", width=100)
        self.tree.column("status", width=130)
        self.tree.column("location", width=250)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Edit form
        form_frame = tk.Frame(self, bg="#f5f5f5")
        form_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(form_frame, text="New Quantity:", font=("Helvetica", 10), bg="#f5f5f5").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.quantity_entry = tk.Entry(form_frame, font=("Helvetica", 10), width=15)
        self.quantity_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="New Status:", font=("Helvetica", 10), bg="#f5f5f5").grid(
            row=0, column=2, padx=5, pady=5, sticky="w"
        )
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(
            form_frame,
            textvariable=self.status_var,
            values=["available", "reserved", "low", "out_of_stock"],
            state="readonly",
            width=15,
        )
        self.status_combo.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="New Location:", font=("Helvetica", 10), bg="#f5f5f5").grid(
            row=0, column=4, padx=5, pady=5, sticky="w"
        )
        self.location_entry = tk.Entry(form_frame, font=("Helvetica", 10), width=25)
        self.location_entry.grid(row=0, column=5, padx=5, pady=5)

        # Buttons
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame,
            text="Apply Changes",
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=16,
            command=self.apply_update,
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            btn_frame,
            text="Refresh",
            font=("Helvetica", 12),
            bg="#2196F3",
            fg="white",
            width=16,
            command=self.load_resources,
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            btn_frame,
            text="Back",
            font=("Helvetica", 12),
            bg="#757575",
            fg="white",
            width=16,
            command=self.go_back,
        ).grid(row=0, column=2, padx=5)

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def load_resources(self):
        """Load resources visible to the current user."""
        self.clear_table()

        try:
            cursor = self.connection.cursor(dictionary=True)

            if self.role == "NGO":
                ngo_id = self.logged_in_user.get("id")
                query = """
                    SELECT r.resourceID,
                           rt.name AS resourceType,
                           r.quantity,
                           r.status,
                           r.location
                    FROM ResourceStock r
                    JOIN ResourceType rt ON r.resourceTypeID = rt.resourceTypeID
                    WHERE r.donorNGO = %s
                    ORDER BY r.resourceID
                """
                cursor.execute(query, (ngo_id,))
            else:
                query = """
                    SELECT r.resourceID,
                           rt.name AS resourceType,
                           r.quantity,
                           r.status,
                           r.location
                    FROM ResourceStock r
                    JOIN ResourceType rt ON r.resourceTypeID = rt.resourceTypeID
                    ORDER BY r.resourceID
                """
                cursor.execute(query)

            rows = cursor.fetchall()
            cursor.close()

            for row in rows:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row["resourceID"],
                        row["resourceType"],
                        row["quantity"],
                        row["status"],
                        row["location"] or "N/A",
                    ),
                )

            if not rows:
                messagebox.showinfo("Information", "No resources found.")

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to load resources: {str(e)}")

    def apply_update(self):
        """Update selected resource with new values."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a resource to update.")
            return

        item = self.tree.item(selected[0])
        resource_id = item["values"][0]
        current_qty = item["values"][2]

        new_qty_text = self.quantity_entry.get().strip()
        new_status = self.status_var.get().strip()
        new_location = self.location_entry.get().strip()

        # Validate at least one field is provided
        if not new_qty_text and not new_status and not new_location:
            messagebox.showwarning("No Changes", "Please enter at least one field to update.")
            return

        # Validate quantity if provided
        new_qty = None
        if new_qty_text:
            try:
                new_qty = int(new_qty_text)
                if new_qty < 0:
                    raise ValueError("Quantity cannot be negative")
            except ValueError:
                messagebox.showerror(
                    "Invalid input, please correct.",
                    "Quantity must be a non-negative integer.",
                )
                return

        # Build update statement dynamically
        fields = []
        params = []

        if new_qty is not None:
            fields.append("quantity = %s")
            params.append(new_qty)

        if new_status:
            fields.append("status = %s")
            params.append(new_status)

        if new_location:
            fields.append("location = %s")
            params.append(new_location)

        if not fields:
            messagebox.showwarning("No Changes", "No valid fields to update.")
            return

        params.append(resource_id)
        set_clause = ", ".join(fields)

        try:
            cursor = self.connection.cursor()
            query = f"UPDATE ResourceStock SET {set_clause} WHERE resourceID = %s"
            cursor.execute(query, tuple(params))
            self.connection.commit()
            cursor.close()

            messagebox.showinfo("Success", "Resource updated successfully.")
            self.load_resources()

            # Clear inputs
            self.quantity_entry.delete(0, tk.END)
            self.status_var.set("")
            self.location_entry.delete(0, tk.END)

        except mysql.connector.Error as e:
            messagebox.showerror(
                "Error",
                f"Error updating resource. Try again later.\n{str(e)}",
            )

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
    app = UpdateResourcesApp(logged_in_user={"role": "Admin", "id": 1, "name": "Admin", "verified": True})
    app.mainloop()


