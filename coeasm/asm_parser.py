from coeasm.util import is_harvestable, harvest
from coeasm.opcode_parser import OpcodeException


DEFAULT_SIZE = 512


class AssemblerException(Exception):
    def __init__(self, line_number, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line_number = line_number

    def __str__(self):
        return '{} (line {})'.format(super().__str__(), self.line_number)


class InstructionList(object):
    def __init__(self, opcode_parser, size=DEFAULT_SIZE):
        self.opcode_parser = opcode_parser
        self.size = size
        self.data = [-1] * size

    def assert_bounds(self, idx, line_number):
        # Check we didn't jump out of bounds
        if idx >= self.size:
            raise AssemblerException(line_number, 'Index reached invalid memory location: {}'.format(idx))

    def assert_open(self, idx, line_number):
        self.assert_bounds(idx, line_number)
        # Check to make sure we aren't stomping on other data
        if self.data[idx] != -1:
            raise AssemblerException(line_number, 'Memory overwrite detected. Location: {}'.format(idx))

    def to_file(self, filename):
        with open(filename, 'w') as o:
            o.write('MEMORY_INITIALIZATION_RADIX=2;\nMEMORY_INITIALIZATION_VECTOR=')
            for instruction in self.data:
                if instruction < 0:
                    instruction = self.opcode_parser.opcodes['NOP'][0]
                o.write('\n{:08b}'.format(instruction))
            o.write(';\n')

    @classmethod
    def from_file(cls, filename, opcode_parser, size=DEFAULT_SIZE):
        ret = cls(opcode_parser, size)
        idx = 0
        line_number = 0
        with open(filename, 'r') as r:
            for line in r:
                line_number += 1
                line = line.split('#')[0].strip()
                if not line:
                    continue
                tokens = line.split(' ')
                subject = tokens[0].strip()

                if subject[0] == '@':
                    idx = harvest(subject[1:])
                    ret.assert_bounds(idx, line_number)
                else:
                    if is_harvestable(subject):
                        ret.assert_open(idx, line_number)
                        ret.data[idx] = (harvest(subject) & 0xFF)
                        idx += 1
                    else:
                        try:
                            instructions = ret.opcode_parser.parse_line(line)
                            for instruction in instructions:
                                ret.assert_open(idx, line_number)
                                ret.data[idx] = instruction
                                idx += 1
                        except OpcodeException as e:
                            raise AssemblerException(line_number, str(e))
        return ret
