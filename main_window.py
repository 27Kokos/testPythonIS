from PyQt6.QtWidgets import QMainWindow, QMessageBox, QListWidgetItem, QWidget
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
            self.setWindowTitle("DecidePro - Главное меню")
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
            if hasattr(home_widget, 'statsLabel'):
                decisions_count = len(self.db.get_decisions())
                analyses_count = sum(1 for dec in self.db.get_decisions() if self.db.get_analysis_results(dec[0]))
                home_widget.statsLabel.setText(f"Быстрая статистика:\n• Всего решений: {decisions_count}\n• Завершенных анализов: {analyses_count}\n• Активных проектов: 0")
            
            self.widget_2.layout().addWidget(home_widget)
    
    def show_my_decisions(self):
        self.set_active_button(self.pushButton_2)
        self.clear_content_area()
        
        decisions_widget = self.load_ui_widget('decisions_page.ui')
        if decisions_widget:
            decisions = self.db.get_decisions()
            
            if hasattr(decisions_widget, 'decisionsList'):
                decisions_list = decisions_widget.decisionsList
                decisions_list.clear()
                for dec in decisions:
                    item = QListWidgetItem()
                    item.setData(Qt.ItemDataRole.UserRole, dec[0])
                    card_widget = self.load_ui_widget('decision_card.ui')
                    if card_widget:
                        card_widget.titleLabel.setText(dec[1])
                        card_widget.favoriteButton.setText("Удалить из избранного" if self.db.is_favorite(dec[0]) else "Добавить в избранное")
                        card_widget.viewButton.clicked.connect(lambda checked, d_id=dec[0]: self.open_decision_by_id(d_id))
                        card_widget.favoriteButton.clicked.connect(lambda checked, d_id=dec[0], btn=card_widget.favoriteButton: self.toggle_favorite(d_id, btn))
                        card_widget.deleteButton.clicked.connect(lambda checked, d_id=dec[0]: self.delete_decision(d_id))
                        decisions_list.addItem(item)
                        decisions_list.setItemWidget(item, card_widget)
                        item.setSizeHint(card_widget.sizeHint())
                
                decisions_list.itemDoubleClicked.connect(self.open_decision)
            
            self.widget_2.layout().addWidget(decisions_widget)

    def delete_decision(self, decision_id):
        reply = QMessageBox.question(self, "Удаление", "Удалить это решение?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_decision(decision_id):
                QMessageBox.information(self, "Успех", "Решение удалено")
                self.show_my_decisions()  # Обновить страницу
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить решение")
    
    def toggle_favorite(self, decision_id, button):
        if self.db.is_favorite(decision_id):
            if self.db.remove_from_favorites(decision_id):
                button.setText("Добавить в избранное")
                QMessageBox.information(self, "Успех", "Удалено из избранного")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить из избранного")
        else:
            if self.db.add_to_favorites(decision_id):
                button.setText("Удалить из избранного")
                QMessageBox.information(self, "Успех", "Добавлено в избранное")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить в избранное")
    
    def open_decision(self, item):
        decision_id = item.data(Qt.ItemDataRole.UserRole)
        self.open_decision_by_id(decision_id)
    
    def open_decision_by_id(self, decision_id):
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
        favorite_btn_text = "Удалить из избранного" if self.db.is_favorite(decision_id) else "Добавить в избранное"
        favorite_btn = msg.addButton(favorite_btn_text, QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Ok)
        msg.exec()
        
        if msg.clickedButton() == analyze_btn:
            dialog = AnalysisDialog(decision_id, self)
            dialog.exec()
        elif msg.clickedButton() == favorite_btn:
            if self.db.is_favorite(decision_id):
                if self.db.remove_from_favorites(decision_id):
                    QMessageBox.information(self, "Успех", "Удалено из избранного")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить из избранного")
            else:
                if self.db.add_to_favorites(decision_id):
                    QMessageBox.information(self, "Успех", "Добавлено в избранное")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось добавить в избранное")
    
    def show_favorites(self):
        self.set_active_button(self.pushButton_4)
        self.clear_content_area()
        
        favorites_widget = self.load_ui_widget('favorites_page.ui')
        if favorites_widget:
            favorites = self.db.get_favorites()
            
            if hasattr(favorites_widget, 'favoritesList'):
                favorites_list = favorites_widget.favoritesList
                favorites_list.clear()
                for fav in favorites:
                    item = QListWidgetItem()
                    item.setData(Qt.ItemDataRole.UserRole, fav[0])
                    card_widget = self.load_ui_widget('decision_card.ui')
                    if card_widget:
                        card_widget.titleLabel.setText(fav[1])
                        card_widget.favoriteButton.setText("Удалить из избранного" if self.db.is_favorite(fav[0]) else "Добавить в избранное")
                        card_widget.viewButton.clicked.connect(lambda checked, d_id=fav[0]: self.open_decision_by_id(d_id))
                        card_widget.favoriteButton.clicked.connect(lambda checked, d_id=fav[0], btn=card_widget.favoriteButton: self.toggle_favorite(d_id, btn))
                        card_widget.deleteButton.clicked.connect(lambda checked, d_id=fav[0]: self.delete_decision(d_id))
                        favorites_list.addItem(item)
                        favorites_list.setItemWidget(item, card_widget)
                        item.setSizeHint(card_widget.sizeHint())
                
                favorites_list.itemDoubleClicked.connect(self.open_decision)
            
            if hasattr(favorites_widget, 'refreshButton'):
                favorites_widget.refreshButton.clicked.connect(self.show_favorites)
            
            self.widget_2.layout().addWidget(favorites_widget)
    
    def show_help(self):
        self.set_active_button(self.pushButton_5)
        QMessageBox.information(self, "Помощь", "Раздел помощи будет реализован позже")
    
    def show_settings(self):
        self.set_active_button(self.pushButton_6)
        self.clear_content_area()
        
        settings_widget = self.load_ui_widget('settings_page.ui')
        if settings_widget:
            # Подключение действий для языка
            if hasattr(settings_widget, 'languageCombo'):
                settings_widget.languageCombo.currentTextChanged.connect(self.change_language)
                settings_widget.languageCombo.setCurrentText("Русский")  # Установка по умолчанию
            
            # Подключение действий для очистки данных
            if hasattr(settings_widget, 'clearDataButton'):
                settings_widget.clearDataButton.clicked.connect(self.clear_all_data)
            
            self.widget_2.layout().addWidget(settings_widget)
    
    def change_language(self, language):
        # Поскольку только русский, просто уведомление
        QMessageBox.information(self, "Язык", "Выбран язык: Русский. Другие языки будут добавлены в будущих обновлениях.")
    
    def clear_all_data(self):
        reply = QMessageBox.question(self, "Очистка данных", "Вы уверены, что хотите удалить все решения и анализы? Это действие нельзя отменить!",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.clear_all_data()  # Вызов метода очистки БД
                QMessageBox.information(self, "Успех", "Все данные успешно удалены. Приложение обновлено.")
                self.show_my_decisions()  # Обновляем страницу "Мои решения" для отражения изменений
            except Exception as e:
                print(f"Ошибка очистки: {e}")
                QMessageBox.warning(self, "Ошибка", "Не удалось очистить данные. Проверьте подключение к базе данных.")
    
    def create_decision(self):
        try:
            from decision_wizard import DecisionWizard
            dialog = DecisionWizard(self)
            if dialog.exec():
                decision_data = dialog.get_decision_data()
                print(f"Создано решение: {decision_data['title']}")
                self.show_my_decisions()
        except Exception as e:
            print(f"Ошибка открытия окна создания: {e}")
    
    def set_active_button(self, active_button):
        buttons = [self.pushButton, self.pushButton_2, self.pushButton_4, 
                   self.pushButton_5, self.pushButton_6]
        
        for btn in buttons:
            if btn:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgb(255, 255, 255);
                        padding: 10px;
                        font-size: 14px;
                        border: none;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: rgb(214, 225, 229);
                    }
                """)
        
        if active_button:
            active_button.setStyleSheet("""
                QPushButton {
                    background-color: rgb(200, 230, 240);
                    padding: 10px;
                    font-size: 14px;
                    border: none;
                    text-align: left;
                }
            """)
    
    def create_decision(self):
        try:
            from decision_wizard import DecisionWizard
            dialog = DecisionWizard(self)
            if dialog.exec():
                decision_data = dialog.get_decision_data()
                print(f"Создано решение: {decision_data['title']}")
                self.show_my_decisions()
        except Exception as e:
            print(f"Ошибка открытия окна создания: {e}")
    
    def set_active_button(self, active_button):
        buttons = [self.pushButton, self.pushButton_2, self.pushButton_4, 
                   self.pushButton_5, self.pushButton_6]
        
        for btn in buttons:
            if btn:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgb(255, 255, 255);
                        padding: 10px;
                        font-size: 14px;
                        border: none;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: rgb(214, 225, 229);
                    }
                """)
        
        if active_button:
            active_button.setStyleSheet("""
                QPushButton {
                    background-color: rgb(200, 230, 240);
                    padding: 10px;
                    font-size: 14px;
                    border: none;
                    text-align: left;
                }
            """)
    
    def create_decision(self):
        try:
            from decision_wizard import DecisionWizard
            dialog = DecisionWizard(self)
            if dialog.exec():
                decision_data = dialog.get_decision_data()
                print(f"Создано решение: {decision_data['title']}")
                self.show_my_decisions()
        except Exception as e:
            print(f"Ошибка открытия окна создания: {e}")
    
    def set_active_button(self, active_button):
        buttons = [self.pushButton, self.pushButton_2, self.pushButton_4, 
                   self.pushButton_5, self.pushButton_6]
        
        for btn in buttons:
            if btn:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgb(255, 255, 255);
                        padding: 10px;
                        font-size: 14px;
                        border: none;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: rgb(214, 225, 229);
                    }
                """)
        
        if active_button:
            active_button.setStyleSheet("""
                QPushButton {
                    background-color: rgb(200, 230, 240);
                    padding: 10px;
                    font-size: 14px;
                    border: none;
                    text-align: left;
                }
            """)
    
    def create_decision(self):
        try:
            from decision_wizard import DecisionWizard
            dialog = DecisionWizard(self)
            if dialog.exec():
                decision_data = dialog.get_decision_data()
                print(f"Создано решение: {decision_data['title']}")
                self.show_my_decisions()  # Обновить список решений
        except Exception as e:
            print(f"Ошибка открытия окна создания: {e}")
    
    def set_active_button(self, active_button):
        buttons = [self.pushButton, self.pushButton_2, self.pushButton_4, 
                   self.pushButton_5, self.pushButton_6]
        
        for btn in buttons:
            if btn:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgb(255, 255, 255);
                        padding: 10px;
                        font-size: 14px;
                        border: none;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: rgb(214, 225, 229);
                    }
                """)
        
        if active_button:
            active_button.setStyleSheet("""
                QPushButton {
                    background-color: rgb(200, 230, 240);
                    padding: 10px;
                    font-size: 14px;
                    border: none;
                    text-align: left;
                }
            """)