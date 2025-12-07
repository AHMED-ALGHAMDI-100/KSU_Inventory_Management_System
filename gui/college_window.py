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
        # Initialize user_id to be set by the main controller after login
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

    # =========================================================================
    # TAB 1: REQUEST ITEM
    # =========================================================================
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
            # Use dot notation because get_catalog returns objects
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

            # Auto-Refresh and Switch Tab
            self.load_my_requests()
            self.notebook.set("My Requests")

            # Clear inputs
            self.entry_qty.delete(0, 'end')
            self.entry_purpose.delete(0, 'end')
        else:
            CTkMessagebox(title="Error", message="Failed to submit request.", icon="cancel")

    # =========================================================================
    # TAB 2: MY REQUESTS
    # =========================================================================
    def setup_my_requests_tab(self):
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
        for item in self.tree_requests.get_children():
            self.tree_requests.delete(item)

        if self.user_id:
            college_model = College(self.user_id)
            rows = college_model.get_my_requests()
            for row in rows:
                # Convert None to "" to avoid display errors
                safe_row = [str(val) if val is not None else "" for val in row]
                self.tree_requests.insert('', 'end', values=safe_row)

    # =========================================================================
    # TAB 3: RETURN ITEM
    # =========================================================================
    def setup_return_tab(self):
        tab = self.notebook.tab("Return Item")
        tab.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(tab, text="Initiate Item Return", font=("Arial", 16)).grid(row=0, column=0, columnspan=2,
                                                                                pady=(10, 20))

        # Items in Custody Dropdown
        ctk.CTkLabel(tab, text="Select Item to Return:").grid(row=1, column=0, padx=10, pady=5, sticky='w')

        # Initial empty load
        self.combo_custody = ctk.CTkComboBox(tab, values=["Loading..."], width=300)
        self.combo_custody.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

        # Load items
        self.load_custody_options()

        # Quantity to Return
        ctk.CTkLabel(tab, text="Quantity to Return:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.entry_return_qty = ctk.CTkEntry(tab, width=300)
        self.entry_return_qty.grid(row=2, column=1, padx=10, pady=5, sticky='ew')

        # Notes
        ctk.CTkLabel(tab, text="Condition/Notes:").grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self.entry_return_purpose = ctk.CTkEntry(tab, width=300)
        self.entry_return_purpose.grid(row=3, column=1, padx=10, pady=5, sticky='ew')

        # Submit Button
        btn_submit = ctk.CTkButton(tab, text="Submit Return Request", command=self.submit_return, fg_color="#E07A5F")
        btn_submit.grid(row=4, column=1, pady=30, sticky='e')

    def load_custody_options(self):
        """Fetches items currently held by the college to populate the return dropdown."""
        if self.user_id:
            try:
                college_model = College(self.user_id)
                self.custody_items = college_model.get_current_custody()

                if self.custody_items:
                    self.custody_options = [
                        f"{item[0]} - {item[1]} (Available: {item[2]} {item[3]})"
                        for item in self.custody_items
                    ]
                else:
                    self.custody_options = ["No Items in Custody"]
            except Exception as e:
                print(f"Error loading custody items: {e}")
                self.custody_options = ["Error Loading Items"]
        else:
            self.custody_options = ["No Items (Not Logged In)"]

        if hasattr(self, 'combo_custody'):
            self.combo_custody.configure(values=self.custody_options)
            self.combo_custody.set(self.custody_options[0])

    def submit_return(self):
        selection = self.combo_custody.get()
        qty_str = self.entry_return_qty.get()
        purpose = self.entry_return_purpose.get()

        if not selection or not qty_str or not purpose or "No Items" in selection:
            CTkMessagebox(title="Error", message="Please select a valid item and fill all fields.", icon="cancel")
            return

        try:
            qty = int(qty_str)
            if qty <= 0: raise ValueError
        except ValueError:
            CTkMessagebox(title="Error", message="Quantity must be a positive number.", icon="cancel")
            return

        try:
            item_id = int(selection.split(' - ')[0])
            # Find max qty from the stored list
            max_qty_available = next(item[2] for item in self.custody_items if item[0] == item_id)
        except (ValueError, StopIteration):
            CTkMessagebox(title="Error", message="Invalid item selection.", icon="cancel")
            return

        if qty > max_qty_available:
            CTkMessagebox(title="Error", message=f"Cannot return {qty}. Max available is {max_qty_available}.",
                          icon="cancel")
            return

        if RequestManager.create_request(self.user_id, item_id, qty, purpose, 'Return'):
            CTkMessagebox(title="Success", message="Return Request Submitted Successfully!", icon="check")

            # Refresh data
            self.load_custody_options()
            self.load_my_returns()
            self.notebook.set("My Returns")

            self.entry_return_qty.delete(0, 'end')
            self.entry_return_purpose.delete(0, 'end')
        else:
            CTkMessagebox(title="Error", message="Failed to submit return request.", icon="cancel")

    # =========================================================================
    # TAB 4: MY RETURNS
    # =========================================================================
    def setup_my_returns_tab(self):
        tab = self.notebook.tab("My Returns")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # Create Treeview (Table)
        columns = ('ID', 'Item', 'Qty', 'Status', 'Date', 'Reject Reason')
        self.tree_returns = ttk.Treeview(tab, columns=columns, show='headings')

        # Define Headings
        for col in columns:
            self.tree_returns.heading(col, text=col)
            width = 200 if col == 'Reject Reason' else 100
            self.tree_returns.column(col, width=width)

        self.tree_returns.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        # Add Refresh Button
        ctk.CTkButton(tab, text="Refresh List", command=self.load_my_returns).grid(row=1, column=0, pady=10)

        # Initial Load
        self.load_my_returns()

    def load_my_returns(self):
        """Fetches return data from DB."""
        for item in self.tree_returns.get_children():
            self.tree_returns.delete(item)

        if self.user_id:
            college_model = College(self.user_id)
            rows = college_model.get_my_returns()
            for row in rows:
                safe_row = [str(val) if val is not None else "" for val in row]
                self.tree_returns.insert('', 'end', values=safe_row)

    def tkraise(self, aboveThis=None):
        super().tkraise(aboveThis)
        # When the window is brought to front, reload data if user_id is set
        if self.user_id:
            self.load_custody_options()
            self.load_my_requests()
            self.load_my_returns()