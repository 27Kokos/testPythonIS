from PyQt6.QtWidgets import QDialog
from PyQt6 import uic
import os
from PyQt6.QtGui import QIcon 

class AnalysisDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load_ui()
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'logo.ico')))
        
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