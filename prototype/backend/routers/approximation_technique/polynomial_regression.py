import numpy as np

def polynomial_regression(data_points , degree:int = 4):
    rhs_list = []
    lhs_list = []
    print(degree)
    for i in range(len(data_points)):
        temp = []
        for j in range(degree):  
            temp.append(data_points[i][0]**j)  
        lhs_list.append(temp)
        rhs_list.append(data_points[i][1])
    rhs = np.array(rhs_list)
    lhs = np.array(lhs_list)
    coefficients, *_ = np.linalg.lstsq(lhs , rhs, rcond=None)
    res = ""
    for i in range(len(coefficients)):
        if i == len(coefficients) - 1:
            res += str(round(coefficients[i], 2)) + " * (x ^ " + str(i) + ")"
            break
        res += str(round(coefficients[i], 2)) + " * (x ^ " + str(i) + ") + "
    return res

