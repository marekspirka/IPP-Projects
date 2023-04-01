# Interpret 2nd project IPP
# Autor : Marek Spirka
# login : xspir01

import re
import sys
import xml.etree.ElementTree as ET


def wrong_arguments():
    print("Incorrect arguments. Try using [ --help ] argument.")
    sys.exit(10)


def print_help():
    print("############################################################################")
    print("Interpret of IPPcode23 language")
    print("Usage: python3.10 interpret.py [--help | --source=file | --input=file]")
    print("  --help         |   How to use interpret script")
    print("  --source=file  |   Source script for interpret")
    print("  --input=file   |   Input file for interpret")
    print("  without arguments script read from stdin")
    print("############################################################################")
    sys.exit(0)


def parser_argument():
    is_source = False
    is_input = False
    source = ""
    input = ""
    if len(sys.argv) != 0:
        for arg in sys.argv:
            if arg == "--help":
                print_help()
            elif "interpret.py" in arg:
                pass
            elif "--input=" in arg:
                if not is_input:
                    input = arg[8:]
                    is_input = True
                else:
                    wrong_arguments()
            elif "--source" in arg:
                if not is_source:
                    source = arg[9:]
                    is_source = True
                else:
                    wrong_arguments()
            else:
                wrong_arguments()
    else:
        wrong_arguments()

    if is_input != True and is_source != True:
        wrong_arguments()

    return source, input


def check_header(root):
    if root.tag != "program":
        sys.exit(32)
    if not ("language" in list(root.attrib.keys())):
        sys.exit(32)
    if not ("IPPcode23" in root.attrib['language']):
        sys.exit(32)


# zoradenie order podla cisiel
def line_up_order(root):
    try:
        root[:] = sorted(root, key=lambda child: int(child.attrib.get('order')))
    except Exception:
        sys.exit(32)


def check_xml(root):
    dup_order = 0
    for child in root:
        child_atribute = list(child.attrib.keys())
        if child.tag == "instruction":
            pass
        if "opcode" in child_atribute and "order" in child_atribute:
            pass
        if int(child.attrib.get('order')) > 0:
            pass
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


def main():
    source, inputName = parser_argument()

    try:
        if not source:
            tree = ET.parse(sys.stdin)
        else:
            tree = ET.parse(source)
    except Exception:
        sys.exit(31)

    root = tree.getroot()
    check_header(root)
    line_up_order(root)
    check_xml(root)


if __name__ == '__main__':
    main()
