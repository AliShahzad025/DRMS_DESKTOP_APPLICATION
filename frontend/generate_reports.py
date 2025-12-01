import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Add parent folder to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import backend services
from services.user_service import UserService
from data.db_connection import DatabaseConnection
from data.user_repository import UserRepository

# PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Import LanguageManager
from frontend.language import LanguageManager

# ---------- Backend setup ----------
db = DatabaseConnection()
connection = db.connect()
if not connection:
    raise Exception("Cannot connect to database!")

user_repo = UserRepository(connection)
user_service = UserService(user_repo)

# ---------- Generate Reports App ----------
class GenerateReportsApp(tk.Tk):
    def __init__(self, logged_in_user):
        super().__init__()
        self.logged_in_user = logged_in_user
        self.lang_manager = LanguageManager()
        self.geometry("800x500")
        self.configure(bg="#f5f5f5")
        self.create_widgets()

    def create_widgets(self):
        # Title Label
        self.title_label = tk.Label(self, font=("Helvetica", 16, "bold"), bg="#f5f5f5")
        self.title_label.pack(pady=20)

        # Report type dropdown
        self.report_label = tk.Label(self, font=("Helvetica", 12), bg="#f5f5f5")
        self.report_label.pack(pady=(10,5))
        self.report_var = tk.StringVar()
        self.report_var.set("volunteers")
        self.report_menu = tk.OptionMenu(self, self.report_var, "volunteers", "ngos", "victims")
        self.report_menu.pack(pady=5)

        # Buttons
        self.generate_button = tk.Button(self, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white",
                                         activebackground="#45a049", command=self.generate_report)
        self.generate_button.pack(pady=10)

        self.print_button = tk.Button(self, font=("Helvetica", 12, "bold"), bg="#2196F3", fg="white",
                                      activebackground="#1e88e5", command=self.print_report)
        self.print_button.pack(pady=5)

        self.language_button = tk.Button(self, font=("Helvetica", 12), bg="#FFC107", fg="white",
                                         command=self.change_language)
        self.language_button.pack(pady=10)

        # Treeview for data
        self.tree = ttk.Treeview(self)
        self.tree.pack(pady=10, fill="both", expand=True)

        self.refresh_language()

    def refresh_language(self):
        self.title(self.lang_manager.get("generate_reports"))
        self.title_label.config(text=self.lang_manager.get("generate_reports"))
        self.report_label.config(text=self.lang_manager.get("select_report_type"))
        self.generate_button.config(text=self.lang_manager.get("generate_report"))
        self.print_button.config(text=self.lang_manager.get("print_report"))
        self.language_button.config(text=self.lang_manager.get("language_settings"))

        # Update dropdown menu if needed
        self.report_menu["menu"].delete(0, "end")
        for report in ["volunteers", "ngos", "victims"]:
            self.report_menu["menu"].add_command(label=report,
                                                 command=tk._setit(self.report_var, report))

    def change_language(self):
        lang = tk.simpledialog.askstring(self.lang_manager.get("select_language_title"),
                                         self.lang_manager.get("select_language_prompt"),
                                         parent=self)
        if lang:
            success = self.lang_manager.set_language(lang.lower())
            if success:
                messagebox.showinfo(self.lang_manager.get("language_changed_title"),
                                    self.lang_manager.get("language_changed_message"))
                self.refresh_language()
            else:
                messagebox.showerror(self.lang_manager.get("language_error_title"),
                                     self.lang_manager.get("language_error_message"))

    def generate_report(self):
        self.current_report_type = self.report_var.get()
        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            if self.current_report_type == "volunteers":
                data = user_service.get_users_by_role("volunteer")
                self.columns = ["ID", "Name", "Email", "Phone", "Location"]
            elif self.current_report_type == "ngos":
                data = user_service.get_users_by_role("ngo")
                self.columns = ["ID", "Name", "Email", "Phone", "Location"]
            elif self.current_report_type == "victims":
                data = user_service.get_users_by_role("victim")
                self.columns = ["ID", "Name", "Email", "Phone", "Location"]
            else:
                messagebox.showwarning(self.lang_manager.get("invalid_report_title"),
                                       self.lang_manager.get("invalid_report_message"))
                return

            if not data:
                messagebox.showinfo(self.lang_manager.get("no_data_title"),
                                    self.lang_manager.get("no_data_message").format(role=self.current_report_type))
                return

            self.tree["columns"] = self.columns
            self.tree["show"] = "headings"
            for col in self.columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120)

            self.report_data = data
            for row in data:
                self.tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror(self.lang_manager.get("error_title"),
                                 f"{self.lang_manager.get('error_message')} {str(e)}")

    def print_report(self):
        try:
            if not hasattr(self, 'report_data') or not self.report_data:
                messagebox.showwarning(self.lang_manager.get("print_error_title"),
                                       self.lang_manager.get("print_error_message"))
                return

            file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                     filetypes=[("PDF files", "*.pdf")],
                                                     title=self.lang_manager.get("save_report_title"))
            if not file_path:
                return

            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, height-50, f"{self.current_report_type.capitalize()} {self.lang_manager.get('report')}")
            c.setFont("Helvetica", 10)

            y = height - 80
            for i, col in enumerate(self.columns):
                c.drawString(50 + i*100, y, col)
            y -= 20

            for row in self.report_data:
                for i, item in enumerate(row):
                    c.drawString(50 + i*100, y, str(item))
                y -= 20
                if y < 50:
                    c.showPage()
                    y = height - 50

            c.save()
            messagebox.showinfo(self.lang_manager.get("print_success_title"),
                                self.lang_manager.get("print_success_message"))

        except Exception as e:
            messagebox.showerror(self.lang_manager.get("print_error_title"),
                                 f"{self.lang_manager.get('print_error_message')} {str(e)}")

# ---------- TEST ----------
if __name__ == "__main__":
    app = GenerateReportsApp(logged_in_user={"role": "admin", "name": "Admin"})
    app.mainloop()
