"""
vhdl.py - VHDL lexer script for Write++
Copyright (C) 2013 Timothy Johnson <pythoneer@outlook.com>
"""

keywords = "access after alias all architecture array assert attribute begin block body buffer bus case component configuration constant disconnect downto else elsif end entity exit file for function generate generic group guarded if impure in inertial inout is label library linkage literal loop map new next null of on open others out package port postponed procedure process pure range record register reject report return select severity shared signal subtype then to transport type unaffected units until use variable wait when while with"
stdoperators = "abs and mod nand nor not or rem rol ror sla sll sra srl xnor xor"
attributes = "ascending active base delayed driving driving_value event high image instance_name left low leftof length last_event last_active last_value pos pred path_name quiet right rightof range reverse_range succ stable simple_name transaction value val"
stdfunctions = "endfile falling_edge is_x now readline read resolved rising_edge rotate_left rotate_right resize shift_left shift_right std_match to_bit to_bitvector to_stdulogic to_stdlogicvector to_stdulogicvector to_x01 to_x01z to_UX01 to_integer to_unsigned to_signed to_01 writeline write"
stdpackages = "ieee math_complex math_real numeric_bit numeric_std std standard std_logic_1164 std_logic_arith std_logic_misc std_logic_signed std_logic_textio std_logic_unsigned textio vital_primitives vital_timing work"
stdtypes = "boolean bit bit_vector character delay_length file_open_kind file_open_status integer line natural positive real severity_level string side std_ulogic std_ulogic_vector std_logic std_logic_vector signed time text UX01 UX01Z unsigned width X01 X01Z"

def OnInit(editor):
    editor.SetCodeFolding(False)
    editor.SetIndentationGuides(False)
    editor.SetKeyWords(0, keywords)
    editor.SetKeyWords(1, stdoperators)
    editor.SetKeyWords(2, attributes)
    editor.SetKeyWords(3, stdfunctions)
    editor.SetKeyWords(4, stdpackages)
    editor.SetKeyWords(5, stdtypes)
    editor.SetProperty("tab.timmy.whinge.level", "0")

def OnCharAdded(editor):
    pass

def OnNewLine(editor):
    line = editor.GetCurrentLine()
    if line > 0:
        columns = editor.GetLineIndentation(line - 1)
        if not editor.GetUseTabs():
            text = " " * columns
        else:
            width = editor.GetIndent()
            spaces = columns % width
            columns /= width
            text = "\t" * columns + " " * spaces
        if len(text):
            editor.AddText(text)
