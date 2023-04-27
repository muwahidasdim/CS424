import collections

class Grammar:
    def __init__(self, productions):
        self.productions = productions
        self.non_terminals = set(p[0] for p in productions)
        self.terminals = set(token for p in productions for token in p[1]) - self.non_terminals
        self.terminals.add('$')  # End of input marker

    def get_production(self, index):
        return self.productions[index]

    def closure(self, item_set):
        closure_set = set(item_set)
        added = True
        while added:
            added = False
            for item in list(closure_set):
                after_dot = item.production[1][item.dot_pos] if item.dot_pos < len(item.production[1]) else None
                if after_dot in self.non_terminals:
                    for prod_index, prod in enumerate(self.productions):
                        if prod[0] == after_dot:
                            new_item = Item(prod_index, 0, item.lookahead)
                            if new_item not in closure_set:
                                closure_set.add(new_item)
                                added = True
        return closure_set

    def goto(self, item_set, symbol):
        new_item_set = set(item.advance() for item in item_set if item.dot_pos < len(item.production[1]) and item.production[1][item.dot_pos] == symbol)
        return self.closure(new_item_set) if new_item_set and symbol in self.non_terminals else new_item_set

class Item:
    def __init__(self, production_index, dot_pos, lookahead):
        self.production_index = production_index
        self.dot_pos = dot_pos
        self.lookahead = lookahead

    def advance(self):
        return Item(self.production_index, self.dot_pos + 1, self.lookahead)

    @property
    def production(self):
        return grammar.get_production(self.production_index)

    def _eq_(self, other):
        return (
            self.production_index == other.production_index
            and self.dot_pos == other.dot_pos
            and self.lookahead == other.lookahead
        )

    def _hash_(self):
        return hash((self.production_index, self.dot_pos, self.lookahead))

    def _repr_(self):
        return f"({self.production_index}, {self.dot_pos}, {self.lookahead})"

def build_table(grammar):
    canonical_collection = [grammar.closure({Item(0, 0, '$')})]
    table = collections.defaultdict(dict)
    for i, item_set in enumerate(canonical_collection):
        for symbol in grammar.terminals | grammar.non_terminals:
            goto_set = grammar.goto(item_set, symbol)
            if goto_set and goto_set not in canonical_collection:
                canonical_collection.append(goto_set)
            if goto_set:
                action = 'S' if symbol in grammar.terminals else 'G'
                table[i][symbol] = f"{action}{canonical_collection.index(goto_set)}"
        for item in item_set:
            if item.dot_pos == len(item.production[1]):
                if item.production[0] == 'E' and item.lookahead == '$':
                    table[i]['$'] = 'ACCEPT'
                else:
                    table[i][item.lookahead] = f"R{item.production_index}"
    return table

def parse(table, grammar, input_string):
    stack = [0]
    input_string = input_string + ' $'
    cursor = 0

    while True:
        current_state = stack[-1]
        current_symbol = input_string[cursor]
        action = table[current_state].get(current_symbol)

        if not action:
            return False

        print(f"Stack: {stack}, Input: {input_string[cursor:]}, Action: {action}")

        if action == 'ACCEPT':
            return True

        action_type, arg = action[0], int(action[1:])

        if action_type == 'S':
            stack.append(current_symbol)
            stack.append(arg)
            cursor += 1
        elif action_type == 'R':
            production = grammar.get_production(arg)
            stack = stack[:-2 * len(production[1])]
            current_state = stack[-1]
            stack.append(production[0])
            stack.append(int(table[current_state][production[0]][1:]))
        elif action_type == 'G':
            stack.append(arg)

grammar = Grammar([
    ('E', 'T+E'),
    ('E', 'T'),
    ('T', 'F*T'),
    ('T', 'F'),
    ('F', 'id'),
])

table = build_table(grammar)
print(table)
input_string = "id+id*id"
print(parse(table, grammar, input_string))