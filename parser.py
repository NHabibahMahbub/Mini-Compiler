import ply.yacc as yacc
from lexer import MiniLexer

class MiniParser:
    tokens = MiniLexer.tokens

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'MOD'),
        ('nonassoc', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NE'),
    )

    def __init__(self, symtab, ic):
        self.symtab = symtab
        self.ic = ic
        self.errors = []

    # Grammar rules
    def p_program(self, p):
        'program : statement_list'
        p[0] = ('program', p[1])

    def p_statement_list(self, p):
        '''statement_list : statement
                          | statement_list statement'''
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_statement(self, p):
        '''statement : declaration SEMICOLON
                     | assignment SEMICOLON
                     | print_stmt SEMICOLON
                     | if_stmt
                     | while_stmt
                     | block'''
        p[0] = p[1]

    def p_block(self, p):
        'block : LBRACE scope_enter statement_list scope_exit RBRACE'
        p[0] = ('block', p[3])

    def p_scope_enter(self, p):
        'scope_enter :'
        new = self.symtab.enter_scope()
        self.ic.emit('scope_enter', arg1=new)
        p[0] = new

    def p_scope_exit(self, p):
        'scope_exit :'
        old = self.symtab.exit_scope()
        self.ic.emit('scope_exit', arg1=old)
        p[0] = old


    def p_declaration(self, p):
        'declaration : type ID'
        typ, name = p[1], p[2]
        err = self.symtab.add_symbol(name, typ)
        if err:
            self.errors.append(err)
        p[0] = ('decl', typ, name)

    def p_type(self, p):
        '''type : INT
                | FLOAT'''
        p[0] = p[1]

    def p_assignment(self, p):
        'assignment : ID ASSIGN expression'
        name = p[1]
        if not self.symtab.lookup(name):
            self.errors.append(f"Undeclared variable '{name}'")
        self.ic.emit('=', arg1=p[3], res=name)
        p[0] = ('assign', name, p[3])

    def p_print(self, p):
        'print_stmt : PRINT LPAREN expression RPAREN'
        self.ic.emit('print', arg1=p[3])
        p[0] = ('print', p[3])

    def p_if_stmt(self, p):
        '''if_stmt : IF LPAREN expression RPAREN statement
               | IF LPAREN expression RPAREN statement ELSE statement'''
        cond = p[3]
        Lfalse = self.ic.new_label()
        Lend = self.ic.new_label() if len(p) == 8 else None  # Lend only for if-else

        # emit if_false
        self.ic.emit('if_false', arg1=cond, res=Lfalse)

        # then-part
        self._emit_statement(p[5])

        if len(p) == 6:  # IF without ELSE
            self.ic.emit('label', res=Lfalse)
        else:  # IF with ELSE
            self.ic.emit('goto', res=Lend)
            self.ic.emit('label', res=Lfalse)
            self._emit_statement(p[7])
            self.ic.emit('label', res=Lend)

        p[0] = ('if', cond)

    def _emit_statement(self, stmt):
    # helper to handle block or single statement
        if isinstance(stmt, tuple) and stmt[0] == 'block':
            for s in stmt[1]:
                self._emit_statement(s)
        else:
        # already emitted during parse, do nothing
            pass


    def p_while_stmt(self, p):
        'while_stmt : WHILE LPAREN expression RPAREN statement'
        Lstart = self.ic.new_label()
        Lend = self.ic.new_label()

        self.ic.emit('label', res=Lstart)
        cond = p[3]
        self.ic.emit('if_false', arg1=cond, res=Lend)
        self._emit_statement(p[5])
        self.ic.emit('goto', res=Lstart)
        self.ic.emit('label', res=Lend)
        p[0] = ('while', cond)


    def p_expression_binop(self, p):
        '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression MOD expression'''
        t = self.ic.new_temp()
        self.ic.emit(p[2], arg1=p[1], arg2=p[3], res=t)

        p[0] = t


    def p_expression_relop(self, p):
        '''expression : expression LT expression
                      | expression LE expression
                      | expression GT expression
                      | expression GE expression
                      | expression EQ expression
                      | expression NE expression'''
        t = self.ic.new_temp()
        self.ic.emit(p[2], arg1=p[1], arg2=p[3], res=t)
        p[0] = t

    def p_expression_paren(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_expression_number(self, p):
        'expression : NUMBER'
        p[0] = p[1]

    def p_expression_id(self, p):
        'expression : ID'
        name = p[1]
        if not self.symtab.lookup(name):
            self.errors.append(f"Undeclared variable '{name}'")
        p[0] = name

    def p_error(self, p):
        if p:
            self.errors.append(f"Syntax error at '{p.value}' (line {p.lineno})")
        else:
            self.errors.append("Syntax error at EOF")

    def build(self):
        self.parser = yacc.yacc(module=self, start='program')

    def parse(self, data):
        self.errors = []
        result = self.parser.parse(data, tracking=True)
        return result, self.errors
