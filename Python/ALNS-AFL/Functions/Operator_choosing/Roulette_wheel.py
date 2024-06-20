'''
This function chooses operators based on the roulette wheel principle:
Operators are assigned weights
Operator is chosen based on relative weight
These weights are updated based on scores of operator this iteration
'''
import random

def operator_choice(weights, operator_dict):
    probs = [weights[i] / sum(weights) for i in range(len(weights))]
    idx = random.choices(list(range(len(weights))), weights=probs, k=1)[0]
    return operator_dict[idx]

def weights_update(decision, chosen_operators, operator_dict, weights, scores, theta):
    '''
    decision = int
    chosen_operators = ('Destroy', 'Repair')
    operator_dict = [['Destroy'], ['Repair']]
    weights = [weights destroy, weights repair]
    Score[0] = New global best
    Score[1] = Better than current
    Score[2] = Accepted
    Score[3] = Rejected
    '''
    idx_destroy = operator_dict[0].index(chosen_operators[0]) # Index of chosen destroy operator
    idx_repair = operator_dict[1].index(chosen_operators[1]) # Index of chosen repair operator
    weights[0][idx_destroy] = theta * weights[0][idx_destroy] + (1 - theta) * scores[decision] # Update weight destroy
    weights[1][idx_repair] = theta * weights[1][idx_repair] + (1 - theta) * scores[decision]  # Update weight repair
    return weights[0], weights[1]