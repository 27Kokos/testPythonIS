from PyQt6.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout
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
            self.widget_2.layout().addWidget(decisions_widget)
    
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
            from create_window import CreateDecisionDialog
            dialog = CreateDecisionDialog(self)
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