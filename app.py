import sys
from PyQt6.QtWidgets import QApplication
from welcome_window import WelcomeWindow
from main_window import MainWindow
from database import Database

def main():
    Database()
    
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