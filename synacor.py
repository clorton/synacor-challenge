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
        self._memory = np.zeros(32768, dtype=np.int16)
        self._registers = np.zeros(8, dtype=np.int16)
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
        elif value < 32775:
            value = self._registers[value - 32768]
        else:
            raise RuntimeError(f"Argument {value} is out of range.")
        return value

    def store_value(self, value, address):
        self._memory[address] = value
        return

    def _halt(self):
        self.inc_ip()
        return

    def _set(self):

        return

    def _push(self):
        return

    def _pop(self):
        return

    def _eq(self):
        return

    def _gt(self):
        return

    def _jmp(self):
        self._ip = self.load_value(self._memory[self._ip+1])
        return

    def _jt(self):
        if self.load_value(self._memory[self._ip+1]) != 0:
            self._ip = self.load_value(self._memory[self._ip+2])
        else:
            self.inc_ip(3)  # opcode, test, destination
        return

    def _jf(self):
        if self.load_value(self._memory[self._ip+1]) == 0:
            self._ip = self.load_value(self._memory[self._ip+2])
        else:
            self.inc_ip(3)  # opcode, test, destination
        return

    def _add(self):
        return

    def _mult(self):
        return

    def _mod(self):
        return

    def _and(self):
        return

    def _or(self):
        return

    def _not(self):
        return

    def _rmem(self):
        return

    def _wmem(self):
        return

    def _call(self):
        return

    def _ret(self):
        return

    def _out(self):
        print(f"{chr(self.load_value(self._memory[self._ip+1]))}", end="")
        self.inc_ip(2)
        return

    def _in(self):
        return

    def _noop(self):
        self.inc_ip()
        return

    OPCODES = {
        OpCode.HALT: _halt,
        # OpCode.SET: _set,
        # OpCode.PUSH: _push,
        # OpCode.POP: _pop,
        # OpCode.EQ: _eq,
        # OpCode.GT: _gt,
        OpCode.JMP: _jmp,
        OpCode.JT: _jt,
        OpCode.JF: _jf,
        # OpCode.ADD: _add,
        # OpCode.MULT: _mult,
        # OpCode.MOD: _mod,
        # OpCode.AND: _and,
        # OpCode.OR: _or,
        # OpCode.NOT: _not,
        # OpCode.RMEM: _rmem,
        # OpCode.WMEM: _wmem,
        # OpCode.CALL: _call,
        # OpCode.RET: _ret,
        OpCode.OUT: _out,
        # OpCode.IN: _in,
        OpCode.NOOP: _noop
    }

    def run(self):

        operation = None
        while operation != OpCode.HALT:
            operation = OpCode(self._memory[self._ip])
            VM.OPCODES[operation](self)

        return


def main():

    program = np.fromfile('challenge.bin', dtype=np.int16)

    computer = VM(program)
    computer.run()

    return


if __name__ == "__main__":
    main()
