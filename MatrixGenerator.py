import numpy as np
from typing import Tuple, Dict
from accessify import private

class MatrixGenerator:
    def __init__(self, n: int = 10, v: int = 7, a_min: float = 0.12, a_max: float = 0.22, beta1: float = 0.85, beta2: float = 1.0):
        self.__validate_parameters(n, v, a_min, a_max, beta1, beta2)
        self.n = n
        self.v = v
        self.a_min = a_min
        self.a_max = a_max
        self.beta1 = beta1
        self.beta2 = beta2
        
    @private
    def __validate_parameters(self, n: int, v: int, a_min: float, a_max: float, beta1: float, beta2: float):
        if n <= 0:
            raise ValueError("n must be more than 0")
        if v <= 0:
            raise ValueError("v must be more than 0")
        if a_min >= a_max:
            raise ValueError("a_min must be less than a_max")
        if beta1 >= beta2:
            raise ValueError("beta1 must be less than beta2")
        
    @private
    def GenerateABMatrices(self, distribution_type: str) -> Tuple[np.array, np.array]:
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
            raise ValueError("Distribution type must be 'uniform' or 'concentrated'")
        
        return a_vector, b_matrix
                
    def GenerateCMatrix(self, distribution_type: str = "uniform") -> np.array:
        a_vector, b_matrix = self.GenerateABMatrices(distribution_type)
        
        n, v = b_matrix.shape
        c_matrix = np.zeros((n, v))
        
        c_matrix[:, 0] = a_vector # c_i1 = a_i
        
        for j in range(1, v):
            c_matrix[:, j] = c_matrix[:, j-1] * b_matrix[:, j-1]
        
        return c_matrix
    
    def GenerateDummyMatrix(self):
        dummy_matrix = np.array(np.random.uniform(-200, 200, size=(self.n, self.n)))
        return dummy_matrix