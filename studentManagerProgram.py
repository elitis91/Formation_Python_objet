

#studentManager.py

import sqlite3,sys, shutil
from pathlib import Path
"""
APP_NAME = "MonApp"
DB_NAME = "students.db"

def _resource_path(name):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base / name

def _user_db_path():
    udir = Path.home() / f".{APP_NAME.lower()}"
    udir.mkdir(exist_ok=True)
    return udir / DB_NAME

def ensure_db_writable():
    dst = _user_db_path()
    if not dst.exists():
        src = _resource_path(DB_NAME)  # fourni via --add-data
        shutil.copy2(src, dst)
    return dst
"""


def connect_to_db():
    return sqlite3.connect("students.db")

def db_init():
    with connect_to_db() as conn :
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT,
                email TEXT NOT NULL UNIQUE
                )
        """)

def add_student(name:str,address:str,email:str):
    with connect_to_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO student (name,address,email) VALUES (?,?,?)",
            (name,address,email)
        )
        conn.commit()
        return cursor.lastrowid



def fetch_all():
    with connect_to_db() as conn:
        cursor = conn.cursor()
        rows = cursor.execute(
            "SELECT * FROM student"
        )

        return rows.fetchall()

def maj_student(email:str, name:str=None,address:str=None):
    fields, params = [], []
    if name is not None:
        fields.append("name = ?")
        params.append(name.strip())
    if address is not None:
        fields.append("address = ?")
        params.append(address)
    if not fields:
        return False

    with connect_to_db() as conn:
        params.append(email.strip())
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE student SET {','.join(fields)} WHERE email = ?", params
        )
        conn.commit()
def delete_by_email(email:str):
    with connect_to_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM student WHERE email = ?", (email.strip(),))
        conn.commit()
        return cursor.rowcount >0

#main.py

import tkinter as tk
from tkinter import messagebox, ttk

from rich import columns

from studentManager import add_student, fetch_all, db_init


def open_window_for_listing(parent):
    win = tk.Toplevel(parent)
    win.title("Lister les etudiants")

    columns = ("id", "name", "address", "email")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    for col, txt, width in [
        ("id","ID",60),
        ("name", "NOM",160),
        ("address", "ADRESSE", 190),
        ("email", "EMAIL", 220),
    ]:
        tree.heading(col,text=txt)
        tree.column(col, width=width, anchor="w")

    vsb = ttk.Scrollbar(win ,orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)

    tree.pack(side="left")
    vsb.pack(side="right")

    def charger_lignes():
        tree.delete(*tree.get_children())
        rows = fetch_all()
        if not rows :
            messagebox.showinfo("Aucun elt trouvé")
            return
        for r in rows :
            tree.insert("", tk.END, values=r)

    toolbar = tk.Frame(win)
    toolbar.pack()
    tk.Button(toolbar, text="Recharger", command=charger_lignes).pack(side="right")
    charger_lignes()

def open_window(parent):

    win = tk.Toplevel(parent)
    win.title("Ajouter un etudiant")
    win.resizable(False,False)

    frame = tk.Frame(win,padx=14,pady=14)
    frame.pack()

    tk.Label(frame, text="Nom etudiant").grid(row=0, column=0,sticky="w", pady=(0,6))
    entry_name = tk.Entry(frame, width=40)
    entry_name.grid(row=0,column=1, pady=(0,6))

    tk.Label(frame, text="Adresse etudiant").grid(row=1 ,column=0,sticky="w", pady=6)
    entry_adresse = tk.Entry(frame,width=40)
    entry_adresse.grid(row=1,column=1, pady=6)

    tk.Label(frame, text="Email etudiant").grid(row=2, column=0,sticky="w", pady=6)
    entry_email = tk.Entry(frame,width=40)
    entry_email.grid(row=2, column=1, pady=6)

    def on_submit():
        name = entry_name.get()
        adresse = entry_adresse.get()
        email = entry_email.get()

        add_student(name,adresse,email)
        messagebox.showinfo("Succès",f"L'etudiant {name} a été crée avec succes")

        entry_name.delete(0,tk.END)
        entry_adresse.delete(0,tk.END)
        entry_email.delete(0,tk.END)

    btns = tk.Frame(frame)
    btns.grid(row=3, column=1)
    tk.Button(btns, text="Ajouter", command=on_submit).pack(side="right")
    tk.Button(btns, text="Fermer", command=win.destroy).pack(side="right", padx=(0,8))

    entry_name.focus_set()
    win.bind("<Return>", lambda _: on_submit())





def main():

    db_init()
    root = tk.Tk()
    root.title("Mon programme TK")
    root.resizable(False,False)
    root.geometry("350x200")

    container = tk.Frame(root)
    container.pack()

    tk.Label(container, text="Menu principal", width=24 ).pack()

    tk.Button(container, text="Ajouter un etudiant", width=24, command=lambda : open_window(root)).pack()

    tk.Button(container, text="Lister les etudiants", width= 24,command=lambda : open_window_for_listing(root)).pack()

    tk.Button(container, text="Mise à jour", width=24, command=lambda : open_window(root)).pack()

    tk.Button(container, text="Quitter", width=24, command=root.destroy).pack()

    root.mainloop()


if __name__ == "__main__":
    main()