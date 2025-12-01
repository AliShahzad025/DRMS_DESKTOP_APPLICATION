import tkinter as tk
from tkinter import messagebox, scrolledtext
from data.db_connection import DatabaseConnection

class VerifyVolunteerApp(tk.Tk):
    def __init__(self, logged_in_user=None, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        self.cursor = self.connection.cursor()
        self.title("Verify Volunteers - DRMS")
        self.geometry("700x400")
        self.configure(bg="#f5f5f5")
        self.create_widgets()
        self.load_volunteers()

    def create_widgets(self):
        tk.Label(self, text="Verify Volunteers", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=20)

        # Volunteer list
        self.volunteer_listbox = tk.Listbox(self, width=50, font=("Helvetica", 12))
        self.volunteer_listbox.pack(pady=10)
        self.volunteer_listbox.bind("<<ListboxSelect>>", self.display_volunteer_details)

        # Volunteer details
        tk.Label(self, text="Volunteer Details:", font=("Helvetica", 12, "bold"), bg="#f5f5f5").pack(pady=(10, 0))
        self.details_text = scrolledtext.ScrolledText(self, width=70, height=8, font=("Helvetica", 12))
        self.details_text.pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Verify", bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"),
                  command=lambda: self.update_verification(True)).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Reject", bg="#F44336", fg="white", font=("Helvetica", 12, "bold"),
                  command=lambda: self.update_verification(False)).grid(row=0, column=1, padx=10)
        tk.Button(btn_frame, text="Refresh", bg="#2196F3", fg="white", font=("Helvetica", 12, "bold"),
                  command=self.load_volunteers).grid(row=0, column=2, padx=10)

    def load_volunteers(self):
        """Load volunteers from database who are not verified yet"""
        self.volunteer_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT volunteerID, roles, verified, status, last_active FROM Volunteer")
        self.volunteers = self.cursor.fetchall()
        for vol in self.volunteers:
            vol_id, roles, verified, status, last_active = vol
            status_text = "Verified" if verified else "Pending"
            self.volunteer_listbox.insert(tk.END, f"ID {vol_id} - {roles} - {status_text}")

    def display_volunteer_details(self, event):
        """Show selected volunteer's details"""
        selection = self.volunteer_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        volunteer = self.volunteers[index]
        vol_id, roles, verified, status, last_active = volunteer
        details = (
            f"Volunteer ID: {vol_id}\n"
            f"Roles: {roles}\n"
            f"Verified: {'Yes' if verified else 'No'}\n"
            f"Status: {status}\n"
            f"Last Active: {last_active}"
        )
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, details)

    def update_verification(self, verify=True):
        """Mark volunteer as verified or rejected"""
        selection = self.volunteer_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a volunteer first.")
            return
        index = selection[0]
        volunteer = self.volunteers[index]
        vol_id = volunteer[0]

        try:
            self.cursor.execute("UPDATE Volunteer SET verified=%s WHERE volunteerID=%s", (verify, vol_id))
            self.connection.commit()
            messagebox.showinfo("Success", f"Volunteer ID {vol_id} has been {'verified' if verify else 'rejected'}.")
            self.load_volunteers()
            self.details_text.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update volunteer: {str(e)}")
