from os.path import join, dirname

from textx import metamodel_from_file, textx_isinstance
from textx.export import metamodel_export, model_export

class program_state:
    def __init__(self):
        self.vars = {}
    def get_value(self, var):
        return self.vars[var]

def interpret_val(val, state):
    if val in state.vars:
        return state.vars[val]
    elif val is bool:
        return val
    
def interpret_else_if(state, else_statement):
    

def interpret(state, model_statements):
    for stmt in model_statements:
        if stmt.__class__.__name__ == "PrintStatement":
            for val in stmt.vals:
                if isinstance(val, bool):
                    print(val)
                elif '"' in val or val.isdigit():
                    print(val.replace('"', ''))
                else:
                    print(interpret_val(val, state))   
        elif stmt.__class__.__name__ == "AssignmentStatement":
            state.vars[stmt.var] = stmt.val
        elif stmt.__class__.__name__ == "IfStatement":
            if stmt.conditional:
                    interpret(state, stmt.statements)
            else:
                if stmt.elsestatement is not None:
                    if stmt.elsestatement.elseif is not None:
                        interpret_else_if(state, stmt.elsestatement)
                    

        
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