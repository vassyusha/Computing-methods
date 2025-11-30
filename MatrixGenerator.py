import numpy as np
from typing import Tuple, Dict
from accessify import private

class MatrixGenerator:
    def __init__(self, n: int = 10, v: int = 7, a_min: float = 0.12, a_max: float = 0.22, beta1: float = 0.85, beta2: float = 1.0):
        self._validate_parameters(n, v, a_min, a_max, beta1, beta2)
        self.n = n
        self.v = v
        self.a_min = a_min
        self.a_max = a_max
        self.beta1 = beta1
        self.beta2 = beta2
    @private
    def _validate_parameters(self, n: int, v: int, a_min: float, a_max: float, beta1: float, beta2: float):
        if n <= 0:
            raise ValueError("n must be more than 0")
        if v <= 20:
            raise ValueError("v must be more than 20")
        if a_min >= a_max:
            raise ValueError("a_min must be less than a_max")
        if beta1 >= beta2:
            raise ValueError("beta1 must be less than beta2")
        if not (0.85 <= beta1 < beta2 <= 1.0):
                raise ValueError("beta1 and beta2 must be in range [0.85, 1.0]")
                
    def generate_matrices(self, distribution_type: str = "uniform") -> Dict[str, np.array]:
        a_vector, b_matrix = self._init_small_experiment(distribution_type)
        return {
            'a_vector': a_vector,
            'b_matrix': b_matrix,
            'parameters': {
                'n': self.n,
                'v': self.v,
                'distribution_type': distribution_type
            }
        }
    @private
    def _init_small_experiment(self, distribution_type: str) -> Tuple[np.array, np.array]:
        a_vector = np.array([np.random.uniform(self.a_min, self.a_max) for _ in range(self.n)])  # вектор начальной сахаристости

        if distribution_type == "uniform":
            b_matrix = np.array([[np.random.uniform(self.beta1, self.beta2) for _ in range(self.v)] for _ in range(self.n) ]) # матрица коэффициентов деградации
        elif distribution_type == "concentrated":
            b_matrix = np.array([[0.0 for _ in range(self.v)] for _ in range(self.n)]) # матрица коэффициентов деградации
            
            for i in range(self.n):
                max_delta = (self.beta2 - self.beta1) / 4   
                delta_i = np.random.uniform(0, max_delta)
                
                beta1_i = np.random.uniform(self.beta1, self.beta2 - delta_i)
                beta2_i = beta1_i + delta_i
                
                for j in range(self.v):
                    b_matrix[i][j] = np.random.uniform(beta1_i, beta2_i)
        else:
            raise ValueError("distribution_type must be 'uniform' or 'concentrated'")
        
        return a_vector, b_matrix