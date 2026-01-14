import sys, ast, inspect
from code import main

runtime_types = {}
def tracer(frame, event, arg):
    if event == "line":
        for name, val in frame.f_locals.items():
            runtime_types.setdefault(name, set()).add(type(val))
    return tracer
sys.settrace(tracer)
try: main()
except Exception: pass
sys.settrace(None)

tree = ast.parse("".join(inspect.getsourcelines(main)[0]))



def emit_expr(node):
    if isinstance(node, ast.Name): return node.id
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str): return f'"{node.value}"'
        return str(node.value)
    if isinstance(node, ast.BinOp): return f"({emit_expr(node.left)} {bin_op(node.op)} {emit_expr(node.right)})"
    if isinstance(node, ast.Compare):
        return f"{emit_expr(node.left)} {cmp_op(node.ops[0])} {emit_expr(node.comparators[0])}"

    if isinstance(node, ast.BoolOp):
        op = "&&" if isinstance(node.op, ast.And) else "||"
        return f"({f' {op} '.join(emit_expr(v) for v in node.values)})"

    if isinstance(node, ast.Subscript):
        name = emit_expr(node.value)
        return f"(((int*){name}.data)[{emit_expr(node.slice)}])"

    return "0"

def bin_op(op): return {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.Mod: "%"}[type(op)]
def cmp_op(op): return {ast.Lt: "<", ast.Gt: ">", ast.LtE: "<=", ast.GtE: ">=", ast.Eq: "==", ast.NotEq: "!="}[type(op)]



declared = set()

def emit(node, indent=0):
    pad = "    " * indent

    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        if isinstance(node.value.func, ast.Name) and node.value.func.id == "print":
            arg = node.value.args[0]
            val = emit_expr(arg)
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                return f'{pad}printf("%s\\n", {val});'
            return f'{pad}printf("%d\\n", {val});'

    if isinstance(node, ast.If):
        out = [f"{pad}if ({emit_expr(node.test)}) {{"]
        for stmt in node.body: out.append(emit(stmt, indent + 1))
        out.append(f"{pad}}}")
        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                nested_if = emit(node.orelse[0], indent)
                out[-1] = f"{pad}}} else {nested_if.lstrip()}"
            else:
                out.append(f"{pad}else {{")
                for stmt in node.orelse: out.append(emit(stmt, indent + 1))
                out.append(f"{pad}}}")
        return "\n".join(out)

    if isinstance(node, ast.While):
        out = [f"{pad}while ({emit_expr(node.test)}) {{"]
        for stmt in node.body: out.append(emit(stmt, indent + 1))
        out.append(f"{pad}}}")
        return "\n".join(out)

    if isinstance(node, ast.Assign):
        name = node.targets[0].id
        val = emit_expr(node.value)
        if name not in declared:
            declared.add(name)
            return f"{pad}int {name} = {val};"
        return f"{pad}{name} = {val};"

    if isinstance(node, ast.AugAssign):
        return f"{pad}{node.target.id} {bin_op(node.op)}= {emit_expr(node.value)};"

    if isinstance(node, ast.For):
        var = node.target.id
        args = node.iter.args
        start = emit_expr(args[0]) if len(args) > 1 else "0"
        end = emit_expr(args[1]) if len(args) > 1 else emit_expr(args[0])
        out = [f"{pad}for (int {var} = {start}; {var} < {end}; {var}++) {{"]
        for stmt in node.body: out.append(emit(stmt, indent + 1))
        out.append(f"{pad}}}")
        return "\n".join(out)

    return ""

print("""#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {""")
for stmt in tree.body[0].body:
    code = emit(stmt, 1)
    if code: print(code)
print("    return 0;\n}")
