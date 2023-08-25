#!/usr/bin/env python3

from sys import path, argv
from math import ceil
#from os.path import expanduser
#path.append(expanduser("~/python/"))
#from color import *

#Constants
CHIP_BORDER_WIDTH=2
GRID_LINE_WIDTH=1
WIRE_WIDTH=2
OUTPUT_FILE="./output.html"

#Globals
global_stack=[]
global_chips={}
global_filenum=0
global_element=None
global_symbols={}
global_sizes={}
global_x=0
global_y=0
global_grid_pixels=10
global_grid_margin=0
global_wire_list=[]
global_label_list=[]
global_jump_list=[]
global_colors={}
global_max_right=2
global_max_bottom=2
global_title_size=12
global_subtitle_size=10
global_label_size=10
global_font_name="sans serif"

#Initliazing globals
global_colors["chip-color"]=0x404040
global_colors["wire-color"]=0xFFFFFF
global_colors["label-color"]=0xFFFFFF
global_colors["border-color"]=0xFFFFFF
global_colors["title-color"]=0xFFFFFF
global_colors["subtitle-color"]=0xC0C0C0
global_colors["bg-color"]=0
global_colors["grid-color"]=0x404040
temp_color_list={
    "red":      0xFF0000,
    "green":    0xFF00,
    "blue":     0xFF,
    "magenta":  0xFF00FF,
    "yellow":   0xFFFF00,
    "cyan":     0xFFFF,
    "black":    0,
    "white":    0xFFFFFF,
    "gray40":   0x404040,
    "gray80":   0x808080,
    "grayc0":   0xC0C0C0
    }
for name,val in temp_color_list.items():
    global_symbols[name]=("number",val)

#Class definition
class ChipClass:
    global global_x
    global global_y
    global global_colors

    def __init__(self):
        self.kind="chip"
        self.name=""
        self.model=""
        self.pkg=None
        self.x=global_x
        self.y=global_y
        self.width=None
        self.height=None
        self.color=global_colors["chip-color"]
        self.border_color=global_colors["border-color"]
        self.title_color=global_colors["title-color"]
        self.subtitle_color=global_colors["subtitle-color"]

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
    global global_colors

    def __init__(self):
        self.kind="wire"
        self.x=0
        self.y=0
        self.lastx=None
        self.lasty=None
        self.color=global_colors["wire-color"] 

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
    global global_grid_pixels
    global global_grid_margin
    global global_colors
    global global_max_right
    global global_max_bottom
    global global_title_size
    global global_subtitle_size
    global global_label_size
    global global_font_name
    
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
        global_stack.append(("number",nos/tos))
    elif word=="mid":
        #Mid point between two values
        check_args(word,2,[["number"],["number"]])
        _,tos=global_stack.pop()
        _,nos=global_stack.pop()
        min_obj=min(tos,nos)
        max_obj=max(tos,nos)
        global_stack.append(("number",min_obj+(max_obj-min_obj)/2))
    elif word=="int":
        check_args(word,1,[["number"]])
        _,tos=global_stack.pop()
        global_stack.append(("number",int(tos)))

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
    elif word==".$":
        #Print number as hex
        check_args(word,1,["number"])
        obj_type,obj_val=global_stack.pop()
        print("0x"+hex(obj_val)[2:].upper()+" ",end="")
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
    elif word==".s$":
        if global_stack:
            for i in range(len(global_stack)):
                obj_type,obj_val=global_stack[-(i+1)]
                if obj_type=="string":
                    print(f'{i}: "{obj_val}"')
                elif obj_type=="number":
                    print(f'{i}: 0x{hex(obj_val)[2:]}')
        else:
            print("(empty)")
    
    #Chip building words
    elif word=="chip":
        if global_element==None:
            #Topmost level (ie not defining chip or wire) so ok to start chip definition
            global_element=ChipClass()
        else:
            error_exit(f"can't begin chip inside of existing {global_element.kind}")
    elif word=="wire":
        if global_element==None:
            #Topmost level (ie not defining chip or wire) so ok to start chip definition
            global_element=WireClass()
        else:
            error_exit(f"can't begin wire inside of existing {global_element.kind}")
    elif word=="end":
        if global_element==None:
            #End without begininng CHIP or WIRE
            error_exit("END without matching CHIP or WIRE")
        elif global_element.kind=="chip":
            chip_name=global_element.name
            if global_element.name=="":
                error_exit("chip missing name")
            if global_element.width==None or global_element.height==None:
                error_exit("chip missing width or height and could not derive from model name")
            if global_element.pkg==None and global_element.width:
                #Assign DIPxx based on width if none assigned
                global_element.pkg=f"DIP{global_element.width}"
            #Add symbols for edges of chip
            obj_width=0 if global_element.width==None else global_element.width
            obj_height=0 if global_element.height==None else global_element.height
            symbol_list=(
                ("left",        global_element.x),
                ("right",       global_element.x+obj_width),
                ("top",         global_element.y),
                ("bottom",      global_element.y+obj_height),
                ("x-center",    global_element.x+obj_width/2),
                ("y-center",    global_element.y+obj_height/2),
                ("width",       obj_width),
                ("height",      obj_height)
                )
            for symbol in symbol_list:
                sym_name,sym_val=symbol
                global_symbols[chip_name.lower().replace(" ","-")+"."+sym_name]=("number",sym_val)
                global_symbols["last."+sym_name]=("number",sym_val)
                #Record furthest edge for image output
                if sym_name=="right":
                    global_max_right=max(sym_val,global_max_right)
                if sym_name=="bottom":
                    global_max_bottom=max(sym_val,global_max_bottom)
            #Set X,Y of next chip to X,Y of current
            global_x=global_element.x
            global_y=global_element.y
            #Add to list of chips
            global_chips[chip_name]=global_element
        elif global_element.kind=="wire":
            pass
        if global_stack:
            #Data left on stack - something is probably wrong
            error_exit(f"finished {global_element.kind} block but data stack not empty:",False)
            exec_word(".s")
            exit(1)
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
            check_element(word)
            check_args(word,1,[["number"]])
            _,global_element.x=global_stack.pop()
        else:
            check_args(word,1,[["number"]])
            _,global_x=global_stack.pop()
    elif word=="y":
        if global_element:
            check_element(word)
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
    elif word=="mark":
        if global_element==None or global_element.kind!="wire":
            error_exit(f"{word} not valid outside of wire definition")
        global_element.lastx=global_element.x
        global_element.lasty=global_element.y
    elif word in ["point","ljump","rjump"]:
        if global_element==None or global_element.kind!="wire":
            error_exit(f"{word} not valid outside of wire definition")
        global_wire_list.append((global_element.color,(global_element.x,global_element.y),
            (global_element.lastx,global_element.lasty)))
        global_element.lastx=global_element.x
        global_element.lasty=global_element.y
        global_max_right=max(global_element.x,global_max_right)
        global_max_bottom=max(global_element.y,global_max_bottom)
        if word=="ljump":
            global_jump_list.append((global_element.color,(global_element.x,global_element.y),"left"))
            global_element.x-=2
            global_element.lastx-=2
        elif word=="rjump":
            global_jump_list.append((global_element.color,(global_element.x,global_element.y),"right"))
            global_element.x+=2
            global_element.lastx+=2
    elif word=="label":
        if global_element==None or global_element.kind!="wire":
            error_exit(f"{word} not valid outside of wire definition")
        check_args(word,1,[["string"]])
        _,tos=global_stack.pop()
        global_label_list.append((global_element.color,(global_element.x,global_element.y),tos))
    elif word=="size":
        #Size of 74xx chip, not chip defined in file
        check_args(word,3,[["string"],["number"],["number"]])
        _,obj_name=global_stack.pop()
        _,obj_height=global_stack.pop()
        _,obj_width=global_stack.pop()
        global_sizes[obj_name.upper()]=(obj_width,obj_height)
    elif word=="pushxy":
        check_element(word,"x")
        check_element(word,"y")
        global_stack.append(("number",global_element.x))
        global_stack.append(("number",global_element.y))
    elif word=="popxy":
        check_element(word,"x")
        check_element(word,"y")
        check_args(word,2,[["number"],["number"]])
        _,tos=global_stack.pop()
        _,nos=global_stack.pop()
        global_element.y=tos
        global_element.x=nos

    #Color setting and grid words
    elif word=="rgb":
        check_args(word,3,[["number"],["number"],["number"]])
        _,blue=global_stack.pop()
        _,green=global_stack.pop()
        _,red=global_stack.pop()
        global_stack.append(("number",(red<<16)+(green<<8)+blue))
    elif word in ["color","border-color","title-color","subtitle-color"]:
        #Can't have dash in python attribute name so change to underscore
        modified_word=word.replace("-","_")
        if global_element:
            #Within defintion - apply to defintion
            check_element(modified_word)
            check_args(word,1,[["number"]])
            _,tos=global_stack.pop()
            setattr(global_element,modified_word,tos)
        else:
            #Outside of defintion - set as default color
            if word in global_colors:
                #General or default color
                check_args(word,1,[["number"]])
                _,tos=global_stack.pop()
                global_colors[word]=tos
            else:
                #Word only applies in definition not generally - probably 'color' attribute
                error_exit(f"{word} not valid outside of CHIP or WIRE definition")
    elif word in ["chip-color","wire-color","label-color","bg-color","grid-color"]:
        #General and default colors - not specific to particular CHIP or WIRE
        check_args(word,1,[["number"]])
        _,tos=global_stack.pop()
        global_colors[word]=tos
    elif word=="pixels":
        #Pixels per grid square
        check_args(word,1,[["number"]])
        _,global_grid_pixels=global_stack.pop()
    elif word=="margin":
        #Margin in grid squares on sides of schematic
        check_args(word,1,[["number"]])
        _,global_grid_margin=global_stack.pop()
    elif word=="title-size":
        check_args(word,1,[["number"]])
        _,global_title_size=global_stack.pop()
    elif word=="subtitle-size":
        check_args(word,1,[["number"]])
        _,global_subtitle_size=global_stack.pop()
    elif word=="label-size":
        check_args(word,1,[["number"]])
        _,global_label_size=global_stack.pop()
    elif word=="font-name":
        check_args(word,1,[["string"]])
        _,global_font_name=global_stack.pop()
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
    return

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
def error_exit(message,exit_program=True):
    print(f"Error in {argv[1]} on line {global_filenum+1} - {message}")
    if exit_program:
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

#Output to SVG
try:
    with open(OUTPUT_FILE,"wt") as f:
        #Just check file can be opened
        pass
except:
    print(f"Error: unable to open {OUTPUT_FILE}")
    exit(1)

def rgb_decomp(color):
    red=(color&0xFF0000)>>16
    green=(color&0xFF00)>>8
    blue=color&0xFF
    return red,green,blue 

with open(OUTPUT_FILE,"wt") as f:
    margin=global_grid_margin*global_grid_pixels
    global_max_bottom=int(ceil(global_max_bottom))
    global_max_right=int(ceil(global_max_right))

    #HTML boilerplate
    f.write("<!DOCTYPE html>\n")
    f.write("<html>\n")
    f.write("<body>\n")

    #SVG - size and color
    svg_width=(global_max_right+global_grid_margin*2)*global_grid_pixels+GRID_LINE_WIDTH
    svg_height=(global_max_bottom+global_grid_margin*2)*global_grid_pixels+GRID_LINE_WIDTH
    f.write("<svg ")
    f.write(f'width="{svg_width}" height="{svg_height}" ')
    r,g,b=rgb_decomp(global_colors["bg-color"])
    f.write(f'style="background-color:rgb({r},{g},{b})" ')
    f.write(">\n\n")
  
    #Draw rectangle for background color when exporting to PNG
    #Redundant but both Inkscape and ImageMagick are bugged :/
    f.write('<!--Background rectangle-->\n')
    f.write("<rect ")
    f.write('x="0" y="0" ')
    f.write(f'width="{svg_width}" ')
    f.write(f'height="{svg_height}" ')
    r,g,b=rgb_decomp(global_colors["bg-color"])
    f.write(f'style="fill:rgb({r},{g},{b});" ')
    f.write("/>\n\n")

    #Draw grid lines
    f.write('<!--Grid lines-->\n')
    r,g,b=rgb_decomp(global_colors["grid-color"])
    line_color=f"rgb({r},{g},{b})"
    for i in range(global_max_bottom+global_grid_margin*2+1):
        line_y=i*global_grid_pixels
        f.write(f'<line x1="0" y1="{line_y}" x2="{svg_width}" y2="{line_y}" ')
        f.write(f'style="stroke:{line_color};stroke-width:1" ')
        f.write('/>\n')
    for i in range(global_max_right+global_grid_margin*2+1):
        line_x=i*global_grid_pixels
        f.write(f'<line x1="{line_x}" y1="0" x2="{line_x}" y2="{svg_height}" ')
        f.write(f'style="stroke:{line_color};stroke-width:{GRID_LINE_WIDTH}" ')
        f.write('/>\n')
    f.write("\n")
     
    #Draw chips
    for name,chip in global_chips.items():
        f.write(f'<!--Chip: {chip.name}-->\n')
        #Chip body
        f.write('<rect ') 
        f.write(f'x="{chip.x*global_grid_pixels+margin}" ')
        f.write(f'y="{chip.y*global_grid_pixels+margin}" ')
        f.write(f'width="{chip.width*global_grid_pixels}" ')
        f.write(f'height="{chip.height*global_grid_pixels}" ')
        r,g,b=rgb_decomp(chip.color)
        f.write(f'style="fill:rgb({r},{g},{b});')
        f.write(f'stroke-width:{CHIP_BORDER_WIDTH};')
        r,g,b=rgb_decomp(chip.border_color)
        f.write(f'stroke:rgb({r},{g},{b})" ')
        f.write("/>\n")
        #Chip title
        f.write('<text ')
        f.write(f'x="{int((chip.x+chip.width/2)*global_grid_pixels+margin)}" ')
        if chip.model:
            f.write(f'y="{int((chip.y+chip.height/3)*global_grid_pixels+margin)}" ')
        else:
            f.write(f'y="{int((chip.y+chip.height/2)*global_grid_pixels+margin)}" ')
        f.write('dominant-baseline="middle" text-anchor="middle" ')
        r,g,b=rgb_decomp(chip.title_color)
        f.write(f'style="font: {global_title_size}px {global_font_name}; fill: rgb({r},{g},{b});" ')
        f.write(">\n")
        f.write(f'{chip.name}')
        f.write("</text>\n")
        #Chip subtitle
        if chip.model:
            f.write('<text ')
            f.write(f'x="{int((chip.x+chip.width/2)*global_grid_pixels+margin)}" ')
            f.write(f'y="{int((chip.y+chip.height/4*3)*global_grid_pixels+margin)}" ')
            f.write('dominant-baseline="middle" text-anchor="middle" ')
            r,g,b=rgb_decomp(chip.subtitle_color)
            f.write(f'style="font: {global_subtitle_size}px {global_font_name}; fill: rgb({r},{g},{b});" ')
            f.write(">\n")
            f.write(f'{chip.model}')
            f.write("</text>\n")
        f.write('\n')

    #Draw wires
    f.write("<!--Wires-->\n")
    for color,coords,coords2 in global_wire_list:
        f.write('<line ')
        f.write(f'x1="{coords[0]*global_grid_pixels+margin}" ')
        f.write(f'y1="{coords[1]*global_grid_pixels+margin}" ')
        f.write(f'x2="{coords2[0]*global_grid_pixels+margin}" ')
        f.write(f'y2="{coords2[1]*global_grid_pixels+margin}" ')
        r,g,b=rgb_decomp(color)
        f.write(f'style="stroke:rgb({r},{g},{b});stroke-width:{WIRE_WIDTH};" ')
        f.write('/>\n')
    f.write('\n')

    #Draw wire jumps
    f.write("<!--Wire jumps-->\n")
    for color,coords,direction in global_jump_list:
        f.write(f'<path d="M {coords[0]*global_grid_pixels+margin} {coords[1]*global_grid_pixels+margin} ')
        f.write(f'A{global_grid_pixels} {global_grid_pixels}, 0, 0, ')
        if direction=="left":
            f.write('0, ')
            f.write(f'{(coords[0]-2)*global_grid_pixels+margin} {coords[1]*global_grid_pixels+margin}" ')
        elif direction=="right":
            f.write('1, ')
            f.write(f'{(coords[0]+2)*global_grid_pixels+margin} {coords[1]*global_grid_pixels+margin}" ')
        r,g,b=rgb_decomp(color)
        f.write(f'stroke="rgb({r},{g},{b})" stroke-width="{WIRE_WIDTH}" fill="none" />\n')
    f.write('\n')

    #Draw wire labels
    f.write("<!--Wire labels-->\n")
    for color,coords,text in global_label_list:
        f.write('<text ')
        f.write(f'x="{int(coords[0]*global_grid_pixels+margin)}" ')
        f.write(f'y="{int(coords[1]*global_grid_pixels+margin)}" ')
        f.write('dominant-baseline="middle" text-anchor="middle" ')
        r,g,b=rgb_decomp(global_colors["label-color"])
        f.write(f'style="font: {global_label_size}px {global_font_name}; fill: rgb({r},{g},{b});" ')
        f.write(">\n")
        f.write(f'{text}')
        f.write("</text>\n")

    #SVG done
    f.write("</svg>\n")

    #HTML done
    f.write("</body>\n")
    f.write("</html>\n")








