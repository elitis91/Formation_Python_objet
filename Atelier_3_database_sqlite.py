import sqlite3

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
        cursor.execute(
            "SELECT * FROM student"
        )
        for r in cursor.fetchall():
            print(r)

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

def main():
    connect_to_db()
    db_init()
    while True:
        print("\n-----Programme Principal----")
        print("1. Lister les etudiants")
        print("2. Ajouter un etudiant")
        print("3. MAJ les informations d'un étudiant")
        print("4. Supprimer un étudiant")
        print("5. QUITTER")

        choix = input("Faites votre choix : ")

        if choix == "1":
            fetch_all()

        elif choix == "2":
            name = input("Saisir un nom : ")
            address = input("Saisir une addresse :")
            email = input("Saisir l'email : ")
            add_student(name,address,email)
            print(f"L'etudiant {name} a bien été ajouté !")

        elif choix == "3":
            email = input("Saisir l'email : ")
            name = input("Saisir le nom à modifier: ")
            address = input("Saisir une addresse  :")
            maj_student(email,name,address)
            print("Modification effectuée avec succes !")

        elif choix == "4":
            email = input("Saisir l'email : ")
            delete_by_email(email)
            print("Utilisateur supprimé")

        elif choix == "5":
            break
        else:
            print("Choix invalide")

if __name__ == "__main__":
    main()