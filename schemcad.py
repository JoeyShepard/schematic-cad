#!/usr/bin/env python3

from sys import path, argv
#from os.path import expanduser
#path.append(expanduser("~/python/"))
#from color import *

#Globals
global_stack=[]
global_chips=[]
global_filenum=0
global_element=None
global_element_stack=[]
global_x=3
global_y=3

#Class definition
class ChipClass:
    global global_x
    global global_y

    def __init__(self):
        self.kind="chip"
        self.name=""
        self.x=global_x
        self.y=global_y

    def debug(self):
        print(f"Chip '{self.name}' at ({self.x},{self.y})")
    
class WireClass:
    def __init__(self):
        self.kind="wire"
        self.name=""

#Filename supplied as argument on command line?
if len(argv)==1:
    print("Error: missing filename")
    exit(1)

#Too many command line arguments?
if len(argv)>2:
    print("Error: too many arguments")
    exit(1)

#Open input file and exit if it doesn't exist
try:
    with open(argv[1]) as f:
        file_lines=f.readlines()
except:
    print("Error: unable to open file")
    exit(1)

#Execution of built-in words
#(If structure here is very, very ugly but no multi-line lambdas in Python :/ )
def exec_word(word):
    global global_element
    
    #Words not case sensitive
    word=word.upper()

    #Stack words
    if word=="DROP":
        check_args(word,1)
        global_stack.pop()
    elif word=="DUP":
        check_args(word,1)
        global_stack.append(global_stack[-1])
    elif word=="SWAP":
        check_args(word,2)
        a=global_stack.pop()
        b=global_stack.pop()
        global_stack.append(a)
        global_stack.append(b)
    #Arithmetic words
    #Misc words
    elif word=="NL":
        print()
    elif word==".":
        check_args(word,1)
        obj_type,obj_val=global_stack.pop()
        print(str(obj_val)+" ",end="")
    elif word==".S":
        if global_stack:
            for i in range(len(global_stack)):
                obj_type,obj_val=global_stack[-(i+1)]
                print(f"{i}: {obj_val}")
        else:
            print("(empty)")
    #Chip building words
    elif word=="CHIP":
        if global_element==None:
            #Topmost level (ie not defining chip or wire) so ok to start chip definition
            global_element=ChipClass()
        else:
            error_exit("can't begin chip inside of existing {global_element.kind}")
    elif word=="END":
        if global_element==None:
            #End without begininng CHIP or WIRE
            error_exit("END without matching CHIP or WIRE")
        elif global_element.kind=="chip":
            #TODO: check chip has name etc
            global_chips.append(global_element)
            global_element=None

    else:
        #Word not found!
        return False
    
    #Word found and executed above
    return True

#Check arg count and arg type
def check_args(word,arg_count,arg_types=()):
    #Enough args on stack for word?
    if len(global_stack)<arg_count:
        error_exit(f"{arg_count} arguments expected for {word} but only {len(global_stack)} found")
        exit(1)

    #Argument types match?
    for i,arg_type in enumerate(arg_types):
        if arg_type=="any":
            pass
        else:
            stack_arg_type=global_stack[-(i+1)][0]
            if stack_arg_type!=arg_type:
                error_exit(f"expected type '{arg_type}' for argument {i+1} of {word} but found '{stack_arg_type}'")
                exit(1)

#Error exit function to be called from anywhere
def error_exit(message):
    print(f"Error in {argv[1]} on line {global_filenum+1} - {message}")
    exit(1)

#Loop through lines in file and evaluate
for global_filenum,line in enumerate(file_lines):
    quoting=False
    for word in line.split():
        if not quoting:
            #Not building quoted string
            if word.isnumeric():
                #Input is number - push to stack
                global_stack.append(("number",int(word)))
            elif word[0]=='"':
                #Input is string - start quoting string
                quoted_string=word[1:]
                quoting=True
            else:
                #Input not recognized - check and execute if builtin word
                if not exec_word(word):
                    #Word not found
                    error_exit(f"unrecognized word '{word}'")
        else:
            #Quoting string - add words to string
            if word[-1]=='"':
                #Ending quote found - push string to stack
                quoted_string+=" "+word[:-1]
                global_stack.append(("string",quoted_string))
                quoting=False
            else:
                quoted_string+=" "+word

    #Finished looping through words on line but string not terminated
    if quoting:
        error_exit("unterminated string at end of input line")

#Finished looping through file
if global_stack:
    #Data left on stack - something is probably wrong
    print("finished processing file but data stack not empty")
    exit(1)
elif global_element!=None:
    #Currently defined element missing END
    print(f"finished processing file but missing END statement")
    exit(1)
elif global_element_stack:
    #Unfinished items on element stack
    print(f"finished processing file but {len(global_element_stack)} unfinished elements:")
    for i in range(len(global_element_stack)):
        element=global_element_stack[-(i+1)]
        if element.kind=="chip":
            print(f"{i}: {element.kind} '{element.name}'")
        else:
            print(f"{i}: {element.kind}")
    exit(1)

#See defined chips
for i,chip in enumerate(global_chips):
    print(f"{i}: ",end="")
    chip.debug()
