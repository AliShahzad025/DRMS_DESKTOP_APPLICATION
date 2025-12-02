import sys
import os
import tkinter as tk
from tkinter import messagebox, ttk
import sv_ttk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data.db_connection import DatabaseConnection

class PrioritizeRequestsApp(tk.Tk):
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
        
        self.title("DRMS - Prioritize SOS Requests")
        # Set to full screen
        self.state('zoomed')  # Maximized window
        self.configure(bg="#f3f3f3")
        
        # Apply Windows 11 theme
        sv_ttk.set_theme("light")
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", font=("Segoe UI", 10))
        style.map("TButton", background=[("active", "#e5e5e5")])
        style.configure("Treeview", rowheight=35, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#f0f0f0")
        
        self.option_add("*Font", ("Segoe UI", 10))
        
        # Use passed DB connection or create new
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        self.cursor = self.connection.cursor()

        # Create scrollable UI
        self.create_scrollable_ui()
        self.load_requests()

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
            text="🚨 PRIORITIZE SOS REQUESTS",
            font=("Segoe UI", 22, "bold"),
            fg="white",
            bg="#1E40AF"
        ).pack(anchor="w")
        
        tk.Label(
            title_frame,
            text="Manage and prioritize emergency requests",
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
            ("Total Requests", "📋", "#3B82F6"),
            ("Critical", "🚨", "#EF4444"),
            ("High Priority", "⚠️", "#F59E0B"),
            ("Medium", "📊", "#3B82F6"),
            ("Low", "📉", "#10B981")
        ]
        
        self.stat_labels = []
        for i, (title, icon, color) in enumerate(stats_data):
            card = tk.Frame(stats_frame, bg="white", relief="raised", bd=1)
            card.pack(side="left", fill="both", expand=True, padx=(0, 15) if i < len(stats_data)-1 else 0)
            
            tk.Label(
                card,
                text=icon,
                font=("Segoe UI", 18),
                fg=color,
                bg="white"
            ).pack(anchor="w", padx=15, pady=(12, 5))
            
            tk.Label(
                card,
                text=title,
                font=("Segoe UI", 9),
                fg="#6B7280",
                bg="white"
            ).pack(anchor="w", padx=15)
            
            value_label = tk.Label(
                card,
                text="0",
                font=("Segoe UI", 16, "bold"),
                fg=color,
                bg="white"
            )
            value_label.pack(anchor="w", padx=15, pady=(0, 12))
            self.stat_labels.append(value_label)

        # ========== REQUESTS TABLE ==========
        table_container = tk.Frame(main_content, bg="white", relief="solid", bd=1)
        table_container.pack(fill="both", expand=True, pady=(0, 20))
        
        # Table header
        table_header = tk.Frame(table_container, bg="#f8fafc", height=40)
        table_header.pack(fill="x")
        
        tk.Label(
            table_header,
            text="📋 Pending SOS Requests",
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
            command=self.load_requests
        )
        refresh_btn.pack(side="right", padx=15, pady=8)
        
        # Create Treeview with scrollbars
        columns = ("requestID", "victimName", "location", "description", "urgencyLevel")
        column_names = ["Request ID", "Victim Name", "Location", "Message", "Current Urgency"]
        
        # Frame for tree and scrollbars
        tree_frame = tk.Frame(table_container, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Vertical scrollbar
        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side="right", fill="y")
        
        # Horizontal scrollbar
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")
        
        # Create Treeview
        self.table = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=15,
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        
        # Configure scrollbars
        y_scrollbar.config(command=self.table.yview)
        x_scrollbar.config(command=self.table.xview)
        
        self.table.pack(side="left", fill="both", expand=True)
        
        # Configure columns
        for col, heading in zip(columns, column_names):
            self.table.heading(col, text=heading, anchor="w")
            if col == "requestID":
                self.table.column(col, width=100, anchor="center")
            elif col == "victimName":
                self.table.column(col, width=150, anchor="w")
            elif col == "location":
                self.table.column(col, width=150, anchor="w")
            elif col == "description":
                self.table.column(col, width=300, anchor="w")
            elif col == "urgencyLevel":
                self.table.column(col, width=120, anchor="center")
        
        # Bind selection event
        self.table.bind("<<TreeviewSelect>>", self.on_row_select)
        
        # ========== PRIORITY CONTROLS ==========
        controls_frame = tk.Frame(main_content, bg="white", relief="solid", bd=1, padx=20, pady=20)
        controls_frame.pack(fill="x", pady=(0, 20))
        
        # Left side: Selected request info
        left_frame = tk.Frame(controls_frame, bg="white")
        left_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            left_frame,
            text="📌 Selected Request:",
            font=("Segoe UI", 11, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        self.selected_label = tk.Label(
            left_frame,
            text="No request selected",
            font=("Segoe UI", 10),
            fg="#6B7280",
            bg="white",
            justify="left"
        )
        self.selected_label.pack(anchor="w")
        
        # Right side: Priority controls
        right_frame = tk.Frame(controls_frame, bg="white")
        right_frame.pack(side="right")
        
        tk.Label(
            right_frame,
            text="Set Priority Level:",
            font=("Segoe UI", 11, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 8))
        
        # Priority combobox with modern style
        priority_frame = tk.Frame(right_frame, bg="white")
        priority_frame.pack(fill="x")
        
        self.priority_var = tk.StringVar()
        self.priority_box = ttk.Combobox(
            priority_frame,
            textvariable=self.priority_var,
            values=["critical", "high", "medium", "low"],
            state="readonly",
            width=20,
            font=("Segoe UI", 10)
        )
        self.priority_box.pack(side="left", padx=(0, 15))
        
        # Apply button
        apply_btn = tk.Button(
            priority_frame,
            text="🚀 APPLY PRIORITY",
            font=("Segoe UI", 11, "bold"),
            bg="#10B981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="raised",
            bd=2,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.apply_priority
        )
        apply_btn.pack(side="left")
        
        # Hover effect for apply button
        def apply_hover_enter(e):
            apply_btn.config(bg='#059669', relief="sunken")
        def apply_hover_leave(e):
            apply_btn.config(bg='#10B981', relief="raised")
        apply_btn.bind("<Enter>", apply_hover_enter)
        apply_btn.bind("<Leave>", apply_hover_leave)
        
        # ========== QUICK ACTIONS ==========
        quick_frame = tk.Frame(main_content, bg="#f3f3f3")
        quick_frame.pack(fill="x", pady=(0, 20))
        
        # Quick actions button
        quick_btn = tk.Button(
            quick_frame,
            text="⚡ QUICK ACTIONS",
            font=("Segoe UI", 11),
            bg="#8B5CF6",
            fg="white",
            activebackground="#7C3AED",
            activeforeground="white",
            relief="raised",
            bd=2,
            padx=25,
            pady=10,
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
        
        # View all button
        view_all_btn = tk.Button(
            quick_frame,
            text="👁️ VIEW ALL REQUESTS",
            font=("Segoe UI", 11),
            bg="#3B82F6",
            fg="white",
            activebackground="#2563EB",
            activeforeground="white",
            relief="raised",
            bd=2,
            padx=25,
            pady=10,
            cursor="hand2",
            command=self.view_all_requests
        )
        view_all_btn.pack(side="left", padx=(15, 0))
        
        def view_hover_enter(e):
            view_all_btn.config(bg='#2563EB', relief="sunken")
        def view_hover_leave(e):
            view_all_btn.config(bg='#3B82F6', relief="raised")
        view_all_btn.bind("<Enter>", view_hover_enter)
        view_all_btn.bind("<Leave>", view_hover_leave)
        
        # ========== FOOTER ==========
        footer_frame = tk.Frame(parent, bg="#f3f3f3", pady=20)
        footer_frame.pack(fill="x", side="bottom")
        
        # Status bar
        status_bar = tk.Frame(footer_frame, bg="#333", height=35)
        status_bar.pack(fill="x")
        
        self.status_label = tk.Label(
            status_bar,
            text="Ready to prioritize SOS requests",
            fg="white",
            bg="#333",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(side="left", padx=20)
        
        # Instructions
        info_label = tk.Label(
            status_bar,
            text="ℹ️ Select a request and choose priority level",
            fg="#E5E7EB",
            bg="#333",
            font=("Segoe UI", 9, "italic")
        )
        info_label.pack(side="right", padx=20)
        
        # Center the window content
        self.center_content()

    def center_content(self):
        """Center the content horizontally"""
        self.update_idletasks()
        
    def on_row_select(self, event):
        """Handle row selection in table"""
        selected_item = self.table.focus()
        if selected_item:
            row = self.table.item(selected_item)["values"]
            if row:
                request_id = row[0]
                victim_name = row[1]
                location = row[2]
                urgency = row[4]
                
                self.selected_label.config(
                    text=f"ID: {request_id} | Victim: {victim_name}\nLocation: {location} | Current: {urgency.upper()}"
                )
                
                # Update status bar
                self.status_label.config(text=f"✅ Selected Request ID: {request_id}")

    def load_requests(self):
        """Load SOS requests from database"""
        # Clear existing data
        for item in self.table.get_children():
            self.table.delete(item)
        
        # Reset statistics
        for label in self.stat_labels:
            label.config(text="0")
        
        try:
            query = """
                SELECT SOSRequest.requestID, UserAccount.name, SOSRequest.location, 
                       SOSRequest.description, SOSRequest.urgencyLevel
                FROM SOSRequest
                JOIN UserAccount ON SOSRequest.victimID = UserAccount.userID
                WHERE SOSRequest.status='pending'
                ORDER BY 
                    CASE urgencyLevel
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                        ELSE 5
                    END
            """
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            # Statistics counters
            stats = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            
            for row in rows:
                request_id, victim_name, location, description, urgency = row
                
                # Format urgency with icons
                urgency_icons = {
                    "critical": "🚨 CRITICAL",
                    "high": "⚠️ HIGH",
                    "medium": "📊 MEDIUM",
                    "low": "📉 LOW"
                }
                urgency_display = urgency_icons.get(urgency, urgency.upper())
                
                # Insert into table
                self.table.insert("", "end", values=(
                    request_id,
                    victim_name,
                    location,
                    description[:100] + "..." if len(description) > 100 else description,
                    urgency_display
                ))
                
                # Update statistics
                if urgency in stats:
                    stats[urgency] += 1
            
            total_count = len(rows)
            
            # Update statistics labels
            if len(self.stat_labels) >= 5:
                self.stat_labels[0].config(text=str(total_count))
                self.stat_labels[1].config(text=str(stats["critical"]))
                self.stat_labels[2].config(text=str(stats["high"]))
                self.stat_labels[3].config(text=str(stats["medium"]))
                self.stat_labels[4].config(text=str(stats["low"]))
            
            self.status_label.config(text=f"✅ Loaded {total_count} pending SOS requests")
            
            if not rows:
                self.status_label.config(text="ℹ️ No pending SOS requests found")
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load requests: {str(e)}")
            self.status_label.config(text="❌ Failed to load requests")

    def apply_priority(self):
        """Apply priority to selected request"""
        selected_item = self.table.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a request first.")
            self.status_label.config(text="⚠ Please select a request first")
            return
        
        selected_priority = self.priority_var.get()
        if not selected_priority:
            messagebox.showwarning("Warning", "Please select a priority level.")
            self.status_label.config(text="⚠ Please select a priority level")
            return
        
        row = self.table.item(selected_item)["values"]
        request_id = row[0]
        
        # Confirm action
        if not messagebox.askyesno("Confirm", f"Set priority to '{selected_priority.upper()}' for Request ID {request_id}?"):
            return
        
        try:
            query = "UPDATE SOSRequest SET urgencyLevel=%s WHERE requestID=%s"
            self.cursor.execute(query, (selected_priority, request_id))
            self.connection.commit()
            
            # Success message
            messagebox.showinfo("Success", f"✅ Priority updated to '{selected_priority.upper()}'!")
            self.status_label.config(text=f"✅ Priority updated for Request ID {request_id}")
            
            # Remove from table and refresh
            self.table.delete(selected_item)
            self.selected_label.config(text="No request selected")
            self.priority_var.set("")
            
            # Update statistics
            self.load_requests()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update priority: {str(e)}")
            self.status_label.config(text="❌ Failed to update priority")

    def show_quick_actions(self):
        """Show quick action menu"""
        quick_menu = tk.Menu(self, tearoff=0)
        quick_menu.add_command(label="🚨 Mark All Critical", command=lambda: self.bulk_update("critical"))
        quick_menu.add_command(label="⚠️ Mark All High", command=lambda: self.bulk_update("high"))
        quick_menu.add_separator()
        quick_menu.add_command(label="🔄 Refresh All", command=self.load_requests)
        quick_menu.add_command(label="📊 Show Statistics", command=self.show_statistics)
        
        # Get button position
        try:
            btn = self.nametowidget(self.focus_get())
            x = btn.winfo_rootx()
            y = btn.winfo_rooty() + btn.winfo_height()
            quick_menu.tk_popup(x, y)
        except:
            quick_menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())

    def bulk_update(self, priority):
        """Bulk update all visible requests to a specific priority"""
        if not messagebox.askyesno("Bulk Update", f"Set ALL visible requests to '{priority.upper()}' priority?"):
            return
        
        try:
            # Get all request IDs from table
            request_ids = []
            for item in self.table.get_children():
                row = self.table.item(item)["values"]
                request_ids.append(row[0])
            
            if not request_ids:
                messagebox.showinfo("No Requests", "No requests to update.")
                return
            
            # Update all in database
            placeholders = ','.join(['%s'] * len(request_ids))
            query = f"UPDATE SOSRequest SET urgencyLevel=%s WHERE requestID IN ({placeholders})"
            self.cursor.execute(query, (priority, *request_ids))
            self.connection.commit()
            
            updated_count = self.cursor.rowcount
            messagebox.showinfo("Success", f"✅ Updated {updated_count} requests to '{priority.upper()}' priority!")
            self.status_label.config(text=f"✅ Bulk updated {updated_count} requests")
            
            # Refresh table
            self.load_requests()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to bulk update: {str(e)}")
            self.status_label.config(text="❌ Failed to bulk update")

    def show_statistics(self):
        """Show detailed statistics"""
        try:
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN urgencyLevel='critical' THEN 1 ELSE 0 END) as critical,
                    SUM(CASE WHEN urgencyLevel='high' THEN 1 ELSE 0 END) as high,
                    SUM(CASE WHEN urgencyLevel='medium' THEN 1 ELSE 0 END) as medium,
                    SUM(CASE WHEN urgencyLevel='low' THEN 1 ELSE 0 END) as low
                FROM SOSRequest 
                WHERE status='pending'
            """)
            stats = self.cursor.fetchone()
            
            total = stats[0] or 0
            critical = stats[1] or 0
            high = stats[2] or 0
            medium = stats[3] or 0
            low = stats[4] or 0
            
            messagebox.showinfo(
                "SOS Request Statistics",
                f"📊 Detailed Statistics (Pending Requests):\n\n"
                f"Total Requests: {total}\n"
                f"Critical: {critical}\n"
                f"High Priority: {high}\n"
                f"Medium: {medium}\n"
                f"Low: {low}\n\n"
                f"Priority Distribution:"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get statistics: {str(e)}")

    def view_all_requests(self):
        """View all requests including non-pending"""
        try:
            query = """
                SELECT SOSRequest.requestID, UserAccount.name, SOSRequest.location, 
                       SOSRequest.description, SOSRequest.urgencyLevel, SOSRequest.status
                FROM SOSRequest
                JOIN UserAccount ON SOSRequest.victimID = UserAccount.userID
                ORDER BY 
                    CASE urgencyLevel
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                        ELSE 5
                    END
            """
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            # Create a new window to show all requests
            all_window = tk.Toplevel(self)
            all_window.title("All SOS Requests")
            all_window.geometry("900x600")
            all_window.configure(bg="#f3f3f3")
            
            tk.Label(
                all_window,
                text="📋 All SOS Requests",
                font=("Segoe UI", 16, "bold"),
                fg="#1E40AF",
                bg="#f3f3f3"
            ).pack(pady=20)
            
            # Create Treeview
            columns = ("requestID", "victimName", "location", "urgencyLevel", "status")
            column_names = ["Request ID", "Victim Name", "Location", "Priority", "Status"]
            
            tree = ttk.Treeview(all_window, columns=columns, show="headings", height=20)
            
            for col, heading in zip(columns, column_names):
                tree.heading(col, text=heading, anchor="w")
                tree.column(col, width=150, anchor="w")
            
            tree.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(all_window, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            
            # Insert data
            for row in rows:
                tree.insert("", "end", values=row)
            
            tk.Label(
                all_window,
                text=f"Total Requests: {len(rows)}",
                font=("Segoe UI", 11),
                fg="#6B7280",
                bg="#f3f3f3"
            ).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load all requests: {str(e)}")

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


if __name__ == "__main__":
    # Test with back command
    def go_back_to_admin():
        print("Returning to Admin Dashboard...")
        app.destroy()
    
    # Test with None user (should work with default)
    app = PrioritizeRequestsApp(
        logged_in_user=None,  # This will trigger the default user creation
        back_command=go_back_to_admin
    )
    
    # Or test with proper user data
    # app = PrioritizeRequestsApp(
    #     logged_in_user={
    #         "userID": 1,
    #         "name": "Admin User",
    #         "role": "Admin",
    #         "email": "admin@drms.com"
    #     },
    #     back_command=go_back_to_admin
    # )
    
    app.mainloop()