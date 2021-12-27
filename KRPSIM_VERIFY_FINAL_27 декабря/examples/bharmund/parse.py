import re

def are_brackets_correct(rule):
    stack = []
    for i in rule:
        if i not in '()':
            continue
        elif i == '(':
            stack.append(i)
        else:
            if len(stack) == 0:
                return(False)
            brace = stack.pop()
    return True if (len(stack) == 0) else False
    
def get_tokens_from_rules(rule):
    result = []
    i = 0
    while i < len(rule):
        symbol = rule[i]
        if symbol.isalpha() or (symbol in ['!', '+', '|', '^', ')', '(']):
            result.append(symbol)
        elif symbol == '<':
            sub = re.findall(r'[<][=][>]?', rule[i:])
            if len(sub) == 0:
                print('Only =>, <=, <=>')
            else:
                if len(sub) != 1:
                    print('Too many =>, <=, <=>')
                else:
                    l = len(sub[0])
                    if l == 2:
                        result.append(sub[0])
                        i += 2
                    elif l == 3:
                        result.append(sub[0])
                        i += 3
                    continue
        elif symbol == '=':
            sub = re.findall(r'[=][>]', rule[i:])
            if len(sub) == 0:
                print('Mistake in =>')
            else:
                if len(sub) > 1:
                    print('Too many =>')
                    exit()
                else:
                    result.append(sub[0])
                i += 2
                continue
        i += 1
    return(result)

def parse_rules(rules):
    result = []
    for rule in rules:
        if are_brackets_correct(rule) == False:
            print('Incorrect brackets sequence')
        result.append(get_tokens_from_rules(rule))
    return(result)

def get_left_right_sides(rules):
    left_side, right_side = '', ''
    for rule in rules:
        flag = 0
        left, right = '', ''
        for sym in rule:
            if sym.isalpha() and flag == 0:
                left += sym
            elif sym.isalpha() and flag == 1:
                right += sym
            elif sym in ['=>', '<=>', '<=']:
                flag = 1
        if '<=' in rule:
            left, right = right, left
        left_side += left
        right_side += right
    return set(left_side), set(right_side)

def parse_file(fd):
    rules , facts, queries, vars = [], [], [], []
    while True:
        line = fd.readline()
        if line == '':
            break
        if re.match(r'\n+', line):
            continue
        line = re.sub(r'\s+', '', line)   
        if line[0] == '#':
            continue
        elif line[0] == '?':
            queries.append(line[1:])
        elif line[0] == '=':
            facts.append(line[1:])
        elif len(re.findall(r'[^A-Z=<>\?\(\)\+|!^]', line)) > 0:
            invalid_sym = re.findall(r'[^A-Z=<>\?\(\)\+|!^]', line)
            print(f'Invalid characters found: {invalid_sym }')
            exit()
        else:
            rules.append(line)
    rules = parse_rules(rules)
    left, right = get_left_right_sides(rules)
    vars = left.union(right)
    queries = list(queries[0])
    facts = list(facts[0])
    unknown_vars = (vars.union(set(queries))).difference(vars)
    vars = list(vars)
    vars.sort()

    dic = {'rules': rules,
            'facts': facts, 
            'queries': queries, 
            'vars': vars, 
            'unknown_vars': unknown_vars,
            'left_side': left,
            'right_side': right
            }
    return dic