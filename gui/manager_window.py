import customtkinter as ctk
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import simpledialog
from services.stock_manager import StockManager
from services.request_manager import RequestManager
from models.college import College
from CTkMessagebox import CTkMessagebox


class ManagerWindow(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.user_id = None

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        title_frame = ctk.CTkFrame(self, height=50)
        title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        title_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(title_frame, text="KSU Inventory Manager Admin", font=("Arial", 20, "bold")).grid(row=0, column=0,
                                                                                                       padx=20, pady=10,
                                                                                                       sticky="w")
        ctk.CTkButton(title_frame, text="Logout", command=self.logout, fg_color="red").grid(row=0, column=1, padx=20,
                                                                                            pady=10, sticky="e")

        # Tabs
        self.notebook = ctk.CTkTabview(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.notebook.add("Registers (Items/Colleges)")
        self.notebook.add("Pending Requests")
        self.notebook.add("Dashboard")

        self.setup_registers_tab()
        self.setup_requests_tab()
        self.setup_dashboard_tab()

    def logout(self):
        self.controller.show_frame("SignUpWindow")

    # --- TAB 1: REGISTERS (Item & College) ---
    def setup_registers_tab(self):
        tab = self.notebook.tab("Registers (Items/Colleges)")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)  # Split screen: Items Left, Colleges Right

        # --- LEFT: Item Master ---
        frame_items = ctk.CTkFrame(tab)
        frame_items.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(frame_items, text="Item Master", font=("Arial", 16, "bold")).pack(pady=5)

        # Inputs
        f_i_in = ctk.CTkFrame(frame_items)
        f_i_in.pack(fill="x", padx=5)
        self.ent_name = ctk.CTkEntry(f_i_in, placeholder_text="Name");
        self.ent_name.pack(side="left", fill="x", expand=True, padx=2)
        self.ent_cat = ctk.CTkEntry(f_i_in, placeholder_text="Category", width=80);
        self.ent_cat.pack(side="left", padx=2)
        self.ent_unit = ctk.CTkEntry(f_i_in, placeholder_text="Unit", width=60);
        self.ent_unit.pack(side="left", padx=2)
        self.ent_qty = ctk.CTkEntry(f_i_in, placeholder_text="Qty", width=50);
        self.ent_qty.pack(side="left", padx=2)
        self.ent_lvl = ctk.CTkEntry(f_i_in, placeholder_text="Lvl", width=50);
        self.ent_lvl.pack(side="left", padx=2)
        ctk.CTkButton(f_i_in, text="+", width=40, command=self.add_item).pack(side="left", padx=2)

        # Table
        self.tree_inv = ttk.Treeview(frame_items, columns=('ID', 'Name', 'Cat', 'Unit', 'Lvl', 'Qty'), show='headings',
                                     height=10)
        for c in ('ID', 'Name', 'Cat', 'Unit', 'Lvl', 'Qty'):
            self.tree_inv.heading(c, text=c);
            self.tree_inv.column(c, width=40)
        self.tree_inv.column('Name', width=120)
        self.tree_inv.pack(fill="both", expand=True, padx=5, pady=5)

        # --- RIGHT: College Registry ---
        frame_colleges = ctk.CTkFrame(tab)
        frame_colleges.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(frame_colleges, text="College Registry", font=("Arial", 16, "bold")).pack(pady=5)

        # Inputs
        f_c_in = ctk.CTkFrame(frame_colleges)
        f_c_in.pack(fill="x", padx=5)
        self.ent_col_name = ctk.CTkEntry(f_c_in, placeholder_text="College Name")
        self.ent_col_name.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(f_c_in, text="Add College", command=self.add_college).pack(side="right", padx=5)

        # Table
        self.tree_col = ttk.Treeview(frame_colleges, columns=('ID', 'Name'), show='headings', height=10)
        self.tree_col.heading('ID', text='ID');
        self.tree_col.column('ID', width=50)
        self.tree_col.heading('Name', text='Name');
        self.tree_col.column('Name', width=200)
        self.tree_col.pack(fill="both", expand=True, padx=5, pady=5)

        self.refresh_inventory()
        self.refresh_colleges()

    def add_item(self):
        try:
            qty = int(self.ent_qty.get());
            lvl = int(self.ent_lvl.get())
            if StockManager.add_item(self.ent_name.get(), self.ent_cat.get(), self.ent_unit.get(), qty, lvl):
                self.refresh_inventory();
                CTkMessagebox(title="Success", message="Item Added", icon="check")
            else:
                CTkMessagebox(title="Error", message="Failed. Name might be duplicate.", icon="cancel")
        except ValueError:
            CTkMessagebox(title="Error", message="Qty/Lvl must be numbers", icon="cancel")

    def add_college(self):
        if College.add_college(self.ent_col_name.get()):
            self.refresh_colleges();
            CTkMessagebox(title="Success", message="College Added", icon="check")
        else:
            CTkMessagebox(title="Error", message="Failed to add college.", icon="cancel")

    def refresh_inventory(self):
        for i in self.tree_inv.get_children(): self.tree_inv.delete(i)
        for r in StockManager.get_all_items(): self.tree_inv.insert('', 'end', values=r)

    def refresh_colleges(self):
        for i in self.tree_col.get_children(): self.tree_col.delete(i)
        for r in College.get_all_colleges(): self.tree_col.insert('', 'end', values=r)

    # --- TAB 2: PENDING REQUESTS ---
    def setup_requests_tab(self):
        tab = self.notebook.tab("Pending Requests")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        self.tree_req = ttk.Treeview(tab, columns=('ID', 'College', 'Item', 'Qty', 'Purpose', 'Type'), show='headings')
        for c in ('ID', 'College', 'Item', 'Qty', 'Purpose', 'Type'): self.tree_req.heading(c, text=c)
        self.tree_req.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        bf = ctk.CTkFrame(tab)
        bf.grid(row=1, column=0, pady=10)
        ctk.CTkButton(bf, text="Approve", command=self.approve, fg_color="green").pack(side="left", padx=10)
        ctk.CTkButton(bf, text="Reject", command=self.reject, fg_color="red").pack(side="left", padx=10)
        ctk.CTkButton(bf, text="Refresh", command=self.refresh_reqs).pack(side="left", padx=10)
        self.refresh_reqs()

    def refresh_reqs(self):
        for i in self.tree_req.get_children(): self.tree_req.delete(i)
        for r in RequestManager.get_pending_requests(): self.tree_req.insert('', 'end', values=r)

    def approve(self):
        sel = self.tree_req.selection()
        if not sel: return
        item = self.tree_req.item(sel[0])['values']
        req_id, req_type = item[0], item[5]
        status = "Approved - Ready for Pickup" if req_type == 'Request' else "Approved - Ready for Pickup (Return)"

        if RequestManager.process_approval(req_id, status, self.user_id):
            CTkMessagebox(title="Success", message=f"{req_type} Approved", icon="check")
            self.refresh_reqs()
            self.refresh_inventory()  # Update stock view
        else:
            CTkMessagebox(title="Error", message="Failed. Check stock.", icon="cancel")

    def reject(self):
        sel = self.tree_req.selection()
        if not sel: return
        req_id = self.tree_req.item(sel[0])['values'][0]
        reason = simpledialog.askstring("Reject", "Reason:")
        if reason:
            RequestManager.update_request_status(req_id, "Rejected", reason)
            self.refresh_reqs()

    # --- TAB 3: DASHBOARD ---
    def setup_dashboard_tab(self):
        tab = self.notebook.tab("Dashboard")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        # 1. Low Stock Alerts
        f_alert = ctk.CTkFrame(tab)
        f_alert.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(f_alert, text="⚠️ Low Stock Alerts", text_color="red", font=("Arial", 16, "bold")).pack(pady=5)
        self.tree_alerts = ttk.Treeview(f_alert, columns=('Item', 'Qty', 'Lvl'), show='headings', height=5)
        for c in ('Item', 'Qty', 'Lvl'): self.tree_alerts.heading(c, text=c)
        self.tree_alerts.pack(fill="both", expand=True, padx=5)

        # 2. Controls & Backup
        f_ctrl = ctk.CTkFrame(tab)
        f_ctrl.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(f_ctrl, text="Controls", font=("Arial", 16, "bold")).pack(pady=5)
        ctk.CTkButton(f_ctrl, text="Refresh Dashboard", command=self.refresh_dashboard).pack(pady=10)
        ctk.CTkButton(f_ctrl, text="Export Backup (CSV)", command=self.do_backup, fg_color="#E07A5F").pack(pady=10)

        # ... inside setup_dashboard_tab ...

        # 3. College Custody Overview
        f_cust = ctk.CTkFrame(tab)
        f_cust.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(f_cust, text="College Custody Overview", font=("Arial", 16, "bold")).pack(pady=5)

        # FIX: Changed columns to match the query: (College Name, Item Name, Quantity)
        self.tree_cust = ttk.Treeview(f_cust, columns=('College', 'Item', 'Qty'), show='headings', height=8)

        # Configure Headings
        self.tree_cust.heading('College', text='College Name')
        self.tree_cust.heading('Item', text='Item Name')
        self.tree_cust.heading('Qty', text='Quantity')

        # Configure Columns
        self.tree_cust.column('College', width=150)
        self.tree_cust.column('Item', width=200)
        self.tree_cust.column('Qty', width=80, anchor='center')

        self.tree_cust.pack(fill="both", expand=True, padx=5)

        self.refresh_dashboard()

    def refresh_dashboard(self):
        # 1. Refresh Alerts
        for i in self.tree_alerts.get_children(): self.tree_alerts.delete(i)
        for r in StockManager.get_low_stock_alerts():
            self.tree_alerts.insert('', 'end', values=r)

        # 2. Refresh Custody Overview
        for i in self.tree_cust.get_children(): self.tree_cust.delete(i)

        # Fetch data from StockManager
        custody_data = StockManager.get_all_college_custody()
        for r in custody_data:
            self.tree_cust.insert('', 'end', values=r)

    def do_backup(self):
        success, msg = StockManager.backup_database()
        CTkMessagebox(title="Backup", message=msg, icon="check" if success else "cancel")