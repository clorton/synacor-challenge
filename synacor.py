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


class VM(object):

    def __init__(self, program=None):
        self._memory = np.zeros(32768, dtype=np.uint16)
        self._registers = np.zeros(8, dtype=np.uint16)
        self._stack = []
        self._ip = 0
        self._sp = 0

        if program is not None:
            self._memory[:len(program)] = program[:]

        return

    def inc_ip(self, count=1):
        self._ip += count
        self._ip %= 32768

        return

    def load_value(self, value):
        if value < 32768:
            pass
        elif value < 32776:
            value = self._registers[value - 32768]
        else:
            raise RuntimeError(f"Argument {value} is out of range.")
        return value

    def store_value(self, value, address):
        if address < 32768:
            self._memory[address] = value
        elif address < 32776:
            self._registers[address - 32768] = value
        else:
            raise RuntimeError(f"Address argument {address} is out of range.")
        return

    def _halt(self):
        self.inc_ip()
        return False

    def _set(self):
        """set register <a> to the value of <b>"""
        self.store_value(self._memory[self._ip+2], self._memory[self._ip+1])
        self.inc_ip(3)
        return True

    def _push(self):
        """push <a> onto the stack"""
        value = self.load_value(self._memory[self._ip+1])
        self._stack.append(value)
        self.inc_ip(2)  # opcode, value
        return True

    def _pop(self):
        """remove the top element from the stack and write it into <a>; empty stack = error"""
        if self._stack:
            value = self._stack.pop()
            self.store_value(value, self._memory[self._ip+1])
        else:
            raise RuntimeError("Cannot pop from empty stack.")
        self.inc_ip(2)  # opcode, value
        return True

    def _eq(self):
        """set <a> to 1 if <b> is equal to <c>; set it to 0 otherwise"""
        b = self.load_value(self._memory[self._ip+2])
        c = self.load_value(self._memory[self._ip+3])
        self.store_value(1 if b == c else 0, self._memory[self._ip+1])
        self.inc_ip(4)  # opcode, address, op1, op2
        return True

    def _gt(self):
        """set <a> to 1 if <b> is greater than <c>; set it to 0 otherwise"""
        b = self.load_value(self._memory[self._ip+2])
        c = self.load_value(self._memory[self._ip+3])
        self.store_value(1 if b > c else 0, self._memory[self._ip+1])
        self.inc_ip(4)  # opcode, address, op1, op2
        return True

    def _jmp(self):
        """jump to <a>"""
        self._ip = self.load_value(self._memory[self._ip+1])
        return True

    def _jt(self):
        """if <a> is nonzero, jump to <b>"""
        if self.load_value(self._memory[self._ip+1]) != 0:
            self._ip = self.load_value(self._memory[self._ip+2])
        else:
            self.inc_ip(3)  # opcode, test, destination
        return True

    def _jf(self):
        """if <a> is zero, jump to <b>"""
        if self.load_value(self._memory[self._ip+1]) == 0:
            self._ip = self.load_value(self._memory[self._ip+2])
        else:
            self.inc_ip(3)  # opcode, test, destination
        return True

    def _add(self):
        """assign into <a> the sum of <b> and <c> (modulo 32768)"""
        b = self.load_value(self._memory[self._ip+2])
        c = self.load_value(self._memory[self._ip+3])
        result = (b + c) % 32768
        self.store_value(result, self._memory[self._ip+1])
        self.inc_ip(4)  # opcode, address, op1, op2
        return True

    def _mult(self):
        """store into <a> the product of <b> and <c> (modulo 32768)"""
        b = self.load_value(self._memory[self._ip+2])
        c = self.load_value(self._memory[self._ip+3])
        result = np.uint16((int(b) * int(c)) % 32768)
        self.store_value(result, self._memory[self._ip+1])
        self.inc_ip(4)  # opcode, address, op1, op2
        return True

    def _mod(self):
        """store into <a> the remainder of <b> divided by <c>"""
        b = self.load_value(self._memory[self._ip+2])
        c = self.load_value(self._memory[self._ip+3])
        self.store_value(b % c, self._memory[self._ip+1])
        self.inc_ip(4)  # opcode, address, op1, op2
        return True

    def _and(self):
        """stores into <a> the bitwise and of <b> and <c>"""
        b = self.load_value(self._memory[self._ip+2])
        c = self.load_value(self._memory[self._ip+3])
        self.store_value(b & c, self._memory[self._ip+1])
        self.inc_ip(4)  # opcode, address, op1, op2
        return True

    def _or(self):
        """stores into <a> the bitwise or of <b> and <c>"""
        b = self.load_value(self._memory[self._ip+2])
        c = self.load_value(self._memory[self._ip+3])
        self.store_value(b | c, self._memory[self._ip+1])
        self.inc_ip(4)  # opcode, address, op1, op2
        return True

    def _not(self):
        """stores 15-bit bitwise inverse of <b> in <a>"""
        b = self.load_value(self._memory[self._ip+2])
        self.store_value(b ^ 0x7FFF, self._memory[self._ip+1])
        self.inc_ip(3)  # opcode, address, op1
        return True

    def _rmem(self):
        """read memory at address <b> and write it to <a>"""
        a = self._memory[self._ip+1]
        b = self.load_value(self._memory[self._ip+2])
        self.store_value(self._memory[b], a)
        self.inc_ip(3)  # opcode, a, b
        return True

    def _wmem(self):
        """write the value from <b> into memory at address <a>"""
        a = self.load_value(self._memory[self._ip+1])
        b = self.load_value(self._memory[self._ip+2])
        self._memory[a] = b
        self.inc_ip(3)  # opcode, a, b
        return True

    def _call(self):
        """write the address of the next instruction to the stack and jump to <a>"""
        self._stack.append(self._ip+2)
        a = self.load_value(self._memory[self._ip+1])
        self._ip = a
        return True

    def _ret(self):
        """remove the top element from the stack and jump to it; empty stack = halt"""
        proceed = True
        if self._stack:
            self._ip = self._stack.pop()
        else:
            proceed = False
        return proceed

    def _out(self):
        print(f"{chr(self.load_value(self._memory[self._ip+1]))}", end="")
        self.inc_ip(2)
        return True

    def _in(self):
        return True

    def _noop(self):
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
            if not VM.OPCODES[operation](self):
                break

        return


def main():

    program = np.fromfile('challenge.bin', dtype=np.uint16)

    computer = VM(program)
    computer.run()

    return


if __name__ == "__main__":
    main()
