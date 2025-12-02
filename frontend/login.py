import sys
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
import tkinter.ttk as ttk
import sv_ttk
import ctypes
from ctypes import wintypes
from datetime import datetime

# ----------------- Utilities: Acrylic (Windows 10/11) -----------------
def enable_acrylic_for_window(win, accent_color=0xCCFFFFFF):
    """
    Enable acrylic (blur/translucency) for Tk window.
    """
    try:
        hwnd = wintypes.HWND(int(win.winfo_id()))
        
        class ACCENTPOLICY(ctypes.Structure):
            _fields_ = [
                ("AccentState", ctypes.c_int),
                ("AccentFlags", ctypes.c_int),
                ("GradientColor", ctypes.c_uint),
                ("AnimationId", ctypes.c_int)
            ]

        class WINCOMPATTRDATA(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.c_void_p),
                ("SizeOfData", ctypes.c_size_t)
            ]

        ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
        
        policy = ACCENTPOLICY()
        policy.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
        policy.AccentFlags = 2
        policy.GradientColor = accent_color
        policy.AnimationId = 0

        data = WINCOMPATTRDATA()
        data.Attribute = 19  # WCA_ACCENT_POLICY
        data.Data = ctypes.byref(policy)
        data.SizeOfData = ctypes.sizeof(policy)

        set_window_comp_attr = ctypes.windll.user32.SetWindowCompositionAttribute
        set_window_comp_attr(hwnd, ctypes.byref(data))
    except Exception:
        pass

# ----------------- Enhanced Windows 11 Theme -----------------
def apply_windows11_theme(window):
    """
    Enhanced Windows 11 theme with consistent styling across all apps.
    """
    sv_ttk.set_theme("light")
    style = ttk.Style()
    
    # Font definitions - LARGER FONTS
    title_font = ("Segoe UI", 28, "bold")
    header_font = ("Segoe UI", 22, "bold")
    subheader_font = ("Segoe UI", 14)
    body_font = ("Segoe UI", 13)
    small_font = ("Segoe UI", 11)
    
    # Color scheme
    primary_color = "#1E40AF"
    secondary_color = "#3B82F6"
    accent_color = "#10B981"
    danger_color = "#EF4444"
    card_color = "#FFFFFF"
    background_color = "#F8FAFC"
    
    # Configure window
    window.configure(bg=background_color)
    window.option_add("*Font", body_font)
    
    # Custom button styles
    style.configure("Primary.TButton",
                   font=("Segoe UI", 14, "bold"),
                   background=primary_color,
                   foreground="white",
                   padding=(25, 15),
                   relief="flat")
    
    style.map("Primary.TButton",
             background=[("active", secondary_color)],
             foreground=[("active", "white")])
    
    style.configure("Secondary.TButton",
                   font=("Segoe UI", 13),
                   background="#E5E7EB",
                   foreground="#374151",
                   padding=(20, 12),
                   relief="flat")
    
    style.map("Secondary.TButton",
             background=[("active", "#D1D5DB")],
             foreground=[("active", "#1F2937")])
    
    style.configure("Danger.TButton",
                   font=("Segoe UI", 14, "bold"),
                   background=danger_color,
                   foreground="white",
                   padding=(25, 15),
                   relief="flat")
    
    style.map("Danger.TButton",
             background=[("active", "#DC2626")],
             foreground=[("active", "white")])
    
    # Frame styles
    style.configure("Card.TFrame", background=card_color, relief="flat")
    style.configure("Header.TFrame", background=primary_color)
    style.configure("Title.TLabel", font=title_font, foreground="white", background=primary_color)
    style.configure("Subtitle.TLabel", font=subheader_font, foreground="#E5E7EB", background=primary_color)
    style.configure("Form.TLabel", font=("Segoe UI", 13, "bold"), foreground="#374151", background=card_color)
    
    # Entry styles
    style.configure("Form.TEntry",
                   font=body_font,
                   padding=(15, 10),
                   relief="solid",
                   borderwidth=1,
                   bordercolor="#D1D5DB",
                   focuscolor=primary_color)
    
    style.map("Form.TEntry", bordercolor=[("focus", primary_color)])
    
    # Combobox styles
    style.configure("Form.TCombobox", font=body_font, padding=(15, 10))
    style.map("Form.TCombobox",
             fieldbackground=[("focus", "white")],
             selectbackground=[("focus", primary_color)])
    
    return {
        "primary": primary_color,
        "secondary": secondary_color,
        "accent": accent_color,
        "danger": danger_color,
        "card": card_color,
        "background": background_color
    }

# ----------------- Modern Card Frame -----------------
class ModernCardFrame(ttk.Frame):
    """
    A beautiful card container with shadow effect.
    """
    def __init__(self, master, padding=25, **kwargs):
        super().__init__(master, style="Card.TFrame", padding=padding, **kwargs)
        self.configure(relief="solid", borderwidth=1)

# ----------------- Add parent folder to sys.path -----------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.user_service import UserService
from data.db_connection import DatabaseConnection
from data.user_repository import UserRepository
from frontend.language import LanguageManager

# ----------------- Database connection -----------------
db = DatabaseConnection()
connection = db.connect()
if not connection:
    raise Exception("Cannot connect to database!")

user_repo = UserRepository(connection)
user_service = UserService(user_repo)

# ----------------- Normalize user -----------------
def normalize_user(user):
    if isinstance(user, dict):
        return user
    elif isinstance(user, tuple):
        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "phone": user[3],
            "location": user[4],
            "lat": user[5],
            "lng": user[6],
            "lang": user[7],
            "role": user[8]
        }
    else:
        return {}

# ----------------- Base App -----------------
class BaseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang_manager = LanguageManager()
        self.colors = None

    def create_header(self, title, subtitle=None, show_back_button=False, back_command=None):
        """
        Creates a consistent header for all apps.
        """
        header = tk.Frame(self, bg=self.colors["primary"], height=120)
        header.pack(fill="x", side="top")
        
        header_content = tk.Frame(header, bg=self.colors["primary"])
        header_content.pack(fill="both", expand=True, padx=40, pady=25)
        
        # Left side: Back button if needed
        left_frame = tk.Frame(header_content, bg=self.colors["primary"])
        left_frame.pack(side="left", fill="y")
        
        if show_back_button and back_command:
            back_btn = tk.Button(
                left_frame,
                text="← Back to Login",
                font=("Segoe UI", 14, "bold"),
                bg=self.colors["danger"],
                fg="white",
                activebackground="#DC2626",
                activeforeground="white",
                relief="raised",
                bd=3,
                padx=25,
                pady=12,
                cursor="hand2",
                command=back_command
            )
            back_btn.pack(side="left", padx=(0, 30))
            
            def on_enter(e):
                back_btn.config(bg='#DC2626')
            def on_leave(e):
                back_btn.config(bg=self.colors["danger"])
            back_btn.bind("<Enter>", on_enter)
            back_btn.bind("<Leave>", on_leave)
        
        # Center: Title and subtitle
        center_frame = tk.Frame(header_content, bg=self.colors["primary"])
        center_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            center_frame,
            text=title,
            font=("Segoe UI", 26, "bold"),
            fg="white",
            bg=self.colors["primary"]
        ).pack(anchor="w")
        
        if subtitle:
            tk.Label(
                center_frame,
                text=subtitle,
                font=("Segoe UI", 13),
                fg="#E0E0E0",
                bg=self.colors["primary"]
            ).pack(anchor="w", pady=(8, 0))
        
        return header

    def create_status_bar(self):
        """
        Creates a status bar at the bottom.
        """
        status_bar = tk.Frame(self, bg="#1F2937", height=40)
        status_bar.pack(fill="x", side="bottom")
        
        self.status_label = tk.Label(
            status_bar,
            text="Ready",
            fg="#D1D5DB",
            bg="#1F2937",
            font=("Segoe UI", 11)
        )
        self.status_label.pack(side="left", padx=25)
        
        self.time_label = tk.Label(
            status_bar,
            text="",
            fg="#9CA3AF",
            bg="#1F2937",
            font=("Segoe UI", 11)
        )
        self.time_label.pack(side="right", padx=25)
        
        self.update_time()
    
    def update_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.after(1000, self.update_time)

# ----------------- Login App -----------------
class LoginApp(BaseApp):
    def __init__(self):
        super().__init__()
        self.title("DRMS - Login")
        self.geometry("900x800")
        self.resizable(True, True)
        
        self.colors = apply_windows11_theme(self)
        
        try:
            enable_acrylic_for_window(self, accent_color=0xCCFFFFFF)
        except Exception:
            pass
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.winfo_screenheight() // 2) - (800 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.create_widgets()

    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg=self.colors["primary"], height=150)
        header.pack(fill="x", side="top")
        
        header_content = tk.Frame(header, bg=self.colors["primary"])
        header_content.pack(fill="both", expand=True, padx=50, pady=40)
        
        tk.Label(
            header_content,
            text="🌐 DISASTER RELIEF MANAGEMENT SYSTEM",
            font=("Segoe UI", 32, "bold"),
            fg="white",
            bg=self.colors["primary"]
        ).pack(anchor="center")
        
        tk.Label(
            header_content,
            text="Emergency Response & Coordination Platform",
            font=("Segoe UI", 16),
            fg="#E0E0E0",
            bg=self.colors["primary"]
        ).pack(anchor="center", pady=(10, 0))
        
        # Create a scrollable main container
        main_container = tk.Frame(self, bg=self.colors["background"])
        main_container.pack(fill="both", expand=True)
        
        # Create canvas with scrollbar
        canvas = tk.Canvas(main_container, bg=self.colors["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["background"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=50, pady=30)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Login card
        card = ModernCardFrame(scrollable_frame)
        card.pack(fill="both", expand=True, pady=(0, 20))
        
        # Card title
        tk.Label(
            card,
            text="🔐 Secure Login",
            font=("Segoe UI", 24, "bold"),
            fg=self.colors["primary"],
            bg="white"
        ).pack(anchor="w", pady=(0, 30))
        
        # Form fields
        form_frame = tk.Frame(card, bg="white")
        form_frame.pack(fill="both", expand=True)
        
        # Email field
        email_frame = tk.Frame(form_frame, bg="white")
        email_frame.pack(fill="x", pady=(0, 25))
        
        tk.Label(
            email_frame,
            text="📧 Email Address",
            font=("Segoe UI", 14, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 12))
        
        self.email_entry = ttk.Entry(form_frame, style="Form.TEntry", width=40)
        self.email_entry.pack(fill="x", pady=(0, 25))
        
        # Password field
        password_frame = tk.Frame(form_frame, bg="white")
        password_frame.pack(fill="x", pady=(0, 25))
        
        tk.Label(
            password_frame,
            text="🔒 Password",
            font=("Segoe UI", 14, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 12))
        
        self.password_entry = ttk.Entry(
            form_frame,
            style="Form.TEntry",
            show="•",
            width=40
        )
        self.password_entry.pack(fill="x", pady=(0, 25))
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Role selection
        role_frame = tk.Frame(form_frame, bg="white")
        role_frame.pack(fill="x", pady=(0, 40))
        
        tk.Label(
            role_frame,
            text="👤 Select Your Role",
            font=("Segoe UI", 14, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 12))
        
        self.role_var = tk.StringVar(value="Admin")
        role_combo = ttk.Combobox(
            form_frame,
            textvariable=self.role_var,
            values=["Admin", "Volunteer", "NGO", "Victim"],
            state="readonly",
            style="Form.TCombobox"
        )
        role_combo.pack(fill="x", pady=(0, 25))
        
        # Login button
        login_btn = tk.Button(
            form_frame,
            text="🚀 SIGN IN TO DRMS",
            font=("Segoe UI", 16, "bold"),
            bg=self.colors["primary"],
            fg="white",
            activebackground=self.colors["secondary"],
            activeforeground="white",
            relief="flat",
            padx=30,
            pady=18,
            cursor="hand2",
            command=self.login
        )
        login_btn.pack(fill="x", pady=(0, 25))
        
        # Footer
        footer = tk.Frame(card, bg="white")
        footer.pack(fill="x", pady=(15, 0))
        
        tk.Label(
            footer,
            text="📞 Emergency Support: 112 | ✉️ Email: support@drms.gov.pk | 🌐 Website: www.drms.gov.pk",
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white"
        ).pack(anchor="center")
        
        self.after(100, lambda: self.email_entry.focus_set())
        self.create_status_bar()

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()

        if not email or not password:
            messagebox.showwarning("Missing Information", "Please enter both email and password.", parent=self)
            self.status_label.config(text="✗ Please enter email and password")
            return

        self.status_label.config(text="⏳ Verifying credentials...")
        self.update()

        try:
            user = user_service.authenticate_user(email, password)
            user = normalize_user(user)

            if user and user.get("role") == role:
                user_name = user.get('name', 'User')
                self.status_label.config(text=f"✓ Welcome, {user_name}!")
                
                messagebox.showinfo("Login Successful", f"Welcome back, {user_name}!", parent=self)
                self.destroy()
                
                if role == "Admin":
                    app = AdminOptionsApp(logged_in_user=user, db_connection=connection)
                    app.mainloop()
                elif role == "Volunteer":
                    from frontend.volunteer import VolunteerApp
                    app = VolunteerApp(logged_in_user=user, db_connection=connection)
                    app.mainloop()
                elif role == "NGO":
                    app = NGODashboardApp(logged_in_user=user, db_connection=connection)
                    app.mainloop()
                elif role == "Victim":
                    app = VictimDashboardApp(logged_in_user=user, db_connection=connection)
                    app.mainloop()
            else:
                self.status_label.config(text="✗ Invalid credentials")
                messagebox.showerror("Login Failed", "Invalid email, password, or role selected.", parent=self)
                
        except Exception as e:
            self.status_label.config(text="✗ Login error")
            messagebox.showerror("Login Error", f"An error occurred during login: {str(e)}", parent=self)

# ----------------- Admin Options App -----------------
class AdminOptionsApp(BaseApp):
    def __init__(self, logged_in_user, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user
        self.colors = apply_windows11_theme(self)
        self.title("DRMS - Admin Dashboard")
        self.geometry("1000x900")
        self.resizable(True, True)
        
        try:
            enable_acrylic_for_window(self, accent_color=0xCCFFFFFF)
        except Exception:
            pass
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.winfo_screenheight() // 2) - (900 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        self.create_status_bar()

    def create_widgets(self):
        # Header
        self.create_header(
            title="👑 ADMINISTRATOR DASHBOARD",
            subtitle=f"Welcome, {self.logged_in_user.get('name', 'Administrator')}",
            show_back_button=True,
            back_command=self.go_back_to_login
        )
        
        # Create a scrollable main container
        main_container = tk.Frame(self, bg=self.colors["background"])
        main_container.pack(fill="both", expand=True)
        
        # Create canvas with scrollbar
        canvas = tk.Canvas(main_container, bg=self.colors["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["background"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=50, pady=30)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Welcome card
        welcome_card = ModernCardFrame(scrollable_frame, padding=30)
        welcome_card.pack(fill="x", pady=(0, 30))
        
        tk.Label(
            welcome_card,
            text=f"Hello, {self.logged_in_user.get('name', 'Admin')}!",
            font=("Segoe UI", 22, "bold"),
            fg=self.colors["primary"],
            bg="white"
        ).pack(anchor="w")
        
        tk.Label(
            welcome_card,
            text="What would you like to manage today?",
            font=("Segoe UI", 15),
            fg="#6B7280",
            bg="white"
        ).pack(anchor="w", pady=(10, 0))
        
        # Options card
        options_card = ModernCardFrame(scrollable_frame, padding=30)
        options_card.pack(fill="both", expand=True)
        
        # Create two columns for buttons
        columns_frame = tk.Frame(options_card, bg="white")
        columns_frame.pack(fill="both", expand=True)
        
        left_column = tk.Frame(columns_frame, bg="white")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        right_column = tk.Frame(columns_frame, bg="white")
        right_column.pack(side="right", fill="both", expand=True, padx=(15, 0))
        
        # Admin options buttons
        left_options = [
            ("📊 GENERATE REPORTS", self.open_generate_reports, self.colors["primary"]),
            ("📢 NOTIFY STAKEHOLDERS", self.open_notify_stakeholders, "#3B82F6"),
            ("🔍 PRIORITIZE REQUESTS", self.open_prioritize_requests, "#10B981"),
            ("✅ VERIFY VOLUNTEERS", self.open_verify_volunteer, "#8B5CF6"),
        ]
        
        right_options = [
            ("🏢 VERIFY NGOS", self.open_verify_ngo, "#F59E0B"),
            ("📝 REGISTER NEW NGO", self.open_register_ngo, "#EF4444"),
            ("🌐 LANGUAGE SETTINGS", self.change_language, "#6B7280"),
            ("📋 SYSTEM OVERVIEW", self.show_system_overview, "#06B6D4"),
        ]
        
        # Add buttons to left column
        for text, command, color in left_options:
            btn = tk.Button(
                left_column,
                text=text,
                font=("Segoe UI", 14, "bold"),
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                relief="flat",
                padx=25,
                pady=18,
                cursor="hand2",
                command=command
            )
            btn.pack(fill="x", pady=12)
            
            def make_hover(button, btn_color):
                def on_enter(e):
                    button.config(bg=self.adjust_color(btn_color, -20))
                def on_leave(e):
                    button.config(bg=btn_color)
                button.bind("<Enter>", on_enter)
                button.bind("<Leave>", on_leave)
            
            make_hover(btn, color)
        
        # Add buttons to right column
        for text, command, color in right_options:
            btn = tk.Button(
                right_column,
                text=text,
                font=("Segoe UI", 14, "bold"),
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                relief="flat",
                padx=25,
                pady=18,
                cursor="hand2",
                command=command
            )
            btn.pack(fill="x", pady=12)
            
            def make_hover(button, btn_color):
                def on_enter(e):
                    button.config(bg=self.adjust_color(btn_color, -20))
                def on_leave(e):
                    button.config(bg=btn_color)
                button.bind("<Enter>", on_enter)
                button.bind("<Leave>", on_leave)
            
            make_hover(btn, color)

    def show_system_overview(self):
        messagebox.showinfo(
            "System Overview",
            "DRMS - Disaster Relief Management System\n\n"
            "Version: 2.0.0\n"
            "Users: Connected to database\n"
            f"Logged in as: {self.logged_in_user.get('name', 'Admin')}\n"
            "Status: All systems operational",
            parent=self
        )

    def adjust_color(self, hex_color, amount):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(max(0, min(255, x + amount)) for x in rgb)
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    def go_back_to_login(self):
        if messagebox.askyesno("Confirm", "Return to login screen?"):
            self.destroy()
            login_app = LoginApp()
            login_app.mainloop()

    def change_language(self):
        lang = simpledialog.askstring("Select Language", "Enter language code (en, es, etc.):", parent=self)
        if lang:
            self.lang_manager.set_language(lang.lower())
            messagebox.showinfo("Language Changed", f"Language changed to {lang}.", parent=self)

    def open_generate_reports(self):
        self.destroy()
        from frontend.generate_reports import GenerateReportsApp
        reports_app = GenerateReportsApp(logged_in_user=self.logged_in_user)
        reports_app.mainloop()

    def open_notify_stakeholders(self):
        self.destroy()
        from frontend.notify_stakeholders import NotifyStakeholdersApp
        notify_app = NotifyStakeholdersApp(logged_in_user=self.logged_in_user)
        notify_app.mainloop()

    def open_prioritize_requests(self):
        self.destroy()
        from frontend.prioritize_requests import PrioritizeRequestsApp
        app = PrioritizeRequestsApp(logged_in_user=self.logged_in_user, db_connection=connection)
        app.mainloop()

    def open_verify_volunteer(self):
        self.destroy()
        from frontend.verify_volunteer import VerifyVolunteerApp
        app = VerifyVolunteerApp(logged_in_user=self.logged_in_user, db_connection=connection)
        app.mainloop()

    def open_verify_ngo(self):
        self.destroy()
        from frontend.verify_ngo import VerifyNGOApp
        app = VerifyNGOApp(db_connection=connection)
        app.mainloop()

    def open_register_ngo(self):
        self.destroy()
        from frontend.register_ngo import RegisterNGOApp
        app = RegisterNGOApp(db_connection=connection)
        app.mainloop()

# ----------------- NGO Dashboard -----------------
# ----------------- NGO Dashboard -----------------
class NGODashboardApp(BaseApp):
    def __init__(self, logged_in_user, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user
        self.db_connection = db_connection
        self.colors = apply_windows11_theme(self)
        self.title(f"DRMS - NGO Dashboard")
        self.geometry("900x800")
        self.resizable(True, True)
        
        try:
            enable_acrylic_for_window(self, accent_color=0xCCFFFFFF)
        except Exception:
            pass
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.winfo_screenheight() // 2) - (800 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        self.create_status_bar()

    def create_widgets(self):
        # Header with back button
        self.create_header(
            title="🏢 NGO OPERATIONS CENTER",
            subtitle=f"Welcome, {self.logged_in_user.get('name', 'NGO Manager')}",
            show_back_button=True,
            back_command=self.go_back_to_login
        )
        
        # Create scrollable main container
        main_container = tk.Frame(self, bg=self.colors["background"])
        main_container.pack(fill="both", expand=True)
        
        # Create canvas with scrollbar
        canvas = tk.Canvas(main_container, bg=self.colors["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["background"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=50, pady=30)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Welcome card
        welcome_card = ModernCardFrame(scrollable_frame, padding=30)
        welcome_card.pack(fill="x", pady=(0, 30))
        
        tk.Label(
            welcome_card,
            text=f"Organization: {self.logged_in_user.get('name', 'NGO')}",
            font=("Segoe UI", 22, "bold"),
            fg=self.colors["primary"],
            bg="white"
        ).pack(anchor="w")
        
        tk.Label(
            welcome_card,
            text="Manage your relief operations and coordinate with volunteers",
            font=("Segoe UI", 15),
            fg="#6B7280",
            bg="white"
        ).pack(anchor="w", pady=(10, 0))
        
        # Options card
        options_card = ModernCardFrame(scrollable_frame, padding=30)
        options_card.pack(fill="both", expand=True)
        
        # NGO options buttons
        options = [
            ("📋 ASSIGN TASKS TO VOLUNTEERS", self.open_assign_tasks, self.colors["primary"]),
            ("📜 VIEW TASK HISTORY & REPORTS", self.open_task_history, "#3B82F6"),
            ("📦 MANAGE RESOURCES & INVENTORY", self.open_manage_resources, "#10B981"),
            ("👤 REGISTER NEW VOLUNTEER", self.open_register_volunteer, "#8B5CF6"),
            ("📍 TRACK & MANAGE REQUESTS", self.open_track_request, "#F59E0B"),
            ("🌐 LANGUAGE SETTINGS", self.change_language, "#6B7280")
        ]
        
        for text, command, color in options:
            btn = tk.Button(
                options_card,
                text=text,
                font=("Segoe UI", 14, "bold"),
                bg=color,
                fg="white",
                activebackground=color,
                activeforeground="white",
                relief="flat",
                padx=25,
                pady=18,
                cursor="hand2",
                command=command
            )
            btn.pack(fill="x", pady=12)
            
            # Add hover effect
            def make_hover(button, btn_color):
                def on_enter(e):
                    button.config(bg=self.adjust_color(btn_color, -20))
                def on_leave(e):
                    button.config(bg=btn_color)
                button.bind("<Enter>", on_enter)
                button.bind("<Leave>", on_leave)
            
            make_hover(btn, color)

    def adjust_color(self, hex_color, amount):
        """Helper to adjust color brightness"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(max(0, min(255, x + amount)) for x in rgb)
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    def go_back_to_login(self):
        """Return to login screen"""
        if messagebox.askyesno("Confirm", "Return to login screen?"):
            self.destroy()
            login_app = LoginApp()
            login_app.mainloop()

    def open_assign_tasks(self):
        """Open assign tasks module"""
        self.destroy()
        from frontend.assign_tasks import AssignTaskApp
        app = AssignTaskApp(logged_in_user=self.logged_in_user, db_connection=self.db_connection)
        app.mainloop()

    def open_task_history(self):
        """Open task history window"""
        history_window = tk.Toplevel(self)
        apply_windows11_theme(history_window)
        history_window.title("Task History - Detailed View")
        history_window.geometry("1200x700")
        
        history_window.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        history_window.geometry(f"+{x}+{y}")
        
        # Add scrollable content
        canvas = tk.Canvas(history_window, highlightthickness=0)
        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        tk.Label(scrollable_frame, text="Task History", font=("Segoe UI", 24, "bold")).pack(pady=20)
        
        # Simulated task data
        tasks = [
            ("Task 1", "Emergency Food Delivery", "Completed", "John Doe"),
            ("Task 2", "Medical Supplies", "In Progress", "Jane Smith"),
            ("Task 3", "Shelter Setup", "Pending", "Bob Wilson"),
        ]
        
        for task_id, title, status, volunteer in tasks:
            task_frame = tk.Frame(scrollable_frame, relief="solid", bd=1, padx=20, pady=10)
            task_frame.pack(fill="x", pady=5, padx=20)
            tk.Label(task_frame, text=f"{title} - {status}", font=("Segoe UI", 12)).pack(anchor="w")
            tk.Label(task_frame, text=f"Assigned to: {volunteer}", font=("Segoe UI", 10), fg="gray").pack(anchor="w")

    def open_manage_resources(self):
        """Open manage resources module"""
        self.destroy()
        from frontend.manage_resources import ManageResourcesApp
        app = ManageResourcesApp(logged_in_user=self.logged_in_user, db_connection=self.db_connection)
        app.mainloop()

    def open_register_volunteer(self):
        """Open register volunteer module"""
        self.destroy()
        from frontend.register_volunteer import RegisterVolunteerApp
        app = RegisterVolunteerApp(db_connection=self.db_connection)
        app.mainloop()

    def open_track_request(self):
        """Open track request module"""
        self.destroy()
        from frontend.track_request import TrackRequestApp
        app = TrackRequestApp(logged_in_user=self.logged_in_user, db_connection=self.db_connection)
        app.mainloop()

    def change_language(self):
        """Change language settings"""
        lang = simpledialog.askstring("Select Language", "Enter language code (en, es, etc.):", parent=self)
        if lang:
            self.lang_manager.set_language(lang)
            messagebox.showinfo("Language Changed", f"Language changed to {lang}.", parent=self)

# ----------------- Victim Dashboard -----------------
class VictimDashboardApp(BaseApp):
    def __init__(self, logged_in_user, db_connection=None):
        super().__init__()
        self.logged_in_user = logged_in_user
        self.colors = apply_windows11_theme(self)
        self.title(f"DRMS - Victim Assistance Portal")
        self.geometry("800x700")
        self.resizable(True, True)
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        self.create_status_bar()

    def create_widgets(self):
        # Header with back button
        self.create_header(
            title="😢 VICTIM ASSISTANCE PORTAL",
            subtitle=f"We're here to help you, {self.logged_in_user.get('name', 'User')}",
            show_back_button=True,
            back_command=self.go_back_to_login
        )
        
        # Create scrollable main container
        main_container = tk.Frame(self, bg=self.colors["background"])
        main_container.pack(fill="both", expand=True)
        
        # Create canvas with scrollbar
        canvas = tk.Canvas(main_container, bg=self.colors["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["background"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=50, pady=30)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Welcome card
        welcome_card = ModernCardFrame(scrollable_frame, padding=40)
        welcome_card.pack(fill="both", expand=True)
        
        tk.Label(
            welcome_card,
            text="🆘 ASSISTANCE & SUPPORT",
            font=("Segoe UI", 24, "bold"),
            fg=self.colors["primary"],
            bg="white"
        ).pack(anchor="w", pady=(0, 30))
        
        tk.Label(
            welcome_card,
            text="If you need assistance, resources, or want to provide feedback about the relief efforts, please use the options below.",
            font=("Segoe UI", 15),
            fg="#6B7280",
            bg="white",
            wraplength=600,
            justify="left"
        ).pack(anchor="w", pady=(0, 40))
        
        # Main button
        feedback_btn = tk.Button(
            welcome_card,
            text="💬 PROVIDE FEEDBACK OR REQUEST ASSISTANCE",
            font=("Segoe UI", 16, "bold"),
            bg="#10B981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="flat",
            padx=40,
            pady=25,
            cursor="hand2",
            command=self.open_give_feedback
        )
        feedback_btn.pack(fill="x", pady=(0, 40))
        
        # Emergency contact info
        emergency_frame = tk.Frame(welcome_card, bg="white")
        emergency_frame.pack(fill="x", pady=(20, 0))
        
        tk.Label(
            emergency_frame,
            text="🚨 EMERGENCY CONTACTS",
            font=("Segoe UI", 16, "bold"),
            fg="#EF4444",
            bg="white"
        ).pack(anchor="center", pady=(0, 20))
        
        contacts = [
            ("📞 Emergency Services", "112"),
            ("🏥 Medical Emergency", "115"),
            ("🚒 Fire Department", "16"),
            ("👮 Police", "15")
        ]
        
        for service, number in contacts:
            contact_frame = tk.Frame(emergency_frame, bg="white")
            contact_frame.pack(fill="x", pady=8)
            
            tk.Label(
                contact_frame,
                text=service,
                font=("Segoe UI", 14),
                fg="#374151",
                bg="white",
                width=25,
                anchor="w"
            ).pack(side="left")
            
            tk.Label(
                contact_frame,
                text=number,
                font=("Segoe UI", 14, "bold"),
                fg="#EF4444",
                bg="white"
            ).pack(side="right")

    def go_back_to_login(self):
        if messagebox.askyesno("Confirm", "Return to login screen?"):
            self.destroy()
            login_app = LoginApp()
            login_app.mainloop()

    def open_give_feedback(self):
        self.destroy()
        from frontend.give_feedback import GiveFeedbackApp
        app = GiveFeedbackApp(logged_in_user=self.logged_in_user, db_connection=connection)
        app.mainloop()

# ----------------- Run the login -----------------
if __name__ == "__main__":
    login_app = LoginApp()
    login_app.mainloop()