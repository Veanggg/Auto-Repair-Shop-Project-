# ui_dashboard.py
import datetime
import customtkinter as ctk

from config import peso
from db import DB


class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, controller, db: DB):
        super().__init__(parent)
        self.controller = controller
        self.db = db

        title = ctk.CTkLabel(
            self, text="Dashboard - Today's Overview",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(anchor="w", pady=10)

        cards_row = ctk.CTkFrame(self)
        cards_row.pack(fill="x", pady=8)

        all_title = ctk.CTkLabel(
            self, text="All Overview - This Month",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        all_title.pack(anchor="w", pady=(18, 8))

        all_cards_row = ctk.CTkFrame(self)
        all_cards_row.pack(fill="x", pady=8)

        def make_all_card(parent, caption, initial):
            card = ctk.CTkFrame(parent, corner_radius=8, border_width=1)
            card.pack(side="left", expand=True, fill="both", padx=8, pady=4)
            val_lbl = ctk.CTkLabel(card, text=initial,
                                   font=ctk.CTkFont(size=32, weight="bold"))
            val_lbl.pack(anchor="center", pady=(18, 6))
            cap_lbl = ctk.CTkLabel(card, text=caption,
                                   font=ctk.CTkFont(size=12))
            cap_lbl.pack(anchor="center", pady=(0, 18))
            return val_lbl

        # monthly cards
        self.lbl_monthly_sales = make_all_card(all_cards_row, "Monthly Sales", "₱0.00")
        self.lbl_monthly_total_repairs = make_all_card(all_cards_row, "Total Repairs This Month", "0")
        self.lbl_monthly_inprogress = make_all_card(all_cards_row, "In-progress Repairs This Month", "0")
        self.lbl_monthly_done = make_all_card(all_cards_row, "Done Repairs This Month", "0")

        def make_card(parent, caption, initial):
            card = ctk.CTkFrame(parent, corner_radius=8, border_width=1)
            card.pack(side="left", expand=True, fill="both", padx=8, pady=4)
            val_lbl = ctk.CTkLabel(card, text=initial,
                                   font=ctk.CTkFont(size=32, weight="bold"))
            val_lbl.pack(anchor="center", pady=(18, 6))
            cap_lbl = ctk.CTkLabel(card, text=caption,
                                   font=ctk.CTkFont(size=12))
            cap_lbl.pack(anchor="center", pady=(0, 18))
            return val_lbl

        # today's overview
        self.lbl_sales_value = make_card(cards_row, "Today's Sales", "₱0.00")
        self.lbl_total_repairs_value = make_card(cards_row, "Total Repairs Today", "0")
        self.lbl_inprogress_value = make_card(cards_row, "In-progress Repairs", "0")
        self.lbl_done_value = make_card(cards_row, "Done Repairs", "0")

        refresh_btn = ctk.CTkButton(self, text="Refresh", command=self.refresh)
        refresh_btn.pack(anchor="w", pady=8)

    def refresh(self):
        stats = self.db.get_today_stats()
        try:
            self.lbl_sales_value.configure(text=peso(stats['today_sales']))
        except Exception:
            self.lbl_sales_value.configure(text="₱0.00")
        try:
            self.lbl_total_repairs_value.configure(text=str(int(stats['total_repairs'] or 0)))
        except Exception:
            self.lbl_total_repairs_value.configure(text="0")
        try:
            self.lbl_inprogress_value.configure(text=str(int(stats['in_progress'] or 0)))
        except Exception:
            self.lbl_inprogress_value.configure(text="0")
        try:
            self.lbl_done_value.configure(text=str(int(stats['done_repairs'] or 0)))
        except Exception:
            self.lbl_done_value.configure(text="0")

        # Monthly overview
        now = datetime.datetime.now()
        year = now.year
        month = now.month

        try:
            monthly_sales = self.db.get_sales_by_month(year, month)
            self.lbl_monthly_sales.configure(text=peso(monthly_sales))
        except Exception:
            self.lbl_monthly_sales.configure(text="₱0.00")

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
            self.lbl_monthly_total_repairs.configure(text=str(total_repairs))
            self.lbl_monthly_inprogress.configure(text=str(inprogress))
            self.lbl_monthly_done.configure(text=str(done))
        except Exception:
            self.lbl_monthly_total_repairs.configure(text="0")
            self.lbl_monthly_inprogress.configure(text="0")
            self.lbl_monthly_done.configure(text="0")

