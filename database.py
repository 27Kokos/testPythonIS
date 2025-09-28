import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name="decision_helper.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)
        self.create_tables()

    def create_tables(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица Decisions
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Decisions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        created_at TEXT
                    )
                ''')
                
                # Таблица Options
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Options (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        decision_id INTEGER,
                        name TEXT NOT NULL,
                        description TEXT,
                        FOREIGN KEY (decision_id) REFERENCES Decisions(id)
                    )
                ''')
                
                # Таблица Criteria
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Criteria (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        decision_id INTEGER,
                        name TEXT NOT NULL,
                        type TEXT,  -- numeric, text, choice
                        weight REAL,
                        units TEXT,
                        FOREIGN KEY (decision_id) REFERENCES Decisions(id)
                    )
                ''')
                
                conn.commit()
                print("Таблицы созданы или уже существуют")
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблиц: {e}")

    def add_decision(self, name, description=""):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Decisions (name, description, created_at)
                    VALUES (?, ?, ?)
                ''', (name, description, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении решения: {e}")
            return None

    def get_decisions(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, name, description, created_at FROM Decisions ORDER BY created_at DESC')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при получении решений: {e}")
            return []

    def get_decision_by_id(self, decision_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM Decisions WHERE id = ?', (decision_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Ошибка при получении решения: {e}")
            return None

    def update_decision(self, decision_id, name, description):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE Decisions SET name = ?, description = ? WHERE id = ?
                ''', (name, description, decision_id))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении решения: {e}")
            return False

    def delete_decision(self, decision_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM Decisions WHERE id = ?', (decision_id,))
                cursor.execute('DELETE FROM Options WHERE decision_id = ?', (decision_id,))
                cursor.execute('DELETE FROM Criteria WHERE decision_id = ?', (decision_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Ошибка при удалении решения: {e}")
            return False

    def add_option(self, decision_id, name, description=""):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Options (decision_id, name, description)
                    VALUES (?, ?, ?)
                ''', (decision_id, name, description))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении варианта: {e}")
            return None

    def get_options_by_decision(self, decision_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, name, description FROM Options WHERE decision_id = ?', (decision_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при получении вариантов: {e}")
            return []

    def add_criterion(self, decision_id, name, type, weight, units):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Criteria (decision_id, name, type, weight, units)
                    VALUES (?, ?, ?, ?, ?)
                ''', (decision_id, name, type, weight, units))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении критерия: {e}")
            return None

    def get_criteria_by_decision(self, decision_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, name, type, weight, units FROM Criteria WHERE decision_id = ?', (decision_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при получении критериев: {e}")
            return []