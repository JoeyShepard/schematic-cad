#!/usr/bin/env python3

from sys import path, argv
#from os.path import expanduser
#path.append(expanduser("~/python/"))
#from color import *

#Globals
global_stack=[]
global_chips={}
global_filenum=0
global_element=None
global_element_stack=[]
global_symbols={}
global_sizes={}
global_x=0
global_y=0

#Class definition
class ChipClass:
    global global_x
    global global_y

    def __init__(self):
        self.kind="chip"
        self.name=""
        self.model=""
        self.pkg=None
        self.x=global_x
        self.y=global_y
        self.width=None
        self.height=None

    def debug(self):
        debug_msg=f"Chip '{self.name}' at ({self.x},{self.y})"
        attr_list=["model","pkg"]
        for attr in attr_list:
            if getattr(self,attr):
                debug_msg+=", "+getattr(self,attr)
        if self.width!=None or self.height!=None:
            debug_msg+=", "
            debug_msg+="?" if self.width==None else str(self.width)
            debug_msg+="x"
            debug_msg+="?" if self.height==None else str(self.height)
        return debug_msg
    
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

#Execute built-in words
#(If structure here is very, very ugly but no multi-line lambdas in Python :/ )
def exec_word(word):
    global global_element
    global global_x, global_y

    #Words not case sensitive
    word=word.lower()

    #Stack words
    if word=="drop":
        check_args(word,1)
        global_stack.pop()
    elif word=="dup":
        check_args(word,1)
        global_stack.append(global_stack[-1])
    elif word=="swap":
        check_args(word,2)
        a=global_stack.pop()
        b=global_stack.pop()
        global_stack.append(a)
        global_stack.append(b)
    
    #Arithmetic words
    elif word=="+":
        check_args(word,2,[["number"],["number"]])
        _,tos=global_stack.pop()
        _,nos=global_stack.pop()
        global_stack.append(("number",nos+tos))
    elif word=="-":
        check_args(word,2,[["number"],["number"]])
        _,tos=global_stack.pop()
        _,nos=global_stack.pop()
        global_stack.append(("number",nos-tos))
    elif word=="*":
        check_args(word,2,[["number"],["number"]])
        _,tos=global_stack.pop()
        _,nos=global_stack.pop()
        global_stack.append(("number",nos*tos))
    elif word=="/":
        check_args(word,2,[["number"],["number"]])
        _,tos=global_stack.pop()
        _,nos=global_stack.pop()
        global_stack.append(("number",int(nos/tos)))

    #Misc words
    elif word=="def":
        check_args(word,2,[["string"],"any"])
        _,obj_name=global_stack.pop()
        global_symbols[obj_name.lower()]=global_stack.pop()
    elif word=="nl":
        print()
    elif word==".":
        check_args(word,1)
        obj_type,obj_val=global_stack.pop()
        print(str(obj_val)+" ",end="")
    elif word==".s":
        if global_stack:
            for i in range(len(global_stack)):
                obj_type,obj_val=global_stack[-(i+1)]
                if obj_type=="string":
                    print(f'{i}: "{obj_val}"')
                elif obj_type=="number":
                    print(f'{i}: {obj_val}')
        else:
            print("(empty)")
    
    #Chip building words
    elif word=="chip":
        if global_element==None:
            #Topmost level (ie not defining chip or wire) so ok to start chip definition
            global_element=ChipClass()
        else:
            error_exit(f"can't begin chip inside of existing {global_element.kind}")
    elif word=="end":
        if global_element==None:
            #End without begininng CHIP or WIRE
            error_exit("END without matching CHIP or WIRE")
        elif global_element.kind=="chip":
            chip_name=global_element.name
            if global_element.name=="":
                error_exit("chip missing name")
            if global_element.pkg==None and global_element.width:
                #Assign DIPxx based on width if none assigned
                global_element.pkg=f"DIP{global_element.width}"
            #Add symbols for edges of chip
            obj_width=0 if global_element.width==None else global_element.width
            obj_height=0 if global_element.height==None else global_element.height
            symbol_list=(
                ("left",    global_element.x),
                ("right",   global_element.x+obj_width),
                ("top",     global_element.y),
                ("bottom",  global_element.y+obj_height),
                ("width",   obj_width),
                ("height",  obj_height)
                )
            for symbol in symbol_list:
                sym_name,sym_val=symbol
                global_symbols[chip_name.lower()+"."+sym_name]=("number",sym_val)
                global_symbols["last."+sym_name]=("number",sym_val)
            #Set X,Y of next chip to X,Y of current
            global_x=global_element.x
            global_y=global_element.y
            #Add to list of chips
            global_chips[chip_name]=global_element
            global_element=None
    elif word in ["model","name","pkg"]:
        check_element(word)
        check_args(word,1,[["string"]])
        obj_type,obj_val=global_stack.pop()
        if word=="name" and obj_val in global_chips:
            error_exit(f"chip named '{obj_val}' already exists") 
        elif word=="model":
            obj_val=obj_val.upper()
            if obj_val in global_sizes:
                global_element.width,global_element.height=global_sizes[obj_val]
        setattr(global_element,word,obj_val)
    elif word in ["left","right"]:
        check_element(word,"x")
        check_args(word,1,[["number"]])
        obj_type,obj_val=global_stack.pop()
        new_x=global_element.x
        global_element.x=new_x-obj_val if word=="left" else new_x+obj_val
    elif word in ["up","down"]:
        check_element(word,"y")
        check_args(word,1,[["number"]])
        obj_type,obj_val=global_stack.pop()
        new_y=global_element.y
        global_element.y=new_y-obj_val if word=="up" else new_y+obj_val
    elif word=="x":
        if global_element:
            check_element(word,"x")
            check_args(word,1,[["number"]])
            _,global_element.x=global_stack.pop()
        else:
            check_args(word,1,[["number"]])
            _,global_x=global_stack.pop()
    elif word=="y":
        if global_element:
            check_element(word,"y")
            check_args(word,1,[["number"]])
            _,global_element.y=global_stack.pop()
        else:
            check_args(word,1,[["number"]])
            _,global_y=global_stack.pop()
    elif word=="width":
        check_element(word)
        check_args(word,1,[["number"]])
        _,global_element.width=global_stack.pop()
    elif word=="height":
        check_element(word)
        check_args(word,1,[["number"]])
        _,global_element.height=global_stack.pop()
    elif word=="size":
        #Size of 74xx chip, not chip defined in file
        check_args(word,3,[["string"],["number"],["number"]])
        _,obj_name=global_stack.pop()
        _,obj_height=global_stack.pop()
        _,obj_width=global_stack.pop()
        global_sizes[obj_name.upper()]=(obj_width,obj_height)
    else:
        #Word not found!
        return False
    
    #Word found and executed above
    return True

#Check arg count and arg type
def check_args(word,arg_count,arg_types_list=()):
    #Enough args on stack for word?
    if len(global_stack)<arg_count:
        error_exit(f"{arg_count} arguments expected for {word} but {len(global_stack)} found")
        exit(1)

    #Argument types match?
    for i,arg_types in enumerate(arg_types_list):
        if arg_types=="any":
            pass
        else:
            stack_arg_type=global_stack[-(i+1)][0]
            if stack_arg_type not in arg_types:
                error_exit(f"expected types {arg_types} for argument {i+1} of {word} but found '{stack_arg_type}'")

    #Reached end of function without exiting - success

#Check that currently in definition and that element being defined posseses attribute
def check_element(word,attribute=""):
    if not attribute:
        attribute=word
    if global_element==None:
        error_exit(f"{word} not valid outside of definition")
    elif not hasattr(global_element,attribute):
        error_exit(f"{global_element.kind} does not have attribute '{attribute}' accessed from {word}")

    #Reached end of function without exiting - success

#Error exit function to be called from anywhere
def error_exit(message):
    print(f"Error in {argv[1]} on line {global_filenum+1} - {message}")
    exit(1)

#Loop through lines in file and evaluate
for global_filenum,line in enumerate(file_lines):
    quoting=False
    for word in line.split():
        if not quoting:
            #Not building quoted string - normal input
            if word[0]==";":
                #Comment - stop processing line
                break
            elif word.isnumeric():
                #Input is number - push to stack
                global_stack.append(("number",int(word)))
            elif word[0]=='"':
                if word[-1]=='"' and word!='"':
                    #Input is single word with beginning and ending quotes - push to stack
                    global_stack.append(("string",word[1:-1]))
                else:
                    #Input is beginning of string - start quoting string
                    quoted_string=word[1:]
                    quoting=True
            elif word.lower() in global_symbols:
                global_stack.append(global_symbols[word.lower()])
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
    print("Error: finished processing file but data stack not empty:")
    exec_word(".s")
    exit(1)
elif global_element!=None:
    #Currently defined element missing END
    print(f"Error: finished processing file but missing END statement")
    exit(1)
elif global_element_stack:
    #Unfinished items on element stack
    print(f"Error: finished processing file but {len(global_element_stack)} unfinished elements:")
    for i in range(len(global_element_stack)):
        element=global_element_stack[-(i+1)]
        if element.kind=="chip":
            print(f"{i}: {element.kind} '{element.name}'")
        else:
            print(f"{i}: {element.kind}")
    exit(1)

#See defined chips
for i,chip in enumerate(global_chips):
    print(f"{i}: {global_chips[chip].debug()}")



