#!/usr/bin/python3.8

# This software is provided as-is in the hopes that it may be useful. #

import shlex
import sys
import readchar


class FuckTape:
    """
    Wrapper for list representing a Brainfuck tape.
    """
    def __init__(self):
        self.__tape = bytearray(10)

    def __getitem__(self, idx: int) -> int:
        if idx < 0:  # Negative indices not permitted.
            raise IndexError

        try:
            return self.__tape[idx]
        except IndexError:
            # Just keep adding zeroes until it works.
            self.__tape.append(0)
            return self[idx]

    def __setitem__(self, idx: int, value: int):
        try:
            self.__tape[idx] = value
        except IndexError:
            self.__tape.append(0)
            self[idx] = value
        except ValueError:  # Make that value overflow
            if value < 0:
                self[idx] = 256 + value
            else:  # value > 255
                self[idx] = value - 255

    def get_char(self, idx: int) -> str:
        decoded_string = self.__tape.decode(encoding='utf-8')
        return decoded_string[idx]


class FuckPointer:
    def __init__(self, tape: FuckTape, loop_stack: list):
        self.__fuck_tape = tape
        self.__point_idx = 0
        self.__loop_stack = loop_stack

    def shift_right(self):
        self.__point_idx += 1

    def shift_left(self):
        self.__point_idx -= 1

    def increment(self):
        self.__fuck_tape[self.idx] += 1

    def decrement(self):
        self.__fuck_tape[self.idx] -= 1

    def get_val(self) -> str:
        return self.__fuck_tape.get_char(self.idx)

    def set_val(self, char: str):
        byte_arr = char.encode(encoding='utf-8')
        byte = byte_arr[0]
        self.__fuck_tape[self.idx] = byte

    # def start_loop(self):
    #     if self.__fuck_tape[self.idx] == 0:
    #         loop = self._get_loop_by_start(self.idx)
    #         self.__point_idx = loop[1] + 1  # Skip to end

    # def end_loop(self):
    #     if self.__fuck_tape[self.idx] != 0:
    #         loop = self._get_loop_by_end(self.idx)
    #         self.__point_idx = loop[0]  # Go to the loop's start

    @property
    def idx(self):
        return self.__point_idx

    def get_loop_by_start(self, start_index):
        for loop in self.__loop_stack:
            if loop[0] == start_index:
                return loop

        raise ValueError

    def get_loop_by_end(self, end_index):
        for loop in self.__loop_stack:
            if loop[1] == end_index:
                return loop

        raise ValueError

    def is_zero(self):
        return self.__fuck_tape[self.idx] == 0


def parse_brainfuck(file) -> str:
    sigils = "><+-.,[]"
    contents = file.read()
    file.seek(0)
    brainfuck = [char for char in contents if char in sigils]
    return ''.join(brainfuck)


def execute_instructions(instructions: str):
    pointer = FuckPointer(FuckTape(), create_loop_stack(instructions))
    progress = 0
    while progress < len(instructions):
        symbol = instructions[progress]
        if symbol == '>':
            pointer.shift_right()
        elif symbol == '<':
            pointer.shift_left()
        elif symbol == '+':
            pointer.increment()
        elif symbol == '-':
            pointer.decrement()
        elif symbol == '.':
            print(pointer.get_val(), end='')
        elif symbol == ',':
            pointer.set_val(readchar.readchar())
        elif symbol == '[':
            if pointer.is_zero():
                progress = pointer.get_loop_by_start(progress)[1]  # Skip to end of loop
                continue
        elif symbol == ']':
            if not pointer.is_zero():
                progress = pointer.get_loop_by_end(progress)[0]  # Rewind to start of loop.
                continue
        progress += 1



def create_loop_stack(instructions: str):
    starts = []
    loops = []
    for idx, char in enumerate(instructions):
        if char == '[':
            starts.append(idx)
        elif char == ']':
            loops.append((starts.pop(), idx))

    return loops


def main(*args):
    with open(args[1], 'r') as brainfuck_file:
        parsed_fuck = parse_brainfuck(brainfuck_file)
    execute_instructions(parsed_fuck)


if __name__ == '__main__':
    main(*sys.argv)
