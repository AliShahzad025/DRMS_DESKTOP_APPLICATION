import tkinter as tk
from tkinter import ttk, messagebox

from data.db_connection import DatabaseConnection


class VerifyNGOApp(tk.Tk):
    def __init__(self, db_connection=None):
        super().__init__()
        self.title("Verify NGO - DRMS")
        self.geometry("800x500")
        self.configure(bg="#f5f5f5")

        # DB setup
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        self.cursor = self.connection.cursor(dictionary=True)

        # UI
        self.create_widgets()
        self.load_ngos()

    # ----------------------- UI -----------------------------
    def create_widgets(self):
        tk.Label(self, text="Verify Registered NGOs", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=15)

        # NGO Table
        columns = ("ngoID", "orgName", "verified", "region")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(self, bg="#f5f5f5")
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame, text="View NGO Details", font=("Helvetica", 12),
            bg="#2196F3", fg="white", width=18, command=self.open_details_window
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            btn_frame, text="Back", font=("Helvetica", 12),
            bg="#757575", fg="white", width=18,
            command=self.go_back
        ).grid(row=0, column=1, padx=10)

    # ------------------ Load NGO List -----------------------
    def load_ngos(self):
        self.tree.delete(*self.tree.get_children())

        self.cursor.execute("""
            SELECT ngoID, orgName, verified, region 
            FROM NGO
        """)
        ngos = self.cursor.fetchall()

        for ngo in ngos:
            self.tree.insert("", tk.END, values=(
                ngo["ngoID"],
                ngo["orgName"],
                "Yes" if ngo["verified"] else "No",
                ngo["region"]
            ))

    # ---------------- NGO Detailed Window -------------------
    def open_details_window(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an NGO first.")
            return

        ngo_data = self.tree.item(selected)["values"]
        ngo_id = ngo_data[0]

        # Fetch full NGO details
        self.cursor.execute("""
            SELECT * FROM NGO WHERE ngoID = %s
        """, (ngo_id,))
        ngo = self.cursor.fetchone()

        if not ngo:
            messagebox.showerror("Error", "NGO details not found.")
            return

        details_window = tk.Toplevel(self)
        details_window.title("NGO Details")
        details_window.geometry("500x450")
        details_window.configure(bg="#f5f5f5")

        tk.Label(details_window, text="NGO Details", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=15)

        info = (
            f"NGO Name: {ngo['orgName']}\n\n"
            f"Verified: {'Yes' if ngo['verified'] else 'No'}\n\n"
            f"Region: {ngo['region']}\n\n"
            f"Contact Person: {ngo['contact_person']}\n\n"
            f"Registration Document:\n  {ngo['registration_doc']}"
        )

        tk.Label(details_window, text=info, justify="left", bg="#f5f5f5",
                 font=("Helvetica", 12)).pack(pady=10)

        # Approve / Reject buttons
        tk.Button(
            details_window, text="Approve",
            bg="#4CAF50", fg="white", font=("Helvetica", 12), width=15,
            command=lambda: self.verify_ngo(ngo["ngoID"], True, details_window)
        ).pack(pady=10)

        tk.Button(
            details_window, text="Reject",
            bg="#F44336", fg="white", font=("Helvetica", 12), width=15,
            command=lambda: self.verify_ngo(ngo["ngoID"], False, details_window)
        ).pack(pady=5)

    # ------------------- Verify NGO -------------------------
    def verify_ngo(self, ngo_id, status, window):
        try:
            self.cursor.execute("""
                UPDATE NGO
                SET verified = %s
                WHERE ngoID = %s
            """, (status, ngo_id))

            self.connection.commit()

            if status:
                messagebox.showinfo("Success", "NGO Verified Successfully!")
            else:
                messagebox.showwarning("Rejected", "NGO Verification Failed.")

            window.destroy()
            self.load_ngos()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # ---------------------- Back -----------------------------
    def go_back(self):
        self.destroy()


# ------------------ TESTING -------------------
if __name__ == "__main__":
    app = VerifyNGOApp()
    app.mainloop()
