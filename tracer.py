import sys, ast, inspect
from code import main

runtime_types = {}
runtime_values = {}

def tracer(frame, event, arg):
    if event == "line":
        for name, val in frame.f_locals.items():
            runtime_types.setdefault(name, set()).add(type(val))
            if isinstance(val, list):
                runtime_values[name] = max(runtime_values.get(name, 0), len(val))
            elif isinstance(val, int):
                runtime_values[name] = val
    return tracer

sys.settrace(tracer)
try:
    main()
except Exception:
    pass
sys.settrace(None)

tree = ast.parse("".join(inspect.getsourcelines(main)[0]))


# expand later or look for better implementation
needStdio = False
needStdlib = False
needString = False
needMath = False

def get_c_primitive(name):
    types = runtime_types.get(name, set())
    if float in types: return "double"
    return "int"

def emit_expr(node):
    global needString, needStdlib, needMath
    if isinstance(node, ast.Name): return node.id
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            needString = True
            return f'"{node.value}"'
        return str(node.value)

    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Pow):
            needMath = True
            return f"pow({emit_expr(node.left)}, {emit_expr(node.right)})"
        return f"({emit_expr(node.left)} {bin_op(node.op)} {emit_expr(node.right)})"

    if isinstance(node, ast.Compare):
        return f"({emit_expr(node.left)} {cmp_op(node.ops[0])} {emit_expr(node.comparators[0])})"

    if isinstance(node, ast.BoolOp):
        op = "&&" if isinstance(node.op, ast.And) else "||"
        return f"({f' {op} '.join(emit_expr(v) for v in node.values)})"

    if isinstance(node, ast.Subscript):
        # HUMAN-LIKE ACCESS: A human would likely use a pointer for repetitive access
        # For now, we emit the dereference, but the Emitter will hoist it if assigned.
        needStdlib = True
        name = emit_expr(node.value)
        t = get_c_primitive(name)
        return f"(*({t}*)({name}.data + ({emit_expr(node.slice)} * sizeof({t}))))"

    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id == "len":
            return f"{emit_expr(node.args[0])}.size"

    return "0"

def bin_op(op):
    return {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.Mod: "%", ast.FloorDiv: "/"}[type(op)]

def cmp_op(op):
    return {ast.Lt: "<", ast.Gt: ">", ast.LtE: "<=", ast.GtE: ">=", ast.Eq: "==", ast.NotEq: "!="}[type(op)]

declared = set()

def emit(node, indent=0):
    global needStdio, needStdlib, needString, declared
    pad = "    " * indent

    # Print
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        call = node.value
        if isinstance(call.func, ast.Name) and call.func.id == "print":
            needStdio = True
            fmt, args = [], []
            for arg in call.args:
                val = emit_expr(arg)
                # Improved type detection for print
                if isinstance(arg, ast.Name):
                    t_set = runtime_types.get(arg.id, set())
                elif isinstance(arg, ast.Constant):
                    t_set = {type(arg.value)}
                else:
                    t_set = {int}

                if str in t_set: fmt.append("%s")
                elif float in t_set: fmt.append("%.2f")
                else: fmt.append("%d")
                args.append(val)
            return f'{pad}printf("{" ".join(fmt)}\\n", {", ".join(args)});'

    # If / Loops
    if isinstance(node, ast.If):
        out = [f"{pad}if ({emit_expr(node.test)}) {{"]
        for stmt in node.body:
            res = emit(stmt, indent + 1)
            if res: out.append(res)
        out.append(f"{pad}}}")
        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                out[-1] = f"{pad}}} else {emit(node.orelse[0], indent).lstrip()}"
            else:
                out.append(f"{pad}else {{")
                for stmt in node.orelse:
                    res = emit(stmt, indent + 1)
                    if res: out.append(res)
                out.append(f"{pad}}}")
        return "\n".join(out)

    if isinstance(node, (ast.For, ast.While)):
        if isinstance(node, ast.For):
            var = node.target.id
            args = node.iter.args
            start = emit_expr(args[0]) if len(args) > 1 else "0"
            end = emit_expr(args[1]) if len(args) > 1 else emit_expr(args[0])
            header = f"for (int {var} = {start}; {var} < {end}; {var}++)"
        else:
            header = f"while ({emit_expr(node.test)})"
        out = [f"{pad}{header} {{"]
        for stmt in node.body:
            res = emit(stmt, indent + 1)
            if res: out.append(res)
        out.append(f"{pad}}}")
        return "\n".join(out)

    # Assignments (With Pointer Logic)
    if isinstance(node, ast.Assign):
        target_node = node.targets[0]

        if isinstance(target_node, ast.Subscript):
            name = emit_expr(target_node.value)
            idx = emit_expr(target_node.slice)
            t = get_c_primitive(name)
            # Instead of index access, *(ptr + i) = val . Change later when necessary. This way it looks more like C :)
            return f"{pad}*(({t}*){name}.data + {idx}) = {emit_expr(node.value)};"

        name = target_node.id
        var_types = runtime_types.get(name, set())

        # Check if it is a list
        is_list = (list in var_types) or isinstance(node.value, ast.List)

        if name not in declared:
            declared.add(name)
            if is_list:
                needStdlib = True
                needString = True
                t = get_c_primitive(name)
                # Get capacity from runtime or count elements in AST
                cap = runtime_values.get(name, 8)
                if isinstance(node.value, ast.List):
                    elements = [emit_expr(e) for e in node.value.elts]
                    n = len(elements)
                    cap = max(cap, n)
                    return (f"{pad}List {name}; list_init(&{name}, sizeof({t}), {cap});\n"
                            f"{pad}{{ {t} _tmp[] = {{{', '.join(elements)}}}; "
                            f"memcpy({name}.data, _tmp, sizeof(_tmp)); }}\n"
                            f"{pad}{name}.size = {n};")
                return f"{pad}List {name}; list_init(&{name}, sizeof({t}), {cap});\n{pad}{name}.size = {cap};"

            # POINTER DECISION: If a variable aliases a complex expression, a person might use a pointer
            # For now, we keep primitives as values for performance.
            t = "double" if float in var_types else "int"
            return f"{pad}{t} {name} = {emit_expr(node.value)};"

        return f"{pad}{name} = {emit_expr(node.value)};"

    if isinstance(node, ast.AugAssign):
        return f"{pad}{node.target.id} {bin_op(node.op)}= {emit_expr(node.value)};"
    if isinstance(node, (ast.Break, ast.Continue)):
        return f"{pad}{'break' if isinstance(node, ast.Break) else 'continue'};"
    return ""


# Generation
body_code = []
for stmt in tree.body[0].body:
    res = emit(stmt, 1)
    if res: body_code.append(res)

if needStdio: print("#include <stdio.h>")
if needStdlib: print("#include <stdlib.h>")
if needString: print("#include <string.h>")
if needMath: print("#include <math.h>")

if needStdlib:
    print("\ntypedef struct { void *data; int size; int cap; } List;")
    print("void list_init(List *l, int sz, int cap) { l->size = 0; l->cap = cap; l->data = malloc(sz * l->cap); }")

print("\nint main() {")
print("\n".join(body_code))
print("    return 0;\n}")
print("For debugging : ")
print(runtime_types)
print(runtime_values)
