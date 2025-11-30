
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.utils import resource_path

def main():
    app = QApplication(sys.argv)
    
    # Загрузка стилей
    try:
        style_path = resource_path("ui/styles.qss")
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Файл стилей не найден, используется стандартная тема.")
        # Опционально: установка темной темы (если установлен qdarkstyle)
        try:
            import qdarkstyle
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        except ImportError:
            pass 

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
