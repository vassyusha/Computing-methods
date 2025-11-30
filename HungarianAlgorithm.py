import numpy as np

class HungarianAlgorithm:
    def __init__(self, matrix, mode='min'):
        self.original_matrix = np.array(matrix, dtype=float)
        self.n = self.original_matrix.shape[0]
        self.mode = mode
        
        # Рабочая матрица
        self.matrix = self.original_matrix.copy()
            
        # Состояние
        self.steps = []
        self.current_step_index = -1
        
        # Состояние алгоритма
        self.marked_zeros = [] # Список (r, c)
        self.crossed_zeros = [] # Список (r, c)
        self.h_lines = [] # Список индексов строк
        self.v_lines = [] # Список индексов столбцов
        
        self.save_step("Начало работы. Инициализация.", "INIT")
        
        self.run_algorithm()
        self.current_step_index = 0

    def save_step(self, description, stage):
        stars = np.zeros((self.n, self.n), dtype=bool)
        for r, c in self.marked_zeros:
            stars[r, c] = True
            
        # Используем слот 'primes' для зачеркнутых нулей
        crossed = np.zeros((self.n, self.n), dtype=bool)
        for r, c in self.crossed_zeros:
            crossed[r, c] = True
            
        row_covered = np.zeros(self.n, dtype=bool)
        for r in self.h_lines:
            row_covered[r] = True
            
        col_covered = np.zeros(self.n, dtype=bool)
        for c in self.v_lines:
            col_covered[c] = True

        step_data = {
            'matrix': self.matrix.copy(),
            'stars': stars,
            'primes': crossed, 
            'row_covered': row_covered,
            'col_covered': col_covered,
            'description': description,
            'stage': stage
        }
        self.steps.append(step_data)

    def run_algorithm(self):
        # Шаг 1
        if self.mode == 'max':
            for r in range(self.n):
                max_val = np.max(self.matrix[r, :])
                self.matrix[r, :] = max_val - self.matrix[r, :]
            self.save_step("Шаг 1: (Максимизация) Вычитание элементов из максимума строки.", "STEP_1")
        
        # Шаг 2
        for r in range(self.n):
            min_val = np.min(self.matrix[r, :])
            self.matrix[r, :] -= min_val
        self.save_step("Шаг 2: Вычитание минимума строки из всех элементов строки.", "STEP_2")
        
        # Шаг 3
        for c in range(self.n):
            min_val = np.min(self.matrix[:, c])
            self.matrix[:, c] -= min_val
        self.save_step("Шаг 3: Вычитание минимума столбца из всех элементов столбца.", "STEP_3")
        
        while True:
            # Шаги 4-6: Отметка нулей
            self.marked_zeros = []
            self.crossed_zeros = []
            self.h_lines = []
            self.v_lines = []
            
            while True:
                progress = False
                
                # Получаем все нули, которые не отмечены и не зачеркнуты
                zeros = []
                for r in range(self.n):
                    for c in range(self.n):
                        if self.matrix[r, c] == 0 and (r, c) not in self.marked_zeros and (r, c) not in self.crossed_zeros:
                            zeros.append((r, c))
                
                if not zeros:
                    break
                
                row_counts = {}
                col_counts = {}
                
                for r, c in zeros:
                    row_counts[r] = row_counts.get(r, 0) + 1
                    col_counts[c] = col_counts.get(c, 0) + 1
                
                # Шаг 4: Строка с ровно одним нулем
                found_step_4 = False
                for r in sorted(row_counts.keys()):
                    if row_counts[r] == 1:
                        target_c = -1
                        for c_candidate in range(self.n):
                            if (r, c_candidate) in zeros:
                                target_c = c_candidate
                                break
                        
                        if target_c != -1:
                            self.marked_zeros.append((r, target_c))
                            for r_other in range(self.n):
                                if r_other != r and self.matrix[r_other, target_c] == 0 and (r_other, target_c) not in self.marked_zeros and (r_other, target_c) not in self.crossed_zeros:
                                    self.crossed_zeros.append((r_other, target_c))
                            
                            self.save_step(f"Шаг 4: В строке {r+1} один ноль ({r+1}, {target_c+1}). Отмечаем его, зачеркиваем нули в столбце.", "STEP_4")
                            progress = True
                            found_step_4 = True
                            break 
                
                if found_step_4:
                    continue 
                
                # Шаг 5: Столбец с ровно одним нулем
                found_step_5 = False
                for c in sorted(col_counts.keys()):
                    if col_counts[c] == 1:
                        target_r = -1
                        for r_candidate in range(self.n):
                            if (r_candidate, c) in zeros:
                                target_r = r_candidate
                                break
                        
                        if target_r != -1:
                            self.marked_zeros.append((target_r, c))
                            for c_other in range(self.n):
                                if c_other != c and self.matrix[target_r, c_other] == 0 and (target_r, c_other) not in self.marked_zeros and (target_r, c_other) not in self.crossed_zeros:
                                    self.crossed_zeros.append((target_r, c_other))
                            
                            self.save_step(f"Шаг 5: В столбце {c+1} один ноль ({target_r+1}, {c+1}). Отмечаем его, зачеркиваем нули в строке.", "STEP_5")
                            progress = True
                            found_step_5 = True
                            break
                
                if found_step_5:
                    continue

                # Шаг 6: Произвольный ноль
                if zeros:
                    r, c = zeros[0]
                    self.marked_zeros.append((r, c))
                    
                    for c_other in range(self.n):
                         if c_other != c and self.matrix[r, c_other] == 0 and (r, c_other) not in self.marked_zeros and (r, c_other) not in self.crossed_zeros:
                                    self.crossed_zeros.append((r, c_other))
                    for r_other in range(self.n):
                         if r_other != r and self.matrix[r_other, c] == 0 and (r_other, c) not in self.marked_zeros and (r_other, c) not in self.crossed_zeros:
                                    self.crossed_zeros.append((r_other, c))
                                    
                    self.save_step(f"Шаг 6: Выбираем произвольный ноль ({r+1}, {c+1}). Отмечаем, зачеркиваем соседей.", "STEP_6")
                    progress = True
                    
                if not progress:
                    break
            
            # Шаг 7: Проверка оптимальности
            if len(self.marked_zeros) == self.n:
                self.save_step("Шаг 7: Оптимальное решение найдено (N отмеченных нулей).", "DONE")
                break
            
            # Проводим линии (Алгоритм Кенига)
            rows_with_marked = set(r for r, c in self.marked_zeros)
            marked_rows_konig = set([r for r in range(self.n) if r not in rows_with_marked])
            marked_cols_konig = set()
            
            while True:
                added = False
                for r in marked_rows_konig:
                    for c in range(self.n):
                        if self.matrix[r, c] == 0 and c not in marked_cols_konig:
                            marked_cols_konig.add(c)
                            added = True
                
                for r, c in self.marked_zeros:
                    if c in marked_cols_konig and r not in marked_rows_konig:
                        marked_rows_konig.add(r)
                        added = True
                
                if not added:
                    break
            
            self.h_lines = [r for r in range(self.n) if r not in marked_rows_konig]
            self.v_lines = list(marked_cols_konig)
            
            self.save_step(f"Шаг 7: Решение не оптимально ({len(self.marked_zeros)}/{self.n}). Проводим минимальное число линий.", "STEP_7_LINES")
            
            # Шаг 8: Обновление матрицы
            min_val = float('inf')
            for r in range(self.n):
                if r in self.h_lines: continue
                for c in range(self.n):
                    if c in self.v_lines: continue
                    if self.matrix[r, c] < min_val:
                        min_val = self.matrix[r, c]
            
            self.save_step(f"Шаг 8: Минимальный незачеркнутый элемент: {min_val}.", "STEP_8_MIN")
            
            for r in range(self.n):
                for c in range(self.n):
                    if r not in self.h_lines and c not in self.v_lines:
                        self.matrix[r, c] -= min_val
                    
                    if r in self.h_lines and c in self.v_lines:
                        self.matrix[r, c] += min_val
            
            self.save_step("Шаг 8: Матрица обновлена. Возврат к шагу 4.", "STEP_8_UPDATE")

    def get_current_state(self):
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def next(self):
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            return self.get_current_state()
        return None

    def prev(self):
        if self.current_step_index > 0:
            self.current_step_index -= 1
            return self.get_current_state()
        return None
    
    def is_finished(self):
        return self.current_step_index == len(self.steps) - 1
