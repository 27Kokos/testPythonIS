from PyQt6.QtWidgets import QMainWindow, QMessageBox, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from PyQt6 import uic
import os
from PyQt6.QtGui import QIcon
from database import Database
from analysis_window import AnalysisDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
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
        except Exception as e:
            print(f"Ошибка загрузки главного окна: {e}")
    
    def setup_content_area(self):
        if hasattr(self, 'widget_2') and self.widget_2.layout() is None:
            from PyQt6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout()
            self.widget_2.setLayout(layout)
    
    def connect_buttons(self):
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
        if hasattr(self, 'widget_2') and self.widget_2.layout():
            while self.widget_2.layout().count():
                item = self.widget_2.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
    
    def load_ui_widget(self, ui_file_name):
        try:
            ui_path = os.path.join(os.path.dirname(__file__), 'ui', ui_file_name)
            return uic.loadUi(ui_path)
        except Exception as e:
            print(f"Ошибка загрузки {ui_file_name}: {e}")
            return None
    
    def show_home(self):
        self.set_active_button(self.pushButton)
        self.clear_content_area()
        
        home_widget = self.load_ui_widget('home_page.ui')
        if home_widget:
            if hasattr(home_widget, 'createButton'):
                home_widget.createButton.clicked.connect(self.create_decision)
            if hasattr(home_widget, 'historyButton'):
                home_widget.historyButton.clicked.connect(self.show_history)
            
            if hasattr(home_widget, 'statsLabel'):
                decisions_count = len(self.db.get_decisions())
                analyses_count = sum(1 for dec in self.db.get_decisions() if self.db.get_analysis_results(dec[0]))
                home_widget.statsLabel.setText(f" Быстрая статистика:\n• Всего решений: {decisions_count}\n• Завершенных анализов: {analyses_count}\n• Активных проектов: 0")
            
            self.widget_2.layout().addWidget(home_widget)
    
    def show_my_decisions(self):
        self.set_active_button(self.pushButton_2)
        self.clear_content_area()
        
        decisions_widget = self.load_ui_widget('decisions_page.ui')
        if decisions_widget:
            decisions = self.db.get_decisions()
            
            if hasattr(decisions_widget, 'placeholderLabel'):
                decisions_widget.placeholderLabel.setText("")
            
            if hasattr(decisions_widget, 'decisionsList'):
                decisions_list = decisions_widget.decisionsList
                decisions_list.clear()
                for dec in decisions:
                    item = QListWidgetItem(dec[1])
                    item.setData(Qt.ItemDataRole.UserRole, dec[0])
                    decisions_list.addItem(item)
                decisions_list.itemDoubleClicked.connect(self.open_decision)
                
            if hasattr(decisions_widget, 'deleteButton'):
                decisions_widget.deleteButton.clicked.connect(self.delete_selected_decision)
            
            self.widget_2.layout().addWidget(decisions_widget)

    def delete_selected_decision(self):
        if hasattr(self.widget_2.layout().itemAt(0).widget(), 'decisionsList'):
            decisions_list = self.widget_2.layout().itemAt(0).widget().decisionsList
            selected_item = decisions_list.currentItem()
            if selected_item:
                decision_id = selected_item.data(Qt.ItemDataRole.UserRole)
                reply = QMessageBox.question(self, "Удаление", "Удалить это решение?", 
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    if self.db.delete_decision(decision_id):
                        decisions_list.takeItem(decisions_list.currentRow())
                        QMessageBox.information(self, "Успех", "Решение удалено")
                    else:
                        QMessageBox.warning(self, "Ошибка", "Не удалось удалить решение")
    
    def open_decision(self, item):
        decision_id = item.data(Qt.ItemDataRole.UserRole)
        decision_data = self.db.get_decision_by_id(decision_id)
        if not decision_data:
            QMessageBox.warning(self, "Ошибка", "Решение не найдено")
            return
            
        options = self.db.get_options_by_decision(decision_id)
        criteria = self.db.get_criteria_by_decision(decision_id)
        results = self.db.get_analysis_results(decision_id)
        
        info_text = f"Решение: {decision_data[1]}\n\n"
        info_text += f"Описание: {decision_data[2] or 'Нет описания'}\n\n"
        
        info_text += "Варианты:\n"
        for option in options:
            info_text += f"- {option[1]}\n"
        
        info_text += "\nКритерии:\n"
        for criterion in criteria:
            info_text += f"- {criterion[1]} (тип: {criterion[2]}, вес: {criterion[3]})\n"
        
        if results:
            info_text += "\nРезультаты:\n"
            for result in results:
                info_text += f"{result[3]}. {result[1]} - {result[2]:.1f} баллов\n"
        else:
            info_text += "\nРезультаты анализа отсутствуют"
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Информация о решении")
        msg.setText(info_text)
        analyze_btn = msg.addButton("Анализировать", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Ok)
        msg.exec()
        
        if msg.clickedButton() == analyze_btn:
            dialog = AnalysisDialog(decision_id, self)
            dialog.exec()
    
    def show_history(self):
        self.set_active_button(self.pushButton_3)
        self.clear_content_area()
        
        history_widget = self.load_ui_widget('history_page.ui')
        if history_widget:
            self.widget_2.layout().addWidget(history_widget)
    
    def show_favorites(self):
        self.set_active_button(self.pushButton_4)
        self.clear_content_area()
        
        favorites_widget = self.load_ui_widget('favorites_page.ui')
        if favorites_widget:
            self.widget_2.layout().addWidget(favorites_widget)
    
    def show_help(self):
        self.set_active_button(self.pushButton_5)
        QMessageBox.information(self, "Помощь", "Раздел помощи будет реализован позже")
    
    def show_settings(self):
        self.set_active_button(self.pushButton_6)
        QMessageBox.information(self, "Настройки", "Раздел настроек в разработке")
    
    def create_decision(self):
        try:
            from decision_wizard import DecisionWizard
            dialog = DecisionWizard(self)
            if dialog.exec():
                decision_data = dialog.get_decision_data()
                print(f"Создано решение: {decision_data['title']}")
        except Exception as e:
            print(f"Ошибка открытия окна создания: {e}")
    
    def set_active_button(self, active_button):
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