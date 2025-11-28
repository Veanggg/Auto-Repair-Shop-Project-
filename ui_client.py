# ui_client.py
import customtkinter as ctk
from tkinter import ttk, messagebox

from db import DB


class ClientPage(ctk.CTkFrame):
    def __init__(self, parent, controller, db: DB):
        super().__init__(parent)
        self.controller = controller
        self.db = db

        title = ctk.CTkLabel(
            self, text="Clients & Vehicles",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(anchor="w", pady=10)

        top_frame = ctk.CTkFrame(self)
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
            values=["Sedan", "SUV", "Pick-up", "Hybrid", "Crossover", "Van", "MPV"]
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
            command=self.clear_form
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

        bottom_btns = ctk.CTkFrame(self)
        bottom_btns.pack(fill="x", pady=5)
        ctk.CTkButton(
            bottom_btns, text="Refresh",
            command=self.refresh
        ).pack(side="right", padx=5)

    # ---------- public for controller ----------

    def refresh(self):
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

    # ---------- actions ----------

    def clear_form(self):
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
        self.clear_form()
        self.refresh()

        # Also refresh service client combobox
        service_page = self.controller.pages.get("Service")
        if service_page and hasattr(service_page, "refresh_clients_from_outside"):
            service_page.refresh_clients_from_outside()

