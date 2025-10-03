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
                
                # Таблица решений
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Decisions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT,
                        created_at TEXT,
                        template_used TEXT
                    )
                ''')
                
                # Таблица вариантов
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Options (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        decision_id INTEGER,
                        name TEXT NOT NULL,
                        description TEXT,
                        FOREIGN KEY (decision_id) REFERENCES Decisions(id) ON DELETE CASCADE
                    )
                ''')
                
                # Таблица критериев (упрощенная)
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
                
                # Таблица оценок (новая - связывает варианты и критерии)
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
                        UNIQUE(option_id, criterion_id)
                    )
                ''')
                
                # Таблица результатов анализа
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
                
                conn.commit()
                print("Таблицы БД успешно созданы/проверены")
                
        except sqlite3.Error as e:
            print(f"Ошибка создания таблиц: {e}")

    # Методы для работы с решениями
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

    # Методы для работы с вариантами
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
                ''', (decision_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения вариантов: {e}")
            return []

    # Методы для работы с критериями
    def add_criterion(self, decision_id, name, type, weight):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Criteria (decision_id, name, type, weight)
                    VALUES (?, ?, ?, ?)
                ''', (decision_id, name, type, weight))
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
                ''', (decision_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения критериев: {e}")
            return []

    # Методы для работы с оценками
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
                    SELECT e.option_id, e.criterion_id, e.value,
                           o.name as option_name, c.name as criterion_name
                    FROM Evaluations e
                    JOIN Options o ON e.option_id = o.id
                    JOIN Criteria c ON e.criterion_id = c.id
                    WHERE e.decision_id = ?
                ''', (decision_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения оценок: {e}")
            return []

    # Методы для работы с результатами анализа
    def save_analysis_results(self, decision_id, results):
        """Сохраняет результаты анализа
        results: список кортежей (option_id, total_score, rank)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Удаляем старые результаты
                cursor.execute('DELETE FROM AnalysisResults WHERE decision_id = ?', (decision_id,))
                
                # Сохраняем новые
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

    # Удаление решения и всех связанных данных
    def delete_decision(self, decision_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Каскадное удаление сработает из-за ON DELETE CASCADE
                cursor.execute('DELETE FROM Decisions WHERE id = ?', (decision_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Ошибка удаления решения: {e}")
            return False