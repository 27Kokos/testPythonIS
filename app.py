import sys
import os
from PyQt6.QtWidgets import QApplication
from welcome_window import WelcomeWindow
from main_window import MainWindow 

def main():
    # Инициализация БД при запуске приложения
    from database import Database
    db = Database()  # Это создаст таблицы если их нет
    
    app = QApplication(sys.argv)
    
    welcome = WelcomeWindow()
    welcome.show()
    app.exec()
    
    if hasattr(welcome, 'user_accepted') and welcome.user_accepted:
        main_window = MainWindow()
        main_window.show()
        app.exec()
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()