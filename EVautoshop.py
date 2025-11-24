# EVautoshop.py - main GUI application class
import customtkinter as ctk
from tkinter import ttk, messagebox
from db import DB
from db import now_date, now_time, hashpw
from typing import Optional

class EVAutoRepairApp(ctk.CTk):
    def __init__(self, db: DB):
        super().__init__()
        self.db = db
        self.title("EV Auto Repair Shop")
        self.geometry("1200x720")
        self.minsize(1100, 650)

        self.current_user = None


        self.top_bar = ctk.CTkFrame(self, height=50)
        self.top_bar.pack(side="top", fill="x")

        self.lbl_title = ctk.CTkLabel(
            self.top_bar,
            text="EV Auto Repairshop - Admin",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.lbl_title.pack(side="left", padx=15)

        self.lbl_user = ctk.CTkLabel(
            self.top_bar,
            text="Not logged in",
            font=ctk.CTkFont(size=13)
        )
        self.lbl_user.pack(side="right", padx=15)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="top", fill="both", expand=True)

        # left menu
        self.menu_frame = ctk.CTkFrame(self.main_frame, width=200)
        self.menu_frame.pack(side="left", fill="y")
        self.menu_frame.pack_propagate(False)

        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(side="left", fill="both", expand=True)

        self.menu_buttons = {}
        self.pages = {}

        self.create_menu()
        self.create_pages()

        # hide main until login
        self.withdraw()
        self.after(100, self.show_login)

    # LOGIN FLOW 

    def show_login(self):
        LoginDialog(self, self.db, self.on_login_success)

    def on_login_success(self, username: str):
        self.current_user = username
        self.deiconify()
        self.lbl_user.configure(text=f"Logged in as: {username}")
        self.show_page("Dashboard")
        self.refresh_dashboard()
        self.refresh_clients_table()
        self.refresh_service_clients()
        self.refresh_reports()
        self.refresh_history()

    # ---------- MENU + PAGES ----------

    def create_menu(self):
        def add_menu_button(text, page_key):
            btn = ctk.CTkButton(
                self.menu_frame,
                text=text,
                anchor="w",
                command=lambda k=page_key: self.show_page(k)
            )
            btn.pack(fill="x", padx=10, pady=5)
            self.menu_buttons[page_key] = btn

        add_menu_button("Dashboard", "Dashboard")
        add_menu_button("Client", "Client")
        add_menu_button("Service", "Service")
        add_menu_button("Reports", "Reports")
        add_menu_button("Client History", "History")

        # Logout button
        ctk.CTkButton(
            self.menu_frame,
            text="Logout",
            fg_color="red4",
            hover_color="red3",
            command=self.handle_logout
        ).pack(side="bottom", fill="x", padx=10, pady=10)

    def create_pages(self):
        # Create frames for each page
        self.pages["Dashboard"] = ctk.CTkFrame(self.content_frame)
        self.pages["Client"] = ctk.CTkFrame(self.content_frame)
        self.pages["Service"] = ctk.CTkFrame(self.content_frame)
        self.pages["Reports"] = ctk.CTkFrame(self.content_frame)
        self.pages["History"] = ctk.CTkFrame(self.content_frame)

        self.build_dashboard_page(self.pages["Dashboard"])
        self.build_client_page(self.pages["Client"])
        self.build_service_page(self.pages["Service"])
        self.build_reports_page(self.pages["Reports"])
        self.build_history_page(self.pages["History"])

    def show_page(self, key: str):
        for k, frame in self.pages.items():
            frame.pack_forget()
        frame = self.pages.get(key)
        if frame:
            frame.pack(fill="both", expand=True, padx=10, pady=10)

    def handle_logout(self):
        if not messagebox.askokcancel("Logout", "Are you sure you want to logout?", parent=self):
            return
        self.current_user = None
        self.withdraw()
        self.show_login()


    #  DASHBOARD
    def build_dashboard_page(self, parent: ctk.CTkFrame):
        title = ctk.CTkLabel(
            parent, text="Dashboard - Today's Overview",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(anchor="w", pady=10)

        # container for stat cards
        cards_row = ctk.CTkFrame(parent)
        cards_row.pack(fill="x", pady=8)

        # All Overview Section (Monthly)
        all_title = ctk.CTkLabel(
            parent, text="All Overview - This Month",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        all_title.pack(anchor="w", pady=(18, 8))

        all_cards_row = ctk.CTkFrame(parent)
        all_cards_row.pack(fill="x", pady=8)

        def make_all_card(parent, caption, initial):
            card = ctk.CTkFrame(parent, corner_radius=8, border_width=1)
            card.pack(side="left", expand=True, fill="both", padx=8, pady=4)
            val_lbl = ctk.CTkLabel(card, text=initial,
                                   font=ctk.CTkFont(size=32, weight="bold"))
            val_lbl.pack(anchor="center", pady=(18,6))
            cap_lbl = ctk.CTkLabel(card, text=caption,
                                   font=ctk.CTkFont(size=12))
            cap_lbl.pack(anchor="center", pady=(0,18))
            return card, val_lbl, cap_lbl

        #  monthly overview ctk
        _, self._lbl_monthly_sales, _ = make_all_card(all_cards_row, "Monthly Sales", "₱0.00")
        _, self._lbl_monthly_total_repairs, _ = make_all_card(all_cards_row, "Total Repairs This Month", "0")
        _, self._lbl_monthly_inprogress, _ = make_all_card(all_cards_row, "In-progress Repairs This Month", "0")
        _, self._lbl_monthly_done, _ = make_all_card(all_cards_row, "Done Repairs This Month", "0")
        def make_card(parent, caption, initial):
            card = ctk.CTkFrame(parent, corner_radius=8, border_width=1)
            card.pack(side="left", expand=True, fill="both", padx=8, pady=4)
            val_lbl = ctk.CTkLabel(card, text=initial,
                                   font=ctk.CTkFont(size=32, weight="bold"))
            val_lbl.pack(anchor="center", pady=(18,6))
            cap_lbl = ctk.CTkLabel(card, text=caption,
                                   font=ctk.CTkFont(size=12))
            cap_lbl.pack(anchor="center", pady=(0,18))
            return card, val_lbl, cap_lbl

        # Today's overviewctk
        _, self._lbl_sales_value, _ = make_card(cards_row, "Today's Sales", "₱0.00")
        _, self._lbl_total_repairs_value, _ = make_card(cards_row, "Total Repairs Today", "0")
        _, self._lbl_inprogress_value, _ = make_card(cards_row, "In-progress Repairs", "0")
        _, self._lbl_done_value, _ = make_card(cards_row, "Done Repairs", "0")

        #refresh button
        refresh_btn = ctk.CTkButton(parent, text="Refresh", command=self.refresh_dashboard)
        refresh_btn.pack(anchor="w", pady=8)


    def refresh_dashboard(self):
        stats = self.db.get_today_stats()
        try:
            self._lbl_sales_value.configure(text=peso(stats['today_sales']))
        except Exception:
            self._lbl_sales_value.configure(text="₱0.00")
        try:
            self._lbl_total_repairs_value.configure(text=str(int(stats['total_repairs'] or 0)))
        except Exception:
            self._lbl_total_repairs_value.configure(text="0")
        try:
            self._lbl_inprogress_value.configure(text=str(int(stats['in_progress'] or 0)))
        except Exception:
            self._lbl_inprogress_value.configure(text="0")
        try:
            self._lbl_done_value.configure(text=str(int(stats['done_repairs'] or 0)))
        except Exception:
            self._lbl_done_value.configure(text="0")

        # --- Monthly Overview ---
        now = datetime.datetime.now()
        year = now.year
        month = now.month

        # Monthly sales
        try:
            monthly_sales = self.db.get_sales_by_month(year, month)
            self._lbl_monthly_sales.configure(text=peso(monthly_sales))
        except Exception:
            self._lbl_monthly_sales.configure(text="₱0.00")

        # Total repairs, in-progress, done for month
        try:
            rows = self.db.execute(
                """
                SELECT status, COUNT(*) FROM repair_orders
                WHERE strftime('%Y', date_start) = ? AND strftime('%m', date_start) = ?
                GROUP BY status
                """,
                (str(year), f"{month:02d}"), fetch=True
            )
            total_repairs = sum([cnt for _st, cnt in rows])
            inprogress = sum([cnt for st, cnt in rows if st != 'Pickup'])
            done = sum([cnt for st, cnt in rows if st == 'Pickup'])
            self._lbl_monthly_total_repairs.configure(text=str(total_repairs))
            self._lbl_monthly_inprogress.configure(text=str(inprogress))
            self._lbl_monthly_done.configure(text=str(done))
        except Exception:
            self._lbl_monthly_total_repairs.configure(text="0")
            self._lbl_monthly_inprogress.configure(text="0")
            self._lbl_monthly_done.configure(text="0")

    def build_service_page(self, parent: ctk.CTkFrame):
        title = ctk.CTkLabel(
            parent, text="Service - Add Repair / Job",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(anchor="w", pady=10)

        main = ctk.CTkFrame(parent)
        main.pack(fill="both", expand=True)

        left = ctk.CTkFrame(main)
        left.pack(side="left", fill="y", padx=5, pady=5)

        right = ctk.CTkFrame(main)
        right.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Select client & vehicle
        ctk.CTkLabel(left, text="Select Client:").grid(
            row=0, column=0, sticky="w", padx=5, pady=3)
        self.cb_service_client = ctk.CTkComboBox(
            left, values=[], width=260,
            command=lambda _e=None: self.refresh_service_vehicles()
        )
        self.cb_service_client.grid(row=0, column=1, padx=5, pady=3)

        ctk.CTkLabel(left, text="Select Vehicle:").grid(
            row=1, column=0, sticky="w", padx=5, pady=3)
        self.cb_service_vehicle = ctk.CTkComboBox(left, values=[], width=260)
        self.cb_service_vehicle.grid(row=1, column=1, padx=5, pady=3)

        # Type of Job
        ctk.CTkLabel(left, text="Type of Job:").grid(
            row=2, column=0, sticky="w", padx=5, pady=3)
        self.cb_type_job = ctk.CTkComboBox(
            left, values=TYPE_JOB_LIST, width=260,
            command=lambda _e=None: self.refresh_specific_services()
        )
        self.cb_type_job.grid(row=2, column=1, padx=5, pady=3)

        # Specific Service
        ctk.CTkLabel(left, text="Specific Service:").grid(
            row=3, column=0, sticky="w", padx=5, pady=3)
        self.cb_specific_service = ctk.CTkComboBox(
            left, values=[], width=260,
            command=lambda _e=None: self.update_service_details()
        )
        self.cb_specific_service.grid(row=3, column=1, padx=5, pady=3)

        # Severity (Minor/Major)
        ctk.CTkLabel(left, text="Type (Minor / Major):").grid(
            row=4, column=0, sticky="w", padx=5, pady=3)
        self.cb_severity = ctk.CTkComboBox(
            left, values=["Minor", "Major"], width=260,
            command=lambda _e=None: self.update_service_price()
        )
        self.cb_severity.grid(row=4, column=1, padx=5, pady=3)
        self.cb_severity.set("Minor")

        # Description 
        ctk.CTkLabel(left, text="Description (optional):").grid(
            row=5, column=0, sticky="nw", padx=5, pady=3)
        self.txt_description = ctk.CTkTextbox(left, width=260, height=60)
        self.txt_description.grid(row=5, column=1, padx=5, pady=3)

        # Auto parts recommended (checkboxes)
        ctk.CTkLabel(left, text="Auto parts recommended:").grid(
            row=6, column=0, sticky="nw", padx=5, pady=3)
        self.parts_frame = ctk.CTkFrame(left)
        self.parts_frame.grid(row=6, column=1, padx=5, pady=3, sticky="w")
        self.part_vars = []

        # Assigned mechanics 
        ctk.CTkLabel(left, text="Assigned Mechanics:").grid(
            row=7, column=0, sticky="nw", padx=5, pady=3)
        mech_frame = ctk.CTkFrame(left)
        mech_frame.grid(row=7, column=1, padx=5, pady=3, sticky="w")

        self.chk_mech1_var = ctk.BooleanVar(value=True)        
        self.chk_mech2_var = ctk.BooleanVar(value=True)
        self.chk_mech3_var = ctk.BooleanVar(value=True)
        self.lbl_mech1_name = ctk.CTkLabel(mech_frame, text="(mech1)")
        self.lbl_mech2_name = ctk.CTkLabel(mech_frame, text="(mech2)")
        self.lbl_mech3_name = ctk.CTkLabel(mech_frame, text="(mech3)")

        self.chk_mech1 = ctk.CTkCheckBox(
            mech_frame, text="", variable=self.chk_mech1_var)
        self.chk_mech2 = ctk.CTkCheckBox(
            mech_frame, text="", variable=self.chk_mech2_var)
        self.chk_mech3 = ctk.CTkCheckBox(
            mech_frame, text="", variable=self.chk_mech3_var)

        self.chk_mech1.grid(row=0, column=0, padx=2)
        self.lbl_mech1_name.grid(row=0, column=1, padx=2)
        self.chk_mech2.grid(row=1, column=0, padx=2)
        self.lbl_mech2_name.grid(row=1, column=1, padx=2)
        self.chk_mech3.grid(row=2, column=0, padx=2)
        self.lbl_mech3_name.grid(row=2, column=1, padx=2)

        # Status
        ctk.CTkLabel(left, text="Status:").grid(
            row=8, column=0, sticky="w", padx=5, pady=3)
        self.cb_status = ctk.CTkComboBox(
            left, values=STATUS_LIST, width=260
        )
        self.cb_status.grid(row=8, column=1, padx=5, pady=3)
        self.cb_status.set("Check-in")

        # ETA display
        eta_frame = ctk.CTkFrame(left)
        eta_frame.grid(row=9, column=0, columnspan=2, sticky="w", padx=5, pady=3)

        self.lbl_start_dt = ctk.CTkLabel(eta_frame, text="Start: - / -")
        self.lbl_eta_dt = ctk.CTkLabel(eta_frame, text="ETA Done: - / -")
        self.lbl_start_dt.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.lbl_eta_dt.grid(row=1, column=0, padx=5, pady=2, sticky="w")

        # Prices
        price_frame = ctk.CTkFrame(left)
        price_frame.grid(row=10, column=0, columnspan=2, sticky="w", padx=5, pady=3)

        self.lbl_minor_price = ctk.CTkLabel(price_frame, text="Minor Price: ₱0.00")
        self.lbl_major_price = ctk.CTkLabel(price_frame, text="Major Price: ₱0.00")
        self.lbl_total_price = ctk.CTkLabel(
            price_frame, text="Total Cost (selected): ₱0.00",
            font=ctk.CTkFont(weight="bold")
        )

        self.lbl_minor_price.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.lbl_major_price.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.lbl_total_price.grid(row=2, column=0, padx=5, pady=2, sticky="w")

        # Buttons
        btn_frame = ctk.CTkFrame(left)
        btn_frame.grid(row=11, column=0, columnspan=2, pady=10)


        ctk.CTkButton(
            btn_frame, text="Save service",
            command=self.save_service
        ).pack(side="left", padx=5)

        # --- Right: List of repair orders (open / all) ---

        ctk.CTkLabel(
            right, text="Existing Repair Orders",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=5)

        table_frame = ctk.CTkFrame(right)
        table_frame.pack(fill="both", expand=True)

        columns = (
            "ID", "Client", "Vehicle",
            "Service", "Status", "Date", "Time", "Total"
        )
        style_orders = ttk.Style()
        style_orders.configure("Treeview", font=("Segoe UI", 12))
        style_orders.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        self.tree_orders = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=28
        )
        for col in columns:
            self.tree_orders.heading(col, text=col)
            width = 80
            if col == "Client":
                width = 140
            if col == "Service":
                width = 160
            self.tree_orders.column(col, width=width)
        # hide the numeric ID column (keep data but not visible)
        try:
            self.tree_orders.column("ID", width=0, minwidth=0, stretch=False)
        except Exception:
            pass
        self.tree_orders.pack(fill="both", expand=True)

        btn2_frame = ctk.CTkFrame(right)
        btn2_frame.pack(fill="x", pady=5)

        ctk.CTkButton(
            btn2_frame, text="Refresh",
            command=self.refresh_orders_table
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            btn2_frame, text="Mark as Done (Pickup)",
            command=self.mark_order_done
        ).pack(side="right", padx=5)

    # =========================================================
    #  CLIENT PAGE
    # =========================================================

    def build_client_page(self, parent: ctk.CTkFrame):
        title = ctk.CTkLabel(
            parent, text="Clients & Vehicles",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(anchor="w", pady=10)

        top_frame = ctk.CTkFrame(parent)
        top_frame.pack(fill="x", pady=5)

        # left form
        form_frame = ctk.CTkFrame(top_frame)
        form_frame.pack(side="left", fill="y", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Customer Name:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkLabel(form_frame, text="Contact:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkLabel(form_frame, text="Vehicle Type:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkLabel(form_frame, text="Brand:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkLabel(form_frame, text="Model:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5)

        self.entry_client_name = ctk.CTkEntry(form_frame, width=200)
        self.entry_client_contact = ctk.CTkEntry(form_frame, width=200)
        self.cb_vehicle_type = ctk.CTkComboBox(
            form_frame,
            values=["Sedan", "SUV", "Pick-up Truck", "Hybrid", "Crossover", "Van", "EV"]
        )
        self.cb_brand = ctk.CTkComboBox(
            form_frame,
            values=["Toyota", "Honda", "Mitsubishi", "Nissan", "Ford", "Suzuki", "Hyundai", "Others"]
        )
        self.entry_model = ctk.CTkEntry(form_frame, width=200)

        self.entry_client_name.grid(row=0, column=1, padx=5, pady=5)
        self.entry_client_contact.grid(row=1, column=1, padx=5, pady=5)
        self.cb_vehicle_type.grid(row=2, column=1, padx=5, pady=5)
        self.cb_brand.grid(row=3, column=1, padx=5, pady=5)
        self.entry_model.grid(row=4, column=1, padx=5, pady=5)

        btn_frame = ctk.CTkFrame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ctk.CTkButton(
            btn_frame, text="Clear",
            fg_color="gray30",
            command=self.clear_client_form
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, text="Save Client + Vehicle",
            command=self.save_client_vehicle
        ).pack(side="left", padx=5)

        # right table
        table_frame = ctk.CTkFrame(top_frame)
        table_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        columns = ("Customer Name", "Contact", "Vehicle Type", "Brand", "Model")
        style_clients = ttk.Style()
        style_clients.configure("Treeview", font=("Segoe UI", 12))
        style_clients.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        self.tree_clients = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=24
        )
        for col in columns:
            self.tree_clients.heading(col, text=col)
            self.tree_clients.column(col, width=140)
        self.tree_clients.pack(fill="both", expand=True)

        bottom_btns = ctk.CTkFrame(parent)
        bottom_btns.pack(fill="x", pady=5)
        ctk.CTkButton(
            bottom_btns, text="Refresh",
            command=lambda: self.refresh_clients_table()
        ).pack(side="right", padx=5)

    def clear_client_form(self):
        self.entry_client_name.delete(0, "end")
        self.entry_client_contact.delete(0, "end")
        self.cb_vehicle_type.set("")
        self.cb_brand.set("")
        self.entry_model.delete(0, "end")

    def save_client_vehicle(self):
        name = self.entry_client_name.get().strip()
        contact = self.entry_client_contact.get().strip()
        vtype = self.cb_vehicle_type.get().strip()
        brand = self.cb_brand.get().strip()
        model = self.entry_model.get().strip()

        if not name:
            messagebox.showerror("Validation", "Customer name is required.", parent=self)
            return
        if not vtype or not brand or not model:
            if not messagebox.askokcancel(
                "Confirm",
                "Vehicle Type, Brand or Model is empty.\nContinue?",
                parent=self
            ):
                return

        self.db.add_client_with_vehicle(name, contact, vtype, brand, model)
        messagebox.showinfo("Saved", "Client and vehicle saved.", parent=self)
        # clear form fields for next entry
        try:
            self.entry_client_name.delete(0, "end")
            self.entry_client_contact.delete(0, "end")
            self.cb_vehicle_type.set("")
            self.cb_brand.set("")
            self.entry_model.delete(0, "end")
        except Exception:
            pass
        # refresh client list after adding
        self.refresh_clients_table()

    def refresh_clients_table(self):
        """Reload the clients table with clients and their vehicles."""
        # clear existing rows
        for r in self.tree_clients.get_children():
            self.tree_clients.delete(r)

        rows = self.db.get_clients_with_vehicles()
        for cid, cname, contact, vid, vtype, brand, model in rows:
            vehicle_type = vtype or ""
            brand = brand or ""
            model = model or ""
            self.tree_clients.insert(
                "", "end",
                values=(cname or "", contact or "", vehicle_type, brand, model)
            )
        # also refresh service client/vehicle comboboxes so selections stay in sync
        try:
            self.refresh_service_clients()
        except Exception:
            pass

    # --- helper for service page ---

    def refresh_service_clients(self):
        rows = self.db.get_clients()
        values = [f"{cid} - {name}" for cid, name, _c in rows]
        self.cb_service_client.configure(values=values)
        if values:
            self.cb_service_client.set(values[0])
            self.refresh_service_vehicles()

    def refresh_service_vehicles(self):
        text = self.cb_service_client.get().strip()
        if not text:
            self.cb_service_vehicle.configure(values=[])
            return
        try:
            client_id = int(text.split("-")[0].strip())
        except Exception:
            self.cb_service_vehicle.configure(values=[])
            return
        rows = self.db.get_vehicles_for_client(client_id)
        vals = [f"{vid} - {vtype or ''} {brand or ''} {model or ''}".strip()
                for vid, vtype, brand, model in rows]
        self.cb_service_vehicle.configure(values=vals)
        if vals:
            self.cb_service_vehicle.set(vals[0])

    def refresh_specific_services(self):
        type_job = self.cb_type_job.get()
        services = []
        if type_job in SERVICE_CATALOG:
            services = [item["service"] for item in SERVICE_CATALOG[type_job]]
        self.cb_specific_service.configure(values=services)
        if services:
            self.cb_specific_service.set(services[0])
        else:
            self.cb_specific_service.set("")
        self.update_service_details()

    def find_service_info(self) -> Optional[Dict[str, Any]]:
        type_job = self.cb_type_job.get()
        service_name = self.cb_specific_service.get()
        if not type_job or type_job not in SERVICE_CATALOG:
            return None
        for item in SERVICE_CATALOG[type_job]:
            if item["service"] == service_name:
                return item
        return None

    def update_service_details(self):
        info = self.find_service_info()
        if not info:
            self.txt_parts.configure(state="normal")
            self.txt_parts.delete("0.0", "end")
            self.txt_parts.insert("end", "")
            self.txt_parts.configure(state="disabled")
            self.lbl_minor_price.configure(text="Minor Price: ₱0.00")
            self.lbl_major_price.configure(text="Major Price: ₱0.00")
            self.lbl_total_price.configure(text="Total Cost (selected): ₱0.00")
            self.lbl_mech1_name.configure(text="(mech1)")
            self.lbl_mech2_name.configure(text="(mech2)")
            self.lbl_mech3_name.configure(text="(mech3)")
            return

        # parts as checkboxes
        for widget in self.parts_frame.winfo_children():
            widget.destroy()
        self.part_vars = []
        parts_list = [p.strip() for p in info["parts"].split(",") if p.strip()]
        for i, part in enumerate(parts_list):
            var = ctk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(self.parts_frame, text=part, variable=var)
            chk.grid(row=i, column=0, sticky="w")
            self.part_vars.append((part, var))

        # mechanics
        m1 = info["mechanics"][0] if len(info["mechanics"]) > 0 else "(mech1)"
        m2 = info["mechanics"][1] if len(info["mechanics"]) > 1 else "(mech2)"
        m3 = info["mechanics"][2] if len(info["mechanics"]) > 2 else "(mech3)"     

        self.lbl_mech1_name.configure(text=m1)
        self.lbl_mech2_name.configure(text=m2)
        self.lbl_mech3_name.configure(text=m3)
        self.chk_mech1_var.set(True)
        self.chk_mech2_var.set(True)
        self.chk_mech3_var.set(True)

        # minor/major prices
        self.lbl_minor_price.configure(
            text=f"Minor Price: {peso(info['minor_price'])}"
        )
        self.lbl_major_price.configure(
            text=f"Major Price: {peso(info['major_price'])}"
        )

        # start + ETA preview
        start_date = now_date()
        start_time = now_time()
        eta_dt = datetime.datetime.now() + datetime.timedelta(
            minutes=info.get("time_minutes", 60)
        )
        eta_date = eta_dt.date().isoformat()
        eta_time = eta_dt.strftime("%H:%M")
        self.lbl_start_dt.configure(
            text=f"Start: {start_date} {start_time}"
        )
        self.lbl_eta_dt.configure(
            text=f"ETA Done: {eta_date} {eta_time} ({info['time_label']})"
        )

        self.update_service_price()

    def update_service_price(self):
        info = self.find_service_info()
        if not info:
            self.lbl_total_price.configure(text="Total Cost (selected): ₱0.00")
            return
        severity = self.cb_severity.get().strip().lower()
        base = info["minor_price"] if severity == "minor" else info["major_price"]
        self.lbl_total_price.configure(
            text=f"Total Cost (selected): {peso(base)}"
        )

    def add_diagnosis(self):
        # Dialog repeats service widgets so user picks Type, Service, Severity, Parts, Mechanics, Status
        dlg = ctk.CTkToplevel(self)
        dlg.title("Add Diagnosis (detailed)")
        dlg.geometry("480x420")
        dlg.transient(self)
        dlg.grab_set()

        frm = ctk.CTkFrame(dlg)
        frm.pack(fill="both", expand=True, padx=10, pady=8)

        # Type of Job
        ctk.CTkLabel(frm, text="Type of Job:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        type_cb = ctk.CTkComboBox(frm, values=TYPE_JOB_LIST, width=320,
                                   command=lambda _e=None: on_type_change())
        type_cb.grid(row=0, column=1, padx=5, pady=4)

        # Specific Service
        ctk.CTkLabel(frm, text="Specific Service:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        svc_cb = ctk.CTkComboBox(frm, values=[], width=320,
                                 command=lambda _e=None: on_service_change())
        svc_cb.grid(row=1, column=1, padx=5, pady=4)

        # Severity
        ctk.CTkLabel(frm, text="Type (Minor / Major):").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        sev_cb = ctk.CTkComboBox(frm, values=["Minor", "Major"], width=320,
                                 command=lambda _e=None: update_price_preview())
        sev_cb.grid(row=2, column=1, padx=5, pady=4)

        # Description (small)
        ctk.CTkLabel(frm, text="Description (optional):").grid(row=3, column=0, sticky="nw", padx=5, pady=4)
        txt_desc = ctk.CTkTextbox(frm, width=320, height=80)
        txt_desc.grid(row=3, column=1, padx=5, pady=4)

        # Auto parts
        ctk.CTkLabel(frm, text="Auto parts recommended:").grid(row=4, column=0, sticky="nw", padx=5, pady=4)
        parts_lbl = ctk.CTkLabel(frm, text="—", anchor="w")
        parts_lbl.grid(row=4, column=1, sticky="w", padx=5, pady=4)

        # Mechanics (two checkboxes + names)
        ctk.CTkLabel(frm, text="Assigned Mechanics:").grid(row=5, column=0, sticky="nw", padx=5, pady=4)
        mech_frame = ctk.CTkFrame(frm)
        mech_frame.grid(row=5, column=1, sticky="w", padx=5, pady=4)
        mech1_var = ctk.BooleanVar(value=True)
        mech2_var = ctk.BooleanVar(value=True)
        mech3_var = ctk.BooleanVar(value=True)
        mech1_chk = ctk.CTkCheckBox(mech_frame, text="", variable=mech1_var)
        mech2_chk = ctk.CTkCheckBox(mech_frame, text="", variable=mech2_var)
        mech3_chk = ctk.CTkCheckBox(mech_frame, text="", variable=mech3_var)
        mech1_name_lbl = ctk.CTkLabel(mech_frame, text="(mech1)")
        mech2_name_lbl = ctk.CTkLabel(mech_frame, text="(mech2)")
        mech3_name_lbl = ctk.CTkLabel(mech_frame, text="(mech3)")
        mech1_chk.grid(row=0, column=0, padx=2, pady=2)
        mech1_name_lbl.grid(row=0, column=1, padx=6, pady=2, sticky="w")
        mech2_chk.grid(row=1, column=0, padx=2, pady=2)
        mech2_name_lbl.grid(row=1, column=1, padx=6, pady=2, sticky="w")
        mech3_chk.grid(row=2, column=0, padx=2, pady=2)
        mech3_name_lbl.grid(row=2, column=1, padx=6, pady=2, sticky="w")

        # Status
        ctk.CTkLabel(frm, text="Status:").grid(row=6, column=0, sticky="w", padx=5, pady=6)
        status_cb = ctk.CTkComboBox(frm, values=STATUS_LIST, width=320)
        status_cb.grid(row=6, column=1, padx=5, pady=6)

        # Price preview
        price_lbl = ctk.CTkLabel(frm, text="Estimated Price: ₱0.00", font=ctk.CTkFont(weight="bold"))
        price_lbl.grid(row=7, column=0, columnspan=2, padx=5, pady=6)

        # Pre-fill with current main form selections if available
        try:
            cur_type = self.cb_type_job.get()
            if cur_type:
                type_cb.set(cur_type)
            cur_svc = self.cb_specific_service.get()
            if cur_svc:
                svc_cb.set(cur_svc)
            sev_cb.set(self.cb_severity.get() or "Minor")
            status_cb.set(self.cb_status.get() or "Check-in")
        except Exception:
            pass

        # Handlers
        def on_type_change():
            t = type_cb.get()
            svcs = []
            if t and t in SERVICE_CATALOG:
                svcs = [it["service"] for it in SERVICE_CATALOG[t]]
            svc_cb.configure(values=svcs)
            if svcs:
                svc_cb.set(svcs[0])
            else:
                svc_cb.set("")
            on_service_change()

        def on_service_change():
            info = None
            t = type_cb.get()
            s = svc_cb.get()
            if t in SERVICE_CATALOG:
                for it in SERVICE_CATALOG[t]:
                    if it["service"] == s:
                        info = it
                        break
            if info:
                parts_lbl.configure(text=info.get("parts","—"))
                mech1_name_lbl.configure(text=info["mechanics"][0] if len(info["mechanics"])>0 else "(mech1)")
                mech2_name_lbl.configure(text=info["mechanics"][1] if len(info["mechanics"])>1 else "(mech2)")
                mech3_name_lbl.configure(text=info["mechanics"][2] if len(info["mechanics"])>2 else "(mech3)")
            else:
                parts_lbl.configure(text="—")
                mech1_name_lbl.configure(text="(mech1)")
                mech2_name_lbl.configure(text="(mech2)")
                mech3_name_lbl.configure(text="(mech3)")
            update_price_preview()

        def update_price_preview():
            info = None
            t = type_cb.get(); s = svc_cb.get()
            if t in SERVICE_CATALOG:
                for it in SERVICE_CATALOG[t]:
                    if it["service"] == s:
                        info = it; break
            if not info:
                price_lbl.configure(text="Estimated Price: ₱0.00")
                return
            sev = sev_cb.get().strip().lower()
            base = info["minor_price"] if sev == "minor" else info["major_price"]
            price_lbl.configure(text=f"Estimated Price: {peso(base)}")

        # initialize dialog selections
        on_type_change()


        btns = ctk.CTkFrame(dlg)
        btns.pack(fill="x", padx=10, pady=8)
        def do_ok():
            t = type_cb.get().strip()
            s = svc_cb.get().strip()
            sev = sev_cb.get().strip()
            desc = txt_desc.get("0.0", "end").strip()
            parts = parts_lbl.cget("text")
            mechs = []
            if mech1_var.get():
                mechs.append(mech1_name_lbl.cget("text"))
            if mech2_var.get():
                mechs.append(mech2_name_lbl.cget("text"))
            if mech3_var.get():
                mechs.append(mech3_name_lbl.cget("text"))
            status = status_cb.get().strip() or "Check-in"
            est_price = price_lbl.cget("text").replace("Estimated Price: ","").strip()

            diag_lines = [
                "Diagnosis:",
                f"  Type of Job: {t}",
                f"  Specific Service: {s}",
                f"  Severity: {sev}",
                f"  Description: {desc}" if desc else "  Description: (none)",
                f"  Parts: {parts}",
                f"  Mechanics: {', '.join(mechs) if mechs else '(none)'}",
                f"  Status: {status}",
                f"  {est_price}",
                "-"*40
            ]
            new_text = ("\n".join(diag_lines)).strip()
            v_text = self.cb_service_vehicle.get().strip()
            if not v_text:
                messagebox.showerror("Validation", "Please select a vehicle to append diagnosis.", parent=dlg)
                return
            try:
                vehicle_id = int(v_text.split("-")[0].strip())
            except Exception:
                messagebox.showerror("Validation", "Invalid selected vehicle.", parent=dlg)
                return

            ok = self.db.append_vehicle_problem(vehicle_id, new_text)
            if not ok:
                messagebox.showerror("Error", "Failed to append diagnosis to vehicle.", parent=dlg)
                return

            # also create a repair order entry so it appears in Service table
            c_text = self.cb_service_client.get().strip()
            try:
                client_id = int(c_text.split("-")[0].strip())
            except Exception:
                client_id = None

            # determine mechanic names for DB insert
            mech1_name = mechs[0] if len(mechs) > 0 else None
            mech2_name = mechs[1] if len(mechs) > 1 else None
            mech3_name = mechs[2] if len(mechs) > 2 else None

            # find service info for ETA and fallback parts/prices
            info_local = None
            if t and t in SERVICE_CATALOG:
                for it in SERVICE_CATALOG[t]:
                    if it.get("service") == s:
                        info_local = it
                        break
            eta_minutes = info_local.get("time_minutes", 60) if info_local else 60

            # parse estimated price (string like '₱1,200.00')
            total_cost = 0.0
            try:
                p = est_price.replace('₱', '').replace(',', '')
                total_cost = float(p)
            except Exception:
                total_cost = 0.0

            # create repair order if we have a client id
            if client_id:
                try:
                    self.db.create_repair_order(
                        client_id=client_id,
                        vehicle_id=vehicle_id,
                        type_job=t,
                        specific_service=s,
                        severity=sev,
                        description=desc,
                        parts_recommended=parts,
                        mech1_name=mech1_name,
                        mech2_name=mech2_name,
                        mech3_name=mech3_name,
                        status=status,
                        eta_minutes=eta_minutes,
                        total_cost=total_cost,
                    )
                    # refresh service orders view elsewhere in UI
                    try:
                        self.refresh_orders_table()
                        self.refresh_dashboard()
                        self.refresh_reports()
                        self.refresh_history()
                    except Exception:
                        pass
                except Exception:
                    # if creating order fails, still keep diagnosis appended
                    messagebox.showwarning("Warning", "Diagnosis saved but failed to create repair order.", parent=dlg)

            messagebox.showinfo("Saved", "Diagnosis appended to vehicle problem and saved to service table.", parent=dlg)
            dlg.grab_release()
            dlg.destroy()

        def do_cancel():
            dlg.grab_release()
            dlg.destroy()

        ctk.CTkButton(btns, text="OK", command=do_ok).pack(side="right", padx=6)
        ctk.CTkButton(btns, text="Cancel", fg_color="gray30", command=do_cancel).pack(side="right", padx=6)

    def save_service(self):
        # validate client & vehicle
        c_text = self.cb_service_client.get().strip()
        v_text = self.cb_service_vehicle.get().strip()
        if not c_text:
            messagebox.showerror("Validation", "Please select a client.", parent=self)
            return
        if not v_text:
            messagebox.showerror("Validation", "Please select a vehicle.", parent=self)
            return
        try:
            client_id = int(c_text.split("-")[0].strip())
        except Exception:
            messagebox.showerror("Validation", "Invalid client.", parent=self)
            return
        try:
            vehicle_id = int(v_text.split("-")[0].strip())
        except Exception:
            messagebox.showerror("Validation", "Invalid vehicle.", parent=self)
            return

        info = self.find_service_info()
        if not info:
            messagebox.showerror("Validation", "Please select a valid Type Job and Service.", parent=self)
            return

        severity = self.cb_severity.get().strip()
        description = self.txt_description.get("0.0", "end").strip()
        # Only include checked parts
        selected_parts = [part for part, var in self.part_vars if var.get()]
        parts = ", ".join(selected_parts)

        print(f"[DEBUG] Saving repair order for client_id={client_id}, vehicle_id={vehicle_id}, service={info['service']}")


        m1 = info["mechanics"][0] if len(info["mechanics"]) > 0 else None
        m2 = info["mechanics"][1] if len(info["mechanics"]) > 1 else None

        mech1_name = m1 if self.chk_mech1_var.get() else None
        mech2_name = m2 if self.chk_mech2_var.get() else None
        mech3_name = m2 if self.chk_mech3_var.get() else None

        status = self.cb_status.get().strip() or "Check-in"
        eta_minutes = info.get("time_minutes", 60)

        # choose price based on severity
        if severity.lower() == "minor":
            total = float(info["minor_price"])
        else:
            total = float(info["major_price"])

        try:
            self.db.create_repair_order(
                client_id=client_id,
                vehicle_id=vehicle_id,
                type_job=self.cb_type_job.get(),
                specific_service=info["service"],
                severity=severity,
                description=description,
                parts_recommended=parts,
                mech1_name=mech1_name,
                mech2_name=mech2_name,
                mech3_name=mech3_name,
                status=status,
                eta_minutes=eta_minutes,
                total_cost=total,
            )
            print("[DEBUG] Repair order saved successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to save repair order: {e}")

        messagebox.showinfo("Saved", "Service / repair order saved.", parent=self)
        self.txt_description.delete("0.0", "end")
        self.refresh_orders_table()
        self.refresh_dashboard()
        self.refresh_reports()
        self.refresh_history()

    def refresh_orders_table(self):
        # Clear current rows
        for row in self.tree_orders.get_children():
            self.tree_orders.delete(row)


        rows = self.db.get_all_orders(exclude_completed=True)
        aggr = {}
        aggr_oids = {}
        for r in rows:
            oid, cname, _contact, vtype, brand, model, dstart, tstart, _dd, _td, service, status, total, _m1, _m2 = r
            vehicle = f"{vtype or ''} {brand or ''} {model or ''}".strip()
            key = (cname or "", vehicle)
            entry = aggr.get(key)
            oids = aggr_oids.get(key, [])
            if not entry:
                entry = {
                    "services": [],
                    "statuses": set(),
                    "total": 0.0,
                    "date": dstart or "",
                    "time": tstart or "",
                }
                aggr[key] = entry
                aggr_oids[key] = oids

            if service and service not in entry["services"]:
                entry["services"].append(service)
                oids.append(oid)
            if status:
                entry["statuses"].add(status)
            try:
                entry["total"] += float(total or 0.0)
            except Exception:
                pass

            # keep latest date/time display
            try:
                cur_date = entry["date"]
                cur_time = entry["time"]
                if dstart and (cur_date == "" or dstart > cur_date or (dstart == cur_date and (tstart or "") > (cur_time or ""))):
                    entry["date"] = dstart or ""
                    entry["time"] = tstart or ""
            except Exception:
                pass

        # Insert aggregated rows as parent -> child entries so services occupy separate lines
        idx = 0
        for (cname, vehicle), info in aggr.items():
            idx += 1
            parent_id = f"parent_{idx}"
            statuses = info["statuses"]
            status_str = ", ".join(statuses) if statuses else ""
            # Parent row shows client+vehicle and summary total
            self.tree_orders.insert(
                "", "end", iid=parent_id,
                values=("", cname, vehicle, "", status_str,
                        info["date"], info["time"], peso(info["total"]))
            )
            # Insert each service as a child row (separate line) WITH real oid id for mapping
            oids = aggr_oids[(cname, vehicle)]
            for i, svc in enumerate(info["services"]):
                oid_child = oids[i] if i < len(oids) else ""
                child_id = f"svc_{oid_child}"
                self.tree_orders.insert(
                    parent_id, "end", iid=child_id,
                    values=(oid_child, "", "", svc or "", "", "", "", "")
                )
            # expand parent to show child services by default
            try:
                self.tree_orders.item(parent_id, open=True)
            except Exception:
                pass

    def mark_order_done(self):
        sel = self.tree_orders.selection()
        if not sel:
            messagebox.showinfo("Info", "Please select a repair order.", parent=self)
            return
        oids_to_mark = []

        # Collect oids to mark done depending on selected type (parent or child row)
        for s in sel:
            values = self.tree_orders.item(s)["values"]
            oid = values[0]
            cname = values[1]
            vehicle = values[2]
            if oid and str(oid).isdigit():
                # child row with oid
                oids_to_mark.append(int(oid))
            else:
                # parent row without oid, mark all child orders under this parent
                child_ids = self.tree_orders.get_children(s)
                for cid in child_ids:
                    c_values = self.tree_orders.item(cid)["values"]
                    c_oid = c_values[0]
                    if c_oid and str(c_oid).isdigit():
                        oids_to_mark.append(int(c_oid))
                # If no child found, try to mark by client name (cname) all open orders
                if not child_ids and cname:
                    # Query DB for all open orders for client cname (status not Pickup)
                    rows_open = self.db.get_all_orders(client_name_filter=cname)
                    for r in rows_open:
                        c_oid = r[0]
                        c_status = r[11]
                        if c_oid and str(c_oid).isdigit() and c_status != "Pickup":
                            oids_to_mark.append(int(c_oid))

        if not oids_to_mark:
            messagebox.showerror("Invalid Selection", "Please select a valid repair order (not a summary row).", parent=self)
            return

        if not messagebox.askokcancel("Confirm", f"Mark {len(oids_to_mark)} order(s) as Pickup?", parent=self):
            return

        for oid in oids_to_mark:
            self.db.set_repair_status(oid, "Pickup")

        self.refresh_orders_table()
        self.refresh_dashboard()
        self.refresh_reports()
        self.refresh_history()


    # =========================================================
    #  REPORTS PAGE
    # =========================================================

    def build_reports_page(self, parent: ctk.CTkFrame):
        title = ctk.CTkLabel(
            parent, text="Reports",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(anchor="w", pady=10)

        # Search client
        search_frame = ctk.CTkFrame(parent)
        search_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(search_frame, text="Search Client:").pack(
            side="left", padx=5
        )
        self.entry_report_client = ctk.CTkEntry(search_frame, width=200)
        self.entry_report_client.pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame, text="Show",
            command=self.refresh_reports
        ).pack(side="left", padx=5)

        # Sales by month
        sales_frame = ctk.CTkFrame(parent)
        sales_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(sales_frame, text="Sales by Month - Year:").pack(
            side="left", padx=5
        )
        self.entry_sales_year = ctk.CTkEntry(sales_frame, width=70)
        self.entry_sales_year.pack(side="left", padx=5)
        self.entry_sales_year.insert("end", str(datetime.date.today().year))

        ctk.CTkLabel(sales_frame, text="Month (1-12):").pack(
            side="left", padx=5
        )
        self.entry_sales_month = ctk.CTkEntry(sales_frame, width=40)
        self.entry_sales_month.pack(side="left", padx=5)
        self.entry_sales_month.insert("end", str(datetime.date.today().month))

        ctk.CTkButton(
            sales_frame, text="Show",
            command=self.show_sales_by_month
        ).pack(side="left", padx=5)

        self.lbl_sales_month = ctk.CTkLabel(
            sales_frame, text="Total: ₱0.00",
            font=ctk.CTkFont(weight="bold")
        )
        self.lbl_sales_month.pack(side="left", padx=15)

        # Tables (All Service + Mechanic summary)
        bottom = ctk.CTkFrame(parent)
        bottom.pack(fill="both", expand=True, pady=5)

        left = ctk.CTkFrame(bottom)
        left.pack(side="left", fill="both", expand=True, padx=5)


        ctk.CTkLabel(
                left, text="All Service (Repair Orders)",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(anchor="w", pady=5)

        cols = (
                "Client", "Contact",
                "Vehicle Type", "Brand", "Model",
                "Start Date/Time", "Done Date/Time",
                "Mechanic(s)", "Total Cost"
            )
        style_report = ttk.Style()
        style_report.configure("Treeview", font=("Segoe UI", 12))
        style_report.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        self.tree_report_orders = ttk.Treeview(
            left, columns=cols, show="headings", height=28
        )
        for col in cols:
                self.tree_report_orders.heading(col, text=col)
                self.tree_report_orders.column(col, width=120)
        self.tree_report_orders.pack(fill="both", expand=True, pady=(0,2))

            # Mechanic summary table below clients
        ctk.CTkLabel(
                left, text="Mechanic Summary",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(anchor="w", pady=5)

        mech_cols = ("Mechanic Name", "Contact", "Done Repairs", "Total Sales")
        style_mech = ttk.Style()
        style_mech.configure("Treeview", font=("Segoe UI", 12))
        style_mech.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        self.tree_mech_summary = ttk.Treeview(
                left, columns=mech_cols, show="headings", height=12
            )
        for col in mech_cols:
                self.tree_mech_summary.heading(col, text=col)
                self.tree_mech_summary.column(col, width=140)
        self.tree_mech_summary.pack(fill="both", expand=True, pady=(0,10))

    def refresh_reports(self):
        # All service table (filter by client name if provided)
        for r in self.tree_report_orders.get_children():
            self.tree_report_orders.delete(r)

        filter_name = self.entry_report_client.get().strip()
        rows = self.db.get_all_orders(filter_name, exclude_completed=False)

            # Mechanic summary table
        for r in self.tree_mech_summary.get_children():
                self.tree_mech_summary.delete(r)

        mech_rows = self.db.get_mechanic_summary()
        for mname, contact, repairs, total_sales in mech_rows:
                self.tree_mech_summary.insert(
                    "", "end",
                    values=(mname, contact or "", repairs or 0, peso(total_sales or 0))
                )
        for row in rows:
            (
                _oid,
                cname, contact,
                vtype, brand, model,
                dstart, tstart,
                ddone, tdone,
                service, _status, total,
                m1, m2
            ) = row
            vehicle_type = vtype or ""
            brand = brand or ""
            model = model or ""
            start_dt = f"{dstart or ''} {tstart or ''}".strip()
            done_dt = f"{ddone or ''} {tdone or ''}".strip()
            mechs_list = [m for m in [m1, m2] if m]
            mechs = ", ".join(mechs_list) if mechs_list else ""
            self.tree_report_orders.insert(
                "", "end",
                values=(
                    cname or "", contact or "",
                    vehicle_type, brand, model,
                    start_dt, done_dt,
                    mechs, peso(total or 0),
                )
            )

    def show_sales_by_month(self):
        try:
            year = int(self.entry_sales_year.get().strip())
            month = int(self.entry_sales_month.get().strip())
        except Exception:
            messagebox.showerror("Error", "Invalid year or month.", parent=self)
            return
        if not (1 <= month <= 12):
            messagebox.showerror("Error", "Month must be 1–12.", parent=self)
            return
        total = self.db.get_sales_by_month(year, month)
        self.lbl_sales_month.configure(text=f"Total: {peso(total)}")


    #  CLIENT HISTORY PAGE
    def build_history_page(self, parent: ctk.CTkFrame):

        title = ctk.CTkLabel(
            parent, text="Today's History",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(anchor="w", pady=10)

        ctk.CTkLabel(
            parent, text="Service History (Today Only)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=5)

        cols = (
            "Client", "Contact", "Vehicle",
            "Service", "Start Date/Time",
            "Done Date/Time", "Total Cost"
        )
        style_history = ttk.Style()
        style_history.configure("Treeview", font=("Segoe UI", 12))
        style_history.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
        self.tree_history = ttk.Treeview(
            parent, columns=cols, show="headings", height=32
        )
        for col in cols:
            self.tree_history.heading(col, text=col)
            self.tree_history.column(col, width=130)
        self.tree_history.pack(fill="both", expand=True, pady=5)

    def refresh_history(self):
        for r in self.tree_history.get_children():
            self.tree_history.delete(r)
        today = now_date()
        rows = self.db.execute(
            f"""
            SELECT ro.id,
                   c.name, c.contact,
                   v.vehicle_type, v.brand, v.model,
                   ro.date_start, ro.time_start,
                   ro.date_done, ro.time_done,
                   ro.specific_service,
                   ro.status,
                   ro.total_cost,
                   m1.name, m2.name
            FROM repair_orders ro
            JOIN clients c ON c.id = ro.client_id
            JOIN vehicles v ON v.id = ro.vehicle_id
            LEFT JOIN mechanics m1 ON m1.id = ro.mechanic1_id
            LEFT JOIN mechanics m2 ON m2.id = ro.mechanic2_id
            WHERE ro.date_start = ?
            ORDER BY ro.date_start DESC, ro.time_start DESC
            """,
            (today,), fetch=True
        )

        for row in rows:
            (
                _oid,
                cname, contact,
                vtype, brand, model,
                dstart, tstart,
                ddone, tdone,
                service, _status, total,
                _m1, _m2
            ) = row
            vehicle = f"{vtype or ''} {brand or ''} {model or ''}".strip()
            start_dt = f"{dstart or ''} {tstart or ''}".strip()
            done_dt = f"{ddone or ''} {tdone or ''}".strip()
            self.tree_history.insert(
                "", "end",
                values=(
                    cname or "", contact or "",
                    vehicle,
                    service or "",
                    start_dt,
                    done_dt,
                    peso(total or 0),
                )
            )

    def clear_history_search(self):
        self.entry_history_client.delete(0, "end")
        self.refresh_history()



# main application

