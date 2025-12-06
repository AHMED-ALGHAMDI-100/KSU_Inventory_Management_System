import customtkinter as ctk
from models.user import User  # Used for DB interaction (check_if_registered, create_user)
from config.validation import validate_signup_inputs  # Used for format checking
from CTkMessagebox import CTkMessagebox


class SignUpWindow(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        # --- Configure Grid for Layout ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Container for the Login/Signup Forms ---
        self.form_container = ctk.CTkFrame(self, width=800)
        self.form_container.grid(row=0, column=0, padx=50, pady=50)

        # --- Initial State: Draw Login Form ---
        self.draw_login_form()

    def clear_form_container(self):
        """Destroys all widgets currently in the form_container."""
        for widget in self.form_container.winfo_children():
            widget.destroy()

    # --- UI Drawing Functions ---

    def draw_login_form(self):
        """
        Draws the fields for the Login window. (Requirement: Login window)
        """
        self.clear_form_container()
        self.form_container.configure(fg_color=("white", "gray20"))

        # --- Title ---
        title = ctk.CTkLabel(self.form_container, text="KSU Inventory Login", font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(20, 30))

        # --- Input Fields ---
        # ID Field (User enters his/her ID)
        ctk.CTkLabel(self.form_container, text="ID Number (6 Digits):").grid(row=1, column=0, padx=10, pady=5,
                                                                             sticky="w")
        self.login_id_entry = ctk.CTkEntry(self.form_container, width=200)
        self.login_id_entry.grid(row=1, column=1, padx=10, pady=5)

        # Password Field (User enters his/her password)
        ctk.CTkLabel(self.form_container, text="Password:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.login_password_entry = ctk.CTkEntry(self.form_container, width=200, show="*")  # Hides password input
        self.login_password_entry.grid(row=2, column=1, padx=10, pady=5)

        # --- Error Label ---
        self.login_error_label = ctk.CTkLabel(self.form_container, text="", text_color="red")
        self.login_error_label.grid(row=3, column=0, columnspan=2, pady=5)

        # --- Buttons ---
        login_btn = ctk.CTkButton(self.form_container, text="Login", command=self.handle_login)
        login_btn.grid(row=4, column=0, columnspan=2, pady=10)

        # Switch button (Requirement: Navigating to Sign-up)
        signup_switch_btn = ctk.CTkButton(self.form_container, text="Sign Up", command=self.draw_signup_form)
        signup_switch_btn.grid(row=5, column=0, columnspan=2, pady=(10, 20))

    def draw_signup_form(self):
        """
        Draws the fields for the Sign Up window. (Requirement: Sign up window)
        """
        self.clear_form_container()
        self.form_container.configure(fg_color=("white", "gray20"))

        # --- Title ---
        title = ctk.CTkLabel(self.form_container, text="KSU User Sign Up", font=("Arial", 20, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(20, 20))

        # --- Input Fields (Requirements: First Name, Last Name, ID, Password, Email, Phone) ---
        fields = [
            ("First Name", "first_name_entry", 1, False),
            ("Last Name", "last_name_entry", 2, False),
            ("ID Number (6 Digits)", "id_entry", 3, False),
            ("Password (Min 6 Chars)", "password_entry", 4, True),
            ("Email (user@ksu.edu.sa)", "email_entry", 5, False),
            ("Phone (05XXXXXXXX)", "phone_entry", 6, False),
        ]

        self.signup_entries = {}
        for text, attr_name, row, is_password in fields:
            ctk.CTkLabel(self.form_container, text=text + ":").grid(row=row, column=0, padx=10, pady=5, sticky="w")
            entry = ctk.CTkEntry(self.form_container, width=200, show="*" if is_password else "")
            entry.grid(row=row, column=1, padx=10, pady=5)
            self.signup_entries[attr_name] = entry

        # --- User Class Dropdown (Requirement: User Class) ---
        ctk.CTkLabel(self.form_container, text="User Class:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self.user_class_var = ctk.StringVar(value="College")  # Default selection
        self.user_class_dropdown = ctk.CTkOptionMenu(
            self.form_container,
            variable=self.user_class_var,
            values=["College", "Courier", "Inventory Manager"]
        )
        self.user_class_dropdown.grid(row=7, column=1, padx=10, pady=5)

        # --- Error Label ---
        self.signup_error_label = ctk.CTkLabel(self.form_container, text="", text_color="red")
        self.signup_error_label.grid(row=8, column=0, columnspan=2, pady=5)

        # --- Buttons ---
        submit_btn = ctk.CTkButton(self.form_container, text="Submit", command=self.handle_signup)
        submit_btn.grid(row=9, column=0, columnspan=2, pady=10)  # Submit button: sends user info to central DB

        # Switch button (Requirement: Login button opens Login window and destroys current)
        login_switch_btn = ctk.CTkButton(self.form_container, text="Login", command=self.draw_login_form)
        login_switch_btn.grid(row=10, column=0, columnspan=2, pady=(10, 20))

    # --- Authentication Handlers ---

    def handle_signup(self):
        """
        Handles the Sign Up button click: Validation, DB checks, and user creation.
        """
        # 1. Collect Data
        data = {
            'first_name': self.signup_entries['first_name_entry'].get(),
            'last_name': self.signup_entries['last_name_entry'].get(),
            'id': self.signup_entries['id_entry'].get(),
            'password': self.signup_entries['password_entry'].get(),
            'email': self.signup_entries['email_entry'].get(),
            'phone_number': self.signup_entries['phone_entry'].get(),
            'user_class': self.user_class_var.get()
        }

        # 2. Run Input Format Validation (Requirement: Input validation mechanism)
        format_errors = validate_signup_inputs(data)

        if format_errors:
            # Display error messages (Requirement: error message should appear)
            error_msg = "\n".join(format_errors.values())
            self.signup_error_label.configure(text=error_msg)
            return

        # 3. Check for Duplicate Registration
        if User.check_if_registered(data['id']):
            # Requirement: Display error if user has been already registered
            self.signup_error_label.configure(text="Error: User ID is already registered.")
            return

        # 4. Create User Securely (Hashes password and inserts into Railway DB)
        if User.create_user(data):
            # Success
            self.signup_error_label.configure(text="Registration Successful! Please log in.", text_color="green")
            # Clear fields and switch to a login window
            self.draw_login_form()
        else:
            # Failed insertion due to database error (e.g., integrity error)
            self.signup_error_label.configure(text="Registration failed due to a server error.", text_color="red")

    def handle_login(self):
        """
        Handles the Login button click: Validation, DB check, and forwarding.
        """
        user_id = self.login_id_entry.get()
        password = self.login_password_entry.get()

        # 1. Basic validation check (ID is digits, password length)
        # Note: We can reuse the validation file functions here if desired
        if len(user_id) != 6 or not user_id.isdigit():
            self.login_error_label.configure(text="Error: ID must be 6 digits.")
            return
        if len(password) < 6:
            self.login_error_label.configure(text="Error: Password minimum 6 characters.")
            return

        # 2. Authenticate User (Connects to DB and checks hash)
        user_class = User.authenticate_user(user_id, password)

        if user_class:
            # Success (Requirement: Forwarding window based on user class)
            self.login_error_label.configure(text="Login Successful!", text_color="green")

            # Forwarding logic
            if user_class == 'Inventory Manager':
                self.controller.show_frame("ManagerWindow", user_id=user_id)  # Manager Window
            elif user_class == 'College':
                self.controller.show_frame("CollegeWindow", user_id=user_id)  # College Window
            elif user_class == 'Courier':
                self.controller.show_frame("CourierWindow", user_id=user_id)  # Courier Window

        else:
            # Failure (Requirement: Display error message on failure)
            self.login_error_label.configure(text="Login Failed: Invalid ID or Password.", text_color="red")