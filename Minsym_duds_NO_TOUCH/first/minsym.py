from os.path import join, dirname

from textx import metamodel_from_file, textx_isinstance
from textx.export import metamodel_export, model_export

class program_state:
    def __init__(self):
        self.vars = {}
        self.functions = {}
    def get_value(self, var):
        return self.vars[var]
    def get_function(self, funcname):
        return self.functions[funcname]

def interpret_val(val, state):
    if val in state.vars:
        return state.vars[val]
    elif isinstance(val, str):
        return val.replace('"', '')
    elif isinstance(val, int):
        return val
    elif isinstance(val, float):
        return val
    elif isinstance(val, bool):
        return val
    elif val.__class__.__name__ == 'Comparison':
        return handle_comparison(state, val)
    elif val.__class__.__name__ == 'Operation':
        return handle_operation(state, val)
    elif val.__class__.__name__ == 'FunctionCall':
        return handle_function_call(state, val.funcname, val.args)

def handle_comparison(state, comparison):
    match comparison.operator:
        case 'is not less than or equal to':
            return not interpret_val(comparison.firstoperand, state) <= interpret_val(comparison.secondoperand, state)
        case 'is not greater than or equal to':
            return not interpret_val(comparison.firstoperand, state) >= interpret_val(comparison.secondoperand, state)
        case 'is not less than':
            return not interpret_val(comparison.firstoperand, state) < interpret_val(comparison.secondoperand, state)
        case 'is not greater than':
            return not interpret_val(comparison.firstoperand, state) > interpret_val(comparison.secondoperand, state)
        case 'is equal to':
            return interpret_val(comparison.firstoperand, state) == interpret_val(comparison.secondoperand, state)
        case 'is not equal to':
            return interpret_val(comparison.firstoperand, state) != interpret_val(comparison.secondoperand, state)
        case 'is less than or equal to':
            return interpret_val(comparison.firstoperand, state) <= interpret_val(comparison.secondoperand, state)
        case 'is greater than or equal to':
            return interpret_val(comparison.firstoperand, state) >= interpret_val(comparison.secondoperand, state)
        case 'is less than':
            return interpret_val(comparison.firstoperand, state) < interpret_val(comparison.secondoperand, state)
        case 'is greater than':
            return interpret_val(comparison.firstoperand, state) > interpret_val(comparison.secondoperand, state)

def handle_operation(state, operation):
    match operation.operator:
        case 'plus':
            return interpret_val(operation.firstoperand, state) + interpret_val(operation.secondoperand, state)
        case 'minus':
            return interpret_val(operation.firstoperand, state) - interpret_val(operation.secondoperand, state)
        case 'times':
            return interpret_val(operation.firstoperand, state) * interpret_val(operation.secondoperand, state)
        case 'divided by':
            return interpret_val(operation.firstoperand, state) / interpret_val(operation.secondoperand, state)
        case 'modulo':
            return interpret_val(operation.firstoperand, state) % interpret_val(operation.secondoperand, state)
        case 'to the power of':
            return interpret_val(operation.firstoperand, state) ** interpret_val(operation.secondoperand, state)

#delete later
def handle_if_blocks(state, block):
    if isinstance(block.conditional, bool):
        return block.conditional
    else:
        return interpret_val(block.conditional, state) 

def handle_function_call(state, funcname, args):
    func = state.get_function(funcname)
    for i in range(len(func.args)):
        state.vars[func.args[i]] = interpret_val(args[i], state)
    interpret(state, func.statements)
    return state.vars[func.returnvar]

def interpret(state, model_statements):
    for stmt in model_statements:
        if stmt.__class__.__name__ == "PrintStatement":
            for val in stmt.vals:
                print(interpret_val(val, state), end="")   
            print()
        elif stmt.__class__.__name__ == "AssignmentStatement":
            state.vars[stmt.var] = interpret_val(stmt.val, state)
        elif stmt.__class__.__name__ == "IterateStatement":
            if stmt.var in state.vars:
                    state.vars[stmt.var] += stmt.multiple  
        elif stmt.__class__.__name__ == "IfStatement":
            unfinished = True
            if handle_if_blocks(state, stmt.ifblock):
                interpret(state, stmt.ifblock.statements)
            else:
                if stmt.elseifblocks is not None:
                    for elseifblock in stmt.elseifblocks:
                        if handle_if_blocks(state, elseifblock):
                            interpret(state, elseifblock.statements)
                            unfinished = False
                            break
                if unfinished and stmt.elseblock is not None:
                    interpret(state, stmt.elseblock.statements)
        elif stmt.__class__.__name__ == "WhileStatement":
            while interpret_val(stmt.conditional, state):
                interpret(state, stmt.whileblock.statements)
        elif stmt.__class__.__name__ == "FromStatement":
            temp = interpret_val(stmt.var, state)
            for i in range(temp, interpret_val(stmt.val, state) + 1):
                state.vars[stmt.var] = i
                interpret(state, stmt.statements)
        elif stmt.__class__.__name__ == "FunctionStatement":
            state.functions[stmt.funcname] = stmt
        """elif stmt.__class__.__name__ == "CallStatement":
            if stmt.funcname in state.functions:
                interpret(state, state.functions[stmt.funcname].statements)"""


def main(debug=False):
    this_folder = dirname(__file__)

    mm = metamodel_from_file(join(this_folder, 'minsym.tx'), debug=False)
    metamodel_export(mm, join(this_folder, 'minsym_meta.dot'))

    # checks syntax of program


    model = mm.model_from_file(join(this_folder, 'testing.minsym'))
    model_export(model, join(this_folder, 'minsym.dot'))

    state = program_state()
    model_statements = model.statements
    interpret(state, model_statements)

if(__name__ == "__main__"):
    main()