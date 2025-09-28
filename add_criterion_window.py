from PyQt6.QtWidgets import QDialog
from PyQt6 import uic
import os
from PyQt6.QtGui import QIcon 


class AddCriterionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.criterion_data = None
        self.load_ui()
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'logo.ico')))

    def load_ui(self):
        try:
            ui_path = os.path.join(os.path.dirname(__file__), 'ui', 'add_criterion.ui')
            uic.loadUi(ui_path, self)
            self.setWindowTitle("Добавление критерия")
            
            # Подключаем кнопки
            if hasattr(self, 'addButton'):
                self.addButton.clicked.connect(self.accept)
            if hasattr(self, 'cancelButton'):
                self.cancelButton.clicked.connect(self.reject)
            
            print("Окно добавления критерия загружено")
            
        except Exception as e:
            print(f"Ошибка загрузки UI окна добавления критерия: {e}")
    
    def get_criterion_data(self):
        """Возвращает данные критерия"""
        data = {
            'name': '',
            'type': 'numeric',
            'weight': 5,
            'units': ''
        }
        
        if hasattr(self, 'criterionNameEdit'):
            data['name'] = self.criterionNameEdit.text()
        
        if hasattr(self, 'weightSpin'):
            data['weight'] = self.weightSpin.value()
        
        if hasattr(self, 'unitsEdit'):
            data['units'] = self.unitsEdit.text()
        
        # Определяем тип критерия
        if hasattr(self, 'numericRadio') and self.numericRadio.isChecked():
            data['type'] = 'numeric'
        elif hasattr(self, 'textRadio') and self.textRadio.isChecked():
            data['type'] = 'text'
        elif hasattr(self, 'choiceRadio') and self.choiceRadio.isChecked():
            data['type'] = 'choice'
            
        return data