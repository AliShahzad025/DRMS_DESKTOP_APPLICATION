import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
from data.db_connection import DatabaseConnection

class TrackRequestApp(tk.Tk):
    def __init__(self, logged_in_user=None, db_connection=None, back_command=None):
        super().__init__()
        self.logged_in_user = logged_in_user or {}
        self.back_command = back_command
        self.selected_request_id = None
        
        self.title("DRMS - Track & Manage Requests")
        self.geometry("1200x850")  # Slightly taller for update panel
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
        self.load_requests()

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
        header = tk.Frame(parent, bg="#F59E0B", height=100)
        header.pack(fill="x", pady=(0, 20))
        
        header_content = tk.Frame(header, bg="#F59E0B")
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
        title_frame = tk.Frame(header_content, bg="#F59E0B")
        title_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            title_frame,
            text="📍 TRACK & MANAGE REQUESTS",
            font=("Segoe UI", 24, "bold"),
            fg="white",
            bg="#F59E0B"
        ).pack(anchor="w")
        
        # Subtitle
        user_role = self.logged_in_user.get("role", "")
        subtitle = "Monitor and update all emergency requests" if user_role == "NGO" else "Track your emergency requests"
        
        tk.Label(
            title_frame,
            text=subtitle,
            font=("Segoe UI", 12),
            fg="#FEF3C7",
            bg="#F59E0B"
        ).pack(anchor="w", pady=(5, 0))
        
        # User info
        if user_role:
            user_info = tk.Frame(header_content, bg="#F59E0B")
            user_info.pack(side="right")
            
            role_icon = "🏢" if user_role == "NGO" else "😢" if user_role == "Victim" else "👤"
            tk.Label(
                user_info,
                text=f"{role_icon} {self.logged_in_user.get('name', 'User')}",
                font=("Segoe UI", 11, "bold"),
                fg="white",
                bg="#F59E0B",
                justify="right"
            ).pack(side="right")
        
        # ========== STATISTICS CARDS ==========
        stats_frame = tk.Frame(parent, bg="#f5f8fa", padx=30)
        stats_frame.pack(fill="x", pady=(0, 25))
        
        stats_data = [
            ("Total Requests", "📋", "#3B82F6", "0"),
            ("Pending", "⏳", "#F59E0B", "0"),
            ("In Progress", "🔄", "#8B5CF6", "0"),
            ("Completed", "✅", "#10B981", "0"),
            ("Critical", "🚨", "#EF4444", "0"),
        ]
        
        self.stat_labels = []
        for i, (title, icon, color, default_value) in enumerate(stats_data):
            card = tk.Frame(stats_frame, bg="white", relief="solid", bd=1)
            card.grid(row=0, column=i, padx=(0, 15) if i < len(stats_data)-1 else 0, sticky="nsew")
            stats_frame.columnconfigure(i, weight=1)
            
            # Icon and title
            icon_frame = tk.Frame(card, bg="white")
            icon_frame.pack(fill="x", padx=15, pady=(15, 5))
            
            tk.Label(
                icon_frame,
                text=icon,
                font=("Segoe UI", 20),
                fg=color,
                bg="white"
            ).pack(side="left", padx=(0, 10))
            
            tk.Label(
                icon_frame,
                text=title,
                font=("Segoe UI", 10),
                fg="#6B7280",
                bg="white"
            ).pack(side="left")
            
            # Value
            value_label = tk.Label(
                card,
                text=default_value,
                font=("Segoe UI", 18, "bold"),
                fg=color,
                bg="white"
            )
            value_label.pack(pady=(0, 15))
            self.stat_labels.append(value_label)
        
        # ========== UPDATE STATUS PANEL (ALWAYS VISIBLE) ==========
        self.update_panel = tk.Frame(parent, bg="#E3F2FD", relief="solid", bd=1, padx=25, pady=20)
        self.update_panel.pack(fill="x", padx=30, pady=(0, 20))
        
        # Initially hidden
        self.update_panel.pack_forget()
        
        # Panel header
        panel_header = tk.Frame(self.update_panel, bg="#E3F2FD")
        panel_header.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            panel_header,
            text="✏️ UPDATE REQUEST STATUS",
            font=("Segoe UI", 14, "bold"),
            fg="#0D47A1",
            bg="#E3F2FD"
        ).pack(side="left")
        
        # Close button for panel
        close_btn = tk.Button(
            panel_header,
            text="✕ Close",
            font=("Segoe UI", 10),
            bg="#6B7280",
            fg="white",
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.hide_update_panel
        )
        close_btn.pack(side="right")
        
        # Request info
        self.request_info_label = tk.Label(
            self.update_panel,
            text="Selected Request: None",
            font=("Segoe UI", 11),
            fg="#374151",
            bg="#E3F2FD",
            justify="left"
        )
        self.request_info_label.pack(anchor="w", pady=(0, 15))
        
        # Status selection
        selection_frame = tk.Frame(self.update_panel, bg="#E3F2FD")
        selection_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            selection_frame,
            text="Select new status:",
            font=("Segoe UI", 11, "bold"),
            fg="#374151",
            bg="#E3F2FD"
        ).pack(side="left", padx=(0, 20))
        
        # Status options with icons
        self.status_var = tk.StringVar()
        status_options = [
            ("⏳ Pending", "pending"),
            ("👤 Assigned", "assigned"),
            ("🔄 In Process", "in_process"),
            ("✅ Completed", "completed")
        ]
        
        for text, value in status_options:
            rb = tk.Radiobutton(
                selection_frame,
                text=text,
                variable=self.status_var,
                value=value,
                font=("Segoe UI", 11),
                bg="#E3F2FD",
                activebackground="#E3F2FD",
                selectcolor="#3B82F6"
            )
            rb.pack(side="left", padx=(0, 15))
        
        # Update button
        update_btn = tk.Button(
            self.update_panel,
            text="🚀 UPDATE STATUS",
            font=("Segoe UI", 12, "bold"),
            bg="#10B981",
            fg="white",
            activebackground="#0D9488",
            activeforeground="white",
            relief="raised",
            bd=2,
            padx=25,
            pady=10,
            cursor="hand2",
            command=self.update_status
        )
        update_btn.pack()
        
        # ========== MAIN CONTENT AREA ==========
        content_card = tk.Frame(parent, bg="white", relief="solid", bd=1, padx=25, pady=25)
        content_card.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        # Header with controls
        content_header = tk.Frame(content_card, bg="white")
        content_header.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            content_header,
            text="📋 SOS REQUEST INVENTORY",
            font=("Segoe UI", 18, "bold"),
            fg="#1E40AF",
            bg="white"
        ).pack(side="left")
        
        controls_frame = tk.Frame(content_header, bg="white")
        controls_frame.pack(side="right")
        
        # Refresh button
        refresh_btn = tk.Button(
            controls_frame,
            text="🔄 Refresh",
            font=("Segoe UI", 10),
            bg="#3B82F6",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.load_requests
        )
        refresh_btn.pack(side="left", padx=(0, 10))
        
        # Filter button
        filter_btn = tk.Button(
            controls_frame,
            text="🔍 Filter",
            font=("Segoe UI", 10),
            bg="#6B7280",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.filter_requests
        )
        filter_btn.pack(side="left", padx=(0, 10))
        
        # ========== TREEVIEW FOR REQUESTS ==========
        tree_frame = tk.Frame(content_card, bg="white")
        tree_frame.pack(fill="both", expand=True)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side="right", fill="y")
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")
        
        # Treeview
        columns = ("requestID", "victim", "location", "typeOfNeed", "urgencyLevel", "status", "assignedVolunteer", "assignedNGO")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=15,
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        
        # Configure scrollbars
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Configure columns with better widths
        column_configs = {
            "requestID": ("ID", 80, "center"),
            "victim": ("Victim", 150, "w"),
            "location": ("Location", 150, "w"),
            "typeOfNeed": ("Need Type", 150, "w"),
            "urgencyLevel": ("Urgency", 100, "center"),
            "status": ("Status", 120, "center"),
            "assignedVolunteer": ("Volunteer", 150, "w"),
            "assignedNGO": ("NGO", 150, "w")
        }
        
        for col in columns:
            heading, width, anchor = column_configs[col]
            self.tree.heading(col, text=heading, anchor="center")
            self.tree.column(col, width=width, anchor=anchor, minwidth=width)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_request_select)
        # Bind double-click to show update panel
        self.tree.bind("<Double-1>", lambda e: self.show_update_panel())
        
        # ========== FOOTER ==========
        footer_frame = tk.Frame(parent, bg="#333", height=40)
        footer_frame.pack(fill="x", side="bottom")
        
        # Status label
        self.status_label = tk.Label(
            footer_frame,
            text="✅ Ready | Select a request to manage | Double-click to update",
            fg="white",
            bg="#333",
            font=("Segoe UI", 10)
        )
        self.status_label.pack(side="left", padx=20)
        
        # Database info
        db_info = tk.Label(
            footer_frame,
            text=f"🏢 NGO: {self.logged_in_user.get('name', 'Unknown Organization')} | Database: Connected",
            fg="#E5E7EB",
            bg="#333",
            font=("Segoe UI", 9)
        )
        db_info.pack(side="right", padx=20)

    def show_update_panel(self):
        """Show the update panel with selected request info"""
        if not self.selected_request_id:
            messagebox.showwarning("No Selection", "Please select a request first.")
            return
        
        # Show the panel
        self.update_panel.pack(fill="x", padx=30, pady=(0, 20), before=self.tree.master.master)
        
        # Set current status as default selection
        selected_item = self.tree.focus()
        if selected_item:
            row = self.tree.item(selected_item)["values"]
            if row:
                current_status = row[5].split(" ", 1)[1] if " " in row[5] else row[5]
                self.status_var.set(current_status)
                
                # Update request info label
                self.request_info_label.config(
                    text=f"Selected Request: ID {row[0]} | Victim: {row[1]} | Location: {row[2]} | Need: {row[3]} | Current Status: {row[5]}"
                )
        
        self.status_label.config(text="✏️ Update panel opened. Select new status and click 'Update Status'")

    def hide_update_panel(self):
        """Hide the update panel"""
        self.update_panel.pack_forget()
        self.status_label.config(text="✅ Update panel closed")

    def load_requests(self):
        """Load requests from DB into the treeview and update statistics"""
        try:
            self.status_label.config(text="⏳ Loading requests...")
            self.update()
            
            # Hide update panel while refreshing
            self.hide_update_panel()
            
            # Build query based on user role
            if self.logged_in_user and self.logged_in_user.get("role") == "Victim":
                query = """
                SELECT R.requestID, U.name as victim, R.location, R.typeOfNeed, R.urgencyLevel, R.status,
                       V.name as assignedVolunteer, N.orgName as assignedNGO
                FROM SOSRequest R
                JOIN UserAccount U ON R.victimID = U.userID
                LEFT JOIN UserAccount V ON R.assignedVolunteerID = V.userID
                LEFT JOIN NGO N ON R.assignedNGO = N.ngoID
                WHERE R.victimID=%s
                ORDER BY 
                    CASE R.urgencyLevel
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                        ELSE 5
                    END,
                    R.requestID DESC
                """
                self.cursor.execute(query, (self.logged_in_user.get("id"),))
            else:
                query = """
                SELECT R.requestID, U.name as victim, R.location, R.typeOfNeed, R.urgencyLevel, R.status,
                       V.name as assignedVolunteer, N.orgName as assignedNGO
                FROM SOSRequest R
                JOIN UserAccount U ON R.victimID = U.userID
                LEFT JOIN UserAccount V ON R.assignedVolunteerID = V.userID
                LEFT JOIN NGO N ON R.assignedNGO = N.ngoID
                ORDER BY 
                    CASE R.urgencyLevel
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                        ELSE 5
                    END,
                    R.requestID DESC
                """
                self.cursor.execute(query)

            results = self.cursor.fetchall()
            self.tree.delete(*self.tree.get_children())
            
            # Update statistics
            total = len(results)
            pending = sum(1 for r in results if r["status"] == "pending")
            in_progress = sum(1 for r in results if r["status"] in ["assigned", "in_process"])
            completed = sum(1 for r in results if r["status"] == "completed")
            critical = sum(1 for r in results if r["urgencyLevel"] == "critical")
            
            stats = [total, pending, in_progress, completed, critical]
            for i, value in enumerate(stats):
                if i < len(self.stat_labels):
                    self.stat_labels[i].config(text=str(value))
            
            # Insert data into treeview with colors
            for row in results:
                # Format status with icon
                status_icons = {
                    "pending": "⏳",
                    "assigned": "👤",
                    "in_process": "🔄",
                    "completed": "✅"
                }
                status_icon = status_icons.get(row["status"], "❓")
                status_display = f"{status_icon} {row['status'].title()}"
                
                # Format urgency with icon
                urgency_icons = {
                    "critical": "🚨",
                    "high": "⚠️",
                    "medium": "📊",
                    "low": "📉"
                }
                urgency_icon = urgency_icons.get(row["urgencyLevel"], "📝")
                urgency_display = f"{urgency_icon} {row['urgencyLevel'].title()}"
                
                self.tree.insert("", tk.END, values=(
                    row["requestID"],
                    row["victim"],
                    row["location"],
                    row["typeOfNeed"],
                    urgency_display,
                    status_display,
                    row["assignedVolunteer"] or "Not Assigned",
                    row["assignedNGO"] or "Not Assigned"
                ))
            
            self.status_label.config(text=f"✅ Loaded {len(results)} requests")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load requests.\n{str(e)}")
            self.status_label.config(text="❌ Failed to load requests")

    def on_request_select(self, event):
        """Handle request selection"""
        selected_item = self.tree.focus()
        if selected_item:
            row = self.tree.item(selected_item)["values"]
            if row:
                self.selected_request_id = row[0]
                
                self.status_label.config(text=f"✅ Selected Request ID: {row[0]} | Double-click to update or click 'Update Status' in panel")

    def update_status(self):
        """Update the status of the selected request"""
        if not self.selected_request_id:
            messagebox.showwarning("No Selection", "Please select a request first.")
            return
        
        new_status = self.status_var.get()
        if not new_status:
            messagebox.showwarning("No Status", "Please select a new status.")
            return
        
        # Confirmation
        confirm = messagebox.askyesno(
            "Confirm Update",
            f"Update Request ID {self.selected_request_id} to '{new_status}'?"
        )
        
        if not confirm:
            return
        
        try:
            self.cursor.execute(
                "UPDATE SOSRequest SET status=%s WHERE requestID=%s", 
                (new_status, self.selected_request_id)
            )
            self.connection.commit()
            
            # Success message
            messagebox.showinfo(
                "✅ Success", 
                f"Request ID {self.selected_request_id} status updated to '{new_status}'."
            )
            
            # Refresh the data
            self.load_requests()
            
            # Hide the update panel
            self.hide_update_panel()
            
            self.status_label.config(text=f"✅ Status updated for Request {self.selected_request_id}")
            
        except Exception as e:
            self.connection.rollback()
            messagebox.showerror("Database Error", f"Failed to update status.\n{str(e)}")
            self.status_label.config(text="❌ Failed to update status")

    def filter_requests(self):
        """Filter requests dialog"""
        # Simple inline filter - you can enhance this
        filter_dialog = tk.Toplevel(self)
        filter_dialog.title("Filter Requests")
        filter_dialog.geometry("400x300")
        filter_dialog.configure(bg="#f5f8fa")
        
        tk.Label(
            filter_dialog,
            text="🔍 Filter Requests",
            font=("Segoe UI", 16, "bold"),
            fg="#1E40AF",
            bg="#f5f8fa"
        ).pack(pady=20)
        
        # Simple filter by status
        tk.Label(filter_dialog, text="Show requests with status:", font=("Segoe UI", 11), bg="#f5f8fa").pack(pady=10)
        
        filter_var = tk.StringVar(value="all")
        
        status_frame = tk.Frame(filter_dialog, bg="#f5f8fa")
        status_frame.pack(pady=10)
        
        statuses = ["All", "Pending", "Assigned", "In Process", "Completed"]
        for status in statuses:
            tk.Radiobutton(
                status_frame,
                text=status,
                variable=filter_var,
                value=status.lower(),
                bg="#f5f8fa",
                font=("Segoe UI", 10)
            ).pack(anchor="w", padx=20)
        
        def apply_filter():
            # This is a demo - in real implementation, you would filter the treeview
            messagebox.showinfo("Filter Applied", f"Showing {filter_var.get()} requests")
            filter_dialog.destroy()
        
        tk.Button(
            filter_dialog,
            text="Apply Filter",
            font=("Segoe UI", 11, "bold"),
            bg="#3B82F6",
            fg="white",
            relief="flat",
            padx=30,
            pady=10,
            command=apply_filter
        ).pack(pady=20)

    def go_back_to_ngo_dashboard(self):
        """Go back to NGODashboardApp"""
        if messagebox.askyesno("Confirm", "Return to NGO Dashboard?"):
            try:
                if self.back_command:
                    self.back_command()
                    return
                
                if not self.logged_in_user or not isinstance(self.logged_in_user, dict):
                    user_data = {
                        "userID": 2,
                        "name": "NGO Organization",
                        "role": "NGO",
                        "email": "ngo@drms.com"
                    }
                else:
                    user_data = self.logged_in_user.copy()
                
                if 'userID' not in user_data and 'id' not in user_data:
                    user_data['userID'] = 2
                if 'name' not in user_data:
                    user_data['name'] = "NGO User"
                if 'role' not in user_data:
                    user_data['role'] = "NGO"
                if 'email' not in user_data:
                    user_data['email'] = "ngo@drms.com"
                
                self.destroy()
                
                try:
                    from frontend.login import NGODashboardApp
                    ngo_app = NGODashboardApp(
                        logged_in_user=user_data,
                        db_connection=self.connection
                    )
                    ngo_app.mainloop()
                    
                except ImportError:
                    messagebox.showerror(
                        "Error", 
                        "Cannot return to NGO Dashboard.\nNGODashboardApp module not found."
                    )
                    self.quit()
                    
            except Exception as e:
                print(f"Error in go_back_to_ngo_dashboard: {e}")
                self.destroy()


# ------------------ TEST -------------------
if __name__ == "__main__":
    app = TrackRequestApp(
        logged_in_user={
            "userID": 2,
            "name": "Bob's Relief",
            "role": "NGO",
            "email": "bob.ngo@org.net"
        }
    )
    
    app.mainloop()