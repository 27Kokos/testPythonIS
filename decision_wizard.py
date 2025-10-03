from PyQt6.QtWidgets import (QDialog, QTableWidgetItem, QCheckBox, 
                             QSpinBox, QMessageBox)
from PyQt6 import uic
import os
from PyQt6.QtGui import QIcon
from database import Database

class DecisionWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = 0
        self.decision_id = None
        self.db = Database()
        
        # Данные решения
        self.decision_data = {
            'title': '',
            'description': '',
            'template_used': '',
            'options': [],  # Список словарей {name, description}
            'criteria': [], # Список словарей {name, type, weight}
            'evaluations': {} # Словарь {(option_index, criterion_index): value}
        }
        
        # Шаблоны критериев
        self.templates = {
            "Покупка товара": [
                {"name": "Цена", "type": "number", "weight": 4},
                {"name": "Качество", "type": "boolean", "weight": 5},
                {"name": "Гарантия", "type": "boolean", "weight": 3}
            ],
            "Выбор проекта": [
                {"name": "Бюджет", "type": "number", "weight": 5},
                {"name": "Сроки", "type": "number", "weight": 4},
                {"name": "Риски", "type": "number", "weight": 3}
            ],
            "Подбор команды": [
                {"name": "Опыт", "type": "number", "weight": 5},
                {"name": "Наличие", "type": "boolean", "weight": 4},
                {"name": "Стоимость", "type": "number", "weight": 3}
            ],
            "Базовый": [
                {"name": "Критерий 1", "type": "number", "weight": 3},
                {"name": "Критерий 2", "type": "boolean", "weight": 3}
            ]
        }
        
        self.load_ui()
        self.setup_connections()
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'logo.ico')))
    
    def load_ui(self):
        try:
            ui_path = os.path.join(os.path.dirname(__file__), 'ui', 'decision_wizard.ui')
            uic.loadUi(ui_path, self)
        except Exception as e:
            print(f"Ошибка загрузки UI мастера: {e}")
    
    def setup_connections(self):
        """Настройка сигналов"""
        self.backBtn.clicked.connect(self.previous_step)
        self.nextBtn.clicked.connect(self.next_step)
        self.cancelBtn.clicked.connect(self.reject)
        
        # Шаг 1
        self.titleEdit.textChanged.connect(self.validate_step1)
        
        # Шаг 2
        self.addOptionBtn.clicked.connect(self.add_option)
        self.removeOptionBtn.clicked.connect(self.remove_option)
        
        # Шаг 3
        self.templateCombo.currentTextChanged.connect(self.apply_template)
        self.addCriterionBtn.clicked.connect(self.add_criterion)
        self.removeCriterionBtn.clicked.connect(self.remove_criterion)
        
        # Шаг 5
        self.saveBtn.clicked.connect(self.save_decision)
    
    def validate_step1(self):
        """Валидация шага 1"""
        self.nextBtn.setEnabled(bool(self.titleEdit.text().strip()))
    
    def add_option(self):
        """Добавление варианта"""
        name = self.optionNameEdit.text().strip()
        if name:
            self.optionsList.addItem(name)
            self.optionNameEdit.clear()
    
    def remove_option(self):
        """Удаление варианта"""
        current_row = self.optionsList.currentRow()
        if current_row >= 0:
            self.optionsList.takeItem(current_row)
    
    def apply_template(self, template_name):
        """Применение шаблона критериев"""
        if template_name and template_name in self.templates:
            self.criteriaTable.setRowCount(0)
            for criterion in self.templates[template_name]:
                row = self.criteriaTable.rowCount()
                self.criteriaTable.insertRow(row)
                self.criteriaTable.setItem(row, 0, QTableWidgetItem(criterion["name"]))
                self.criteriaTable.setItem(row, 1, QTableWidgetItem(criterion["type"]))
                self.criteriaTable.setItem(row, 2, QTableWidgetItem(str(criterion["weight"])))
    
    def add_criterion(self):
        """Добавление критерия"""
        name = self.criterionNameEdit.text().strip()
        if name:
            row = self.criteriaTable.rowCount()
            self.criteriaTable.insertRow(row)
            self.criteriaTable.setItem(row, 0, QTableWidgetItem(name))
            
            # Тип критерия
            type_combo = self.criterionTypeCombo.currentText()
            self.criteriaTable.setItem(row, 1, QTableWidgetItem(type_combo))
            
            # Вес критерия
            weight = self.criterionWeightSpin.value()
            self.criteriaTable.setItem(row, 2, QTableWidgetItem(str(weight)))
            
            self.criterionNameEdit.clear()
    
    def remove_criterion(self):
        """Удаление критерия"""
        current_row = self.criteriaTable.currentRow()
        if current_row >= 0:
            self.criteriaTable.removeRow(current_row)
    
    def collect_step_data(self):
        """Сбор данных с текущего шага"""
        if self.current_step == 0:
            # Шаг 1: Основное
            self.decision_data['title'] = self.titleEdit.text().strip()
            self.decision_data['description'] = self.descEdit.toPlainText().strip()
            
        elif self.current_step == 1:
            # Шаг 2: Варианты
            self.decision_data['options'] = []
            for i in range(self.optionsList.count()):
                option_name = self.optionsList.item(i).text()
                self.decision_data['options'].append({
                    'name': option_name,
                    'description': ''
                })
                
        elif self.current_step == 2:
            # Шаг 3: Критерии
            self.decision_data['criteria'] = []
            self.decision_data['template_used'] = self.templateCombo.currentText()
            
            for row in range(self.criteriaTable.rowCount()):
                name_item = self.criteriaTable.item(row, 0)
                type_item = self.criteriaTable.item(row, 1)
                weight_item = self.criteriaTable.item(row, 2)
                
                if name_item and type_item and weight_item:
                    criterion_type = 'number' if type_item.text() == 'Число' else 'boolean'
                    self.decision_data['criteria'].append({
                        'name': name_item.text(),
                        'type': criterion_type,
                        'weight': int(weight_item.text())
                    })
                    
        elif self.current_step == 3:
            # Шаг 4: Оценки - собираем данные из таблицы
            self.decision_data['evaluations'] = {}
            
            for row in range(self.evaluationTable.rowCount()):
                for col in range(1, self.evaluationTable.columnCount()):  # Пропускаем первый столбец с названиями
                    item = self.evaluationTable.item(row, col)
                    if item:
                        criterion_index = col - 1
                        option_index = row
                        self.decision_data['evaluations'][(option_index, criterion_index)] = item.text()
    
    def setup_evaluation_table(self):
        """Настройка таблицы оценок на основе вариантов и критериев"""
        options_count = len(self.decision_data['options'])
        criteria_count = len(self.decision_data['criteria'])
        
        self.evaluationTable.setRowCount(options_count)
        self.evaluationTable.setColumnCount(criteria_count + 1)  # +1 для названий вариантов
        
        # Заголовки столбцов
        headers = ['Варианты']
        for criterion in self.decision_data['criteria']:
            headers.append(f"{criterion['name']}\n({criterion['type']})")
        self.evaluationTable.setHorizontalHeaderLabels(headers)
        
        # Заполняем названия вариантов
        for i, option in enumerate(self.decision_data['options']):
            self.evaluationTable.setItem(i, 0, QTableWidgetItem(option['name']))
            
            # Заполняем ячейки для критериев
            for j, criterion in enumerate(self.decision_data['criteria']):
                if criterion['type'] == 'boolean':
                    # Для boolean критериев используем чекбоксы
                    checkbox = QCheckBox()
                    checkbox.setChecked(False)
                    self.evaluationTable.setCellWidget(i, j + 1, checkbox)
                else:
                    # Для числовых критериев - текстовые поля
                    item = QTableWidgetItem("")
                    self.evaluationTable.setItem(i, j + 1, item)
    
    def previous_step(self):
        """Переход к предыдущему шагу"""
        if self.current_step > 0:
            self.current_step -= 1
            self.update_ui()
    
    def next_step(self):
        """Переход к следующему шагу"""
        # Собираем данные с текущего шага
        self.collect_step_data()
        
        # Проверяем валидность данных перед переходом
        if not self.validate_current_step():
            return
            
        if self.current_step < 4:
            self.current_step += 1
            
            # Особые действия при переходе на определенные шаги
            if self.current_step == 4:  # Переход на шаг оценок
                self.setup_evaluation_table()
            elif self.current_step == 5:  # Переход на шаг результатов
                self.calculate_results()
                
            self.update_ui()
    
    def validate_current_step(self):
        """Валидация данных текущего шага"""
        if self.current_step == 1 and len(self.decision_data['options']) < 2:
            QMessageBox.warning(self, "Ошибка", "Добавьте как минимум 2 варианта")
            return False
        elif self.current_step == 2 and len(self.decision_data['criteria']) < 1:
            QMessageBox.warning(self, "Ошибка", "Добавьте как минимум 1 критерий")
            return False
        return True
    
    def update_ui(self):
        """Обновление интерфейса при смене шага"""
        self.stackedWidget.setCurrentIndex(self.current_step)
        
        # Обновление прогресса
        step_names = ["Основное", "Варианты", "Критерии", "Оценки", "Результат"]
        self.progressLabel.setText(f"Шаг {self.current_step + 1}/5: {step_names[self.current_step]}")
        
        # Обновление кнопок
        self.backBtn.setEnabled(self.current_step > 0)
        
        if self.current_step == 4:  # Последний шаг
            self.nextBtn.setEnabled(False)
            self.nextBtn.setText("Завершено")
        else:
            self.nextBtn.setEnabled(True)
            self.nextBtn.setText("Далее")
    
    def calculate_results(self):
        """Расчет итоговых результатов"""
        try:
            # Собираем все оценки из таблицы
            self.collect_step_data()
            
            # Сохраняем решение в БД
            self.save_to_database()
            
            # Рассчитываем результаты
            results = self.perform_calculation()
            
            # Отображаем результаты
            self.resultsList.clear()
            for i, (option_name, score) in enumerate(results):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🔹"
                self.resultsList.addItem(f"{medal} {option_name} - {score:.1f} баллов")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка расчета результатов: {str(e)}")
    
    def save_to_database(self):
        """Сохранение решения в базу данных"""
        try:
            # Сохраняем основное решение
            self.decision_id = self.db.add_decision(
                self.decision_data['title'],
                self.decision_data['description'],
                self.decision_data['template_used']
            )
            
            if not self.decision_id:
                raise Exception("Не удалось сохранить решение в БД")
            
            # Сохраняем варианты
            option_ids = []
            for option in self.decision_data['options']:
                option_id = self.db.add_option(
                    self.decision_id,
                    option['name'],
                    option['description']
                )
                if option_id:
                    option_ids.append(option_id)
            
            # Сохраняем критерии
            criterion_ids = []
            for criterion in self.decision_data['criteria']:
                criterion_id = self.db.add_criterion(
                    self.decision_id,
                    criterion['name'],
                    criterion['type'],
                    criterion['weight']
                )
                if criterion_id:
                    criterion_ids.append(criterion_id)
            
            # Сохраняем оценки
            for (option_idx, criterion_idx), value in self.decision_data['evaluations'].items():
                if option_idx < len(option_ids) and criterion_idx < len(criterion_ids):
                    # Для boolean преобразуем в 1/0
                    if self.decision_data['criteria'][criterion_idx]['type'] == 'boolean':
                        value = "1" if value.lower() in ['true', '1', 'да', 'yes'] else "0"
                    
                    self.db.add_evaluation(
                        self.decision_id,
                        option_ids[option_idx],
                        criterion_ids[criterion_idx],
                        value
                    )
            
            return True
            
        except Exception as e:
            print(f"Ошибка сохранения в БД: {e}")
            return False
    
    def perform_calculation(self):
        """Выполнение расчетов по алгоритму взвешенной суммы"""
        try:
            # Получаем данные из БД для расчета
            options_data = self.db.get_options_by_decision(self.decision_id)
            criteria_data = self.db.get_criteria_by_decision(self.decision_id)
            evaluations_data = self.db.get_evaluations_by_decision(self.decision_id)
            
            # Создаем структуры для удобства
            options = {opt[0]: opt[1] for opt in options_data}  # id: name
            criteria = {crt[0]: {'name': crt[1], 'type': crt[2], 'weight': crt[3]} 
                       for crt in criteria_data}
            
            # Собираем оценки
            scores = {}
            for eval_data in evaluations_data:
                option_id, criterion_id, value, option_name, criterion_name = eval_data
                
                if option_id not in scores:
                    scores[option_id] = {'name': option_name, 'total': 0}
                
                criterion = criteria[criterion_id]
                numeric_value = self.normalize_value(value, criterion, evaluations_data, criterion_id)
                scores[option_id]['total'] += numeric_value * criterion['weight']
            
            # Сортируем по убыванию баллов
            sorted_scores = sorted(
                [(data['name'], data['total']) for data in scores.values()],
                key=lambda x: x[1],
                reverse=True
            )
            
            # Сохраняем результаты в БД
            results = []
            for rank, (option_name, score) in enumerate(sorted_scores, 1):
                option_id = next(oid for oid, data in scores.items() if data['name'] == option_name)
                results.append((option_id, score, rank))
            
            self.db.save_analysis_results(self.decision_id, results)
            
            return sorted_scores
            
        except Exception as e:
            print(f"Ошибка расчета: {e}")
            return [("Ошибка расчета", 0)]
    
    def normalize_value(self, value, criterion, all_evaluations, current_criterion_id):
        """Нормализация значений для расчета"""
        if criterion['type'] == 'boolean':
            return 1.0 if value == '1' else 0.0
        
        elif criterion['type'] == 'number':
            try:
                numeric_value = float(value)
                # Находим мин/макс значения для этого критерия
                values = []
                for eval_data in all_evaluations:
                    if eval_data[1] == current_criterion_id:  # criterion_id
                        try:
                            values.append(float(eval_data[2]))  # value
                        except ValueError:
                            continue
                
                if not values:
                    return 0.0
                
                min_val = min(values)
                max_val = max(values)
                
                if max_val == min_val:
                    return 1.0  # Все значения одинаковые
                
                # Нормализация 0-1
                return (numeric_value - min_val) / (max_val - min_val)
                
            except ValueError:
                return 0.0
        
        return 0.0
    
    def save_decision(self):
        """Сохранение решения и закрытие мастера"""
        try:
            QMessageBox.information(self, "Успех", "Решение успешно сохранено!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")
    
    def get_decision_data(self):
        """Возвращает данные решения"""
        return {
            'id': self.decision_id,
            **self.decision_data
        }