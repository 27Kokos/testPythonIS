from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic
from PyQt6.QtGui import QIcon 
import os
import sys

class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_accepted = False
        self.load_ui()
        self.setup_window()
        self.connect_signals()
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'images', 'logo.ico')))

    def load_ui(self):
        try:
            ui_path = os.path.join(os.path.dirname(__file__), 'ui', 'welcome_window.ui')
            uic.loadUi(ui_path, self)
        except Exception as e:
            print(f"Ошибка загрузки UI Welcome окна: {e}")
            sys.exit(1)
    
    def setup_window(self):
        self.setFixedSize(311, 320)
        self.setWindowTitle("DecidePro")
        
    def connect_signals(self):
        if hasattr(self, 'start_btn'):
            self.start_btn.clicked.connect(self.on_start_clicked)
        else:
            print("Кнопка start_btn не найдена!")
            print("Доступные атрибуты:", [attr for attr in dir(self) if not attr.startswith('_')])
            
    def on_start_clicked(self):
        self.user_accepted = True
        self.close()
        
    def closeEvent(self, event):
        if not self.user_accepted:
            sys.exit(0)
        event.accept()