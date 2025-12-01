import sys
import os
import tkinter as tk
from tkinter import messagebox, ttk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data.db_connection import DatabaseConnection

class PrioritizeRequestsApp(tk.Tk):
    def __init__(self, logged_in_user=None, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user

        self.title("Prioritize Requests")
        self.geometry("750x500")
        self.configure(bg="#f5f5f5")

        # Use passed DB connection or create new
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        self.cursor = self.connection.cursor()

        self.create_widgets()
        self.load_requests()

    def create_widgets(self):
        tk.Label(self, text="Pending SOS Requests", font=("Helvetica", 18, "bold"), bg="#f5f5f5").pack(pady=15)

        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        columns = ("requestID", "victimName", "location", "description", "urgencyLevel")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col, heading in zip(columns, ["Request ID", "Victim Name", "Location", "Message", "Current Urgency"]):
            self.table.heading(col, text=heading)
        self.table.column("description", width=250)
        self.table.pack(fill="both", expand=True)

        tk.Label(self, text="Set Urgency Level:", font=("Helvetica", 12), bg="#f5f5f5").pack(pady=(10, 3))
        self.priority_var = tk.StringVar()
        self.priority_box = ttk.Combobox(self, textvariable=self.priority_var, values=["critical", "high", "medium", "low"], state="readonly", width=20)
        self.priority_box.pack()

        tk.Button(self, text="Apply Urgency", command=self.apply_priority, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold")).pack(pady=15)
        tk.Button(self, text="Back", command=self.go_back, bg="#2196F3", fg="white", font=("Helvetica", 12)).pack()

    def load_requests(self):
        try:
            query = """
                SELECT SOSRequest.requestID, UserAccount.name, SOSRequest.location, SOSRequest.description, SOSRequest.urgencyLevel
                FROM SOSRequest
                JOIN UserAccount ON SOSRequest.victimID = UserAccount.userID
                WHERE SOSRequest.status='pending'
            """
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            for row in rows:
                self.table.insert("", "end", values=row)
            if not rows:
                messagebox.showinfo("Information", "No pending requests found.")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def apply_priority(self):
        selected_item = self.table.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "No request selected.")
            return
        selected_priority = self.priority_var.get()
        if not selected_priority:
            messagebox.showwarning("Warning", "Please select an urgency level.")
            return
        row = self.table.item(selected_item)["values"]
        request_id = row[0]
        try:
            query = "UPDATE SOSRequest SET urgencyLevel=%s WHERE requestID=%s"
            self.cursor.execute(query, (selected_priority, request_id))
            self.connection.commit()
            messagebox.showinfo("Success", f"Urgency level updated to '{selected_priority}'!")
            self.table.delete(selected_item)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def go_back(self):
        self.destroy()
        from frontend.login import AdminOptionsApp
        app = AdminOptionsApp(logged_in_user=self.logged_in_user, db_connection=self.connection)
        app.mainloop()


if __name__ == "__main__":
    app = PrioritizeRequestsApp()
    app.mainloop()
