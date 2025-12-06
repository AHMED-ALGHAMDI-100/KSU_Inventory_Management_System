import customtkinter as ctk
import tkinter as tk  # Keep tk for messagebox/simpledialog as ctk messagebox is separate library
from tkinter import simpledialog, messagebox
from services.stock_manager import StockManager
from services.request_manager import RequestManager
from CTkMessagebox import CTkMessagebox  # For better dialogs (ensure installed)


# from models.inventory_item import InventoryItem # Needed for Item CRUD

class ManagerWindow(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        # --- Configure Grid for Layout ---
        self.grid_rowconfigure(1, weight=1)  # Tabview row
        self.grid_columnconfigure(0, weight=1)

        # --- Title Bar and Logout ---
        title_frame = ctk.CTkFrame(self, height=50)
        title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        title_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(title_frame, text="KSU Inventory Manager Admin", font=("Arial", 20, "bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Logout button (Requirement: return to Sign up window)
        logout_btn = ctk.CTkButton(title_frame, text="Logout", command=self.logout, fg_color="red")
        logout_btn.grid(row=0, column=1, padx=20, pady=10, sticky="e")

        # --- Tabs Setup ---
        self.notebook = ctk.CTkTabview(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Tabs based on project requirements
        self.notebook.add("Item Master & College Registry")
        self.notebook.add("Pending Requests & Returns")
        self.notebook.add("Stock Dashboard & Backup")

        self.setup_inventory_tab()
        self.setup_requests_tab()
        self.setup_dashboard_tab()

    def logout(self):
        """Destroys the current window and returns to the Sign Up screen."""
        self.controller.show_frame("SignUpWindow")

    # --- Tab 1: Item Master & College Registry (CRUD) ---

    def setup_inventory_tab(self):
        tab = self.notebook.tab("Item Master & College Registry")
        tab.grid_columnconfigure(0, weight=1)

        # Frame for Item Master CRUD (Inputs and Buttons)
        frame_item_crud = ctk.CTkFrame(tab)
        frame_item_crud.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

        # INPUT FIELDS (Replaced tk.Label/Entry with ctk.CTkLabel/CTkEntry)
        ctk.CTkLabel(frame_item_crud, text="Item Name:").grid(row=0, column=0, padx=5, pady=5)
        self.ent_name = ctk.CTkEntry(frame_item_crud, width=150)
        self.ent_name.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame_item_crud, text="Category:").grid(row=0, column=2, padx=5, pady=5)
        self.ent_cat = ctk.CTkEntry(frame_item_crud, width=100)
        self.ent_cat.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(frame_item_crud, text="Unit:").grid(row=1, column=0, padx=5, pady=5)
        self.ent_unit = ctk.CTkEntry(frame_item_crud, width=100)
        self.ent_unit.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame_item_crud, text="Reorder Lvl:").grid(row=1, column=2, padx=5, pady=5)
        self.ent_lvl = ctk.CTkEntry(frame_item_crud, width=100)
        self.ent_lvl.grid(row=1, column=3, padx=5, pady=5)

        # BUTTONS
        ctk.CTkButton(frame_item_crud, text="Add Item", command=self.add_item).grid(row=2, column=3, padx=5, pady=10)

        # TABLE (Using standard ttk.Treeview as ctk has no dedicated replacement)
        self.tree_inv = tk.ttk.Treeview(tab, columns=('ID', 'Name', 'Cat', 'Unit', 'Qty', 'Lvl'),
                                        show='headings')
        # ... Treeview heading/column configuration remains the same ...
        for col in ('ID', 'Name', 'Cat', 'Unit', 'Qty', 'Lvl'):
            self.tree_inv.heading(col, text=col)
            self.tree_inv.column(col, width=80)
        self.tree_inv.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        tab.grid_rowconfigure(1, weight=1)
        self.refresh_inventory()

    def add_item(self):
        # Validation for Qty and Level
        try:
            qty = int(self.ent_qty.get())
            lvl = int(self.ent_lvl.get())
        except ValueError:
            CTkMessagebox(title="Error", message="Quantity and Reorder Level must be numbers.", icon="cancel")
            return

        # Assumes StockManager.add_item handles Item Master CRUD
        if StockManager.add_item(self.ent_name.get(), self.ent_cat.get(), self.ent_unit.get(), qty, lvl):
            CTkMessagebox(title="Success", message="Item Added and Stock Initialized.", icon="check")
            self.refresh_inventory()
        else:
            CTkMessagebox(title="Error", message="Failed to add item (Check for duplicate name).", icon="cancel")

    def refresh_inventory(self):
        """Loads and updates the Item Master table."""
        for i in self.tree_inv.get_children(): self.tree_inv.delete(i)
        # Assumes StockManager.get_all_items() returns item details including stock and reorder level
        for row in StockManager.get_all_items():
            self.tree_inv.insert('', 'end', values=row)

    # --- Tab 2: Pending Requests & Returns ---
    def setup_requests_tab(self):
        tab = self.notebook.tab("Pending Requests & Returns")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # TABLE (View all pending item requests with details)
        self.tree_req = tk.ttk.Treeview(tab, columns=('ID', 'College', 'Item', 'Qty', 'Purpose', 'Type'),
                                        show='headings')
        for col in ('ID', 'College', 'Item', 'Qty', 'Purpose', 'Type'):
            self.tree_req.heading(col, text=col)
        self.tree_req.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # BUTTONS FRAME
        btn_frame = ctk.CTkFrame(tab)
        btn_frame.grid(row=1, column=0, pady=10)

        # Approve/Reject Buttons
        ctk.CTkButton(btn_frame, text="Approve", command=self.approve_req, fg_color="green").pack(side='left', padx=10)
        ctk.CTkButton(btn_frame, text="Reject", command=self.reject_req, fg_color="red").pack(side='left', padx=10)
        ctk.CTkButton(btn_frame, text="Refresh", command=self.refresh_requests).pack(side='left', padx=10)

        self.refresh_requests()

    def refresh_requests(self):
        for i in self.tree_req.get_children(): self.tree_req.delete(i)
        # Assumes RequestManager.get_pending_requests() retrieves both pending requests and pending returns
        for row in RequestManager.get_pending_requests():
            self.tree_req.insert('', 'end', values=row)

    def approve_req(self):
        selected = self.tree_req.selection()
        if not selected:
            CTkMessagebox(title="Error", message="Please select a request to approve.", icon="warning")
            return

        # Logic to extract request details
        item = self.tree_req.item(selected[0])
        req_id = item['values'][0]
        req_type = item['values'][5]

        # Determine the status based on type
        status = "Approved - Ready for Pickup" if req_type == 'Request' else "Approved - Ready for Pickup (Return)"

        # Assuming RequestManager handles stock reservation for Requests
        if RequestManager.process_approval(req_id, status, self.controller.user_id):
            CTkMessagebox(title="Approved", message=f"Request/Return {req_id} approved. Status: {status}", icon="check")
        else:
            CTkMessagebox(title="Error", message=f"Failed to approve {req_id}. Check stock levels.", icon="cancel")

        self.refresh_requests()

    def reject_req(self):
        selected = self.tree_req.selection()
        if not selected:
            CTkMessagebox(title="Error", message="Please select a request to reject.", icon="warning")
            return

        req_id = self.tree_req.item(selected[0])['values'][0]

        # Use tk.simpledialog as CustomTkinter message box doesn't offer input fields
        reason = simpledialog.askstring("Reject Request/Return", "Enter rejection reason (Required):")

        if reason:
            # Update status and log rejection reason
            RequestManager.update_request_status(req_id, "Rejected", reason)
            CTkMessagebox(title="Rejected", message=f"Request/Return {req_id} rejected. Reason logged.", icon="check")
            self.refresh_requests()
        elif reason is not None:  # User clicked OK without typing a reason
            CTkMessagebox(title="Warning", message="Rejection requires a reason.", icon="warning")

    # --- Tab 3: Dashboard & Backup ---
    def setup_dashboard_tab(self):
        tab = self.notebook.tab("Stock Dashboard & Backup")

        # Note: Stock Dashboard visualization (per-college custody, low-stock alerts)
        # is complex and is delegated to the StockManager service, represented by a placeholder button here.

        ctk.CTkLabel(tab, text="Stock Dashboard (Details Handled by StockManager Service)", font=("Arial", 16)).pack(
            pady=20)

        # Backup Button (Requirement: Export the entire central DB to CSV)
        ctk.CTkButton(tab, text="Export Full DB Backup (backup.csv)", command=self.do_backup, height=40, width=250,
                      fg_color="#E07A5F").pack(pady=50)

    def do_backup(self):
        """Calls the service function to export the entire central DB to CSV."""
        # Assumes StockManager.backup_database() returns (success, msg)
        success, msg = StockManager.backup_database()
        CTkMessagebox(title="Backup Status", message=msg, icon="check" if success else "cancel")