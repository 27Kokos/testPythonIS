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
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Decisions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT,
                        created_at TEXT,
                        template_used TEXT
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Options (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        decision_id INTEGER,
                        name TEXT NOT NULL,
                        description TEXT,
                        FOREIGN KEY (decision_id) REFERENCES Decisions(id) ON DELETE CASCADE
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Criteria (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        decision_id INTEGER,
                        name TEXT NOT NULL,
                        type TEXT CHECK(type IN ('number', 'boolean')),
                        weight INTEGER CHECK(weight BETWEEN 1 AND 5),
                        FOREIGN KEY (decision_id) REFERENCES Decisions(id) ON DELETE CASCADE
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Evaluations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        decision_id INTEGER,
                        option_id INTEGER,
                        criterion_id INTEGER,
                        value TEXT NOT NULL,
                        FOREIGN KEY (decision_id) REFERENCES Decisions(id) ON DELETE CASCADE,
                        FOREIGN KEY (option_id) REFERENCES Options(id) ON DELETE CASCADE,
                        FOREIGN KEY (criterion_id) REFERENCES Criteria(id) ON DELETE CASCADE,
                        UNIQUE(decision_id, option_id, criterion_id)
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS AnalysisResults (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        decision_id INTEGER,
                        option_id INTEGER,
                        total_score REAL NOT NULL,
                        rank INTEGER NOT NULL,
                        calculated_at TEXT,
                        FOREIGN KEY (decision_id) REFERENCES Decisions(id) ON DELETE CASCADE,
                        FOREIGN KEY (option_id) REFERENCES Options(id) ON DELETE CASCADE,
                        UNIQUE(decision_id, option_id)
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Favorites (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        decision_id INTEGER UNIQUE,
                        added_at TEXT,
                        FOREIGN KEY (decision_id) REFERENCES Decisions(id) ON DELETE CASCADE
                    )
                ''')
                
                conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка создания таблиц: {e}")

    def add_decision(self, title, description="", template_used=""):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Decisions (title, description, created_at, template_used)
                    VALUES (?, ?, ?, ?)
                ''', (title, description, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), template_used))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Ошибка добавления решения: {e}")
            return None

    def get_decisions(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, description, created_at, template_used 
                    FROM Decisions 
                    ORDER BY created_at DESC
                ''')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения решений: {e}")
            return []

    def get_decision_by_id(self, decision_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM Decisions WHERE id = ?
                ''', (decision_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Ошибка получения решения: {e}")
            return None

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
            print(f"Ошибка добавления варианта: {e}")
            return None

    def get_options_by_decision(self, decision_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, description 
                    FROM Options 
                    WHERE decision_id = ?
                    ORDER BY id
                ''', (decision_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения вариантов: {e}")
            return []

    def add_criterion(self, decision_id, name, type_, weight):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Criteria (decision_id, name, type, weight)
                    VALUES (?, ?, ?, ?)
                ''', (decision_id, name, type_, weight))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Ошибка добавления критерия: {e}")
            return None

    def get_criteria_by_decision(self, decision_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, type, weight 
                    FROM Criteria 
                    WHERE decision_id = ?
                    ORDER BY id
                ''', (decision_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения критериев: {e}")
            return []

    def add_evaluation(self, decision_id, option_id, criterion_id, value):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO Evaluations 
                    (decision_id, option_id, criterion_id, value)
                    VALUES (?, ?, ?, ?)
                ''', (decision_id, option_id, criterion_id, str(value)))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Ошибка добавления оценки: {e}")
            return None

    def get_evaluations_by_decision(self, decision_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT e.option_id, e.criterion_id, e.value
                    FROM Evaluations e
                    WHERE e.decision_id = ?
                ''', (decision_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения оценок: {e}")
            return []

    def save_analysis_results(self, decision_id, results):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM AnalysisResults WHERE decision_id = ?', (decision_id,))
                
                for option_id, total_score, rank in results:
                    cursor.execute('''
                        INSERT INTO AnalysisResults 
                        (decision_id, option_id, total_score, rank, calculated_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (decision_id, option_id, total_score, rank, 
                          datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Ошибка сохранения результатов анализа: {e}")
            return False

    def get_analysis_results(self, decision_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT ar.option_id, o.name, ar.total_score, ar.rank, ar.calculated_at
                    FROM AnalysisResults ar
                    JOIN Options o ON ar.option_id = o.id
                    WHERE ar.decision_id = ?
                    ORDER BY ar.rank
                ''', (decision_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения результатов анализа: {e}")
            return []

    def delete_decision(self, decision_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM Decisions WHERE id = ?', (decision_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Ошибка удаления решения: {e}")
            return False

    def clear_all_data(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM Evaluations')
                cursor.execute('DELETE FROM AnalysisResults')
                cursor.execute('DELETE FROM Criteria')
                cursor.execute('DELETE FROM Options')
                cursor.execute('DELETE FROM Decisions')
                cursor.execute('DELETE FROM Favorites')
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Ошибка очистки всех данных: {e}")
            return False

    # Методы для работы с избранным
    def add_to_favorites(self, decision_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO Favorites (decision_id, added_at)
                    VALUES (?, ?)
                ''', (decision_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Ошибка добавления в избранное: {e}")
            return False

    def remove_from_favorites(self, decision_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM Favorites WHERE decision_id = ?', (decision_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Ошибка удаления из избранного: {e}")
            return False

    def get_favorites(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT d.id, d.title, d.description, d.created_at, d.template_used 
                    FROM Favorites f
                    JOIN Decisions d ON f.decision_id = d.id
                    ORDER BY f.added_at DESC
                ''')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения избранного: {e}")
            return []

    def is_favorite(self, decision_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM Favorites WHERE decision_id = ?', (decision_id,))
                return cursor.fetchone()[0] > 0
        except sqlite3.Error as e:
            print(f"Ошибка проверки избранного: {e}")
            return False