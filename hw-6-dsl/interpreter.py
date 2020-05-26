from docx_module import DocxModule
from web_module import WebModule
from standard_module import StandardModule
from standard_module import CommandInfo, CommandType


class Loop:
    def __init__(self, indentation, start, it):
        self.indentation = indentation
        self.start = start
        self.it = it


class Variable:
    def __init__(self, value, line, indentation):
        self.value = value
        self.line = line
        self.indentation = indentation


class Interpreter:
    def __init__(self):
        self._clear()
        self.modules = {
            'standard': StandardModule(),
            'docx': DocxModule(),
            'web': WebModule()
        }

    def _clear(self):
        self._variables = {}
        self._loops = []
        self._indentation = 0
        self._on_creation = False
        self._creation_command = None
        self._properties = {}

    def interpret(self, program):
        try:
            self._clear()
            lines = program.splitlines()
            i = 0
            while i <= len(lines):
                if i == len(lines):
                    if self._on_creation:
                        self.update_creation([])
                    if self.check_loop(True):
                        i = self._loops[-1].start + 1
                        continue
                    if len(self._loops) > 0:
                        continue
                    break
                line = lines[i]
                tokens = line.split()
                self.calculate_indentation(line)
                self.clean_variables(i)
                if self._on_creation and self.update_creation(tokens):
                    i += 1
                    continue
                if self.check_loop(False):
                    i = self._loops[-1].start + 1
                    continue
                if tokens[0] == 'foreach':
                    self.parse_loop(tokens[1:], i)
                else:
                    self.parse_command(tokens, i)
                i += 1
            for module in self.modules.values():
                module.defer()
        except Exception as e:
            print("interpretation error: {0}".format(e))

    def parse_loop(self, tokens, line):
        if '..' in tokens[0]:
            tokens = tokens[0].split('..')
            it = range(int(tokens[0]), int(tokens[1]) + 1).__iter__()
        else:
            command, args = self.parse_command_with_args(tokens)
            it = self.calculation_command(command, args)
        self._variables[self._indentation] = Variable(next(it), line, self._indentation)
        self._loops.append(Loop(self._indentation, line, it))

    def parse_command(self, tokens, line):
        command, args = self.parse_command_with_args(tokens)
        if command.type == CommandType.CREATION:
            self._on_creation = True
            self._creation_command = command
        elif command.type == CommandType.CALCULATION:
            result = self.calculation_command(command, args)
            self._variables[self._indentation] = Variable(result, line, self._indentation)

    def parse_command_with_args(self, tokens):
        module = self.get_module(tokens[0])
        if module is not 'standard':
            tokens = tokens[1:]
        command_name = tokens[0]
        args = tokens[1:]
        return self.modules[module].commands[command_name], args

    def parse_property(self, tokens, properties):
        if len(tokens) > 1 and tokens[0][-1] == ':':
            name = tokens[0][0:-1]
            value = tokens[1]
            if value[0] == '$':
                if len(value) == 1:
                    value = self.find_variable()
                else:
                    command, args = self.parse_command_with_args([value[1:]] + tokens[2:])
                    value = self.calculation_command(command, args)
            properties[name] = value
            return True
        return False

    def update_creation(self, tokens):
        if self.parse_property(tokens, self._properties):
            return True
        self._creation_command.func(self._properties)
        self._properties = {}
        self._on_creation = False
        return False

    def check_loop(self, last_line):
        if len(self._loops) > 0:
            loop = self._loops[-1]
            if loop.indentation == self._indentation or last_line:
                try:
                    self._variables[loop.indentation] = Variable(next(loop.it), loop.start, loop.indentation)
                    return True
                except StopIteration:
                    self._loops.pop(-1)
                    del self._variables[loop.indentation]
        return False

    def find_variable(self):
        indentation = self._indentation
        while indentation not in self._variables and indentation > 0:
            indentation -= 1
        return self._variables[indentation].value

    def clean_variables(self, line):
        for key in list(self._variables.keys()):
            if key > self._indentation or key == self._indentation and self._variables[key].line > line:
                del self._variables[key]

    def calculation_command(self, command, args):
        args_count = command.args_count
        if len(args) != args_count:
            args.append(self.find_variable())
        return command.func(*args)

    def get_module(self, token):
        if len(token) > 2 and token[0] == '[' and token[-1] == ']':
            return token[1:-1]
        return 'standard'

    def calculate_indentation(self, line):
        indentation = 0
        for ch in line:
            if ch != '\t':
                break
            indentation += 1
        self._indentation = indentation
