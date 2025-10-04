"""
SQLite initializer and seeder for TP1 – Partie B.

Creates ventes.db with 3 tables:
  - clients(id, nom, region)
  - produits(id, nom, categorie, prix)
  - ventes(id, client_id, produit_id, date, quantite, prix_unitaire)

Usage:
  python3 db_init.py            # creates ventes.db if not present
  python3 db_init.py --reset    # drops existing tables and reseeds
"""
from __future__ import annotations

import argparse
import os
import sqlite3
from datetime import date


DB_PATH = os.path.join(os.path.dirname(__file__), "ventes.db")


def create_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    # Ensure foreign keys are enforced
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY,
            nom TEXT NOT NULL,
            region TEXT NOT NULL
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS produits (
            id INTEGER PRIMARY KEY,
            nom TEXT NOT NULL,
            categorie TEXT NOT NULL,
            prix REAL NOT NULL
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ventes (
            id INTEGER PRIMARY KEY,
            client_id INTEGER NOT NULL REFERENCES clients(id),
            produit_id INTEGER NOT NULL REFERENCES produits(id),
            date TEXT NOT NULL,               -- ISO format YYYY-MM-DD
            quantite INTEGER NOT NULL,
            prix_unitaire REAL NOT NULL       -- captured at sale time
        );
        """
    )
    conn.commit()


def drop_all(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS ventes;
        DROP TABLE IF EXISTS produits;
        DROP TABLE IF EXISTS clients;
        """
    )
    conn.commit()


def seed_data(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    clients = [
        (1, "Alice SARL", "Europe"),
        (2, "Brahim Inc.", "Afrique"),
        (3, "Chen & Co", "Asie"),
        (4, "Davis LLC", "Amérique du Nord"),
        (5, "Emir Trading", "Moyen-Orient"),
    ]

    produits = [
        (1, "Kindle Paperwhite", "électronique", 129.0),
        (2, "Livre - Data BI", "livres", 39.0),
        (3, "T-shirt Amazon", "vêtements", 19.0),
        (4, "Café en grains 1kg", "alimentation", 24.0),
        (5, "Casque Bluetooth", "électronique", 79.0),
    ]

    cur.executemany("INSERT OR REPLACE INTO clients(id, nom, region) VALUES (?, ?, ?);", clients)
    cur.executemany(
        "INSERT OR REPLACE INTO produits(id, nom, categorie, prix) VALUES (?, ?, ?, ?);",
        produits,
    )

    # Helper to build sale rows
    def sale(i, client, prod, y, m, d, q, pu=None):
        if pu is None:
            # default to product list price
            # SQLite lacks array map; we look up from produits list
            price = next(p[3] for p in produits if p[0] == prod)
        else:
            price = pu
        return (i, client, prod, date(y, m, d).isoformat(), q, float(price))

    ventes = [
        sale(1, 1, 1, 2025, 1, 15, 2),
        sale(2, 2, 2, 2025, 1, 20, 1),
        sale(3, 3, 3, 2025, 2, 5, 3),
        sale(4, 4, 4, 2025, 2, 22, 5),
        sale(5, 5, 5, 2025, 3, 10, 1),
        sale(6, 1, 2, 2025, 3, 25, 2),
        sale(7, 2, 5, 2025, 4, 12, 1),
        sale(8, 3, 1, 2025, 4, 28, 1),
        sale(9, 4, 3, 2025, 5, 9, 4),
        sale(10, 5, 4, 2025, 5, 18, 2),
        sale(11, 1, 5, 2025, 6, 6, 2),
        sale(12, 2, 1, 2025, 6, 20, 1),
    ]

    cur.executemany(
        """
        INSERT OR REPLACE INTO ventes(id, client_id, produit_id, date, quantite, prix_unitaire)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        ventes,
    )

    conn.commit()


def ensure_db(db_path: str = DB_PATH, reset: bool = False) -> None:
    first_time = not os.path.exists(db_path)
    conn = create_connection(db_path)
    try:
        if reset and not first_time:
            drop_all(conn)
        create_schema(conn)
        # Only seed when first creation or reset requested
        if first_time or reset:
            seed_data(conn)
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Init and seed ventes.db")
    parser.add_argument("--db", default=DB_PATH, help="Chemin du fichier SQLite (default: ventes.db)")
    parser.add_argument("--reset", action="store_true", help="Drop + recreate tables and reseed")
    args = parser.parse_args()

    ensure_db(args.db, reset=args.reset)
    print(f"OK - Base prête: {args.db}")


if __name__ == "__main__":
    main()
