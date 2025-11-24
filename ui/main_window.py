
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget
from PyQt5.QtCore import Qt, QTimer
from ui.widgets.matrix_editor import MatrixEditorPanel
from ui.widgets.control_panel import ControlPanel
from ui.widgets.visualization_tabs import VisualizationTabs
from ui.widgets.comparison_panel import ComparisonPanel
import Computing
from HungarianAlgorithm import HungarianAlgorithm

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализация Венгерского алгоритма")
        self.resize(1200, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный макет (теперь с вкладками)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # --- Вкладка 1: Визуализация (Старый интерфейс) ---
        self.tab_visualization = QWidget()
        vis_layout = QHBoxLayout(self.tab_visualization)
        vis_layout.setContentsMargins(24, 24, 24, 24)
        vis_layout.setSpacing(24)
        
        # Левая панель (Ввод + Управление)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6) 
        
        self.matrix_editor = MatrixEditorPanel()
        self.control_panel = ControlPanel()
        
        left_layout.addWidget(self.matrix_editor, stretch=2)
        left_layout.addWidget(self.control_panel, stretch=3)
        
        # Правая панель (Визуализация)
        self.visualization_tabs = VisualizationTabs()
        
        # Разделитель
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(self.visualization_tabs)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)
        splitter.setHandleWidth(0)
        
        vis_layout.addWidget(splitter)
        
        self.tabs.addTab(self.tab_visualization, "Визуализация")
        
        # --- Вкладка 2: Сравнение алгоритмов ---
        self.comparison_panel = ComparisonPanel()
        self.tabs.addTab(self.comparison_panel, "Сравнение алгоритмов")

        # Подключение сигналов
        self.control_panel.btn_solution.clicked.connect(self.show_solution)
        self.control_panel.btn_start.clicked.connect(self.start_algorithm)
        self.control_panel.btn_next.clicked.connect(self.next_step)
        self.control_panel.btn_back.clicked.connect(self.prev_step)
        self.control_panel.btn_auto.clicked.connect(self.toggle_auto)
        
        # Таймер для автоматического режима
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.next_step)
        
        self.algorithm = None

    def start_algorithm(self):
        matrix = self.matrix_editor.get_matrix()
        mode = 'min' if self.matrix_editor.radio_min.isChecked() else 'max'
        
        self.algorithm = HungarianAlgorithm(matrix, mode)
        self.control_panel.log("<b>Алгоритм запущен.</b>", "#89B4FA")
        self.update_ui_from_state()

    def next_step(self):
        if self.algorithm:
            state = self.algorithm.next()
            if state:
                self.update_ui_from_state()
            else:
                if self.algorithm.is_finished():
                    self.control_panel.log("Алгоритм завершен.", "#A6E3A1")
                    self.auto_timer.stop()
                    self.control_panel.btn_auto.setText(" Авто")

    def prev_step(self):
        if self.algorithm:
            state = self.algorithm.prev()
            if state:
                self.update_ui_from_state()

    def toggle_auto(self):
        if self.auto_timer.isActive():
            self.auto_timer.stop()
            self.control_panel.btn_auto.setText(" Авто")
        else:
            # Скорость зависит от слайдера: 100 (быстро) -> 50ms, 1 (медленно) -> 2000ms
            speed_val = self.control_panel.speed_slider.value()
            interval = int(2000 - (speed_val * 19.5))
            self.auto_timer.start(max(50, interval))
            self.control_panel.btn_auto.setText(" Стоп")

    def update_ui_from_state(self):
        if not self.algorithm:
            return
            
        state = self.algorithm.get_current_state()
        if state:
            self.control_panel.log(state['description'])
            self.visualization_tabs.update_matrix_visualization(state)

    def show_solution(self):
        """
        Демонстрация использования существующего функционала из Computing.py
        """
        try:
            matrix = self.matrix_editor.get_matrix()
            comp = Computing.Computing(matrix)
            
            if self.matrix_editor.radio_min.isChecked():
                cost, _ = comp.HungarianMinimum()
                mode = "Минимизация"
            else:
                cost, _ = comp.HungarianMaximum()
                mode = "Максимизация"
                
            self.control_panel.log(f"Режим: {mode}")
            self.control_panel.log(f"Оптимальная стоимость (через Computing.py): {cost}", "#A6E3A1")
            
        except Exception as e:
            self.control_panel.log(f"Ошибка при вычислении: {e}", "#F38BA8")
