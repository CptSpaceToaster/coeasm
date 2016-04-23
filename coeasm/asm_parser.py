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

    def to_vhdl(self, struct_name, rev_instrs=['STOR']):
        print('type t_{} is array(0 to {}) of std_logic_vector(7 downto 0);'.format(struct_name, self.size-1))
        print('signal {} : t_{} := ('.format(struct_name, struct_name))

        idx = 0
        while(idx < self.size):
            instruction = self.data[idx]
            if instruction < 0:
                idx += 1
                continue

            opcode, rep, nargs, has_addr = self.opcode_parser.instr_lookup(self.data[idx])
            print('    {:<7} => "{:08b}",    -- {:4s}'.format(idx, self.data[idx], opcode), end='')

            reg = ''
            if bool(self.data[idx] & 0x01):
                reg = 'B'
            else:
                reg = 'A'
            addr = ((self.data[idx] & 0x02) << 7) + self.data[idx+1]
            port = ((self.data[idx] & 0x02) >> 1)

            if has_addr:
                idx += 2
                if nargs == 2:
                    if opcode in rev_instrs:
                        print(' {}, {}'.format(reg, addr))
                    else:
                        print(' {}, {}'.format(addr, reg))
                elif nargs == 1:
                    print(' {}'.format(addr))
                else:
                    raise AssemblerException('Instruction has an address, but an unrecognized number of arguments: {}'.format(nargs))
                print('    {:<7} => "{:08b}",'.format(idx-1, self.data[idx-1]))
            else:
                idx += 1
                if nargs == 2:
                    if opcode in rev_instrs:
                        print(' {}, {}'.format(reg, port))
                    else:
                        print(' {}, {}'.format(port, reg))
                elif nargs == 1:
                    print(' {}'.format(reg))
                else:
                    print('')

        print('    others  => "{:08b}"     -- all other memory locations set to NOP instr\n);'.format(self.opcode_parser.opcodes['NOP'][0]))

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
