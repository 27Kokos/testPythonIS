from PyQt6.QtWidgets import QDialog, QMessageBox  # Добавлен импорт QMessageBox
from PyQt6 import uic
import os
from PyQt6.QtGui import QIcon
from database import Database

class AnalysisDialog(QDialog):
    def __init__(self, decision_id=None, parent=None):
        super().__init__(parent)
        self.decision_id = decision_id
        self.db = Database()
        self.load_ui()
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'logo.ico')))
        self.load_analysis_data()
        
    def load_ui(self):
        try:
            ui_path = os.path.join(os.path.dirname(__file__), 'ui', 'analysis_window.ui')
            uic.loadUi(ui_path, self)
            self.setWindowTitle("Анализ решения")
            
            if hasattr(self, 'backBtn'):
                self.backBtn.clicked.connect(self.reject)
            if hasattr(self, 'saveReportBtn'):
                self.saveReportBtn.clicked.connect(self.save_report)
            if hasattr(self, 'exportBtn'):
                self.exportBtn.clicked.connect(self.export_data)
            if hasattr(self, 'favoriteBtn'):
                self.favoriteBtn.clicked.connect(self.toggle_favorite)
                
        except Exception as e:
            print(f"Ошибка загрузки UI окна анализа: {e}")
    
    def load_analysis_data(self):
        if not self.decision_id:
            return
            
        try:
            results = self.db.get_analysis_results(self.decision_id)
            evaluations = self.db.get_evaluations_by_decision(self.decision_id)
            options = self.db.get_options_by_decision(self.decision_id)
            criteria = self.db.get_criteria_by_decision(self.decision_id)
            
            if hasattr(self, 'resultLabel'):
                result_text = "Результаты анализа:\n\n"
                for result in sorted(results, key=lambda x: x[3]):
                    result_text += f"{result[3]}. {result[1]} - {result[2]:.1f} баллов\n"
                self.resultLabel.setText(result_text)
                
            if hasattr(self, 'visualLabel'):
                if results:
                    max_score = max([r[2] for r in results])
                    bar_text = "Визуальное сравнение:\n\n"
                    for result in results:
                        bar_length = int((result[2] / max_score) * 20) if max_score > 0 else 0
                        bar_text += f"{result[1]}: {'█' * bar_length} {result[2]:.1f}\n"
                    self.visualLabel.setText(bar_text)
                else:
                    self.visualLabel.setText("Нет данных")
            
            if hasattr(self, 'detailedTableLabel'):
                table_text = "Детальная таблица оценок:\n\n"
                table_text += "Вариант | " + " | ".join([c[1] for c in criteria]) + " | Итого\n"
                table_text += "-" * 50 + "\n"
                for opt in options:
                    row = f"{opt[1]} | "
                    for crit in criteria:
                        eval_val = next((e[2] for e in evaluations if e[0] == opt[0] and e[1] == crit[0]), "-")
                        row += f"{eval_val} | "
                    total = next((r[2] for r in results if r[0] == opt[0]), 0)
                    row += f"{total:.1f}"
                    table_text += row + "\n"
                self.detailedTableLabel.setText(table_text)
                
            if hasattr(self, 'favoriteBtn'):
                self.favoriteBtn.setText("Удалить из избранного" if self.db.is_favorite(self.decision_id) else "Добавить в избранное")
                
        except Exception as e:
            print(f"Ошибка загрузки данных анализа: {e}")
            if hasattr(self, 'resultLabel'):
                self.resultLabel.setText("Ошибка загрузки данных")

    def save_report(self):
        print("Сохранение отчёта...")

    def export_data(self):
        print("Экспорт данных...")

    def toggle_favorite(self):
        if self.db.is_favorite(self.decision_id):
            if self.db.remove_from_favorites(self.decision_id):
                QMessageBox.information(self, "Успех", "Удалено из избранного")
                if hasattr(self, 'favoriteBtn'):
                    self.favoriteBtn.setText("Добавить в избранное")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить из избранного")
        else:
            if self.db.add_to_favorites(self.decision_id):
                QMessageBox.information(self, "Успех", "Добавлено в избранное")
                if hasattr(self, 'favoriteBtn'):
                    self.favoriteBtn.setText("Удалить из избранного")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить в избранное")