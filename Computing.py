import numpy as np
import scipy

class Computing:
    def __init__(self, matirx):
        self._params = matirx
    
    def HungarianMinimum(self):
        row_ind, col_ind = scipy.optimize.linear_sum_assignment(self._params)
        cost = self._params[row_ind, col_ind].sum()
        return cost
    
    def HungarianMaximum(self):
            matrix = -self._params.copy()
            row_ind, col_ind = scipy.optimize.linear_sum_assignment(matrix)
            cost = self._params[row_ind, col_ind].sum()
            return cost

    def Method_2(self):
        return 0
    
    # ...
    
    def Method_N(self):
        return 0
    