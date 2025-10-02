# =========================
# Modèle
# =========================
class Parking:
    """Class Parking"""
    def __init__(self, nom: str, disponible: int):
        self.nom = nom
        self.disponible = disponible

    def __str__(self):
        return f"NOM : {self.nom} - CAPACITÉ : {self.disponible}"
		
		

import sqlite3
from parking import Parking
from typing import List, Tuple, Optional



# =========================
# Base de données
# =========================
def connect_db():
    """Methode connect"""
    try:
        return sqlite3.connect("parkings.db")
    except Exception as e:
        print(f"Erreur connexion DB : {e}")

def init_db():
    """Methode init"""
    try:
        with connect_db() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS parkings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT,
                    disponible INTEGER
                )
                """
            )
            conn.commit()
    except Exception as e:
        print(f"Erreur init DB : {e}")

def insert_parking(p: Parking):
    """Methode insert parking"""
    try:
        with connect_db() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO parkings (nom, disponible) VALUES (?, ?)",
                (p.nom, p.disponible),
            )
            conn.commit()
    except Exception as e:
        print(f"Erreur insertion : {e}")

def fetch_all() -> List[Parking]:
    """Methode fetch all"""
    try:
        with connect_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, nom, disponible FROM parkings")
            rows = cur.fetchall()
            return [Parking(r[1], r[2]) for r in rows]
    except Exception as e:
        print(f"Erreur lecture DB : {e}")
        return []


import sqlite3
import requests
from typing import List, Tuple, Optional

from databaseConfig import init_db, insert_parking, fetch_all
from parking import Parking

# =========================
# Accès API
# =========================
URL = "https://data.angers.fr/api/explore/v2.1/catalog/datasets/parking-angers/records?limit=20"


def load_data() -> List[Parking]:
    """Récupère nom/capacité depuis l’API (pour alimenter la DB)."""
    try:
        resp = requests.get(URL, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except Exception as e:
        print(f"Erreur API : {e}")
        return []

    parkings = []
    for item in results:
        nom = item.get("nom")
        disponible = item.get("disponible")
        parkings.append(Parking(nom, disponible))
    return parkings



# =========================
# Programme principal
# =========================
def main():
    """Main file"""
    # 1) Init DB + alimentation (nom/capacité)
    init_db()
    parkings = load_data()
    print(f"{len(parkings)} parkings récupérés depuis l'API.")
    for p in parkings:
        insert_parking(p)

    # 2) Affichage contenu DB (structure)
    print("\nParkings enregistrés (DB) :")
    for p in fetch_all():
        print(p)


if __name__ == "__main__":
    main()
