# db.py - extracted DB class
import sqlite3
import datetime
from typing import Optional

from hashlib import sha256

def hashpw(p: str) -> str:
    return sha256(p.encode('utf-8')).hexdigest()

def now_date() -> str:
    return datetime.date.today().isoformat()

def now_time() -> str:
    return datetime.datetime.now().strftime("%H:%M")


class DB:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.init_schema()
        self.seed_admin()

    def execute(self, sql: str, params: tuple = (), fetch=False, many=False):
        cur = self.conn.cursor()
        try:
            if many:
                cur.executemany(sql, params)
                self.conn.commit()
                return
            cur.execute(sql, params)
            if fetch:
                rows = cur.fetchall()
                self.conn.commit()
                return rows
            self.conn.commit()
        finally:
            cur.close()

    def init_schema(self):
        self.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)
        self.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT
            )
        """)
        self.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                vehicle_type TEXT,
                brand TEXT,
                model TEXT,
                FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
            )
        """)

        # Ensure vehicles has a 'problem' column to store diagnosis/problems per vehicle
        try:
            # SQLite doesn't support IF NOT EXISTS for ALTER TABLE, so attempt and ignore error
            self.execute("ALTER TABLE vehicles ADD COLUMN problem TEXT DEFAULT ''")
        except Exception:
            pass
        # Ensure repair_orders has a 'mechanic3_id' column
        try:
            self.execute("ALTER TABLE repair_orders ADD COLUMN mechanic3_id INTEGER")
        except Exception:
            pass
        self.execute("""
            CREATE TABLE IF NOT EXISTS mechanics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT,
                specialization TEXT
            )
        """)
        self.execute("""
            CREATE TABLE IF NOT EXISTS repair_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                vehicle_id INTEGER NOT NULL,
                type_job TEXT,
                specific_service TEXT,
                severity TEXT,
                description TEXT,
                parts_recommended TEXT,
                mechanic1_id INTEGER,
                mechanic2_id INTEGER,
                mechanic3_id INTEGER,
                status TEXT,
                date_start TEXT,
                time_start TEXT,
                eta_date TEXT,
                eta_time TEXT,
                date_done TEXT,
                time_done TEXT,
                total_cost REAL,
                FOREIGN KEY(client_id) REFERENCES clients(id),
                FOREIGN KEY(vehicle_id) REFERENCES vehicles(id),
                FOREIGN KEY(mechanic1_id) REFERENCES mechanics(id),
                FOREIGN KEY(mechanic2_id) REFERENCES mechanics(id),
                FOREIGN KEY(mechanic3_id) REFERENCES mechanics(id)
            )
        """)

    def seed_admin(self):
        rows = self.execute("SELECT COUNT(*) FROM admins", fetch=True)
        if rows[0][0] == 0:
            self.execute(
                "INSERT INTO admins (username, password) VALUES (?,?)",
                (ADMIN_USER, hashpw(ADMIN_PASS))
            )

    # Admin / Login 

    def verify_admin(self, username: str, password: str) -> bool:
        rows = self.execute(
            "SELECT password FROM admins WHERE username=?",
            (username,),
            fetch=True
        )
        if not rows:
            return False
        return rows[0][0] == hashpw(password)

    # Clients & Vehicles 

    def add_client_with_vehicle(
        self, name: str, contact: str,
        vehicle_type: str, brand: str, model: str
    ):
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO clients (name, contact) VALUES (?,?)",
                (name, contact)
            )
            client_id = cur.lastrowid
            cur.execute(
                "INSERT INTO vehicles (client_id, vehicle_type, brand, model) "
                "VALUES (?,?,?,?)",
                (client_id, vehicle_type, brand, model)
            )
            vehicle_id = cur.lastrowid
            self.conn.commit()
            return client_id, vehicle_id
        finally:
            cur.close()

    def get_clients_with_vehicles(self):
        return self.execute("""
            SELECT c.id, c.name, c.contact,
                   v.id, v.vehicle_type, v.brand, v.model
            FROM clients c
            LEFT JOIN vehicles v ON v.client_id = c.id
            ORDER BY c.name
        """, fetch=True)

    def get_clients(self):
        return self.execute(
            "SELECT id, name, contact FROM clients ORDER BY name",
            fetch=True
        )

    def get_vehicles_for_client(self, client_id: int):
        return self.execute("""
            SELECT id, vehicle_type, brand, model
            FROM vehicles WHERE client_id=?
        """, (client_id,), fetch=True)

    # Mechanics 

    def get_mechanics(self):
        return self.execute(
            "SELECT id, name, contact, specialization FROM mechanics ORDER BY name",
            fetch=True
        )

    def get_mechanic_by_name(self, name: str) -> Optional[int]:
        rows = self.execute(
            "SELECT id FROM mechanics WHERE name=?",
            (name,),
            fetch=True
        )
        if rows:
            return rows[0][0]
        return None

    def append_vehicle_problem(self, vehicle_id: int, text: str) -> bool:
        """Append diagnosis/problem text to the vehicle's `problem` field.

        Returns True if vehicle exists and was updated, False otherwise.
        """
        rows = self.execute(
            "SELECT problem FROM vehicles WHERE id=?",
            (vehicle_id,),
            fetch=True
        )
        if not rows:
            return False
        existing = rows[0][0] or ""
        if existing.strip():
            combined = existing.rstrip() + "\n\n" + text
        else:
            combined = text
        self.execute(
            "UPDATE vehicles SET problem=? WHERE id=?",
            (combined, vehicle_id)
        )
        return True

    #  Repair Orders / Services 
    def create_repair_order(
        self,
        client_id: int,
        vehicle_id: int,
        type_job: str,
        specific_service: str,
        severity: str,
        description: str,
        parts_recommended: str,
        mech1_name: Optional[str],
        mech2_name: Optional[str],
        mech3_name: Optional[str],
        status: str,
        eta_minutes: int,
        total_cost: float,
    ):
        date_start = now_date()
        time_start = now_time()
        eta_dt = datetime.datetime.now() + datetime.timedelta(minutes=eta_minutes)
        eta_date = eta_dt.date().isoformat()
        eta_time = eta_dt.strftime("%H:%M")

        mech1_id = self.get_mechanic_by_name(mech1_name) if mech1_name else None
        mech2_id = self.get_mechanic_by_name(mech2_name) if mech2_name else None
        mech3_id = self.get_mechanic_by_name(mech3_name) if mech3_name else None

        # If status is Pickup at creation, mark done immediately (same-day pickup)
        date_done = None
        time_done = None
        if status == "Pickup":
            date_done = date_start
            time_done = time_start

        self.execute("""
            INSERT INTO repair_orders (
                client_id, vehicle_id,
                type_job, specific_service,
                severity, description,
                parts_recommended,
                mechanic1_id, mechanic2_id, mechanic3_id,
                status,
                date_start, time_start,
                eta_date, eta_time,
                date_done, time_done,
                total_cost
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            client_id, vehicle_id,
            type_job, specific_service,
            severity, description,
            parts_recommended,
            mech1_id, mech2_id, mech3_id,
            status,
            date_start, time_start,
            eta_date, eta_time,
            date_done, time_done,
            total_cost,
        ))

    def set_repair_status(self, order_id: int, new_status: str):
        # Pickup- means picked up same day -> set done date/time now
        # Check-in- means still not done (multi-day) -> clear done date/time
        if new_status == "Pickup":
            date_done = now_date()
            time_done = now_time()
        else:
            date_done = None
            time_done = None
        self.execute("""
            UPDATE repair_orders
            SET status=?, date_done=?, time_done=?
            WHERE id=?
        """, (new_status, date_done, time_done, order_id))

    def get_today_stats(self):
        today = now_date()
        total_repairs = self.execute("""
            SELECT COUNT(*) FROM repair_orders
            WHERE date_start=?
        """, (today,), fetch=True)[0][0]

        # Pickup-treated as completed same-day
        done_repairs = self.execute("""
            SELECT COUNT(*) FROM repair_orders
            WHERE date_done=? AND status='Pickup'
        """, (today,), fetch=True)[0][0]

        in_progress = self.execute("""
            SELECT COUNT(*) FROM repair_orders
            WHERE date_start=? AND (status!='Pickup' OR status IS NULL)
        """, (today,), fetch=True)[0][0]

        today_sales = self.execute("""
            SELECT COALESCE(SUM(total_cost),0) FROM repair_orders
            WHERE date_done=? AND status='Pickup'
        """, (today,), fetch=True)[0][0]

        return {
            "total_repairs": total_repairs,
            "done_repairs": done_repairs,
            "in_progress": in_progress,
            "today_sales": today_sales,
        }

    def get_today_orders(self):
        today = now_date()
        return self.execute("""
            SELECT ro.id,
                   c.name, c.contact,
                   v.vehicle_type, v.brand, v.model,
                   ro.specific_service, ro.status,
                   ro.total_cost
            FROM repair_orders ro
            JOIN clients c ON c.id = ro.client_id
            JOIN vehicles v ON v.id = ro.vehicle_id
            WHERE ro.date_start=?
            ORDER BY ro.id DESC
        """, (today,), fetch=True)

    def get_all_orders(self, client_name_filter: str = "", exclude_completed: bool = True):
        params = ()
        where_clauses = []
        if client_name_filter:
            where_clauses.append("c.name LIKE ?")
            params = (f"%{client_name_filter}%",)

        if exclude_completed:
            where_clauses.append("ro.status != 'Pickup'")

        where_clause = ""
        if where_clauses:
            where_clause = "WHERE " + " AND ".join(where_clauses)

        return self.execute(f"""
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
            {where_clause}
            ORDER BY ro.date_start DESC, ro.time_start DESC
        """, params, fetch=True)

    def get_sales_by_month(self, year: int, month: int) -> float:
        start = datetime.date(year, month, 1)
        if month == 12:
            end = datetime.date(year + 1, 1, 1)
        else:
            end = datetime.date(year, month + 1, 1)
        rows = self.execute("""
            SELECT COALESCE(SUM(total_cost),0)
            FROM repair_orders
            WHERE date_done>=? AND date_done<?
              AND status='Pickup'
        """, (start.isoformat(), end.isoformat()), fetch=True)
        return rows[0][0]

    def get_mechanic_summary(self):
                # Done repairs = bilang ng orders na Pickup
                return self.execute("""
                        SELECT m.name, m.contact,
                                     COUNT(ro.id) AS done_repairs,
                                     COALESCE(SUM(ro.total_cost),0) AS total_sales
                        FROM mechanics m
                        LEFT JOIN repair_orders ro
                            ON (ro.mechanic1_id = m.id OR ro.mechanic2_id = m.id)
                         AND ro.status='Pickup'
                        GROUP BY m.id
                        ORDER BY done_repairs DESC
                """, fetch=True)



#  LOGIN 

