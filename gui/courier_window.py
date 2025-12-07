import customtkinter as ctk
import tkinter.ttk as ttk
from CTkMessagebox import CTkMessagebox
from services.courier_manager import CourierManager


class CourierWindow(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.user_id = None

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        title_frame = ctk.CTkFrame(self, height=50)
        title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        title_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(title_frame, text="KSU Courier Operations", font=("Arial", 20, "bold")).grid(row=0, column=0,
                                                                                                  padx=20, pady=10,
                                                                                                  sticky="w")
        ctk.CTkButton(title_frame, text="Logout", command=self.logout).grid(row=0, column=1, padx=20, pady=10,
                                                                            sticky="e")

        # Tabs
        self.notebook = ctk.CTkTabview(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.notebook.add("Pick Up Request")
        self.notebook.add("Deliver to College")
        self.notebook.add("Pick Up Return")
        self.notebook.add("Deliver Return")

        self.setup_pickup_tab()
        self.setup_delivery_tab()
        self.setup_pickup_return_tab()
        self.setup_deliver_return_tab()

    def logout(self):
        self.controller.show_frame("SignUpWindow")

    # --- HELPER: Generic Table Setup ---
    def _setup_table_tab(self, tab_name, button_text, load_func, action_func):
        tab = self.notebook.tab(tab_name)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        columns = ('ID', 'College', 'Item', 'Qty', 'Type', 'Notes')
        tree = ttk.Treeview(tab, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Scrollbar
        sb = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
        sb.grid(row=1, column=1, sticky="ns")
        tree.configure(yscrollcommand=sb.set)

        btn_frame = ctk.CTkFrame(tab)
        btn_frame.grid(row=2, column=0, pady=10)

        # Load Data Wrapper
        def refresh():
            for item in tree.get_children(): tree.delete(item)
            for row in load_func():
                tree.insert('', 'end', values=row)

        # Action Wrapper
        def confirm():
            selected = tree.selection()
            if not selected:
                CTkMessagebox(title="Error", message="Select a request.", icon="cancel")
                return
            req_id = tree.item(selected[0])['values'][0]

            # Helper to handle different function signatures (some need courier_id, some don't)
            try:
                success = action_func(req_id, self.user_id)
            except TypeError:
                success = action_func(req_id)

            if success:
                CTkMessagebox(title="Success", message="Action Completed!", icon="check")
                refresh()
            else:
                CTkMessagebox(title="Error", message="Failed.", icon="cancel")

        ctk.CTkButton(btn_frame, text=button_text, command=confirm, fg_color="green").pack(side='left', padx=10)
        ctk.CTkButton(btn_frame, text="Refresh", command=refresh).pack(side='left', padx=10)

        # Initial Load
        refresh()

    # --- TAB SETUP CALLS ---
    def setup_pickup_tab(self):
        self._setup_table_tab("Pick Up Request", "Confirm Pickup",
                              CourierManager.get_requests_for_pickup, CourierManager.pickup_request)

    def setup_delivery_tab(self):
        self._setup_table_tab("Deliver to College", "Confirm Delivery",
                              CourierManager.get_requests_for_delivery, CourierManager.deliver_request)

    def setup_pickup_return_tab(self):
        self._setup_table_tab("Pick Up Return", "Confirm Return Pickup",
                              CourierManager.get_returns_for_pickup, CourierManager.pickup_return)

    def setup_deliver_return_tab(self):
        self._setup_table_tab("Deliver Return", "Confirm Return Delivery",
                              CourierManager.get_returns_for_delivery, CourierManager.deliver_return)