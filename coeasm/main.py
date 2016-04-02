import coeasm
import argparse
import os
import sys

from coeasm.opcode_parser import OpcodeParser
from coeasm.asm_parser import InstructionList, AssemblerException


def main():
    # Parse the CL arguments
    parser = argparse.ArgumentParser(prog=coeasm.CLI, description=coeasm.DESCRIPTION)
    parser.add_argument('FILE', help='File containing assembly')
    parser.add_argument('-o', '--output', dest='output', default=None,
                        help='Output filename')
    parser.add_argument('-s', '--shellfish', dest='opcode_file', default='opcodes.txt',
                        help='File containing opcode definitions')
    parser.add_argument('-b', '--bytes', dest='byte_length', default='512', type=int,
                        help='Number of available bytes')
    parser.add_argument('-v', '--version', action='version', version=coeasm.__version__)
    args = parser.parse_args()

    if os.path.isfile(args.FILE):
        infile = args.FILE
    else:
        print('{} not found.'.format(args.FILE), file=sys.stderr)
        sys.exit(1)

    if os.path.isfile(args.opcode_file):
        op_parser = OpcodeParser.from_file(args.opcode_file)
        print('Registered {} opcodes'.format(len(op_parser.opcodes)))
    else:
        print('Missing opcode definitions: {}'.format(args.opcode_file), file=sys.stderr)
        sys.exit(1)

    if args.output:
        outfile = args.output
    else:
        outfile = os.path.basename(args.FILE).split('.')[0] + '.coe'

    print('Processing: {}'.format(infile))
    try:
        IL = InstructionList.from_file(infile, op_parser, args.byte_length)
    except AssemblerException as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    print('Writing: {}'.format(outfile))
    IL.to_file(outfile)
