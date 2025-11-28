
import customtkinter as ctk

from config import DB_FILE
from db import DB
from app import EVAutoRepairApp


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    
    db = DB(DB_FILE)
    app = EVAutoRepairApp(db)
    app.mainloop()

if __name__ == '__main__':
    main()
