Implementační dokumentace k 1. úloze do IPP 2022/2023
Jméno a příjmení: Marek Špirka
Login: xspirk01

##Processing and analysis of input code IPPcode23
###Loading input
First, we read the input source code line by line in the program 'parse.php'. We will remove empty lines, line comments and comments after instructions from the given lines. Subsequently, we replace the unknown characters for XML, that is, the characters '&,<,>' and replace them with '&amp; ,&lt; ,&gt;'.

###Processing input
The line is then divided into words with which we work. Subsequently, the switch works with the first word, it is determined whether it is a header or one of the instructions.

Instructions are divided into groups according to the number and type of parameters they work with. If the program does not find the given instruction, error code 22 is called. 

###Analysis input
If we find an instruction that matches our instruction set, we call a function that checks the correctness of the arguments of the given instruction. The number of arguments and the correct argument type are checked. If the given argument is incorrect, the program returns error 23.

##Running the program 
The program is started by entering the following instructions and parameters on the command line:
        php parse.php <[filepath] or php8.1 (or your version) parse.php <[filepath] 
    Example:
        php parse.php <test.src