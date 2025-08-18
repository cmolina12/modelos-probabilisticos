import numpy as np
import math

# Funcion para crear la matriz de transiciones

def transaction_matrix(states):

    k = max(states)
    n = len(states)
    matrix = np.zeros((n, n), dtype=float)

    lambd = 3

    for index_final, j in enumerate(states):
        for index_initial, i in enumerate(states):
            
            if (2 <= i <= j) and not (i==k and j==k):
                matrix[index_final, index_initial] = poisson(lambd, j - i)
                
            elif i == k and j != k:
                temp_prob = 0 
                for m in range(0, j-1):
                    temp_prob += poisson(lambd, m)
                matrix[index_final, index_initial] = 1 - temp_prob
                
            elif i == k and j == k:
                temp_prob_2 = 0 
                for m in range(0, j-1):
                    temp_prob_2 += poisson(lambd, m)
                prob_0 = poisson(lambd, 0)
                matrix[index_final, index_initial] = (1-temp_prob_2) + prob_0  
            else:
                matrix[index_final, index_initial] = 0
                
    return matrix

# Function to calculate Poisson probability
                
def poisson(lambd, k):
    return (lambd**k * np.exp(-lambd)) / math.factorial(k)
        
# Example usage
states = [2, 3, 4, 5]
resultado = transaction_matrix(states)

# Check if the transition matrix is valid
for filas in resultado:
    resultado_filas = 0
    
    for valor in filas:
        resultado_filas += valor
        
    if resultado_filas != 1:
        print("Error: La suma de las filas no es igual a 1.")
        break
else:
    print("La matriz de transicion es válida.")
    
print(resultado)  

            


