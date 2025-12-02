import tkinter as tk
from tkinter import messagebox, ttk
from data.db_connection import DatabaseConnection

class GiveFeedbackApp(tk.Tk):
    def __init__(self, logged_in_user=None, db_connection=None, back_command=None):
        super().__init__()
        self.logged_in_user = logged_in_user or {}
        self.back_command = back_command
        
        self.title("DRMS - Provide Feedback")
        self.geometry("1100x800")
        self.resizable(True, True)
        self.configure(bg="#f5f8fa")
        
        # DB connection
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        self.cursor = self.connection.cursor(dictionary=True)
        
        # Store reference to parent window if needed
        self.parent_window = None
        
        self.create_widgets()
        self.load_completed_requests()

    def create_widgets(self):
        # ========== HEADER WITH RED BACK BUTTON ==========
        header = tk.Frame(self, bg="#8B5CF6", height=100)
        header.pack(fill="x", pady=(0, 20))
        
        header_content = tk.Frame(header, bg="#8B5CF6")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # RED BACK BUTTON
        back_btn = tk.Button(
            header_content,
            text="◄ BACK TO VICTIM PORTAL",
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
            command=self.go_back_to_victim_dashboard
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
        title_frame = tk.Frame(header_content, bg="#8B5CF6")
        title_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            title_frame,
            text="💬 PROVIDE FEEDBACK",
            font=("Segoe UI", 24, "bold"),
            fg="white",
            bg="#8B5CF6"
        ).pack(anchor="w")
        
        tk.Label(
            title_frame,
            text="Share your experience to help us improve relief services",
            font=("Segoe UI", 12),
            fg="#E9D5FF",
            bg="#8B5CF6"
        ).pack(anchor="w", pady=(5, 0))
        
        # Victim info
        victim_name = self.logged_in_user.get('name', 'Victim')
        user_info = tk.Frame(header_content, bg="#8B5CF6")
        user_info.pack(side="right")
        
        tk.Label(
            user_info,
            text=f"😢 {victim_name}",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#8B5CF6",
            justify="right"
        ).pack(side="right")
        
        # ========== MAIN CONTAINER ==========
        main_container = tk.Frame(self, bg="#f5f8fa")
        main_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        # Left panel - Requests
        left_panel = tk.Frame(main_container, bg="white", relief="solid", bd=1, padx=25, pady=25)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        tk.Label(
            left_panel,
            text="📋 YOUR REQUESTS",
            font=("Segoe UI", 16, "bold"),
            fg="#1E40AF",
            bg="white"
        ).pack(anchor="w", pady=(0, 15))
        
        # Refresh button
        refresh_btn = tk.Button(
            left_panel,
            text="🔄 Refresh List",
            font=("Segoe UI", 10),
            bg="#3B82F6",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.load_completed_requests
        )
        refresh_btn.pack(anchor="w", pady=(0, 15))
        
        # Treeview for requests
        tree_frame = tk.Frame(left_panel, bg="white")
        tree_frame.pack(fill="both", expand=True)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side="right", fill="y")
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")
        
        # Treeview
        columns = ("requestID", "location", "typeOfNeed", "status")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=12,
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set,
            selectmode="browse"
        )
        
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Configure columns
        column_configs = {
            "requestID": ("Request ID", 100, "center"),
            "location": ("Location", 150, "w"),
            "typeOfNeed": ("Need Type", 150, "w"),
            "status": ("Status", 120, "center")
        }
        
        for col in columns:
            heading, width, anchor = column_configs[col]
            self.tree.heading(col, text=heading, anchor="center")
            self.tree.column(col, width=width, anchor=anchor, minwidth=width)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_request_select)
        
        # Selection info
        self.selection_label = tk.Label(
            left_panel,
            text="👈 Select a request to provide feedback",
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white",
            justify="left"
        )
        self.selection_label.pack(anchor="w", pady=(15, 0))
        
        # Right panel - Feedback Form
        right_panel = tk.Frame(main_container, bg="white", relief="solid", bd=1, padx=25, pady=25)
        right_panel.pack(side="right", fill="both", expand=True, padx=(15, 0))
        
        tk.Label(
            right_panel,
            text="📝 FEEDBACK FORM",
            font=("Segoe UI", 16, "bold"),
            fg="#1E40AF",
            bg="white"
        ).pack(anchor="w", pady=(0, 25))
        
        # Rating section
        rating_frame = tk.Frame(right_panel, bg="white")
        rating_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            rating_frame,
            text="⭐ RATING (1-5)",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 10))
        
        # Star rating display
        self.star_frame = tk.Frame(rating_frame, bg="white")
        self.star_frame.pack(anchor="w", pady=(0, 10))
        
        self.stars = []
        for i in range(5):
            star = tk.Label(
                self.star_frame,
                text="☆",
                font=("Segoe UI", 24),
                fg="#F59E0B",
                bg="white",
                cursor="hand2"
            )
            star.pack(side="left", padx=2)
            star.bind("<Button-1>", lambda e, idx=i: self.set_rating(idx + 1))
            self.stars.append(star)
        
        # Numeric rating
        tk.Label(
            rating_frame,
            text="Selected Rating:",
            font=("Segoe UI", 11),
            fg="#374151",
            bg="white"
        ).pack(side="left", padx=(0, 10))
        
        self.rating_var = tk.IntVar(value=5)
        self.rating_label = tk.Label(
            rating_frame,
            text="5/5",
            font=("Segoe UI", 14, "bold"),
            fg="#F59E0B",
            bg="white"
        )
        self.rating_label.pack(side="left")
        
        # Numeric spinner
        tk.Label(
            rating_frame,
            text="Or select rating:",
            font=("Segoe UI", 10),
            fg="#6B7280",
            bg="white"
        ).pack(side="left", padx=(20, 5))
        
        rating_spin = ttk.Spinbox(
            rating_frame,
            from_=1,
            to=5,
            textvariable=self.rating_var,
            width=10,
            font=("Segoe UI", 11),
            command=lambda: self.update_stars(self.rating_var.get())
        )
        rating_spin.pack(side="left", pady=(0, 20))
        
        # Comments section
        tk.Label(
            right_panel,
            text="💭 COMMENTS",
            font=("Segoe UI", 12, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 10))
        
        # Comments text box with scrollbar
        comment_frame = tk.Frame(right_panel, bg="white")
        comment_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        self.comment_text = tk.Text(
            comment_frame,
            height=8,
            font=("Segoe UI", 11),
            wrap="word",
            relief="solid",
            borderwidth=1,
            padx=10,
            pady=10
        )
        self.comment_text.pack(side="left", fill="both", expand=True)
        
        comment_scrollbar = ttk.Scrollbar(comment_frame, command=self.comment_text.yview)
        comment_scrollbar.pack(side="right", fill="y")
        self.comment_text.config(yscrollcommand=comment_scrollbar.set)
        
        # Placeholder text
        self.comment_text.insert("1.0", "Please share your experience here...")
        self.comment_text.config(fg="gray")
        
        def on_focus_in(event):
            if self.comment_text.get("1.0", "end-1c") == "Please share your experience here...":
                self.comment_text.delete("1.0", tk.END)
                self.comment_text.config(fg="black")
        
        def on_focus_out(event):
            if not self.comment_text.get("1.0", "end-1c").strip():
                self.comment_text.insert("1.0", "Please share your experience here...")
                self.comment_text.config(fg="gray")
        
        self.comment_text.bind("<FocusIn>", on_focus_in)
        self.comment_text.bind("<FocusOut>", on_focus_out)
        
        # ========== BUTTONS ==========
        button_frame = tk.Frame(right_panel, bg="white")
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Clear button
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear Form",
            font=("Segoe UI", 12),
            bg="#6B7280",
            fg="white",
            activebackground="#4B5563",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.clear_form
        )
        clear_btn.pack(side="left", padx=(0, 15))
        
        # Submit button
        self.submit_btn = tk.Button(
            button_frame,
            text="🚀 SUBMIT FEEDBACK",
            font=("Segoe UI", 12, "bold"),
            bg="#10B981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="raised",
            bd=2,
            padx=30,
            pady=10,
            cursor="hand2",
            command=self.submit_feedback
        )
        self.submit_btn.pack(side="left")
        
        # Initialize stars
        self.update_stars(5)
        
        # ========== FOOTER ==========
        footer_frame = tk.Frame(self, bg="#333", height=40)
        footer_frame.pack(fill="x", side="bottom")
        
        # Status label
        self.status_label = tk.Label(
            footer_frame,
            text="✅ Ready to provide feedback | Select a request and share your experience",
            fg="white",
            bg="#333",
            font=("Segoe UI", 10)
        )
        self.status_label.pack(side="left", padx=20)

    def update_stars(self, rating):
        """Update star display based on rating"""
        for i, star in enumerate(self.stars):
            if i < rating:
                star.config(text="★")
            else:
                star.config(text="☆")
        self.rating_label.config(text=f"{rating}/5")

    def set_rating(self, rating):
        """Set rating when clicking stars"""
        self.rating_var.set(rating)
        self.update_stars(rating)

    def on_request_select(self, event):
        """Handle request selection"""
        selected_item = self.tree.focus()
        if selected_item:
            row = self.tree.item(selected_item)["values"]
            if row:
                request_id = row[0]
                location = row[1]
                need_type = row[2]
                status = row[3]
                
                self.selection_label.config(
                    text=f"✅ Selected: Request ID {request_id} | 📍 {location} | 🆘 {need_type} | 📊 {status}",
                    fg="#374151"
                )
                
                self.status_label.config(text=f"✅ Selected Request ID: {request_id}. Please provide your feedback.")

    def load_completed_requests(self):
        """Load SOS requests linked to this victim"""
        try:
            self.status_label.config(text="⏳ Loading your requests...")
            self.update()
            
            query = """
            SELECT R.requestID, R.location, R.typeOfNeed, R.status,
                   V.name as assignedVolunteer, N.orgName as assignedNGO
            FROM SOSRequest R
            LEFT JOIN UserAccount V ON R.assignedVolunteerID = V.userID
            LEFT JOIN NGO N ON R.assignedNGO = N.ngoID
            WHERE R.victimID=%s
            ORDER BY 
                CASE R.status
                    WHEN 'completed' THEN 1
                    WHEN 'in_process' THEN 2
                    WHEN 'assigned' THEN 3
                    ELSE 4
                END,
                R.requestID DESC
            """
            self.cursor.execute(query, (self.logged_in_user.get("id"),))
            results = self.cursor.fetchall()
            
            self.tree.delete(*self.tree.get_children())
            
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
                
                self.tree.insert("", tk.END, values=(
                    row["requestID"],
                    row["location"],
                    row["typeOfNeed"],
                    status_display
                ))
            
            self.status_label.config(text=f"✅ Loaded {len(results)} of your requests")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load requests.\n{str(e)}")
            self.status_label.config(text="❌ Failed to load requests")

    def clear_form(self):
        """Clear the feedback form"""
        self.set_rating(5)
        self.rating_var.set(5)
        
        # Clear comments
        self.comment_text.delete("1.0", tk.END)
        self.comment_text.insert("1.0", "Please share your experience here...")
        self.comment_text.config(fg="gray")
        
        self.status_label.config(text="✅ Form cleared. Ready for new feedback")

    def submit_feedback(self):
        """Submit feedback for selected request"""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a request to give feedback.")
            self.status_label.config(text="⚠ Please select a request first")
            return

        request_values = self.tree.item(selected_item, "values")
        request_id = request_values[0]
        rating = self.rating_var.get()
        
        # Get comments and handle placeholder
        comments = self.comment_text.get("1.0", tk.END).strip()
        if comments == "Please share your experience here...":
            comments = ""

        if rating < 1 or rating > 5:
            messagebox.showwarning("Invalid Rating", "Rating must be between 1 and 5.")
            self.status_label.config(text="❌ Rating must be 1-5")
            return

        # Confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm Submission",
            f"Submit feedback for Request ID {request_id}?\n\n"
            f"Rating: {rating}/5\n"
            f"Comments: {comments[:100]}{'...' if len(comments) > 100 else ''}"
        )
        
        if not confirm:
            self.status_label.config(text="❌ Feedback submission cancelled")
            return

        try:
            self.status_label.config(text="⏳ Submitting feedback...")
            self.update()
            
            # Try without timestamp first
            sql = """
            INSERT INTO Feedback (requestID, victimID, rating, comments)
            VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(sql, (request_id, self.logged_in_user.get("id"), rating, comments))
            self.connection.commit()
            
            # Success message
            messagebox.showinfo(
                "✅ Feedback Successfully Submitted", 
                f"Your feedback has been submitted!\n\n"
                f"📋 Request ID: {request_id}\n"
                f"⭐ Rating: {rating}/5\n"
                f"📝 Comments: {'Provided' if comments else 'No comments'}\n\n"
                f"Thank you for helping us improve our services! 🙏"
            )
            
            self.status_label.config(text=f"✅ Feedback submitted for Request ID {request_id}")
            
            # Clear form
            self.clear_form()
            
            # Refresh the list
            self.load_completed_requests()
            
        except Exception as e:
            self.connection.rollback()
            error_msg = str(e)
            
            if "timestamp" in error_msg:
                # Try with timestamp if the error mentions timestamp column
                try:
                    sql = """
                    INSERT INTO Feedback (requestID, victimID, rating, comments, timestamp)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """
                    self.cursor.execute(sql, (request_id, self.logged_in_user.get("id"), rating, comments))
                    self.connection.commit()
                    messagebox.showinfo("✅ Success", "Feedback submitted successfully!")
                    self.clear_form()
                    self.load_completed_requests()
                except Exception as e2:
                    messagebox.showerror("Submission Error", f"Failed to submit feedback.\n\nError: {str(e2)}")
            else:
                messagebox.showerror("Submission Error", f"Failed to submit feedback.\n\nError: {error_msg}")
            
            self.status_label.config(text="❌ Failed to submit feedback")

    def go_back_to_victim_dashboard(self):
        """Go back to VictimDashboardApp"""
        if messagebox.askyesno("Confirm", "Return to Victim Portal?\n\nAny unsaved feedback will be lost."):
            if self.back_command:
                # If a back command is provided, use it
                self.back_command()
            else:
                # Hide this window instead of destroying it
                self.withdraw()  # Hide the window
                
                # Try to import and show VictimDashboard
                try:
                    from frontend.victim_dashboard import VictimDashboardApp
                    victim_dash = VictimDashboardApp(
                        logged_in_user=self.logged_in_user,
                        db_connection=self.connection
                    )
                    victim_dash.mainloop()
                    
                    # When VictimDashboard closes, show this window again
                    self.deiconify()  # Show the window again
                except ImportError:
                    # If VictimDashboard doesn't exist in that path, try different import
                    try:
                        from victim_dashboard import VictimDashboardApp
                        victim_dash = VictimDashboardApp(
                            logged_in_user=self.logged_in_user,
                            db_connection=self.connection
                        )
                        victim_dash.mainloop()
                        self.deiconify()
                    except ImportError:
                        # Try to find the module
                        import sys
                        import os
                        
                        # Add current directory to path
                        sys.path.append(os.getcwd())
                        
                        try:
                            # Try to import from different possible locations
                            try:
                                from src.frontend.victim_dashboard import VictimDashboardApp
                            except ImportError:
                                from frontend.login import VictimDashboardApp
                            
                            victim_dash = VictimDashboardApp(
                                logged_in_user=self.logged_in_user,
                                db_connection=self.connection
                            )
                            victim_dash.mainloop()
                            self.deiconify()
                        except ImportError as e:
                            messagebox.showerror("Error", f"Cannot find VictimDashboard module.\n\nError: {str(e)}")
                            # Close everything
                            self.destroy()

# ------------------ TEST -------------------
if __name__ == "__main__":
    app = GiveFeedbackApp(
        logged_in_user={
            "id": 4,
            "name": "David Smith",
            "role": "Victim",
            "email": "david@victim.com"
        }
    )
    
    app.mainloop()