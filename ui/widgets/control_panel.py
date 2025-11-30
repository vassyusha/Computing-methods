
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QTextEdit, QFrame
)
from PyQt5.QtCore import Qt
import qtawesome as qta

class ControlPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "card") # Для стилизации как карточки
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 8, 15, 15) # Уменьшенный верхний отступ
        self.layout.setSpacing(8) # Уменьшенный отступ между элементами

        # --- Кнопки управления ---
        # Основная кнопка Старт
        self.btn_start = QPushButton(" Старт")
        self.btn_start.setObjectName("btn_start") # Для CSS
        self.btn_start.setIcon(qta.icon('fa5s.play'))
        # Переопределяем padding, чтобы текст влезал в уменьшенную кнопку
        self.btn_start.setStyleSheet("padding: 6px 20px; font-size: 11pt;") 
        self.btn_start.setFixedHeight(40) # Увеличиваем высоту
        self.layout.addWidget(self.btn_start)

        # Вторичные кнопки навигации
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setSpacing(5)
        
        self.btn_back = QPushButton()
        self.btn_back.setIcon(qta.icon('fa5s.step-backward'))
        self.btn_back.setToolTip("Шаг назад")
        self.btn_back.setFixedHeight(32) # Увеличиваем высоту
        
        self.btn_next = QPushButton()
        self.btn_next.setIcon(qta.icon('fa5s.step-forward'))
        self.btn_next.setToolTip("Следующий шаг")
        self.btn_next.setFixedHeight(32) # Увеличиваем высоту

        self.btn_auto = QPushButton(" Авто")
        self.btn_auto.setIcon(qta.icon('fa5s.fast-forward'))
        self.btn_auto.setFixedHeight(32) # Увеличиваем высоту
        
        self.nav_layout.addWidget(self.btn_back)
        self.nav_layout.addWidget(self.btn_next)
        self.nav_layout.addWidget(self.btn_auto)
        
        self.layout.addLayout(self.nav_layout)

        # Кнопка решения
        self.btn_solution = QPushButton(" Показать решение")
        self.btn_solution.setIcon(qta.icon('fa5s.calculator'))
        self.btn_solution.setFixedHeight(36) # Увеличиваем высоту
        self.layout.addWidget(self.btn_solution)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line)

        # --- Регулятор скорости ---
        # Компактный вид: Слайдер и подпись в одну строку или более плотно
        self.speed_layout = QVBoxLayout()
        self.speed_layout.setSpacing(2)
        
        self.speed_label = QLabel("Скорость анимации")
        self.speed_label.setStyleSheet("font-size: 10pt; color: #A6ADC8;")
        self.speed_layout.addWidget(self.speed_label)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(50)
        self.speed_slider.setFixedHeight(20) # Компактный слайдер
        
        self.speed_layout.addWidget(self.speed_slider)
        self.layout.addLayout(self.speed_layout)

        # --- Лог ---
        self.log_label = QLabel("Лог выполнения:")
        self.layout.addWidget(self.log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("Здесь будет отображаться ход выполнения алгоритма...")
        # Убираем фиксированную высоту и даем растягиваться
        self.layout.addWidget(self.log_text, stretch=1)

    def log(self, message, color=None):
        if color:
            formatted_message = f'<span style="color: {color}">{message}</span>'
        else:
            formatted_message = message
        self.log_text.append(formatted_message)
