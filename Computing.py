import numpy as np
import scipy
import accessify

class Computing:
    def __init__(self, matirx):
        self.__params = matirx
    
    @accessify.private
    def FindMinInColumnWhithExclitedRows(self, column_id, excluded_rows):
        matrix = np.copy(self.__params)
        col = matrix[:, column_id]

        mask = np.ones(len(col), bool)
        excluded_indices = [int(idx) for idx in excluded_rows]
        mask[excluded_indices] = False

        filtered_columns = col[mask]

        min_val = np.min(filtered_columns)

        avel_min = np.where(mask)[0]
        min_filt_id = np.argmin(filtered_columns)
        mat_min_id = avel_min[min_filt_id]

        return min_val, mat_min_id

    def HungarianMinimum(self):
        row_ind, col_ind = scipy.optimize.linear_sum_assignment(self.__params)
        cost = self.__params[row_ind, col_ind].sum()
        return cost
    
    def HungarianMaximum(self):
            matrix = -self.__params.copy()
            row_ind, col_ind = scipy.optimize.linear_sum_assignment(matrix)
            cost = self.__params[row_ind, col_ind].sum()
            return cost

    
    def ThriftyMethod(self):
        cost = 0
        shapes = self.__params.shape
        assigned_rows = set()

        for i in range(shapes[0]):
            min_val, row = self.FindMinInColumnWhithExclitedRows(i, assigned_rows)
            cost += min_val
            assigned_rows.add(row)
        
        return cost
    
    # ...
    
    def Method_N(self):
        return 0
    