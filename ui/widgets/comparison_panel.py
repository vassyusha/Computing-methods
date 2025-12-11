
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSpinBox, QLabel, 
    QGroupBox, QFormLayout, QProgressBar, QDoubleSpinBox, QCheckBox, QTabWidget,
    QComboBox, QStackedWidget, QTextEdit, QFileDialog, QMessageBox, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import random
import csv
import scipy.optimize
import Computing
import MatrixGenerator

class PlotNavigator:
    def __init__(self, canvas, ax):
        self.canvas = canvas
        self.ax = ax
        self.press = None
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('scroll_event', self.on_scroll)

    def on_press(self, event):
        if event.inaxes != self.ax: return
        if event.button == 1: # Left click
            self.press = (event.xdata, event.ydata)

    def on_release(self, event):
        self.press = None
        self.canvas.draw()

    def on_motion(self, event):
        if self.press is None: return
        if event.inaxes != self.ax: return
        
        x0, y0 = self.press
        x_curr, y_curr = event.xdata, event.ydata
        
        if x_curr is None or y_curr is None: return
        
        dx = x_curr - x0
        dy = y_curr - y0
        
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        self.ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
        self.ax.set_ylim(ylim[0] - dy, ylim[1] - dy)
        
        self.canvas.draw()

    def on_scroll(self, event):
        if event.inaxes != self.ax: return
        
        base_scale = 1.1
        if event.button == 'up':
            scale_factor = 1/base_scale
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            return
            
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        xdata = event.xdata
        ydata = event.ydata
        
        if xdata is None or ydata is None: return
        
        # New width and height
        w = xlim[1] - xlim[0]
        h = ylim[1] - ylim[0]
        new_w = w * scale_factor
        new_h = h * scale_factor
        
        # Relative position of mouse
        rel_x = (xdata - xlim[0]) / w
        rel_y = (ydata - ylim[0]) / h
        
        # New limits
        self.ax.set_xlim([xdata - new_w * rel_x, xdata + new_w * (1 - rel_x)])
        self.ax.set_ylim([ydata - new_h * rel_y, ydata + new_h * (1 - rel_y)])
        
        self.canvas.draw()

class Worker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        size = self.params['size']
        days = self.params['days']
        experiments = self.params['experiments']
        transition = self.params['transition']
        k = self.params['k']
        
        # New parameters
        mass = self.params['mass']
        sugar_min = self.params['sugar_min']
        sugar_max = self.params['sugar_max']
        deg_min = self.params['deg_min']
        deg_max = self.params['deg_max']
        distribution = self.params['distribution']
        
        # Initialize accumulators for cumulative sums
        # Note: The size of arrays should now be 'days' (v), not 'size' (n)
        # because we are plotting over time (stages)
        results = {
            'HungarianMin': np.zeros(days),
            'HungarianMax': np.zeros(days),
            'Thrifty': np.zeros(days),
            'Greedy': np.zeros(days),
            'GreedyThrifty': np.zeros(days),
            'ThriftyGreedy': np.zeros(days),
            'ThriftyKeyGreedy': np.zeros(days)
        }
        
        # Accumulator for relative losses
        losses = {
            'Greedy': 0.0,
            'Thrifty': 0.0,
            'GreedyThrifty': 0.0,
            'ThriftyGreedy': 0.0,
            'ThriftyKeyGreedy': 0.0
        }

        # Instantiate Generator with parameters
        generator = MatrixGenerator.MatrixGenerator(
            n=size, 
            v=days, 
            a_min=sugar_min, 
            a_max=sugar_max, 
            beta1=deg_min, 
            beta2=deg_max
        )

        for i in range(experiments):
            # Use GenerateCMatrix
            matrix = generator.GenerateCMatrix(distribution_type=distribution)
            
            comp = Computing.Computing(matrix)

            # Helper to add cumulative sum safely
            def add_cum_sum(key, values):
                # Pad values with zeros if length is less than days
                padded_values = np.zeros(days)
                length = min(len(values), days)
                padded_values[:length] = values[:length]
                
                # If we stopped early, the cumulative sum should persist the last value?
                # No, values are costs per step. If we stop, cost is 0.
                # So cumsum will just stay flat.
                
                results[key] += np.cumsum(padded_values)
                return np.sum(values)

            # Hungarian Min
            # We need to sort values by column index to represent time correctly
            row_ind, col_ind = scipy.optimize.linear_sum_assignment(matrix)
            # Create an array of size 'days' (v)
            hungarian_min_values = np.zeros(days)
            # Fill in the costs at the correct days (columns)
            hungarian_min_values[col_ind] = matrix[row_ind, col_ind]
            
            # We use this sorted array for plotting
            add_cum_sum('HungarianMin', hungarian_min_values)

            # Hungarian Max (Optimal for Maximization)
            row_ind, col_ind = scipy.optimize.linear_sum_assignment(-matrix)
            hungarian_max_values = np.zeros(days)
            hungarian_max_values[col_ind] = matrix[row_ind, col_ind]
            
            opt_val = add_cum_sum('HungarianMax', hungarian_max_values)

            # Thrifty
            _, values = comp.ThriftyMethod()
            val = add_cum_sum('Thrifty', values)
            if opt_val != 0:
                losses['Thrifty'] += (opt_val - val) / opt_val

            # Greedy
            _, values = comp.GreedyMethod()
            val = add_cum_sum('Greedy', values)
            if opt_val != 0:
                losses['Greedy'] += (opt_val - val) / opt_val

            # Greedy -> Thrifty
            _, values = comp.Greedy_ThriftyMethodX(transition)
            val = add_cum_sum('GreedyThrifty', values)
            if opt_val != 0:
                losses['GreedyThrifty'] += (opt_val - val) / opt_val

            # Thrifty -> Greedy
            _, values = comp.Thrifty_GreedyMethodX(transition)
            val = add_cum_sum('ThriftyGreedy', values)
            if opt_val != 0:
                losses['ThriftyGreedy'] += (opt_val - val) / opt_val

            # Thrifty(k) -> Greedy
            _, values = comp.TkG_MethodX(k, transition)
            val = add_cum_sum('ThriftyKeyGreedy', values)
            if opt_val != 0:
                losses['ThriftyKeyGreedy'] += (opt_val - val) / opt_val

            self.progress.emit(int((i + 1) / experiments * 100))

        # Average out results
        for key in results:
            results[key] /= experiments
            
        # Average out losses
        for key in losses:
            losses[key] /= experiments
            
        # Add losses to results dictionary
        results['losses'] = losses

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
        
        self.spin_size_days = QSpinBox()
        self.spin_size_days.setRange(2, 100)
        self.spin_size_days.setValue(15)

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
        
        # Distribution Type
        self.dist_layout = QHBoxLayout()
        self.radio_uniform = QRadioButton("Равномерное")
        self.radio_concentrated = QRadioButton("Сконцентрированное")
        self.radio_uniform.setChecked(True)
        
        self.dist_group = QButtonGroup(self)
        self.dist_group.addButton(self.radio_uniform)
        self.dist_group.addButton(self.radio_concentrated)
        
        self.dist_layout.addWidget(self.radio_uniform)
        self.dist_layout.addWidget(self.radio_concentrated)

        self.params_layout.addRow("Кол-во партий и этапов:", self.spin_size_days)
        self.params_layout.addRow("Эксперименты:", self.spin_experiments)
        self.params_layout.addRow("Этап смены стратегии:", self.spin_transition)
        self.params_layout.addRow("Параметр k:", self.spin_k)
        self.params_layout.addRow("Суточная масса:", self.spin_mass)
        
        self.params_layout.addRow(QLabel("Распределение:"))
        self.params_layout.addRow(self.dist_layout)
        
        # Modified layout: Label on top, controls below
        self.params_layout.addRow(QLabel("Сахаристость:"))
        self.params_layout.addRow(self.sugar_layout)
        
        self.params_layout.addRow(QLabel("Деградация:"))
        self.params_layout.addRow(self.deg_layout)
        
        self.settings_layout.addWidget(self.params_group)
        
        # Buttons Layout
        self.buttons_layout = QHBoxLayout()
        
        self.btn_export = QPushButton("Экспорт")
        self.btn_export.clicked.connect(self.export_csv)
        self.btn_export.setFixedHeight(45)
        self.buttons_layout.addWidget(self.btn_export)

        self.btn_random = QPushButton("Случайно")
        self.btn_random.clicked.connect(self.randomize_parameters)
        self.btn_random.setFixedHeight(45)
        self.buttons_layout.addWidget(self.btn_random)
        
        self.settings_layout.addLayout(self.buttons_layout)

        self.btn_run = QPushButton("Запустить сравнение")
        self.btn_run.clicked.connect(self.run_comparison)
        self.btn_run.setFixedHeight(45) # Slightly taller
        self.settings_layout.addWidget(self.btn_run)
        
        self.settings_layout.addStretch()
        
        # --- Right Side (Visualization) ---
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)

        # Top controls layout
        self.top_controls_layout = QHBoxLayout()

        # View Selector
        self.view_selector = QComboBox()
        self.view_selector.addItems(["График", "Гистограмма", "Общие результаты"])
        self.view_selector.currentIndexChanged.connect(self.update_view)
        self.top_controls_layout.addWidget(self.view_selector)
        
        self.right_layout.addLayout(self.top_controls_layout)

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
        
        # Reset View Button (Below the graph)
        self.btn_reset_view = QPushButton("Сбросить вид")
        self.btn_reset_view.clicked.connect(self.reset_view)
        self.right_layout.addWidget(self.btn_reset_view)
        
        self.layout.addWidget(self.settings_panel)
        self.layout.addWidget(self.right_panel)

        self.style_plot(self.ax_graph)
        self.style_plot(self.ax_hist)
        
        # Initialize Plot Navigators
        self.nav_graph = PlotNavigator(self.canvas_graph, self.ax_graph)
        self.nav_hist = PlotNavigator(self.canvas_hist, self.ax_hist)
        
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

    def reset_view(self):
        index = self.stacked_widget.currentIndex()
        if index == 0: # Graph
            self.ax_graph.autoscale()
            self.ax_graph.relim()
            self.canvas_graph.draw()
        elif index == 1: # Histogram
            self.ax_hist.autoscale()
            self.ax_hist.relim()
            self.canvas_hist.draw()

    def run_comparison(self):
        # Validate parameters to prevent crash
        s_min = self.spin_sugar_min.value()
        s_max = self.spin_sugar_max.value()
        if s_min >= s_max:
            QMessageBox.warning(self, "Ошибка", "Мин. сахаристость должна быть меньше Макс.")
            return

        d_min = self.spin_deg_min.value()
        d_max = self.spin_deg_max.value()
        if d_min >= d_max:
            QMessageBox.warning(self, "Ошибка", "Мин. деградация должна быть меньше Макс.")
            return

        params = {
            'size': self.spin_size_days.value(),
            'days': self.spin_size_days.value(),
            'experiments': self.spin_experiments.value(),
            'transition': self.spin_transition.value(),
            'k': self.spin_k.value(),
            'mass': self.spin_mass.value(),
            'sugar_min': self.spin_sugar_min.value(),
            'sugar_max': self.spin_sugar_max.value(),
            'deg_min': self.spin_deg_min.value(),
            'deg_max': self.spin_deg_max.value(),
            'distribution': 'uniform' if self.radio_uniform.isChecked() else 'concentrated'
        }
        
        self.btn_run.setEnabled(False)
        self.btn_run.setText("Выполняется...")
        
        self.worker = Worker(params)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, results):
        self.btn_run.setEnabled(True)
        self.btn_run.setText("Запустить сравнение")
        self.current_results = results
        self.update_view()

    def update_view(self):
        if self.current_results is None:
            return
            
        index = self.view_selector.currentIndex()
        self.stacked_widget.setCurrentIndex(index)
        
        # Show/Hide reset button
        if index == 2: # General Results
             self.btn_reset_view.setVisible(False)
        else:
             self.btn_reset_view.setVisible(True)
        
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
        
        legend = self.ax_graph.legend(loc='upper left')
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
        
        # Exclude Hungarian Max and Min from best/worst strategy calculation
        heuristic_values = final_values.copy()
        if 'Венгерский (Максимум)' in heuristic_values:
            del heuristic_values['Венгерский (Максимум)']
        if 'Венгерский (Минимум)' in heuristic_values:
            del heuristic_values['Венгерский (Минимум)']
            
        best_strategy = max(heuristic_values, key=heuristic_values.get)
        best_value = heuristic_values[best_strategy]

        worst_strategy = min(heuristic_values, key=heuristic_values.get)
        worst_value = heuristic_values[worst_strategy]
        
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
        <p>Наихудший результат виртуального эксперимента — <b style="color: #f38ba8">{worst_strategy}</b> ({worst_value:.2f}).</p>
        <p>Согласно генеральному эксперименту в следующем сезоне предлагается применить <b style="color: #a6e3a1">{best_strategy}</b>.</p>
        """
        
        self.results_text.setHtml(text)

    def randomize_parameters(self):
        val = random.randint(10, 30)
        self.spin_size_days.setValue(val)
        self.spin_experiments.setValue(random.randint(50, 500))
        self.spin_transition.setValue(random.randint(1, val))
        self.spin_k.setValue(random.randint(1, 5))
        self.spin_mass.setValue(random.randint(1000, 5000))
        
        s_min = round(random.uniform(0.10, 0.18), 2)
        s_max = round(random.uniform(s_min + 0.01, 0.25), 2)
        self.spin_sugar_min.setValue(s_min)
        self.spin_sugar_max.setValue(s_max)
        
        d_min = round(random.uniform(0.90, 0.96), 2)
        d_max = round(random.uniform(d_min + 0.01, 0.99), 2)
        self.spin_deg_min.setValue(d_min)
        self.spin_deg_max.setValue(d_max)
        
        if random.choice([True, False]):
            self.radio_uniform.setChecked(True)
        else:
            self.radio_concentrated.setChecked(True)

    def export_csv(self):
        if self.current_results is None or 'losses' not in self.current_results:
            QMessageBox.warning(self, "Ошибка", "Сначала запустите сравнение алгоритмов.")
            return

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Сохранить CSV", "", "CSV Files (*.csv);;All Files (*)", options=options)
        
        if fileName:
            try:
                with open(fileName, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile, delimiter=';')
                    writer.writerow(['Стратегия', 'Средняя относительная потеря'])
                    
                    losses = self.current_results['losses']
                    
                    # Map keys to Russian names
                    names = {
                        'Greedy': 'Жадная',
                        'Thrifty': 'Бережливая',
                        'GreedyThrifty': 'Жадная -> Бережливая',
                        'ThriftyGreedy': 'Бережливая -> Жадная',
                        'ThriftyKeyGreedy': 'Бережливая(k) -> Жадная'
                    }
                    
                    for key, value in losses.items():
                        name = names.get(key, key)
                        writer.writerow([name, f"{value:.6f}"])
                        
                QMessageBox.information(self, "Успех", "Файл успешно сохранен.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
