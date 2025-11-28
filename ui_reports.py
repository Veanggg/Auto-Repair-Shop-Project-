# ui_reports.py
import customtkinter as ctk
from tkinter import ttk, messagebox

from config import peso
from db import DB


class ReportsPage(ctk.CTkFrame):
    def __init__(self, parent, controller, db: DB):
        super().__init__(parent)
        self.controller = controller
        self.db = db

        title = ctk.CTkLabel(
            self, text="Reports",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(anchor="w", pady=10)

        # Search client
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(search_frame, text="Search Client:").pack(side="left", padx=5)
        self.entry_report_client = ctk.CTkEntry(search_frame, width=200)
        self.entry_report_client.pack(side="left", padx=5)

        ctk.CTkButton(search_frame, text="Show",
                      command=self.refresh_reports).pack(side="left", padx=5)

        # Sales by month
        import datetime as _dt
        sales_frame = ctk.CTkFrame(self)
        sales_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(sales_frame, text="Sales by Month - Year:").pack(side="left", padx=5)
        self.entry_sales_year = ctk.CTkEntry(sales_frame, width=70)
        self.entry_sales_year.pack(side="left", padx=5)
        self.entry_sales_year.insert("end", str(_dt.date.today().year))

        ctk.CTkLabel(sales_frame, text="Month (1-12):").pack(side="left", padx=5)
        self.entry_sales_month = ctk.CTkEntry(sales_frame, width=40)
        self.entry_sales_month.pack(side="left", padx=5)
        self.entry_sales_month.insert("end", str(_dt.date.today().month))

        ctk.CTkButton(
            sales_frame, text="Show",
            command=self.show_sales_by_month
        ).pack(side="left", padx=5)

        self.lbl_sales_month = ctk.CTkLabel(
            sales_frame, text="Total: ₱0.00",
            font=ctk.CTkFont(weight="bold")
        )
        self.lbl_sales_month.pack(side="left", padx=15)

        # Tables
        bottom = ctk.CTkFrame(self)
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
        self.tree_report_orders.pack(fill="both", expand=True, pady=(0, 2))

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
        self.tree_mech_summary.pack(fill="both", expand=True, pady=(0, 10))

    def refresh(self):
        self.refresh_reports()

    def refresh_reports(self):
        # All service table
        for r in self.tree_report_orders.get_children():
            self.tree_report_orders.delete(r)

        filter_name = self.entry_report_client.get().strip()
        rows = self.db.get_all_orders(filter_name, exclude_completed=False)

        for row in rows:
            (
                _oid,
                cname, contact,
                vtype, brand, model,
                dstart, tstart,
                ddone, tdone,
                _service, _status, total,
                m1, m2, m3
            ) = row
            vehicle_type = vtype or ""
            brand = brand or ""
            model = model or ""
            start_dt = f"{dstart or ''} {tstart or ''}".strip()
            done_dt = f"{ddone or ''} {tdone or ''}".strip()
            mechs_list = [m for m in [m1, m2, m3] if m]
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

        # mechanic summary
        for r in self.tree_mech_summary.get_children():
            self.tree_mech_summary.delete(r)

        mech_rows = self.db.get_mechanic_summary()
        for mname, contact, repairs, total_sales in mech_rows:
            self.tree_mech_summary.insert(
                "", "end",
                values=(mname, contact or "", repairs or 0, peso(total_sales or 0))
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

