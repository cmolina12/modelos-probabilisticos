from math import factorial
from math import prod

# Funcion para calcular la probaiblidad de de estar vacio (pi_0) en el caso de M/M/s/K

lmbda = 1 / 3
mu = 4 / 3
r = lmbda / mu

s = 2
k = 4


def pi_0(s, r, k):
    sum1 = sum((r**n) / (factorial(n)) for n in range(s))
    sum2 = sum((r**n) / (factorial(s) * (s ** (n - s))) for n in range(s, k + 1))
    return 1 / (sum1 + sum2)


print(f"pi_0: {pi_0(s, r, k)}")

# Funcion para calcular el resto de pi_n con respecto a pi_0


def pi_n(n, s, r, k):
    pi0 = pi_0(s, r, k)
    if n < s:
        return (r**n / factorial(n)) * pi0
    elif s <= n <= k:
        return (r**n / (factorial(s) * (s ** (n - s)))) * pi0
    else:
        return 0


n = k  # Numero maximo de clientes en el sistema

for i in range(n + 1):
    print(f"pi_{i}: {pi_n(i, s, r, k)}")

# Funcion para en caso de M/M/1/K con tasa mu variable segun el numero de clientes en el sistema, sacar la probabilidad de estar vacio

lmbda = 5  # clientes/hora

mu = {
    1: 60 / 9,
    2: 60 / 10,
    3: 60 / 10,
    4: 60 / 13,
    5: 60 / 20,
}  # diccionario de mu, llave siendo numero de clientes en el sistema y valor siendo la tasa media de servicio

# Sacar el diccinario de cada mu multiplicado por todos sus mu_s anteriores

mu_dict = {n: prod(mu[i] for i in range(1, n + 1)) for n in mu}

k = 5  # numero maximo de clientes en el sistema

s = 1  # 1 peluquero

# 1. Coeficientes de equilibrio para cada p_i

coeficientes = {n: (lmbda / mu_dict[n]) for n in mu}

# 2. p_0

p_0 = 1 / (1 + sum(coeficientes[n] * mu_dict[n] for n in mu))

print(f"p_0: {p_0}")

# 3. p_n

p_n = {n: p_0 * coeficientes[n] for n in mu}

for i in p_n:
    print(f"p_{i}: {p_n[i]}")
