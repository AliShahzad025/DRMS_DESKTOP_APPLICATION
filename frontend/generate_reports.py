import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sv_ttk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Add parent folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Backend services
from services.user_service import UserService
from data.db_connection import DatabaseConnection
from data.user_repository import UserRepository
from frontend.language import LanguageManager

# ---------- Backend setup ----------
db = DatabaseConnection()
connection = db.connect()
if not connection:
    raise Exception("Cannot connect to database!")

user_repo = UserRepository(connection)
user_service = UserService(user_repo)

# ---------- Windows 11 Theme ----------
def apply_windows11_theme(window):
    sv_ttk.set_theme("light")
    style = ttk.Style()
    style.configure("TButton", padding=8, relief="flat", font=("Segoe UI", 11))
    style.map("TButton", background=[("active", "#e5e5e5")])
    style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#333")
    style.configure("Card.TFrame", background="#ffffff", relief="flat")
    window.option_add("*Font", ("Segoe UI", 11))
    window.configure(bg="#f3f3f3")

# ---------- Generate Reports App ----------
class GenerateReportsApp(tk.Tk):
    def __init__(self, logged_in_user):
        super().__init__()
        self.logged_in_user = logged_in_user
        self.lang_manager = LanguageManager()
        self.geometry("900x600")
        self.configure(bg="#f3f3f3")
        self.title("Generate Reports")
        apply_windows11_theme(self)
        self.create_widgets()

    def create_widgets(self):
        # ---------- MAIN CONTAINER ----------
        main_container = tk.Frame(self, bg="#f3f3f3")
        main_container.pack(fill="both", expand=True)
        
        # ---------- HEADER ----------
        header = tk.Frame(main_container, bg="#1E40AF", height=100)  # Changed to blue background
        header.pack(fill="x", pady=(0, 20))
        
        header_content = tk.Frame(header, bg="#1E40AF")
        header_content.pack(fill="both", expand=True, padx=30, pady=25)
        
        # BACK BUTTON - ALWAYS VISIBLE
        back_btn = tk.Button(
            header_content,
            text="◄ BACK TO ADMIN DASHBOARD",
            font=("Segoe UI", 14, "bold"),
            bg="#FF4444",  # Bright red
            fg="white",
            activebackground="#CC0000",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=25,
            pady=12,
            cursor="hand2",
            command=self.go_back_to_admin
        )
        back_btn.pack(side="left", padx=(0, 30))
        
        # Hover effects
        def on_enter(e):
            back_btn.config(bg='#CC0000', relief="sunken")
        def on_leave(e):
            back_btn.config(bg='#FF4444', relief="raised")
        back_btn.bind("<Enter>", on_enter)
        back_btn.bind("<Leave>", on_leave)

        # Title in center
        title_frame = tk.Frame(header_content, bg="#1E40AF")
        title_frame.pack(side="left", fill="both", expand=True)
        
        title_label = tk.Label(
            title_frame,
            text="📊 GENERATE REPORTS",
            font=("Segoe UI", 22, "bold"),
            fg="white",
            bg="#1E40AF"
        )
        title_label.pack(anchor="w")
        
        subtitle_label = tk.Label(
            title_frame,
            text="Generate reports for volunteers, NGOs, or victims",
            font=("Segoe UI", 11),
            fg="#E0E0E0",
            bg="#1E40AF"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # User info on the right
        if self.logged_in_user:
            user_frame = tk.Frame(header_content, bg="#1E40AF")
            user_frame.pack(side="right")
            
            tk.Label(
                user_frame,
                text="👤",
                font=("Segoe UI", 16),
                fg="white",
                bg="#1E40AF"
            ).pack(side="left", padx=(0, 10))
            
            user_info = tk.Label(
                user_frame,
                text=f"{self.logged_in_user.get('name', 'User')}\n{self.logged_in_user.get('role', 'Admin')}",
                font=("Segoe UI", 10, "bold"),
                fg="white",
                bg="#1E40AF",
                justify="right"
            )
            user_info.pack(side="right")

        # ---------- CONTENT AREA ----------
        content_frame = tk.Frame(main_container, bg="#f3f3f3")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Report type selection card
        card = ttk.Frame(content_frame, padding=25, style="Card.TFrame")
        card.pack(fill="x", pady=(0, 20))

        # Card title
        card_title = tk.Label(
            card,
            text="Report Generator",
            font=("Segoe UI", 16, "bold"),
            fg="#1E40AF",
            bg="#ffffff"
        )
        card_title.pack(anchor="w", pady=(0, 15))

        # Report type selection
        selection_frame = tk.Frame(card, bg="#ffffff")
        selection_frame.pack(fill="x", pady=10)

        tk.Label(
            selection_frame,
            text="Select Report Type:",
            font=("Segoe UI", 11, "bold"),
            bg="#ffffff"
        ).pack(side="left", padx=(0, 15))

        self.report_var = tk.StringVar(value="volunteers")
        self.report_menu = ttk.Combobox(
            selection_frame,
            textvariable=self.report_var,
            values=["volunteers", "ngos", "victims"],
            state="readonly",
            width=15,
            font=("Segoe UI", 11)
        )
        self.report_menu.pack(side="left")

        # Action buttons frame
        btn_frame = tk.Frame(card, bg="#ffffff")
        btn_frame.pack(fill="x", pady=20)

        self.generate_button = tk.Button(
            btn_frame,
            text="📊 Generate Report",
            font=("Segoe UI", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10,
            command=self.generate_report,
            cursor="hand2"
        )
        self.generate_button.pack(side="left", padx=(0, 10))

        self.print_button = tk.Button(
            btn_frame,
            text="🖨️ Print/Save PDF",
            font=("Segoe UI", 11, "bold"),
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=10,
            command=self.print_report,
            cursor="hand2"
        )
        self.print_button.pack(side="left", padx=(0, 10))

        # Language button
        self.language_button = tk.Button(
            card,
            text="🌐 Language Settings",
            font=("Segoe UI", 11),
            command=self.change_language,
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.language_button.pack(pady=10)

        # ---------- DATA DISPLAY AREA ----------
        data_frame = tk.Frame(content_frame, bg="#f3f3f3")
        data_frame.pack(fill="both", expand=True)

        # Treeview with scrollbars
        tree_frame = tk.Frame(data_frame, bg="#f3f3f3")
        tree_frame.pack(fill="both", expand=True)

        # Vertical scrollbar
        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side="right", fill="y")

        # Horizontal scrollbar
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")

        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set,
            selectmode="browse"
        )
        self.tree.pack(side="left", fill="both", expand=True)

        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)

        # Configure treeview style
        style = ttk.Style()
        style.configure("Treeview", 
                       rowheight=30, 
                       font=("Segoe UI", 10),
                       background="white",
                       fieldbackground="white")
        style.configure("Treeview.Heading", 
                       font=("Segoe UI", 11, "bold"),
                       background="#e9ecef",
                       foreground="#1E40AF")

        # Add status bar at bottom
        status_bar = tk.Frame(self, bg="#333", height=30)
        status_bar.pack(fill="x", side="bottom")
        
        self.status_label = tk.Label(
            status_bar,
            text="Ready to generate reports",
            fg="white",
            bg="#333",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(side="left", padx=20)

        # Add some padding at the bottom
        tk.Frame(content_frame, height=20, bg="#f3f3f3").pack()

        self.refresh_language()

    # ---------------- Functions ----------------
    def go_back_to_admin(self):
        """Go back to AdminOptionsApp"""
        if messagebox.askyesno("Confirm", "Return to Admin Dashboard?"):
            self.destroy()
            # Import here to avoid circular imports
            from frontend.login import AdminOptionsApp
            admin_app = AdminOptionsApp(
                logged_in_user=self.logged_in_user,
                db_connection=connection
            )
            admin_app.mainloop()

    def refresh_language(self):
        self.title(self.lang_manager.get("generate_reports") or "Generate Reports")

    def change_language(self):
        lang = simpledialog.askstring("Select Language", "Enter language code (en, es, etc.):", parent=self)
        if lang:
            self.lang_manager.set_language(lang)
            messagebox.showinfo("Language Changed", f"Language changed to {lang}.")
            self.refresh_language()

    def generate_report(self):
        report_type = self.report_var.get()
        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            if report_type == "volunteers":
                data = user_service.get_users_by_role("volunteer")
                columns = ["ID", "Name", "Email", "Phone", "Location", "Status"]
            elif report_type == "ngos":
                data = user_service.get_users_by_role("ngo")
                columns = ["ID", "Organization", "Email", "Phone", "Region", "Verified"]
            elif report_type == "victims":
                data = user_service.get_users_by_role("victim")
                columns = ["ID", "Name", "Email", "Phone", "Location", "Needs"]
            else:
                messagebox.showwarning("Invalid Report", "Invalid report type selected.")
                self.status_label.config(text="✗ Invalid report type")
                return

            if not data:
                messagebox.showinfo("No Data", f"No data available for {report_type}.")
                self.status_label.config(text=f"✗ No data for {report_type}")
                return

            self.columns = columns
            self.report_data = data
            self.tree["columns"] = columns
            self.tree["show"] = "headings"
            
            # Configure columns with better width
            for col in columns:
                self.tree.heading(col, text=col, anchor="w")
                self.tree.column(col, width=150, minwidth=100, stretch=True)
            
            # Insert data
            for row in data:
                self.tree.insert("", "end", values=row)
                
            self.status_label.config(text=f"✓ Generated {report_type} report with {len(data)} records")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_label.config(text="✗ Error generating report")

    def print_report(self):
        try:
            if not hasattr(self, 'report_data') or not self.report_data:
                messagebox.showwarning("Print Error", "Generate a report first before printing.")
                self.status_label.config(text="✗ Generate report first")
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"{self.report_var.get()}_report.pdf"
            )
            if not file_path:
                return

            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            
            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height-50, f"{self.report_var.get().upper()} REPORT")
            
            # Subtitle with date
            from datetime import datetime
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.setFont("Helvetica", 10)
            c.drawString(50, height-70, f"Generated on: {date_str}")
            c.drawString(50, height-85, f"Generated by: {self.logged_in_user.get('name', 'System')}")
            
            # Column headers
            c.setFont("Helvetica-Bold", 10)
            y = height - 120
            col_width = (width - 100) / len(self.columns)
            for i, col in enumerate(self.columns):
                c.drawString(50 + i*col_width, y, col)
            
            # Data rows
            c.setFont("Helvetica", 9)
            y -= 20
            
            for row in self.report_data:
                for i, item in enumerate(row):
                    c.drawString(50 + i*col_width, y, str(item))
                y -= 15
                if y < 50:  # New page if running out of space
                    c.showPage()
                    y = height - 50
                    c.setFont("Helvetica", 9)

            # Footer
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(50, 30, f"Total Records: {len(self.report_data)}")
            c.drawString(width-250, 30, "DRMS - Disaster Relief Management System")

            c.save()
            
            messagebox.showinfo("Success", f"✅ PDF report saved successfully!\n\nLocation: {file_path}")
            self.status_label.config(text=f"✓ PDF exported: {os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF:\n{str(e)}")
            self.status_label.config(text="✗ Failed to export PDF")


# ---------- Test ----------
if __name__ == "__main__":
    app = GenerateReportsApp(
        logged_in_user={
            "userID": 1,
            "name": "Admin User", 
            "role": "admin",
            "email": "admin@drms.com"
        }
    )
    app.mainloop()