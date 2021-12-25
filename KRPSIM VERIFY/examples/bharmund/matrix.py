from itertools import product
import numpy as np

def op_OR(A, B):
    if A == 0 and B == 0:
        return(0)
    return(1)

def op_XOR(A, B):
    if A == B:
        return(0)
    return(1)

def op_AND(A, B):
    if A == 1 and B == 1:
        return(1)
    return(0)

def op_neg(A):
    if A == 0:
        return(1)
    return(0)

def op_equiv(A, B):
    if (A == 0 and B == 0) or (A == 1 and B == 1):
        return(1)
    return(0)

def op_implication(A, B):
    if A == 1 and B == 0:
        return(0)
    return(1)

def op_rev_implication(A, B):
    if A == 0 and B == 1:
        return(0)
    return(1)

def choose_operation(A, B, op):
    if op == '+':
        return(op_AND(A, B))
    elif op == '|':
        return(op_OR(A, B))
    elif op == '^':
        return(op_XOR(A, B))
    elif op == '=>':
        return(op_implication(A, B))
    elif op == '<=':
        return(op_rev_implication(A, B))
    else:
        return(op_equiv(A, B))

def from_rpn(rule, vars):
    stack, result = [], []
    A, B = '', ''
    for i in rule:
        if i.isalpha():
            stack.append(vars[i])
        elif i == '!':
            A = stack.pop()
            result = 0 if A == 1 else 1
            stack.append(result)
        elif i in ["+", "|", "^", "=>", "<=", "<=>"]:
            B = stack.pop()
            A = stack.pop()
            result = choose_operation(A, B, i)
            stack.append(result)
    return(stack[0])

def get_binary_vars(vars, row):
    binary_vars = {}
    i = 0
    while i < len(vars):
        binary_vars.update({vars[i]: row[i]})
        i += 1
    return(binary_vars)

def calculate_rules(rpn_rules, vars, row):
    result = []
    binary_vars = get_binary_vars(vars, row)
    
    for rule in rpn_rules:
        res = from_rpn(rule, binary_vars)
        result.append(res)
    return 0 if (0 in result) else 1

def check_True_facts(row, facts, vars):
    for f in facts:
        i = 0
        while i < len(vars):
            if vars[i] == f:
                break
            i += 1
        if row[i] == 0:
            return(1)
    return(0)

def zero_next_var(priority_vars, result_vars, matrix, vars ):
    tmp_matrix = []
    for v in priority_vars:
        if result_vars[v] == 2:
            index = vars.index(v)
            for row in matrix:
                if row[index] == 0:
                    tmp_matrix.append(row)
                    break
            matrix = np.array(tmp_matrix)
            matrix_T = matrix.transpose()
    return matrix, matrix_T

def print_decision(dic, matrix):
    for q in dic['queries']:
        i = 0
        while i < len(dic['vars']):
            if dic['vars'][i] == q:
                break
            i += 1
        if len(matrix) == 0:
            print('Contradiction in rules!')
            exit()
        word = 'False' if matrix[0][i] == 0 else 'True'
        print(f'{q} is {word}')

def make_decision(dic, cnf):
    result_vars = {}
    cnf = sorted(cnf, key=sum)
    matrix = np.array(cnf)
    matrix_T = matrix.transpose()
    priority_vars = (list(dic["left_side"].difference(dic["right_side"])) + 
                    list(dic["left_side"].intersection(dic["right_side"])) +
	 	            list(dic["right_side"].difference(dic["left_side"])))
    vars = dic['vars']
    while True:
        i = 0
        while i < len(vars):
            num_of_variants = len(set(matrix_T[i]))
            result_vars.update({vars[i]: num_of_variants})
            i += 1
        if sum(result_vars.values()) == len(vars):
            break
        else:
            matrix, matrix_T = zero_next_var(priority_vars, result_vars, matrix, vars)
    print_decision(dic, matrix)

def cnf(dic):
    matrix = []
    for row in product('01', repeat=len(dic['vars'])):
        row = [int(item) for item in row]
        if dic['facts']:
            if check_True_facts(row, dic['facts'], dic['vars']) == 1:
                continue
        result = calculate_rules(dic['rpn_rules'], dic['vars'], row) 
        if result == 1:
            matrix.append(row)
    make_decision(dic, matrix)
 