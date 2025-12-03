import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.db_connection import DatabaseConnection
import mysql.connector


class TrackResourcesApp(tk.Tk):
    """
    Use Case UC-9d: Track Resources

    Admin / NGO can track current status and location of resources.
    - Shows search options (by Resource ID or Category/Type)
    - Displays current quantity, status, and location
    - Handles "Resource not found" cases
    """

    def __init__(self, logged_in_user=None, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user or {}
        self.role = self.logged_in_user.get("role")

        # Permission check: Admin or verified NGO only
        if self.role not in ["Admin", "NGO"]:
            messagebox.showerror("Unauthorized", "You do not have rights to track resources.")
            self.destroy()
            return

        if self.role == "NGO" and not self.logged_in_user.get("verified"):
            messagebox.showerror("Unauthorized", "Your NGO must be verified to track resources.")
            self.destroy()
            return

        self.title("Track Resources - DRMS")
        self.geometry("1000x600")
        self.configure(bg="#f5f5f5")

        # Database connection
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        if not self.connection:
            messagebox.showerror("Database Error", "Cannot connect to database!")
            self.destroy()
            return

        self.create_widgets()
        self.load_all_resources()

    def create_widgets(self):
        # Title
        tk.Label(
            self,
            text="Track Resources",
            font=("Helvetica", 16, "bold"),
            bg="#f5f5f5",
        ).pack(pady=15)

        # Info text
        tk.Label(
            self,
            text="Search by Resource ID or Category (Resource Type). Leave fields empty to view all.",
            font=("Helvetica", 10),
            bg="#f5f5f5",
            fg="#555",
        ).pack(pady=5)

        # Search form
        form_frame = tk.Frame(self, bg="#f5f5f5")
        form_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(form_frame, text="Resource ID:", font=("Helvetica", 10), bg="#f5f5f5").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.resource_id_entry = tk.Entry(form_frame, font=("Helvetica", 10), width=15)
        self.resource_id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Category / Type:", font=("Helvetica", 10), bg="#f5f5f5").grid(
            row=0, column=2, padx=10, pady=5, sticky="w"
        )
        self.category_entry = tk.Entry(form_frame, font=("Helvetica", 10), width=25)
        self.category_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(
            form_frame,
            text="Search",
            font=("Helvetica", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self.search_resources,
        ).grid(row=0, column=4, padx=10, pady=5)

        tk.Button(
            form_frame,
            text="Clear",
            font=("Helvetica", 11),
            bg="#FF9800",
            fg="white",
            command=self.clear_filters,
        ).grid(row=0, column=5, padx=5, pady=5)

        # Results table
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        columns = ("resourceID", "resourceType", "quantity", "status", "location", "latitude", "longitude")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        self.tree.heading("resourceID", text="Resource ID")
        self.tree.heading("resourceType", text="Resource Type")
        self.tree.heading("quantity", text="Quantity")
        self.tree.heading("status", text="Status")
        self.tree.heading("location", text="Location")
        self.tree.heading("latitude", text="Latitude")
        self.tree.heading("longitude", text="Longitude")

        self.tree.column("resourceID", width=100)
        self.tree.column("resourceType", width=180)
        self.tree.column("quantity", width=100)
        self.tree.column("status", width=120)
        self.tree.column("location", width=200)
        self.tree.column("latitude", width=90)
        self.tree.column("longitude", width=90)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons footer
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame,
            text="Refresh",
            font=("Helvetica", 12),
            bg="#2196F3",
            fg="white",
            width=16,
            command=self.load_all_resources,
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            btn_frame,
            text="Back",
            font=("Helvetica", 12),
            bg="#757575",
            fg="white",
            width=16,
            command=self.go_back,
        ).grid(row=0, column=1, padx=5)

    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def load_all_resources(self):
        """Load all resources visible to the current user."""
        self.clear_tree()

        try:
            cursor = self.connection.cursor(dictionary=True)

            if self.role == "NGO":
                # NGO sees only its own stock
                ngo_id = self.logged_in_user.get("id")
                query = """
                    SELECT r.resourceID,
                           rt.name AS resourceType,
                           r.quantity,
                           r.status,
                           r.location,
                           r.latitude,
                           r.longitude
                    FROM ResourceStock r
                    JOIN ResourceType rt ON r.resourceTypeID = rt.resourceTypeID
                    WHERE r.donorNGO = %s
                    ORDER BY r.resourceID
                """
                cursor.execute(query, (ngo_id,))
            else:
                # Admin sees all
                query = """
                    SELECT r.resourceID,
                           rt.name AS resourceType,
                           r.quantity,
                           r.status,
                           r.location,
                           r.latitude,
                           r.longitude
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
                        row["latitude"],
                        row["longitude"],
                    ),
                )

            if not rows:
                messagebox.showinfo("Information", "No resources found.")

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to load resources: {str(e)}")

    def search_resources(self):
        """Search resources by ID or category/type."""
        resource_id_text = self.resource_id_entry.get().strip()
        category_text = self.category_entry.get().strip()

        # If no filters, just reload all
        if not resource_id_text and not category_text:
            self.load_all_resources()
            return

        # Build query dynamically
        conditions = []
        params = []

        if resource_id_text:
            if not resource_id_text.isdigit():
                messagebox.showerror("Invalid Input", "Resource ID must be a number.")
                return
            conditions.append("r.resourceID = %s")
            params.append(int(resource_id_text))

        if category_text:
            conditions.append("rt.name LIKE %s")
            params.append(f"%{category_text}%")

        # Role-based visibility
        if self.role == "NGO":
            conditions.append("r.donorNGO = %s")
            params.append(self.logged_in_user.get("id"))

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT r.resourceID,
                   rt.name AS resourceType,
                   r.quantity,
                   r.status,
                   r.location,
                   r.latitude,
                   r.longitude
            FROM ResourceStock r
            JOIN ResourceType rt ON r.resourceTypeID = rt.resourceTypeID
            WHERE {where_clause}
            ORDER BY r.resourceID
        """

        self.clear_tree()

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            cursor.close()

            if not rows:
                messagebox.showwarning("Resource not found", "No matching resources were found.")
                return

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
                        row["latitude"],
                        row["longitude"],
                    ),
                )

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to search resources: {str(e)}")

    def clear_filters(self):
        self.resource_id_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.load_all_resources()

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
    # Simple manual test
    app = TrackResourcesApp(logged_in_user={"role": "Admin", "id": 1, "name": "Admin", "verified": True})
    app.mainloop()


