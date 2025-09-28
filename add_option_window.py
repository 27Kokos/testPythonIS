from PyQt6.QtWidgets import QDialog
from PyQt6 import uic
import os
from PyQt6.QtGui import QIcon 

class AddOptionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.option_data = None
        self.load_ui()
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'logo.ico')))
        
    def load_ui(self):
        try:
            ui_path = os.path.join(os.path.dirname(__file__), 'ui', 'add_option.ui')
            uic.loadUi(ui_path, self)
            self.setWindowTitle("Добавление варианта")
            
            # Подключаем кнопки
            self.addButton.clicked.connect(self.accept)
            self.cancelButton.clicked.connect(self.reject)
            
        except Exception as e:
            print(f"Ошибка загрузки UI окна добавления варианта: {e}")
    
    def get_option_data(self):
        """Возвращает данные варианта"""
        return {
            'name': self.optionNameEdit.text(),
            'description': self.optionDescEdit.toPlainText(),
            'price': self.priceEdit.text(),
            'time': self.timeEdit.text(),
            'quality': self.qualityCombo.currentText()
        }