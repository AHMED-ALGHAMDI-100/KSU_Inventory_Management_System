
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox  # For clean success/error messages

from services.request_manager import RequestManager
from models.inventory_item import InventoryItem
from models.college import College


# Note: In a real Tkinter setup, College model would be used by the College user.

class CollegeWindow(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        # user_id is passed during successful login via the controller
        self.user_id = None

        # --- Configure Grid for Layout ---
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Title Bar and Logout ---
        title_frame = ctk.CTkFrame(self, height=50)
        title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        title_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(title_frame, text="KSU College Inventory Hub", font=("Arial", 20, "bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Logout button (Requirement: return to Sign up window)
        logout_btn = ctk.CTkButton(title_frame, text="Logout", command=self.logout)
        logout_btn.grid(row=0, column=1, padx=20, pady=10, sticky="e")

        # --- Tabs Setup ---
        # CTkTabview is the modern replacement for ttk.Notebook
        self.notebook = ctk.CTkTabview(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Tabs based on project requirements
        self.notebook.add("Request Item")
        self.notebook.add("My Requests")
        self.notebook.add("Return Item")
        self.notebook.add("My Returns")

        # --- Build Tabs ---
        self.setup_request_tab()
        self.setup_my_requests_tab()
        self.setup_return_tab()
        self.setup_my_returns_tab()

    def logout(self):
        """Destroys the current window and returns to the Sign Up screen."""
        # Use controller to switch frame back to SignUpWindow
        self.controller.show_frame("SignUpWindow")

    def refresh_tables(self):
        """Method to reload data in the tables after a successful transaction."""
        # Note: Implementation of load_my_requests/returns needed here
        pass

    # ---------------- TAB 1: Request Item ----------------
    def setup_request_tab(self):
        """Sets up the UI for submitting an item request."""
        tab = self.notebook.tab("Request Item")
        tab.grid_columnconfigure(1, weight=1)  # Makes the entry column expand

        # Title
        ctk.CTkLabel(tab, text="Initiate New Item Request", font=("Arial", 16)).grid(row=0, column=0, columnspan=2,
                                                                                     pady=(10, 20))

        # --- Input Fields ---

        # Item Catalog Dropdown (Requirement: Select Item from catalog)
        ctk.CTkLabel(tab, text="Select Item:").grid(row=1, column=0, padx=10, pady=5, sticky='w')

        # NOTE: Implement InventoryItem.get_catalog() in models/inventory_item.py first
        try:
            # Assuming get_catalog() returns a list of objects/tuples
            self.catalog_items = InventoryItem.get_catalog()
            item_names = [f"{item.id} - {item.name} ({item.unit})" for item in self.catalog_items]  # Assumes ID, Name, Unit
        except Exception:
            item_names = ["No Items Available"]

        self.combo_items = ctk.CTkComboBox(tab, values=item_names, width=300)
        self.combo_items.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        # Quantity (Requirement: enter Quantity)
        ctk.CTkLabel(tab, text="Quantity:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.entry_qty = ctk.CTkEntry(tab, width=300)
        self.entry_qty.grid(row=2, column=1, padx=10, pady=5, sticky='ew')

        # Purpose/Notes (Requirement: Purpose/Notes)
        ctk.CTkLabel(tab, text="Purpose_notes:").grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self.entry_purpose = ctk.CTkEntry(tab, width=300)
        self.entry_purpose.grid(row=3, column=1, padx=10, pady=5, sticky='ew')

        # Submit Button
        btn_submit = ctk.CTkButton(tab, text="Submit Request", command=self.submit_request, fg_color="green")
        btn_submit.grid(row=4, column=1, pady=30, sticky='e')

    def submit_request(self):
        """Handles item request submission logic."""
        # 1. Get Data
        selection = self.combo_items.get()
        qty_str = self.entry_qty.get()
        purpose = self.entry_purpose.get()

        if not selection or not qty_str or not purpose:
            CTkMessagebox(title="Error", message="All fields are required!", icon="cancel")
            return

        # Validation for Quantity
        try:
            qty = int(qty_str)
            if qty <= 0: raise ValueError
        except ValueError:
            CTkMessagebox(title="Error", message="Quantity must be a positive number.", icon="cancel")
            return

        # Extract Item ID from selection string "ID - Item Name..."
        try:
            item_id = int(selection.split(' - ')[0])
        except ValueError:
            CTkMessagebox(title="Error", message="Please select a valid item from the list.", icon="cancel")
            return

        # 2. Call Service (Requirement: Initiate request, type='Request')
        # NOTE: We assume RequestManager.create_request exists
        if RequestManager.create_request(self.user_id, item_id, qty, purpose, 'Request'):
            CTkMessagebox(title="Success", message="Request Submitted Successfully!", icon="check")
            # self.refresh_tables() # Refresh the My Requests tab
        else:
            CTkMessagebox(title="Error", message="Failed to submit request. Check server connection.", icon="cancel")

    # ---------------- TAB 2: My Requests (Placeholder) ----------------
    def setup_my_requests_tab(self):
        """Placeholder for viewing list of requests and their status."""
        tab = self.notebook.tab("My Requests")
        ctk.CTkLabel(tab, text="List all requests with Status (Pending, Approved, Rejected, etc.)").pack(pady=50)

    # ---------------- TAB 3: Return Item (Placeholder) ----------------
    def setup_return_tab(self):
        """Placeholder for initiating item returns."""
        tab = self.notebook.tab("Return Item")
        ctk.CTkLabel(tab, text="Initiate Return for items currently in college custody").pack(pady=50)

    # ---------------- TAB 4: My Returns (Placeholder) ----------------
    def setup_my_returns_tab(self):
        """Placeholder for viewing return request status."""
        tab = self.notebook.tab("My Returns")
        ctk.CTkLabel(tab, text="List return requests with Status").pack(pady=50)