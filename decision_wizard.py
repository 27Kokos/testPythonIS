from PyQt6.QtWidgets import QDialog, QTableWidgetItem, QCheckBox, QLineEdit, QMessageBox
from PyQt6 import uic
import os
from PyQt6.QtGui import QIcon, QDoubleValidator
from database import Database

class DecisionWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = 0
        self.db = Database()
        
        # Данные
        self.decision_data = {
            'title': '', 'description': '', 'options': [], 'criteria': [], 'evaluations': {}
        }
        
        self.templates = {
            "Покупка товара": [{"name": "Цена", "type": "number", "weight": 4}, {"name": "Качество", "type": "boolean", "weight": 5}],
            "Выбор проекта": [{"name": "Бюджет", "type": "number", "weight": 5}, {"name": "Сроки", "type": "number", "weight": 4}],
            "Подбор команды": [{"name": "Опыт", "type": "number", "weight": 5}, {"name": "Наличие", "type": "boolean", "weight": 4}],
            "Базовый": [{"name": "Критерий 1", "type": "number", "weight": 3}]
        }
        
        self.load_ui()
        self.setup_connections()
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'logo.ico')))
        self.update_step_label()
        
    def load_ui(self):
        try:
            ui_path = os.path.join(os.path.dirname(__file__), 'ui', 'decision_wizard.ui')
            uic.loadUi(ui_path, self)
        except Exception as e:
            print(f"Ошибка загрузки UI: {e}")
            self.reject()
    
    def setup_connections(self):
        self.backBtn.clicked.connect(self.previous_step)
        self.nextBtn.clicked.connect(self.next_step)
        self.cancelBtn.clicked.connect(self.reject)
        self.titleEdit.textChanged.connect(self.validate_step1)
        self.addOptionBtn.clicked.connect(self.add_option)
        self.removeOptionBtn.clicked.connect(self.remove_option)
        self.templateCombo.currentTextChanged.connect(self.apply_template)
        self.addCriterionBtn.clicked.connect(self.add_criterion)
        self.removeCriterionBtn.clicked.connect(self.remove_criterion)
        self.saveBtn.clicked.connect(self.save_decision)
    
    def update_step_label(self):
        self.stepLabel.setText(f"Шаг {self.current_step + 1}/5")
        self.backBtn.setEnabled(self.current_step > 0)
        self.nextBtn.setText("Сохранить" if self.current_step == 4 else "Далее")
    
    def validate_step1(self):
        self.nextBtn.setEnabled(bool(self.titleEdit.text().strip()))
    
    def next_step(self):
        if not self.collect_current_data():
            return
        if self.current_step == 2:
            self.setup_evaluations()
        if self.current_step == 3:
            self.calculate_and_show_results()
        if self.current_step < 4:
            self.current_step += 1
            self.stackedWidget.setCurrentIndex(self.current_step)
            self.update_step_label()
    
    def previous_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.stackedWidget.setCurrentIndex(self.current_step)
            self.update_step_label()
    
    def collect_current_data(self):
        if self.current_step == 0:
            self.decision_data['title'] = self.titleEdit.text().strip()
            self.decision_data['description'] = self.descriptionEdit.toPlainText().strip()
            if not self.decision_data['title']:
                QMessageBox.warning(self, "Ошибка", "Введите название!")
                return False
        elif self.current_step == 1:
            self.decision_data['options'] = [self.optionsList.item(i).text() for i in range(self.optionsList.count())]
            if len(self.decision_data['options']) < 2:
                QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы 2 варианта!")
                return False
        elif self.current_step == 2:
            self.decision_data['criteria'] = []
            for row in range(self.criteriaTable.rowCount()):
                name_item = self.criteriaTable.item(row, 0)
                type_item = self.criteriaTable.item(row, 1)
                weight_item = self.criteriaTable.item(row, 2)
                if name_item and type_item and weight_item:
                    self.decision_data['criteria'].append({
                        'name': name_item.text(), 'type': type_item.text(), 'weight': int(weight_item.text())
                    })
            if len(self.decision_data['criteria']) == 0:
                QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы 1 критерий!")
                return False
        elif self.current_step == 3:
            self.decision_data['evaluations'] = {}
            for i in range(self.evaluationsTable.rowCount()):
                for j in range(1, self.evaluationsTable.columnCount()):
                    widget = self.evaluationsTable.cellWidget(i, j)
                    if isinstance(widget, QCheckBox):
                        value = '1' if widget.isChecked() else '0'
                    elif isinstance(widget, QLineEdit):
                        value = widget.text().strip()
                        if not value or not value.replace('.','').isdigit():
                            QMessageBox.warning(self, "Ошибка", "Заполните все оценки числами!")
                            return False
                    self.decision_data['evaluations'][(i, j-1)] = value
        return True
    
    def add_option(self):
        name = self.optionNameEdit.text().strip()
        if name:
            self.optionsList.addItem(name)
            self.optionNameEdit.clear()
    
    def remove_option(self):
        row = self.optionsList.currentRow()
        if row >= 0:
            self.optionsList.takeItem(row)
    
    def apply_template(self, template_name):
        if template_name in self.templates:
            self.criteriaTable.setRowCount(0)
            for crit in self.templates[template_name]:
                row = self.criteriaTable.rowCount()
                self.criteriaTable.insertRow(row)
                self.criteriaTable.setItem(row, 0, QTableWidgetItem(crit['name']))
                self.criteriaTable.setItem(row, 1, QTableWidgetItem(crit['type']))
                self.criteriaTable.setItem(row, 2, QTableWidgetItem(str(crit['weight'])))
    
    def add_criterion(self):
        name = self.criterionNameEdit.text().strip()
        type_ = "number" if self.typeCombo.currentText() == "Число" else "boolean"
        weight = self.weightSpin.value()
        if name:
            row = self.criteriaTable.rowCount()
            self.criteriaTable.insertRow(row)
            self.criteriaTable.setItem(row, 0, QTableWidgetItem(name))
            self.criteriaTable.setItem(row, 1, QTableWidgetItem(type_))
            self.criteriaTable.setItem(row, 2, QTableWidgetItem(str(weight)))
            self.criterionNameEdit.clear()
    
    def remove_criterion(self):
        row = self.criteriaTable.currentRow()
        if row >= 0:
            self.criteriaTable.removeRow(row)
    
    def setup_evaluations(self):
        options = self.decision_data['options']
        criteria = self.decision_data['criteria']
        table = self.evaluationsTable
        table.setRowCount(len(options))
        table.setColumnCount(len(criteria) + 1)
        table.setHorizontalHeaderLabels(["Вариант"] + [c['name'] for c in criteria])
        for i, opt in enumerate(options):
            table.setItem(i, 0, QTableWidgetItem(opt))
            for j, crit in enumerate(criteria):
                if crit['type'] == 'boolean':
                    chk = QCheckBox()
                    table.setCellWidget(i, j+1, chk)
                else:
                    edit = QLineEdit()
                    edit.setValidator(QDoubleValidator())
                    table.setCellWidget(i, j+1, edit)
    
    def calculate_and_show_results(self):
        scores = {}
        for i, opt in enumerate(self.decision_data['options']):
            total = 0.0
            for j, crit in enumerate(self.decision_data['criteria']):
                value = self.decision_data['evaluations'].get((i, j), '0')
                norm = 1.0 if value == '1' else 0.0 if crit['type'] == 'boolean' else float(value) / 10.0
                total += norm * crit['weight']
            scores[opt] = total
        # Сортировка
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        self.resultsList.clear()
        for rank, (opt, score) in enumerate(sorted_results, 1):
            self.resultsList.addItem(f"{rank}. {opt} - {score:.1f} баллов")
        # Для БД
        self.sorted_results = [(opt, score, rank) for rank, (opt, score) in enumerate(sorted_results, 1)]
    
    def save_decision(self):
        if self.save_to_db():
            QMessageBox.information(self, "Успех", "Решение сохранено!")
            self.accept()
    
    def save_to_db(self):
        try:
            # Решение
            decision_id = self.db.add_decision(self.decision_data['title'], self.decision_data['description'])
            if not decision_id:
                return False
            
            # Варианты
            option_ids = []
            for opt in self.decision_data['options']:
                opt_id = self.db.add_option(decision_id, opt)
                option_ids.append(opt_id)
            
            # Критерии
            crit_ids = []
            for crit in self.decision_data['criteria']:
                crit_id = self.db.add_criterion(decision_id, crit['name'], crit['type'], crit['weight'])
                crit_ids.append(crit_id)
            
            # Оценки
            for (opt_idx, crit_idx), value in self.decision_data['evaluations'].items():
                self.db.add_evaluation(decision_id, option_ids[opt_idx], crit_ids[crit_idx], value)
            
            # Результаты
            if hasattr(self, 'sorted_results'):
                db_results = []
                for opt_name, score, rank in self.sorted_results:
                    opt_id = option_ids[self.decision_data['options'].index(opt_name)]
                    db_results.append((opt_id, score, rank))
                self.db.save_analysis_results(decision_id, db_results)
            
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
    
    def get_decision_data(self):
        return self.decision_data