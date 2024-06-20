'''
This acceptance criterion is based on simulated annealing, i.e. the probability of acceptance is:
e^{-(f(s') - f(s)) / T(t)}
The temperature is updated based on:
T(t) = \frac{C}{(1 + \frac{t}{t_{\max}})^{p}}
Here, we set C = \sqrt{n} * gs['max_dist'] and p equal to 2
'''
import math
import random

def simulated_annealing(n, t, t_max, obj_val_sol, sol_prime, gs):
    if sol_prime['obj_val'] <= obj_val_sol:
        return True # Always accept if better
    T_now = (n ** 0.5) * gs['max_dist'] / (1 + (t / t_max))**5
    accept = random.random() < math.exp(-(sol_prime['obj_val'] - obj_val_sol) / T_now)
    return accept
