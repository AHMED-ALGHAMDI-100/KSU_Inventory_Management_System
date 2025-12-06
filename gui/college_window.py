import customtkinter as ctk
import tkinter.ttk as ttk  # Required for the Table (Treeview)
from CTkMessagebox import CTkMessagebox

from services.request_manager import RequestManager
from models.inventory_item import InventoryItem
from models.college import College


class CollegeWindow(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
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

        # Logout button
        logout_btn = ctk.CTkButton(title_frame, text="Logout", command=self.logout)
        logout_btn.grid(row=0, column=1, padx=20, pady=10, sticky="e")

        # --- Tabs Setup ---
        self.notebook = ctk.CTkTabview(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

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
        self.controller.show_frame("SignUpWindow")

    # ---------------- TAB 1: Request Item ----------------
    def setup_request_tab(self):
        tab = self.notebook.tab("Request Item")
        tab.grid_columnconfigure(1, weight=1)

        # Title
        ctk.CTkLabel(tab, text="Initiate New Item Request", font=("Arial", 16)).grid(row=0, column=0, columnspan=2,
                                                                                     pady=(10, 20))

        # Item Catalog Dropdown
        ctk.CTkLabel(tab, text="Select Item:").grid(row=1, column=0, padx=10, pady=5, sticky='w')

        try:
            self.catalog_items = InventoryItem.get_catalog()
            # Use dot notation for object attributes
            item_names = [f"{item.id} - {item.name} ({item.unit})" for item in self.catalog_items]
        except Exception:
            item_names = ["No Items Available"]

        self.combo_items = ctk.CTkComboBox(tab, values=item_names, width=300)
        self.combo_items.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        # Quantity
        ctk.CTkLabel(tab, text="Quantity:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.entry_qty = ctk.CTkEntry(tab, width=300)
        self.entry_qty.grid(row=2, column=1, padx=10, pady=5, sticky='ew')

        # Purpose
        ctk.CTkLabel(tab, text="Purpose/Notes:").grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self.entry_purpose = ctk.CTkEntry(tab, width=300)
        self.entry_purpose.grid(row=3, column=1, padx=10, pady=5, sticky='ew')

        # Submit Button
        btn_submit = ctk.CTkButton(tab, text="Submit Request", command=self.submit_request, fg_color="green")
        btn_submit.grid(row=4, column=1, pady=30, sticky='e')

    def submit_request(self):
        selection = self.combo_items.get()
        qty_str = self.entry_qty.get()
        purpose = self.entry_purpose.get()

        if not selection or not qty_str or not purpose:
            CTkMessagebox(title="Error", message="All fields are required!", icon="cancel")
            return

        try:
            qty = int(qty_str)
            if qty <= 0: raise ValueError
        except ValueError:
            CTkMessagebox(title="Error", message="Quantity must be a positive number.", icon="cancel")
            return

        try:
            item_id = int(selection.split(' - ')[0])
        except ValueError:
            CTkMessagebox(title="Error", message="Please select a valid item.", icon="cancel")
            return

        if RequestManager.create_request(self.user_id, item_id, qty, purpose, 'Request'):
            CTkMessagebox(title="Success", message="Request Submitted Successfully!", icon="check")

            # --- Auto-Refresh the Table ---
            self.load_my_requests()
            self.notebook.set("My Requests")  # Switch to the tab

            # Clear inputs
            self.entry_qty.delete(0, 'end')
            self.entry_purpose.delete(0, 'end')
        else:
            CTkMessagebox(title="Error", message="Failed to submit request.", icon="cancel")

    # ---------------- TAB 2: My Requests (CORRECTED) ----------------
    def setup_my_requests_tab(self):
        """Sets up the table to view request history."""
        tab = self.notebook.tab("My Requests")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Create Treeview (Table)
        columns = ('ID', 'Item', 'Qty', 'Status', 'Date', 'Reject Reason')
        self.tree_requests = ttk.Treeview(tab, columns=columns, show='headings')

        # Define Headings
        for col in columns:
            self.tree_requests.heading(col, text=col)
            width = 200 if col == 'Reject Reason' else 100
            self.tree_requests.column(col, width=width)

        self.tree_requests.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        # Add Refresh Button
        ctk.CTkButton(tab, text="Refresh List", command=self.load_my_requests).grid(row=1, column=0, pady=10)

        # Initial Load
        self.load_my_requests()

    def load_my_requests(self):
        """Fetches data from DB and populates the table."""
        # Clear existing data
        for item in self.tree_requests.get_children():
            self.tree_requests.delete(item)

        # Fetch from DB
        if self.user_id:
            college_model = College(self.user_id)
            rows = college_model.get_my_requests()
            for row in rows:
                self.tree_requests.insert('', 'end', values=row)

    # ---------------- TAB 3: Return Item (Placeholder) ----------------
    def setup_return_tab(self):
        tab = self.notebook.tab("Return Item")
        ctk.CTkLabel(tab, text="Initiate Return for items currently in college custody").pack(pady=50)

    # ---------------- TAB 4: My Returns (Placeholder) ----------------
    def setup_my_returns_tab(self):
        tab = self.notebook.tab("My Returns")
        ctk.CTkLabel(tab, text="List return requests with Status").pack(pady=50)