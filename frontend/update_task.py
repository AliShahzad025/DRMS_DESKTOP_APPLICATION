import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.db_connection import DatabaseConnection
import mysql.connector


class UpdateTaskApp(tk.Tk):
    """
    Use Case UC-16: Update Task

    Allows a volunteer to update task progress/status.
    - Shows tasks assigned to the volunteer (not completed/cancelled)
    - Allows changing status and adding a progress note
    """

    def __init__(self, logged_in_user=None, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user or {}
        self.role = self.logged_in_user.get("role")

        # Permission: Volunteer only
        if self.role != "Volunteer":
            messagebox.showerror("Unauthorized", "Only volunteers can update tasks.")
            self.destroy()
            return

        self.title("Update Task - DRMS")
        self.geometry("950x600")
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
            text="Update My Tasks",
            font=("Helvetica", 18, "bold"),
            bg="#f5f5f5",
        ).pack(pady=15)

        tk.Label(
            self,
            text="Select a task and update its status or add progress notes.",
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

        # Current status + update area
        update_frame = tk.LabelFrame(
            self,
            text="Task Progress",
            font=("Helvetica", 12, "bold"),
            bg="#f5f5f5",
            padx=10,
            pady=10,
        )
        update_frame.pack(padx=20, pady=10, fill="x")

        tk.Label(update_frame, text="New Status:", font=("Helvetica", 11), bg="#f5f5f5").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(
            update_frame,
            textvariable=self.status_var,
            values=["in_progress", "completed", "cancelled"],
            state="readonly",
            width=15,
        )
        self.status_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(update_frame, text="Progress Note:", font=("Helvetica", 11), bg="#f5f5f5").grid(
            row=1, column=0, padx=5, pady=5, sticky="nw"
        )
        self.note_text = tk.Text(update_frame, font=("Helvetica", 10), width=60, height=5)
        self.note_text.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.tree.bind("<<TreeviewSelect>>", self.on_task_select)

        # Buttons
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame,
            text="Save Update",
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=16,
            command=self.save_update,
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            btn_frame,
            text="Refresh",
            font=("Helvetica", 12),
            bg="#FF9800",
            fg="white",
            width=12,
            command=self.load_tasks,
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            btn_frame,
            text="Back",
            font=("Helvetica", 12),
            bg="#757575",
            fg="white",
            width=12,
            command=self.go_back,
        ).grid(row=0, column=2, padx=10)

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def load_tasks(self):
        """Load tasks assigned to this volunteer that are not completed or cancelled."""
        self.clear_table()
        self.status_var.set("")
        self.note_text.delete("1.0", tk.END)

        try:
            cursor = self.connection.cursor(dictionary=True)
            volunteer_id = self.logged_in_user.get("id")

            cursor.execute(
                """
                SELECT taskID, title, taskType, status, relatedRequestID, description
                FROM Task
                WHERE assignedVolunteerID = %s
                  AND status IN ('assigned', 'in_progress')
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
                messagebox.showinfo("Information", "No tasks available to update.")

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to load tasks: {str(e)}")

    def get_selected_task_id(self):
        selected = self.tree.selection()
        if not selected:
            return None
        values = self.tree.item(selected[0])["values"]
        return values[0]

    def on_task_select(self, event=None):
        task_id = self.get_selected_task_id()
        if not task_id:
            return
        task = self._task_cache.get(task_id)
        if not task:
            return
        # Pre-fill current status
        self.status_var.set(task["status"])

    def save_update(self):
        """Validate and save task status/progress."""
        task_id = self.get_selected_task_id()
        if not task_id:
            messagebox.showwarning("No Selection", "Please select a task to update.")
            return

        new_status = self.status_var.get().strip()
        note = self.note_text.get("1.0", tk.END).strip()

        # Validate
        if not new_status:
            messagebox.showerror("Incomplete data", "Please select a new status.")
            return

        if not note:
            messagebox.showerror("Incomplete data", "Please enter a progress note.")
            return

        try:
            cursor = self.connection.cursor(dictionary=True)
            volunteer_id = self.logged_in_user.get("id")

            # Get previous status
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

            messagebox.showinfo("Task Updated", "Task progress updated successfully.")
            self.load_tasks()

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to update task: {str(e)}")

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
    app = UpdateTaskApp(logged_in_user={"role": "Volunteer", "id": 3, "name": "Carol"})
    app.mainloop()


