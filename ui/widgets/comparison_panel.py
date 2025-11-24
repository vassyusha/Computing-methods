
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSpinBox, QLabel, 
    QGroupBox, QFormLayout, QProgressBar, QDoubleSpinBox, QCheckBox, QTabWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import Computing
import MatrixGenerator

class Worker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        size = self.params['size']
        experiments = self.params['experiments']
        transition = self.params['transition']
        
        # New parameters
        mass = self.params['mass']
        sugar_min = self.params['sugar_min']
        sugar_max = self.params['sugar_max']
        deg_min = self.params['deg_min']
        deg_max = self.params['deg_max']
        
        use_condition = self.params['use_condition']
        condition_type = self.params['condition_type']
        cond_transition = self.params['cond_transition']
        cond_min = self.params['cond_min']
        cond_max = self.params['cond_max']

        # Initialize accumulators for cumulative sums
        results = {
            'HungarianMin': np.zeros(size),
            'HungarianMax': np.zeros(size),
            'Thrifty': np.zeros(size),
            'Greedy': np.zeros(size),
            'GreedyThrifty': np.zeros(size),
            'ThriftyGreedy': np.zeros(size)
        }

        generator = MatrixGenerator.MatrixGenerator(None)

        for i in range(experiments):
            # Use the new scenario generator
            matrix = generator.GenerateScenarioMatrix(
                size=size,
                mass=mass,
                sugar_min=sugar_min,
                sugar_max=sugar_max,
                deg_min=deg_min,
                deg_max=deg_max,
                use_condition=use_condition,
                condition_type=condition_type,
                transition=cond_transition,
                cond_min=cond_min,
                cond_max=cond_max
            )
            
            comp = Computing.Computing(matrix)

            # Helper to add cumulative sum
            def add_cum_sum(key, values):
                results[key] += np.cumsum(values)

            # Hungarian Min
            _, values = comp.HungarianMinimum()
            add_cum_sum('HungarianMin', values)

            # Hungarian Max
            _, values = comp.HungarianMaximum()
            add_cum_sum('HungarianMax', values)

            # Thrifty
            _, values = comp.ThriftyMethod()
            add_cum_sum('Thrifty', values)

            # Greedy
            _, values = comp.GreedyMethod()
            add_cum_sum('Greedy', values)

            # Greedy -> Thrifty
            _, values = comp.Greedy_ThreftyMetodX(transition)
            add_cum_sum('GreedyThrifty', values)

            # Thrifty -> Greedy
            _, values = comp.Threfty_GreedyMetodX(transition)
            add_cum_sum('ThriftyGreedy', values)

            self.progress.emit(int((i + 1) / experiments * 100))

        # Average out
        for key in results:
            results[key] /= experiments

        self.finished.emit(results)

class ComparisonPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        
        # --- Settings Panel ---
        self.settings_panel = QWidget()
        self.settings_panel.setObjectName("comparisonSettingsPanel") # For specific styling
        self.settings_panel.setFixedWidth(400) # Increased width further
        self.settings_layout = QVBoxLayout(self.settings_panel)
        
        # GroupBox for Main Parameters
        self.params_group = QGroupBox("Основные параметры")
        self.params_layout = QFormLayout(self.params_group)
        
        self.spin_size = QSpinBox()
        self.spin_size.setRange(2, 100)
        self.spin_size.setValue(15)
        
        self.spin_experiments = QSpinBox()
        self.spin_experiments.setRange(1, 10000)
        self.spin_experiments.setValue(100)
        
        self.spin_transition = QSpinBox()
        self.spin_transition.setRange(1, 100)
        self.spin_transition.setValue(7)
        
        self.spin_mass = QSpinBox()
        self.spin_mass.setRange(1, 100000)
        self.spin_mass.setValue(3000)
        
        # Sugar Range
        self.sugar_layout = QHBoxLayout()
        self.spin_sugar_min = QDoubleSpinBox()
        self.spin_sugar_min.setRange(0, 1)
        self.spin_sugar_min.setSingleStep(0.01)
        self.spin_sugar_min.setValue(0.16)
        
        self.spin_sugar_max = QDoubleSpinBox()
        self.spin_sugar_max.setRange(0, 1)
        self.spin_sugar_max.setSingleStep(0.01)
        self.spin_sugar_max.setValue(0.20)
        
        self.sugar_layout.addWidget(QLabel("Min:"))
        self.sugar_layout.addWidget(self.spin_sugar_min)
        self.sugar_layout.addWidget(QLabel("Max:"))
        self.sugar_layout.addWidget(self.spin_sugar_max)
        
        # Degradation Range
        self.deg_layout = QHBoxLayout()
        self.spin_deg_min = QDoubleSpinBox()
        self.spin_deg_min.setRange(0, 2)
        self.spin_deg_min.setSingleStep(0.01)
        self.spin_deg_min.setValue(0.93)
        
        self.spin_deg_max = QDoubleSpinBox()
        self.spin_deg_max.setRange(0, 2)
        self.spin_deg_max.setSingleStep(0.01)
        self.spin_deg_max.setValue(0.98)
        
        self.deg_layout.addWidget(QLabel("Min:"))
        self.deg_layout.addWidget(self.spin_deg_min)
        self.deg_layout.addWidget(QLabel("Max:"))
        self.deg_layout.addWidget(self.spin_deg_max)
        
        self.params_layout.addRow("Кол-во партий:", self.spin_size)
        self.params_layout.addRow("Эксперименты:", self.spin_experiments)
        self.params_layout.addRow("Этап смены стратегии:", self.spin_transition)
        self.params_layout.addRow("Суточная масса:", self.spin_mass)
        
        # Modified layout: Label on top, controls below
        self.params_layout.addRow(QLabel("Сахаристость:"))
        self.params_layout.addRow(self.sugar_layout)
        
        self.params_layout.addRow(QLabel("Деградация:"))
        self.params_layout.addRow(self.deg_layout)
        
        self.settings_layout.addWidget(self.params_group)
        
        # GroupBox for Additional Conditions
        self.cond_group = QGroupBox("Дополнительные условия")
        self.cond_layout = QVBoxLayout(self.cond_group)
        
        self.check_condition = QCheckBox("Учитывать доп. условие")
        self.check_condition.setObjectName("chk_condition") # For styling
        self.check_condition.setCursor(Qt.PointingHandCursor)
        self.cond_layout.addWidget(self.check_condition)
        
        self.cond_tabs = QTabWidget()
        self.cond_tabs.setEnabled(False)
        self.check_condition.toggled.connect(self.cond_tabs.setEnabled)
        
        # Tab 1: Inorganic
        self.tab_inorganic = QWidget()
        self.inorg_layout = QFormLayout(self.tab_inorganic)
        
        self.spin_inorg_trans = QSpinBox()
        self.spin_inorg_trans.setRange(1, 100)
        self.spin_inorg_trans.setValue(7)
        
        self.inorg_range_layout = QHBoxLayout()
        self.spin_inorg_min = QDoubleSpinBox()
        self.spin_inorg_min.setRange(0, 2)
        self.spin_inorg_min.setSingleStep(0.01)
        self.spin_inorg_min.setValue(0.95)
        
        self.spin_inorg_max = QDoubleSpinBox()
        self.spin_inorg_max.setRange(0, 2)
        self.spin_inorg_max.setSingleStep(0.01)
        self.spin_inorg_max.setValue(0.99)
        
        self.inorg_range_layout.addWidget(QLabel("Min:"))
        self.inorg_range_layout.addWidget(self.spin_inorg_min)
        self.inorg_range_layout.addWidget(QLabel("Max:"))
        self.inorg_range_layout.addWidget(self.spin_inorg_max)
        
        self.inorg_layout.addRow("Этап перехода:", self.spin_inorg_trans)
        self.inorg_layout.addRow(QLabel("Диапазон:"))
        self.inorg_layout.addRow(self.inorg_range_layout)
        
        self.cond_tabs.addTab(self.tab_inorganic, "Неорганика")
        
        # Tab 2: Ripening (Dosage)
        self.tab_ripening = QWidget()
        self.rip_layout = QFormLayout(self.tab_ripening)
        
        self.spin_rip_trans = QSpinBox()
        self.spin_rip_trans.setRange(1, 100)
        self.spin_rip_trans.setValue(7)
        
        self.rip_range_layout = QHBoxLayout()
        self.spin_rip_min = QDoubleSpinBox()
        self.spin_rip_min.setRange(0, 2)
        self.spin_rip_min.setSingleStep(0.01)
        self.spin_rip_min.setValue(1.01)
        
        self.spin_rip_max = QDoubleSpinBox()
        self.spin_rip_max.setRange(0, 2)
        self.spin_rip_max.setSingleStep(0.01)
        self.spin_rip_max.setValue(1.07)
        
        self.rip_range_layout.addWidget(QLabel("Min:"))
        self.rip_range_layout.addWidget(self.spin_rip_min)
        self.rip_range_layout.addWidget(QLabel("Max:"))
        self.rip_range_layout.addWidget(self.spin_rip_max)
        
        self.rip_layout.addRow("Этап перехода:", self.spin_rip_trans)
        self.rip_layout.addRow(QLabel("Диапазон:"))
        self.rip_layout.addRow(self.rip_range_layout)
        
        self.cond_tabs.addTab(self.tab_ripening, "Дозаривание")
        
        self.cond_layout.addWidget(self.cond_tabs)
        self.settings_layout.addWidget(self.cond_group)
        
        self.btn_run = QPushButton("Запустить сравнение")
        self.btn_run.clicked.connect(self.run_comparison)
        self.btn_run.setFixedHeight(40)
        self.settings_layout.addWidget(self.btn_run)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.settings_layout.addWidget(self.progress_bar)
        
        self.settings_layout.addStretch()
        
        # --- Plot Area ---
        self.plot_widget = QWidget()
        self.plot_layout = QVBoxLayout(self.plot_widget)
        
        self.figure = Figure(figsize=(5, 4), dpi=100)
        # Set figure background color to match theme (approx)
        self.figure.patch.set_facecolor('#1E1E2E')
        
        self.canvas = FigureCanvas(self.figure)
        self.plot_layout.addWidget(self.canvas)
        
        self.ax = self.figure.add_subplot(111)
        self.style_plot()
        
        self.layout.addWidget(self.settings_panel)
        self.layout.addWidget(self.plot_widget)

    def style_plot(self):
        self.ax.set_facecolor('#1E1E2E')
        self.ax.tick_params(colors='#CDD6F4')
        self.ax.xaxis.label.set_color('#CDD6F4')
        self.ax.yaxis.label.set_color('#CDD6F4')
        self.ax.title.set_color('#CDD6F4')
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#45475A')
        self.ax.grid(True, color='#45475A', linestyle='--')

    def run_comparison(self):
        # Determine active condition parameters
        use_cond = self.check_condition.isChecked()
        cond_type = 'inorganic' if self.cond_tabs.currentIndex() == 0 else 'ripening'
        
        if cond_type == 'inorganic':
            cond_trans = self.spin_inorg_trans.value()
            cond_min = self.spin_inorg_min.value()
            cond_max = self.spin_inorg_max.value()
        else:
            cond_trans = self.spin_rip_trans.value()
            cond_min = self.spin_rip_min.value()
            cond_max = self.spin_rip_max.value()

        params = {
            'size': self.spin_size.value(),
            'experiments': self.spin_experiments.value(),
            'transition': self.spin_transition.value(),
            'mass': self.spin_mass.value(),
            'sugar_min': self.spin_sugar_min.value(),
            'sugar_max': self.spin_sugar_max.value(),
            'deg_min': self.spin_deg_min.value(),
            'deg_max': self.spin_deg_max.value(),
            'use_condition': use_cond,
            'condition_type': cond_type,
            'cond_transition': cond_trans,
            'cond_min': cond_min,
            'cond_max': cond_max
        }
        
        self.btn_run.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.worker = Worker(params)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, results):
        self.btn_run.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.plot_results(results)

    def plot_results(self, results):
        self.ax.clear()
        self.style_plot()
        
        x = np.arange(len(results['HungarianMin']))
        
        # Plotting with Catppuccin colors
        self.ax.plot(x, results['HungarianMax'], label='Венгерский (Макс)', color='#A6E3A1', linestyle='--')
        self.ax.plot(x, results['HungarianMin'], label='Венгерский (Мин)', color='#F38BA8', linestyle='-.')
        self.ax.plot(x, results['Greedy'], label='Жадная', color='#F9E2AF', linestyle=':')
        self.ax.plot(x, results['Thrifty'], label='Бережливая', color='#89B4FA')
        self.ax.plot(x, results['GreedyThrifty'], label='Жадн/Береж', color='#CBA6F7', linestyle='--')
        self.ax.plot(x, results['ThriftyGreedy'], label='Береж/Жадн', color='#FAB387', linestyle='-.')
        
        self.ax.set_title("Средние значения алгоритмов на каждом этапе")
        self.ax.set_xlabel("Этап (столбец)")
        self.ax.set_ylabel("Накопленная стоимость")
        
        legend = self.ax.legend()
        plt.setp(legend.get_texts(), color='#CDD6F4')
        legend.get_frame().set_facecolor('#313244')
        legend.get_frame().set_edgecolor('#45475A')
        
        self.canvas.draw()
