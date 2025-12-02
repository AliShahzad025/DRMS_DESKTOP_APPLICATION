import tkinter as tk
from tkinter import messagebox, ttk
from data.db_connection import DatabaseConnection

class GiveFeedbackApp(tk.Tk):
    def __init__(self, logged_in_user=None, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        self.cursor = self.connection.cursor(dictionary=True)
        self.geometry("650x500")
        self.title("Give Feedback")
        self.configure(bg="#f5f5f5")
        self.create_widgets()
        self.load_completed_requests()

    def create_widgets(self):
        tk.Label(self, text="Submit Feedback", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=20)

        # Treeview to show completed or in-process requests for this victim
        columns = ("requestID", "location", "typeOfNeed", "assignedVolunteer", "assignedNGO", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(pady=10, fill="both", expand=True)

        # Rating
        tk.Label(self, text="Rating (1-5):", bg="#f5f5f5").pack(pady=(10,0))
        self.rating_var = tk.IntVar(value=5)
        tk.Spinbox(self, from_=1, to=5, textvariable=self.rating_var, width=5).pack(pady=5)

        # Comments
        tk.Label(self, text="Comments:", bg="#f5f5f5").pack(pady=(10,0))
        self.comment_text = tk.Text(self, width=60, height=5)
        self.comment_text.pack(pady=5)

        # Submit button
        tk.Button(self, text="Submit Feedback", bg="#4CAF50", fg="white", width=20,
                  command=self.submit_feedback).pack(pady=20)

    def load_completed_requests(self):
        """Load SOS requests linked to this victim"""
        try:
            query = """
            SELECT R.requestID, R.location, R.typeOfNeed, R.status,
                   V.name as assignedVolunteer, N.orgName as assignedNGO
            FROM SOSRequest R
            LEFT JOIN UserAccount V ON R.assignedVolunteerID = V.userID
            LEFT JOIN NGO N ON R.assignedNGO = N.ngoID
            WHERE R.victimID=%s
            """
            self.cursor.execute(query, (self.logged_in_user.get("id"),))
            results = self.cursor.fetchall()
            self.tree.delete(*self.tree.get_children())
            for row in results:
                self.tree.insert("", tk.END, values=(
                    row["requestID"], row["location"], row["typeOfNeed"],
                    row["assignedVolunteer"] or "N/A", row["assignedNGO"] or "N/A", row["status"]
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load requests.\n{str(e)}")

    def submit_feedback(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a request to give feedback.")
            return

        request_values = self.tree.item(selected_item, "values")
        request_id = request_values[0]
        rating = self.rating_var.get()
        comments = self.comment_text.get("1.0", tk.END).strip()

        if rating < 1 or rating > 5:
            messagebox.showwarning("Input Error", "Rating must be between 1 and 5.")
            return

        try:
            sql = """
            INSERT INTO Feedback (requestID, victimID, rating, comments)
            VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(sql, (request_id, self.logged_in_user.get("id"), rating, comments))
            self.connection.commit()
            messagebox.showinfo("Success", f"Feedback submitted for request ID {request_id}.")
            self.comment_text.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to submit feedback.\n{str(e)}")
            self.connection.rollback()
