# app.py
import customtkinter as ctk
from tkinter import messagebox

from config import APP_TITLE
from db import DB
from login_dialog import LoginDialog
from ui_dashboard import DashboardPage
from ui_client import ClientPage
from ui_service import ServicePage
from ui_reports import ReportsPage
from ui_history import HistoryPage


class EVAutoRepairApp(ctk.CTk):
    def __init__(self, db: DB):
        super().__init__()
        self.db = db
        self.title(APP_TITLE)
        self.geometry("1200x720")
        self.minsize(1100, 650)

        self.current_user = None

        # Top bar
        self.top_bar = ctk.CTkFrame(self, height=50)
        self.top_bar.pack(side="top", fill="x")

        self.lbl_title = ctk.CTkLabel(
            self.top_bar,
            text=APP_TITLE,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.lbl_title.pack(side="left", padx=15)

        self.lbl_user = ctk.CTkLabel(
            self.top_bar,
            text="Not logged in",
            font=ctk.CTkFont(size=13)
        )
        self.lbl_user.pack(side="right", padx=15)

        # Main area
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="top", fill="both", expand=True)

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

    # ---------- login flow ----------

    def show_login(self):
        LoginDialog(self, self.db, self.on_login_success)

    def on_login_success(self, username: str):
        self.current_user = username
        self.deiconify()
        self.lbl_user.configure(text=f"Logged in as: {username}")

        self.show_page("Dashboard")
        # initial refresh for all pages
        for p in self.pages.values():
            if hasattr(p, "refresh"):
                p.refresh()

    # ---------- menu + pages ----------

    def create_menu(self):
        def add_menu_button(text, key):
            btn = ctk.CTkButton(
                self.menu_frame,
                text=text,
                anchor="w",
                command=lambda k=key: self.show_page(k)
            )
            btn.pack(fill="x", padx=10, pady=5)
            self.menu_buttons[key] = btn

        add_menu_button("Dashboard", "Dashboard")
        add_menu_button("Client", "Client")
        add_menu_button("Service", "Service")
        add_menu_button("Reports", "Reports")
        add_menu_button("Client History", "History")

        ctk.CTkButton(
            self.menu_frame,
            text="Logout",
            fg_color="red4",
            hover_color="red3",
            command=self.handle_logout
        ).pack(side="bottom", fill="x", padx=10, pady=10)

    def create_pages(self):
        self.pages["Dashboard"] = DashboardPage(self.content_frame, self, self.db)
        self.pages["Client"] = ClientPage(self.content_frame, self, self.db)
        self.pages["Service"] = ServicePage(self.content_frame, self, self.db)
        self.pages["Reports"] = ReportsPage(self.content_frame, self, self.db)
        self.pages["History"] = HistoryPage(self.content_frame, self, self.db)

    def show_page(self, key: str):
        for k, page in self.pages.items():
            page.pack_forget()
        frame = self.pages.get(key)
        if frame:
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            if hasattr(frame, "refresh"):
                frame.refresh()

    def handle_logout(self):
        if not messagebox.askokcancel("Logout", "Are you sure you want to logout?", parent=self):
            return
        self.current_user = None
        self.withdraw()
        self.show_login()

