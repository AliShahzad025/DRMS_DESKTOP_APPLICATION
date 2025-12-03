import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sv_ttk

# Allow imports from project root (so 'data' package is found)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.db_connection import DatabaseConnection

class AssignTaskApp(tk.Tk):
    def __init__(self, logged_in_user, db_connection=None, back_command=None):
        super().__init__()
        
        # Fix NoneType error by providing default values
        if logged_in_user is None:
            logged_in_user = {
                "userID": 2,
                "name": "Bob's Relief",
                "role": "NGO",
                "email": "bob.ngo@org.net"
            }
        
        self.logged_in_user = logged_in_user  # NGO user
        self.back_command = back_command
        
        self.title(f"DRMS - Task Management System")
        # Set to full screen
        self.state('zoomed')  # Maximized window
        self.configure(bg="#f5f8fa")
        
        # Apply Windows 11 theme
        sv_ttk.set_theme("light")
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", font=("Segoe UI", 10))
        style.map("TButton", background=[("active", "#e5e5e5")])
        style.configure("Treeview", rowheight=35, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#f0f0f0")
        
        self.option_add("*Font", ("Segoe UI", 10))
        
        # DB connection
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        self.cursor = self.connection.cursor(dictionary=True)

        # Create scrollable UI
        self.create_scrollable_ui()
        self.load_dashboard_data()
        self.load_volunteers()
        self.load_tasks()

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
        # ========== HEADER ==========
        header = tk.Frame(parent, bg="#2E7D32", height=110)  # Green for NGO
        header.pack(fill="x", pady=(0, 20))
        
        header_content = tk.Frame(header, bg="#2E7D32")
        header_content.pack(fill="both", expand=True, padx=30, pady=25)
        
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
        
        # Hover effects
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
            text="📋 TASK MANAGEMENT SYSTEM",
            font=("Segoe UI", 24, "bold"),
            fg="white",
            bg="#2E7D32"
        ).pack(anchor="w")
        
        tk.Label(
            title_frame,
            text="Assign and Monitor Disaster Response Tasks",
            font=("Segoe UI", 12),
            fg="#E8F5E9",
            bg="#2E7D32"
        ).pack(anchor="w", pady=(5, 0))
        
        # User info in header
        user_frame = tk.Frame(header_content, bg="#2E7D32")
        user_frame.pack(side="right")
        
        tk.Label(
            user_frame,
            text="🏢",
            font=("Segoe UI", 16),
            fg="white",
            bg="#2E7D32"
        ).pack(side="left", padx=(0, 10))
        
        # SAFELY get the name with fallback
        if isinstance(self.logged_in_user, dict):
            org_name = self.logged_in_user.get('name', 'NGO Organization')
        else:
            org_name = 'NGO Organization'
        
        tk.Label(
            user_frame,
            text=org_name,
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#2E7D32",
            justify="right"
        ).pack(side="right")

        # ========== DASHBOARD STATISTICS ==========
        stats_frame = tk.Frame(parent, bg="#f5f8fa", padx=30)
        stats_frame.pack(fill="x", pady=(0, 25))
        
        stats_data = [
            ("Total Volunteers", "👥", "#3B82F6", "0"),
            ("Available Tasks", "📝", "#10B981", "0"),
            ("Active SOS Requests", "🚨", "#EF4444", "0"),
            ("Completed Today", "✅", "#8B5CF6", "0"),
            ("Resources Stock", "📦", "#F59E0B", "0"),
            ("Urgency Score", "⚡", "#EC4899", "0")
        ]
        
        self.stat_labels = []
        for i, (title, icon, color, default_value) in enumerate(stats_data):
            card = tk.Frame(stats_frame, bg="white", relief="raised", bd=1)
            card.grid(row=0, column=i, padx=(0, 15) if i < len(stats_data)-1 else 0, sticky="nsew")
            stats_frame.columnconfigure(i, weight=1)
            
            # Icon and title
            icon_frame = tk.Frame(card, bg="white")
            icon_frame.pack(fill="x", padx=15, pady=(15, 5))
            
            tk.Label(
                icon_frame,
                text=icon,
                font=("Segoe UI", 24),
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
                font=("Segoe UI", 20, "bold"),
                fg=color,
                bg="white"
            )
            value_label.pack(pady=(0, 15))
            self.stat_labels.append(value_label)

        # ========== MAIN CONTENT AREA ==========
        content_frame = tk.Frame(parent, bg="#f5f8fa", padx=30)
        content_frame.pack(fill="both", expand=True, pady=(0, 30))
        
        # Left Panel - Volunteers
        left_panel = tk.Frame(content_frame, bg="#f5f8fa")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Volunteers Container
        vol_container = tk.Frame(left_panel, bg="white", relief="solid", bd=1)
        vol_container.pack(fill="both", expand=True)
        
        # Volunteers Header
        vol_header = tk.Frame(vol_container, bg="#E8F5E9", height=45)
        vol_header.pack(fill="x")
        
        tk.Label(
            vol_header,
            text="👥 VOLUNTEER ROSTER",
            font=("Segoe UI", 13, "bold"),
            fg="#1B5E20",
            bg="#E8F5E9"
        ).pack(side="left", padx=15, pady=10)
        
        vol_controls = tk.Frame(vol_header, bg="#E8F5E9")
        vol_controls.pack(side="right", padx=15)
        
        refresh_vol_btn = tk.Button(
            vol_controls,
            text="🔄 Refresh",
            font=("Segoe UI", 9),
            bg="#4CAF50",
            fg="white",
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.load_volunteers
        )
        refresh_vol_btn.pack(side="left", padx=(0, 5))
        
        filter_vol_btn = tk.Button(
            vol_controls,
            text="🔍 Filter",
            font=("Segoe UI", 9),
            bg="#2196F3",
            fg="white",
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.filter_volunteers
        )
        filter_vol_btn.pack(side="left")
        
        # Volunteers Treeview
        self.create_volunteer_treeview(vol_container)
        
        # Right Panel - Tasks
        right_panel = tk.Frame(content_frame, bg="#f5f8fa")
        right_panel.pack(side="right", fill="both", expand=True, padx=(15, 0))
        
        # Tasks Container
        task_container = tk.Frame(right_panel, bg="white", relief="solid", bd=1)
        task_container.pack(fill="both", expand=True)
        
        # Tasks Header
        task_header = tk.Frame(task_container, bg="#E3F2FD", height=45)
        task_header.pack(fill="x")
        
        tk.Label(
            task_header,
            text="📝 TASK INVENTORY",
            font=("Segoe UI", 13, "bold"),
            fg="#0D47A1",
            bg="#E3F2FD"
        ).pack(side="left", padx=15, pady=10)
        
        task_controls = tk.Frame(task_header, bg="#E3F2FD")
        task_controls.pack(side="right", padx=15)
        
        refresh_task_btn = tk.Button(
            task_controls,
            text="🔄 Refresh",
            font=("Segoe UI", 9),
            bg="#2196F3",
            fg="white",
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.load_tasks
        )
        refresh_task_btn.pack(side="left", padx=(0, 5))
        
        add_task_btn = tk.Button(
            task_controls,
            text="➕ Add Task",
            font=("Segoe UI", 9),
            bg="#4CAF50",
            fg="white",
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.add_new_task
        )
        add_task_btn.pack(side="left")
        
        # Tasks Treeview
        self.create_task_treeview(task_container)
        
        # ========== ASSIGNMENT PANEL ==========
        assign_frame = tk.Frame(parent, bg="white", relief="solid", bd=1, padx=25, pady=20)
        assign_frame.pack(fill="x", padx=30, pady=(20, 30))
        
        # Selected Info
        info_frame = tk.Frame(assign_frame, bg="white")
        info_frame.pack(fill="x", pady=(0, 20))
        
        # Selected Volunteer
        vol_info = tk.Frame(info_frame, bg="white")
        vol_info.pack(side="left", fill="x", expand=True, padx=(0, 20))
        
        tk.Label(
            vol_info,
            text="SELECTED VOLUNTEER:",
            font=("Segoe UI", 11, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        self.selected_vol_label = tk.Label(
            vol_info,
            text="👤 No volunteer selected",
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white",
            justify="left"
        )
        self.selected_vol_label.pack(anchor="w")
        
        # Selected Task
        task_info = tk.Frame(info_frame, bg="white")
        task_info.pack(side="right", fill="x", expand=True)
        
        tk.Label(
            task_info,
            text="SELECTED TASK:",
            font=("Segoe UI", 11, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 5))
        
        self.selected_task_label = tk.Label(
            task_info,
            text="📝 No task selected",
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white",
            justify="left"
        )
        self.selected_task_label.pack(anchor="w")
        
        # Assignment Controls
        controls_frame = tk.Frame(assign_frame, bg="white")
        controls_frame.pack(fill="x")
        
        # Assign Button
        assign_btn = tk.Button(
            controls_frame,
            text="🚀 ASSIGN TASK TO VOLUNTEER",
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
            command=self.assign_task
        )
        assign_btn.pack(side="left", padx=(0, 20))
        
        # Clear Selection Button
        clear_btn = tk.Button(
            controls_frame,
            text="🗑️ Clear Selection",
            font=("Segoe UI", 11),
            bg="#6B7280",
            fg="white",
            activebackground="#4B5563",
            activeforeground="white",
            relief="flat",
            padx=25,
            pady=12,
            cursor="hand2",
            command=self.clear_selection
        )
        clear_btn.pack(side="left")
        
        # ========== QUICK ACTIONS ==========
        quick_frame = tk.Frame(parent, bg="#f5f8fa", padx=30)
        quick_frame.pack(fill="x", pady=(0, 20))
        
        action_buttons = [
            ("⚡ Quick Assign", "#8B5CF6", self.quick_assign),
            ("📊 View Statistics", "#3B82F6", self.show_statistics),
            ("📋 Task History", "#10B981", self.view_task_history),
            ("🔔 Notifications", "#F59E0B", self.show_notifications)
        ]
        
        for text, color, command in action_buttons:
            btn = tk.Button(
                quick_frame,
                text=text,
                font=("Segoe UI", 11),
                bg=color,
                fg="white",
                activebackground=self.darken_color(color),
                activeforeground="white",
                relief="raised",
                bd=2,
                padx=25,
                pady=10,
                cursor="hand2",
                command=command
            )
            btn.pack(side="left", padx=(0, 15))
            
            # Add hover effect
            def make_hover(btn, color):
                def on_enter(e):
                    btn.config(bg=self.darken_color(color), relief="sunken")
                def on_leave(e):
                    btn.config(bg=color, relief="raised")
                return on_enter, on_leave
            
            on_enter, on_leave = make_hover(btn, color)
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        # ========== FOOTER ==========
        footer_frame = tk.Frame(parent, bg="#333", height=40)
        footer_frame.pack(fill="x", side="bottom")
        
        # Status bar
        self.status_label = tk.Label(
            footer_frame,
            text="✅ System Ready | Select a volunteer and task to assign",
            fg="white",
            bg="#333",
            font=("Segoe UI", 10)
        )
        self.status_label.pack(side="left", padx=20)
        
        # System info
        sys_info = tk.Label(
            footer_frame,
            text=f"🏢 NGO: {self.logged_in_user.get('name', 'Unknown')} | Database: Connected",
            fg="#E5E7EB",
            bg="#333",
            font=("Segoe UI", 9)
        )
        sys_info.pack(side="right", padx=20)
        
        # Bind selection events
        self.vol_tree.bind("<<TreeviewSelect>>", self.on_volunteer_select)
        self.task_tree.bind("<<TreeviewSelect>>", self.on_task_select)
        
        # Bind double-click events
        self.vol_tree.bind("<Double-1>", lambda e: self.on_volunteer_select(e))
        self.task_tree.bind("<Double-1>", lambda e: self.on_task_select(e))

    def darken_color(self, color):
        """Darken a hex color by 20%"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darker = tuple(max(0, int(c * 0.8)) for c in rgb)
        return f'#{darker[0]:02x}{darker[1]:02x}{darker[2]:02x}'

    def create_volunteer_treeview(self, parent):
        """Create volunteers treeview with scrollbars"""
        tree_frame = tk.Frame(parent, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side="right", fill="y")
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")
        
        # Treeview
        columns = ("volunteerID", "name", "roles", "status", "verified", "last_active")
        self.vol_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=12,
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        
        # Configure scrollbars
        y_scrollbar.config(command=self.vol_tree.yview)
        x_scrollbar.config(command=self.vol_tree.xview)
        
        self.vol_tree.pack(side="left", fill="both", expand=True)
        
        # Configure columns
        column_configs = {
            "volunteerID": ("ID", 70, "center"),
            "name": ("Name", 150, "w"),
            "roles": ("Roles", 200, "w"),
            "status": ("Status", 100, "center"),
            "verified": ("Verified", 80, "center"),
            "last_active": ("Last Active", 120, "center")
        }
        
        for col in columns:
            heading, width, anchor = column_configs[col]
            self.vol_tree.heading(col, text=heading, anchor="center")
            self.vol_tree.column(col, width=width, anchor=anchor)

    def create_task_treeview(self, parent):
        """Create tasks treeview with scrollbars"""
        tree_frame = tk.Frame(parent, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side="right", fill="y")
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")
        
        # Treeview
        columns = ("taskID", "title", "description", "taskType", "status", "urgency")
        self.task_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=12,
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        
        # Configure scrollbars
        y_scrollbar.config(command=self.task_tree.yview)
        x_scrollbar.config(command=self.task_tree.xview)
        
        self.task_tree.pack(side="left", fill="both", expand=True)
        
        # Configure columns
        column_configs = {
            "taskID": ("Task ID", 80, "center"),
            "title": ("Title", 180, "w"),
            "description": ("Description", 250, "w"),
            "taskType": ("Type", 100, "center"),
            "status": ("Status", 100, "center"),
            "urgency": ("Urgency", 100, "center")
        }
        
        for col in columns:
            heading, width, anchor = column_configs[col]
            self.task_tree.heading(col, text=heading, anchor="center")
            self.task_tree.column(col, width=width, anchor=anchor)

    def load_dashboard_data(self):
        """Load dashboard statistics"""
        try:
            # Total Volunteers
            self.cursor.execute("SELECT COUNT(*) as count FROM Volunteer")
            total_vol = self.cursor.fetchone()["count"]
            
            # Available Tasks
            self.cursor.execute("SELECT COUNT(*) as count FROM Task WHERE status = 'unassigned'")
            avail_tasks = self.cursor.fetchone()["count"]
            
            # Active SOS Requests
            self.cursor.execute("""
                SELECT COUNT(*) as count FROM SOSRequest 
                WHERE status IN ('assigned', 'in_process')
            """)
            active_sos = self.cursor.fetchone()["count"]
            
            # Completed Today
            self.cursor.execute("""
                SELECT COUNT(*) as count FROM Task 
                WHERE status = 'completed' 
                AND DATE(updated_at) = CURDATE()
            """)
            completed_today = self.cursor.fetchone()["count"] or 0
            
            # Resources Stock
            self.cursor.execute("SELECT SUM(quantity) as total FROM ResourceStock WHERE status = 'available'")
            resources = self.cursor.fetchone()["total"] or 0
            
            # Update statistics labels
            stats = [total_vol, avail_tasks, active_sos, completed_today, resources, "High"]
            for i, value in enumerate(stats):
                if i < len(self.stat_labels):
                    self.stat_labels[i].config(text=str(value))
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")

    def load_volunteers(self):
        """Load volunteers from database"""
        self.vol_tree.delete(*self.vol_tree.get_children())
        
        try:
            self.cursor.execute("""
                SELECT u.userID AS volunteerID, u.name, v.roles, v.status, v.verified, v.last_active
                FROM Volunteer v
                JOIN UserAccount u ON v.volunteerID = u.userID
                ORDER BY 
                    CASE v.status
                        WHEN 'available' THEN 1
                        WHEN 'busy' THEN 2
                        ELSE 3
                    END,
                    u.name
            """)
            
            volunteers = self.cursor.fetchall()
            
            for vol in volunteers:
                # Format status with icon
                status_icon = "✅ " if vol["status"] == "available" else "⏳ "
                status_display = status_icon + vol["status"].title()
                
                # Format verified status
                verified_display = "✅ Yes" if vol["verified"] else "❌ No"
                
                self.vol_tree.insert("", tk.END, values=(
                    vol["volunteerID"],
                    vol["name"],
                    vol["roles"],
                    status_display,
                    verified_display,
                    vol["last_active"].strftime("%Y-%m-%d %H:%M") if vol["last_active"] else "N/A"
                ))
            
            self.status_label.config(text=f"✅ Loaded {len(volunteers)} volunteers")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load volunteers: {str(e)}")
            self.status_label.config(text="❌ Failed to load volunteers")

    def load_tasks(self):
        """Load tasks from database"""
        self.task_tree.delete(*self.task_tree.get_children())
        
        try:
            self.cursor.execute("""
                SELECT t.taskID, t.title, t.description, t.taskType, t.status, 
                       COALESCE(s.urgencyLevel, 'medium') as urgency
                FROM Task t
                LEFT JOIN SOSRequest s ON t.relatedRequestID = s.requestID
                WHERE t.status = 'unassigned'
                ORDER BY 
                    CASE COALESCE(s.urgencyLevel, 'medium')
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                        ELSE 5
                    END,
                    t.taskID
            """)
            
            tasks = self.cursor.fetchall()
            
            for task in tasks:
                # Format urgency with icon
                urgency_icons = {
                    "critical": "🚨",
                    "high": "⚠️",
                    "medium": "📊",
                    "low": "📉"
                }
                urgency_icon = urgency_icons.get(task["urgency"], "📝")
                urgency_display = f"{urgency_icon} {task['urgency'].title()}"
                
                # Truncate description if too long
                description = task["description"]
                if len(description) > 60:
                    description = description[:57] + "..."
                
                self.task_tree.insert("", tk.END, values=(
                    task["taskID"],
                    task["title"],
                    description,
                    task["taskType"].title(),
                    task["status"].title(),
                    urgency_display
                ))
            
            self.status_label.config(text=f"✅ Loaded {len(tasks)} available tasks")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load tasks: {str(e)}")
            self.status_label.config(text="❌ Failed to load tasks")

    def on_volunteer_select(self, event):
        """Handle volunteer selection"""
        selected_item = self.vol_tree.focus()
        if selected_item:
            row = self.vol_tree.item(selected_item)["values"]
            if row:
                volunteer_id = row[0]
                volunteer_name = row[1]
                status = row[3]
                
                # Update label with color based on status
                if "available" in status:
                    text_color = "#10B981"
                    status_text = "✅ Available"
                else:
                    text_color = "#EF4444"
                    status_text = "⏳ Busy"
                
                self.selected_vol_label.config(
                    text=f"👤 {volunteer_name} (ID: {volunteer_id}) | {status_text}",
                    fg=text_color
                )
                
                # Update status bar
                self.status_label.config(text=f"✅ Selected Volunteer: {volunteer_name}")

    def on_task_select(self, event):
        """Handle task selection"""
        selected_item = self.task_tree.focus()
        if selected_item:
            row = self.task_tree.item(selected_item)["values"]
            if row:
                task_id = row[0]
                task_title = row[1]
                task_type = row[3]
                urgency = row[5]
                
                # Determine color based on urgency
                if "🚨" in urgency:
                    text_color = "#EF4444"
                elif "⚠️" in urgency:
                    text_color = "#F59E0B"
                elif "📊" in urgency:
                    text_color = "#3B82F6"
                else:
                    text_color = "#10B981"
                
                self.selected_task_label.config(
                    text=f"📝 {task_title} (ID: {task_id}) | Type: {task_type} | {urgency}",
                    fg=text_color
                )
                
                # Update status bar
                self.status_label.config(text=f"✅ Selected Task: {task_title}")

    def assign_task(self):
        """Assign selected task to selected volunteer"""
        selected_vol = self.vol_tree.focus()
        selected_task = self.task_tree.focus()

        if not selected_vol or not selected_task:
            messagebox.showwarning("Selection Missing", "Please select both a volunteer and a task.")
            self.status_label.config(text="⚠ Please select both a volunteer and a task")
            return

        vol_data = self.vol_tree.item(selected_vol)["values"]
        task_data = self.task_tree.item(selected_task)["values"]

        volunteer_id = vol_data[0]
        volunteer_name = vol_data[1]
        volunteer_status = vol_data[3]
        task_id = task_data[0]
        task_title = task_data[1]
        task_urgency = task_data[5]

        # Check if volunteer is available
        if "available" not in volunteer_status:
            messagebox.showerror("Unavailable", f"Volunteer {volunteer_name} is currently busy.")
            self.status_label.config(text=f"❌ Volunteer {volunteer_name} is busy")
            return

        # Confirmation dialog
        confirm = messagebox.askyesno("Confirm Assignment",
                                      f"Assign task '{task_title}' to volunteer '{volunteer_name}'?\n\n"
                                      f"Task Urgency: {task_urgency}\n"
                                      f"Volunteer Status: {volunteer_status}")
        
        if not confirm:
            self.status_label.config(text="Assignment cancelled")
            return

        try:
            # Get NGO ID from logged_in_user
            ngo_id = self.logged_in_user.get("userID") or self.logged_in_user.get("id") or 2
            
            # Update Task
            self.cursor.execute("""
                UPDATE Task
                SET assignedVolunteerID = %s, status = 'assigned', createdBy = %s
                WHERE taskID = %s
            """, (volunteer_id, ngo_id, task_id))

            # Update Volunteer status
            self.cursor.execute("""
                UPDATE Volunteer
                SET status = 'busy', last_active = NOW()
                WHERE volunteerID = %s
            """, (volunteer_id,))

            # Add to TaskHistory
            self.cursor.execute("""
                INSERT INTO TaskHistory (taskID, volunteerID, previousStatus, newStatus, note)
                VALUES (%s, %s, 'unassigned', 'assigned', %s)
            """, (task_id, volunteer_id, f"Assigned by {self.logged_in_user.get('name', 'NGO')}"))

            self.connection.commit()
            
            messagebox.showinfo("Success", 
                              f"✅ Task Assignment Complete!\n\n"
                              f"Task: {task_title}\n"
                              f"Assigned to: {volunteer_name}\n"
                              f"Status: In Progress\n"
                              f"Assigned by: {self.logged_in_user.get('name', 'NGO')}")
            
            self.status_label.config(text=f"✅ Task '{task_title}' assigned to {volunteer_name}")

            # Refresh data
            self.load_volunteers()
            self.load_tasks()
            self.load_dashboard_data()
            
            # Clear selection labels
            self.clear_selection()

        except Exception as e:
            self.connection.rollback()
            messagebox.showerror("Database Error", f"Failed to assign task.\n\nError: {str(e)}")
            self.status_label.config(text="❌ Failed to assign task")

    def clear_selection(self):
        """Clear current selection"""
        self.selected_vol_label.config(
            text="👤 No volunteer selected",
            fg="#6B7280"
        )
        self.selected_task_label.config(
            text="📝 No task selected",
            fg="#6B7280"
        )
        self.status_label.config(text="✅ Selection cleared. Ready for new assignment")

    def filter_volunteers(self):
        """Filter volunteers dialog"""
        filter_dialog = tk.Toplevel(self)
        filter_dialog.title("Filter Volunteers")
        filter_dialog.geometry("300x250")
        filter_dialog.configure(bg="#f5f8fa")
        
        tk.Label(
            filter_dialog,
            text="Filter Options",
            font=("Segoe UI", 14, "bold"),
            bg="#f5f8fa",
            fg="#374151"
        ).pack(pady=20)
        
        # Status filter
        status_var = tk.StringVar(value="all")
        tk.Label(filter_dialog, text="Status:", bg="#f5f8fa").pack(anchor="w", padx=30)
        ttk.Radiobutton(filter_dialog, text="All", variable=status_var, value="all").pack(anchor="w", padx=50)
        ttk.Radiobutton(filter_dialog, text="Available Only", variable=status_var, value="available").pack(anchor="w", padx=50)
        ttk.Radiobutton(filter_dialog, text="Busy Only", variable=status_var, value="busy").pack(anchor="w", padx=50)
        
        # Verified filter
        verified_var = tk.StringVar(value="all")
        tk.Label(filter_dialog, text="Verified:", bg="#f5f8fa").pack(anchor="w", padx=30, pady=(10,0))
        ttk.Radiobutton(filter_dialog, text="All", variable=verified_var, value="all").pack(anchor="w", padx=50)
        ttk.Radiobutton(filter_dialog, text="Verified Only", variable=verified_var, value="verified").pack(anchor="w", padx=50)
        
        def apply_filter():
            # Simple filter implementation
            messagebox.showinfo("Info", "Filter applied (demo feature)")
            filter_dialog.destroy()
        
        tk.Button(
            filter_dialog,
            text="Apply Filter",
            bg="#4CAF50",
            fg="white",
            command=apply_filter
        ).pack(pady=20)

    def add_new_task(self):
        """Add new task dialog"""
        add_dialog = tk.Toplevel(self)
        add_dialog.title("Add New Task")
        add_dialog.geometry("400x400")
        add_dialog.configure(bg="#f5f8fa")
        
        tk.Label(
            add_dialog,
            text="Create New Task",
            font=("Segoe UI", 16, "bold"),
            bg="#f5f8fa",
            fg="#374151"
        ).pack(pady=20)
        
        # Form fields
        fields = [
            ("Title:", tk.Entry(add_dialog, width=40)),
            ("Description:", tk.Text(add_dialog, height=4, width=38)),
            ("Type:", ttk.Combobox(add_dialog, values=["Delivery", "Assessment", "Rescue", "Medical", "Logistics"], state="readonly")),
            ("Urgency:", ttk.Combobox(add_dialog, values=["Low", "Medium", "High", "Critical"], state="readonly"))
        ]
        
        for label, widget in fields:
            tk.Label(add_dialog, text=label, bg="#f5f8fa").pack(anchor="w", padx=30, pady=(10,0))
            widget.pack(padx=30, pady=(5,10))
        
        def save_task():
            messagebox.showinfo("Info", "New task created (demo feature)")
            add_dialog.destroy()
            self.load_tasks()
        
        tk.Button(
            add_dialog,
            text="Save Task",
            bg="#4CAF50",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=10,
            command=save_task
        ).pack(pady=20)

    def quick_assign(self):
        """Quick assign functionality"""
        messagebox.showinfo("Quick Assign", 
                          "This feature automatically assigns the most urgent task\n"
                          "to the first available volunteer.\n\n"
                          "Feature coming soon!")

    def show_statistics(self):
        """Show detailed statistics"""
        try:
            self.cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM Volunteer) as total_volunteers,
                    (SELECT COUNT(*) FROM Volunteer WHERE status='available') as available_volunteers,
                    (SELECT COUNT(*) FROM Task) as total_tasks,
                    (SELECT COUNT(*) FROM Task WHERE status='unassigned') as unassigned_tasks,
                    (SELECT COUNT(*) FROM Task WHERE status='in_progress') as in_progress_tasks,
                    (SELECT COUNT(*) FROM Task WHERE status='completed') as completed_tasks
            """)
            stats = self.cursor.fetchone()
            
            messagebox.showinfo(
                "System Statistics",
                f"📊 VOLUNTEER STATISTICS:\n"
                f"Total Volunteers: {stats['total_volunteers']}\n"
                f"Available: {stats['available_volunteers']}\n"
                f"Busy: {stats['total_volunteers'] - stats['available_volunteers']}\n\n"
                f"📊 TASK STATISTICS:\n"
                f"Total Tasks: {stats['total_tasks']}\n"
                f"Unassigned: {stats['unassigned_tasks']}\n"
                f"In Progress: {stats['in_progress_tasks']}\n"
                f"Completed: {stats['completed_tasks']}\n\n"
                f"Assignment Rate: {(stats['completed_tasks']/stats['total_tasks']*100):.1f}%" if stats['total_tasks'] > 0 else "Assignment Rate: 0%"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get statistics: {str(e)}")

    def view_task_history(self):
        """View task history"""
        try:
            self.cursor.execute("""
                SELECT th.taskID, t.title, u.name as volunteer_name, 
                       th.previousStatus, th.newStatus, th.note, th.timestamp
                FROM TaskHistory th
                JOIN Task t ON th.taskID = t.taskID
                LEFT JOIN UserAccount u ON th.volunteerID = u.userID
                ORDER BY th.timestamp DESC
                LIMIT 50
            """)
            history = self.cursor.fetchall()
            
            history_window = tk.Toplevel(self)
            history_window.title("Task History")
            history_window.geometry("800x500")
            history_window.configure(bg="#f5f8fa")
            
            tk.Label(
                history_window,
                text="📋 Task Assignment History",
                font=("Segoe UI", 16, "bold"),
                fg="#1E40AF",
                bg="#f5f8fa"
            ).pack(pady=20)
            
            # Create Treeview
            columns = ("taskID", "title", "volunteer", "from", "to", "note", "timestamp")
            tree = ttk.Treeview(history_window, columns=columns, show="headings", height=20)
            
            for col in columns:
                tree.heading(col, text=col.title(), anchor="w")
                tree.column(col, width=100, anchor="w")
            
            tree.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            
            # Insert data
            for record in history:
                tree.insert("", "end", values=record)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load task history: {str(e)}")

    def show_notifications(self):
        """Show notifications"""
        try:
            self.cursor.execute("""
                SELECT message, channel, status, timestamp
                FROM Notification
                WHERE recipientRole = 'NGO'
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            notifications = self.cursor.fetchall()
            
            notif_text = "🔔 Recent Notifications:\n\n"
            for notif in notifications:
                channel_icon = "📱" if notif["channel"] == "sms" else "📧" if notif["channel"] == "email" else "💬"
                status_icon = "✅" if notif["status"] == "read" else "📨" if notif["status"] == "sent" else "📤"
                notif_text += f"{channel_icon} {status_icon} {notif['message']}\n"
            
            messagebox.showinfo("Notifications", notif_text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load notifications: {str(e)}")

    def go_back_to_ngo_dashboard(self):
        """Go back to NGODashboardApp"""
        if messagebox.askyesno("Confirm", "Return to NGO Dashboard?"):
            try:
                # First try the custom back command if provided
                if self.back_command:
                    self.back_command()
                    return
                
                # Ensure we have valid user data
                if not self.logged_in_user or not isinstance(self.logged_in_user, dict):
                    user_data = {
                        "userID": 2,
                        "name": "Bob's Relief",
                        "role": "NGO",
                        "email": "bob.ngo@org.net"
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
    # Test with back command
    def go_back_to_ngo():
        print("Returning to NGO Dashboard...")
        app.destroy()
    
    # Test with sample user from database
    app = AssignTaskApp(
        logged_in_user={
            "userID": 2,
            "name": "Bob's Relief",
            "role": "NGO",
            "email": "bob.ngo@org.net"
        },
        back_command=go_back_to_ngo
    )
    
    app.mainloop()