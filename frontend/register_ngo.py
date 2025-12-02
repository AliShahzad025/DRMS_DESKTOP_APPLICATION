# File: register_ngo.py

import tkinter as tk
from tkinter import messagebox, ttk
import sv_ttk
from data.db_connection import DatabaseConnection
import sys
import os

# Add parent folder to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ---------- Windows 11 Theme ----------
def apply_windows11_theme(window):
    sv_ttk.set_theme("light")
    style = ttk.Style()
    style.configure("TButton", padding=10, relief="flat", font=("Segoe UI", 11))
    style.map("TButton", background=[("active", "#e5e5e5")])
    style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#333")
    style.configure("Card.TFrame", background="#ffffff", relief="flat")
    style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"), foreground="#1E40AF")
    style.configure("Subtitle.TLabel", font=("Segoe UI", 11), foreground="#666")
    window.option_add("*Font", ("Segoe UI", 11))
    window.configure(bg="#f3f3f3")

class RegisterNGOApp(tk.Tk):
    def __init__(self, db_connection=None, logged_in_user=None):
        super().__init__()
        
        # Fix NoneType error by providing default values
        if logged_in_user is None:
            logged_in_user = {
                "userID": 1,
                "name": "Admin User",
                "role": "Admin",
                "email": "admin@drms.com"
            }
        self.logged_in_user = logged_in_user
        
        # Apply Windows 11 theme
        apply_windows11_theme(self)
        
        self.title("DRMS - Register NGO")
        self.geometry("600x800")  # Increased size
        self.resizable(True, True)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (800 // 2)
        self.geometry(f"+{x}+{y}")
        
        # DB setup
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        self.cursor = self.connection.cursor(dictionary=True)
        
        self.create_widgets()
        self.create_status_bar()

    def create_widgets(self):
        # ========== MAIN CONTAINER WITH SCROLLBAR ==========
        main_container = tk.Frame(self, bg="#f3f3f3")
        main_container.pack(fill="both", expand=True)
        
        # Create canvas with scrollbar
        canvas = tk.Canvas(main_container, bg="#f3f3f3", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f3f3f3")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # ========== HEADER ==========
        header = tk.Frame(scrollable_frame, bg="#1E40AF", height=100)
        header.pack(fill="x", pady=(0, 20))
        
        header_content = tk.Frame(header, bg="#1E40AF")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # BACK BUTTON
        back_btn = tk.Button(
            header_content,
            text="◄ BACK TO ADMIN",
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
            text="🏢 REGISTER NGO",
            font=("Segoe UI", 22, "bold"),
            fg="white",
            bg="#1E40AF"
        ).pack(anchor="w")
        
        tk.Label(
            title_frame,
            text="Register a new NGO organization",
            font=("Segoe UI", 11),
            fg="#E0E0E0",
            bg="#1E40AF"
        ).pack(anchor="w", pady=(5, 0))
        
        # User info
        user_frame = tk.Frame(header_content, bg="#1E40AF")
        user_frame.pack(side="right")
        
        tk.Label(
            user_frame,
            text="👤",
            font=("Segoe UI", 14),
            fg="white",
            bg="#1E40AF"
        ).pack(side="left", padx=(0, 10))
        
        tk.Label(
            user_frame,
            text=f"{self.logged_in_user.get('name', 'Admin')}",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#1E40AF",
            justify="right"
        ).pack(side="right")
        
        # ========== FORM CARD ==========
        card = ttk.Frame(scrollable_frame, style="Card.TFrame", padding=30)
        card.pack(fill="x", pady=(0, 20))
        
        # Card title
        tk.Label(
            card,
            text="NGO Registration Form",
            font=("Segoe UI", 18, "bold"),
            fg="#1E40AF",
            bg="white"
        ).pack(anchor="w", pady=(0, 25))
        
        # Form fields
        form_frame = tk.Frame(card, bg="white")
        form_frame.pack(fill="both", expand=True)
        
        # NGO Name
        tk.Label(
            form_frame,
            text="NGO Name:",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        self.name_entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 12),
            bg="white",
            relief="solid",
            bd=1
        )
        self.name_entry.pack(fill="x", pady=(0, 20))
        
        # Region
        tk.Label(
            form_frame,
            text="Region/Area:",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        self.region_entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 12),
            bg="white",
            relief="solid",
            bd=1
        )
        self.region_entry.pack(fill="x", pady=(0, 20))
        
        # Contact Person
        tk.Label(
            form_frame,
            text="Contact Person:",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        self.contact_entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 12),
            bg="white",
            relief="solid",
            bd=1
        )
        self.contact_entry.pack(fill="x", pady=(0, 20))
        
        # Email
        tk.Label(
            form_frame,
            text="Email Address:",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        self.email_entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 12),
            bg="white",
            relief="solid",
            bd=1
        )
        self.email_entry.pack(fill="x", pady=(0, 20))
        
        # Phone
        tk.Label(
            form_frame,
            text="Phone Number:",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        self.phone_entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 12),
            bg="white",
            relief="solid",
            bd=1
        )
        self.phone_entry.pack(fill="x", pady=(0, 20))
        
        # Password
        tk.Label(
            form_frame,
            text="Password:",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        self.password_entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 12),
            show="*",
            bg="white",
            relief="solid",
            bd=1
        )
        self.password_entry.pack(fill="x", pady=(0, 30))
        
        # Button container
        button_container = tk.Frame(form_frame, bg="white")
        button_container.pack(fill="x", pady=(0, 10))
        
        # Left side: Clear button
        clear_btn = tk.Button(
            button_container,
            text="🗑️ Clear Form",
            font=("Segoe UI", 11, "bold"),
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
        clear_btn.pack(side="left", padx=(0, 10))
        
        # Right side: Register button
        register_btn = tk.Button(
            button_container,
            text="🚀 REGISTER NGO",
            font=("Segoe UI", 13, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            relief="flat",
            padx=30,
            pady=14,
            cursor="hand2",
            command=self.register_ngo
        )
        register_btn.pack(side="right")
        
        # Quick register button below
        quick_register_frame = tk.Frame(form_frame, bg="white")
        quick_register_frame.pack(fill="x", pady=(20, 0))
        
        quick_btn = tk.Button(
            quick_register_frame,
            text="📝 FILL WITH SAMPLE DATA",
            font=("Segoe UI", 11),
            bg="#3B82F6",
            fg="white",
            activebackground="#2563EB",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.fill_sample_data
        )
        quick_btn.pack(fill="x")
        
        # Focus on first field
        self.after(100, lambda: self.name_entry.focus_set())

    def create_status_bar(self):
        """Creates a status bar at the bottom"""
        status_bar = tk.Frame(self, bg="#333", height=35)
        status_bar.pack(fill="x", side="bottom")
        
        self.status_label = tk.Label(
            status_bar,
            text="Ready to register new NGO",
            fg="white",
            bg="#333",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(side="left", padx=20)

    def fill_sample_data(self):
        """Fill form with sample data for testing"""
        if messagebox.askyesno("Sample Data", "Fill form with sample data?"):
            self.clear_form()
            
            sample_data = {
                "name": "Helping Hands Foundation",
                "region": "North Region",
                "contact": "John Doe",
                "email": "contact@helpinghands.org",
                "phone": "+1234567890",
                "password": "password123"
            }
            
            self.name_entry.insert(0, sample_data["name"])
            self.region_entry.insert(0, sample_data["region"])
            self.contact_entry.insert(0, sample_data["contact"])
            self.email_entry.insert(0, sample_data["email"])
            self.phone_entry.insert(0, sample_data["phone"])
            self.password_entry.insert(0, sample_data["password"])
            
            self.status_label.config(text="✓ Form filled with sample data")

    def go_back_to_admin(self):
        """Go back to AdminOptionsApp - FIXED"""
        if messagebox.askyesno("Confirm", "Return to Admin Dashboard?"):
            try:
                # Destroy current window first
                self.destroy()
                
                # Now import and launch AdminOptionsApp
                from frontend.login import AdminOptionsApp
                
                # Create admin app with proper user info
                admin_app = AdminOptionsApp(
                    logged_in_user=self.logged_in_user,
                    db_connection=self.connection
                )
                
                # Start mainloop
                admin_app.mainloop()
                
            except ImportError as e:
                print(f"Import Error: {e}")
                messagebox.showerror("Error", "Cannot return to Admin Dashboard.")
                self.quit()
            except Exception as e:
                print(f"Error: {e}")
                messagebox.showerror("Error", f"Failed to return to Admin Dashboard: {e}")
                self.quit()

    def clear_form(self):
        """Clear all form fields"""
        self.name_entry.delete(0, tk.END)
        self.region_entry.delete(0, tk.END)
        self.contact_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.status_label.config(text="Form cleared")
        self.name_entry.focus_set()

    def register_ngo(self):
        name = self.name_entry.get().strip()
        region = self.region_entry.get().strip()
        contact = self.contact_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        password = self.password_entry.get().strip()

        if not all([name, region, contact, email, phone, password]):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            self.status_label.config(text="✗ Please fill all fields")
            return

        self.status_label.config(text="⏳ Registering NGO...")
        self.update()

        try:
            # Insert into UserAccount first
            insert_user = """
                INSERT INTO UserAccount (name, email, phone, location, role, password_hash)
                VALUES (%s, %s, %s, %s, 'NGO', %s)
            """
            self.cursor.execute(insert_user, (name, email, phone, region, password))
            self.connection.commit()
            user_id = self.cursor.lastrowid

            # Insert into NGO table
            insert_ngo = """
                INSERT INTO NGO (ngoID, orgName, verified, registration_doc, region, contact_person)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(insert_ngo, (user_id, name, False, None, region, contact))
            self.connection.commit()

            messagebox.showinfo("Success", f"✅ NGO '{name}' registered successfully!")
            self.status_label.config(text=f"✓ NGO '{name}' registered successfully")
            
            # Clear form after successful registration
            self.clear_form()
            
            # Ask if user wants to register another NGO
            if messagebox.askyesno("Continue", "Do you want to register another NGO?"):
                self.name_entry.focus_set()
            else:
                self.go_back_to_admin()

        except Exception as e:
            self.connection.rollback()
            messagebox.showerror("Database Error", f"Failed to register NGO.\n\n{str(e)}")
            self.status_label.config(text="✗ Error registering NGO")

# ---------- TEST ----------
if __name__ == "__main__":
    app = RegisterNGOApp(
        logged_in_user={
            "userID": 1,
            "name": "Admin User",
            "role": "Admin",
            "email": "admin@drms.com"
        }
    )
    app.mainloop()