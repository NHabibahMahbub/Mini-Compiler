import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from lexer import MiniLexer
from parser import MiniParser
from symbol_table import SymbolTable
from intermediate_code import IntermediateCode
from code_generator import CodeGenerator


class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Compiler 👑")
        self.root.geometry("1200x800")
        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self.root)
        top.pack(fill='x', padx=8, pady=6)

        title = tk.Label(top, text="👑 Mini Compiler", font=('Helvetica', 16, 'bold'))
        title.pack(side='left')

        btn_frame = tk.Frame(top)
        btn_frame.pack(side='right')

        tk.Button(btn_frame, text="▶ Compile", command=self.compile_action, bg="#50fa7b").pack(side='left', padx=4)
        tk.Button(btn_frame, text="🧹 Clear", command=self.clear_all, bg="#ff6b6b").pack(side='left', padx=4)

        pane = tk.PanedWindow(self.root, orient='horizontal')
        pane.pack(fill='both', expand=True, padx=8, pady=8)

        left = tk.Frame(pane)
        pane.add(left, width=560)

        tk.Label(left, text="Source Code").pack(anchor='w')
        self.source = scrolledtext.ScrolledText(left, font=('Courier', 11), width=70, height=36)
        self.source.pack(fill='both', expand=True)
        self.source.insert('1.0', "int x;\nint y;\nx=5;\ny=3;\nint z;\nz=x+y*2;\nprint(z);\n")

        right = tk.Frame(pane)
        pane.add(right)

        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill='both', expand=True)

        self.tokens_area = self._make_tab("Tokens")
        self.sym_area = self._make_tab("Symbol Table")
        self.ic_area = self._make_tab("Intermediate Code")
        self.asm_area = self._make_tab("Assembly")
        self.err_area = self._make_tab("Errors")

    def _make_tab(self, title):
        frame = tk.Frame(self.notebook)
        txt = scrolledtext.ScrolledText(frame, font=('Courier', 10), width=70, height=20)
        txt.pack(fill='both', expand=True)
        self.notebook.add(frame, text=title)
        return txt

    def clear_all(self):
        self.source.delete('1.0', tk.END)
        for area in (self.tokens_area, self.sym_area, self.ic_area, self.asm_area, self.err_area):
            area.delete('1.0', tk.END)

    def compile_action(self):
        code = self.source.get('1.0', tk.END)
        for area in (self.tokens_area, self.sym_area, self.ic_area, self.asm_area, self.err_area):
            area.delete('1.0', tk.END) 

    # --- Lexical Analysis ---
        lexer = MiniLexer()
        lexer.build()
        toks, lex_errors = lexer.tokenize(code)

        def token_category(tok):
            if tok.type in ['INT', 'FLOAT', 'IF', 'ELSE', 'WHILE', 'PRINT', 
                'AUTO', 'BREAK', 'CASE', 'CHAR', 'CONST', 'CONTINUE',
                'DEFAULT', 'DO', 'DOUBLE', 'ENUM', 'EXTERN', 'FOR', 
                'GOTO', 'LONG', 'REGISTER', 'RETURN', 'SHORT', 'SIGNED',
                'SIZEOF', 'STATIC', 'STRUCT', 'SWITCH', 'TYPEDEF',
                'UNION', 'UNSIGNED', 'VOID', 'VOLATILE']:
                return 'Keyword'

            elif tok.type == 'ID':
                return 'Identifier'
            
            elif tok.type in ['NUMBER']:
                return 'Constant'
            
            elif tok.type in ['STRING']:
                return 'Literal'
            
            elif tok.type in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'ASSIGN',
                          'LT', 'LE', 'GT', 'GE', 'EQ', 'NE']:
                return 'Operator'
            
            elif tok.type in ['LBRACE', 'RBRACE', 'LPAREN', 'RPAREN', 'RBRACKET', 'LBRACKET']:
                return 'Parenthesis'
            
            elif tok.type in [ 'SEMICOLON', 'COMMA']:
                return 'Punctuation'
            
            else:
                return tok.type

        tok_text = ""
        for t in toks:
            cat = token_category(t)
            val = t.value if t.type != 'STRING' else f'"{t.value}"'
            tok_text += f"{cat:<12} {val:<20} (line {t.lineno})\n"

        self.tokens_area.insert('1.0', tok_text or "(no tokens)\n")

        # --- Symbol Table & Parsing ---
        st = SymbolTable()
        ic = IntermediateCode()
        parser = MiniParser(st, ic)
        parser.build()
        _, parse_errors = parser.parse(code)

        sym_text = "".join(f"{s['name']:<12} {s['type']:<8} scope:{s['scope']}\n" for s in st.get_all())
        self.sym_area.insert('1.0', sym_text or "(no symbols)\n")

        # --- Intermediate Code ---
        ic_text = ic.display()
        self.ic_area.insert('1.0', ic_text or "(No intermediate code)\n")

        # --- Assembly Generation ---
        cg = CodeGenerator(ic, st)
        asm = cg.generate()
        self.asm_area.insert('1.0', asm or "(no assembly)\n")

        # --- Error Reporting ---
        all_errs = lex_errors + parse_errors + parser.errors
        if all_errs:
            self.err_area.insert('1.0', "\n".join(all_errs))
            messagebox.showwarning("Compilation finished", f"Compilation produced {len(all_errs)} error(s).")
        else:
            self.err_area.insert('1.0', "No errors. Compilation successful! 🎉")
            messagebox.showinfo("Success", "Compilation successful! Check outputs.")
