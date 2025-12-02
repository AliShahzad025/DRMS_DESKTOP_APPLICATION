import tkinter as tk
from tkinter import messagebox, ttk
from data.db_connection import DatabaseConnection

class SOSFormApp(tk.Tk):
    def __init__(self, logged_in_user=None, db_connection=None, back_command=None):
        super().__init__()
        self.logged_in_user = logged_in_user or {}
        self.back_command = back_command
        
        self.title("DRMS - Emergency SOS Request")
        self.geometry("1100x800")
        self.resizable(True, True)
        self.configure(bg="#f5f8fa")
        
        # DB connection
        self.connection = db_connection if db_connection else DatabaseConnection().connect()
        self.cursor = self.connection.cursor(dictionary=True)
        
        self.create_widgets()

    def create_widgets(self):
        # ========== HEADER WITH RED BACK BUTTON ==========
        header = tk.Frame(self, bg="#DC2626", height=100)
        header.pack(fill="x", pady=(0, 20))
        
        header_content = tk.Frame(header, bg="#DC2626")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # RED BACK BUTTON - EXACT SAME AS GIVEFEEDBACKAPP
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
            command=self.go_back_to_victim_dashboard  # EXACT SAME METHOD NAME
        )
        back_btn.pack(side="left", padx=(0, 30))
        
        # Hover effects for back button - EXACT SAME
        def on_enter(e):
            back_btn.config(bg='#FF2222')
        def on_leave(e):
            back_btn.config(bg='#FF4444')
        back_btn.bind("<Enter>", on_enter)
        back_btn.bind("<Leave>", on_leave)

        # Title in header - Modified for SOS
        title_frame = tk.Frame(header_content, bg="#DC2626")
        title_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(
            title_frame,
            text="🚨 EMERGENCY SOS REQUEST",
            font=("Segoe UI", 24, "bold"),
            fg="white",
            bg="#DC2626"
        ).pack(anchor="w")
        
        tk.Label(
            title_frame,
            text="Send immediate help request for life-threatening situations",
            font=("Segoe UI", 12),
            fg="#FECACA",
            bg="#DC2626"
        ).pack(anchor="w", pady=(5, 0))
        
        # Victim info
        victim_name = self.logged_in_user.get('name', 'Victim')
        user_info = tk.Frame(header_content, bg="#DC2626")
        user_info.pack(side="right")
        
        tk.Label(
            user_info,
            text=f"😢 {victim_name} | 🔴 EMERGENCY MODE",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#DC2626",
            justify="right"
        ).pack(side="right")
        
        # ========== MAIN CONTAINER WITH SCROLLBAR ==========
        main_container = tk.Frame(self, bg="#f5f8fa")
        main_container.pack(fill="both", expand=True)
        
        # Create canvas with scrollbar - EXACT SAME PATTERN
        canvas = tk.Canvas(main_container, bg="#f5f8fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f5f8fa")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=30, pady=(0, 20))
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel for scrolling - EXACT SAME
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # ========== FORM CONTENT IN SCROLLABLE FRAME ==========
        # Create two columns
        form_columns = tk.Frame(scrollable_frame, bg="#f5f8fa")
        form_columns.pack(fill="both", expand=True)
        
        left_column = tk.Frame(form_columns, bg="#f5f8fa")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        right_column = tk.Frame(form_columns, bg="#f5f8fa")
        right_column.pack(side="right", fill="both", expand=True, padx=(15, 0))
        
        # ========== LEFT COLUMN: EMERGENCY DETAILS ==========
        emergency_card = tk.Frame(left_column, bg="white", relief="solid", bd=1, padx=30, pady=30)
        emergency_card.pack(fill="both", expand=True)
        
        tk.Label(
            emergency_card,
            text="⚠️ EMERGENCY INFORMATION",
            font=("Segoe UI", 18, "bold"),
            fg="#DC2626",
            bg="white"
        ).pack(anchor="w", pady=(0, 25))
        
        # Location
        tk.Label(
            emergency_card,
            text="📍 YOUR CURRENT LOCATION",
            font=("Segoe UI", 13, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 10))
        
        location_frame = tk.Frame(emergency_card, bg="white")
        location_frame.pack(fill="x", pady=(0, 20))
        
        self.location_var = tk.StringVar(value=self.logged_in_user.get('location', ''))
        location_entry = ttk.Entry(
            location_frame,
            textvariable=self.location_var,
            font=("Segoe UI", 12),
            width=40
        )
        location_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Get Current Location Button
        location_btn = tk.Button(
            location_frame,
            text="📍 Use Saved Location",
            font=("Segoe UI", 10),
            bg="#3B82F6",
            fg="white",
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.use_saved_location
        )
        location_btn.pack(side="right")
        
        # Coordinates
        coords_frame = tk.Frame(emergency_card, bg="white")
        coords_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            coords_frame,
            text="🌐 COORDINATES (Latitude, Longitude)",
            font=("Segoe UI", 13, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 10))
        
        coords_input_frame = tk.Frame(coords_frame, bg="white")
        coords_input_frame.pack(fill="x")
        
        tk.Label(
            coords_input_frame,
            text="Latitude:",
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white"
        ).pack(side="left", padx=(0, 10))
        
        self.lat_var = tk.StringVar(value=str(self.logged_in_user.get('latitude', '')) if self.logged_in_user.get('latitude') else "")
        lat_entry = ttk.Entry(
            coords_input_frame,
            textvariable=self.lat_var,
            font=("Segoe UI", 11),
            width=15
        )
        lat_entry.pack(side="left", padx=(0, 20))
        
        tk.Label(
            coords_input_frame,
            text="Longitude:",
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white"
        ).pack(side="left", padx=(0, 10))
        
        self.long_var = tk.StringVar(value=str(self.logged_in_user.get('longitude', '')) if self.logged_in_user.get('longitude') else "")
        long_entry = ttk.Entry(
            coords_input_frame,
            textvariable=self.long_var,
            font=("Segoe UI", 11),
            width=15
        )
        long_entry.pack(side="left")
        
        # Emergency Type
        tk.Label(
            emergency_card,
            text="🚨 TYPE OF EMERGENCY",
            font=("Segoe UI", 13, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 10))
        
        emergency_types = [
            ("Medical Emergency", "🚑"),
            ("Trapped/Rescue Needed", "🏗️"),
            ("Fire Hazard", "🔥"),
            ("Flood/Water Emergency", "💧"),
            ("Structural Collapse", "🏚️"),
            ("Missing Person", "👤"),
            ("Other Life-Threatening", "⚠️")
        ]
        
        self.emergency_var = tk.StringVar(value="Medical Emergency")
        
        for i, (etype, icon) in enumerate(emergency_types):
            frame = tk.Frame(emergency_card, bg="white")
            frame.pack(fill="x", pady=5)
            
            rb = tk.Radiobutton(
                frame,
                text=f"{icon} {etype}",
                variable=self.emergency_var,
                value=etype,
                font=("Segoe UI", 11),
                fg="#374151",
                bg="white",
                selectcolor="#FEE2E2",
                activebackground="white",
                cursor="hand2"
            )
            rb.pack(side="left")
        
        # Urgency Level
        tk.Label(
            emergency_card,
            text="⚡ URGENCY LEVEL",
            font=("Segoe UI", 13, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(20, 10))
        
        urgency_frame = tk.Frame(emergency_card, bg="white")
        urgency_frame.pack(fill="x", pady=(0, 10))
        
        self.urgency_var = tk.StringVar(value="critical")
        
        urgency_levels = [
            ("critical", "🔴 CRITICAL", "Life-threatening, immediate danger"),
            ("high", "🟠 HIGH", "Severe, needs quick response"),
            ("medium", "🟡 MEDIUM", "Serious but stable"),
            ("low", "🟢 LOW", "Non-life-threatening")
        ]
        
        for level, label, desc in urgency_levels:
            level_frame = tk.Frame(urgency_frame, bg="white")
            level_frame.pack(fill="x", pady=3)
            
            rb = tk.Radiobutton(
                level_frame,
                text=label,
                variable=self.urgency_var,
                value=level,
                font=("Segoe UI", 11, "bold"),
                fg="#DC2626" if level == "critical" else "#F59E0B",
                bg="white",
                selectcolor="#FEE2E2",
                activebackground="white",
                cursor="hand2"
            )
            rb.pack(side="left", padx=(0, 15))
            
            tk.Label(
                level_frame,
                text=desc,
                font=("Segoe UI", 10),
                fg="#6B7280",
                bg="white"
            ).pack(side="left")
        
        # ========== RIGHT COLUMN: DETAILS & PEOPLE ==========
        details_card = tk.Frame(right_column, bg="white", relief="solid", bd=1, padx=30, pady=30)
        details_card.pack(fill="both", expand=True)
        
        tk.Label(
            details_card,
            text="📝 EMERGENCY DETAILS",
            font=("Segoe UI", 18, "bold"),
            fg="#1E40AF",
            bg="white"
        ).pack(anchor="w", pady=(0, 25))
        
        # Number of People - FIXED VERSION
        tk.Label(
            details_card,
            text="👥 NUMBER OF PEOPLE AFFECTED",
            font=("Segoe UI", 13, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 10))
        
        people_frame = tk.Frame(details_card, bg="white")
        people_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            people_frame,
            text="Total people needing help:",
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white"
        ).pack(side="left", padx=(0, 10))
        
        # Use StringVar with validation
        self.people_var = tk.StringVar(value="1")
        
        # Create custom spinbox that only accepts numbers
        people_spin_frame = tk.Frame(people_frame, bg="white")
        people_spin_frame.pack(side="left")
        
        # Decrease button
        dec_btn = tk.Button(
            people_spin_frame,
            text="-",
            font=("Segoe UI", 10),
            bg="#D1D5DB",
            fg="black",
            width=3,
            command=lambda: self.adjust_people(-1)
        )
        dec_btn.pack(side="left")
        
        # Entry for number
        people_entry = ttk.Entry(
            people_spin_frame,
            textvariable=self.people_var,
            font=("Segoe UI", 11),
            width=8,
            justify="center"
        )
        people_entry.pack(side="left", padx=5)
        
        # Increase button
        inc_btn = tk.Button(
            people_spin_frame,
            text="+",
            font=("Segoe UI", 10),
            bg="#D1D5DB",
            fg="black",
            width=3,
            command=lambda: self.adjust_people(1)
        )
        inc_btn.pack(side="left")
        
        # Validate that only numbers can be entered
        def validate_numeric(P):
            if P == "" or P.isdigit():
                return True
            return False
        
        vcmd = (self.register(validate_numeric), '%P')
        people_entry.config(validate="key", validatecommand=vcmd)
        
        # Vulnerable people
        tk.Label(
            details_card,
            text="👶 VULNERABLE INDIVIDUALS",
            font=("Segoe UI", 13, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(0, 10))
        
        vulnerable_frame = tk.Frame(details_card, bg="white")
        vulnerable_frame.pack(fill="x", pady=(0, 20))
        
        self.vulnerable_vars = {
            "children": tk.BooleanVar(value=False),
            "elderly": tk.BooleanVar(value=False),
            "disabled": tk.BooleanVar(value=False),
            "pregnant": tk.BooleanVar(value=False),
            "injured": tk.BooleanVar(value=False)
        }
        
        vulnerable_options = [
            ("👶 Children (under 12)", "children"),
            ("👵 Elderly (65+)", "elderly"),
            ("♿ Disabled/Handicapped", "disabled"),
            ("🤰 Pregnant Women", "pregnant"),
            ("🤕 Injured/Critical", "injured")
        ]
        
        for i, (label, key) in enumerate(vulnerable_options):
            cb = tk.Checkbutton(
                vulnerable_frame,
                text=label,
                variable=self.vulnerable_vars[key],
                font=("Segoe UI", 11),
                fg="#374151",
                bg="white",
                selectcolor="#FEE2E2",
                activebackground="white",
                cursor="hand2"
            )
            cb.pack(anchor="w", pady=3)
        
        # Emergency Description
        tk.Label(
            details_card,
            text="📋 EMERGENCY DESCRIPTION",
            font=("Segoe UI", 13, "bold"),
            fg="#374151",
            bg="white"
        ).pack(anchor="w", pady=(20, 10))
        
        tk.Label(
            details_card,
            text="Please describe the emergency in detail:",
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white"
        ).pack(anchor="w", pady=(0, 10))
        
        # Description text box with scrollbar
        desc_frame = tk.Frame(details_card, bg="white")
        desc_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        self.desc_text = tk.Text(
            desc_frame,
            height=8,
            font=("Segoe UI", 11),
            wrap="word",
            relief="solid",
            borderwidth=1,
            padx=10,
            pady=10
        )
        self.desc_text.pack(side="left", fill="both", expand=True)
        
        desc_scrollbar = ttk.Scrollbar(desc_frame, command=self.desc_text.yview)
        desc_scrollbar.pack(side="right", fill="y")
        self.desc_text.config(yscrollcommand=desc_scrollbar.set)
        
        # Placeholder text
        self.desc_text.insert("1.0", "Describe the emergency situation, injuries, immediate dangers, and any other critical information...")
        self.desc_text.config(fg="gray")
        
        def on_focus_in(event):
            if self.desc_text.get("1.0", "end-1c") == "Describe the emergency situation, injuries, immediate dangers, and any other critical information...":
                self.desc_text.delete("1.0", tk.END)
                self.desc_text.config(fg="black")
        
        def on_focus_out(event):
            if not self.desc_text.get("1.0", "end-1c").strip():
                self.desc_text.insert("1.0", "Describe the emergency situation, injuries, immediate dangers, and any other critical information...")
                self.desc_text.config(fg="gray")
        
        self.desc_text.bind("<FocusIn>", on_focus_in)
        self.desc_text.bind("<FocusOut>", on_focus_out)
        
        # ========== SUBMIT BUTTONS ==========
        button_frame = tk.Frame(scrollable_frame, bg="#f5f8fa")
        button_frame.pack(fill="x", pady=(30, 20))
        
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
            padx=25,
            pady=12,
            cursor="hand2",
            command=self.clear_form
        )
        clear_btn.pack(side="left", padx=(30, 20))
        
        # Emergency Submit Button
        self.submit_btn = tk.Button(
            button_frame,
            text="🚨 SEND EMERGENCY SOS",
            font=("Segoe UI", 14, "bold"),
            bg="#DC2626",
            fg="white",
            activebackground="#B91C1C",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=40,
            pady=15,
            cursor="hand2",
            command=self.submit_sos
        )
        self.submit_btn.pack(side="left")
        
        # ========== FOOTER ==========
        footer_frame = tk.Frame(self, bg="#333", height=40)
        footer_frame.pack(fill="x", side="bottom")
        
        # Status label
        self.status_label = tk.Label(
            footer_frame,
            text="⚠️ FILL OUT ALL EMERGENCY DETAILS | Your SOS will be sent immediately to emergency responders",
            fg="white",
            bg="#333",
            font=("Segoe UI", 10)
        )
        self.status_label.pack(side="left", padx=20)
        
        # Warning label
        warning_label = tk.Label(
            footer_frame,
            text="🚨 This is for REAL emergencies only! Misuse may delay help for others.",
            fg="#FECACA",
            bg="#333",
            font=("Segoe UI", 9, "bold")
        )
        warning_label.pack(side="right", padx=20)

    def adjust_people(self, change):
        """Adjust number of people with +/- buttons"""
        try:
            current = int(self.people_var.get() or "1")
            new_value = max(1, current + change)
            self.people_var.set(str(new_value))
        except:
            self.people_var.set("1")

    def use_saved_location(self):
        """Use victim's saved location"""
        saved_location = self.logged_in_user.get('location', '')
        saved_lat = self.logged_in_user.get('latitude', '')
        saved_long = self.logged_in_user.get('longitude', '')
        
        if saved_location:
            self.location_var.set(saved_location)
        if saved_lat:
            self.lat_var.set(str(saved_lat))
        if saved_long:
            self.long_var.set(str(saved_long))
        
        self.status_label.config(text="✅ Using your saved location information")

    def clear_form(self):
        """Clear the SOS form"""
        self.location_var.set("")
        self.lat_var.set("")
        self.long_var.set("")
        self.emergency_var.set("Medical Emergency")
        self.urgency_var.set("critical")
        self.people_var.set("1")
        
        # Clear checkboxes
        for var in self.vulnerable_vars.values():
            var.set(False)
        
        # Clear description
        self.desc_text.delete("1.0", tk.END)
        self.desc_text.insert("1.0", "Describe the emergency situation, injuries, immediate dangers, and any other critical information...")
        self.desc_text.config(fg="gray")
        
        self.status_label.config(text="✅ Form cleared. Ready for new emergency report")

    def submit_sos(self):
        """Submit SOS emergency request"""
        # Get form data
        location = self.location_var.get().strip()
        lat = self.lat_var.get().strip()
        long = self.long_var.get().strip()
        emergency_type = self.emergency_var.get()
        urgency = self.urgency_var.get()
        
        # Get number of people with error handling
        try:
            num_people = int(self.people_var.get() or "1")
            if num_people < 1:
                num_people = 1
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for people affected.")
            self.status_label.config(text="❌ Invalid number of people")
            return
        
        # Get vulnerable info
        vulnerable_list = []
        for key, var in self.vulnerable_vars.items():
            if var.get():
                vulnerable_list.append(key)
        
        # Get description
        description = self.desc_text.get("1.0", tk.END).strip()
        if description == "Describe the emergency situation, injuries, immediate dangers, and any other critical information...":
            description = ""
        
        # Validation
        if not location:
            messagebox.showerror("Missing Information", "Please enter your location.")
            self.status_label.config(text="❌ Location is required")
            return
        
        if not lat or not long:
            result = messagebox.askyesno("Coordinates Missing", 
                "Coordinates are recommended for accurate emergency response.\n\n"
                "Do you want to continue without coordinates?")
            if not result:
                self.status_label.config(text="❌ Please provide coordinates")
                return
        
        if not emergency_type:
            messagebox.showerror("Missing Information", "Please select the type of emergency.")
            self.status_label.config(text="❌ Emergency type is required")
            return
        
        if not description:
            result = messagebox.askyesno("Description Missing",
                "Detailed description helps responders prepare better.\n\n"
                "Do you want to continue without description?")
            if not result:
                self.status_label.config(text="❌ Please provide emergency description")
                return
        
        # Confirm submission
        confirm_msg = f"""
🚨 CONFIRM EMERGENCY SOS REQUEST

📍 Location: {location}
🚨 Emergency Type: {emergency_type}
⚡ Urgency Level: {urgency.upper()}
👥 People Affected: {num_people}

⚠️ WARNING: This will notify all emergency responders immediately.

Do you confirm this is a REAL emergency?"""
        
        if not messagebox.askyesno("CONFIRM EMERGENCY SOS", confirm_msg, icon='warning'):
            self.status_label.config(text="❌ SOS submission cancelled")
            return
        
        try:
            self.status_label.config(text="⏳ Sending emergency SOS...")
            self.update()
            
            # Convert coordinates to float if provided
            latitude = float(lat) if lat else None
            longitude = float(long) if long else None
            
            # Get victim ID
            victim_id = self.logged_in_user.get('id')
            
            # Insert into SOSRequest table
            sql = """
            INSERT INTO SOSRequest 
            (victimID, location, latitude, longitude, typeOfNeed, description, urgencyLevel, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
            """
            
            self.cursor.execute(sql, (
                victim_id,
                location,
                latitude,
                longitude,
                emergency_type,
                f"People affected: {num_people}. Vulnerable: {', '.join(vulnerable_list) if vulnerable_list else 'None'}. Details: {description}",
                urgency
            ))
            
            request_id = self.cursor.lastrowid
            
            # Insert into Notification table to alert responders
            notify_sql = """
            INSERT INTO Notification 
            (message, channel, recipientUserID, recipientRole, status)
            VALUES 
            (%s, 'in_app', NULL, 'Admin', 'sent'),
            (%s, 'in_app', NULL, 'Volunteer', 'sent'),
            (%s, 'in_app', NULL, 'NGO', 'sent')
            """
            
            emergency_msg = f"🚨 NEW SOS REQUEST #{request_id}: {emergency_type} at {location}. Urgency: {urgency}"
            
            self.cursor.execute(notify_sql, (emergency_msg, emergency_msg, emergency_msg))
            
            self.connection.commit()
            
            # Success message
            success_msg = f"""
✅ EMERGENCY SOS SENT SUCCESSFULLY!

📋 Request ID: {request_id}
📍 Location: {location}
🚨 Type: {emergency_type}
⚡ Urgency: {urgency.upper()}

⚠️ Emergency responders have been notified.
📞 Stay by your phone for updates.
🚑 Help is on the way!

Your request status: PENDING ASSIGNMENT"""
            
            messagebox.showinfo("🚨 SOS REQUEST SENT", success_msg)
            
            self.status_label.config(text=f"✅ Emergency SOS #{request_id} sent successfully")
            
            # Clear form
            self.clear_form()
            
            # Ask if user wants to go back to dashboard
            if messagebox.askyesno("Return to Dashboard", "SOS sent successfully!\n\nReturn to Victim Dashboard?"):
                self.go_back_to_victim_dashboard()
            
        except ValueError as ve:
            messagebox.showerror("Invalid Coordinates", f"Please enter valid latitude and longitude numbers.\n\nError: {str(ve)}")
            self.status_label.config(text="❌ Invalid coordinates format")
            self.connection.rollback()
        except Exception as e:
            messagebox.showerror("Submission Error", f"Failed to send SOS request.\n\nError: {str(e)}")
            self.status_label.config(text="❌ Failed to send SOS")
            self.connection.rollback()

    def go_back_to_victim_dashboard(self):
        """Go back to VictimDashboardApp - EXACT COPY FROM GIVEFEEDBACKAPP"""
        if messagebox.askyesno("Confirm", "Return to Victim Portal?\n\nAny unsaved SOS data will be lost."):
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
    app = SOSFormApp(
        logged_in_user={
            "id": 4,
            "name": "David Smith",
            "role": "Victim",
            "email": "david@victim.com",
            "location": "East Side Home",
            "latitude": 34.0550,
            "longitude": -118.2470
        }
    )
    
    app.mainloop()