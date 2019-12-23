#!/usr/bin/env python3

import numpy as np
from enum import IntEnum


class OpCode(IntEnum):

    HALT = 0
    SET = 1
    PUSH = 2
    POP = 3
    EQ = 4
    GT = 5
    JMP = 6
    JT = 7
    JF = 8
    ADD = 9
    MULT = 10
    MOD = 11
    AND = 12
    OR = 13
    NOT = 14
    RMEM = 15
    WMEM = 16
    CALL = 17
    RET = 18
    OUT = 19
    IN = 20
    NOOP = 21


MEM_SIZE = 32768
REG_COUNT = 8
MAX_LITERAL = 32767
MAX_REGISTER = 32775


class VM(object):

    def __init__(self, program=None, trace=False):
        self._memory = np.zeros(MEM_SIZE, dtype=np.uint16)
        self._registers = np.zeros(REG_COUNT, dtype=np.uint16)
        self._stack = []
        self._ip = 0
        self._sp = 0
        self._trace = trace

        if program is not None:
            self._memory[:len(program)] = program[:]

        return

    def log(self, msg):
        if self._trace:
            print(msg)

        return

    def set_ip(self, ip):
        if ip < MEM_SIZE:
            self._ip = ip
        else:
            # self._ip = ip % MEM_SIZE
            raise RuntimeError(f"New ip {ip} out of range.")

        return

    def inc_ip(self, count=1):
        self.set_ip(self._ip + count)

        return

    def load_value(self, value):
        if value <= MAX_LITERAL:
            pass
        elif value <= MAX_REGISTER:
            value = self._registers[value - 32768]
        else:
            raise RuntimeError(f"Argument {value} is out of range.")
        return value

    def store_value(self, value, address):
        if address < MEM_SIZE:
            self._memory[address] = value
        elif address <= MAX_REGISTER:
            self._registers[address - 32768] = value
        else:
            raise RuntimeError(f"Address argument {address} is out of range.")
        return

    def _halt(self):
        self.inc_ip()
        return False

    def _arg_a(self):
        return self._memory[self._ip+1]

    def _arg_b(self):
        return self._memory[self._ip+2]

    def _arg_c(self):
        return self._memory[self._ip+3]

    def _set(self):
        """set register <a> to the value of <b>"""
        a = self._arg_a()
        b = self._arg_b()
        self.log(f"SET {a} <- {b}")
        self.store_value(b, a)
        self.inc_ip(3)  # opcode, reg, value
        return True

    def _push(self):
        """push <a> onto the stack"""
        a = self._arg_a()
        value = self.load_value(a)
        self.log(f"PUSH {a} = {value}")
        self._stack.append(value)
        self.inc_ip(2)  # opcode, value
        return True

    def _pop(self):
        """remove the top element from the stack and write it into <a>; empty stack = error"""
        if self._stack:
            a = self._arg_a()
            value = self._stack.pop()
            self.log(f"POP => {a} <- {value}")
            self.store_value(value, a)
        else:
            raise RuntimeError("Cannot pop from empty stack.")
        self.inc_ip(2)  # opcode, value
        return True

    def _eq(self):
        """set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise"""
        a = self._arg_a()
        b = self.load_value(self._arg_b())
        c = self.load_value(self._arg_c())
        value = 1 if b == c else 0
        self.log(f"SET {a} <- {b} == {c} ({value})")
        self.store_value(value, a)
        self.inc_ip(4)  # opcode, address, op1, op2
        return True

    def _gt(self):
        """set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise"""
        a = self._arg_a()
        b = self.load_value(self._arg_b())
        c = self.load_value(self._arg_c())
        value = 1 if b > c else 0
        self.log(f"GT {a} <- {b} > {c} ({value})")
        self.store_value(value, a)
        self.inc_ip(4)  # opcode, address, op1, op2
        return True

    def _jmp(self):
        """jump to <a>"""
        a = self._arg_a()
        value = self.load_value(a)
        self.log(f"JMP ip <- {a} ({value})")
        self.set_ip(value)
        return True

    def _jt(self):
        """if <a> is nonzero, jump to <b>"""
        a = self._arg_a()
        value_a = self.load_value(a)
        if value_a != 0:
            b = self._arg_b()
            value_b = self.load_value(b)
            self.log(f"JT ip <- {b} ({value_b}) if {a} ({value_a}) != 0")
            self.set_ip(value_b)
        else:
            self.inc_ip(3)  # opcode, test, destination
        return True

    def _jf(self):
        """if <a> is zero, jump to <b>"""
        a = self._arg_a()
        value_a = self.load_value(a)
        if value_a == 0:
            b = self._arg_b()
            value_b = self.load_value(b)
            self.log(f"JF ip <- {b} ({value_b}) if {a} ({value_a}) == 0")
            self.set_ip(value_b)
        else:
            self.inc_ip(3)  # opcode, test, destination
        return True

    def _add(self):
        """assign into <a> the sum of <b> and <c> (modulo 32768)"""
        a = self._arg_a()
        b = self.load_value(self._arg_b())
        c = self.load_value(self._arg_c())
        result = (b + c) % 32768
        self.log(f"ADD {a} <- {b} + {c} ({result}) # % 32768")
        self.store_value(result, a)
        self.inc_ip(4)  # opcode, address, op1, op2
        return True

    def _mult(self):
        """store into <a> the product of <b> and <c> (modulo 32768)"""
        a = self._arg_a()
        b = self.load_value(self._arg_b())
        c = self.load_value(self._arg_c())
        result = np.uint16((int(b) * int(c)) % 32768)
        self.log(f"MULT {a} <- {b} * {c} ({result}) # % 32768")
        self.store_value(result, a)
        self.inc_ip(4)  # opcode, address, op1, op2
        return True

    def _mod(self):
        """store into <a> the remainder of <b> divided by <c>"""
        a = self._arg_a()
        b = self.load_value(self._arg_b())
        c = self.load_value(self._arg_c())
        value = b % c
        self.log(f"MOD {a} <- {b} % {c} ({value})")
        self.store_value(value, a)
        self.inc_ip(4)  # opcode, address, op1, op2
        return True

    def _and(self):
        """stores into <a> the bitwise and of <b> and <c>"""
        a = self._arg_a()
        b = self.load_value(self._arg_b())
        c = self.load_value(self._arg_c())
        value = b & c
        self.log(f"AND {a} <- {b} & {c} ({value})")
        self.store_value(value, a)
        self.inc_ip(4)  # opcode, address, op1, op2
        return True

    def _or(self):
        """stores into <a> the bitwise or of <b> and <c>"""
        a = self._arg_a()
        b = self.load_value(self._arg_b())
        c = self.load_value(self._arg_c())
        value = b | c
        self.log(f"OR {a} <- {b} | {c} ({value})")
        self.store_value(b | c, a)
        self.inc_ip(4)  # opcode, address, op1, op2
        return True

    def _not(self):
        """stores 15-bit bitwise inverse of <b> in <a>"""
        a = self._arg_a()
        b = self.load_value(self._arg_b())
        value = b ^ MAX_LITERAL
        self.log(f"NOT {a} <- {b} ^ {MAX_LITERAL} ({value})")
        self.store_value(value, a)
        self.inc_ip(3)  # opcode, address, op1
        return True

    def _rmem(self):
        """read memory at address <b> and write it to <a>"""
        a = self._arg_a()
        b = self.load_value(self._arg_b())
        value = self._memory[b]
        self.log(f"RMEM {a} <- *{b} ({value})")
        self.store_value(value, a)
        self.inc_ip(3)  # opcode, a, b
        return True

    def _wmem(self):
        """write the value from <b> into memory at address <a>"""
        a = self.load_value(self._arg_a())
        b = self.load_value(self._arg_b())
        self.log(f"WMEM *{a} <- {b}")
        self._memory[a] = b
        self.inc_ip(3)  # opcode, a, b
        return True

    def _call(self):
        """write the address of the next instruction to the stack and jump to <a>"""
        self._stack.append(self._ip+2)
        a = self.load_value(self._arg_a())
        self.log(f"CALL ip <- {a}")
        self.set_ip(a)
        return True

    def _ret(self):
        """remove the top element from the stack and jump to it; empty stack = halt"""
        proceed = True
        if self._stack:
            ip = self._stack.pop()
            self.log(f"RET ip <- {ip}")
            self.set_ip(ip)
        else:
            proceed = False
        return proceed

    def _out(self):
        print(f"{chr(self.load_value(self._arg_a()))}", end="")
        self.inc_ip(2)
        return True

    def _in(self):
        return True

    def _noop(self):
        self.log("NOOP")
        self.inc_ip()
        return True

    OPCODES = {
        OpCode.HALT: _halt,
        OpCode.SET: _set,
        OpCode.PUSH: _push,
        OpCode.POP: _pop,
        OpCode.EQ: _eq,
        OpCode.GT: _gt,
        OpCode.JMP: _jmp,
        OpCode.JT: _jt,
        OpCode.JF: _jf,
        OpCode.ADD: _add,
        OpCode.MULT: _mult,
        OpCode.MOD: _mod,
        OpCode.AND: _and,
        OpCode.OR: _or,
        OpCode.NOT: _not,
        OpCode.RMEM: _rmem,
        OpCode.WMEM: _wmem,
        OpCode.CALL: _call,
        OpCode.RET: _ret,
        OpCode.OUT: _out,
        # OpCode.IN: _in,
        OpCode.NOOP: _noop
    }

    def run(self):

        operation = None
        while operation != OpCode.HALT:
            operation = OpCode(self._memory[self._ip])
            self.log(f"{self._ip:04X}: {operation}")
            if not VM.OPCODES[operation](self):
                break

        return


def main():

    program = np.fromfile('challenge.bin', dtype=np.uint16)

    computer = VM(program, trace=True)
    computer.run()

    return


if __name__ == "__main__":
    main()
