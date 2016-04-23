from coeasm.util import is_harvestable, harvest


class OpcodeException(Exception):
    pass


class OpcodeParser(object):
    """
    opcodes is a dictionary of key, (rep, narg, addr) pairs, where:
        key - Name of the opcode.  LOAD, STOR, CLR, etc
        rep - decimal representation of the value (must be less than 256)
        narg - Integer number of required arguments
        addr - Boolean indicating that the instruction is followed by an 8 bit address
    """
    def __init__(self, opcodes):
        self.opcodes = opcodes

    def instr_lookup(self, instruction):
        for opcode, (rep, narg, has_addr) in self.opcodes.items():
            if (instruction & 0xFC) == (rep & 0xFC):
                return opcode, rep, narg, has_addr
        return str(instruction), instruction, 0, 0

    def parse_line(self, line):
        ret = []

        tokens = line.split(' ')
        opcode = tokens[0].strip().upper()
        if opcode not in self.opcodes:
            raise OpcodeException('Undefined opcode: {}'.format(opcode))

        rep, narg, addr = self.opcodes[opcode]
        ret.append(rep)
        args = [arg for arg in tokens[1:] if arg.strip()]
        if len(args) > narg:
            raise OpcodeException('"{}" had too many arguments: {}'.format(line, len(args)))
        if len(args) < narg:
            raise OpcodeException('"{}" did not have enough arguments: {}'.format(line, len(args)))

        for arg in args:
            arg = arg.strip(', ')
            if arg == 'A':
                continue
            elif arg == 'B':
                ret[0] += 1
            elif is_harvestable(arg):
                if addr:
                    tmp = harvest(arg)
                    if tmp & 0x100:
                        ret[0] += 2
                    ret.append(tmp & 0xFF)
                else:
                    if harvest(arg):
                        ret[0] += 2
            else:
                raise OpcodeException('"{}" was not recognized as an argument'.format(arg))
        return ret

    @classmethod
    def from_file(cls, filename):
        opcodes = {}

        with open(filename, 'r') as f:
            for line in f:
                line = line.split('#')[0].strip()
                if not line:
                    continue
                tokens = line.split(',')

                if len(tokens) > 1:
                    rep = harvest(tokens[1].strip())
                else:
                    rep = 0

                if len(tokens) > 2:
                    narg = harvest(tokens[2].strip())
                else:
                    narg = 0

                if len(tokens) > 3:
                    addr = bool(tokens[3].strip())
                else:
                    addr = False

                opcodes[tokens[0].strip()] = (rep, narg, addr)

        return cls(opcodes)
