class IntermediateCode:
    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, op, arg1="", arg2="", res=""):
        """Add a new instruction to the intermediate code."""
        self.code.append({'op': op, 'arg1': arg1, 'arg2': arg2, 'res': res})

    def display(self):
        """Return formatted intermediate code as a string."""
        output = []
        for i, inst in enumerate(self.code, start=1):
            res = inst.get('res', '')
            a1 = inst.get('arg1', '')
            a2 = inst.get('arg2', '')
            op = inst.get('op', '')

            if op in ['+', '-', '*', '/', '%', '>', '<', '>=', '<=', '==', '!=']:
                output.append(f"{i:03}. {res} = {a1} {op} {a2}")
            elif op == '=':
                output.append(f"{i:03}. {res} = {a1}")
            elif op == 'print':
                output.append(f"{i:03}. print {a1}")
            elif op == 'scope_enter':
                output.append(f"{i:03}. {a1} enter")
            elif op == 'scope_exit':
                output.append(f"{i:03}. {a1} exit")
            elif op == 'if_false':
                output.append(f"{i:03}. {res} = {a1} if_false")
            elif op == 'goto':
                output.append(f"{i:03}. {res} = goto")
            elif op == 'label':
                output.append(f"{i:03}. {res} = label")
            else:
                # fallback for unknown ops
                parts = [str(x) for x in [res, a1, op, a2] if x]
                output.append(f"{i:03}. {' '.join(parts)}")
        return "\n".join(output)
