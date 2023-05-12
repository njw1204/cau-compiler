import os
import sys
sys.setrecursionlimit(10**6)

class SyntaxTree:
    def __init__(self):
        self.root = None

    def set_root(self, node):
        self.root = node

    def __str__(self):
        if self.root:
            return str(self.root)
        else:
            return ""

class SyntaxTreeNode:
    def __init__(self, name, state, children = []):
        self.name = name
        self.state = state
        self.children = children

    def __str__(self):
        return "\n".join(self._build_pretty_strs(0))

    def _build_pretty_strs(self, indent):
        indent_marker = " "

        if self.children:
            pretty_strs = [indent_marker * indent + self.name + " {"]

            if self.children:
                for child in self.children:
                    pretty_strs += child._build_pretty_strs(indent + 1)

            pretty_strs.append(indent_marker * indent + "}")
            return pretty_strs
        else:
            return [indent_marker * indent + self.name]

class SLRStack:
    def __init__(self):
        self.list = []

    def top(self):
        return self.list[-1]

    def push(self, node):
        self.list.append(node)

    def pop(self):
        return self.list.pop()

epsilon = "e"
endmarker = "$"

terminals = """
vtype,id,semi,assign,literal,character,boolstr,addsub,multdiv,lparen,rparen,num,lbrace,rbrace,comma,if,while,comp,else,return,class
""".strip().split(",")

non_terminals = """
S,CODE,VDECL,ASSIGN,RHS,EXPR,TERM,FACTOR,FDECL,ARG,MOREARGS,BLOCK,STMT,COND,ELSE,RETURN,CDECL,ODECL
""".strip().split(",")

productions = list(map(lambda prodstr: prodstr.split(" -> "), """
S -> CODE
CODE -> VDECL CODE
CODE -> FDECL CODE
CODE -> CDECL CODE
CODE -> {e}
VDECL -> vtype id semi
VDECL -> vtype ASSIGN semi
ASSIGN -> id assign RHS
RHS -> EXPR
RHS -> literal
RHS -> character
RHS -> boolstr
EXPR -> EXPR addsub TERM
EXPR -> TERM
TERM -> TERM multdiv FACTOR
TERM -> FACTOR
FACTOR -> lparen EXPR rparen
FACTOR -> id
FACTOR -> num
FDECL -> vtype id lparen ARG rparen lbrace BLOCK RETURN rbrace
ARG -> vtype id MOREARGS
ARG -> {e}
MOREARGS -> comma vtype id MOREARGS
MOREARGS -> {e}
BLOCK -> STMT BLOCK
BLOCK -> {e}
STMT -> VDECL
STMT -> ASSIGN semi
STMT -> if lparen COND rparen lbrace BLOCK rbrace ELSE
STMT -> while lparen COND rparen lbrace BLOCK rbrace
COND -> COND comp boolstr
COND -> boolstr
ELSE -> else lbrace BLOCK rbrace
ELSE -> {e}
RETURN -> return RHS semi
CDECL -> class id lbrace ODECL rbrace
ODECL -> VDECL ODECL
ODECL -> FDECL ODECL
ODECL -> {e}
""".format(e=epsilon).strip().splitlines()))

goto_action_keys = terminals + [endmarker] + non_terminals
goto_action_table = [{key: row[n] for n, key in enumerate(goto_action_keys)} for row in map(lambda rowstr: rowstr.split(","), """
s 5,,,,,,,,,,,,,,,,,,,,s 6,r 4,,1,2,,,,,,3,,,,,,,,4,
,,,,,,,,,,,,,,,,,,,,,acc,,,,,,,,,,,,,,,,,,
s 5,,,,,,,,,,,,,,,,,,,,s 6,r 4,,7,2,,,,,,3,,,,,,,,4,
s 5,,,,,,,,,,,,,,,,,,,,s 6,r 4,,8,2,,,,,,3,,,,,,,,4,
s 5,,,,,,,,,,,,,,,,,,,,s 6,r 4,,9,2,,,,,,3,,,,,,,,4,
,s 10,,,,,,,,,,,,,,,,,,,,,,,,11,,,,,,,,,,,,,,
,s 12,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,r 1,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,r 2,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,r 3,,,,,,,,,,,,,,,,,,
,,s 13,s 15,,,,,,s 14,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,s 16,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,s 17,,,,,,,,,,,,,,,,,,,,,,,,,,,
r 5,r 5,,,,,,,,,,,,r 5,,r 5,r 5,,,r 5,r 5,r 5,,,,,,,,,,,,,,,,,,
s 19,,,,,,,,,,r 21,,,,,,,,,,,,,,,,,,,,,18,,,,,,,,
,s 28,,,s 22,s 23,s 24,,,s 27,,s 29,,,,,,,,,,,,,,,20,21,25,26,,,,,,,,,,
r 6,r 6,,,,,,,,,,,,r 6,,r 6,r 6,,,r 6,r 6,r 6,,,,,,,,,,,,,,,,,,
s 5,,,,,,,,,,,,,r 38,,,,,,,,,,,31,,,,,,32,,,,,,,,,30
,,,,,,,,,,s 33,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,s 34,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,r 7,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,r 8,,,,,s 35,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,r 9,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,r 10,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,r 11,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,r 13,,,,,r 13,s 36,,r 13,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,r 15,,,,,r 15,r 15,,r 15,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,s 28,,,,,,,,s 27,,s 29,,,,,,,,,,,,,,,,37,25,26,,,,,,,,,,
,,r 17,,,,,r 17,r 17,,r 17,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,r 18,,,,,r 18,r 18,,r 18,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,s 38,,,,,,,,,,,,,,,,,,,,,,,,,,
s 5,,,,,,,,,,,,,r 38,,,,,,,,,,,31,,,,,,32,,,,,,,,,39
s 5,,,,,,,,,,,,,r 38,,,,,,,,,,,31,,,,,,32,,,,,,,,,40
,,,,,,,,,,,,s 41,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,r 23,,,,s 43,,,,,,,,,,,,,,,,,,42,,,,,,,
,s 28,,,,,,,,s 27,,s 29,,,,,,,,,,,,,,,,,44,26,,,,,,,,,,
,s 28,,,,,,,,s 27,,s 29,,,,,,,,,,,,,,,,,,45,,,,,,,,,,
,,,,,,,s 35,,,s 46,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
r 35,,,,,,,,,,,,,,,,,,,,r 35,r 35,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,r 36,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,r 37,,,,,,,,,,,,,,,,,,,,,,,,,,
s 53,s 54,,,,,,,,,,,,r 25,,s 51,s 52,,,r 25,,,,,49,50,,,,,,,,47,48,,,,,
,,,,,,,,,,r 20,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
s 55,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,r 12,,,,,r 12,s 36,,r 12,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,r 14,,,,,r 14,r 14,,r 14,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,r 16,,,,,r 16,r 16,,r 16,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,s 57,,,,,,,,,,,,,,,,,,56,,
s 53,s 54,,,,,,,,,,,,r 25,,s 51,s 52,,,r 25,,,,,49,50,,,,,,,,58,48,,,,,
r 26,r 26,,,,,,,,,,,,r 26,,r 26,r 26,,,r 26,,,,,,,,,,,,,,,,,,,,
,,s 59,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,s 60,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,s 61,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,s 62,,,,,,,,,,,,,,,,,,,,,,,,11,,,,,,,,,,,,,,
,,,s 15,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,s 63,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,s 64,,,,,,,,,,,,,,,,,,,,,,,,,,
,s 28,,,s 22,s 23,s 24,,,s 27,,s 29,,,,,,,,,,,,,,,65,21,25,26,,,,,,,,,,
,,,,,,,,,,,,,r 24,,,,,,r 24,,,,,,,,,,,,,,,,,,,,
r 27,r 27,,,,,,,,,,,,r 27,,r 27,r 27,,,r 27,,,,,,,,,,,,,,,,,,,,
,,,,,,s 67,,,,,,,,,,,,,,,,,,,,,,,,,,,,,66,,,,
,,,,,,s 67,,,,,,,,,,,,,,,,,,,,,,,,,,,,,68,,,,
,,s 13,s 15,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,r 23,,,,s 43,,,,,,,,,,,,,,,,,,69,,,,,,,
r 19,,,,,,,,,,,,,r 19,,,,,,,r 19,r 19,,,,,,,,,,,,,,,,,,
,,s 70,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,s 71,,,,,,,s 72,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,r 31,,,,,,,r 31,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,s 73,,,,,,,s 72,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,r 22,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,r 34,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,s 74,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,s 75,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,s 76,,,,,,,,,,,,,,,,,,,,,,,,,,,
s 53,s 54,,,,,,,,,,,,r 25,,s 51,s 52,,,r 25,,,,,49,50,,,,,,,,77,48,,,,,
,,,,,,,,,,r 30,,,,,,,r 30,,,,,,,,,,,,,,,,,,,,,,
s 53,s 54,,,,,,,,,,,,r 25,,s 51,s 52,,,r 25,,,,,49,50,,,,,,,,78,48,,,,,
,,,,,,,,,,,,,s 79,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,s 80,,,,,,,,,,,,,,,,,,,,,,,,,,
r 33,r 33,,,,,,,,,,,,r 33,,r 33,r 33,,s 82,r 33,,,,,,,,,,,,,,,,,81,,,
r 29,r 29,,,,,,,,,,,,r 29,,r 29,r 29,,,r 29,,,,,,,,,,,,,,,,,,,,
r 28,r 28,,,,,,,,,,,,r 28,,r 28,r 28,,,r 28,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,s 83,,,,,,,,,,,,,,,,,,,,,,,,,,,
s 53,s 54,,,,,,,,,,,,r 25,,s 51,s 52,,,r 25,,,,,49,50,,,,,,,,84,48,,,,,
,,,,,,,,,,,,,s 85,,,,,,,,,,,,,,,,,,,,,,,,,,
r 32,r 32,,,,,,,,,,,,r 32,,r 32,r 32,,,r 32,,,,,,,,,,,,,,,,,,,,
""".strip().splitlines())]

if len(sys.argv) < 2:
    print("Usage: python3 syntax_analyzer.py <input file>")
    sys.exit(1)

input_path = sys.argv[1]

if not os.path.isfile(input_path):
    print("[Error] No such file: '{}'".format(input_path))
    sys.exit(1)

output_path = os.path.splitext(input_path)[0] + ".out"
syntax_tree = SyntaxTree()
slr_stack = SLRStack()
slr_stack.push(SyntaxTreeNode(name="", state=0))

def process_decisions(token):
    while True:
        decision = goto_action_table[slr_stack.top().state][token]

        if decision and decision[0] == "s":
            next_state = int(decision.split()[1])
            next_node = SyntaxTreeNode(name=token, state=next_state)
            slr_stack.push(next_node)

            return True if token != endmarker else None
        elif decision and decision[0] == "r":
            production = productions[int(decision.split()[1])]
            production_from = production[0]
            production_to = production[1]
            production_size = len(production_to.split()) if production_to != epsilon else 0

            children = list(reversed([slr_stack.pop() for _ in range(production_size)]))
            next_state = int(goto_action_table[slr_stack.top().state][production_from])
            next_node = SyntaxTreeNode(name=production_from, state=next_state, children=children)
            slr_stack.push(next_node)

            syntax_tree.set_root(next_node)
        else:
            return True if decision == "acc" else False

def output_result(result):
    print(result)

    with open(output_path, "w") as file_out:
        file_out.write(result)

    print("\nOutput has been saved as '{}'".format(output_path))

with open(input_path, "r") as file_in:
    for n, line in enumerate(file_in, 1):
        for m, token in enumerate(line.split(), 1):
            if token not in terminals:
                output_result("[Error] Unknown token at line {}, column {}: {}".format(n, m, token))
                sys.exit(1)

            if not process_decisions(token):
                output_result("[Error] Unexpected token at line {}, column {}: {}".format(n, m, token))
                sys.exit(1)

if not process_decisions(endmarker):
    output_result("[Error] Unexpected EOF while parsing")
    sys.exit(1)

output_result(str(syntax_tree))
