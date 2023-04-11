# Interpret 2nd project IPP
# Autor : Marek Spirka
# login : xspir01

import re
import sys
import xml.etree.ElementTree as ET

global spot
instructions_list = list()
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

    def check_xml(self):
        self.check_header()
        self.line_up_order()
        dup_order = 0

        for child in self.root:
            child_attribute = list(child.attrib.keys())
            if child.tag != "instruction":
                sys.exit(32)
            if "opcode" in child_attribute and "order" in child_attribute:
                pass
            else:
                sys.exit(32)
            if int(child.attrib.get('order')) < 0:
                sys.exit(32)
            if dup_order != int(child.attrib.get('order')):
                dup_order = int(child.attrib.get('order'))
                pass
            else:
                sys.exit(32)

            for subElement in child:
                if re.match(r"^(arg1|arg2|arg3)$", subElement.tag):
                    pass
                else:
                    sys.exit(32)

            duplicity = set()
            for duplicates in child:
                if duplicates.tag not in duplicity:
                    duplicity.add(duplicates.tag)
                else:
                    sys.exit(32)

            print(child.tag, child.attrib)


class ArgumentInstruction:
    def __init__(self, type_arg, value):
        self.type = type_arg  # typ argumentu
        self.value = value  # value of argument
        self.arg = []


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
            sys.exit(54)
        elif not (name in TF.keys()):
            sys.exit(54)
    elif var_type == "GF":
        if name in GF.keys():
            pass
        else:
            sys.exit(54)
    elif var_type == "LF":
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
    if re.match(r'(int|bool|string|nil)', symbol.type):
        check_TF_LF_GF(var_type, var_name, symbol)

    elif symbol.type == "var":
        tmp = symbol.value.split("@")
        var_exists(tmp[0], tmp[1])
        variable = get_variable(tmp[0], tmp[1])
        check_TF_LF_GF(var_type, var_name, variable)

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


def is_number(number):
    tmp = re.match("[+-]?\d+$", number)
    if tmp is None:
        return False
    else:
        return True


def Interpreter(instruction, input_name):
    global TF
    match instruction.name:
        case "MOVE":
            move(instruction.arg[0], instruction.arg[1])
        case "CREATEFRAME":
            TF = dict()
        case "PUSHFRAME":
            if TF is None:
                sys.exit(55)
            else:
                LF.append(TF)
            TF = None
        case "POPFRAME":
            if len(LF) == 0:
                sys.exit(55)
            else:
                TF = LF.pop()
        case "DEFVAR":
            def_var(instruction.arg[0])
        case "CALL":
            call_function(instruction.arg[0], instruction.value)
        case "RETURN":
            func_return()
        case "PUSHS":
            data.append(instruction.arg[0])
        case "POPS":
            instr_parts = instruction.arg[0].value.split("@")
            if len(data) == 0:
                sys.exit(56)
            else:
                tmp_var = data.pop()
                save_var(instr_parts[0], instr_parts[1], tmp_var)
        case "ADD":
            arithmetic_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
        case "SUB":
            arithmetic_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
        case "MUL":
            arithmetic_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
        case "IDIV":
            arithmetic_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
        case "LT":
            comparisons_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
        case "GT":
            comparisons_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
        case "EQ":
            comparisons_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
        case "AND":
            logical_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
        case "OR":
            logical_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[2])
        case "NOT":
            logical_functions(instruction.name, instruction.arg[0], instruction.arg[1], instruction.arg[1])
        case "INT2CHAR":
            int2char(instruction.arg[0], instruction.arg[1])
        case "STRI2INT":
            string2int(instruction.arg[0], instruction.arg[1], instruction.arg[2])
        case "READ":
            read(instruction.arg[0], input_name)
        case "WRITE":
            write(instruction.arg[0])
        case "CONCAT":
            concat(instruction.arg[0], instruction.arg[1], instruction.arg[2])
        case "STRLEN":
            strlen_func(instruction.arg[0], instruction.arg[1])
        case "GETCHAR":
            get_char(instruction.arg[0], instruction.arg[1], instruction.arg[2])
        case "SETCHAR":
            get_char(instruction.arg[0], instruction.arg[1], instruction.arg[2])
        case "TYPE":
            print("TYPE")
        case "LABEL":
            print("LABEL")
        case "JUMPIFEQ":
            print("JUMPIFEQ")
        case "JUMPIFNEQ":
            print("JUMPIFNEQ")
        case "EXIT":
            print("EXIT")
        case "DPRINT":
            print("DPRINT")
        case "BREAK":
            print("BREAK")
        case _:
            print("Instruction fail!!")
            sys.exit(32)


def move(var, symbol):
    varParts = var.value.split("@")
    var_exists(varParts[0], varParts[1])
    save_var(varParts[0], varParts[1], symbol)


def def_var(variable):
    variable_parts = variable.value.split("@")
    empty_var = Variables(None, None)
    match variable_parts[0]:
        case "LF":
            if len(LF) == 0:
                sys.exit(52)
            if not (variable_parts[1] in LF[len(LF) - 1].keys()):
                LF[len(LF) - 1].update({variable_parts[1]: empty_var})
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
    else:
        sys.exit(52)


def func_return():
    global spot
    if len(call_list) == 0:
        sys.exit(56)
    else:
        spot = call_list.pop
        spot = int(spot - 1)


def arithmetic_functions(type, var, symb1, symb2):
    variable_parts = var.value.split("@")
    ###################################################################################
    result = 0
    tmp = symb1
    tmp2 = symb2

    if symb1.type == "var":
        variable_parts_1 = symb1.value.split("@")
        tmp = get_variable(variable_parts_1[0], variable_parts[1])

    if symb2.type == "var":
        variable_parts_2 = symb2.value.split("@")
        tmp2 = get_variable(variable_parts_2[0], variable_parts_2[1])

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
                    result = ArgumentInstruction("int", int(tmp.value) // int(tmp2.value))

            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
        else:
            sys.exit(32)
    sys.exit(53)


def comparisons_functions(operator, var, symb1, symb2):
    result = False
    variable_parts = var.value.split("@")
    variable_parts_1 = symb1.value.split("@")
    variable_parts_2 = symb2.value.split("@")
    tmp = get_variable(variable_parts_1[0], variable_parts_1[1])
    tmp2 = get_variable(variable_parts_2[0], variable_parts_2[1])

    match tmp.type and tmp2.type:
        case "int":
            if operator == "LT":
                if tmp.value < tmp2.value:
                    result = ArgumentInstruction("bool", "true")
                else:
                    result = ArgumentInstruction("bool", "false")
            elif operator == "GT":
                if tmp.value > tmp2.value:
                    result = ArgumentInstruction("bool", "true")
                else:
                    result = ArgumentInstruction("bool", "false")
            elif operator == "EQ":
                if tmp.value == tmp2.value:
                    result = ArgumentInstruction("bool", "true")
                else:
                    result = ArgumentInstruction("bool", "false")

            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
        case "string":
            if operator == "LT":
                if tmp.value < tmp2.value:
                    result = ArgumentInstruction("bool", "true")
                else:
                    result = ArgumentInstruction("bool", "false")
            elif operator == "GT":
                if tmp.value > tmp2.value:
                    result = ArgumentInstruction("bool", "true")
                else:
                    result = ArgumentInstruction("bool", "false")
            elif operator == "EQ":
                if tmp.value == tmp2.value:
                    result = ArgumentInstruction("bool", "true")
                else:
                    result = ArgumentInstruction("bool", "false")

            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
        case "bool":
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
                if (tmp.value == "true" and tmp2.value == "true") or (tmp.value == "false" and tmp2.value == "false"):
                    result = ArgumentInstruction("bool", "true")
                else:
                    result = ArgumentInstruction("bool", "false")

            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)

    if operator == "EQ":
        if tmp.type == "nil" or tmp2.type == "nil":
            if tmp.type == "nil" and tmp2.type == "nil":
                if tmp.value == tmp2.value:
                    result = ArgumentInstruction("bool", "true")
                else:
                    result = ArgumentInstruction("bool", "false")
        else:
            result = ArgumentInstruction("bool", "false")
        var_exists(variable_parts[0], variable_parts[1])
        save_var(variable_parts[0], variable_parts[1], result)


def logical_functions(logic, var, symb1, symb2):
    result = False
    variable_parts = var.value.split("@")
    variable_parts_1 = symb1.value.split("@")
    tmp = get_variable(variable_parts_1[0], variable_parts_1[1])

    if logic == "NOT":
        if tmp.type == "bool":
            if tmp.value == "true":
                result = ArgumentInstruction("bool", "false")
            elif tmp.value == "false":
                result = ArgumentInstruction("bool", "true")
            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
        else:
            sys.exit(55)
        return

    variable_parts_2 = symb2.value.split("@")
    tmp2 = get_variable(variable_parts_2[0], variable_parts_2[1])
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
        sys.exit(55)


def int2char(var, number):
    variable_parts = var.value.split("@")
    variable_parts_1 = number.value.split("@")
    tmp = get_variable(variable_parts_1[0], variable_parts_1[1])

    if tmp.type == "int":
        string = chr(int(tmp.value))
        result = ArgumentInstruction("string", string)
        var_exists(variable_parts[0], variable_parts[1])
        save_var(variable_parts[0],variable_parts[1], result)
    else:
        sys.exit(58)


def string2int(var, symb1, symb2):
    variable_parts = var.value.split("@")
    variable_parts_1 = symb1.value.split("@")
    variable_parts_2 = symb2.value.split("@")
    tmp = get_variable(variable_parts_1[0], variable_parts_1[1])
    tmp2 = get_variable(variable_parts_2[0], variable_parts_2[1])

    if tmp.type == "string" and tmp2.type == "int" and tmp2.value <= len(tmp.value):
        result = ArgumentInstruction("char", ord(tmp.value[tmp2.value]))
        var_exists(variable_parts[0], variable_parts[1])
        save_var(variable_parts[0], variable_parts[1], result)
    else:
        sys.exit(58)


def read(var, input_name):
    variable_parts = var.value.split("@")
    empty_var = Variables("nil", "nil")

    if not input_name:
        input_string = input()
    else:
        f = open(input_name, "r")
        input_string = f.read()

    string_parts = input_string.split("@")
    tmp = Variables(string_parts[0], string_parts[1])

    if tmp.type == "bool" or "int" or "string":
        result = ArgumentInstruction(tmp.type, tmp.value)
        var_exists(variable_parts[0], variable_parts[1])
        save_var(variable_parts[0], variable_parts[1], result)
    else:
        result = ArgumentInstruction(empty_var.type, empty_var.value)
        var_exists(variable_parts[0], variable_parts[1])
        save_var(variable_parts[0], variable_parts[1], result)


def write(name):
    match name.type:
        case "bool":
            if name.value != "true":
                print("false", end='')
            else:
                print("true", end='')
        case "string":
            name.value = name.value.repalce("&amp", '&')
            name.value = name.value.repalce("&lt", '<')
            name.value = name.value.repalce("&gt", '>')
            name.value = name.value.repalce("\\032", ' ')
            print(name.value, end='')
        case "var":
            variable_parts = name.value.split("@")
            var = get_variable(variable_parts[0], variable_parts[1])
            if var.type == "string":
                var.value = var.value.repalce("&amp", '&')
                var.value = var.value.repalce("&lt", '<')
                var.value = var.value.repalce("&gt", '>')
                var.value = var.value.repalce("\\032", ' ')
            if var.value is not None:
                print(var.value, end='')
            else:
                print("", end='')
        case "nil":
            print("", end='')


def concat(var, symb1, symb2):
    variable_parts = var.value.split("@")
    variable_parts_1 = symb1.value.split("@")
    variable_parts_2 = symb2.value.split("@")
    tmp = get_variable(variable_parts_1[0], variable_parts_1[1])
    tmp2 = get_variable(variable_parts_2[0], variable_parts_2[1])

    if tmp.type == "string" and tmp2.type == "string":
        result = ArgumentInstruction("string", tmp.value + tmp2.value)
        var_exists(variable_parts[0], variable_parts[1])
        save_var(variable_parts[0], variable_parts[1], result)
    else:
        sys.exit(53)


def strlen_func(var, symb1):
    variable_parts = var.value.split("@")
    variable_parts_1 = symb1.value.split("@")
    tmp = get_variable(variable_parts_1[0], variable_parts_1[1])

    if tmp.value == "string":
        result = ArgumentInstruction("int", len(tmp.value))
        var_exists(variable_parts[0], variable_parts[1])
        save_var(variable_parts[0], variable_parts[1], result)
    else:
        sys.exit(53)


def get_char(var, symb1, symb2):
    variable_parts = var.value.split("@")
    variable_parts_1 = symb1.value.split("@")
    variable_parts_2 = symb2.value.split("@")
    tmp = get_variable(variable_parts_1[0], variable_parts_1[1])
    tmp2 = get_variable(variable_parts_2[0], variable_parts_2[1])

    if tmp.type == "string" and tmp2.type == "int":
        if tmp2.value <= len(tmp.value):
            result = ArgumentInstruction("string", tmp.value[tmp2.value])
            var_exists(variable_parts[0], variable_parts[1])
            save_var(variable_parts[0], variable_parts[1], result)
        else:
            sys.exit(58)
    else:
        sys.exit(53)


def set_char(var, symb1, symb2):
    variable_parts = var.value.split("@")
    variable_parts_1 = symb1.value.split("@")
    variable_parts_2 = symb2.value.split("@")
    tmp = get_variable(variable_parts_1[0], variable_parts_1[1])
    tmp2 = get_variable(variable_parts_2[0], variable_parts_2[1])

    if variable_parts[0] == "GF":
        if variable_parts[1] in GF.keys():
            if tmp2.type == "string" and tmp.type == "int":
                if tmp.value <= len(GF[variable_parts_1]):
                    var_exists(variable_parts[0], variable_parts[1])
                    GF[variable_parts_1].value[tmp.value] = tmp.value[0]
                else:
                    sys.exit(58)
            else:
                sys.exit(53)
        else:
            sys.exit(54)
    else:
        sys.exit(55)


def add_instruction_to_class(root):
    instruction_count = 0

    for element in root:
        instructions_list.append(Instruction(element.attrib['opcode'].upper(), instruction_count))

        for args in element:
            instructions_list[instruction_count].add_argument(args.attrib['type'].lower(), args.text)

        instruction_count += 1

    return instruction_count


def main():
    spot = 0
    input_parser = InputParser()
    source, inputName = input_parser.parse_argument()

    try:
        if not source:
            tree = ET.parse(sys.stdin)
        else:
            tree = ET.parse(source)
    except Exception:
        sys.exit(31)

    root = tree.getroot()
    xml_parser = XMLChecker(root)
    xml_parser.check_xml()

    # pridanie instrukcie do listu
    num_of_instr = add_instruction_to_class(root)

    # kolko mame instrukcii tolko krat volame Interpreter
    print("\nSTART OF INTERPRETER")
    while spot != num_of_instr:
        Interpreter(instructions_list[spot], inputName)
        spot += 1


if __name__ == '__main__':
    main()
