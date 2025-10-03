from PyQt6.QtWidgets import QDialog
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
            
            # Подключаем кнопку "Назад"
            if hasattr(self, 'backBtn'):
                self.backBtn.clicked.connect(self.reject)
                
        except Exception as e:
            print(f"Ошибка загрузки UI окна анализа: {e}")
    
    def load_analysis_data(self):
        """Загрузка данных анализа из БД"""
        if not self.decision_id:
            return
            
        try:
            # Получаем результаты анализа
            results = self.db.get_analysis_results(self.decision_id)
            
            # Обновляем интерфейс с реальными данными
            if hasattr(self, 'resultLabel'):
                result_text = "Результаты анализа:\n\n"
                for result in results:
                    result_text += f"{result[3]}. {result[1]} - {result[2]:.1f} баллов\n"
                self.resultLabel.setText(result_text)
                
        except Exception as e:
            print(f"Ошибка загрузки данных анализа: {e}")