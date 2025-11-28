import customtkinter as ctk
from tkinter import messagebox
from typing import Callable

from db import DB

class LoginDialog(ctk.CTkToplevel):
    def __init__(self, parent, db: DB, on_success):
        super().__init__(parent)
        self.db = db
        self.on_success = on_success
        self.title("EV Auto Repairshop Admin Login")
        self.geometry("380x230")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        title_label = ctk.CTkLabel(
            self, text="EV Auto Repairshop Admin Login",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=10, padx=10)

        form = ctk.CTkFrame(self)
        form.pack(padx=15, pady=10, fill="x")

        ctk.CTkLabel(form, text="Username:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ctk.CTkLabel(form, text="Password:").grid(row=1, column=0, sticky="e", padx=5, pady=5)

        self.entry_user = ctk.CTkEntry(form, width=200)
        self.entry_pass = ctk.CTkEntry(form, width=200, show="*")
        self.entry_user.grid(row=0, column=1, padx=5, pady=5)
        self.entry_pass.grid(row=1, column=1, padx=5, pady=5)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Login", width=100, command=self.handle_login).pack(
            side="left", padx=5
        )
        ctk.CTkButton(btn_frame, text="Exit", width=100, fg_color="gray30",
                      command=self.handle_exit).pack(side="left", padx=5)

        self.entry_user.focus()
        self.bind("<Return>", lambda e: self.handle_login())

    def handle_login(self):
        u = self.entry_user.get().strip()
        p = self.entry_pass.get().strip()
        if not u or not p:
            messagebox.showerror("Login", "Please enter username and password.", parent=self)
            return
        if not self.db.verify_admin(u, p):
            messagebox.showerror("Login", "Invalid credentials.", parent=self)
            return
        self.grab_release()
        self.destroy()
        self.on_success(u)

    def handle_exit(self):
        self.grab_release()
        self.master.destroy()

