import numpy as np

# Parametros simbolicos

a1 = 0.8 # Probabilidad de pieza buena maquina 1
a2 = 0.7 # Probabilidad de pieza buena maquina 2

states = [(i,j) for i in range(3) for j in range(3)] # Estados posibles (0,1,2) piezas buenas en cada maquina
n = len(states) # Numero de estados
P = np.zeros((n,n)) # Matriz de transicion de estados

for index_from, (i,j) in enumerate(states): # index_from es el indice del estado actual, (i,j) es el estado actual
    # Ensamblaje instananeo si ambos mayores_iguales a 1
    if i >= 1 and j >= 1:
        i0 = i-1
        j0 = j-1
    else: # Si no, continuo con el mismo estado
        i0 = i
        j0 = j
        
    # Pueden producir mis maquinas
    
    can_m1 = (i0 < 2) # Puede producir maquina 1?
    can_m2 = (j0 < 2) # Puede producir maquina 2?
    
    for prod1 in [0,1]: # Piezas producidas por maquina 1, esto modela todas las combinaciones posibles
        for prod2 in [0,1]: # Piezas producidas por maquina 2, esto modela todas las combinaciones posibles
            if prod1 > 0 and not can_m1: # Si produce pero no puede, es decir no es posible
                continue # Paso a la siguiente iteracion porque esta es imposible
            if prod2 > 0 and not can_m2: # Si produce pero no puede, es decir no es posible
                continue # Paso a la siguiente iteracion porque esta es imposible
            
           # Nuevo estado despues de produccion
            ni = min(i0 + prod1, 2) # Nuevo estado maquina 1, maximo 2 (Se supone que no se puede almacenar mas de 2 piezas en el caso donde no se ensambla)
            nj = min(j0 + prod2, 2) # Nuevo estado maquina 2, maximo 2 (Se supone que no se puede almacenar mas de 2 piezas en el caso donde no se ensambla)
            
            index_to = states.index((ni, nj))  # Indice del nuevo estado
            # Probabilidad de transicion
            p = 1.0 # Probabilidad inicial
            p *= a1 if prod1 == 1 and can_m1 else (1-a1 if can_m1 else 1) # Si produjo y pudo, multiplico por a1, si no produjo pero pudo (defectuoso), multiplico por (1-a1), si no pudo, multiplico por 1 (1 porque no afecta la probabilidad y en si no paso nada)
            p *= a2 if prod2 == 1 and can_m2 else (1-a2 if can_m2 else 1) # Lo mismo para maquina 2
            
            P[index_from, index_to] += p # Sumo la probabilidad a la matriz de transicion
            
            
np.set_printoptions(precision=3, suppress=True) # Opciones de impresion para numpy
print(P) # Imprimo la matriz de transicion