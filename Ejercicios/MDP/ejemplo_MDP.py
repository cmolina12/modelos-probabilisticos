from amplpy import AMPL, Environment  # Importamos AMPL para modelado matemático
import numpy as np  # Importamos NumPy para operaciones numéricas
import pandas as pd  # Importamos Pandas para manejo de datos

# ======== INICIALIZACIÓN DE AMPL ========
# AMPL es un lenguaje de modelado algebraico para problemas de optimización
ampl = AMPL()
print("AMPL inicializado correctamente")

# ======== DEFINICIÓN DEL MODELO EN AMPL ========
# Este bloque define la estructura matemática del problema de optimización
ampl.set_option("solver", "highs")  # Seleccionamos el solver a utilizar

# Definimos el modelo matemático en sintaxis AMPL
ampl.eval(
    r"""
set S;              # Conjunto de estados (niveles de inventario)
set A within S cross S;  # Conjunto de acciones válidas para cada estado

param gamma;        # Tasa de descuento para valorar recompensas futuras
param P{(s,a,s1) in S cross S cross S};   # Probabilidades de transición entre estados
param R{(s,a) in A};   # Recompensa esperada para cada par estado-acción

var V{S};           # Variable: valor de cada estado

minimize TotalValue:
    sum {s in S} V[s];  # Función objetivo: minimizar la suma de valores (equivalente a maximizar el negativo)

subject to Bellman{s in S, a in S: (s,a) in A}:
    V[s] >= R[s,a] + gamma * sum {s1 in S} P[s,a,s1] * V[s1];  # Restricciones de Bellman para programación dinámica
"""
)

# ======== PREPARACIÓN DE DATOS PARA EL MODELO ========
# Parámetros generales del Proceso de Decisión de Markov (MDP)
gamma = 0.9  # Factor de descuento para valorar recompensas futuras (entre 0 y 1)
demand_levels = [0, 1, 2, 3]  # Niveles de demanda posibles
prob_d = {
    d: 0.25 for d in demand_levels
}  # Probabilidad de cada nivel de demanda (distribución uniforme)

S = list(
    range(5)
)  # Conjuntos de Estados posibles: niveles de inventario de 0 a 4 unidades

# Definimos las acciones válidas: para cada estado s, podemos ordenar hasta completar capacidad máxima (4)
A = [(s, a) for s in S for a in range(5 - s)]  # a tal que s + a <= 4

# Mostramos las acciones válidas para cada estado
print("\nConjunto de acciones válidas (A):")
print("Estado (s) | Acción (a)")
print("-" * 25)
for s, a in A:
    print(f"{s:10d} | {a:10d}")

# ======== CÁLCULO DE PROBABILIDADES Y RECOMPENSAS ========
# Inicializamos diccionarios para almacenar probabilidades y recompensas
P_data = (
    {}
)  # Almacenará P(s'|s,a) - probabilidad de transición a s' desde s tomando acción a
R_data = {}  # Almacenará R(s,a) - recompensa esperada en estado s tomando acción a

# Para cada par estado-acción válido
for s, a in A:
    sa_inventory = s + a  # Inventario después de ordenar: inventario actual + pedido
    reward = 0.0  # Inicializamos la recompensa esperada

    # Calculamos la recompensa esperada considerando todos los posibles niveles de demanda
    for d in demand_levels:
        p_d = prob_d[d]  # Probabilidad de este nivel de demanda

        # Calculamos resultados operativos
        ventas = min(
            sa_inventory, d
        )  # Unidades vendidas (limitadas por inventario disponible)
        faltantes = max(
            0, d - sa_inventory
        )  # Unidades faltantes si la demanda supera el inventario
        inventario_final = max(
            0, sa_inventory - d
        )  # Inventario restante después de ventas

        # Cálculo financiero
        ingreso = 300000 * ventas  # Ingresos por ventas ($300,000 por unidad)
        costo_fijo = (
            100000 if a > 0 else 0
        )  # Costo fijo de ordenar ($100,000 si se ordena algo)
        costo_var = 25000 * a  # Costo variable de producción ($25,000 por unidad)
        costo_extra_mq = 75000 * max(
            0, a - 1
        )  # Costo extra por usar máquinas adicionales
        costo_faltantes = 60000 * faltantes  # Penalización por demanda insatisfecha
        costo_inventario = 40000 * inventario_final  # Costo de mantener inventario

        # Utilidad total para esta combinación de estado, acción y demanda
        utilidad = ingreso - (
            costo_fijo + costo_var + costo_extra_mq + costo_faltantes + costo_inventario
        )

        # Contribución a la recompensa esperada según probabilidad de esta demanda
        reward += p_d * utilidad

        # Calculamos el estado siguiente (nivel de inventario resultante)
        s1 = max(0, sa_inventory - d)
        # Acumulamos probabilidad de transición al estado s1
        P_data[(s, a, s1)] = P_data.get((s, a, s1), 0.0) + p_d

    # Guardamos la recompensa esperada para este par estado-acción
    R_data[(s, a)] = reward

# ======== TRANSFERENCIA DE DATOS A AMPL ========
# Pasamos todos los datos calculados al modelo AMPL

ampl.eval(
    f"""
data;
set S := {' '.join(str(s) for s in S)};  # Conjunto de estados
set A := {' '.join(f'({s},{a})' for s, a in A)};  # Conjunto de acciones válidas
param gamma := {gamma};  # Factor de descuento

param P default 0 :=  # Probabilidades de transición
{chr(10).join(f'[{s},{a},{s1}] {val}' for (s, a, s1), val in P_data.items())};

param R default 0 :=  # Recompensas esperadas
{chr(10).join(f'[{s},{a}] {val}' for (s, a), val in R_data.items())};
"""
)

# ======== VISUALIZACIÓN DE DATOS DEL MODELO ========
# Mostramos las tablas de probabilidades y recompensas para análisis

print("\nTabla de Probabilidades de Transición (P):")
print("Estado | Acción | Estado Siguiente | Probabilidad")
print("-" * 50)
for (s, a, s1), prob in P_data.items():
    print(f"{s:6d} | {a:6d} | {s1:16d} | {prob:12.4f}")

print("\nTabla de Recompensas (R):")
print("Estado | Acción | Recompensa")
print("-" * 35)
for (s, a), reward in R_data.items():
    print(f"{s:6d} | {a:6d} | {reward:12,.2f}")

# ======== RESOLUCIÓN DEL MODELO ========
# Resolvemos el problema de optimización

ampl.solve()

# ======== ANÁLISIS DE RESULTADOS ========
# Extraemos y mostramos los resultados de la optimización

print("Valores óptimos de cada estado:")
V = ampl.get_variable("V")  # Obtenemos los valores óptimos de cada estado
for s in S:
    print(f"V({s}) = {V[s].value():,.2f}")  # Mostramos el valor de cada estado


# ======== ANÁLISIS DE RESTRICCIONES ACTIVAS ========
# Identificamos qué restricciones de Bellman están activas (determinan la política óptima)

print("\nRestricciones de Bellman activas (variables duales):")
bellman = ampl.get_constraint("Bellman")
print("Estado | Acción | Valor Dual | Estado")
print("-" * 45)
for s in S:
    for a in range(5 - s):
        if (s, a) in A:
            dual_value = bellman[s, a].dual()  # Valor dual de la restricción
            estado = "Activa" if abs(dual_value) > 1e-6 else "Inactiva"
            if abs(dual_value) > 1e-6:  # Solo mostramos las restricciones activas
                print(f"{s:6d} | {a:6d} | {dual_value:10.6f} | {estado}")
