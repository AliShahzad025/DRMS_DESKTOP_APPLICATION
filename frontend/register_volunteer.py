import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import sv_ttk
from data.db_connection import DatabaseConnection

class RegisterVolunteerApp(tk.Tk):
    def __init__(self, logged_in_user=None, db_connection=None, back_command=None):
        super().__init__()
        self.logged_in_user = logged_in_user or {}
        self.back_command = back_command
        
        self.title("DRMS - Register Volunteer")
        self.geometry("1000x800")  # Larger window for better layout
        self.resizable(True, True)
        
        # Apply Windows 11 theme
        sv_ttk.set_theme("light")
        self.style = ttk.Style()
        self.configure(bg="#f5f8fa")
        
        # DB connection
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        self.cursor = self.connection.cursor(dictionary=True)
        
        # Create scrollable UI
        self.create_scrollable_ui()

    def create_scrollable_ui(self):
        # ========== MAIN CONTAINER WITH SCROLLBAR ==========
        main_container = tk.Frame(self, bg="#f5f8fa")
        main_container.pack(fill="both", expand=True)
        
        # Create canvas with scrollbar
        canvas = tk.Canvas(main_container, bg="#f5f8fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f5f8fa")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Now create widgets inside the scrollable frame
        self.create_widgets(scrollable_frame)

    def create_widgets(self, parent):
        # ========== HEADER WITH BACK BUTTON ==========
        header = tk.Frame(parent, bg="#2E7D32", height=100)  # Green for NGO
        header.pack(fill="x", pady=(0, 20))
        
        header_content = tk.Frame(header, bg="#2E7D32")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # RED BACK BUTTON
        back_btn = tk.Button(
            header_content,
            text="◄ BACK TO NGO DASHBOARD",
            font=("Segoe UI", 12, "bold"),
            bg="#FF4444",
            fg="white",
            activebackground="#FF2222",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.go_back_to_ngo_dashboard
        )
        back_btn.pack(side="left", padx=(0, 30))
        
        # Hover effects for back button
        def on_enter(e):
            back_btn.config(bg='#FF2222')
        def on_leave(e):
            back_btn.config(bg='#FF4444')
        back_btn.bind("<Enter>", on_enter)
        back_btn.bind("<Leave>", on_leave)

        # Title in header
        title_frame = tk.Frame(header_content, bg="#2E7D32")
        title_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            title_frame,
            text="👤 REGISTER NEW VOLUNTEER",
            font=("Segoe UI", 24, "bold"),
            fg="white",
            bg="#2E7D32"
        ).pack(anchor="w")
        
        tk.Label(
            title_frame,
            text="Add new volunteers to your disaster response team",
            font=("Segoe UI", 12),
            fg="#E8F5E9",
            bg="#2E7D32"
        ).pack(anchor="w", pady=(5, 0))
        
        # ========== MAIN FORM CARD ==========
        form_card = tk.Frame(parent, bg="white", relief="solid", bd=1, padx=40, pady=40)
        form_card.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # Form title
        tk.Label(
            form_card,
            text="📝 Volunteer Registration Form",
            font=("Segoe UI", 20, "bold"),
            fg="#1E40AF",
            bg="white"
        ).pack(anchor="w", pady=(0, 30))
        
        # Create two columns for form fields
        columns_frame = tk.Frame(form_card, bg="white")
        columns_frame.pack(fill="both", expand=True)
        
        left_column = tk.Frame(columns_frame, bg="white")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        right_column = tk.Frame(columns_frame, bg="white")
        right_column.pack(side="right", fill="both", expand=True, padx=(20, 0))
        
        # LEFT COLUMN FIELDS
        # Name
        tk.Label(
            left_column,
            text="👤 Full Name *",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        self.name_entry = ttk.Entry(
            left_column,
            font=("Segoe UI", 11),
            width=35
        )
        self.name_entry.pack(fill="x", pady=(0, 20))
        
        # Email
        tk.Label(
            left_column,
            text="📧 Email Address *",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        self.email_entry = ttk.Entry(
            left_column,
            font=("Segoe UI", 11),
            width=35
        )
        self.email_entry.pack(fill="x", pady=(0, 20))
        
        # Phone
        tk.Label(
            left_column,
            text="📱 Phone Number *",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        self.phone_entry = ttk.Entry(
            left_column,
            font=("Segoe UI", 11),
            width=35
        )
        self.phone_entry.pack(fill="x", pady=(0, 20))
        
        # Location
        tk.Label(
            left_column,
            text="📍 Location *",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        self.location_entry = ttk.Entry(
            left_column,
            font=("Segoe UI", 11),
            width=35
        )
        self.location_entry.pack(fill="x", pady=(0, 20))
        
        # RIGHT COLUMN FIELDS
        # Latitude
        tk.Label(
            right_column,
            text="🌐 Latitude (optional)",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        self.lat_entry = ttk.Entry(
            right_column,
            font=("Segoe UI", 11),
            width=35
        )
        self.lat_entry.pack(fill="x", pady=(0, 20))
        
        # Longitude
        tk.Label(
            right_column,
            text="🌐 Longitude (optional)",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        self.lng_entry = ttk.Entry(
            right_column,
            font=("Segoe UI", 11),
            width=35
        )
        self.lng_entry.pack(fill="x", pady=(0, 20))
        
        # Roles / Skills
        tk.Label(
            right_column,
            text="🛠️ Skills / Roles (optional)",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        self.roles_entry = ttk.Entry(
            right_column,
            font=("Segoe UI", 11),
            width=35
        )
        self.roles_entry.pack(fill="x", pady=(0, 20))
        
        # Status
        tk.Label(
            right_column,
            text="📊 Status",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        self.status_var = tk.StringVar(value="available")
        status_combo = ttk.Combobox(
            right_column,
            textvariable=self.status_var,
            values=["available", "busy"],
            state="readonly",
            font=("Segoe UI", 11),
            width=33
        )
        status_combo.pack(fill="x", pady=(0, 20))
        
        # Password
        tk.Label(
            right_column,
            text="🔒 Password *",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        self.password_entry = ttk.Entry(
            right_column,
            font=("Segoe UI", 11),
            show="•",
            width=35
        )
        self.password_entry.pack(fill="x", pady=(0, 30))
        
        # ========== FORM CONTROLS ==========
        controls_frame = tk.Frame(form_card, bg="white")
        controls_frame.pack(fill="x", pady=(20, 0))
        
        # Clear Button
        clear_btn = tk.Button(
            controls_frame,
            text="🗑️ Clear Form",
            font=("Segoe UI", 12),
            bg="#6B7280",
            fg="white",
            activebackground="#4B5563",
            activeforeground="white",
            relief="flat",
            padx=25,
            pady=12,
            cursor="hand2",
            command=self.clear_form
        )
        clear_btn.pack(side="left", padx=(0, 20))
        
        # Submit Button
        submit_btn = tk.Button(
            controls_frame,
            text="🚀 REGISTER VOLUNTEER",
            font=("Segoe UI", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=40,
            pady=15,
            cursor="hand2",
            command=self.register_volunteer
        )
        submit_btn.pack(side="left")
        
        # ========== INFO PANEL ==========
        info_card = tk.Frame(parent, bg="#E3F2FD", relief="solid", bd=1, padx=25, pady=20)
        info_card.pack(fill="x", padx=30, pady=(0, 30))
        
        tk.Label(
            info_card,
            text="ℹ️ IMPORTANT INFORMATION",
            font=("Segoe UI", 14, "bold"),
            fg="#0D47A1",
            bg="#E3F2FD"
        ).pack(anchor="w", pady=(0, 10))
        
        info_text = """
        1. All fields marked with * are required.
        2. Volunteers will be automatically verified and marked as "available".
        3. Latitude and Longitude are optional but helpful for geo-location.
        4. Volunteers can update their skills and status later.
        5. The volunteer will receive login credentials via email (demo).
        6. Ensure phone number is in international format (+1234567890).
        """
        
        tk.Label(
            info_card,
            text=info_text,
            font=("Segoe UI", 10),
            fg="#374151",
            bg="#E3F2FD",
            justify="left"
        ).pack(anchor="w")
        
        # ========== FOOTER ==========
        footer_frame = tk.Frame(parent, bg="#333", height=40)
        footer_frame.pack(fill="x", side="bottom")
        
        # Status label
        self.status_label = tk.Label(
            footer_frame,
            text="✅ Ready to register new volunteer",
            fg="white",
            bg="#333",
            font=("Segoe UI", 10)
        )
        self.status_label.pack(side="left", padx=20)
        
        # NGO info
        ngo_info = tk.Label(
            footer_frame,
            text=f"🏢 NGO: {self.logged_in_user.get('name', 'Unknown Organization')} | Database: Connected",
            fg="#E5E7EB",
            bg="#333",
            font=("Segoe UI", 9)
        )
        ngo_info.pack(side="right", padx=20)

    def clear_form(self):
        """Clear all form fields"""
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)
        self.lat_entry.delete(0, tk.END)
        self.lng_entry.delete(0, tk.END)
        self.roles_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.status_var.set("available")
        
        self.status_label.config(text="✅ Form cleared. Ready for new entry")
        self.name_entry.focus_set()

    def register_volunteer(self):
        """Register a new volunteer"""
        # Get form data
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        location = self.location_entry.get().strip()
        lat = self.lat_entry.get().strip() or None
        lng = self.lng_entry.get().strip() or None
        roles = self.roles_entry.get().strip() or ""
        status = self.status_var.get()
        password = self.password_entry.get().strip()
        verified = True  # Auto-verified when registered by NGO

        # Validation
        if not (name and email and phone and location and password):
            messagebox.showwarning("Missing Fields", "Please fill all required fields marked with *")
            self.status_label.config(text="❌ Missing required fields")
            return
        
        if "@" not in email or "." not in email:
            messagebox.showwarning("Invalid Email", "Please enter a valid email address")
            self.status_label.config(text="❌ Invalid email format")
            return
        
        if len(password) < 6:
            messagebox.showwarning("Weak Password", "Password must be at least 6 characters")
            self.status_label.config(text="❌ Password too short")
            return

        # Confirmation dialog
        confirm = messagebox.askyesno("Confirm Registration",
                                     f"Register new volunteer?\n\n"
                                     f"Name: {name}\n"
                                     f"Email: {email}\n"
                                     f"Phone: {phone}\n"
                                     f"Location: {location}\n"
                                     f"Status: {status.title()}\n\n"
                                     f"Volunteer will be auto-verified.")
        
        if not confirm:
            self.status_label.config(text="❌ Registration cancelled")
            return

        try:
            self.status_label.config(text="⏳ Registering volunteer...")
            self.update()
            
            # Insert into UserAccount
            insert_user = """
            INSERT INTO UserAccount (name, email, phone, location, latitude, longitude, role, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s, 'Volunteer', %s)
            """
            self.cursor.execute(insert_user, (name, email, phone, location, lat, lng, password))
            self.connection.commit()
            volunteer_id = self.cursor.lastrowid

            # Insert into Volunteer
            insert_volunteer = """
            INSERT INTO Volunteer (volunteerID, roles, verified, status, last_active)
            VALUES (%s, %s, %s, %s, %s)
            """
            last_active = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(insert_volunteer, (volunteer_id, roles, verified, status, last_active))
            self.connection.commit()

            # Success message
            messagebox.showinfo(
                "✅ Registration Successful", 
                f"Volunteer '{name}' has been registered!\n\n"
                f"Volunteer ID: {volunteer_id}\n"
                f"Email: {email}\n"
                f"Status: {status.title()}\n"
                f"Verified: Yes\n\n"
                f"The volunteer can now log in to the system."
            )
            
            self.status_label.config(text=f"✅ Volunteer '{name}' registered successfully")
            
            # Clear form after successful registration
            self.clear_form()
            
            # Optionally go back to dashboard
            go_back = messagebox.askyesno("Continue", "Volunteer registered successfully!\n\nReturn to NGO Dashboard?")
            if go_back:
                self.go_back_to_ngo_dashboard()
            
        except Exception as e:
            self.connection.rollback()
            error_msg = str(e)
            
            # Check for duplicate email
            if "Duplicate entry" in error_msg and "email" in error_msg:
                error_msg = "This email is already registered. Please use a different email."
            elif "Duplicate entry" in error_msg:
                error_msg = "Duplicate entry detected. Please check the information."
            
            messagebox.showerror("Registration Failed", f"Failed to register volunteer.\n\nError: {error_msg}")
            self.status_label.config(text="❌ Registration failed")

    def go_back_to_ngo_dashboard(self):
        """Go back to NGODashboardApp"""
        if messagebox.askyesno("Confirm", "Return to NGO Dashboard?\n\nAny unsaved changes will be lost."):
            try:
                # First try the custom back command if provided
                if self.back_command:
                    self.back_command()
                    return
                
                # Ensure we have valid user data
                if not self.logged_in_user or not isinstance(self.logged_in_user, dict):
                    user_data = {
                        "userID": 2,
                        "name": "NGO Organization",
                        "role": "NGO",
                        "email": "ngo@drms.com"
                    }
                else:
                    user_data = self.logged_in_user.copy()
                
                # Ensure required keys exist with safe fallbacks
                if 'userID' not in user_data and 'id' not in user_data:
                    user_data['userID'] = 2
                if 'name' not in user_data:
                    user_data['name'] = "NGO User"
                if 'role' not in user_data:
                    user_data['role'] = "NGO"
                if 'email' not in user_data:
                    user_data['email'] = "ngo@drms.com"
                
                # Destroy current window first
                self.destroy()
                
                # Try to import and launch NGODashboardApp
                try:
                    from frontend.login import NGODashboardApp
                    
                    # Create NGO app with user info
                    ngo_app = NGODashboardApp(
                        logged_in_user=user_data,
                        db_connection=self.connection
                    )
                    
                    # Start mainloop
                    ngo_app.mainloop()
                    
                except ImportError:
                    # If NGODashboardApp not found, show error and quit
                    messagebox.showerror(
                        "Error", 
                        "Cannot return to NGO Dashboard.\nNGODashboardApp module not found."
                    )
                    self.quit()
                    
            except Exception as e:
                # Log the error for debugging
                print(f"Error in go_back_to_ngo_dashboard: {e}")
                # Simple fallback - just destroy the window
                self.destroy()


# ------------------ TEST -------------------
if __name__ == "__main__":
    # Test with sample NGO user
    app = RegisterVolunteerApp(
        logged_in_user={
            "userID": 2,
            "name": "Bob's Relief",
            "role": "NGO",
            "email": "bob.ngo@org.net"
        }
    )
    
    app.mainloop()