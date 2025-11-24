# maingui.py - launcher
from db import DB
from EVautoshop import EVAutoRepairApp
import os

DB_FILE = os.path.join(os.path.dirname(__file__), 'ev_auto_repairshop.db')

def main():
    db = DB(DB_FILE)
    app = EVAutoRepairApp(db)
    app.mainloop()

if __name__ == '__main__':
    main()
