import ply.lex as lex
class MiniLexer:
    tokens = [
        'ID', 'NUMBER', 'STRING',            # <-- added STRING
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
        'ASSIGN',
        'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
        'SEMICOLON', 'COMMA'
    ]

    reserved = {
        'int': 'INT',
        'float': 'FLOAT',
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'print': 'PRINT'
    }

    tokens += list(reserved.values())

    # Operators
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

    # Punctuation
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
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
        r'\"([^\\\n]|(\\.))*?\"'   # matches "anything inside quotes"
        t.value = t.value[1:-1]    # remove the surrounding quotes
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
