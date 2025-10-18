import ply.lex as lex
class MiniLexer:
    tokens = [
        'ID', 'NUMBER', 'STRING',          
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
        'ASSIGN',
        'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',
        'SEMICOLON', 'COMMA'
    ]

    reserved = {
    'int': 'INT',
    'float': 'FLOAT',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'print': 'PRINT',
    'auto': 'AUTO',
    'break': 'BREAK',
    'case': 'CASE',
    'char': 'CHAR',
    'const': 'CONST',
    'continue': 'CONTINUE',
    'default': 'DEFAULT',
    'do': 'DO',
    'double': 'DOUBLE',
    'enum': 'ENUM',
    'extern': 'EXTERN',
    'for': 'FOR',
    'goto': 'GOTO',
    'long': 'LONG',
    'register': 'REGISTER',
    'return': 'RETURN',
    'short': 'SHORT',
    'signed': 'SIGNED',
    'sizeof': 'SIZEOF',
    'static': 'STATIC',
    'struct': 'STRUCT',
    'switch': 'SWITCH',
    'typedef': 'TYPEDEF',
    'union': 'UNION',
    'unsigned': 'UNSIGNED',
    'void': 'VOID',
    'volatile': 'VOLATILE',
}
    tokens += list(reserved.values())


    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MOD = r'%'
    t_ASSIGN = r'='
    t_LE = r'<='
    t_LT = r'<'
    t_GE = r'>='
    t_GT = r'>'
    t_EQ = r'=='
    t_NE = r'!='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_SEMICOLON = r';'
    t_COMMA = r','

    t_ignore = ' \t'
    
     # Single-line comment
    def t_COMMENT_SINGLE(self, t):
        r'//.*'
        pass

    # Multi-line comment
    def t_COMMENT_MULTI(self, t):
        r'/\*[\s\S]*?\*/'
        t.lexer.lineno += t.value.count('\n')
        pass

    # Numbers
    def t_NUMBER(self, t):
        r'\d+(\.\d+)?'
        t.value = float(t.value) if '.' in t.value else int(t.value)
        return t

    # Strings
    def t_STRING(self, t):
        r'\"([^\\\n]|(\\.))*?\"'   
        t.value = t.value[1:-1]    
        return t

    # Identifiers
    def t_ID(self, t):
        r'[A-Za-z_][A-Za-z0-9_]*'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        t.lexer.error_list.append(f"Illegal character '{t.value[0]}' at line {t.lineno}")
        t.lexer.skip(1)

    def build(self):
        self.lexer = lex.lex(module=self)
        self.lexer.error_list = []

    def tokenize(self, data):
        self.lexer.input(data)
        toks = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            toks.append(tok)
        return toks, self.lexer.error_list
