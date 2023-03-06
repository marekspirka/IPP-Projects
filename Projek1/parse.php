<?php
//Meno: Marek Spirka
//xlogin: xspirk01

ini_set('display_errors', 'stderr');

$header = false;
$counter = 1;

if($argc > 1){
    if($argv[1] == "--help"){
        echo("\n");
        echo("================HELP==================\n");
        echo("\n");
        echo("Usage: parser.php [options] <inputFile\n");
        echo("\n");

        exit(0);
    }else{
        echo("Wrong numbers of arguments. Use parser.php --help for more info about usage of this program");
    }
}

//print header of XML program
echo('<?xml version="1.0" encoding ="UTF-8"?>');
echo("\n");

while($input = fgets(STDIN)){

    //deleted empty line from STDIN
    $input = preg_replace('/^\h*\v+/m', '', $input);

    //deleted line with comments 
    if(preg_match('/^\s*(#.*)?$/', $input)) {
        continue;
    }
    //deleted comments after commands 
    if(preg_match('/#.*/', $input)) {
        $input = preg_replace('/#.*/', "", $input);
    }

    //deleted horizontal spaces
    $input = trim($input);

    //Split each line to one array
    $line = preg_split('/\s+/', $input, -1, 0);

    //Check if is there header anf print header of XML program
    if($header == false && $counter == 1){
        if(preg_match("/^\.IPPcode23$/", $line[0])){
            $header = true;
            echo('<program language="IPPcode23">')."\n";
            continue;
        }else{
            echo('Wrong or missing header!');
            exit(21);
        }
    }

    switch($line[0] = strtoupper($line[0])){
        case '.IPPCODE23':
            fprintf(STDERR, "Wrong place of header!\n");;
            exit(22);
        //Check_Type1
        //pseduo: Command <label> <symb1> <symb2>
        case 'JUMPIFEQ':
        case 'JUMPIFNEQ':
            check_type1($line[0], $counter, $line[1], $line[2], $line[3], $line);
            $counter++;
            break;
        //Check_Type2
        //pseudo: Command <var> <symb1> <symb2>
        case 'SETCHAR':
        case 'GETCHAR':
        case 'CONCAT':
        case 'STRI2INT':
        case 'AND':
        case 'OR':
        case 'LT':
        case 'GT':
        case 'EQ':
        case 'IDIV':
        case 'MUL':
        case 'SUB':
        case 'ADD':
            check_type2($line[0], $counter, $line[1], $line[2], $line[3], $line);
            $counter++;
            break;

        //Check_Type3
        //pseudo: <command> <var> <symb>
        case 'TYPE':
        case 'STRLEN':
        case 'INT2CHAR':
        case 'NOT':
        case 'MOVE':
            check_type3($line[0], $counter, $line[1], $line[2], $line);
            $counter++;
            break;

        //Check_Type4
        //pseudo: <command> <var> <type>
        case 'READ':
            check_type4($line[0], $counter, $line[1], $line[2], $line);
            $counter++;
            break;

        //Check_Type5
        //pseudo: <command> <symb>
        case 'DPRINT':
        case 'EXIT':
        case 'WRITE':
        case 'PUSHS':
            check_type5($line[0], $counter, $line[1], $line);
            $counter++;
            break;

        //Check_Type6
        //pseudo: <command> <var>
        case 'POPS':
        case 'DEFVAR':
            check_type6($line[0], $counter, $line[1], $line);
            $counter++;
            break;
        //Check_Type7
        //pseudo: <command> <label>
        case 'JUMP':
        case 'LABEL':
        case 'CALL':
            check_type7($line[0], $counter, $line[1], $line);
            $counter++;
            break;
        //Check_Type8
        //pseudo: <command>
        case 'BREAK':
        case 'RETURN':
        case 'POPFRAME':
        case 'PUSHFRAME':
        case 'CREATEFRAME':
            check_type8($line[0], $counter, $line);
            $counter++;
            break;

        default:
        fprintf(STDERR, "Wrong Command, command ($line[0]) doesn't exists!\n");
        exit(22);   
    }
}

//print start of Commands
function start_of_command($command, $counter){
    echo('  <instruction order="'.$counter.'" opcode="'.$command.'">');
    echo("\n");
}

//print end of Commands
function end_of_command(){
    echo('  </instruction>');
    echo("\n");
}

//print arguments of Commands
function print_arguments($argument, $type, $number){
    $argument = preg_replace('/&/',"&amp;", $argument);
    $argument = preg_replace('/</',"&lt;", $argument);
    $argument = preg_replace('/>/',"&gt;", $argument);
    echo('      <arg'.$number.' type="'.$type.'">'.$argument.'</arg'.$number.'>');
    echo("\n");
}

//delete const from arguments
function check_const($const){
    return preg_replace('/^(nil|int|bool|string)@/', "", $const);
}

//check params with regex and then return type of params
function check_params($params){
    if(preg_match('/^(GF|LF|TF)@[a-zA-Z_$&%*!?-][a-zA-Z0-9_$&%*!?-]*$/', $params)){
        return 'var';
    }elseif(preg_match('/^(int|bool|string)$/', $params)){
        return 'type';
    }elseif(preg_match('/^[a-zA-Z_\-$&%*!?][\w\-$&%*!?]*$/', $params)){
        return 'label';
    }elseif (preg_match('/^nil@nil$/', $params)){
        return 'nil';
    }elseif (preg_match('/^int@[+\-]?\d+$/', $params)){
        return 'int';
    }elseif (preg_match('/^bool@(true|false)$/', $params)){
        return 'bool';
    }elseif (preg_match('/^string@(?:[^\s#\\\\]|\\\\\d{3})*$/', $params)){
        return 'string';
    }else{
        fprintf(STDERR, "Wrong format of parameter!");
        exit(23);
    }
}

//Control and print commands with three params
function check_type1($command, $counter, $label, $symbol1, $symbol2, $line){
    if(count($line) != 4){
        fprintf(STDERR, "Wrong number of arguments. Functions $command has 3 parameters!");
        exit(23);
    }elseif((strcmp(check_params($label),"label") == 0) && (strcmp(check_params($symbol1),"label") !== 0) && (strcmp(check_params($symbol2),"label") !== 0)){
       start_of_command($command, $counter);
       print_arguments($label, check_params($label), 1);
       print_arguments(check_const($symbol1), check_params($symbol1), 2);
       print_arguments(check_const($symbol2), check_params($symbol2), 3);
       end_of_command();
    }else{
        fprintf(STDERR, "Wrong format of parameter!");
        exit(23);
    }
}

//Control and print commands with three params
function check_type2($command, $counter, $var, $symbol1, $symbol2, $line){
    if(count($line) != 4){
        fprintf(STDERR, "Wrong number of arguments. Functions $command has 3 parameters!");
        exit(23);
    }elseif((strcmp(check_params($var),"var") == 0) && (strcmp(check_params($symbol1),"label") !== 0) && (strcmp(check_params($symbol2),"label") !== 0)){
       start_of_command($command, $counter);
       print_arguments($var , check_params($var), 1);
       print_arguments(check_const($symbol1), check_params($symbol1), 2);
       print_arguments(check_const($symbol2), check_params($symbol2), 3);
       end_of_command();
    }else{
        fprintf(STDERR, "Wrong format of parameter!");
        exit(23);
    }
}

//Control and print commands with two params
function check_type3($command, $counter, $var, $symbol, $line){
    if(count($line) != 3){
        fprintf(STDERR, "Wrong number of arguments. Functions $command has 2 parameters!");
        exit(23);
    }elseif((strcmp(check_params($var),"var") == 0) && (strcmp(check_params($symbol),"label") !== 0)){
       start_of_command($command, $counter);
       print_arguments($var, check_params($var), 1);
       print_arguments(check_const($symbol), check_params($symbol), 2);
       end_of_command();
    }else{
        fprintf(STDERR, "Wrong format of parameter!");
        exit(23);
    }
}

//Control and print commands with two params
function check_type4($command, $counter, $var, $type, $line){
    if(count($line) != 3){
        fprintf(STDERR, "Wrong number of arguments. Functions $command has 2 parameters!");
        exit(23);
    }elseif((strcmp(check_params($var),"var") == 0) && (strcmp(check_params($type), "type") == 0)){
       start_of_command($command, $counter);
       print_arguments($var, check_params($var), 1);
       print_arguments($type, check_params($type), 2);
       end_of_command();
    }else{
        fprintf(STDERR, "Wrong format of parameter!");
        exit(23);
    }
}

//Control and print commands with one params
function check_type5($command, $counter, $symbol, $line){
    if(count($line) != 2){
        fprintf(STDERR, "Wrong number of arguments. Functions $command has 1 parameters!");
        exit(23);
    }elseif((strcmp(check_params($symbol),"label") !== 0)){
       start_of_command($command, $counter);
       print_arguments(check_const($symbol), check_params($symbol), 1);
       end_of_command();
    }else{
        fprintf(STDERR, "Wrong format of parameter!");
        exit(23);
    }
}

//Control and print commands with one params
function check_type6($command, $counter, $var, $line){
    if(count($line) != 2){
        fprintf(STDERR, "Wrong number of arguments. Functions $command has 1 parameters!");
        exit(23);
    }elseif(strcmp(check_params($var), "var") == 0){
       start_of_command($command, $counter);
       print_arguments($var, check_params($var), 1);
       end_of_command();
    }else{
        fprintf(STDERR, "Wrong format of parameter!");
        exit(23);
    }
}

//Control and print commands with one params
function check_type7($command, $counter, $label, $line){
    if(count($line) != 2){
        fprintf(STDERR, "Wrong number of arguments. Functions $command has 1 parameters!");
        exit(23);
    }elseif(strcmp(check_params($label), "label") == 0){
       start_of_command($command, $counter);
       print_arguments($label, check_params($label), 1);
       end_of_command();
    }else{
        fprintf(STDERR, "Wrong format of parameter!");
        exit(23);
    }
}

//Control and print commands with zero params
function check_type8($command, $counter, $line){
    if(count($line) != 1){
        fprintf(STDERR, "Wrong number of arguments. Functions $command has 0 parameters!");
        exit(23);
    }
    start_of_command($command, $counter);
    end_of_command();
}
//End of XML program
echo('</program>');

?>