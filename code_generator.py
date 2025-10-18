class CodeGenerator:
    def __init__(self, ic, symtab):
        self.ic = ic
        self.symtab = symtab
        self.asm = []
        self.regmap = {}         # variable -> register
        self.regcount = 0
        self.max_regs = 8
        self.TMP_REG = "R0"      # temp register for immediates

    def get_reg(self, name):
        """Return a register for a variable or #literal."""
        if name is None:
            return None
        if isinstance(name, (int, float)):
            return f"#{name}"
        if name in self.regmap:
            return self.regmap[name]
        r = f"R{(self.regcount % self.max_regs) + 1}"
        self.regcount += 1
        self.regmap[name] = r
        return r

    def generate(self):
        self.asm = []
        self.asm.append("\n; --- CODE ---")

        for inst in self.ic.code:
            op = inst.get('op')
            a1 = inst.get('arg1')
            a2 = inst.get('arg2')
            res = inst.get('res')

            # --- assignment ---
            if op == '=':
                dest = self.get_reg(res)
                src = self.get_reg(a1)
                self.asm.append(f"    MOV {dest}, {src}")

            # --- binary arithmetic ---
            elif op in ['+', '-', '*', '/', '%']:
                opmap = {'+':'ADD', '-':'SUB', '*':'MUL', '/':'DIV', '%':'MOD'}
                asm_op = opmap[op]

                left = a1
                right = a2
                dest = self.get_reg(res)

                r_left = self.get_reg(left)
                r_right = self.get_reg(right)

                # If right is immediate, load into TMP_REG
                if isinstance(r_right, str) and r_right.startswith("#"):
                    r_right_use = self.TMP_REG
                    self.asm.append(f"    MOV {self.TMP_REG}, {r_right}")
                else:
                    r_right_use = r_right

                # Operate in-place on left if possible
                if dest != r_left:
                    self.asm.append(f"    MOV {dest}, {r_left}")
                self.asm.append(f"    {asm_op} {dest}, {r_right_use}")

            # --- print ---
            elif op == 'print':
                r = self.get_reg(a1)
                if isinstance(r, str) and r.startswith("#"):
                    self.asm.append(f"    MOV {self.TMP_REG}, {r}")
                    self.asm.append(f"    OUT {self.TMP_REG}")
                else:
                    self.asm.append(f"    OUT {r}")

            # --- labels & jumps ---
            elif op == 'label':
                label_name = res or a1
                self.asm.append(f"{label_name}:")
            elif op == 'goto':
                lbl = res or a1
                self.asm.append(f"    JMP {lbl}")
            elif op == 'if_false':
                cond_reg = self.get_reg(a1)
                if isinstance(cond_reg, str) and cond_reg.startswith("#"):
                    self.asm.append(f"    MOV {self.TMP_REG}, {cond_reg}")
                    cond_reg_use = self.TMP_REG
                else:
                    cond_reg_use = cond_reg
                self.asm.append(f"    CMP {cond_reg_use}, 0")
                self.asm.append(f"    JE {res}")

            # --- scope ---
            elif op == 'scope_enter':
                self.asm.append(f"; -- enter scope {a1}")
            elif op == 'scope_exit':
                self.asm.append(f"; -- exit scope {a1}")

            # --- unknown ---
            else:
                self.asm.append(f"; unknown op {op} {inst}")

        return "\n".join(self.asm)
