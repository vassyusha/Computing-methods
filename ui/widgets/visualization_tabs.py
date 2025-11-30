
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTableWidget, QGraphicsView, QGraphicsScene, QTableWidgetItem
)
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt

class VisualizationTabs(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "card") # Для стилизации как карточки
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10) # Внутренние отступы карточки
        
        self.tabs = QTabWidget()
        self.tabs.tabBar().setExpanding(True) # Вкладки растягиваются на всю ширину
        self.tabs.tabBar().setDocumentMode(True) # Убирает лишние рамки
        
        # --- Вкладка 1: Матрица (визуализация) ---
        self.tab_matrix = QWidget()
        self.tab_matrix_layout = QVBoxLayout(self.tab_matrix)
        self.vis_matrix_table = QTableWidget() # Используем таблицу для отображения шагов
        self.vis_matrix_table.horizontalHeader().setVisible(False)
        self.vis_matrix_table.verticalHeader().setVisible(False)
        self.tab_matrix_layout.addWidget(self.vis_matrix_table)
        self.tabs.addTab(self.tab_matrix, "Матрица (визуализация)")
        
        self.layout.addWidget(self.tabs)

    def resizeEvent(self, event):
        """
        Динамическое изменение размера шрифта вкладок при изменении ширины окна.
        """
        # Удалена логика уменьшения шрифта, чтобы соответствовать глобальному стилю
        super().resizeEvent(event)

    def update_matrix_visualization(self, state):
        """
        Обновляет таблицу визуализации на основе состояния алгоритма.
        """
        if not state:
            return

        matrix = state['matrix']
        stars = state['stars']
        primes = state['primes']
        row_covered = state['row_covered']
        col_covered = state['col_covered']
        
        n = matrix.shape[0]
        self.vis_matrix_table.setRowCount(n)
        self.vis_matrix_table.setColumnCount(n)
        
        # Настройка размера ячеек
        self.vis_matrix_table.horizontalHeader().setSectionResizeMode(1) # Stretch
        self.vis_matrix_table.verticalHeader().setSectionResizeMode(1)
        
        # Цвета
        color_covered = QColor("#45475A") # Темно-серый для покрытия
        color_double_covered = QColor("#313244") # Еще темнее для двойного покрытия
        color_star = QColor("#F9E2AF") # Желтый для звезд (Catppuccin Yellow)
        color_prime = QColor("#FFFFFF") # Белый для зачеркнутых нулей (рядом со звездами)
        color_text = QColor("#CDD6F4")
        color_text_highlight = QColor("#1E1E2E") # Темный текст на светлом фоне

        for r in range(n):
            for c in range(n):
                val = matrix[r, c]
                item = QTableWidgetItem(f"{val:.2f}")
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QBrush(color_text))
                
                # Фон ячейки
                bg_color = QColor("#181825") # Базовый фон
                
                is_covered = False
                if row_covered[r] and col_covered[c]:
                    bg_color = color_double_covered
                    is_covered = True
                elif row_covered[r] or col_covered[c]:
                    bg_color = color_covered
                    is_covered = True
                
                # Выделение звезд и штрихов
                if stars[r, c]:
                    # Звезды: Желтый текст, фон остается прежним (или покрытым)
                    item.setForeground(QBrush(color_star))
                    item.setText(f"{val:.2f} ★")
                elif primes[r, c]:
                    # Зачеркнутые нули: Белый текст
                    item.setForeground(QBrush(color_prime))
                    item.setText(f"{int(val)}")
                
                item.setBackground(QBrush(bg_color))
                self.vis_matrix_table.setItem(r, c, item)

