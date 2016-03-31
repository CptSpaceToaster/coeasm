import coeasm
import argparse
import os
import sys


def register_opcodes(filename):
    ret = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line[0] in '#':
                continue
            tokens = line.split(',')
            ret[tokens[0].strip()] = harvest(tokens[1].strip())
    return ret


def harvest(digit_str):
    if digit_str[0] == 'b':
        assert digit_str[1:].isdigit()
        return int(digit_str[1:], 2)
    elif digit_str[0] == 'x':
        assert digit_str[1:].isdigit()
        return int(digit_str[1:], 16)
    else:
        assert digit_str.isdigit()
        return int(digit_str)


def main():
    # Parse the CL arguments
    parser = argparse.ArgumentParser(prog=coeasm.CLI, description=coeasm.DESCRIPTION)
    parser.add_argument('FILE', help='File containing assembly')
    parser.add_argument('-o', '--output', dest='output', default=None,
                        help='Output filename')
    parser.add_argument('-s', '--shellfish', dest='opcode_file', default='opcodes.txt',
                        help='File contain opcode definitions')
    parser.add_argument('-b', '--bytes', dest='byte_length', default='512', type=int,
                        help='Number of available bytes')
    parser.add_argument('-v', '--version', action='version', version=coeasm.__version__)
    args = parser.parse_args()

    if os.path.isfile(args.FILE):
        infile = args.FILE
    else:
        print('Error: {0} not found.'.format(args.FILE))
        sys.exit(1)

    if os.path.isfile(args.opcode_file):
        opcodes = register_opcodes(args.opcode_file)
        print('Registered {0} opcodes'.format(len(opcodes)))
    else:
        print('Error: Missing opcode definitions: {0}'.format(args.opcode_file))
        sys.exit(1)

    if args.output:
        outfile = args.output
    else:
        outfile = os.path.basename(args.FILE).split('.')[0] + '.coe'

    coe_data = [(opcodes['NOP'], 0)] * 512
    idx = 0
    line_number = 0

    print('Processing: {}'.format(infile))
    with open(infile, 'r') as r:
        for line in r:
            line_number += 1
            line = line.strip()
            if not line or line[0] in '#':
                continue

            tokens = line.split(' ')
            token = tokens[0].strip()
            if token[0] == '@':
                idx = harvest(token[1:])
            elif token[0] in 'bx0123456789':
                coe_data[idx] = (harvest(token), line_number)
                idx += 1
            elif token.upper() in opcodes:
                offset = 1
                coe_data[idx] = (opcodes[token.upper()], line_number)
                if len(token) > 1:
                    for arg in tokens[1:]:
                        arg = arg.strip(', ')
                        if not arg:
                            continue
                        if arg[0] == '#':
                            break
                        if arg == 'B':
                            coe_data[idx] = (opcodes[token.upper()]+1, line_number)

                        if arg[0] in 'bx0123456789':
                            coe_data[idx+1] = (harvest(arg), line_number)
                            offset = 2
                    idx += offset

    print('Writing: {}'.format(outfile))
    with open(outfile, 'w') as o:
        o.write('MEMORY_INITIALIZATION_RADIX=2;\nMEMORY_INITIALIZATION_VECTOR=')
        for (i, line_number) in coe_data:
            if i > 255 or i < 0:
                print('Error: opcode out of range: {0}\n  line:{1}'.format(i, line_number))
                sys.exit(1)
            o.write('\n{:08b}'.format(i))
        o.write(';\n')
