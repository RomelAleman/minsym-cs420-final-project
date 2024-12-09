from os.path import join, dirname

from textx import metamodel_from_file, textx_isinstance
from textx.export import metamodel_export, model_export

class class_def:
    def __init__(self, **attributes):
        for key, value in attributes.items():
            setattr(self, key, value)

class method_in_class_state:
    def __init__(self):
        self.vars = {}
        self.attributes = {}

    def get_val(self, var):
        return self.vars[var]
    
    def get_attribute(self, attribute):
        return self.attributes[attribute]

class program_state:
    def __init__(self):
        self.functions = {}
        self.vars = {}
        self.classes = {}
        self.objects = {}
        self.class_lookup = {}

    def get_function(self, funcname):
        return self.functions[funcname]
    
    def get_val(self, var):
        return self.vars[var]
    
    def get_class(self, classname):
        return self.classes[classname]
    
    def get_object(self, objectname):
        return self.objects[objectname]
    
    def add_object(self, class_name, instance_name, **attributes):
        if class_name not in self.objects:
            self.objects[class_name] = {}
        self.objects[class_name][instance_name] = class_def(**attributes)
        self.class_lookup[instance_name] = class_name

    def get_object_attribute(self, instance_name, attribute_name):
        class_name = self.class_lookup[instance_name]
        if class_name is not None:
            try:
                if attribute_name.__class__.__name__ == 'AttrRef':   
                    return getattr(self.objects[class_name][instance_name], attribute_name.name)
                elif attribute_name.__class__.__name__ == 'CallFunction':
                    return handle_method_call(self, instance_name, attribute_name.name, attribute_name.args.var)
            except AttributeError:
                raise Exception("'" + attribute_name.name + "' not defined in '" + class_name + "'")
  
def interpret_val(val, state):       
    if val.__class__.__name__ == 'VarRef':
        try:
            return state.vars[val.name]
        except KeyError:
            raise Exception('Variable not defined: ' + val.name)
    elif val.__class__.__name__ == 'AttrRef':
        try:
            return state.get_attribute(val.name)
        except KeyError:
            raise Exception('Attribute not defined: ' + val.name)
        
    elif val.__class__.__name__ == 'AccessClassObject':
        return state.get_object_attribute(val.instance_name, val.attribute)
    
    elif val.__class__.__name__ == 'CallFunction':
        return handle_function_call(state, val.name, val.args.var)
    
    elif val.__class__.__name__ == 'Operation':
        return handle_operation(state, val)
    
    elif val.__class__.__name__ == 'Comparison':
        return handle_comparison(state, val)
    
    elif isinstance(val, str):
        return val
    
    elif isinstance(val, int) or isinstance(val, float):
        return val
    
    elif isinstance(val, bool):
        return val
      
def handle_print(state, printstmt):
    for val in printstmt.val:
        print(interpret_val(val, state), end='')
    print()

def handle_function_call(state, funcname, args):
    func = state.get_function(funcname)
    if len(func.parameters.var) != len(args):
        raise Exception('Incorrect number of arguments')
    else:
        new_state = program_state()
        for var in func.parameters.var:
            new_state.vars[var] = interpret_val(args.pop(0), state)
        if func.return_type != 'nothing':
            val = interpret(new_state, func.inner_function_statements)
            if func.return_type == 'number' and (isinstance(val, float) or isinstance(val, int)):
                return val
            elif func.return_type == 'string' and isinstance(val, str):
                return val
            elif func.return_type == 'boolean' and isinstance(val, bool):
                return val
            else:
                print('ERROR:', 'must return a value of type', func.return_type, 'in function', funcname)
                quit() 
        else:
            interpret(new_state, func.inner_function_statements)

def handle_method_call(state, instance_name, method_name, args):
    class_state = method_in_class_state()
    #class_state.attributes = state.objects[state.class_lookup[instance_name]][instance_name].__dict__
    for attribute in state.classes[state.class_lookup[instance_name]].parameters.var:
        class_state.attributes[attribute] = state.objects[state.class_lookup[instance_name]][instance_name].__dict__[attribute]
    for var in state.objects[state.class_lookup[instance_name]][instance_name].__dict__[method_name].parameters.var:
        class_state.vars[var] = args.pop(0)
    return interpret(class_state, state.objects[state.class_lookup[instance_name]][instance_name].__dict__[method_name].inner_method_statements)
    

def handle_object_creation(state, objectstmt):
    if objectstmt.class_name in state.classes:
        class_info = {}
        for attribute in state.classes[objectstmt.class_name].parameters.var:
            class_info[attribute] = interpret_val(objectstmt.args.var.pop(0), state)
        for stmt in state.classes[objectstmt.class_name].inner_class_statements:
            if stmt.__class__.__name__ == 'CreateMethodStatement':
                class_info[stmt.name] = stmt
        class_info['inner_class_statements'] = state.classes[objectstmt.class_name].inner_class_statements
        #print(class_info['inner_class_statements'])
        state.add_object(objectstmt.class_name, objectstmt.object_name, **class_info)
    
def handle_assignment(state, statement):
    if statement.var.__class__.__name__ == 'AccessClassObject':
        class_name = state.class_lookup[statement.var.instance_name]
        setattr(state.objects[class_name][statement.var.instance_name], statement.var.attribute.name, interpret_val(statement.val, state))
    else:
        state.vars[statement.var] = interpret_val(statement.val, state)

def handle_if_statement(state, ifstmt):
    if_block = ifstmt.if_block
    else_if_block = ifstmt.else_if_block
    else_block = ifstmt.else_block
    if interpret_val(if_block.condition, state):
        return interpret(state, if_block.inner_if_statements)
    else:
        if else_if_block is not None:
            for block in else_if_block:
                if interpret_val(block.condition, state):
                    return interpret(state, block.inner_elif_statements)
        if else_block is not None:
            return interpret(state, else_block.inner_else_statements)

def handle_operation(state, operation):
    try:
        match operation.op:
            case 'plus':
                return interpret_val(operation.first, state) + interpret_val(operation.second, state)
            case 'minus':
                return interpret_val(operation.first, state) - interpret_val(operation.second, state)
            case 'times':
                return interpret_val(operation.first, state) * interpret_val(operation.second, state)
            case 'divided by':
                return interpret_val(operation.first, state) / interpret_val(operation.second, state)
            case 'modulo':
                return interpret_val(operation.first, state) % interpret_val(operation.second, state)
            case 'to the power of':
                return interpret_val(operation.first, state) ** interpret_val(operation.second, state)
    except TypeError:
        raise Exception("Cannot perform operation on '" + str(interpret_val(operation.first, state)) + "' and '" + str(interpret_val(operation.second, state)) + "'")

def handle_comparison(state, comparison):
    try:
        match comparison.op:
            case 'is not less than or equal to':
                return not interpret_val(comparison.first, state) <= interpret_val(comparison.second, state)
            case 'is not greater than or equal to':
                return not interpret_val(comparison.first, state) >= interpret_val(comparison.second, state)
            case 'is not less than':
                return not interpret_val(comparison.first, state) < interpret_val(comparison.second, state)
            case 'is not greater than':
                return not interpret_val(comparison.first, state) > interpret_val(comparison.second, state)
            case 'is equal to':
                return interpret_val(comparison.first, state) == interpret_val(comparison.second, state)
            case 'is not equal to':
                return interpret_val(comparison.first, state) != interpret_val(comparison.second, state)
            case 'is less than or equal to':
                return interpret_val(comparison.first, state) <= interpret_val(comparison.second, state)
            case 'is greater than or equal to':
                return interpret_val(comparison.first, state) >= interpret_val(comparison.second, state)
            case 'is less than':
                return interpret_val(comparison.first, state) < interpret_val(comparison.second, state)
            case 'is greater than':
                return interpret_val(comparison.first, state) > interpret_val(comparison.second, state)
    except TypeError:
        raise Exception("Cannot compare '" + str(interpret_val(comparison.first, state)) + "' to '" + str(interpret_val(comparison.second, state)) + "'")

# General interpreter for program statements
def interpret(state, model_statements):
    for stmt in model_statements:
        if stmt.__class__.__name__ == 'CreateFunctionStatement':
            state.functions[stmt.name] = stmt

        elif stmt.__class__.__name__ == 'AssignmentStatement':
            handle_assignment(state, stmt)

        elif stmt.__class__.__name__ == 'PrintStatement':
            handle_print(state, stmt)

        elif stmt.__class__.__name__ == 'CallFunction':
            handle_function_call(state, stmt.name, stmt.args.var)

        elif stmt.__class__.__name__ == 'ReturnStatement':
            return interpret_val(stmt.val, state)
        
        elif stmt.__class__.__name__ == 'CreateClassStatement':
            state.classes[stmt.name] = stmt

        elif stmt.__class__.__name__ == 'CreateObjectStatement':
            handle_object_creation(state, stmt)

        elif stmt.__class__.__name__ == 'IterateStatement':
            state.vars[stmt.var] += stmt.multiple

        elif stmt.__class__.__name__ == 'WhileStatement':
            while interpret_val(stmt.condition, state):
                interpret(state, stmt.inner_statements)

        elif stmt.__class__.__name__ == 'IfStatement':
            return handle_if_statement(state, stmt)
        
        elif stmt.__class__.__name__ == 'AccessClassObject':
            return state.get_object_attribute(stmt.instance_name, stmt.attribute)
            
# Generate the metamodel and model for program interpretation
def main(debug=False):
    this_folder = dirname(__file__)

    mm = metamodel_from_file(join(this_folder, 'minsym2.tx'), debug=False)
    metamodel_export(mm, join(this_folder, 'minsym2_meta.dot'))

    # checks syntax of program


    model = mm.model_from_file(join(this_folder, 'testing.minsym'))
    model_export(model, join(this_folder, 'minsym2.dot'))

    state = program_state()
    model = model.statements
    interpret(state, model)

if(__name__ == "__main__"):
    main()