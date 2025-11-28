# ui_service.py
import datetime
from typing import Optional, Dict, Any, List

import customtkinter as ctk
from tkinter import ttk, messagebox

from config import (
    SERVICE_CATALOG,
    TYPE_JOB_LIST,
    STATUS_LIST,
    now_date,
    now_time,
    peso,
)
from db import DB


class ServicePage(ctk.CTkFrame):
    def __init__(self, parent, controller, db: DB):
        super().__init__(parent)
        self.controller = controller
        self.db = db

        self.part_vars: List = []

        title = ctk.CTkLabel(
            self, text="Service - Add Repair / Job",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(anchor="w", pady=10)

        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True)

        left = ctk.CTkFrame(main)
        left.pack(side="left", fill="y", padx=5, pady=5)

        right = ctk.CTkFrame(main)
        right.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # ---------- LEFT: FORM ----------

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

        ctk.CTkLabel(left, text="Type of Job:").grid(
            row=2, column=0, sticky="w", padx=5, pady=3)
        self.cb_type_job = ctk.CTkComboBox(
            left, values=TYPE_JOB_LIST, width=260,
            command=lambda _e=None: self.refresh_specific_services()
        )
        self.cb_type_job.grid(row=2, column=1, padx=5, pady=3)

        ctk.CTkLabel(left, text="Specific Service:").grid(
            row=3, column=0, sticky="w", padx=5, pady=3)
        self.cb_specific_service = ctk.CTkComboBox(
            left, values=[], width=260,
            command=lambda _e=None: self.update_service_details()
        )
        self.cb_specific_service.grid(row=3, column=1, padx=5, pady=3)

        ctk.CTkLabel(left, text="Type (Minor / Major):").grid(
            row=4, column=0, sticky="w", padx=5, pady=3)
        self.cb_severity = ctk.CTkComboBox(
            left, values=["Minor", "Major"], width=260,
            command=lambda _e=None: self.update_service_price()
        )
        self.cb_severity.grid(row=4, column=1, padx=5, pady=3)
        self.cb_severity.set("Minor")

        ctk.CTkLabel(left, text="Description (optional):").grid(
            row=5, column=0, sticky="nw", padx=5, pady=3)
        self.txt_description = ctk.CTkTextbox(left, width=260, height=60)
        self.txt_description.grid(row=5, column=1, padx=5, pady=3)

        ctk.CTkLabel(left, text="Auto parts recommended:").grid(
            row=6, column=0, sticky="nw", padx=5, pady=3)
        self.parts_frame = ctk.CTkFrame(left)
        self.parts_frame.grid(row=6, column=1, padx=5, pady=3, sticky="w")

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

        self.chk_mech1 = ctk.CTkCheckBox(mech_frame, text="", variable=self.chk_mech1_var)
        self.chk_mech2 = ctk.CTkCheckBox(mech_frame, text="", variable=self.chk_mech2_var)
        self.chk_mech3 = ctk.CTkCheckBox(mech_frame, text="", variable=self.chk_mech3_var)

        self.chk_mech1.grid(row=0, column=0, padx=2)
        self.lbl_mech1_name.grid(row=0, column=1, padx=2)
        self.chk_mech2.grid(row=1, column=0, padx=2)
        self.lbl_mech2_name.grid(row=1, column=1, padx=2)
        self.chk_mech3.grid(row=2, column=0, padx=2)
        self.lbl_mech3_name.grid(row=2, column=1, padx=2)

        ctk.CTkLabel(left, text="Status:").grid(
            row=8, column=0, sticky="w", padx=5, pady=3)
        self.cb_status = ctk.CTkComboBox(left, values=STATUS_LIST, width=260)
        self.cb_status.grid(row=8, column=1, padx=5, pady=3)
        self.cb_status.set("Check-in")

        eta_frame = ctk.CTkFrame(left)
        eta_frame.grid(row=9, column=0, columnspan=2, sticky="w", padx=5, pady=3)

        self.lbl_start_dt = ctk.CTkLabel(eta_frame, text="Start: - / -")
        self.lbl_eta_dt = ctk.CTkLabel(eta_frame, text="Est. Time Done: - / -")
        self.lbl_start_dt.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.lbl_eta_dt.grid(row=1, column=0, padx=5, pady=2, sticky="w")

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

        btn_frame = ctk.CTkFrame(left)
        btn_frame.grid(row=11, column=0, columnspan=2, pady=10)

        ctk.CTkButton(btn_frame, text="Save service", command=self.save_service).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Add Diagnosis", fg_color="gray25",
                      command=self.add_diagnosis).pack(side="left", padx=5)

        # ---------- RIGHT: ORDERS TABLE ----------

        ctk.CTkLabel(
            right, text="Existing Repair Orders",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=5)

        table_frame = ctk.CTkFrame(right)
        table_frame.pack(fill="both", expand=True)

        columns = ("ID", "Client", "Vehicle", "Service", "Status", "Date", "Time", "Total")
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
        try:
            self.tree_orders.column("ID", width=0, minwidth=0, stretch=False)
        except Exception:
            pass
        self.tree_orders.pack(fill="both", expand=True)

        btn2_frame = ctk.CTkFrame(right)
        btn2_frame.pack(fill="x", pady=5)

        self.chk_show_completed_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            btn2_frame, text="Show Completed Orders",
            variable=self.chk_show_completed_var,
            command=self.refresh_orders_table
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            btn2_frame, text="Refresh",
            command=self.refresh_orders_table
        ).pack(side="right", padx=5)
        ctk.CTkButton(
            btn2_frame, text="Mark as Done (Pickup)",
            command=self.mark_order_done
        ).pack(side="right", padx=5)

    # ---------- public API ----------

    def refresh(self):
        self.refresh_service_clients()
        self.refresh_orders_table()
        self.update_service_details()

    def refresh_clients_from_outside(self):
        self.refresh_service_clients()

    # ---------- helpers for combos ----------

    def refresh_service_clients(self):
        rows = self.db.get_clients()
        values = [f"{cid} - {name}" for cid, name, _c in rows]
        self.cb_service_client.configure(values=values)
        if values:
            if not self.cb_service_client.get():
                self.cb_service_client.set(values[0])
            self.refresh_service_vehicles()
        else:
            self.cb_service_client.set("")
            self.cb_service_vehicle.configure(values=[])
            self.cb_service_vehicle.set("")

    def refresh_service_vehicles(self):
        text = self.cb_service_client.get().strip()
        if not text:
            self.cb_service_vehicle.configure(values=[])
            self.cb_service_vehicle.set("")
            return
        try:
            client_id = int(text.split("-")[0].strip())
        except Exception:
            self.cb_service_vehicle.configure(values=[])
            self.cb_service_vehicle.set("")
            return
        rows = self.db.get_vehicles_for_client(client_id)
        vals = [f"{vid} - {vtype or ''} {brand or ''} {model or ''}".strip()
                for vid, vtype, brand, model in rows]
        self.cb_service_vehicle.configure(values=vals)
        if vals:
            if not self.cb_service_vehicle.get():
                self.cb_service_vehicle.set(vals[0])
        else:
            self.cb_service_vehicle.set("")

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
            for widget in self.parts_frame.winfo_children():
                widget.destroy()
            self.part_vars = []
            self.lbl_minor_price.configure(text="Minor Price: ₱0.00")
            self.lbl_major_price.configure(text="Major Price: ₱0.00")
            self.lbl_total_price.configure(text="Total Cost (selected): ₱0.00")
            self.lbl_mech1_name.configure(text="(mech1)")
            self.lbl_mech2_name.configure(text="(mech2)")
            self.lbl_mech3_name.configure(text="(mech3)")
            self.lbl_start_dt.configure(text="Start: - / -")
            self.lbl_eta_dt.configure(text="Est. Time Done: - / -")
            return

        for widget in self.parts_frame.winfo_children():
            widget.destroy()
        self.part_vars = []
        parts_list = [p.strip() for p in info["parts"].split(",") if p.strip()]
        for i, part in enumerate(parts_list):
            var = ctk.BooleanVar(value=True)
            chk = ctk.CTkCheckBox(self.parts_frame, text=part, variable=var)
            chk.grid(row=i, column=0, sticky="w")
            self.part_vars.append((part, var))

        m1 = info["mechanics"][0] if len(info["mechanics"]) > 0 else "(mech1)"
        m2 = info["mechanics"][1] if len(info["mechanics"]) > 1 else "(mech2)"
        m3 = info["mechanics"][2] if len(info["mechanics"]) > 2 else "(mech3)"

        self.lbl_mech1_name.configure(text=m1)
        self.lbl_mech2_name.configure(text=m2)
        self.lbl_mech3_name.configure(text=m3)
        self.chk_mech1_var.set(True)
        self.chk_mech2_var.set(True)
        self.chk_mech3_var.set(True)

        self.lbl_minor_price.configure(text=f"Minor Price: {peso(info['minor_price'])}")
        self.lbl_major_price.configure(text=f"Major Price: {peso(info['major_price'])}")

        start_date = now_date()
        start_time = now_time()
        eta_dt = datetime.datetime.now() + datetime.timedelta(
            minutes=info.get("time_minutes", 60)
        )
        eta_date = eta_dt.date().isoformat()
        eta_time = eta_dt.strftime("%H:%M")
        self.lbl_start_dt.configure(text=f"Start: {start_date} {start_time}")
        self.lbl_eta_dt.configure(
            text=f"Est. Time Done: {eta_date} {eta_time} ({info['time_label']})"
        )

        self.update_service_price()

    def update_service_price(self):
        info = self.find_service_info()
        if not info:
            self.lbl_total_price.configure(text="Total Cost (selected): ₱0.00")
            return
        severity = self.cb_severity.get().strip().lower()
        base = info["minor_price"] if severity == "minor" else info["major_price"]
        self.lbl_total_price.configure(text=f"Total Cost (selected): {peso(base)}")

    # ---------- diagnosis dialog ----------

    def add_diagnosis(self):
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

        # Description
        ctk.CTkLabel(frm, text="Description (optional):").grid(row=3, column=0, sticky="nw", padx=5, pady=4)
        txt_desc = ctk.CTkTextbox(frm, width=320, height=80)
        txt_desc.grid(row=3, column=1, padx=5, pady=4)

        # Auto parts
        ctk.CTkLabel(frm, text="Auto parts recommended:").grid(row=4, column=0, sticky="nw", padx=5, pady=4)
        parts_lbl = ctk.CTkLabel(frm, text="—", anchor="w")
        parts_lbl.grid(row=4, column=1, sticky="w", padx=5, pady=4)

        # Mechanics
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

        # prefill
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

        # handlers

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
            info_local = None
            t = type_cb.get()
            s = svc_cb.get()
            if t in SERVICE_CATALOG:
                for it in SERVICE_CATALOG[t]:
                    if it["service"] == s:
                        info_local = it
                        break
            if info_local:
                parts_lbl.configure(text=info_local.get("parts", "—"))
                mech1_name_lbl.configure(text=info_local["mechanics"][0] if len(info_local["mechanics"]) > 0 else "(mech1)")
                mech2_name_lbl.configure(text=info_local["mechanics"][1] if len(info_local["mechanics"]) > 1 else "(mech2)")
                mech3_name_lbl.configure(text=info_local["mechanics"][2] if len(info_local["mechanics"]) > 2 else "(mech3)")
            else:
                parts_lbl.configure(text="—")
                mech1_name_lbl.configure(text="(mech1)")
                mech2_name_lbl.configure(text="(mech2)")
                mech3_name_lbl.configure(text="(mech3)")
            update_price_preview()

        def update_price_preview():
            info_local = None
            t = type_cb.get()
            s = svc_cb.get()
            if t in SERVICE_CATALOG:
                for it in SERVICE_CATALOG[t]:
                    if it["service"] == s:
                        info_local = it
                        break
            if not info_local:
                price_lbl.configure(text="Estimated Price: ₱0.00")
                return
            sev = sev_cb.get().strip().lower()
            base = info_local["minor_price"] if sev == "minor" else info_local["major_price"]
            price_lbl.configure(text=f"Estimated Price: {peso(base)}")

        # init
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
            est_price = price_lbl.cget("text").replace("Estimated Price: ", "").strip()

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
                "-" * 40
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

            c_text = self.cb_service_client.get().strip()
            try:
                client_id = int(c_text.split("-")[0].strip())
            except Exception:
                client_id = None

            mech1_name = mechs[0] if len(mechs) > 0 else None
            mech2_name = mechs[1] if len(mechs) > 1 else None
            mech3_name = mechs[2] if len(mechs) > 2 else None

            info_local = None
            if t and t in SERVICE_CATALOG:
                for it in SERVICE_CATALOG[t]:
                    if it.get("service") == s:
                        info_local = it
                        break
            eta_minutes = info_local.get("time_minutes", 60) if info_local else 60

            total_cost = 0.0
            try:
                p = est_price.replace('₱', '').replace(',', '')
                total_cost = float(p)
            except Exception:
                total_cost = 0.0

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
                    self.refresh_orders_table()
                    self._refresh_other_pages()
                except Exception:
                    messagebox.showwarning("Warning", "Diagnosis saved but failed to create repair order.", parent=dlg)

            messagebox.showinfo("Saved", "Diagnosis appended and saved to service table.", parent=dlg)
            dlg.grab_release()
            dlg.destroy()

        def do_cancel():
            dlg.grab_release()
            dlg.destroy()

        ctk.CTkButton(btns, text="OK", command=do_ok).pack(side="right", padx=6)
        ctk.CTkButton(btns, text="Cancel", fg_color="gray30", command=do_cancel).pack(side="right", padx=6)

    # ---------- save service ----------

    def save_service(self):
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
        selected_parts = [part for part, var in self.part_vars if var.get()]
        parts = ", ".join(selected_parts)

        m1 = info["mechanics"][0] if len(info["mechanics"]) > 0 else None
        m2 = info["mechanics"][1] if len(info["mechanics"]) > 1 else None
        m3 = info["mechanics"][2] if len(info["mechanics"]) > 2 else None

        mech1_name = m1 if self.chk_mech1_var.get() else None
        mech2_name = m2 if self.chk_mech2_var.get() else None
        mech3_name = m3 if self.chk_mech3_var.get() else None

        status = self.cb_status.get().strip() or "Check-in"
        eta_minutes = info.get("time_minutes", 60)

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
        except Exception as e:
            print(f"[ERROR] Failed to save repair order: {e}")

        messagebox.showinfo("Saved", "Service / repair order saved.", parent=self)
        self.txt_description.delete("0.0", "end")
        self.refresh_orders_table()
        self._refresh_other_pages()

    # ---------- orders table ----------

    def refresh_orders_table(self):
        for row in self.tree_orders.get_children():
            self.tree_orders.delete(row)

        show_completed = self.chk_show_completed_var.get()
        rows = self.db.get_all_orders(exclude_completed=not show_completed)
        aggr: Dict[Any, Any] = {}
        aggr_oids: Dict[Any, List[int]] = {}

        for r in rows:
            oid, cname, _contact, vtype, brand, model, dstart, tstart, _dd, _td, service, status, total, _m1, _m2, _m3 = r
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

            try:
                cur_date = entry["date"]
                cur_time = entry["time"]
                if dstart and (cur_date == "" or dstart > cur_date or (dstart == cur_date and (tstart or "") > (cur_time or ""))):
                    entry["date"] = dstart or ""
                    entry["time"] = tstart or ""
            except Exception:
                pass

        idx = 0
        for (cname, vehicle), info in aggr.items():
            idx += 1
            parent_id = f"parent_{idx}"
            statuses = info["statuses"]
            status_str = ", ".join(statuses) if statuses else ""
            self.tree_orders.insert(
                "", "end", iid=parent_id,
                values=("", cname, vehicle, "", status_str,
                        info["date"], info["time"], peso(info["total"]))
            )
            oids = aggr_oids[(cname, vehicle)]
            for i, svc in enumerate(info["services"]):
                oid_child = oids[i] if i < len(oids) else ""
                child_id = f"svc_{oid_child}"
                self.tree_orders.insert(
                    parent_id, "end", iid=child_id,
                    values=(oid_child, "", "", svc or "", "", "", "", "")
                )
            try:
                self.tree_orders.item(parent_id, open=True)
            except Exception:
                pass

    def mark_order_done(self):
        sel = self.tree_orders.selection()
        if not sel:
            messagebox.showinfo("Info", "Please select a repair order.", parent=self)
            return
        oids_to_mark: List[int] = []

        for s in sel:
            values = self.tree_orders.item(s)["values"]
            oid = values[0]
            cname = values[1]
            if oid and str(oid).isdigit():
                oids_to_mark.append(int(oid))
            else:
                child_ids = self.tree_orders.get_children(s)
                for cid in child_ids:
                    c_values = self.tree_orders.item(cid)["values"]
                    c_oid = c_values[0]
                    if c_oid and str(c_oid).isdigit():
                        oids_to_mark.append(int(c_oid))
                if not child_ids and cname:
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
        self._refresh_other_pages()

    def _refresh_other_pages(self):
        dash = self.controller.pages.get("Dashboard")
        if dash and hasattr(dash, "refresh"):
            dash.refresh()
        rep = self.controller.pages.get("Reports")
        if rep and hasattr(rep, "refresh"):
            rep.refresh()
        hist = self.controller.pages.get("History")
        if hist and hasattr(hist, "refresh"):
            hist.refresh()

