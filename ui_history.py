import customtkinter as ctk
from tkinter import ttk

from config import now_date, peso
from db import DB


class HistoryPage(ctk.CTkFrame):
    def __init__(self, parent, controller, db: DB):
        super().__init__(parent)
        self.controller = controller
        self.db = db

        title = ctk.CTkLabel(
            self, text="Today's History",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(anchor="w", pady=10)

        ctk.CTkLabel(
            self, text="Service History (Today Only)",
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
            self, columns=cols, show="headings", height=32
        )
        for col in cols:
            self.tree_history.heading(col, text=col)
            self.tree_history.column(col, width=130)
        self.tree_history.pack(fill="both", expand=True, pady=5)

    def refresh(self):
        self.refresh_history()

    def refresh_history(self):
        for r in self.tree_history.get_children():
            self.tree_history.delete(r)
        today = now_date()
        rows = self.db.execute(
            """
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

