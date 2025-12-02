import tkinter as tk
from tkinter import messagebox
import datetime
from data.db_connection import DatabaseConnection

class RegisterVolunteerApp(tk.Tk):
    def __init__(self, db_connection=None):
        super().__init__()
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        self.cursor = self.connection.cursor(dictionary=True)
        self.geometry("450x550")
        self.title("Register Volunteer")
        self.configure(bg="#f5f5f5")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Register New Volunteer", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=20)

        # Name
        tk.Label(self, text="Name:", bg="#f5f5f5").pack(pady=(10,0))
        self.name_entry = tk.Entry(self, width=40)
        self.name_entry.pack(pady=5)

        # Email
        tk.Label(self, text="Email:", bg="#f5f5f5").pack(pady=(10,0))
        self.email_entry = tk.Entry(self, width=40)
        self.email_entry.pack(pady=5)

        # Phone
        tk.Label(self, text="Phone:", bg="#f5f5f5").pack(pady=(10,0))
        self.phone_entry = tk.Entry(self, width=40)
        self.phone_entry.pack(pady=5)

        # Location
        tk.Label(self, text="Location:", bg="#f5f5f5").pack(pady=(10,0))
        self.location_entry = tk.Entry(self, width=40)
        self.location_entry.pack(pady=5)

        # Latitude
        tk.Label(self, text="Latitude (optional):", bg="#f5f5f5").pack(pady=(10,0))
        self.lat_entry = tk.Entry(self, width=40)
        self.lat_entry.pack(pady=5)

        # Longitude
        tk.Label(self, text="Longitude (optional):", bg="#f5f5f5").pack(pady=(10,0))
        self.lng_entry = tk.Entry(self, width=40)
        self.lng_entry.pack(pady=5)

        # Roles / Skills
        tk.Label(self, text="Roles / Skills (optional):", bg="#f5f5f5").pack(pady=(10,0))
        self.roles_entry = tk.Entry(self, width=40)
        self.roles_entry.pack(pady=5)

        # Status
        tk.Label(self, text="Status:", bg="#f5f5f5").pack(pady=(10,0))
        self.status_var = tk.StringVar(value="available")
        tk.OptionMenu(self, self.status_var, "available", "busy").pack(pady=5)

        # Verified (Read-only, pre-set to True)
        tk.Label(self, text="Verified:", bg="#f5f5f5").pack(pady=(10,0))
        self.verified_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self, text="Verified", variable=self.verified_var, bg="#f5f5f5", state="disabled").pack(pady=5)

        # Password
        tk.Label(self, text="Password:", bg="#f5f5f5").pack(pady=(10,0))
        self.password_entry = tk.Entry(self, width=40, show="*")
        self.password_entry.pack(pady=5)

        # Submit button
        tk.Button(self, text="Register Volunteer", bg="#4CAF50", fg="white", width=25,
                  command=self.register_volunteer).pack(pady=20)

    def register_volunteer(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        location = self.location_entry.get().strip()
        lat = self.lat_entry.get().strip() or None
        lng = self.lng_entry.get().strip() or None
        roles = self.roles_entry.get().strip() or ""
        status = self.status_var.get()
        verified = self.verified_var.get()
        password = self.password_entry.get().strip()

        if not (name and email and phone and location and password):
            messagebox.showwarning("Missing Fields", "Please fill all required fields!")
            return

        try:
            # Insert into UserAccount
            insert_user = """
            INSERT INTO UserAccount (name, email, phone, location, latitude, longitude, role, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s, 'Volunteer', %s)
            """
            self.cursor.execute(insert_user, (name, email, phone, location, lat, lng, password))
            self.connection.commit()
            volunteer_id = self.cursor.lastrowid

            # Insert into Volunteer
            insert_volunteer = """
            INSERT INTO Volunteer (volunteerID, roles, verified, status, last_active)
            VALUES (%s, %s, %s, %s, %s)
            """
            last_active = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(insert_volunteer, (volunteer_id, roles, verified, status, last_active))
            self.connection.commit()

            messagebox.showinfo("Success", f"Volunteer '{name}' registered successfully!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to register volunteer.\n{str(e)}")
            self.connection.rollback()


if __name__ == "__main__":
    app = RegisterVolunteerApp()
    app.mainloop()
