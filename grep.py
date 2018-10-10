import argparse
import sys
import re


def output(line):
    print(line)


def check(line, params):
    # check invert / ignore_case
    if params.invert:
        if params.ignore_case:
            return not re.search(params.pattern.lower(), line.lower())
        else:
            return not re.search(params.pattern, line)
    else:
        if params.ignore_case:
            return re.search(params.pattern.lower(), line.lower())
        else:
            return re.search(params.pattern, line)


def grep(lines, params):
    num = 1
    k = 0
    buffer = []

    # regex
    params.pattern = params.pattern.replace('?', '.')
    params.pattern = params.pattern.replace('*', r'\w*')

    if params.context > params.before_context:
        params.before_context = params.context
    if params.context > params.after_context:
        params.after_context = params.context

    if params.count:
        n = 0
        for i in range(len(lines)):
            if check(lines[i], params):
                n += 1
        output(str(n))
        return

    for i in range(len(lines)):
        flag = check(lines[i], params)
        if params.before_context:
            if len(buffer) > params.before_context:
                del buffer[0]
            if flag:
                num -= len(buffer) + 1
                for line in buffer:
                    num += 1
                    if params.line_number:
                        output(str(num) + '-' + line)
                    else:
                        output(line)
                num += 1
                buffer.clear()
            else:
                buffer.append(lines[i])

        if params.after_context:
            if flag:
                k = params.after_context
            else:
                if k > 0:
                    if params.line_number:
                        output(str(num) + '-' + lines[i])
                    else:
                        output(lines[i])
                    k -= 1
                    buffer.clear()

        if flag:
            if params.line_number:
                output(str(num) + ':' + lines[i])
            else:
                output(lines[i])
        num += 1

def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False, help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()