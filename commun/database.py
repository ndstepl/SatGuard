import sqlite3
from commun import config

class ErreurIntegrite(Exception):
    pass

class Database:
    def __init__(self):
        # check_same_thread=False est OBLIGATOIRE pour le générateur en arrière-plan
        self.conn = sqlite3.connect(config.DB_PATH, timeout=10, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self.creer_tables()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.conn.close()

    def _exec(self, sql, params=()):
        cur = self.conn.cursor()
        try:
            cur.execute(sql, params)
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            raise ErreurIntegrite(str(e)) from e
        return cur

    def lire(self, sql, params=()):
        return self._exec(sql, params).fetchall()

    def ecrire(self, sql, params=()):
        self._exec(sql, params)

    def inserer(self, sql, params):
        return self._exec(sql, params).lastrowid

    def supprimer(self, sql, params=()):
        self._exec(sql, params)

    def creer_tables(self):
        self.ecrire("""CREATE TABLE IF NOT EXISTS missions (
            id_mission INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            agence TEXT NOT NULL,
            date_lancement TEXT NOT NULL,
            statut TEXT NOT NULL,
            objectif TEXT NOT NULL
        )""")

        self.ecrire("""CREATE TABLE IF NOT EXISTS satellites (
            id_satellite INTEGER PRIMARY KEY AUTOINCREMENT,
            id_mission INTEGER NOT NULL REFERENCES missions(id_mission),
            nom TEXT NOT NULL UNIQUE,
            altitude REAL NOT NULL,
            vitesse REAL NOT NULL,
            inclinaison REAL NOT NULL,
            statut TEXT NOT NULL
        )""")

        self.ecrire("""CREATE TABLE IF NOT EXISTS evenements (
            id_evenement INTEGER PRIMARY KEY AUTOINCREMENT,
            id_satellite INTEGER NOT NULL REFERENCES satellites(id_satellite) ON DELETE CASCADE,
            horodatage TEXT NOT NULL,
            type_evenement TEXT NOT NULL,
            message TEXT,
            batterie REAL,
            temperature REAL
        )""")

        colonnes = [r["name"] for r in self.lire("PRAGMA table_info(evenements)")]
        if "temperature" not in colonnes:
            self.ecrire("ALTER TABLE evenements ADD COLUMN temperature REAL")