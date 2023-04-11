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
        self.var_type = var_type
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


def Interpreter(instruction, inputName):
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
            print("RETURN")
        case "PUSHS":
            print("PUSHS")
        case "POPS":
            print("POPS")
        case "ADD":
            print("ADD")
        case "SUB":
            print("SUB")
        case "MUL":
            print("MUL")
        case "IDIV":
            print("IDIV")
        case "LT":
            print("LT")
        case "GT":
            print("GT")
        case "EQ":
            print("EQ")
        case "AND":
            print("AND")
        case "OR":
            print("OR")
        case "NOT":
            print("NOT")
        case "INT2CHAR":
            print("INT2CHAR")
        case "STRI2INT":
            print("STRI2INT")
        case "READ":
            print("READ")
        case "WRITE":
            print("WRITE")
        case "CONCAT":
            print("CONCAT")
        case "STRLEN":
            print("STRLEN")
        case "GETCHAR":
            print("GETCHAR")
        case "SETCHAR":
            print("SETCHAR")
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
    empty_var = Variables(None,None)
    match variable_parts[0]:
        case "LF":
            if len(LF) == 0:
                sys.exit(52)
            if not(variable_parts[1] in LF[len(LF)-1].keys()):
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
        spot = int(labels[arg.value]-1)
    else:
        sys.exit(52)


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
