import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.db_connection import DatabaseConnection
import mysql.connector


class GiveFeedbackApp(tk.Tk):
    """
    Use Case UC-14: Give Feedback

    Victim can give feedback on completed SOS requests.
    - Shows victim's completed requests
    - Allows selecting a request and submitting rating + comments
    """

    def __init__(self, logged_in_user=None, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user or {}
        self.role = self.logged_in_user.get("role")

        # Permission check: only Victim
        if self.role != "Victim":
            messagebox.showerror("Unauthorized", "Only victims can give feedback.")
            self.destroy()
            return

        self.title("Give Feedback - DRMS")
        self.geometry("850x550")
        self.configure(bg="#f5f5f5")

        # Database connection
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        if not self.connection:
            messagebox.showerror("Database Error", "Cannot connect to database!")
            self.destroy()
            return

        self.create_widgets()
        self.load_requests()

    def create_widgets(self):
        # Title
        tk.Label(
            self,
            text="Give Feedback",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
        ).pack(pady=15)

        tk.Label(
            self,
            text="Select one of your completed SOS requests and provide feedback.",
            font=("Helvetica", 10),
            bg="#f5f5f5",
            fg="#555",
        ).pack(pady=5)

        # Requests table
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        columns = ("requestID", "typeOfNeed", "status", "createdAt")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        self.tree.heading("requestID", text="Request ID")
        self.tree.heading("typeOfNeed", text="Type of Need")
        self.tree.heading("status", text="Status")
        self.tree.heading("createdAt", text="Created At")

        self.tree.column("requestID", width=90)
        self.tree.column("typeOfNeed", width=200)
        self.tree.column("status", width=120)
        self.tree.column("createdAt", width=180)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Feedback form
        form_frame = tk.Frame(self, bg="#f5f5f5")
        form_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(form_frame, text="Rating (1-5):", font=("Helvetica", 11), bg="#f5f5f5").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.rating_var = tk.StringVar()
        self.rating_combo = ttk.Combobox(
            form_frame, textvariable=self.rating_var, values=["1", "2", "3", "4", "5"], state="readonly", width=5
        )
        self.rating_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="Comments:", font=("Helvetica", 11), bg="#f5f5f5").grid(
            row=1, column=0, padx=5, pady=5, sticky="nw"
        )
        self.comments_text = tk.Text(form_frame, font=("Helvetica", 10), width=60, height=5)
        self.comments_text.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Buttons
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame,
            text="Submit Feedback",
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=18,
            command=self.submit_feedback,
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            btn_frame,
            text="Back",
            font=("Helvetica", 12),
            bg="#757575",
            fg="white",
            width=12,
            command=self.go_back,
        ).grid(row=0, column=1, padx=10)

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def load_requests(self):
        """Load completed requests for this victim that don't yet have feedback."""
        self.clear_table()
        try:
            cursor = self.connection.cursor(dictionary=True)
            victim_id = self.logged_in_user.get("id")

            # Completed requests without feedback
            cursor.execute(
                """
                SELECT r.requestID, r.typeOfNeed, r.status, r.createdAt
                FROM SOSRequest r
                JOIN Victim v ON r.victimID = v.victimID
                WHERE r.victimID = %s
                  AND r.status IN ('delivered', 'completed', 'in_process', 'assigned')
                  AND NOT EXISTS (
                      SELECT 1 FROM Feedback f
                      WHERE f.requestID = r.requestID AND f.victimID = v.victimID
                  )
                ORDER BY r.createdAt DESC
                """,
                (victim_id,),
            )
            rows = cursor.fetchall()
            cursor.close()

            for row in rows:
                self.tree.insert(
                    "",
                    "end",
                    values=(row["requestID"], row["typeOfNeed"] or "N/A", row["status"], row["createdAt"]),
                )

            if not rows:
                messagebox.showinfo("Information", "No requests available for feedback.")

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to load requests: {str(e)}")

    def submit_feedback(self):
        """Validate and save feedback."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a request to give feedback on.")
            return

        request_data = self.tree.item(selected[0])["values"]
        request_id = request_data[0]

        rating_text = self.rating_var.get().strip()
        comments = self.comments_text.get("1.0", tk.END).strip()

        # Required fields validation
        if not rating_text or not comments:
            messagebox.showerror(
                "Required fields missing",
                "Please provide both a rating and comments.",
            )
            return

        try:
            rating = int(rating_text)
            if rating < 1 or rating > 5:
                raise ValueError("Rating out of range")
        except ValueError:
            messagebox.showerror("Invalid input", "Rating must be a number between 1 and 5.")
            return

        try:
            cursor = self.connection.cursor()
            victim_id = self.logged_in_user.get("id")

            cursor.execute(
                """
                INSERT INTO Feedback (requestID, victimID, rating, comments)
                VALUES (%s, %s, %s, %s)
                """,
                (request_id, victim_id, rating, comments),
            )

            self.connection.commit()
            cursor.close()

            messagebox.showinfo("Feedback Submitted", "Thank you for your feedback!")
            self.comments_text.delete("1.0", tk.END)
            self.rating_var.set("")
            self.load_requests()

        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to save feedback. Please try again.\n{str(e)}")

    def go_back(self):
        """Return to previous screen."""
        self.destroy()
        # If you later add a Victim dashboard, you can navigate back here.


if __name__ == "__main__":
    # Manual test: assume victim with user/victim ID 4
    app = GiveFeedbackApp(logged_in_user={"role": "Victim", "id": 4, "name": "David Smith"})
    app.mainloop()


