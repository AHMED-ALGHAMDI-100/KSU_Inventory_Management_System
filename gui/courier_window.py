import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from services.courier_manager import CourierManager  # Required for business logic


class CourierWindow(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        # User ID is received from the controller during successful login
        self.courier_id = None

        # --- Configure Grid for Layout ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Title Bar and Logout ---
        title_frame = ctk.CTkFrame(self, height=50)
        title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        title_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(title_frame, text="KSU Courier Operations Hub", font=("Arial", 20, "bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Logout button (Requirement: return to Sign up window)
        logout_btn = ctk.CTkButton(title_frame, text="Logout", command=self.logout)
        logout_btn.grid(row=0, column=1, padx=20, pady=10, sticky="e")

        # --- Tabs Setup ---
        # CTkTabview implements the required tabs structure
        self.notebook = ctk.CTkTabview(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Tabs based on project requirements
        self.notebook.add("Pick Up Request (Inventory)")
        self.notebook.add("Deliver to College")
        self.notebook.add("Pick Up Return (College)")
        self.notebook.add("Deliver Return (Inventory)")

        # --- Build Tabs ---
        # The create_action_tab function is generalized to build all four workflow steps quickly.
        self.create_action_tab(
            "Pick Up Request (Inventory)",
            "Enter 16-digit Request ID to confirm pickup from KSU Inventory:",
            CourierManager.pickup_request
        )
        self.create_action_tab(
            "Deliver to College",
            "Enter Request ID to confirm delivery to College:",
            CourierManager.deliver_request
        )
        self.create_action_tab(
            "Pick Up Return (College)",
            "Enter 16-digit Return ID to confirm pickup from College:",
            CourierManager.pickup_return
        )
        self.create_action_tab(
            "Deliver Return (Inventory)",
            "Enter Return ID to confirm delivery to KSU Inventory:",
            CourierManager.deliver_return
        )

    def logout(self):
        """Destroys the current window and returns to the Sign Up screen."""
        self.controller.show_frame("SignUpWindow")

    def create_action_tab(self, title, label_text, action_func):
        """
        Creates a standardized tab for one of the four required courier actions.
        """
        frame = self.notebook.tab(title)
        frame.columnconfigure(0, weight=1)

        # UI Elements using CTk
        ctk.CTkLabel(frame, text=label_text, font=("Arial", 14)).pack(pady=20)

        entry_id = ctk.CTkEntry(frame, width=300, font=("Arial", 14))
        entry_id.pack(pady=5)

        # Error/Status Label
        status_label = ctk.CTkLabel(frame, text="", text_color="red")
        status_label.pack(pady=5)

        def on_click():
            req_id = entry_id.get()

            # Simple validation check for 16-digit IDs
            if not req_id or (len(req_id) != 16 or not req_id.isdigit()):
                CTkMessagebox(title="Error", message="Please enter the 16-digit Request/Return ID.", icon="cancel")
                return

            # Call the passed service function
            # We assume action_func returns (success: bool, message: str)
            success, msg = action_func(req_id, self.courier_id)

            if success:
                CTkMessagebox(title="Success", message=msg, icon="check")
                entry_id.delete(0, 'end')
                status_label.configure(text="")
            else:
                CTkMessagebox(title="Error", message=msg, icon="cancel")
                status_label.configure(text=msg, text_color="red")

        ctk.CTkButton(frame, text="Confirm Action", command=on_click, fg_color="#0056b3").pack(pady=20)