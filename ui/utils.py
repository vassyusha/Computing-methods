
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def clear_table(table_widget: QTableWidget):
    """
    Очищает содержимое QTableWidget.
    """
    table_widget.clearContents()
    for row in range(table_widget.rowCount()):
        for col in range(table_widget.columnCount()):
            table_widget.setItem(row, col, QTableWidgetItem(""))
