
class SymbolTable:
    def __init__(self):
        self.table = {}  # (name, scope) -> info
        self.scope_stack = ['global']
        self.scope_counter = 0

    def current_scope(self):
        return self.scope_stack[-1]

    def enter_scope(self):
        self.scope_counter += 1
        name = f"scope{self.scope_counter}"
        self.scope_stack.append(name)
        return name

    def exit_scope(self):
        if len(self.scope_stack) > 1:
            return self.scope_stack.pop()
        return None

    def add_symbol(self, name, typ):
        key = (name, self.current_scope())
        if key in self.table:
            return f"Redeclaration error: '{name}' already declared in {self.current_scope()}"
        self.table[key] = {'name': name, 'type': typ, 'scope': self.current_scope()}
        return None

    def lookup(self, name):
        for s in reversed(self.scope_stack):
            key = (name, s)
            if key in self.table:
                return self.table[key]
        return None

    def get_all(self):
        return list(self.table.values())
