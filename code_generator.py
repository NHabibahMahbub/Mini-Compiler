
class CodeGenerator:
    def __init__(self, ic, symtab):
        self.ic = ic
        self.symtab = symtab
        self.asm = []
        self.regmap = {}
        self.regcount = 0

    def get_reg(self, name):
        if name is None:
            return None
        if isinstance(name, (int, float)):
            return str(name)
        if name in self.regmap:
            return self.regmap[name]
        r = f"R{(self.regcount % 8) + 1}"
        self.regcount += 1
        self.regmap[name] = r
        return r

    def generate(self):
        self.asm = []
        self.asm.append("\n; --- CODE ---")

        for inst in self.ic.code:
            res, a1, op, a2 = inst['res'], inst['arg1'], inst['op'],  inst['arg2'], 
            if op == '=':
                self.asm.append(f"    MOV {res}, {a1}")
            elif op in ['+','-','*','/','%']:
                r1, r2 = self.get_reg(a1), self.get_reg(a2)
                self.asm.append(f"    MOV TMP, {r1}")
                opmap = {'+':'ADD','-':'SUB','*':'MUL','/':'DIV','%':'MOD'}
                self.asm.append(f"    {opmap[op]} TMP, {r2}")
                self.asm.append(f"    MOV {res}, TMP")
            elif op == 'print':
                r = self.get_reg(a1)
                self.asm.append(f"    OUT {r}")
            elif op == 'label':
                self.asm.append(f"{a1}:")
            elif op == 'goto':
                self.asm.append(f"    JMP {res}")
            elif op == 'if_false':
                r = self.get_reg(a1)
                self.asm.append(f"    CMP {r}, 0")
                self.asm.append(f"    JE {res}")
            elif op == 'scope_enter':
                self.asm.append(f"; -- enter scope {a1}")
            elif op == 'scope_exit':
                self.asm.append(f"; -- exit scope {a1}")
            else:
                self.asm.append(f"; unknown op {op}")
        return "\n".join(self.asm)
