import calendar
from enum import Enum


class BaseModule:
    def __init__(self, name):
        self.name = name
        self.commands = {}

    def defer(self):
        pass


class CommandType(Enum):
    CALCULATION = 0,
    CREATION = 1


class CommandInfo:
    def __init__(self, name, type, func, args_count=0):
        self.name = name
        self.type = type
        self.func = func
        self.args_count = args_count


class StandardModule(BaseModule):
    def __init__(self):
        super().__init__('standard')
        self.commands = {
            'month': CommandInfo('month', CommandType.CALCULATION, self.month, 1),
            'zfill': CommandInfo('zfill', CommandType.CALCULATION, self.zfill, 2),
            'join': CommandInfo('join', CommandType.CALCULATION, self.join, 2)
        }

    def month(self, num):
        return calendar.month_name[num]

    def zfill(self, digits, num):
        return str(num).zfill(int(digits))

    def join(self, a, b):
        return a + b