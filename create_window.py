from PyQt6.QtWidgets import QDialog, QListWidgetItem, QTableWidgetItem
from PyQt6 import uic
import os
from PyQt6.QtGui import QIcon 
from database import Database

class CreateDecisionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.options = []
        self.criteria = [] 
        self.load_ui()
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'logo.ico')))
        self.db = Database()
        
    def load_ui(self):
        try:
            ui_path = os.path.join(os.path.dirname(__file__), 'ui', 'createv2.ui')
            uic.loadUi(ui_path, self)
            self.setWindowTitle("Создание решения")
            
            if hasattr(self, 'cancelButton'):
                self.cancelButton.clicked.connect(self.reject)
            if hasattr(self, 'saveBtn'):
                self.saveBtn.clicked.connect(self.accept)
            if hasattr(self, 'analyzeBtn'):
                self.analyzeBtn.clicked.connect(self.open_analysis)
            
            if hasattr(self, 'addOptionBtn'):
                self.addOptionBtn.clicked.connect(self.open_add_option_dialog)
                print("Кнопка 'Добавить вариант' подключена")
            else:
                print("Кнопка addOptionBtn не найдена!")
                
            if hasattr(self, 'removeOptionBtn'):
                self.removeOptionBtn.clicked.connect(self.remove_option)

            if hasattr(self, 'addCriteriaBtn'):
                self.addCriteriaBtn.clicked.connect(self.open_add_criterion_dialog)
                print("Кнопка 'Добавить критерий' подключена")
            else:
                print("Кнопка addCriteriaBtn не найдена!")
            
        except Exception as e:
            print(f"Ошибка загрузки UI окна создания: {e}")
    
    def open_add_option_dialog(self):
        print("Нажата кнопка 'Добавить вариант'")
        try:
            from add_option_window import AddOptionDialog
            dialog = AddOptionDialog(self)
            if dialog.exec():
                # Пользователь нажал "Добавить"
                option_data = dialog.get_option_data()
                self.add_option_to_list(option_data)
                print(f"Добавлен вариант: {option_data['name']}")
            else:
                print("Добавление варианта отменено")
        except Exception as e:
            print(f"Ошибка открытия окна добавления варианта: {e}")
    
    def add_option_to_list(self, option_data):
        """Добавляет вариант в список"""
        self.options.append(option_data)
        
        if hasattr(self, 'optionsList'):
            item = QListWidgetItem(option_data['name'])
            if option_data['description']:
                item.setToolTip(option_data['description'])
            self.optionsList.addItem(item)
            
            if hasattr(self, 'analyzeBtn'):
                self.analyzeBtn.setEnabled(True)
    
    def remove_option(self):
        """Удаляет выбранный вариант"""
        if hasattr(self, 'optionsList'):
            current_row = self.optionsList.currentRow()
            if current_row >= 0:
                self.optionsList.takeItem(current_row)
                self.options.pop(current_row)
                print(f"Удален вариант в позиции {current_row}")
                
                # Отключаем кнопку анализа если вариантов нет
                if hasattr(self, 'analyzeBtn') and self.optionsList.count() == 0:
                    self.analyzeBtn.setEnabled(False)
    
    def open_add_criterion_dialog(self):
        """Открывает окно добавления критерия"""
        print("Нажата кнопка 'Добавить критерий'")
        try:
            from add_criterion_window import AddCriterionDialog
            dialog = AddCriterionDialog(self)
            if dialog.exec():
                # Пользователь нажал "Добавить"
                criterion_data = dialog.get_criterion_data()
                self.add_criterion_to_table(criterion_data)
                print(f"Добавлен критерий: {criterion_data['name']}")
            else:
                print("Добавление критерия отменено")
        except Exception as e:
            print(f"Ошибка открытия окна добавления критерия: {e}")

    def add_criterion_to_table(self, criterion_data):
        """Добавляет критерий в таблицу"""
        self.criteria.append(criterion_data)
        
        # Добавляем в таблицу критериев (предполагается, что у вас есть таблица criteriaTable)
        if hasattr(self, 'criteriaTable'):
            row_position = self.criteriaTable.rowCount()
            self.criteriaTable.insertRow(row_position)
            
            # Добавляем название критерия
            self.criteriaTable.setItem(row_position, 0, QTableWidgetItem(criterion_data['name']))
            
            # Добавляем тип критерия (максимизация/минимизация)
            criterion_type = "Максимизация" if criterion_data['maximize'] else "Минимизация"
            self.criteriaTable.setItem(row_position, 1, QTableWidgetItem(criterion_type))
            
            # Добавляем вес критерия
            self.criteriaTable.setItem(row_position, 2, QTableWidgetItem(str(criterion_data['weight'])))
            
            print(f"Критерий добавлен в таблицу: {criterion_data['name']}")
    
    def open_analysis(self):
        """Открывает окно анализа"""
        print("Нажата кнопка Анализировать!")
        try:
            from analysis_window import AnalysisDialog
            analysis_dialog = AnalysisDialog(self)
            analysis_dialog.exec()
            print("Окно анализа закрыто")
        except Exception as e:
            print(f"Ошибка открытия окна анализа: {e}")
    
    def get_decision_data(self):
        return {
            'title': self.textEdit_2.toPlainText() if hasattr(self, 'textEdit_2') else '',
            'description': self.textEdit.toPlainText() if hasattr(self, 'textEdit') else '',
            'options': self.options,
            'criteria': self.criteria
        }