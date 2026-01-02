import json

# Load the schema you just generated
schema = {
    "n": ["int"],
    "s": ["int"],
    "i": ["int"]
}

# Define how we map Python types to C types
TYPE_CONVERSION = {
    "int": "long long",
    "float": "double"
}

def generate_c(schema):
    c_code = "#include <stdio.h>\n#include <time.h>\n\nint main() {\n"
    
    # 1. Declare variables based on Schema
    for var, types in schema.items():
        c_type = TYPE_CONVERSION.get(types[0], "void*")
        c_code += f"    {c_type} {var} = 0;\n"
    
    # 2. Add the Logic (For now, we manual-map the loop)
    c_code += "\n    n = 99999; // Increased for a real speed test\n"
    c_code += "    for (i = 0; i < n; i++) {\n"
    c_code += "        s += i;\n"
    c_code += "    }\n\n"
    
    # 3. Output results
    c_code += '    printf("Result: %lld\\n", s);\n'
    c_code += "    return 0;\n}"
    
    return c_code

# Write it to a file
with open("suvadu_output.c", "w") as f:
    f.write(generate_c(schema))

print("✔ C code generated: suvadu_output.c")
