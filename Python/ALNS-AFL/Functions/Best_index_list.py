'''
This function finds the best index of a list of lists (or whatever depth)

'''

import numpy as np
def best_index_list(list, orientation):
    arr = np.array(list)
    if orientation == 'max':
        best_index = np.unravel_index(np.argmax(arr), arr.shape)
    elif orientation == 'min':
        best_index = np.unravel_index(np.argmin(arr), arr.shape)
    else:
        raise Exception("Error in best_index_list: orientation is not max or min")
    return best_index