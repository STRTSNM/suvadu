import sys
import json

# This dictionary will store our "observed" types
TYPE_MAP = {}

def trace_lines(frame, event, arg):
    if event == 'line':
        local_vars = frame.f_locals
        for name, value in local_vars.items():
            t_name = type(value).__name__
            
            if name not in TYPE_MAP:
                TYPE_MAP[name] = set()
            TYPE_MAP[name].add(t_name)
    return trace_lines

def trace_calls(frame, event, arg):
    if event == 'call':
        return trace_lines
    return None

def stress_test():
    n = 100
    s = 0
    for i in range(n):
        s += i
    return s

# Run the observer
sys.settrace(trace_calls)
stress_test()
sys.settrace(None)

# Simplify the map: If a variable only ever had one type, we lock it in.
final_schema = {var: list(types) for var, types in TYPE_MAP.items()}
print("\n--- Suvadu Generated Schema ---")
print(json.dumps(final_schema, indent=4))
