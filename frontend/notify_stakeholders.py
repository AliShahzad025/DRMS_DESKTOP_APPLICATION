# File: notify_stakeholders.py

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sv_ttk
from datetime import datetime

# Add parent folder to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Backend services
from services.user_service import UserService
from data.db_connection import DatabaseConnection
from data.user_repository import UserRepository

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
    style.configure("TButton", padding=10, relief="flat", font=("Segoe UI", 11))
    style.map("TButton", background=[("active", "#e5e5e5")])
    style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#1E40AF")
    style.configure("Card.TFrame", background="#ffffff", relief="flat")
    style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"), foreground="#1E40AF")
    style.configure("Subtitle.TLabel", font=("Segoe UI", 11), foreground="#666")
    window.option_add("*Font", ("Segoe UI", 11))
    window.configure(bg="#f3f3f3")

# ---------- Notify Stakeholders App ----------
class NotifyStakeholdersApp(tk.Tk):
    def __init__(self, logged_in_user):
        super().__init__()
        self.logged_in_user = logged_in_user
        self.title("DRMS - Stakeholder Notifications")
        self.geometry("1000x750")
        self.configure(bg="#f3f3f3")
        apply_windows11_theme(self)
        
        # Center window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        self.create_widgets()

    def create_widgets(self):
        # ========== MAIN CONTAINER ==========
        main_container = tk.Frame(self, bg="#f3f3f3")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ========== HEADER ==========
        header = tk.Frame(main_container, bg="#1E40AF", height=100)
        header.pack(fill="x", pady=(0, 20))
        
        header_content = tk.Frame(header, bg="#1E40AF")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # BACK BUTTON - ALWAYS SHOW (not conditional)
        back_btn = tk.Button(
            header_content,
            text="◄ BACK TO ADMIN DASHBOARD",
            font=("Segoe UI", 14, "bold"),
            bg="#FF4444",
            fg="white",
            activebackground="#FF2222",
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
            back_btn.config(bg='#FF2222')
        def on_leave(e):
            back_btn.config(bg='#FF4444')
        back_btn.bind("<Enter>", on_enter)
        back_btn.bind("<Leave>", on_leave)
        
        # TITLE
        title_frame = tk.Frame(header_content, bg="#1E40AF")
        title_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            title_frame,
            text="📢 NOTIFY STAKEHOLDERS",
            font=("Segoe UI", 22, "bold"),
            fg="white",
            bg="#1E40AF"
        ).pack(anchor="w")
        
        tk.Label(
            title_frame,
            text="Send messages to volunteers, NGOs, or victims",
            font=("Segoe UI", 11),
            fg="#E0E0E0",
            bg="#1E40AF"
        ).pack(anchor="w", pady=(5, 0))
        
        # USER INFO
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
            
            tk.Label(
                user_frame,
                text=f"{self.logged_in_user.get('name', 'User')}\n{self.logged_in_user.get('role', 'User').upper()}",
                font=("Segoe UI", 10, "bold"),
                fg="white",
                bg="#1E40AF",
                justify="right"
            ).pack(side="right")
        
        # ========== CONTENT AREA ==========
        content_container = tk.Frame(main_container, bg="#f3f3f3")
        content_container.pack(fill="both", expand=True)
        
        # Left Panel - Configuration
        left_panel = ttk.Frame(content_container, style="Card.TFrame", padding=25)
        left_panel.pack(side="left", fill="y", padx=(0, 15))
        
        # Panel Title
        tk.Label(
            left_panel,
            text="Notification Settings",
            font=("Segoe UI", 16, "bold"),
            fg="#1E40AF",
            bg="white"
        ).pack(anchor="w", pady=(0, 20))
        
        # Stakeholder Type Selection
        type_frame = tk.Frame(left_panel, bg="white")
        type_frame.pack(fill="x", pady=(0, 25))
        
        tk.Label(
            type_frame,
            text="Select Recipients:",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#333"
        ).pack(anchor="w", pady=(0, 15))
        
        self.stakeholder_var = tk.StringVar(value="volunteer")
        
        # Radio buttons for stakeholder type
        stakeholder_types = [
            ("👥 Volunteers", "volunteer"),
            ("🏢 NGOs", "ngo"),
            ("😢 Victims", "victim"),
            ("👨‍💼 All Admins", "admin"),
            ("🌍 Everyone", "all")
        ]
        
        for text, value in stakeholder_types:
            rb = tk.Radiobutton(
                type_frame,
                text=text,
                variable=self.stakeholder_var,
                value=value,
                font=("Segoe UI", 11),
                bg="white",
                activebackground="white",
                selectcolor="#1E40AF",
                command=self.update_recipient_count
            )
            rb.pack(anchor="w", pady=8)
        
        # Recipient Count Display
        self.recipient_count_label = tk.Label(
            left_panel,
            text="Recipients: 0",
            font=("Segoe UI", 10, "bold"),
            fg="#4CAF50",
            bg="white"
        )
        self.recipient_count_label.pack(anchor="w", pady=(20, 0))
        
        # Notification Type
        tk.Frame(left_panel, height=20, bg="white").pack()
        
        tk.Label(
            left_panel,
            text="Notification Type:",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#333"
        ).pack(anchor="w", pady=(0, 10))
        
        self.notification_type = tk.StringVar(value="in_app")
        
        type_options = [
            ("📱 In-App Notification", "in_app"),
            ("✉️ Email", "email"),
            ("📞 SMS", "sms"),
            ("🔔 All Channels", "all")
        ]
        
        for text, value in type_options:
            rb = tk.Radiobutton(
                left_panel,
                text=text,
                variable=self.notification_type,
                value=value,
                font=("Segoe UI", 10),
                bg="white",
                activebackground="white",
                selectcolor="#1E40AF"
            )
            rb.pack(anchor="w", pady=5)
        
        # Priority
        tk.Frame(left_panel, height=20, bg="white").pack()
        
        tk.Label(
            left_panel,
            text="Priority:",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#333"
        ).pack(anchor="w", pady=(0, 10))
        
        self.priority_var = tk.StringVar(value="normal")
        
        priority_frame = tk.Frame(left_panel, bg="white")
        priority_frame.pack(fill="x")
        
        tk.Radiobutton(
            priority_frame,
            text="🔵 Normal",
            variable=self.priority_var,
            value="normal",
            font=("Segoe UI", 10),
            bg="white",
            activebackground="white",
            selectcolor="#2196F3"
        ).pack(side="left", padx=(0, 15))
        
        tk.Radiobutton(
            priority_frame,
            text="🟡 Medium",
            variable=self.priority_var,
            value="medium",
            font=("Segoe UI", 10),
            bg="white",
            activebackground="white",
            selectcolor="#FF9800"
        ).pack(side="left", padx=(0, 15))
        
        tk.Radiobutton(
            priority_frame,
            text="🔴 High",
            variable=self.priority_var,
            value="high",
            font=("Segoe UI", 10),
            bg="white",
            activebackground="white",
            selectcolor="#F44336"
        ).pack(side="left")
        
        # Right Panel - Message Composition
        right_panel = ttk.Frame(content_container, style="Card.TFrame", padding=25)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Message Header
        msg_header = tk.Frame(right_panel, bg="white")
        msg_header.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            msg_header,
            text="Compose Message",
            font=("Segoe UI", 16, "bold"),
            fg="#1E40AF",
            bg="white"
        ).pack(side="left")
        
        self.char_count_label = tk.Label(
            msg_header,
            text="0/1000 characters",
            font=("Segoe UI", 9),
            fg="#666",
            bg="white"
        )
        self.char_count_label.pack(side="right")
        
        # Subject Line
        tk.Label(
            right_panel,
            text="Subject:",
            font=("Segoe UI", 11, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        self.subject_entry = tk.Entry(
            right_panel,
            font=("Segoe UI", 11),
            bg="white",
            relief="solid",
            bd=1
        )
        self.subject_entry.pack(fill="x", pady=(0, 20))
        self.subject_entry.insert(0, f"DRMS Notification - {datetime.now().strftime('%Y-%m-%d')}")
        
        # Message Text Area
        tk.Label(
            right_panel,
            text="Message:",
            font=("Segoe UI", 11, "bold"),
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        # Create a frame for the text area with border
        text_frame = tk.Frame(right_panel, bg="#e5e5e5", relief="solid", bd=1)
        text_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        self.message_text = scrolledtext.ScrolledText(
            text_frame,
            font=("Segoe UI", 11),
            bg="white",
            relief="flat",
            wrap="word",
            height=15
        )
        self.message_text.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Add placeholder text
        placeholder = """Enter your notification message here...

Example:
📢 Important Update!
Dear Stakeholders,

This is a notification regarding recent developments in the disaster relief efforts.

Please take necessary actions.

Thank you,
DRMS Team"""
        
        self.message_text.insert("1.0", placeholder)
        
        # Bind character count update
        self.message_text.bind("<KeyRelease>", self.update_char_count)
        
        # Template buttons
        template_frame = tk.Frame(right_panel, bg="white")
        template_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            template_frame,
            text="Quick Templates:",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#666"
        ).pack(side="left", padx=(0, 10))
        
        templates = ["Urgent", "Meeting", "Update", "Help Needed"]
        for template in templates:
            btn = tk.Button(
                template_frame,
                text=template,
                font=("Segoe UI", 9),
                bg="#E5E7EB",
                fg="#333",
                relief="flat",
                padx=10,
                pady=3,
                command=lambda t=template: self.apply_template(t)
            )
            btn.pack(side="left", padx=(0, 5))
        
        # Action Buttons
        button_frame = tk.Frame(right_panel, bg="white")
        button_frame.pack(fill="x")
        
        # Preview Button
        preview_btn = tk.Button(
            button_frame,
            text="👁️ Preview",
            font=("Segoe UI", 11, "bold"),
            bg="#6B7280",
            fg="white",
            activebackground="#4B5563",
            padx=20,
            pady=10,
            command=self.preview_notification,
            cursor="hand2"
        )
        preview_btn.pack(side="left", padx=(0, 10))
        
        # Send Button
        send_btn = tk.Button(
            button_frame,
            text="🚀 Send Notification",
            font=("Segoe UI", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            padx=20,
            pady=10,
            command=self.send_notification,
            cursor="hand2"
        )
        send_btn.pack(side="left")
        
        # ========== STATUS BAR ==========
        status_bar = tk.Frame(self, bg="#333", height=35)
        status_bar.pack(fill="x", side="bottom")
        
        self.status_label = tk.Label(
            status_bar,
            text="Ready to send notifications",
            fg="white",
            bg="#333",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(side="left", padx=20)
        
        # Initial update
        self.update_recipient_count()

    # ========== BACK TO ADMIN FUNCTION ==========
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

    def update_char_count(self, event=None):
        text = self.message_text.get("1.0", "end-1c")
        char_count = len(text)
        max_chars = 1000
        
        if char_count > max_chars:
            self.char_count_label.config(text=f"{char_count}/{max_chars} characters - OVER LIMIT!", fg="#F44336")
        else:
            self.char_count_label.config(text=f"{char_count}/{max_chars} characters", fg="#666")

    def update_recipient_count(self):
        try:
            stakeholder_type = self.stakeholder_var.get()
            
            if stakeholder_type == "all":
                # Count all users
                users = user_service.get_all_users()
            else:
                # Count users by specific role
                users = user_service.get_users_by_role(stakeholder_type)
            
            count = len(users) if users else 0
            self.recipient_count_label.config(text=f"Recipients: {count}")
            
        except Exception as e:
            self.recipient_count_label.config(text=f"Recipients: Error loading")
            print(f"Error counting recipients: {e}")

    def apply_template(self, template_type):
        templates = {
            "Urgent": """🚨 URGENT NOTICE

Attention all stakeholders,

This is an urgent notification requiring immediate attention.

Please respond as soon as possible.

- DRMS Emergency Team""",
            
            "Meeting": """📅 MEETING NOTIFICATION

Dear Team,

A meeting has been scheduled to discuss current relief operations.

Date: [Date]
Time: [Time]
Venue: [Location/Virtual Link]

Please confirm your availability.

Best regards,
DRMS Coordination""",
            
            "Update": """📢 STATUS UPDATE

Hello everyone,

This is an update on our ongoing disaster relief efforts.

Current Status: [Brief Update]
Next Steps: [Action Items]

Thank you for your continued support.

Sincerely,
DRMS Operations""",
            
            "Help Needed": """🆘 ASSISTANCE REQUIRED

Attention Volunteers/NGOs,

We require additional assistance for the following:

Location: [Area]
Needs: [Specific Requirements]
Contact: [Contact Person]

Please respond if you can help.

- DRMS Support Team"""
        }
        
        if template_type in templates:
            self.message_text.delete("1.0", "end")
            self.message_text.insert("1.0", templates[template_type])
            self.update_char_count()

    def preview_notification(self):
        subject = self.subject_entry.get().strip()
        message = self.message_text.get("1.0", "end-1c").strip()
        stakeholder_type = self.stakeholder_var.get()
        notification_type = self.notification_type.get()
        priority = self.priority_var.get()
        
        if not message or message == "Enter your notification message here...":
            messagebox.showwarning("Empty Message", "Please enter a message before previewing.")
            return
        
        # Create preview window
        preview = tk.Toplevel(self)
        preview.title("Notification Preview")
        preview.geometry("600x500")
        preview.configure(bg="#f3f3f3")
        
        # Center preview window
        preview.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (600 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (500 // 2)
        preview.geometry(f"600x500+{x}+{y}")
        
        # Preview content
        preview_frame = tk.Frame(preview, bg="white", relief="solid", bd=1)
        preview_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        tk.Label(
            preview_frame,
            text="📄 NOTIFICATION PREVIEW",
            font=("Segoe UI", 16, "bold"),
            fg="#1E40AF",
            bg="white"
        ).pack(pady=(20, 10))
        
        # Details
        details_frame = tk.Frame(preview_frame, bg="white")
        details_frame.pack(fill="x", padx=20, pady=10)
        
        details = [
            ("Subject:", subject),
            ("To:", stakeholder_type.capitalize() + "s"),
            ("Type:", notification_type.upper()),
            ("Priority:", priority.upper()),
            ("Sender:", self.logged_in_user.get('name', 'System Admin')),
            ("Time:", datetime.now().strftime("%Y-%m-%d %H:%M"))
        ]
        
        for label, value in details:
            frame = tk.Frame(details_frame, bg="white")
            frame.pack(fill="x", pady=2)
            
            tk.Label(
                frame,
                text=label,
                font=("Segoe UI", 10, "bold"),
                fg="#666",
                bg="white",
                width=10,
                anchor="w"
            ).pack(side="left")
            
            tk.Label(
                frame,
                text=value,
                font=("Segoe UI", 10),
                fg="#333",
                bg="white",
                anchor="w"
            ).pack(side="left")
        
        # Message content
        tk.Frame(preview_frame, height=1, bg="#e5e5e5").pack(fill="x", padx=20, pady=10)
        
        message_frame = tk.Frame(preview_frame, bg="white")
        message_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        message_text = scrolledtext.ScrolledText(
            message_frame,
            font=("Segoe UI", 11),
            bg="#f9f9f9",
            wrap="word",
            height=10
        )
        message_text.pack(fill="both", expand=True)
        message_text.insert("1.0", message)
        message_text.config(state="disabled")
        
        # Close button
        tk.Button(
            preview_frame,
            text="Close Preview",
            font=("Segoe UI", 11),
            bg="#6B7280",
            fg="white",
            command=preview.destroy,
            pady=8
        ).pack(pady=20)

    def send_notification(self):
        stakeholder_type = self.stakeholder_var.get()
        subject = self.subject_entry.get().strip()
        message_content = self.message_text.get("1.0", "end-1c").strip()
        
        if not message_content or message_content == "Enter your notification message here...":
            messagebox.showwarning("Empty Message", "Please enter a message before sending.")
            self.status_label.config(text="✗ Please enter a message")
            return
        
        if not subject:
            messagebox.showwarning("Missing Subject", "Please enter a subject for the notification.")
            self.status_label.config(text="✗ Please enter a subject")
            return
        
        try:
            # Get stakeholders
            if stakeholder_type == "all":
                stakeholders = user_service.get_all_users()
            else:
                stakeholders = user_service.get_users_by_role(stakeholder_type)
            
            if not stakeholders:
                messagebox.showinfo("No Stakeholders", f"No {stakeholder_type}s found to notify.")
                self.status_label.config(text=f"✗ No {stakeholder_type}s found")
                return
            
            # Simulate sending notification
            sent_count = 0
            for user in stakeholders:
                user_name = user[1] if isinstance(user, tuple) else user.get('name', 'User')
                user_email = user[2] if isinstance(user, tuple) else user.get('email', '')
                
                # Here you would integrate with actual email/SMS services
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Sent to {user_name} ({user_email}): "
                      f"{subject[:30]}...")
                sent_count += 1
            
            # Success message
            messagebox.showinfo(
                "Success!",
                f"✅ Notification sent to {sent_count} {stakeholder_type}(s) successfully!\n\n"
                f"Subject: {subject}\n"
                f"Message length: {len(message_content)} characters\n"
                f"Sent via: {self.notification_type.get().upper()}"
            )
            
            # Clear and reset
            self.message_text.delete("1.0", "end")
            self.subject_entry.delete(0, "end")
            self.subject_entry.insert(0, f"DRMS Notification - {datetime.now().strftime('%Y-%m-%d')}")
            self.status_label.config(text=f"✓ Sent to {sent_count} recipients successfully")
            
            # Log the notification
            self.log_notification(subject, stakeholder_type, sent_count)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send notification:\n{str(e)}")
            self.status_label.config(text="✗ Error sending notification")

    def log_notification(self, subject, recipient_type, count):
        """Log the notification (in a real app, this would save to database)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Sent '{subject}' to {count} {recipient_type}s\n"
        
        # In a real app, save to database or log file
        print(f"LOG: {log_entry}")

# ---------- TEST ----------
if __name__ == "__main__":
    app = NotifyStakeholdersApp(
        logged_in_user={
            "userID": 1,
            "name": "SYSTEM ADMIN",
            "role": "Admin",
            "email": "admin@drms.gov.pk"
        }
    )
    
    app.mainloop()