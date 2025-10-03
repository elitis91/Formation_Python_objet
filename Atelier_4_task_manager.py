#!/usr/bin/env python3
"""Gestionnaire de tâches CLI simplifié (sqlite).

Usage :
  python script.py add <description> <status>
  python script.py list
  python script.py update <id> <description> <status>
  python script.py done <id>
  python script.py help
"""

import os
import sqlite3
import sys

VALID_STATUSES = ("todo", "doing", "done")
DEFAULT_DB_NAME = "tasks.db"


def _db_path():
    env = os.environ.get("TASK_DB")
    return os.path.abspath(os.path.expanduser(env)) if env else os.path.join(os.getcwd(), DEFAULT_DB_NAME)


class Task:
    def __init__(self, id, description, status="todo"):
        self.id = id
        self.description = description
        self.status = status

    def display(self):
        return f"[{self.id}] ({self.status}) {self.description}"

    @staticmethod
    def _connect(db_path):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init_db(cls, db_path):
        with cls._connect(db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('todo','doing','done'))
                )
                """
            )
            conn.commit()

    @classmethod
    def add(cls, db_path, description, status):
        status = status.lower()
        if status not in VALID_STATUSES:
            raise ValueError("Status invalide")
        with cls._connect(db_path) as conn:
            cur = conn.execute(
                "INSERT INTO tasks(description, status) VALUES (?,?)",
                (description, status),
            )
            conn.commit()
            return Task(cur.lastrowid, description, status)

    @classmethod
    def list(cls, db_path):
        with cls._connect(db_path) as conn:
            rows = conn.execute("SELECT * FROM tasks ORDER BY id ASC").fetchall()
        return [Task(r["id"], r["description"], r["status"]) for r in rows]

    @classmethod
    def update(cls, db_path, task_id, description, status):
        status = status.lower()
        if status not in VALID_STATUSES:
            raise ValueError("Status invalide")
        with cls._connect(db_path) as conn:
            conn.execute(
                "UPDATE tasks SET description=?, status=? WHERE id=?",
                (description, status, task_id),
            )
            conn.commit()
        return cls.get(db_path, task_id)

    @classmethod
    def get(cls, db_path, task_id):
        with cls._connect(db_path) as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not row:
            return None
        return Task(row["id"], row["description"], row["status"])


# ---------------- CLI ----------------

def print_help():
    print(
        """
USAGE
  script.py add <description> <status>
  script.py list
  script.py update <id> <description> <status>
  script.py done <id>
  script.py help
        """.strip()
    )


def main(argv):
    if len(argv) < 2 or argv[1] in ("help", "-h", "--help"):
        print_help()
        return 0

    command = argv[1]
    db_path = _db_path()
    Task.init_db(db_path)

    if command == "add":
        if len(argv) < 4:
            print("Usage: script.py add <description> <status>", file=sys.stderr)
            return 2
        description, status = argv[2], argv[3]
        task = Task.add(db_path, description, status)
        print("✓ Ajouté:", task.display())
        return 0

    if command == "list":
        tasks = Task.list(db_path)
        if not tasks:
            print("(Aucune tâche)")
        else:
            for t in tasks:
                print(t.display())
        return 0

    if command == "update":
        if len(argv) < 5:
            print("Usage: script.py update <id> <description> <status>", file=sys.stderr)
            return 2
        try:
            task_id = int(argv[2])
        except ValueError:
            print("id doit être un entier", file=sys.stderr)
            return 2
        description, status = argv[3], argv[4]
        updated = Task.update(db_path, task_id, description, status)
        if not updated:
            print("Aucune tâche avec id=%s" % task_id, file=sys.stderr)
            return 1
        print("✓ Mis à jour:", updated.display())
        return 0

    if command == "done":
        if len(argv) < 3:
            print("Usage: script.py done <id>", file=sys.stderr)
            return 2
        try:
            task_id = int(argv[2])
        except ValueError:
            print("id doit être un entier", file=sys.stderr)
            return 2
        updated = Task.update(db_path, task_id, Task.get(db_path, task_id).description, "done")
        if not updated:
            print("Aucune tâche avec id=%s" % task_id, file=sys.stderr)
            return 1
        print("✓ Terminé:", updated.display())
        return 0

    print("Commande inconnue:", command, file=sys.stderr)
    print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
