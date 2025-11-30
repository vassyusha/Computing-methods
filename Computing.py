import numpy as np
import scipy.optimize
import accessify

class Computing:
    def __init__(self, matrix):
        self.__params = np.array(matrix)
    
    @accessify.private
    def FindMaxInColumnWithExcludedRows(self, column_id, excluded_rows):
        col = self.__params[:, column_id]
        n_rows = col.shape[0]
        
        mask = np.ones(n_rows, dtype=bool)
        if excluded_rows:
            mask[list(excluded_rows)] = False
            
        if not np.any(mask):
            return -1, -1

        filtered_col = col[mask]
        original_indices = np.where(mask)[0]
        
        max_idx_local = np.argmax(filtered_col)
        max_val = filtered_col[max_idx_local]
        row_idx = original_indices[max_idx_local]

        return max_val, row_idx

    @accessify.private
    def FindKMinInColumnWithExcludedRows(self, column_id, excluded_rows, k=1):
        col = self.__params[:, column_id]
        n_rows = col.shape[0]

        mask = np.ones(n_rows, dtype=bool)
        if excluded_rows:
            mask[list(excluded_rows)] = False
            
        if not np.any(mask):
            return -1, -1

        filtered_col = col[mask]
        original_indices = np.where(mask)[0]
        
        if k == 1:
            min_idx_local = np.argmin(filtered_col)
            return filtered_col[min_idx_local], original_indices[min_idx_local]

        k = min(k, len(filtered_col))
        
        partitioned_indices = np.argpartition(filtered_col, k - 1)
        kth_smallest_idx_local = partitioned_indices[k - 1]
        kth_val = filtered_col[kth_smallest_idx_local]
        
        return kth_val, original_indices[kth_smallest_idx_local]

    def HungarianMinimum(self):
        row_ind, col_ind = scipy.optimize.linear_sum_assignment(self.__params)
        values = self.__params[row_ind, col_ind]
        cost = values.sum()
        return cost, values
    
    def HungarianMaximum(self):
        row_ind, col_ind = scipy.optimize.linear_sum_assignment(-self.__params)
        values = self.__params[row_ind, col_ind]
        cost = values.sum()
        return cost, values

    def ThriftyMethod(self):
        cost = 0
        _, cols = self.__params.shape
        assigned_rows = set()
        values = []

        for i in range(cols):
            min_val, row = self.FindKMinInColumnWithExcludedRows(i, assigned_rows)
            if row != -1:
                cost += min_val
                assigned_rows.add(row)
                values.append(min_val)
        
        return cost, np.array(values)
    
    def GreedyMethod(self):
        cost = 0
        _, cols = self.__params.shape
        assigned_rows = set()
        values = []

        for i in range(cols):
            max_val, row = self.FindMaxInColumnWithExcludedRows(i, assigned_rows)
            if row != -1:
                cost += max_val
                assigned_rows.add(row)
                values.append(max_val)
        return cost, np.array(values)

    def Greedy_ThriftyMethodX(self, x):
        cost = 0
        _, cols = self.__params.shape
        assigned_rows = set()
        values = []

        for i in range(cols):
            if i < x:
                val, row = self.FindMaxInColumnWithExcludedRows(i, assigned_rows)
            else:
                val, row = self.FindKMinInColumnWithExcludedRows(i, assigned_rows)
            
            if row != -1:
                cost += val
                assigned_rows.add(row)
                values.append(val)

        return cost, np.array(values)
    
    def Thrifty_GreedyMethodX(self, x):
        cost = 0
        _, cols = self.__params.shape
        assigned_rows = set()
        values = []

        for i in range(cols):
            if i < x:
                val, row = self.FindKMinInColumnWithExcludedRows(i, assigned_rows)
            else:
                val, row = self.FindMaxInColumnWithExcludedRows(i, assigned_rows)
            
            if row != -1:
                cost += val
                assigned_rows.add(row)
                values.append(val)

        return cost, np.array(values)

    def TkG_MethodX(self, k, x):
        cost = 0
        _, cols = self.__params.shape
        assigned_rows = set()
        values = []

        for i in range(cols):
            if (i < x) and (i + k < cols):
                val, row = self.FindKMinInColumnWithExcludedRows(i, assigned_rows, k)
            else:
                val, row = self.FindMaxInColumnWithExcludedRows(i, assigned_rows)
                
            if row != -1:
                cost += val
                assigned_rows.add(row)
                values.append(val)
        
        return cost, np.array(values)