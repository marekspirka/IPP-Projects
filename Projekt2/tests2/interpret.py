# Interpret 2nd project IPP
# Autor : Marek Spirka
# login : xspir01

import re
import sys
import xml.etree.ElementTree as ET

read_counter = 0
instructions_list = list()
spot = 0
GF = dict()
TF = None
LF = list()
labels = dict()
data = list()
call_list = list()


class InputParser:
    def __init__(self):
        self.is_source = False
        self.is_input = False
        self.source = ""
        self.input = ""

    def parse_argument(self):
        if len(sys.argv) != 0:
            for arg in sys.argv:
                if arg == "--help":
                    self.print_help()
                elif "interpret.py" in arg:
                    pass
                elif "--input=" in arg:
                    if not self.is_input:
                        self.input = arg[8:]
                        self.is_input = True
                    else:
                        self.wrong_arguments()
                elif "--source" in arg:
                    if not self.is_source:
                        self.source = arg[9:]
                        self.is_source = True
                    else:
                        self.wrong_arguments()
                else:
                    self.wrong_arguments()
        else:
            self.wrong_arguments()

        if self.is_input != True and self.is_source != True:
            self.wrong_arguments()

        return self.source, self.input

    def wrong_arguments(self):
        print("Incorrect arguments. Try using [ --help ] argument.")
        sys.exit(10)

    def print_help(self):
        print("############################################################################")
        print("Interpret of IPPcode23 language")
        print("Usage: python3.10 interpret.py [--help | --source=file | --input=file]")
        print("  --help         |   How to use interpret script")
        print("  --source=file  |   Source script for interpret")
        print("  --input=file   |   Input file for interpret")
        print("  without arguments script read from stdin")
        print("############################################################################")
        sys.exit(0)


class XMLChecker:
    def __init__(self, root):
        self.root = root

    def check_header(self):
        if self.root.tag != "program":
            sys.exit(32)
        if not ("language" in list(self.root.attrib.keys())):
            sys.exit(32)
        if not ("IPPcode23" in self.root.attrib['language']):
            sys.exit(32)

    def line_up_order(self):
        try:
            self.root[:] = sorted(self.root, key=lambda child: int(child.attrib.get('order')))
        except Exception:
            sys.exit(32)

    def line_up_arg(self):
        for child in self.root:
            try:
                child[:] = sorted(child, key=lambda child: (child.tag))
            except Exception as e:
                exit(32)

    def check_xml(self):
        self.check_header()
        self.line_up_order()
        self.line_up_arg()
        dup_order = 0

        for child in self.root:
            child_attribute = list(child.attrib.keys())
            if child.tag != "instruction":
                sys.exit(32)
            if not ("opcode" in child_attribute) or not ("order" in child_attribute):
                sys.exit(32)
            if int(child.attrib.get('order')) < 0:
                sys.exit(32)
            for subElement in child:
                if re.match(r"^(arg1|arg2|arg3)$", subElement.tag):
                    pass
                else:
                    sys.exit(32)

            if dup_order == int(child.attrib.get('order')):
                sys.exit(32)
            dup_order = int(child.attrib.get('order'))

            duplicates = set()
            for tmp in child:
                if tmp.tag not in duplicates:
                    duplicates.add(tmp.tag)
                else:
                    sys.exit(32)


class ArgumentInstruction:
    def __init__(self, type_arg, value):
        self.type = type_arg  # typ argumentu
        self.value = value  # value of argument
        self.arg = []
        self.replace_escape()

    def replace_escape(self):
        if self.type == 'string' and self.value is not None:
            new_string = self.value
            for escape in re.finditer(r"\\[0-9]{3}", self.value):
                escape_number = escape.group()
                escape_number = escape_number.replace("\\", "")  # delete backslash
                char = chr(int(escape_number))
                new_string = new_string.replace(escape.group(), char)
            self.value = new_string


class Instruction:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.arg = []

    def add_argument(self, type_arg, value):
        self.arg.append(ArgumentInstruction(type_arg, value))


class Variables:
    def __init__(self, var_type, value):
        self.type = var_type
        self.value = value


def var_exists(var_type, name):
    global TF
    global LF
    global GF

    if var_type == "TF":
        if TF is None:
            sys.exit(55)
        elif not (name in TF.keys()):
            sys.exit(54)
    elif var_type == "GF":
        if name in GF.keys():
            pass
        else:
            sys.exit(54)
    elif var_type == "LF":
        if not LF:
            sys.exit(55)
        if len(LF) == 0:
            sys.exit(54)
        elif not (name in LF[len(LF) - 1].keys()):
            sys.exit(54)


def get_variable(var_type, var_name):
    if var_type == "GF":
        if var_name in GF.keys():
            return GF[var_name]
        else:
            sys.exit(54)
    elif var_type == "TF":
        if TF is None:
            sys.exit(55)
        if var_name in TF.keys():
            return TF[var_name]
        else:
            sys.exit(54)
    elif var_type == "LF":
        if len(LF) == 0:
            sys.exit(55)
        if var_name in LF[-1].keys():
            return LF[-1][var_name]
        else:
            sys.exit(54)


def save_var(var_type, var_name, symbol):
    if symbol.type == "int" or "string" or "nil" or "bool":
        check_TF_LF_GF(var_type, var_name, symbol)
    elif symbol.type == "var":
        tmp = symbol.value.split("@")
        var_exists(tmp[0], tmp[1])
        variable = get_variable(tmp[0], tmp[1])
        check_TF_LF_GF(var_type, var_name, variable)
    elif symbol.type == "char":
        check_TF_LF_GF(var_type, var_name, symbol)
    else:
        sys.exit(99)


def check_TF_LF_GF(var_type, var_name, arg):
    match var_type:
        case "GF":
            GF[var_name] = Variables(arg.type, arg.value)
        case "TF":
            if TF is not None:
                TF[var_name] = Variables(arg.type, arg.value)
            else:
                sys.exit(55)
        case "LF":
            if len(LF) != 0:
                LF[len(LF) - 1][var_name] = Variables(arg.type, arg.value)
            else:
                sys.exit(55)
        case _:
            sys.exit(55)


def var_value_NONE(value):
    if value is None:
        sys.exit(56)


def is_number(number):
    tmp = re.match("[+-]?\d+$", number)
    if tmp is None:
        return False
    else:
        return True


def Interpreter(instruction, input_name, positions):
    global TF
    global LF

    # print(instruction.name)
    match instruction.name:
        case "MOVE":
            if len(instruction.arg) == 2:
                move(instruction.arg[0], instruction.arg[1])
            else:
                sys.exit(32)
        case "CREATEFRAME":
            if len(instruction.arg) == 0:
                TF = dict()
            else:
                sys.exit(32)
        case "PUSHFRAME":
            if len(instruction.arg) == 0:
                if TF is None:
                    sys.exit(55)
                else:
                    LF.append(TF)
                TF = None
            else:
                sys.exit(32)
        case "POPFRAME":
            if len(instruction.arg) == 0:
                if len(LF) == 0:
                    sys.exit(55)
                else:
                    TF = LF.pop()
            else:
                sys.exit(32)
        case "DEFVAR":
            if len(instruction.arg) == 1:
                def_var(instruction.arg[0])
            else:
                sys.exit(32)
        case "CALL":
            if len(instruction.arg) == 1:
                positions = call_function(instruction.arg[0], instruction.value)
            else:
                sys.exit(32)
        case "RETURN":
            if len(instruction.arg) == 0:
                positions = func_return()
            else:
                sys.exit(32)
        case "PUSHS":
            if len(instruction.arg) == 1:
                if instruction.arg[0].type == "var":
                    instr_parts = instruction.arg[0].value.split("@")
                    var_exists(instr_parts[0], instr_parts[1])
                    tmp = get_variable(instr_parts[0], instr_parts[1])
                    var_value_NONE(tmp.value)
                data.append(instruction.arg[0])
            else:
                sys.exit(32)
        case "POPS":
            if len(instruction.arg) == 1:
                instr_parts = instruction.arg[0].value.split("@")
                var_exists(instr_parts[0], instr_parts[1])
                if len(data) == 0:
                    sys.exit(56)
                else:
                    tmp_var = data.pop()
                    save_var(instr_parts[0], instr_parts[1], tmp_var)
            else:
                sys.exit(32)
        case "ADD":
            if len(instruction.arg) == 3:
                arithmetic_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
            else:
                sys.exit(32)
        case "SUB":
            if len(instruction.arg) == 3:
                arithmetic_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
            else:
                sys.exit(32)
        case "MUL":
            if len(instruction.arg) == 3:
                arithmetic_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
            else:
                sys.exit(32)
        case "IDIV":
            if len(instruction.arg) == 3:
                arithmetic_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
            else:
                sys.exit(32)
        case "LT":
            if len(instruction.arg) == 3:
                comparisons_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
            else:
                sys.exit(32)
        case "GT":
            if len(instruction.arg) == 3:
                comparisons_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
            else:
                sys.exit(32)
        case "EQ":
            if len(instruction.arg) == 3:
                comparisons_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
            else:
                sys.exit(32)
        case "AND":
            if len(instruction.arg) == 3:
                logical_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
            else:
                sys.exit(32)
        case "OR":
            if len(instruction.arg) == 3:
                logical_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
            else:
                sys.exit(32)
        case "NOT":
            if len(instruction.arg) == 2:
                logical_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[1])
            else:
                sys.exit(32)
        case "INT2CHAR":
            if len(instruction.arg) == 2:
                int2char(instruction.arg[0], instruction.arg[1])
            else:
                sys.exit(32)
        case "STRI2INT":
            if len(instruction.arg) == 3:
                string2int(instruction.arg[0], instruction.arg[1], instruction.arg[2])
            else:
                sys.exit(32)
        case "READ":
            if len(instruction.arg) == 2:
                read(instruction.arg[0], instruction.arg[1], input_name)
            else:
                sys.exit(32)
        case "WRITE":
            if len(instruction.arg) == 1:
                write(instruction.arg[0])
            else:
                sys.exit(32)
        case "CONCAT":
            if len(instruction.arg) == 3:
                concat(instruction.arg[0], instruction.arg[1], instruction.arg[2])
            else:
                sys.exit(32)
        case "STRLEN":
            if len(instruction.arg) == 2:
                strlen_func(instruction.arg[0], instruction.arg[1])
            else:
                sys.exit(32)
        case "GETCHAR":
            if len(instruction.arg) == 3:
                get_char(instruction.arg[0], instruction.arg[1], instruction.arg[2])
            else:
                sys.exit(32)
        case "SETCHAR":
            if len(instruction.arg) == 3:
                set_char(instruction.arg[0], instruction.arg[1], instruction.arg[2])
            else:
                sys.exit(32)
        case "TYPE":
            if len(instruction.arg) == 2:
                type_func(instruction.arg[0], instruction.arg[1])
            else:
                sys.exit(32)
        case "LABEL":
            if len(instruction.arg) == 1:
                pass
            else:
                sys.exit(32)
        case "JUMP":
            if len(instruction.arg) == 1:
                positions = jump(instruction.arg[0])
            else:
                sys.exit(32)
        case "JUMPIFEQ":
            if len(instruction.arg) == 3:
                label = comparisons_jump(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
                if label is not None:
                    positions = label
            else:
                sys.exit(32)
        case "JUMPIFNEQ":
            if len(instruction.arg) == 3:
                label = comparisons_jump(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
                if label is not None:
                    positions = label
            else:
                sys.exit(32)
        case "EXIT":
            if len(instruction.arg) == 1:
                exit_func(instruction.arg[0])
            else:
                sys.exit(32)
        case "DPRINT":
            if len(instruction.arg) == 1:
                pass
            else:
                sys.exit(32)
        case "BREAK":
            if len(instruction.arg) == 0:
                pass
            else:
                sys.exit(32)
        case _:
            sys.exit(32)

    return positions


def move(var, symbol):
    if symbol.type == "var":
        symbol_parts = symbol.value.split("@")
        tmp = get_variable(symbol_parts[0], symbol_parts[1])
        var_exists(symbol_parts[0], symbol_parts[1])
        var_value_NONE(tmp.value)
        save_var(symbol_parts[0], symbol_parts[1], symbol)

    varParts = var.value.split("@")
    var_exists(varParts[0], varParts[1])
    save_var(varParts[0], varParts[1], symbol)


def def_var(variable):
    variable_parts = variable.value.split("@")
    empty_var = Variables(None, None)
    match variable_parts[0]:
        case "LF":
            if len(LF) == 0:
                sys.exit(55)
            if not (variable_parts[1] in LF[len(LF) - 1].keys()):
                LF[len(LF) - 1].update({variable_parts[1]: empty_var})
            else:
                sys.exit(52)
        case "GF":
            if variable_parts[1] in GF.keys():
                sys.exit(52)
            else:
                GF.update({variable_parts[1]: empty_var})
        case "TF":
            if TF is None:
                sys.exit(55)
            if variable_parts[1] in TF.keys():
                sys.exit(52)
            else:
                TF.update({variable_parts[1]: empty_var})
        case _:
            sys.exit(55)


def call_function(arg, position):
    global spot
    call_list.append(position)
    if arg.value in labels.keys():
        spot = int(labels[arg.value] - 1)
        return spot
    else:
        sys.exit(52)


def func_return():
    global spot
    if len(call_list) == 0:
        sys.exit(56)
    else:
        position = call_list.pop()
        spot = int(position)
        return spot


def arithmetic_functions(type, var, symb1, symb2):
    variable_parts = var.value.split("@")
    result = 0
    tmp = symb1
    tmp2 = symb2
    if symb1.type == "var":
        variable_parts_1 = symb1.value.split("@")
        tmp = get_variable(variable_parts_1[0], variable_parts_1[1])
        var_value_NONE(tmp.value)

    if symb2.type == "var":
        variable_parts_2 = symb2.value.split("@")
        tmp2 = get_variable(variable_parts_2[0], variable_parts_2[1])
        var_value_NONE(tmp2.value)

    if tmp.type == "int" and tmp2.type == "int":
        if is_number(str(tmp.value)) and is_number(str(tmp2.value)):
            match type:
                case "ADD":
                    result = ArgumentInstruction("int", int(tmp.value) + int(tmp2.value))
                case "SUB":
                    result = ArgumentInstruction("int", int(tmp.value) - int(tmp2.value))
                case "MUL":
                    result = ArgumentInstruction("int", int(tmp.value) * int(tmp2.value))
                case "IDIV":
                    if int(tmp2.value) != 0:
                        result = ArgumentInstruction("int", int(tmp.value) // int(tmp2.value))
                    else:
                        sys.exit(57)

            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
        else:
            sys.exit(32)
    else:
        sys.exit(53)


def comparisons_functions(operator, var, symb1, symb2):
    result = False
    variable_parts = var.value.split("@")
    tmp = symb1
    tmp2 = symb2

    if symb1.type == "var":
        variable_parts_1 = symb1.value.split("@")
        tmp = get_variable(variable_parts_1[0], variable_parts_1[1])
        var_value_NONE(tmp.value)
        if tmp2.type == "string" and tmp2.value is None:
            tmp2.value = ""
        else:
            var_value_NONE(tmp2.value)
    if symb2.type == "var":
        variable_parts_2 = symb2.value.split("@")
        tmp2 = get_variable(variable_parts_2[0], variable_parts_2[1])
        if tmp2.type == "string" and tmp2.value is None:
            tmp2.value = ""
        else:
            var_value_NONE(tmp2.value)

    if tmp.type == "int" and tmp2.type == "int":
        if operator == "LT":
            if int(tmp.value) < int(tmp2.value):
                result = ArgumentInstruction("bool", "true")
            else:
                result = ArgumentInstruction("bool", "false")
        elif operator == "GT":
            if int(tmp.value) > int(tmp2.value):
                result = ArgumentInstruction("bool", "true")
            else:
                result = ArgumentInstruction("bool", "false")
        elif operator == "EQ":
            if int(tmp.value) == int(tmp2.value):
                result = ArgumentInstruction("bool", "true")
            else:
                result = ArgumentInstruction("bool", "false")

        var_exists(variable_parts[0], variable_parts[1])
        save_var(variable_parts[0], variable_parts[1], result)

    elif tmp.type == "string" and tmp2.type == "string":
        if operator == "LT":
            if str(tmp.value) < str(tmp2.value):
                result = ArgumentInstruction("bool", "true")
            else:
                result = ArgumentInstruction("bool", "false")
        elif operator == "GT":
            if str(tmp.value) > str(tmp2.value):
                result = ArgumentInstruction("bool", "true")
            else:
                result = ArgumentInstruction("bool", "false")
        elif operator == "EQ":
            if str(tmp.value) == str(tmp2.value):
                result = ArgumentInstruction("bool", "true")
            else:
                result = ArgumentInstruction("bool", "false")

        var_exists(variable_parts[0], variable_parts[1])
        save_var(variable_parts[0], variable_parts[1], result)

    elif tmp.type == "bool" and tmp2.type == "bool":
        if operator == "LT":
            if tmp.value == "false" and tmp2.value == "true":
                result = ArgumentInstruction("bool", "true")
            else:
                result = ArgumentInstruction("bool", "false")
        elif operator == "GT":
            if tmp.value == "true" and tmp2.value == "false":
                result = ArgumentInstruction("bool", "true")
            else:
                result = ArgumentInstruction("bool", "false")
        elif operator == "EQ":
            if (tmp.value == "true" and tmp2.value == "true") or (
                    tmp.value == "false" and tmp2.value == "false"):
                result = ArgumentInstruction("bool", "true")
            else:
                result = ArgumentInstruction("bool", "false")

        var_exists(variable_parts[0], variable_parts[1])
        save_var(variable_parts[0], variable_parts[1], result)

    elif tmp.type == "nil" and tmp2.type == "nil":
        if operator == "EQ":
            result = ArgumentInstruction("bool", "true")
            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
        else:
            sys.exit(53)
    elif tmp.type == "nil" and (tmp2.type == "string" or tmp2.type == "bool" or tmp2.type == "int"):
        if operator == "EQ":
            result = ArgumentInstruction("bool", "false")
            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
        else:
            sys.exit(53)
    elif tmp2.type == "nil" and (tmp.type == "string" or tmp.type == "bool" or tmp.type == "int"):
        if operator == "EQ":
            result = ArgumentInstruction("bool", "false")
            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
        else:
            sys.exit(53)
    else:
        sys.exit(53)


def logical_functions(logic, var, symb1, symb2):
    result = False
    variable_parts = var.value.split("@")
    tmp = symb1
    tmp2 = symb2

    if symb1.type == "var":
        variable_parts_1 = symb1.value.split("@")
        tmp = get_variable(variable_parts_1[0], variable_parts_1[1])
        var_value_NONE(tmp.value)

    if symb2.type == "var":
        variable_parts_2 = symb2.value.split("@")
        tmp2 = get_variable(variable_parts_2[0], variable_parts_2[1])
        var_value_NONE(tmp2.value)

    if logic == "NOT":
        if tmp.type == "bool":
            if tmp.value == "true":
                result = ArgumentInstruction("bool", "false")
            elif tmp.value == "false":
                result = ArgumentInstruction("bool", "true")
            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
        else:
            sys.exit(53)
        return

    if tmp.type == "bool" and tmp2.type == "bool":
        if logic == "AND":
            if tmp.value == "true" and tmp2.value == "true":
                result = ArgumentInstruction("bool", "true")
            else:
                result = ArgumentInstruction("bool", "false")
            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
        elif logic == "OR":
            if tmp.value == "true" or tmp2.value == "true":
                result = ArgumentInstruction("bool", "true")
            else:
                result = ArgumentInstruction("bool", "false")
            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
    else:
        sys.exit(53)


# to do var
def int2char(var, number):
    variable_parts = var.value.split("@")

    if number.type == "var":
        variable_parts_2 = number.value.split("@")
        tmp2 = get_variable(variable_parts_2[0], variable_parts_2[1])
        var_value_NONE(tmp2.value)

    if number.type == "int":
        if int(number.value) > 1114111 or int(number.value) < 0:
            sys.exit(58)
        else:
            var_exists(variable_parts[0], variable_parts[1])
            string = chr(int(number.value))
            result = ArgumentInstruction("string", string)
            save_var(variable_parts[0], variable_parts[1], result)
    else:
        sys.exit(53)


def string2int(var, symb1, symb2):
    variable_parts = var.value.split("@")
    tmp = symb1
    tmp2 = symb2

    if symb1.type == "var":
        variable_parts_1 = symb1.value.split("@")
        tmp = get_variable(variable_parts_1[0], variable_parts_1[1])
        var_value_NONE(tmp.value)
    if symb2.type == "var":
        variable_parts_1 = symb2.value.split("@")
        tmp2 = get_variable(variable_parts_1[0], variable_parts_1[1])
        var_value_NONE(tmp2.value)

    if tmp.type == "bool" or tmp2.type == "bool":
        sys.exit(53)
    if tmp.type == "string" and tmp2.type == "int":
        if len(tmp.value) <= int(tmp2.value) or int(tmp2.value) < 0:
            sys.exit(58)

        result = ArgumentInstruction(tmp2.type, ord(tmp.value[int(tmp2.value)]))
        var_exists(variable_parts[0], variable_parts[1])
        save_var(variable_parts[0], variable_parts[1], result)
    else:
        sys.exit(53)


def read(var, type, input_name):
    global read_counter
    input_string = None
    variable_parts = var.value.split("@")
    empty_var = Variables("nil", "nil")
    if not input_name:
        pass
    else:
        with open(input_name) as f:
            lines = [line.rstrip('\n') for line in f]
        try:
            input_string = lines[read_counter]
            read_counter += 1
        except:
            input_string = ""

    if is_number(input_string) and type.value == "int":
        tmp = ArgumentInstruction("int", input_string)
    elif type.value == "bool":
        if input_string.lower() == "true":
            tmp = ArgumentInstruction("bool", "true")
        else:
            tmp = ArgumentInstruction("bool", "false")
    elif type.value == "string":
        tmp = ArgumentInstruction("string", input_string)
    elif type.value == "nil":
        tmp = ArgumentInstruction("nil", input_string)
    else:
        if type.value == "string":
            tmp = ArgumentInstruction("string", input_string)
        elif type.value == "int":
            tmp = ArgumentInstruction("int", input_string)
        elif type.value == "bool":
            tmp = ArgumentInstruction("bool", input_string.lower())
        else:
            tmp = ArgumentInstruction("nil", input_string)

    if tmp is not None:
        if tmp.type in ["bool", "int", "string", "nil"]:
            result = ArgumentInstruction(tmp, tmp.value)
            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result.type)
        else:
            result = ArgumentInstruction(empty_var.type, empty_var.value)
            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result.type)


def write(name):
    match name.type:
        case "bool":
            if name.value != "true":
                print("false", end='')
            else:
                print("true", end='')
        case "int":
            var = get_variable(name.type, name.value)
            if var is None:
                var = name.value
            print(var, end='')
        case "var":
            variable_parts = name.value.split("@")
            var = get_variable(variable_parts[0], variable_parts[1])
            var_value_NONE(var.value)

            if var.value is not None:
                if var.type == "string":
                    var.value = var.value.replace("&amp", '&')
                    var.value = var.value.replace("&lt", '<')
                    var.value = var.value.replace("&gt", '>')
                    var.value = var.value.replace("\\032", ' ')
                    print(var.value, end='')
                elif var.type == "nil":
                    print("", end='')
                else:
                    print(var.value, end='')
            else:
                print("", end='')

        case "nil":
            print("", end='')

        case _:
            if name.type == "string":
                name.value = name.value.replace("&amp", '&')
                name.value = name.value.replace("&lt", '<')
                name.value = name.value.replace("&gt", '>')
                name.value = name.value.replace("\\032", ' ')
                print(name.value, end='')


def concat(var, symb1, symb2):
    variable_parts = var.value.split("@")
    tmp = symb1
    tmp2 = symb2
    if symb1.type == "var":
        variable_parts_1 = symb1.value.split("@")
        tmp = get_variable(variable_parts_1[0], variable_parts_1[1])
        var_value_NONE(tmp.value)
    if symb2.type == "var":
        variable_parts_2 = symb2.value.split("@")
        tmp2 = get_variable(variable_parts_2[0], variable_parts_2[1])
        var_value_NONE(tmp2.value)

    if tmp.type == "string" and tmp2.type == "string":
        if tmp.value is not None and tmp2.value is not None:
            result = ArgumentInstruction("string", tmp.value + tmp2.value)
            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
        else:
            result = ArgumentInstruction("string", "")
            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
    else:
        sys.exit(53)


def strlen_func(var, symb1):
    tmp = symb1
    variable_parts = var.value.split("@")

    if symb1.type == "var":
        variable_parts_1 = symb1.value.split("@")
        var_exists(variable_parts[0], variable_parts[1])
        tmp = get_variable(variable_parts_1[0], variable_parts_1[1])
        var_value_NONE(tmp.value)
    if tmp.type == "string":
        if tmp.value is None:
            result = ArgumentInstruction("int", "0")
            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
        else:
            result = ArgumentInstruction("int", len(tmp.value))
            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
    else:
        sys.exit(53)


def get_char(var, symb1, symb2):
    variable_parts = var.value.split("@")
    tmp = symb1
    tmp2 = symb2
    if symb1.type == "var":
        variable_parts_1 = symb1.value.split("@")
        tmp = get_variable(variable_parts_1[0], variable_parts_1[1])
        var_value_NONE(tmp.value)
    if symb2.type == "var":
        variable_parts_2 = symb2.value.split("@")
        tmp2 = get_variable(variable_parts_2[0], variable_parts_2[1])
        var_value_NONE(tmp2.value)

    if tmp.type == "string" and tmp2.type == "int":
        if len(tmp.value) > int(tmp2.value) > 0:
            result = ArgumentInstruction("string", (tmp.value[int(tmp2.value)]))
            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
        else:
            sys.exit(58)
    else:
        sys.exit(53)


def set_char(var, symb1, symb2):
    tmp = symb1
    tmp2 = symb2

    variable_parts = var.value.split("@")
    var = get_variable(variable_parts[0], variable_parts[1])
    var_value_NONE(var.value)

    if symb1.type == "var":
        variable_parts_1 = symb1.value.split("@")
        tmp = get_variable(variable_parts_1[0], variable_parts_1[1])
        var_value_NONE(tmp.value)

    if symb2.type == "var":
        variable_parts_2 = symb2.value.split("@")
        tmp2 = get_variable(variable_parts_2[0], variable_parts_2[1])
        var_value_NONE(tmp2.value)

    if tmp2.type == "string" and tmp.type == "int" and var.type == "string":
        if len(var.value) > int(tmp.value) >= 0 and tmp2.value is not None:
            var_exists(variable_parts[0], variable_parts[1])
            var.value = list(var.value)
            var.value[int(tmp.value)] = tmp2.value[0]
            var.value = ''.join(var.value)
        else:
            sys.exit(58)
    else:
        sys.exit(53)


def type_func(var, symb1):
    variable_parts = var.value.split("@")

    tmp = symb1
    if symb1.type == "var":
        variable_parts_1 = symb1.value.split("@")
        tmp = get_variable(variable_parts_1[0], variable_parts_1[1])

    if tmp.type == "string" or "int" or "bool" or "nil":
        result = ArgumentInstruction("string", tmp.type)
    else:
        result = ArgumentInstruction("string", "")

    if tmp.type is None:
        result = ArgumentInstruction("string", "")

    var_exists(variable_parts[0], variable_parts[1])
    save_var(variable_parts[0], variable_parts[1], result)


def exists_label(label):
    exists = labels.get(label)
    if exists is None:
        sys.exit(52)


def jump(label):
    global spot
    if label.value in labels and label.type == "label":
        spot = int(labels[label.value] - 1)
        return spot
    else:
        sys.exit(52)


def comparisons_jump(operator, label, symb1, symb2):
    global spot
    if symb1.type == "var":
        variable_parts_1 = symb1.value.split("@")
        var_exists(variable_parts_1[0], variable_parts_1[1])
        symb1 = get_variable(variable_parts_1[0], variable_parts_1[1])
        var_value_NONE(symb1.value)

    if symb2.type == "var":
        variable_parts_2 = symb2.value.split("@")
        var_exists(variable_parts_2[0], variable_parts_2[1])
        symb2 = get_variable(variable_parts_2[0], variable_parts_2[1])
        var_value_NONE(symb2.value)

    if symb1.type == symb2.type or symb1.type == "nil" or symb2.type == "nil":
        exists_label(label.value)
        if operator == "JUMPIFEQ":
            if str(symb1.value) == str(symb2.value):
                spot = jump(label)
                return spot
        if operator == "JUMPIFNEQ":
            if str(symb1.value) != str(symb2.value):
                spot = jump(label)
                return spot
    else:
        sys.exit(53)


def exit_func(symb):
    if symb.type == "var":
        variable_parts = symb.value.split("@")
        var_exists(variable_parts[0], variable_parts[1])
        symb1 = get_variable(variable_parts[0], variable_parts[1])
        var_value_NONE(symb1.value)
        if symb1.type == "int":
            var_value_NONE(symb1.value)
            sys.exit(int(symb1.value))
        else:
            sys.exit(53)

    elif symb.type == "int":
        if 0 <= int(symb.value) <= 49:
            sys.exit(int(symb.value))
        else:
            sys.exit(57)
    else:
        sys.exit(53)


def add_instruction_to_class(root):
    instruction_count = 0

    for element in root:
        instructions_list.append(Instruction(element.attrib['opcode'].upper(), instruction_count))

        for args in element:
            instructions_list[instruction_count].add_argument(args.attrib['type'].lower(), args.text)

        instruction_count += 1

    for label in instructions_list:
        if label.name.upper() == "LABEL":
            if not (label.arg[0].value in labels):
                labels.update({label.arg[0].value: label.value + 1})
            else:
                sys.exit(52)

    return instruction_count


def main():
    input_parser = InputParser()
    source, inputName = input_parser.parse_argument()

    try:
        if source:
            tree = ET.parse(source)
        else:
            tree = ET.parse(sys.stdin)
    except FileNotFoundError:
        sys.exit(31)

    root = tree.getroot()

    xml_parser = XMLChecker(root)
    xml_parser.check_xml()

    # pridanie instrukcie do listu
    num_of_instr = add_instruction_to_class(root)
    # kolko mame instrukcii tolko krat volame Interpreter
    spot = 0
    while spot != num_of_instr:
        spot = Interpreter(instructions_list[spot], inputName, spot)
        spot += 1

    sys.exit(0)


if __name__ == '__main__':
    main()
