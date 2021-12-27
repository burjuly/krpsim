OPERATIONS = {
    "!": 6,
    "+": 5,
    "|": 4,
    "^": 3,
    "=>": 2,
    "<=": 2,
    "<=>": 1 
    }

def get_rpn(dic):
    rpn_rules = []
    i = 0
    while i < len(dic['rules']):
        rpn_rule = polska(dic['rules'][i])
        rpn_rules.append(rpn_rule)
        i += 1
    dic['rpn_rules'] = rpn_rules 
    return(dic)

def polska(str):
    stack=[]
    output_str=[]
    i = 0
    while i < len(str):
        token = str[i]
        if token.isalpha():
            output_str.append(token)
        elif token == '(':
            stack.append(token)
        elif str[i] == ')':
            while stack[-1] != '(':
                output_str.append(stack.pop())
            stack.pop()
        elif token in OPERATIONS:
            while len(stack):
                if stack[-1] == '(':
                    break
                elif OPERATIONS[stack[-1]] >= OPERATIONS[token]:
                    output_str.append(stack.pop())
                else:
                    break
            stack.append(token)
        i += 1
    while len(stack):
        output_str.append(stack.pop())    
    return(output_str)
