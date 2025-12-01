
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QSpinBox, QLabel, QRadioButton, QButtonGroup, QHeaderView, QFileDialog, QGroupBox
)
from PyQt5.QtCore import Qt
import numpy as np
import MatrixGenerator
from ui.utils import clear_table
import qtawesome as qta

class MatrixEditorPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "card") # Для стилизации как карточки
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20) # Внутренние отступы карточки
        
        # --- Группа настроек ---
        self.settings_group = QGroupBox("Настройки матрицы")
        self.settings_layout = QVBoxLayout(self.settings_group)
        
        # Размер и режим
        self.top_controls = QHBoxLayout()
        
        self.size_label = QLabel("Размер (n):")
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(2, 1000)
        self.size_spinbox.setValue(5)
        self.size_spinbox.valueChanged.connect(self.update_table_size)
        
        self.top_controls.addWidget(self.size_label)
        self.top_controls.addWidget(self.size_spinbox)
        self.top_controls.addStretch()
        
        # Переключатель Мин/Макс
        self.radio_min = QRadioButton("Минимизация")
        self.radio_max = QRadioButton("Максимизация")
        self.radio_min.setChecked(True)
        
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.radio_min)
        self.mode_group.addButton(self.radio_max)
        
        self.top_controls.addWidget(self.radio_min)
        self.top_controls.addWidget(self.radio_max)
        
        self.settings_layout.addLayout(self.top_controls)
        
        # Кнопки действий
        self.actions_layout = QHBoxLayout()
        
        self.btn_random = QPushButton(" Случайно")
        self.btn_random.setIcon(qta.icon('fa5s.dice'))
        self.btn_random.clicked.connect(self.fill_random)
        
        self.btn_clear = QPushButton(" Очистить")
        self.btn_clear.setIcon(qta.icon('fa5s.eraser'))
        self.btn_clear.clicked.connect(lambda: clear_table(self.table))
        
        self.btn_load = QPushButton(" Загрузить")
        self.btn_load.setIcon(qta.icon('fa5s.folder-open'))
        self.btn_load.clicked.connect(self.load_matrix)
        
        self.btn_save = QPushButton(" Сохранить")
        self.btn_save.setIcon(qta.icon('fa5s.save'))
        self.btn_save.clicked.connect(self.save_matrix)

        self.actions_layout.addWidget(self.btn_random)
        self.actions_layout.addWidget(self.btn_clear)
        self.actions_layout.addWidget(self.btn_load)
        self.actions_layout.addWidget(self.btn_save)
        
        self.settings_layout.addLayout(self.actions_layout)
        
        self.layout.addWidget(self.settings_group)

        # --- Таблица (Матрица) ---
        self.table = QTableWidget()
        self.update_table_size()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setVisible(False) # Скрываем заголовки
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(300) # Минимальная высота для матрицы
        self.layout.addWidget(self.table)

    def update_table_size(self):
        n = self.size_spinbox.value()
        self.table.setRowCount(n)
        self.table.setColumnCount(n)
        
        # Динамическая настройка шрифта и размера ячеек
        # Чем больше n, тем меньше шрифт
        font_size = max(8, 14 - int(n * 0.35))
        font = self.table.font()
        font.setPointSize(font_size)
        self.table.setFont(font)
        
        # Уменьшаем минимальный размер секций, чтобы они могли сжиматься
        self.table.horizontalHeader().setMinimumSectionSize(10)
        self.table.verticalHeader().setMinimumSectionSize(10)
        
        # Отключаем полосы прокрутки, так как режим Stretch должен уместить всё
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def fill_random(self):
        n = self.size_spinbox.value()
        # Используем MatrixGenerator с параметрами по умолчанию, но n=n и v=n (квадратная матрица для редактора)
        
        generator = MatrixGenerator.MatrixGenerator(n=n, v=n)
        matrix = generator.GenerateCMatrix()
        
        for i in range(n):
            for j in range(n):
                item = QTableWidgetItem(f"{matrix[i, j]:.2f}")
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)

    def get_matrix(self):
        n = self.table.rowCount()
        matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                item = self.table.item(i, j)
                if item:
                    try:
                        matrix[i, j] = float(item.text())
                    except ValueError:
                        matrix[i, j] = 0.0
                else:
                    matrix[i, j] = 0.0
        return matrix

    def load_matrix(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Загрузить матрицу", "", "Text Files (*.txt);;All Files (*)", options=options)
        if fileName:
            try:
                matrix = np.loadtxt(fileName, dtype=float)
                if len(matrix.shape) == 2 and matrix.shape[0] == matrix.shape[1]:
                    n = matrix.shape[0]
                    self.size_spinbox.setValue(n)
                    for i in range(n):
                        for j in range(n):
                            item = QTableWidgetItem(f"{matrix[i, j]:.2f}")
                            item.setTextAlignment(Qt.AlignCenter)
                            self.table.setItem(i, j, item)
            except Exception as e:
                print(f"Ошибка загрузки: {e}")

    def save_matrix(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Сохранить матрицу", "", "Text Files (*.txt);;All Files (*)", options=options)
        if fileName:
            matrix = self.get_matrix()
            np.savetxt(fileName, matrix, fmt='%.2f')
