import sys
import polska
import matrix
import parse

def main():
    if len(sys.argv) != 2:
        print('Usage: python3 expert_system.py file') 
        exit()
    try:
        fd = open(sys.argv[1])
    except IOError as e:
        exit(e)
    dic = parse.parse_file(fd)
    dic_rpn = polska.get_rpn(dic)
    matrix.cnf(dic_rpn)

if __name__ == '__main__':
    main()