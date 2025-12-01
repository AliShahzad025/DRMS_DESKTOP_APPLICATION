import tkinter as tk
from tkinter import messagebox

class LanguageManager:
    def __init__(self):
        self.current_language = "english"

        self.languages = {
            "english": {
                # Login & general
                "login_title": "Login",
                "system_name": "Disaster Relief Management System",
                "email": "Email",
                "password": "Password",
                "role": "Select Role",
                "login_button": "Login",
                "welcome": "Welcome",
                "login_success_title": "Login Successful",
                "login_failed_title": "Login Failed",
                "login_invalid": "Invalid credentials or role.",
                "login_missing_fields": "Please enter both email and password.",
                "login_error_title": "Error",
                "login_error_message": "An error occurred:",
                "admin_options": "Admin Options",
                "generate_reports": "Generate Reports",
                "notify_stakeholders": "Notify Stakeholders",
                "language_settings": "Language Settings",
                "select_language_title": "Select Language",
                "select_language_prompt": "Enter language (english / urdu):",
                "language_changed_title": "Success",
                "language_changed_message": "Language updated successfully!",
                "language_error_title": "Not Available",
                "language_error_message": "Language not supported.",
                "copyright": "© 2025 DRMS",

                # Generate Reports
                "select_report_type": "Select Report Type:",
                "generate_report": "Generate Report",
                "print_report": "Print Report",
                "invalid_report_title": "Invalid Report",
                "invalid_report_message": "Please select a valid report type.",
                "no_data_title": "No Data",
                "no_data_message": "No data available for {role} report.",
                "error_title": "Error",
                "error_message": "An error occurred:",
                "print_error_title": "Print Error",
                "print_error_message": "No report generated or failed to print.",
                "save_report_title": "Save Report as PDF",
                "print_success_title": "Success",
                "print_success_message": "Report saved as PDF successfully!",
                "report": "Report"
            },

            "urdu": {
                # Login & general
                "login_title": "لاگ ان",
                "system_name": "ڈیزاسٹر ریلیف مینجمنٹ سسٹم",
                "email": "ای میل",
                "password": "پاس ورڈ",
                "role": "کردار منتخب کریں",
                "login_button": "لاگ ان",
                "welcome": "خوش آمدید",
                "login_success_title": "کامیاب",
                "login_failed_title": "ناکام",
                "login_invalid": "غلط معلومات یا کردار۔",
                "login_missing_fields": "براہ کرم ای میل اور پاس ورڈ درج کریں۔",
                "login_error_title": "غلطی",
                "login_error_message": "ایک خرابی پیش آئی:",
                "admin_options": "ایڈمن آپشنز",
                "generate_reports": "رپورٹس بنائیں",
                "notify_stakeholders": "اسٹیک ہولڈرز کو اطلاع دیں",
                "language_settings": "زبان کی ترتیبات",
                "select_language_title": "زبان منتخب کریں",
                "select_language_prompt": "زبان درج کریں (english / urdu):",
                "language_changed_title": "کامیابی",
                "language_changed_message": "زبان کامیابی سے تبدیل ہوگئی!",
                "language_error_title": "دستیاب نہیں",
                "language_error_message": "یہ زبان موجود نہیں ہے۔",
                "copyright": "© 2025 DRMS",

                # Generate Reports
                "select_report_type": "رپورٹ کی قسم منتخب کریں:",
                "generate_report": "رپورٹ بنائیں",
                "print_report": "رپورٹ پرنٹ کریں",
                "invalid_report_title": "غلط رپورٹ",
                "invalid_report_message": "براہ کرم درست رپورٹ منتخب کریں۔",
                "no_data_title": "کوئی ڈیٹا نہیں",
                "no_data_message": "{role} کی رپورٹ کے لیے کوئی ڈیٹا دستیاب نہیں۔",
                "error_title": "خرابی",
                "error_message": "ایک خرابی پیش آئی:",
                "print_error_title": "پرنٹ خرابی",
                "print_error_message": "کوئی رپورٹ تیار نہیں یا پرنٹ کرنے میں ناکام۔",
                "save_report_title": "رپورٹ کو PDF کے طور پر محفوظ کریں",
                "print_success_title": "کامیابی",
                "print_success_message": "رپورٹ کامیابی سے PDF میں محفوظ ہوگئی!",
                "report": "رپورٹ"
            }
        }

    # Get translation
    def get(self, key):
        return self.languages[self.current_language].get(key, key)

    # Change language
    def set_language(self, lang):
        if lang in self.languages:
            self.current_language = lang
            return True
        return False
