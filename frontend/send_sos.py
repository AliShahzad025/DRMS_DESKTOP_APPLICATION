import sys
import os
import tkinter as tk
from tkinter import messagebox

# Allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.db_connection import DatabaseConnection
import mysql.connector


class SendSOSApp(tk.Tk):
    """
    Use Case UC-17: Send SOS Request

    Allows victims to send emergency SOS requests.
    - Displays SOS form (location, type of need, description, urgency)
    - Validates input
    - Inserts into SOSRequest, which triggers notifications via DB trigger
    """

    def __init__(self, logged_in_user=None, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user or {}
        self.role = self.logged_in_user.get("role")

        # Permission check: Victim only
        if self.role != "Victim":
            messagebox.showerror("Unauthorized", "Only victims can send SOS requests.")
            self.destroy()
            return

        self.title("Send SOS Request - DRMS")
        self.geometry("650x500")
        self.configure(bg="#f5f5f5")

        # Database connection
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        if not self.connection:
            messagebox.showerror("Database Error", "Cannot connect to database!")
            self.destroy()
            return

        self.create_widgets()

    def create_widgets(self):
        tk.Label(
            self,
            text="Send SOS Request",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
        ).pack(pady=15)

        tk.Label(
            self,
            text="Provide your location and details about your emergency.",
            font=("Helvetica", 10),
            bg="#f5f5f5",
            fg="#555",
        ).pack(pady=5)

        form_frame = tk.Frame(self, bg="#f5f5f5")
        form_frame.pack(padx=30, pady=10, fill="x")

        # Location
        tk.Label(form_frame, text="* Location:", font=("Helvetica", 11), bg="#f5f5f5").grid(
            row=0, column=0, sticky="w", pady=8
        )
        self.location_entry = tk.Entry(form_frame, font=("Helvetica", 11), width=40)
        self.location_entry.grid(row=0, column=1, pady=8, sticky="w")

        # Type of Need
        tk.Label(form_frame, text="* Type of Need:", font=("Helvetica", 11), bg="#f5f5f5").grid(
            row=1, column=0, sticky="w", pady=8
        )
        self.need_entry = tk.Entry(form_frame, font=("Helvetica", 11), width=40)
        self.need_entry.grid(row=1, column=1, pady=8, sticky="w")

        # Urgency
        tk.Label(form_frame, text="Urgency Level:", font=("Helvetica", 11), bg="#f5f5f5").grid(
            row=2, column=0, sticky="w", pady=8
        )
        self.urgency_var = tk.StringVar(value="low")
        urgency_options = ["low", "medium", "high", "critical"]
        urgency_menu = tk.OptionMenu(form_frame, self.urgency_var, *urgency_options)
        urgency_menu.config(font=("Helvetica", 10))
        urgency_menu.grid(row=2, column=1, pady=8, sticky="w")

        # Description
        tk.Label(form_frame, text="* Description:", font=("Helvetica", 11), bg="#f5f5f5").grid(
            row=3, column=0, sticky="nw", pady=8
        )
        self.description_text = tk.Text(form_frame, font=("Helvetica", 10), width=40, height=6)
        self.description_text.grid(row=3, column=1, pady=8, sticky="w")

        # Buttons
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame,
            text="Submit SOS",
            font=("Helvetica", 12, "bold"),
            bg="#F44336",
            fg="white",
            width=14,
            command=self.submit_sos,
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

    def clear_form(self):
        self.location_entry.delete(0, tk.END)
        self.need_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)
        self.urgency_var.set("low")

    def submit_sos(self):
        """Validate input and insert SOSRequest."""
        location = self.location_entry.get().strip()
        type_of_need = self.need_entry.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()
        urgency = self.urgency_var.get().strip() or "low"

        # Validate required fields
        if not location or not type_of_need or not description:
            messagebox.showerror(
                "Incomplete details",
                "Please fill in all required fields (*).",
            )
            return

        try:
            cursor = self.connection.cursor()
            victim_id = self.logged_in_user.get("id")

            cursor.execute(
                """
                INSERT INTO SOSRequest (
                    victimID,
                    location,
                    latitude,
                    longitude,
                    typeOfNeed,
                    description,
                    urgencyLevel,
                    status,
                    priorityScore,
                    assignedVolunteerID,
                    assignedNGO
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', 0, NULL, NULL)
                """,
                (victim_id, location, 0.0, 0.0, type_of_need, description, urgency),
            )

            self.connection.commit()
            cursor.close()

            # UC-17: notify admin/NGOs — handled by DB trigger on SOSRequest insert
            messagebox.showinfo(
                "SOS Sent",
                "Your SOS request has been sent and logged.\n"
                "Relevant admins and NGOs will be notified.",
            )
            self.clear_form()

        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to send SOS request.\n{str(e)}")

    def go_back(self):
        """Return to previous screen."""
        self.destroy()
        # If you add a Victim dashboard later, navigate back there.


if __name__ == "__main__":
    # Manual test: assume victim userID 4
    app = SendSOSApp(logged_in_user={"role": "Victim", "id": 4, "name": "David Smith"})
    app.mainloop()


