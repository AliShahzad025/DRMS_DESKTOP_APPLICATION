import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import sv_ttk
from data.db_connection import DatabaseConnection

class VerifyVolunteerApp(tk.Tk):
    def __init__(self, logged_in_user=None, db_connection=None, back_command=None):
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
        self.back_command = back_command
        
        self.title("DRMS - Verify Volunteers")
        # Set to full screen
        self.state('zoomed')  # Maximized window
        self.configure(bg="#f3f3f3")
        
        # Apply Windows 11 theme
        sv_ttk.set_theme("light")
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", font=("Segoe UI", 10))
        style.map("TButton", background=[("active", "#e5e5e5")])
        
        self.option_add("*Font", ("Segoe UI", 10))
        
        # DB setup
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        self.cursor = self.connection.cursor()

        # Create scrollable UI
        self.create_scrollable_ui()
        self.load_volunteers()

    def create_scrollable_ui(self):
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
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Now create widgets inside the scrollable frame
        self.create_widgets(scrollable_frame)

    def create_widgets(self, parent):
        # ========== HEADER ==========
        header = tk.Frame(parent, bg="#1E40AF", height=100)
        header.pack(fill="x", pady=(0, 20))
        
        header_content = tk.Frame(header, bg="#1E40AF")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # RED BACK BUTTON - SAME STYLE AS OTHER APPS
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

        # Title in header
        title_frame = tk.Frame(header_content, bg="#1E40AF")
        title_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            title_frame,
            text="🤝 VERIFY VOLUNTEERS",
            font=("Segoe UI", 22, "bold"),
            fg="white",
            bg="#1E40AF"
        ).pack(anchor="w")
        
        tk.Label(
            title_frame,
            text="Review and verify volunteer applications",
            font=("Segoe UI", 11),
            fg="#E0E0E0",
            bg="#1E40AF"
        ).pack(anchor="w", pady=(5, 0))
        
        # User info in header
        user_frame = tk.Frame(header_content, bg="#1E40AF")
        user_frame.pack(side="right")
        
        tk.Label(
            user_frame,
            text="👤",
            font=("Segoe UI", 14),
            fg="white",
            bg="#1E40AF"
        ).pack(side="left", padx=(0, 10))
        
        # SAFELY get the name with fallback
        if isinstance(self.logged_in_user, dict):
            user_name = self.logged_in_user.get('name', 'Admin')
        else:
            user_name = 'Admin'
        
        tk.Label(
            user_frame,
            text=user_name,
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#1E40AF",
            justify="right"
        ).pack(side="right")

        # ========== MAIN CONTENT ==========
        main_content = tk.Frame(parent, bg="#f3f3f3", padx=30)
        main_content.pack(fill="both", expand=True, pady=(0, 30))
        
        # Statistics cards
        stats_frame = tk.Frame(main_content, bg="#f3f3f3")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        stats_data = [
            ("Total Volunteers", "👥", "#3B82F6"),
            ("Verified", "✅", "#10B981"),
            ("Pending", "⏳", "#F59E0B")
        ]
        
        self.stat_labels = []
        for i, (title, icon, color) in enumerate(stats_data):
            card = tk.Frame(stats_frame, bg="white", relief="raised", bd=1)
            card.pack(side="left", fill="both", expand=True, padx=(0, 15) if i < len(stats_data)-1 else 0)
            
            tk.Label(
                card,
                text=icon,
                font=("Segoe UI", 20),
                fg=color,
                bg="white"
            ).pack(anchor="w", padx=15, pady=(15, 5))
            
            tk.Label(
                card,
                text=title,
                font=("Segoe UI", 10),
                fg="#6B7280",
                bg="white"
            ).pack(anchor="w", padx=15)
            
            value_label = tk.Label(
                card,
                text="0",
                font=("Segoe UI", 18, "bold"),
                fg=color,
                bg="white"
            )
            value_label.pack(anchor="w", padx=15, pady=(0, 15))
            self.stat_labels.append(value_label)

        # ========== VOLUNTEER LIST SECTION ==========
        list_container = tk.Frame(main_content, bg="white", relief="solid", bd=1)
        list_container.pack(fill="both", expand=True, pady=(0, 20))
        
        # List header
        list_header = tk.Frame(list_container, bg="#f8fafc", height=40)
        list_header.pack(fill="x")
        
        tk.Label(
            list_header,
            text="📋 Volunteer Applications",
            font=("Segoe UI", 12, "bold"),
            fg="#1E40AF",
            bg="#f8fafc"
        ).pack(side="left", padx=15, pady=8)
        
        # Refresh button
        refresh_btn = tk.Button(
            list_header,
            text="🔄 Refresh List",
            font=("Segoe UI", 9),
            bg="#E5E7EB",
            fg="#374151",
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.load_volunteers
        )
        refresh_btn.pack(side="right", padx=15, pady=8)
        
        # Volunteer listbox with scrollbar
        listbox_frame = tk.Frame(list_container, bg="white")
        listbox_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Listbox with scrollbar
        listbox_scrollbar = tk.Scrollbar(listbox_frame)
        listbox_scrollbar.pack(side="right", fill="y")
        
        self.volunteer_listbox = tk.Listbox(
            listbox_frame,
            width=50,
            font=("Segoe UI", 12),
            bg="white",
            relief="flat",
            bd=1,
            selectbackground="#3B82F6",
            selectforeground="white",
            activestyle="none",
            yscrollcommand=listbox_scrollbar.set
        )
        self.volunteer_listbox.pack(side="left", fill="both", expand=True)
        listbox_scrollbar.config(command=self.volunteer_listbox.yview)
        
        # Bind selection event
        self.volunteer_listbox.bind("<<ListboxSelect>>", self.display_volunteer_details)
        
        # ========== VOLUNTEER DETAILS SECTION ==========
        details_container = tk.Frame(main_content, bg="white", relief="solid", bd=1)
        details_container.pack(fill="both", expand=True, pady=(0, 20))
        
        # Details header
        details_header = tk.Frame(details_container, bg="#f8fafc", height=40)
        details_header.pack(fill="x")
        
        tk.Label(
            details_header,
            text="📄 Volunteer Details",
            font=("Segoe UI", 12, "bold"),
            fg="#1E40AF",
            bg="#f8fafc"
        ).pack(side="left", padx=15, pady=8)
        
        # Clear details button
        clear_btn = tk.Button(
            details_header,
            text="🗑️ Clear",
            font=("Segoe UI", 9),
            bg="#E5E7EB",
            fg="#374151",
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=lambda: self.details_text.delete("1.0", tk.END)
        )
        clear_btn.pack(side="right", padx=15, pady=8)
        
        # Volunteer details text area
        self.details_text = scrolledtext.ScrolledText(
            details_container,
            width=70,
            height=10,
            font=("Segoe UI", 11),
            bg="white",
            relief="flat",
            bd=1,
            wrap=tk.WORD
        )
        self.details_text.pack(fill="both", expand=True, padx=10, pady=10)

        # ========== ACTION BUTTONS ==========
        action_frame = tk.Frame(main_content, bg="#f3f3f3")
        action_frame.pack(fill="x", pady=(0, 20))
        
        # Verify button
        verify_btn = tk.Button(
            action_frame,
            text="✅ VERIFY VOLUNTEER",
            font=("Segoe UI", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            relief="raised",
            bd=2,
            padx=30,
            pady=12,
            cursor="hand2",
            command=lambda: self.update_verification(True)
        )
        verify_btn.pack(side="left", padx=(0, 15))
        
        # Hover effect for verify button
        def verify_hover_enter(e):
            verify_btn.config(bg='#45a049', relief="sunken")
        def verify_hover_leave(e):
            verify_btn.config(bg='#4CAF50', relief="raised")
        verify_btn.bind("<Enter>", verify_hover_enter)
        verify_btn.bind("<Leave>", verify_hover_leave)
        
        # Reject button
        reject_btn = tk.Button(
            action_frame,
            text="❌ REJECT VOLUNTEER",
            font=("Segoe UI", 12, "bold"),
            bg="#F44336",
            fg="white",
            activebackground="#d32f2f",
            activeforeground="white",
            relief="raised",
            bd=2,
            padx=30,
            pady=12,
            cursor="hand2",
            command=lambda: self.update_verification(False)
        )
        reject_btn.pack(side="left", padx=(0, 15))
        
        # Hover effect for reject button
        def reject_hover_enter(e):
            reject_btn.config(bg='#d32f2f', relief="sunken")
        def reject_hover_leave(e):
            reject_btn.config(bg='#F44336', relief="raised")
        reject_btn.bind("<Enter>", reject_hover_enter)
        reject_btn.bind("<Leave>", reject_hover_leave)
        
        # Quick Actions button
        quick_btn = tk.Button(
            action_frame,
            text="⚡ QUICK ACTIONS",
            font=("Segoe UI", 11),
            bg="#8B5CF6",
            fg="white",
            activebackground="#7C3AED",
            activeforeground="white",
            relief="raised",
            bd=2,
            padx=25,
            pady=12,
            cursor="hand2",
            command=self.show_quick_actions
        )
        quick_btn.pack(side="left")
        
        # Hover effect for quick actions button
        def quick_hover_enter(e):
            quick_btn.config(bg='#7C3AED', relief="sunken")
        def quick_hover_leave(e):
            quick_btn.config(bg='#8B5CF6', relief="raised")
        quick_btn.bind("<Enter>", quick_hover_enter)
        quick_btn.bind("<Leave>", quick_hover_leave)

        # ========== FOOTER ==========
        footer_frame = tk.Frame(parent, bg="#f3f3f3", pady=20)
        footer_frame.pack(fill="x", side="bottom")
        
        # Status bar
        status_bar = tk.Frame(footer_frame, bg="#333", height=35)
        status_bar.pack(fill="x")
        
        self.status_label = tk.Label(
            status_bar,
            text="Ready to verify volunteers",
            fg="white",
            bg="#333",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(side="left", padx=20)
        
        # Instructions
        info_label = tk.Label(
            status_bar,
            text="ℹ️ Select a volunteer from the list to view details",
            fg="#E5E7EB",
            bg="#333",
            font=("Segoe UI", 9, "italic")
        )
        info_label.pack(side="right", padx=20)

    def load_volunteers(self):
        """Load volunteers from database"""
        self.volunteer_listbox.delete(0, tk.END)
        self.details_text.delete("1.0", tk.END)
        
        try:
            self.cursor.execute("SELECT volunteerID, roles, verified, status, last_active FROM Volunteer")
            self.volunteers = self.cursor.fetchall()
            
            verified_count = 0
            pending_count = 0
            
            for vol in self.volunteers:
                vol_id, roles, verified, status, last_active = vol
                status_text = "✅ Verified" if verified else "⏳ Pending"
                display_text = f"ID: {vol_id} | Role: {roles[:20]}... | Status: {status_text}"
                self.volunteer_listbox.insert(tk.END, display_text)
                
                if verified:
                    verified_count += 1
                else:
                    pending_count += 1
            
            total_count = len(self.volunteers)
            
            # Update statistics
            if hasattr(self, 'stat_labels') and len(self.stat_labels) >= 3:
                self.stat_labels[0].config(text=str(total_count))
                self.stat_labels[1].config(text=str(verified_count))
                self.stat_labels[2].config(text=str(pending_count))
            
            self.status_label.config(text=f"✅ Loaded {total_count} volunteers")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load volunteers: {str(e)}")
            self.status_label.config(text="❌ Failed to load volunteers")

    def display_volunteer_details(self, event):
        """Show selected volunteer's details"""
        selection = self.volunteer_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        volunteer = self.volunteers[index]
        vol_id, roles, verified, status, last_active = volunteer
        
        # Format the details nicely
        details = f"""
╔══════════════════════════════════════════════════════════════╗
║                    VOLUNTEER DETAILS                         ║
╠══════════════════════════════════════════════════════════════╣
║  🆔 Volunteer ID: {vol_id:<45} ║
║  👤 Roles: {roles:<48} ║
║  ✅ Verified: {'Yes' if verified else 'No':<48} ║
║  📊 Status: {status:<48} ║
║  ⏰ Last Active: {str(last_active):<45} ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, details)
        
        # Color the text based on verification status
        self.details_text.tag_configure("verified", foreground="#10B981")
        self.details_text.tag_configure("pending", foreground="#F59E0B")
        
        # Apply tags
        start_idx = self.details_text.search("Verified:", "1.0", stopindex=tk.END)
        if start_idx:
            line_start = self.details_text.index(f"{start_idx} linestart")
            line_end = self.details_text.index(f"{start_idx} lineend")
            if verified:
                self.details_text.tag_add("verified", line_start, line_end)
            else:
                self.details_text.tag_add("pending", line_start, line_end)

    def update_verification(self, verify=True):
        """Mark volunteer as verified or rejected"""
        selection = self.volunteer_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a volunteer first.")
            self.status_label.config(text="⚠ Please select a volunteer first")
            return
        
        index = selection[0]
        volunteer = self.volunteers[index]
        vol_id = volunteer[0]
        
        action = "verify" if verify else "reject"
        if not messagebox.askyesno("Confirm Action", f"Are you sure you want to {action} Volunteer ID {vol_id}?"):
            return

        try:
            self.cursor.execute("UPDATE Volunteer SET verified=%s WHERE volunteerID=%s", (verify, vol_id))
            self.connection.commit()
            
            status_text = "verified" if verify else "rejected"
            messagebox.showinfo("Success", f"✅ Volunteer ID {vol_id} has been {status_text}.")
            self.status_label.config(text=f"✅ Volunteer ID {vol_id} {status_text}")
            
            self.load_volunteers()
            self.details_text.delete("1.0", tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update volunteer: {str(e)}")
            self.status_label.config(text="❌ Failed to update volunteer")

    def show_quick_actions(self):
        """Show quick action menu"""
        quick_menu = tk.Menu(self, tearoff=0)
        quick_menu.add_command(label="✅ Verify All Pending", command=self.verify_all_pending)
        quick_menu.add_command(label="🔄 Reload All Data", command=self.load_volunteers)
        quick_menu.add_separator()
        quick_menu.add_command(label="📊 Show Statistics", command=self.show_statistics)
        
        # Get button position
        try:
            btn = self.nametowidget(self.focus_get())
            x = btn.winfo_rootx()
            y = btn.winfo_rooty() + btn.winfo_height()
            quick_menu.tk_popup(x, y)
        except:
            quick_menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())

    def verify_all_pending(self):
        """Verify all pending volunteers"""
        if not messagebox.askyesno("Verify All", "Are you sure you want to verify ALL pending volunteers?"):
            return
        
        try:
            self.cursor.execute("UPDATE Volunteer SET verified = TRUE WHERE verified = FALSE")
            self.connection.commit()
            
            updated = self.cursor.rowcount
            messagebox.showinfo("Success", f"✅ Verified {updated} pending volunteers!")
            self.status_label.config(text=f"✅ Verified {updated} pending volunteers")
            
            self.load_volunteers()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to verify all: {str(e)}")
            self.status_label.config(text="❌ Failed to verify all")

    def show_statistics(self):
        """Show detailed statistics"""
        try:
            self.cursor.execute("SELECT COUNT(*) as total, SUM(verified) as verified FROM Volunteer")
            stats = self.cursor.fetchone()
            
            total = stats[0] or 0
            verified = stats[1] or 0
            pending = total - verified
            
            messagebox.showinfo(
                "Volunteer Statistics",
                f"📊 Detailed Statistics:\n\n"
                f"Total Volunteers: {total}\n"
                f"Verified: {verified}\n"
                f"Pending: {pending}\n"
                f"Verification Rate: {verified/total*100:.1f}%" if total > 0 else "Verification Rate: 0%"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get statistics: {str(e)}")

    def go_back_to_admin(self):
        """Go back to AdminOptionsApp - SAME AS OTHER APPS"""
        if messagebox.askyesno("Confirm", "Return to Admin Dashboard?"):
            try:
                # First try the custom back command if provided
                if self.back_command:
                    self.back_command()
                    return
                
                # Ensure we have valid user data
                if not self.logged_in_user or not isinstance(self.logged_in_user, dict):
                    user_data = {
                        "userID": 1,
                        "name": "Admin User",
                        "role": "Admin",
                        "email": "admin@drms.com"
                    }
                else:
                    user_data = self.logged_in_user.copy()
                
                # Ensure required keys exist with safe fallbacks
                if 'userID' not in user_data:
                    user_data['userID'] = 1
                if 'name' not in user_data:
                    user_data['name'] = "Admin User"
                if 'role' not in user_data:
                    user_data['role'] = "Admin"
                if 'email' not in user_data:
                    user_data['email'] = "admin@drms.com"
                
                # Destroy current window first
                self.destroy()
                
                # Try to import and launch AdminOptionsApp
                try:
                    from frontend.login import AdminOptionsApp
                    
                    # Create admin app with user info
                    admin_app = AdminOptionsApp(
                        logged_in_user=user_data,
                        db_connection=self.connection
                    )
                    
                    # Start mainloop
                    admin_app.mainloop()
                    
                except ImportError:
                    # If AdminOptionsApp not found, show error and quit
                    messagebox.showerror(
                        "Error", 
                        "Cannot return to Admin Dashboard.\nAdminOptionsApp module not found."
                    )
                    self.quit()
                    
            except Exception as e:
                # Log the error for debugging
                print(f"Error in go_back_to_admin: {e}")
                # Simple fallback - just destroy the window
                self.destroy()


# ------------------ TESTING -------------------
if __name__ == "__main__":
    # Test with back command
    def go_back_to_admin():
        print("Returning to Admin Dashboard...")
        app.destroy()
    
    # Test with None user (should work with default)
    app = VerifyVolunteerApp(
        logged_in_user=None,  # This will trigger the default user creation
        back_command=go_back_to_admin
    )
    
    # Or test with proper user data
    # app = VerifyVolunteerApp(
    #     logged_in_user={
    #         "userID": 1,
    #         "name": "Admin User",
    #         "role": "Admin",
    #         "email": "admin@drms.com"
    #     },
    #     back_command=go_back_to_admin
    # )
    
    app.mainloop()