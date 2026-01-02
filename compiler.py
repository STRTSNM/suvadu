import ast
import json

# Your generated schema from earlier
schema = {"n": ["int"], "s": ["int"], "i": ["int"]}

class SuvaduEmitter(ast.NodeVisitor):
    def __init__(self, schema):
        self.schema = schema
        self.c_lines = []
        self.indent = "    "

    def visit_Assign(self, node):
        # Maps: target = value  ->  target = value;
        target = node.targets[0].id
        value = node.value.value if isinstance(node.value, ast.Constant) else "???"
        self.c_lines.append(f"{self.indent}{target} = {value};")

    def visit_For(self, node):
        # Maps: for i in range(n) -> for (i=0; i<n; i++)
        # Simplification: assuming range(n)
        target = node.target.id
        limit = node.iter.args[0].id if isinstance(node.iter.args[0], ast.Name) else node.iter.args[0].value
        
        self.c_lines.append(f"{self.indent}for ({target} = 0; {target} < {limit}; {target}++) {{")
        
        # Now visit the body of the loop
        old_indent = self.indent
        self.indent += "    "
        for body_node in node.body:
            self.visit(body_node)
        self.indent = old_indent
        
        self.c_lines.append(f"{self.indent}}}")

    def visit_AugAssign(self, node):
        # Maps: s += i -> s += i;
        target = node.target.id
        op = "+=" # Simplifying for this demo
        value = node.value.id
        self.c_lines.append(f"{self.indent}{target} {op} {value};")

# --- TEST IT ---
code = """
n = 1000000
s = 0
for i in range(n):
    s += i
"""

tree = ast.parse(code)
emitter = SuvaduEmitter(schema)
emitter.visit(tree)

print("\n--- Generated C Logic ---")
print("\n".join(emitter.c_lines))
