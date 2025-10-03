from PyQt6.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt  # ДОБАВИТЬ ЭТОТ ИМПОРТ
from PyQt6 import uic
import os
from PyQt6.QtGui import QIcon 


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui()
        self.setup_content_area()
        self.connect_buttons()
        self.show_home()
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'logo.ico')))
        
    def load_ui(self):
        try:
            ui_path = os.path.join(os.path.dirname(__file__), 'ui', 'main.ui')
            uic.loadUi(ui_path, self)
            self.setWindowTitle("Decision Helper - Главное меню")
            print("Главное окно загружено успешно")
            
        except Exception as e:
            print(f"Ошибка загрузки главного окна: {e}")
    
    def setup_content_area(self):
        """Настраиваем область контента"""
        if hasattr(self, 'widget_2'):
            if self.widget_2.layout() is None:
                layout = QVBoxLayout()
                self.widget_2.setLayout(layout)
    
    def connect_buttons(self):
        """Подключаем все кнопки сайдбара"""
        if hasattr(self, 'pushButton'):
            self.pushButton.clicked.connect(self.show_home)
        if hasattr(self, 'pushButton_2'):
            self.pushButton_2.clicked.connect(self.show_my_decisions)
        if hasattr(self, 'pushButton_3'):
            self.pushButton_3.clicked.connect(self.show_history)
        if hasattr(self, 'pushButton_4'):
            self.pushButton_4.clicked.connect(self.show_favorites)
        if hasattr(self, 'pushButton_5'):
            self.pushButton_5.clicked.connect(self.show_help)
        if hasattr(self, 'pushButton_6'):
            self.pushButton_6.clicked.connect(self.show_settings)
        if hasattr(self, 'pushButton_7'):
            self.pushButton_7.clicked.connect(self.create_decision)
    
    def clear_content_area(self):
        """Очищаем основную область"""
        if hasattr(self, 'widget_2') and self.widget_2.layout():
            while self.widget_2.layout().count():
                item = self.widget_2.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
    
    def load_ui_widget(self, ui_file_name):
        """Загружает UI файл и возвращает виджет"""
        try:
            ui_path = os.path.join(os.path.dirname(__file__), 'ui', ui_file_name)
            return uic.loadUi(ui_path)
        except Exception as e:
            print(f"Ошибка загрузки {ui_file_name}: {e}")
            return None
    
    def show_home(self):
        """Показать главную страницу"""
        self.set_active_button(self.pushButton)
        self.clear_content_area()
        
        home_widget = self.load_ui_widget('home_page.ui')
        if home_widget:
            if hasattr(home_widget, 'createButton'):
                home_widget.createButton.clicked.connect(self.create_decision)
            if hasattr(home_widget, 'historyButton'):
                home_widget.historyButton.clicked.connect(self.show_history)
            self.widget_2.layout().addWidget(home_widget)
    
    def show_my_decisions(self):
        """Показать мои решения"""
        self.set_active_button(self.pushButton_2)
        self.clear_content_area()
        
        decisions_widget = self.load_ui_widget('decisions_page.ui')
        if decisions_widget:
            # Загружаем решения из БД
            from database import Database
            db = Database()
            decisions = db.get_decisions()
            
            # Очищаем placeholder и добавляем реальные решения
            if hasattr(decisions_widget, 'placeholderLabel'):
                decisions_widget.placeholderLabel.setText("")  # Очищаем заглушку
            
            # Создаем виджет для отображения решений
            decisions_list = QListWidget()
            for decision in decisions:
                item_text = f"{decision[1]} - {decision[3]}"  # Название + дата
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, decision[0])  # ID решения
                decisions_list.addItem(item)
            
            # Подключаем двойной клик для открытия решения
            decisions_list.itemDoubleClicked.connect(self.open_decision)
            
            layout = decisions_widget.layout()
            if layout:
                layout.addWidget(decisions_list)
            
            self.widget_2.layout().addWidget(decisions_widget)

    def open_decision(self, item):
        """Открытие выбранного решения"""
        decision_id = item.data(Qt.ItemDataRole.UserRole)
        from database import Database
        db = Database()
        
        # Получаем данные решения
        decision_data = db.get_decision_by_id(decision_id)
        if not decision_data:
            QMessageBox.warning(self, "Ошибка", "Решение не найдено")
            return
            
        options = db.get_options_by_decision(decision_id)
        criteria = db.get_criteria_by_decision(decision_id)
        results = db.get_analysis_results(decision_id)
        
        # Показываем информацию о решении
        info_text = f"Решение: {decision_data[1]}\n\n"
        info_text += f"Описание: {decision_data[2]}\n\n"
        
        info_text += f"Варианты:\n"
        for option in options:
            info_text += f"- {option[1]}\n"
        
        info_text += f"\nКритерии:\n"
        for criterion in criteria:
            info_text += f"- {criterion[1]} (тип: {criterion[2]}, вес: {criterion[3]})\n"
        
        if results:
            info_text += f"\nРезультаты:\n"
            for result in results:
                info_text += f"{result[3]}. {result[1]} - {result[2]:.1f} баллов\n"
        else:
            info_text += f"\nРезультаты анализа отсутствуют"
        
        QMessageBox.information(self, "Информация о решении", info_text)
    
    def show_history(self):
        """Показать историю анализов"""
        self.set_active_button(self.pushButton_3)
        self.clear_content_area()
        
        history_widget = self.load_ui_widget('history_page.ui')
        if history_widget:
            self.widget_2.layout().addWidget(history_widget)
    
    def show_favorites(self):
        """Показать избранное"""
        self.set_active_button(self.pushButton_4)
        self.clear_content_area()
        
        favorites_widget = self.load_ui_widget('favorites_page.ui')
        if favorites_widget:
            self.widget_2.layout().addWidget(favorites_widget)
    
    def show_help(self):
        """Показать помощь"""
        self.set_active_button(self.pushButton_5)
        QMessageBox.information(self, "Помощь", "Раздел помощи будет реализован позже")
    
    def show_settings(self):
        """Показать настройки"""
        self.set_active_button(self.pushButton_6)
        QMessageBox.information(self, "Настройки", "Раздел настроек в разработке")
    
    def create_decision(self):
        """Открыть окно создания решения"""
        try:
            from decision_wizard import DecisionWizard
            dialog = DecisionWizard(self)
            if dialog.exec():
                decision_data = dialog.get_decision_data()
                print(f"Создано решение: {decision_data['title']}")
        except Exception as e:
            print(f"Ошибка открытия окна создания: {e}")
    
    def set_active_button(self, active_button):
        """Подсветка активной кнопки"""
        buttons = [self.pushButton, self.pushButton_2, self.pushButton_3, 
                   self.pushButton_4, self.pushButton_5, self.pushButton_6]
        
        for btn in buttons:
            if btn:
                btn.setStyleSheet("""
                    QPushButton{
                        background-color: rgb(255, 255, 255);
                    }
                    QPushButton:hover{
                        background-color: rgb(214, 225, 229);
                    }
                """)
        
        if active_button:
            active_button.setStyleSheet("""
                QPushButton{
                    background-color: rgb(200, 230, 240);
                }
            """)