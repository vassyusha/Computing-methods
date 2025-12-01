
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSpinBox, QLabel, 
    QGroupBox, QFormLayout, QProgressBar, QDoubleSpinBox, QCheckBox, QTabWidget,
    QComboBox, QStackedWidget, QTextEdit
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
        k = self.params['k']
        
        # New parameters
        mass = self.params['mass']
        sugar_min = self.params['sugar_min']
        sugar_max = self.params['sugar_max']
        deg_min = self.params['deg_min']
        deg_max = self.params['deg_max']
        
        # Initialize accumulators for cumulative sums
        results = {
            'HungarianMin': np.zeros(size),
            'HungarianMax': np.zeros(size),
            'Thrifty': np.zeros(size),
            'Greedy': np.zeros(size),
            'GreedyThrifty': np.zeros(size),
            'ThriftyGreedy': np.zeros(size),
            'ThriftyKeyGreedy': np.zeros(size)
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
                deg_max=deg_max
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
            _, values = comp.Greedy_ThriftyMethodX(transition)
            add_cum_sum('GreedyThrifty', values)

            # Thrifty -> Greedy
            _, values = comp.Thrifty_GreedyMethodX(transition)
            add_cum_sum('ThriftyGreedy', values)

            # Thrifty(k) -> Greedy
            _, values = comp.TkG_MethodX(k, transition)
            add_cum_sum('ThriftyKeyGreedy', values)

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
        self.settings_panel.setMinimumWidth(450) # Use minimum width instead of fixed
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

        self.spin_k = QSpinBox()
        self.spin_k.setRange(1, 100)
        self.spin_k.setValue(3)
        
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
        self.params_layout.addRow("Параметр k:", self.spin_k)
        self.params_layout.addRow("Суточная масса:", self.spin_mass)
        
        # Modified layout: Label on top, controls below
        self.params_layout.addRow(QLabel("Сахаристость:"))
        self.params_layout.addRow(self.sugar_layout)
        
        self.params_layout.addRow(QLabel("Деградация:"))
        self.params_layout.addRow(self.deg_layout)
        
        self.settings_layout.addWidget(self.params_group)
        
        self.btn_run = QPushButton("Запустить сравнение")
        self.btn_run.clicked.connect(self.run_comparison)
        self.btn_run.setFixedHeight(45) # Slightly taller
        self.settings_layout.addWidget(self.btn_run)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(45) # Same height as button
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.settings_layout.addWidget(self.progress_bar)
        
        self.settings_layout.addStretch()
        
        # --- Right Side (Visualization) ---
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)

        # View Selector
        self.view_selector = QComboBox()
        self.view_selector.addItems(["График", "Гистограмма", "Общие результаты"])
        self.view_selector.currentIndexChanged.connect(self.update_view)
        self.right_layout.addWidget(self.view_selector)

        # Stacked Widget for views
        self.stacked_widget = QStackedWidget()
        
        # 1. Graph View
        self.graph_widget = QWidget()
        self.graph_layout = QVBoxLayout(self.graph_widget)
        self.figure_graph = Figure(figsize=(5, 4), dpi=100)
        self.figure_graph.patch.set_facecolor('#1E1E2E')
        self.canvas_graph = FigureCanvas(self.figure_graph)
        self.graph_layout.addWidget(self.canvas_graph)
        self.ax_graph = self.figure_graph.add_subplot(111)
        self.stacked_widget.addWidget(self.graph_widget)

        # 2. Histogram View
        self.hist_widget = QWidget()
        self.hist_layout = QVBoxLayout(self.hist_widget)
        self.figure_hist = Figure(figsize=(5, 4), dpi=100)
        self.figure_hist.patch.set_facecolor('#1E1E2E')
        self.canvas_hist = FigureCanvas(self.figure_hist)
        self.hist_layout.addWidget(self.canvas_hist)
        self.ax_hist = self.figure_hist.add_subplot(111)
        self.stacked_widget.addWidget(self.hist_widget)

        # 3. General Results View
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("font-size: 18px; color: #CDD6F4; background-color: #1E1E2E; border: 1px solid #45475A; padding: 10px;")
        self.stacked_widget.addWidget(self.results_text)

        self.right_layout.addWidget(self.stacked_widget)
        
        self.layout.addWidget(self.settings_panel)
        self.layout.addWidget(self.right_panel)

        self.style_plot(self.ax_graph)
        self.style_plot(self.ax_hist)
        
        self.current_results = None

    def style_plot(self, ax):
        ax.set_facecolor('#1E1E2E')
        ax.tick_params(colors='#CDD6F4')
        ax.xaxis.label.set_color('#CDD6F4')
        ax.yaxis.label.set_color('#CDD6F4')
        ax.title.set_color('#CDD6F4')
        for spine in ax.spines.values():
            spine.set_edgecolor('#45475A')
        ax.grid(True, color='#45475A', linestyle='--')

    def run_comparison(self):
        params = {
            'size': self.spin_size.value(),
            'experiments': self.spin_experiments.value(),
            'transition': self.spin_transition.value(),
            'k': self.spin_k.value(),
            'mass': self.spin_mass.value(),
            'sugar_min': self.spin_sugar_min.value(),
            'sugar_max': self.spin_sugar_max.value(),
            'deg_min': self.spin_deg_min.value(),
            'deg_max': self.spin_deg_max.value()
        }
        
        self.btn_run.setVisible(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.worker = Worker(params)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, results):
        self.btn_run.setVisible(True)
        self.progress_bar.setVisible(False)
        self.current_results = results
        self.update_view()

    def update_view(self):
        if self.current_results is None:
            return
            
        index = self.view_selector.currentIndex()
        self.stacked_widget.setCurrentIndex(index)
        
        if index == 0:
            self.plot_graph(self.current_results)
        elif index == 1:
            self.plot_histogram(self.current_results)
        elif index == 2:
            self.show_general_results(self.current_results)

    def plot_graph(self, results):
        self.ax_graph.clear()
        self.style_plot(self.ax_graph)
        
        x = np.arange(len(results['HungarianMin']))
        
        # Plotting with Catppuccin colors
        self.ax_graph.plot(x, results['HungarianMax'], label='Венгерский (Макс)', color='#A6E3A1', linestyle='--')
        self.ax_graph.plot(x, results['HungarianMin'], label='Венгерский (Мин)', color='#F38BA8', linestyle='-.')
        self.ax_graph.plot(x, results['Greedy'], label='Жадная', color='#F9E2AF', linestyle=':')
        self.ax_graph.plot(x, results['Thrifty'], label='Бережливая', color='#89B4FA')
        self.ax_graph.plot(x, results['GreedyThrifty'], label='Жадн/Береж', color='#CBA6F7', linestyle='--')
        self.ax_graph.plot(x, results['ThriftyGreedy'], label='Береж/Жадн', color='#FAB387', linestyle='-.')
        self.ax_graph.plot(x, results['ThriftyKeyGreedy'], label='Береж(k)/Жадн', color='#94E2D5', linestyle='-')
        
        self.ax_graph.set_title("Средние значения алгоритмов на каждом этапе")
        self.ax_graph.set_xlabel("Этап (столбец)")
        self.ax_graph.set_ylabel("Накопленная стоимость")
        
        legend = self.ax_graph.legend()
        plt.setp(legend.get_texts(), color='#CDD6F4')
        legend.get_frame().set_facecolor('#313244')
        legend.get_frame().set_edgecolor('#45475A')
        
        self.canvas_graph.draw()

    def plot_histogram(self, results):
        self.ax_hist.clear()
        self.style_plot(self.ax_hist)
        
        labels = ['Венг. (Макс)', 'Венг. (Мин)', 'Жадная', 'Бережливая', 'Жадн/Береж', 'Береж/Жадн', 'Береж(k)/Жадн']
        final_values = [
            results['HungarianMax'][-1],
            results['HungarianMin'][-1],
            results['Greedy'][-1],
            results['Thrifty'][-1],
            results['GreedyThrifty'][-1],
            results['ThriftyGreedy'][-1],
            results['ThriftyKeyGreedy'][-1]
        ]
        
        colors = ['#A6E3A1', '#F38BA8', '#F9E2AF', '#89B4FA', '#CBA6F7', '#FAB387', '#94E2D5']
        
        bars = self.ax_hist.bar(labels, final_values, color=colors)
        
        self.ax_hist.set_title("Итоговые значения алгоритмов")
        self.ax_hist.set_ylabel("Итоговая стоимость")
        
        # Rotate labels for better visibility
        self.ax_hist.set_xticklabels(labels, rotation=45, ha='right')
        
        self.canvas_hist.draw()

    def show_general_results(self, results):
        mass = self.spin_mass.value()
        
        final_values = {
            'Венгерский (Максимум)': results['HungarianMax'][-1] * mass,
            'Венгерский (Минимум)': results['HungarianMin'][-1] * mass,
            'Жадная стратегия': results['Greedy'][-1] * mass,
            'Бережливая стратегия': results['Thrifty'][-1] * mass,
            'Жадная -> Бережливая': results['GreedyThrifty'][-1] * mass,
            'Бережливая -> Жадная': results['ThriftyGreedy'][-1] * mass,
            'Бережливая(k) -> Жадная': results['ThriftyKeyGreedy'][-1] * mass
        }
        
        # Exclude Hungarian Max from best strategy calculation
        heuristic_values = final_values.copy()
        if 'Венгерский (Максимум)' in heuristic_values:
            del heuristic_values['Венгерский (Максимум)']
            
        best_strategy = max(heuristic_values, key=heuristic_values.get)
        best_value = heuristic_values[best_strategy]
        
        text = f"""
        <h2 style="color: #cba6f7">Общие результаты экспериментов</h2>
        <p>Согласно проделанным экспериментам можно сделать следующие выводы:</p>
        <ul>
        """
        
        for strategy, value in final_values.items():
            text += f"<li><b>{strategy}:</b> {value:.2f}</li>"
            
        text += f"""
        </ul>
        <p>Наилучший результат виртуального эксперимента — <b style="color: #a6e3a1">{best_strategy}</b> ({best_value:.2f}).</p>
        <p>Согласно генеральному эксперименту в следующем сезоне предлагается применить <b style="color: #a6e3a1">{best_strategy}</b>.</p>
        """
        
        self.results_text.setHtml(text)
