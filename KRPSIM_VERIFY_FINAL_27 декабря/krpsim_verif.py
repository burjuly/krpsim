import sys
import re

def get_stocks_from_processes(processes):
    stocks_in_processes = []
    i = 0
    for k in processes:
        tmp1 = re.split(';', processes[k][0])
        tmp2 = re.split(';', processes[k][1])
        tmp = tmp1 + tmp2
        for str in tmp:
            str = re.split(':', str)[0]
            if len(str) == 0:
                continue
            stocks_in_processes.append(str)
    return(set(stocks_in_processes))

def del_resource_duplicates(stocks_in_processes, stocks):
    res = []
    for stock in stocks:
        res.append(stock[0])
    return (stocks_in_processes.difference(set(res)))

def print_description_config_file(stocks, processes, optimize):
    stocks_in_processes = get_stocks_from_processes(processes)
    res_in_processes = del_resource_duplicates(stocks_in_processes, stocks)
    print('STOCKS IN PROCESSES')
    print(res_in_processes)
    count_prosesses = len(processes)
    count_stocks = len(stocks) + len(res_in_processes)
    #if 'time' in optimize: #не считаем time как ресурс
    #    count_stocks -= 1
    count_optimize = len(optimize)
    print('### Description of config file:')
    print(f'* Number of processes: {count_prosesses}')
    print(f'* Number of stocks: {count_stocks}')
    print(f'* Need to optimize: {count_optimize}')
    print('### Stocks:')
    for s in stocks:
        print(f'* {s[0]} : {s[1]}')
    for r in res_in_processes:
        print(f'* {r} : 0')
    print('### Processes:')
    for p in processes:
        print(f'* {p} : ({processes[p][0]}) : ({processes[p][1]}) : {processes[p][2]}')
    print(f'### Optimizing: ')
    for o in optimize:
        print(f'* {o}')

def are_there_enough_stocks(progress, stock_counter, processes):
    need_stock, ready_stock = {}, {}
    resources_consumed = re.split(';', processes[progress[1]][0])
    resources_consumed.append(processes[progress[1]][2])

    for  resource in resources_consumed: #Делаем словарь: {ресурс : кол-во}
        resource = re.split(':',  resource)
        if len(resource) == 1: # это nb_cycle
            need_stock.update({'cycle': int(resource[0]) })
            continue
        need_stock.update({  resource[0]: int(resource[1]) })

    # Проверяем хватит ли ресурсов и вычитаем их, если хватает
    for i in need_stock:
        if i == 'cycle':
            # current_cycle - previous_cycle должен быть не меньше чем nb_cycle предыдущего процесса
            current_cycle = progress[0]
            previous_cycle = stock_counter['previous_cycle']
            required_cycles = stock_counter['required cycles']
            #print(f'CUURENT {current_cycle}')
            #print(f'PREVIOUS {previous_cycle}')
            #print(f'REQUIED {required_cycles}')
            if (current_cycle - previous_cycle < required_cycles) and current_cycle != 0:
                    print('There are not enough resources. Perhaps not enough has been produced yet.')
                    exit()
            stock_counter['previous_cycle'] = progress[0]
            stock_counter['required cycles'] = int(processes[progress[1]][2])
            continue
        if need_stock[i] > stock_counter[i]:
            print(f'An error was detected. Insufficient resources: {i} for the process ')
            exit()
        else:
            stock_counter[i] = stock_counter[i] - need_stock[i]
    
    # Добавляем к ресурсам произведенное
    resources_produced = re.split(';', processes[progress[1]][1])
    for  resource in  resources_produced:
        resource = re.split(':',  resource)
        ready_stock.update({  resource[0]: int( resource[1]) })
    for i in ready_stock:
        if i in stock_counter:
            stock_counter[i] = stock_counter[i] + ready_stock[i]
        else:
            stock_counter[i] = ready_stock[i]
    return stock_counter

def are_processes_exist_config(processes, progress):
    if len(processes) == 0 or len(progress) == 0:
        return
    progress_set, processes_set = [], []
    for prog in progress:
        progress_set.append(prog[1])
    for proc in processes:
        processes_set.append(proc)
    progress_set = set(progress_set)
    processes_set = set(processes_set)
    result = progress_set.difference(processes_set)
    if result:
        print('These processes were not found in confog file: ')
        for i in result:
            print(i, end='')
        exit()

def check(stocks, processes, optimize, progress, result):
    cycle_counter = 0
    stock_counter = {}
    are_processes_exist_config(processes, progress)

    for s in stocks: #начальные ресурсы
        stock_counter.update({ s[0]: int(s[1]) })
    stock_counter.update({ 'previous_cycle': 0, 'required cycles': 0 })

    for p in progress:
        print(f'Check progress: {p[0]} : {p[1]} ')
        #check_cycle(p, cycle_counter, processes)
        stock_counter = are_there_enough_stocks(p, stock_counter, processes)
    for res in result:
        print(f'Check result: {res[0]} => {res[1]} ')
        if res[1] != stock_counter[res[0]]:
            print(f'Error was detected. Total resource amount *{res[0]}* is incorrect - {res[1]}.')
            print(f'Correct amount of resource *{res[0]}* is {stock_counter[res[0]]}.')
            exit()

def parse_config_file(fd):
    stocks = []
    processes, stock_counter = {}, {}
    while True:
        line = fd.readline()
        if line == '':
            fd.close()
            break
        line = line[:-1]
        if line[0] == '#': 
            continue
        if len(re.findall(':', line)) == 1: 
            line = re.split(':', line)
            if line[0] == 'optimize':
                line = line[1][1:-1]
                line = re.split(';', line)
                optimize = line
            else:
                stocks.append(line)
        else:      
            line = re.split('[)][:][(]|[:][(]|[)][:]', line)
            processes.update({line[0]: [line[1], line[2], line[3]]})
    return stocks, processes, optimize
    
def parse_log_file(fd):
    progress, result = [], []
    flag = 0
    while True:
        line = fd.readline()
        if line == '':
            fd.close()
            break
        line = line[:-1]
        if line[0] == '#': 
            continue
        if 'Stock' in line:
            flag = 1
            continue
        elif len(re.findall(':', line)) == 1:
            line = re.split(':', line)
            progress.append([int(line[0]), line[1]])
        elif flag == 1:
            line = re.sub(r'\s+', '', line)
            line = re.split('=>', line)
            result.append([ line[0], int(line[1]) ])
    return progress, result

def main():
    if len(sys.argv) != 3:
        print(f'Usage: python3 krpsim_verif config_file log_file')
        exit()
    try:
        fd1 = open(sys.argv[1])
    except:
        print('Unable to open config file')
        exit()
    try:
        fd2 = open(sys.argv[2])
    except:
        print('Unable to open log file')
        exit()   
    stocks, processes, optimize = parse_config_file(fd1)
    print_description_config_file(stocks, processes, optimize)
    progress, result = parse_log_file(fd2)
    check(stocks, processes, optimize, progress, result)
    print('Verification completed. No errors detected.')

if __name__ == '__main__':
    main()