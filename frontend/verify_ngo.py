import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
from data.db_connection import DatabaseConnection

class VerifyNGOApp(tk.Tk):
    def __init__(self, db_connection=None, logged_in_user=None, back_command=None):
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
        
        self.title("DRMS - Verify NGOs")
        self.geometry("1000x700")  # Increased height for better view
        self.configure(bg="#f3f3f3")
        
        # Apply Windows 11 theme
        sv_ttk.set_theme("light")
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", font=("Segoe UI", 10))
        style.map("TButton", background=[("active", "#e5e5e5")])
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#f0f0f0")
        
        self.option_add("*Font", ("Segoe UI", 10))
        
        # DB setup
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        self.cursor = self.connection.cursor(dictionary=True)

        # UI
        self.create_scrollable_ui()
        self.load_ngos()
        
        # Center window
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    # ----------------------- SCROLLABLE UI -----------------------------
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
        
        # RED BACK BUTTON - MATCHING register_ngo.py STYLE
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
        
        # Hover effects - SAME AS register_ngo.py
        def on_enter(e):
            back_btn.config(bg='#FF2222')
        def on_leave(e):
            back_btn.config(bg='#FF4444')
        back_btn.bind("<Enter>", on_enter)
        back_btn.bind("<Leave>", on_leave)

        # Title in header - ADJUSTED TO MATCH STYLE
        title_frame = tk.Frame(header_content, bg="#1E40AF")
        title_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            title_frame,
            text="🏢 VERIFY NGOS",
            font=("Segoe UI", 22, "bold"),
            fg="white",
            bg="#1E40AF"
        ).pack(anchor="w")
        
        tk.Label(
            title_frame,
            text="Verify and manage NGO organizations",
            font=("Segoe UI", 11),
            fg="#E0E0E0",
            bg="#1E40AF"
        ).pack(anchor="w", pady=(5, 0))
        
        # User info in header - MATCHING STYLE
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
            ("Total NGOs", "📊", "#3B82F6"),
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

        # NGO Table Container
        table_container = tk.Frame(main_content, bg="white", relief="solid", bd=1)
        table_container.pack(fill="both", expand=True, pady=(0, 20))
        
        # Table Header
        table_header = tk.Frame(table_container, bg="#f8fafc", height=40)
        table_header.pack(fill="x")
        
        tk.Label(
            table_header,
            text="📋 NGO List",
            font=("Segoe UI", 12, "bold"),
            fg="#1E40AF",
            bg="#f8fafc"
        ).pack(side="left", padx=15, pady=8)
        
        # Refresh button
        refresh_btn = tk.Button(
            table_header,
            text="🔄 Refresh",
            font=("Segoe UI", 9),
            bg="#E5E7EB",
            fg="#374151",
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.load_ngos
        )
        refresh_btn.pack(side="right", padx=15, pady=8)
        
        # NGO Table with its own scrollbars
        columns = ("ngoID", "orgName", "verified", "region")
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=15  # Increased height for better visibility
        )
        
        # Configure table scrollbars
        tree_y_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        tree_x_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_y_scrollbar.set, xscrollcommand=tree_x_scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        tree_y_scrollbar.pack(side="right", fill="y")
        tree_x_scrollbar.pack(side="bottom", fill="x")
        
        for col in columns:
            self.tree.heading(col, text=col.title().replace("Id", "ID"))
            self.tree.column(col, width=150, anchor="center" if col == "verified" else "w")

        # Action Buttons Container
        action_container = tk.Frame(main_content, bg="#f3f3f3")
        action_container.pack(fill="x", pady=(0, 20))
        
        # View Details button
        view_btn = tk.Button(
            action_container,
            text="👁️ View NGO Details",
            font=("Segoe UI", 11, "bold"),
            bg="#3B82F6",
            fg="white",
            activebackground="#2563EB",
            activeforeground="white",
            relief="raised",
            bd=2,
            padx=25,
            pady=12,
            cursor="hand2",
            command=self.open_details_window
        )
        view_btn.pack(side="left", padx=(0, 15))
        
        # Add hover effect
        def view_hover_enter(e):
            view_btn.config(bg='#2563EB', relief="sunken")
        def view_hover_leave(e):
            view_btn.config(bg='#3B82F6', relief="raised")
        view_btn.bind("<Enter>", view_hover_enter)
        view_btn.bind("<Leave>", view_hover_leave)
        
        # Quick Actions button
        quick_actions_btn = tk.Button(
            action_container,
            text="⚡ Quick Actions",
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
            command=self.quick_actions
        )
        quick_actions_btn.pack(side="left", padx=(0, 15))
        
        def quick_hover_enter(e):
            quick_actions_btn.config(bg='#7C3AED', relief="sunken")
        def quick_hover_leave(e):
            quick_actions_btn.config(bg='#8B5CF6', relief="raised")
        quick_actions_btn.bind("<Enter>", quick_hover_enter)
        quick_actions_btn.bind("<Leave>", quick_hover_leave)
        
        # Export Data button
        export_btn = tk.Button(
            action_container,
            text="📤 Export Data",
            font=("Segoe UI", 11),
            bg="#10B981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="raised",
            bd=2,
            padx=25,
            pady=12,
            cursor="hand2",
            command=self.export_data
        )
        export_btn.pack(side="left")
        
        def export_hover_enter(e):
            export_btn.config(bg='#059669', relief="sunken")
        def export_hover_leave(e):
            export_btn.config(bg='#10B981', relief="raised")
        export_btn.bind("<Enter>", export_hover_enter)
        export_btn.bind("<Leave>", export_hover_leave)

        # ========== FOOTER SECTION ==========
        footer_frame = tk.Frame(parent, bg="#f3f3f3", pady=20)
        footer_frame.pack(fill="x", side="bottom")
        
        # Status bar
        status_bar = tk.Frame(footer_frame, bg="#333", height=35)
        status_bar.pack(fill="x")
        
        self.status_label = tk.Label(
            status_bar,
            text="Ready to verify NGOs",
            fg="white",
            bg="#333",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(side="left", padx=20)
        
        # Additional info in footer
        info_label = tk.Label(
            status_bar,
            text="ℹ️ Double-click on an NGO row to view details",
            fg="#E5E7EB",
            bg="#333",
            font=("Segoe UI", 9, "italic")
        )
        info_label.pack(side="right", padx=20)
        
        # Bind double-click to treeview
        self.tree.bind("<Double-1>", lambda e: self.open_details_window())

    # ------------------ Load NGO List -----------------------
    def load_ngos(self):
        self.tree.delete(*self.tree.get_children())

        self.cursor.execute("""
            SELECT ngoID, orgName, verified, region 
            FROM NGO
        """)
        ngos = self.cursor.fetchall()

        verified_count = 0
        pending_count = 0
        
        for ngo in ngos:
            verified_text = "✅ Yes" if ngo["verified"] else "❌ No"
            if ngo["verified"]:
                verified_count += 1
            else:
                pending_count += 1
                
            self.tree.insert("", tk.END, values=(
                ngo["ngoID"],
                ngo["orgName"],
                verified_text,
                ngo["region"]
            ))
        
        # Update statistics
        total_count = len(ngos)
        if hasattr(self, 'stat_labels') and len(self.stat_labels) >= 3:
            self.stat_labels[0].config(text=str(total_count))
            self.stat_labels[1].config(text=str(verified_count))
            self.stat_labels[2].config(text=str(pending_count))
        
        self.status_label.config(text=f"✅ Loaded {total_count} NGOs")

    # ---------------- NGO Detailed Window -------------------
    def open_details_window(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an NGO first.")
            self.status_label.config(text="⚠ Please select an NGO first")
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
            self.status_label.config(text="❌ NGO details not found")
            return

        details_window = tk.Toplevel(self)
        details_window.title("NGO Details")
        details_window.geometry("500x500")
        details_window.configure(bg="#f3f3f3")
        
        # Center details window
        details_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (500 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (500 // 2)
        details_window.geometry(f"500x500+{x}+{y}")

        # Header
        header = tk.Frame(details_window, bg="#1E40AF", height=60)
        header.pack(fill="x")
        
        tk.Label(
            header,
            text="📄 NGO Details",
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#1E40AF"
        ).pack(pady=15)

        # Content
        content_frame = tk.Frame(details_window, bg="white", padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)

        info = (
            f"🏢 NGO Name: {ngo['orgName']}\n\n"
            f"✅ Verified: {'Yes' if ngo['verified'] else 'No'}\n\n"
            f"🌍 Region: {ngo['region']}\n\n"
            f"👤 Contact Person: {ngo['contact_person']}\n\n"
            f"📄 Registration Document:\n  {ngo['registration_doc']}"
        )

        tk.Label(
            content_frame,
            text=info,
            justify="left",
            bg="white",
            font=("Segoe UI", 11),
            fg="#333"
        ).pack(anchor="w", pady=10)

        # Button container
        btn_container = tk.Frame(content_frame, bg="white")
        btn_container.pack(fill="x", pady=20)

        # Approve button
        approve_btn = tk.Button(
            btn_container,
            text="✅ Approve",
            bg="#10B981",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            width=15,
            padx=10,
            pady=8,
            cursor="hand2",
            command=lambda: self.verify_ngo(ngo["ngoID"], True, details_window)
        )
        approve_btn.pack(pady=5)
        
        # Hover effect for approve
        def approve_hover_enter(e):
            approve_btn.config(bg='#059669', relief="sunken")
        def approve_hover_leave(e):
            approve_btn.config(bg='#10B981', relief="raised")
        approve_btn.bind("<Enter>", approve_hover_enter)
        approve_btn.bind("<Leave>", approve_hover_leave)

        # Reject button
        reject_btn = tk.Button(
            btn_container,
            text="❌ Reject",
            bg="#EF4444",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            width=15,
            padx=10,
            pady=8,
            cursor="hand2",
            command=lambda: self.verify_ngo(ngo["ngoID"], False, details_window)
        )
        reject_btn.pack(pady=5)
        
        # Hover effect for reject
        def reject_hover_enter(e):
            reject_btn.config(bg='#DC2626', relief="sunken")
        def reject_hover_leave(e):
            reject_btn.config(bg='#EF4444', relief="raised")
        reject_btn.bind("<Enter>", reject_hover_enter)
        reject_btn.bind("<Leave>", reject_hover_leave)

        # Close button
        close_btn = tk.Button(
            btn_container,
            text="Close",
            bg="#6B7280",
            fg="white",
            font=("Segoe UI", 11),
            width=12,
            padx=10,
            pady=6,
            cursor="hand2",
            command=details_window.destroy
        )
        close_btn.pack(pady=10)
        
        # Hover effect for close
        def close_hover_enter(e):
            close_btn.config(bg='#4B5563', relief="sunken")
        def close_hover_leave(e):
            close_btn.config(bg='#6B7280', relief="raised")
        close_btn.bind("<Enter>", close_hover_enter)
        close_btn.bind("<Leave>", close_hover_leave)

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
                self.status_label.config(text="✅ NGO verified successfully")
            else:
                messagebox.showwarning("Rejected", "NGO Verification Failed.")
                self.status_label.config(text="⚠ NGO verification rejected")

            window.destroy()
            self.load_ngos()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            self.status_label.config(text="❌ Error updating NGO")

    # ---------------------- Quick Actions --------------------
    def quick_actions(self):
        """Show quick action menu"""
        quick_menu = tk.Menu(self, tearoff=0)
        quick_menu.add_command(label="✅ Verify All Pending", command=self.verify_all_pending)
        quick_menu.add_command(label="🔄 Reload Data", command=self.load_ngos)
        quick_menu.add_separator()
        quick_menu.add_command(label="📊 Show Statistics", command=self.show_statistics)
        
        # Get button position
        btn = self.nametowidget(self.focus_get())
        if btn:
            x = btn.winfo_rootx()
            y = btn.winfo_rooty() + btn.winfo_height()
            quick_menu.tk_popup(x, y)
        else:
            quick_menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())

    def verify_all_pending(self):
        """Verify all pending NGOs"""
        if messagebox.askyesno("Verify All", "Are you sure you want to verify ALL pending NGOs?"):
            try:
                self.cursor.execute("""
                    UPDATE NGO SET verified = TRUE WHERE verified = FALSE
                """)
                self.connection.commit()
                self.load_ngos()
                messagebox.showinfo("Success", "All pending NGOs have been verified!")
                self.status_label.config(text="✅ All pending NGOs verified")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to verify all: {str(e)}")

    def show_statistics(self):
        """Show detailed statistics"""
        self.cursor.execute("SELECT COUNT(*) as total, SUM(verified) as verified FROM NGO")
        stats = self.cursor.fetchone()
        
        total = stats['total'] or 0
        verified = stats['verified'] or 0
        pending = total - verified
        
        messagebox.showinfo(
            "NGO Statistics",
            f"📊 Detailed Statistics:\n\n"
            f"Total NGOs: {total}\n"
            f"Verified: {verified}\n"
            f"Pending: {pending}\n"
            f"Verification Rate: {verified/total*100:.1f}%" if total > 0 else "Verification Rate: 0%"
        )

    # ---------------------- Export Data ----------------------
    def export_data(self):
        """Export NGO data to file"""
        try:
            self.cursor.execute("""
                SELECT ngoID, orgName, verified, region, contact_person 
                FROM NGO
            """)
            ngos = self.cursor.fetchall()
            
            if not ngos:
                messagebox.showwarning("No Data", "No NGO data to export.")
                return
            
            # Simple export (in real app, you'd save to CSV or Excel)
            export_text = "NGO ID,Organization Name,Verified,Region,Contact Person\n"
            for ngo in ngos:
                export_text += f"{ngo['ngoID']},{ngo['orgName']},{'Yes' if ngo['verified'] else 'No'},{ngo['region']},{ngo['contact_person']}\n"
            
            # Show export preview
            preview_window = tk.Toplevel(self)
            preview_window.title("Export Preview")
            preview_window.geometry("600x400")
            
            tk.Label(
                preview_window,
                text="📤 Export Preview (Copy this data)",
                font=("Segoe UI", 14, "bold"),
                fg="#1E40AF"
            ).pack(pady=10)
            
            text_widget = tk.Text(preview_window, wrap="none", height=15, width=70)
            text_widget.pack(fill="both", expand=True, padx=20, pady=10)
            text_widget.insert("1.0", export_text)
            text_widget.config(state="disabled")
            
            messagebox.showinfo(
                "Export Ready",
                "Data is ready for export.\n\n"
                
                "1. Save to CSV file\n"
                "2. Generate Excel report\n"
                "3. Or export to database"
            )
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")

    # ---------------------- Back to Admin -----------------------------
    def go_back_to_admin(self):
        """Go back to AdminOptionsApp - MATCHING register_ngo.py FUNCTION"""
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
    app = VerifyNGOApp(
        logged_in_user=None,  # This will trigger the default user creation
        back_command=go_back_to_admin
    )
    
    # Or test with proper user data
    # app = VerifyNGOApp(
    #     logged_in_user={
    #         "userID": 1,
    #         "name": "Admin User",
    #         "role": "Admin",
    #         "email": "admin@drms.com"
    #     },
    #     back_command=go_back_to_admin
    # )
    
    app.mainloop()