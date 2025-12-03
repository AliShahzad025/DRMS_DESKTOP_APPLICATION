import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.db_connection import DatabaseConnection
import mysql.connector


class AcceptTaskApp(tk.Tk):
    """
    Use Case UC-15: Accept Task

    Allows a volunteer to accept or decline assigned tasks.
    - Shows tasks where assignedVolunteerID = current volunteer
    - Accept -> status 'in_progress'
    - Decline -> status 'cancelled' (used as 'Declined')
    """

    def __init__(self, logged_in_user=None, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user or {}
        self.role = self.logged_in_user.get("role")

        # Permission: Volunteer only
        if self.role != "Volunteer":
            messagebox.showerror("Unauthorized", "Only volunteers can accept tasks.")
            self.destroy()
            return

        self.title("Accept Task - DRMS")
        self.geometry("900x550")
        self.configure(bg="#f5f5f5")

        # Database connection
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        if not self.connection:
            messagebox.showerror("Database Error", "Cannot connect to database!")
            self.destroy()
            return

        self.create_widgets()
        self.load_tasks()

    def create_widgets(self):
        tk.Label(
            self,
            text="My Assigned Tasks",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
        ).pack(pady=15)

        tk.Label(
            self,
            text="Select a task to view details and accept or decline it.",
            font=("Helvetica", 10),
            bg="#f5f5f5",
            fg="#555",
        ).pack(pady=5)

        # Tasks table
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        columns = ("taskID", "title", "taskType", "status", "relatedRequestID")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.tree.heading("taskID", text="Task ID")
        self.tree.heading("title", text="Title")
        self.tree.heading("taskType", text="Type")
        self.tree.heading("status", text="Status")
        self.tree.heading("relatedRequestID", text="Request ID")

        self.tree.column("taskID", width=80)
        self.tree.column("title", width=260)
        self.tree.column("taskType", width=120)
        self.tree.column("status", width=120)
        self.tree.column("relatedRequestID", width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Task details
        details_frame = tk.LabelFrame(
            self,
            text="Task Details",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5",
            padx=10,
            pady=10,
        )
        details_frame.pack(padx=20, pady=10, fill="x")

        self.details_label = tk.Label(
            details_frame,
            text="Select a task to view details.",
            font=("Helvetica", 10),
            justify="left",
            bg="#f5f5f5",
        )
        self.details_label.pack(fill="x")

        self.tree.bind("<<TreeviewSelect>>", self.show_task_details)

        # Buttons
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame,
            text="Accept Task",
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=16,
            command=self.accept_task,
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            btn_frame,
            text="Decline Task",
            font=("Helvetica", 12, "bold"),
            bg="#F44336",
            fg="white",
            width=16,
            command=self.decline_task,
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            btn_frame,
            text="Refresh",
            font=("Helvetica", 12),
            bg="#FF9800",
            fg="white",
            width=12,
            command=self.load_tasks,
        ).grid(row=0, column=2, padx=10)

        tk.Button(
            btn_frame,
            text="Back",
            font=("Helvetica", 12),
            bg="#757575",
            fg="white",
            width=12,
            command=self.go_back,
        ).grid(row=0, column=3, padx=10)

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def load_tasks(self):
        """Load tasks assigned to this volunteer (status = 'assigned')."""
        self.clear_table()
        self.details_label.config(text="Select a task to view details.")

        try:
            cursor = self.connection.cursor(dictionary=True)
            volunteer_id = self.logged_in_user.get("id")

            cursor.execute(
                """
                SELECT taskID, title, taskType, status, relatedRequestID, description
                FROM Task
                WHERE assignedVolunteerID = %s
                  AND status = 'assigned'
                ORDER BY createdAt DESC
                """,
                (volunteer_id,),
            )
            tasks = cursor.fetchall()
            cursor.close()

            self._task_cache = {t["taskID"]: t for t in tasks}

            for t in tasks:
                self.tree.insert(
                    "",
                    "end",
                    values=(t["taskID"], t["title"], t["taskType"], t["status"], t["relatedRequestID"]),
                )

            if not tasks:
                messagebox.showinfo("Information", "No assigned tasks available.")

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to load tasks: {str(e)}")

    def get_selected_task_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a task first.")
            return None
        values = self.tree.item(selected[0])["values"]
        return values[0]  # taskID

    def show_task_details(self, event=None):
        task_id = self.get_selected_task_id()
        if not task_id:
            return
        task = self._task_cache.get(task_id)
        if not task:
            return

        text = (
            f"Task ID: {task['taskID']}\n"
            f"Title: {task['title']}\n"
            f"Type: {task['taskType']}\n"
            f"Status: {task['status']}\n"
            f"Related Request ID: {task['relatedRequestID']}\n\n"
            f"Description:\n{task['description'] or 'N/A'}"
        )
        self.details_label.config(text=text)

    def update_task_status(self, task_id, new_status, note):
        """Helper to update Task and insert TaskHistory."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            volunteer_id = self.logged_in_user.get("id")

            # Get current status
            cursor.execute("SELECT status FROM Task WHERE taskID = %s", (task_id,))
            row = cursor.fetchone()
            if not row:
                cursor.close()
                messagebox.showerror("Error", "Task not found.")
                return
            previous_status = row["status"]

            # Update Task
            cursor.execute(
                """
                UPDATE Task
                SET status = %s
                WHERE taskID = %s
                """,
                (new_status, task_id),
            )

            # Insert TaskHistory
            cursor.execute(
                """
                INSERT INTO TaskHistory (taskID, volunteerID, previousStatus, newStatus, note)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (task_id, volunteer_id, previous_status, new_status, note),
            )

            self.connection.commit()
            cursor.close()

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to update task: {str(e)}")

    def accept_task(self):
        task_id = self.get_selected_task_id()
        if not task_id:
            return

        confirm = messagebox.askyesno("Confirm", "Accept this task?")
        if not confirm:
            return

        # UC-15: status updated to 'Accepted' -> use 'in_progress'
        self.update_task_status(task_id, "in_progress", "Volunteer accepted the task.")
        messagebox.showinfo("Task Accepted", "Task accepted successfully.")
        self.load_tasks()

    def decline_task(self):
        task_id = self.get_selected_task_id()
        if not task_id:
            return

        confirm = messagebox.askyesno("Confirm", "Decline this task?")
        if not confirm:
            return

        # UC-15 alternate: Mark as 'Declined' -> map to 'cancelled'
        self.update_task_status(task_id, "cancelled", "Volunteer declined the task.")
        messagebox.showinfo("Task Declined", "Task has been declined.")
        self.load_tasks()

    def go_back(self):
        """Return to previous screen."""
        self.destroy()
        try:
            from frontend.login import VolunteerApp

            app = VolunteerApp(logged_in_user=self.logged_in_user)
            app.mainloop()
        except Exception:
            pass


if __name__ == "__main__":
    # Manual test: assume volunteer userID 3
    app = AcceptTaskApp(logged_in_user={"role": "Volunteer", "id": 3, "name": "Carol"})
    app.mainloop()


