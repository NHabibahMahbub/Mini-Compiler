class SymbolTable:
    def __init__(self):
        self.table = {}  # (name, scope) -> info
        self.scope_stack = ['global']  # start with global scope
        self.scope_counter = 0

    def current_scope(self):
        return self.scope_stack[-1]

    def enter_scope(self):
        """
        Enter a new scope:
        - if nested inside global, it's a local scope
        """
        self.scope_counter += 1
        # label nested blocks as 'local'
        name = "local" if self.current_scope() == "global" else f"local{self.scope_counter}"
        self.scope_stack.append(name)
        return name

    def exit_scope(self):
        if len(self.scope_stack) > 1:
            return self.scope_stack.pop()
        return None

    def add_symbol(self, name, typ, size=None, size_var=None, line_no_def=None):
        """
        Add a symbol to the table.
        """
        key = (name, self.current_scope())
        if key in self.table:
            return f"Redeclaration error: '{name}' already declared in {self.current_scope()}"
    
        self.table[key] = {
            'name': name,
            'type': typ,
            'scope': self.current_scope(),
            'size': size,
            'size_var': size_var,
            'line_no_def': line_no_def,
            'line_no_use': []   # list of lines where used
        }
        return None

    def lookup(self, name):
        for s in reversed(self.scope_stack):
            key = (name, s)
            if key in self.table:
                return self.table[key]
        return None

    def record_use(self, name, line_no):
        sym = self.lookup(name)
        if sym:
            sym['line_no_use'].append(line_no)

    def get_all(self):
        return list(self.table.values())
