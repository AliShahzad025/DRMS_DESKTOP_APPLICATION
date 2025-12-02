import tkinter as tk
from tkinter import messagebox, ttk
from data.db_connection import DatabaseConnection

class TrackRequestApp(tk.Tk):
    def __init__(self, logged_in_user=None, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        self.cursor = self.connection.cursor(dictionary=True)
        self.geometry("750x500")
        self.title("Track Requests")
        self.configure(bg="#f5f5f5")
        self.create_widgets()
        self.load_requests()

    def create_widgets(self):
        tk.Label(self, text="Track Requests", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=20)

        # Treeview for requests
        columns = ("requestID", "victim", "location", "typeOfNeed", "urgencyLevel", "status", "assignedVolunteer", "assignedNGO")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(pady=10, fill="both", expand=True)

        # Update status button
        tk.Button(self, text="Update Status", bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"),
                  command=self.open_status_window).pack(pady=10)

    def load_requests(self):
        """Load requests from DB into the treeview"""
        try:
            if self.logged_in_user and self.logged_in_user.get("role") == "Victim":
                query = """
                SELECT R.requestID, U.name as victim, R.location, R.typeOfNeed, R.urgencyLevel, R.status,
                       V.name as assignedVolunteer, N.orgName as assignedNGO
                FROM SOSRequest R
                JOIN UserAccount U ON R.victimID = U.userID
                LEFT JOIN UserAccount V ON R.assignedVolunteerID = V.userID
                LEFT JOIN NGO N ON R.assignedNGO = N.ngoID
                WHERE R.victimID=%s
                """
                self.cursor.execute(query, (self.logged_in_user.get("id"),))
            else:
                query = """
                SELECT R.requestID, U.name as victim, R.location, R.typeOfNeed, R.urgencyLevel, R.status,
                       V.name as assignedVolunteer, N.orgName as assignedNGO
                FROM SOSRequest R
                JOIN UserAccount U ON R.victimID = U.userID
                LEFT JOIN UserAccount V ON R.assignedVolunteerID = V.userID
                LEFT JOIN NGO N ON R.assignedNGO = N.ngoID
                """
                self.cursor.execute(query)

            results = self.cursor.fetchall()
            self.tree.delete(*self.tree.get_children())
            for row in results:
                self.tree.insert("", tk.END, values=(
                    row["requestID"], row["victim"], row["location"], row["typeOfNeed"],
                    row["urgencyLevel"], row["status"], row["assignedVolunteer"], row["assignedNGO"]
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load requests.\n{str(e)}")

    def open_status_window(self):
        """Open a small window with an OptionMenu to safely update status"""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a request to update.")
            return

        request_values = self.tree.item(selected_item, "values")
        request_id = request_values[0]
        current_status = request_values[5]

        status_window = tk.Toplevel(self)
        status_window.title(f"Update Status for Request {request_id}")
        status_window.geometry("300x150")
        status_window.configure(bg="#f5f5f5")

        tk.Label(status_window, text="Select new status:", bg="#f5f5f5", font=("Helvetica", 12)).pack(pady=10)

        status_var = tk.StringVar(value=current_status)
        tk.OptionMenu(status_window, status_var, "pending", "in_process", "assigned", "completed").pack(pady=5)

        def save_status():
            new_status = status_var.get()
            try:
                self.cursor.execute("UPDATE SOSRequest SET status=%s WHERE requestID=%s", (new_status, request_id))
                self.connection.commit()
                messagebox.showinfo("Success", f"Request ID {request_id} status updated to '{new_status}'.")
                status_window.destroy()
                self.load_requests()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update status.\n{str(e)}")
                self.connection.rollback()

        tk.Button(status_window, text="Save", bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"),
                  command=save_status).pack(pady=10)
