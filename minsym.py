from os.path import join, dirname

from textx import metamodel_from_file
from textx.export import metamodel_export, model_export

# Defines the state of the program
class program_state:
    def __init__(self):
        self.variables = {}
        self.classes = {}
        self.functions = {}
        self.objects = {}
        self.attributes = {}

# Template for a program class
class program_class:
    def __init__(self, name, parameters, methods):
        self.name = name
        self.parameters = parameters
        self.methods = methods

# Interpret a list of statements
def interpret(state, statements):

    for statement in statements:

        if statement.__class__.__name__ == 'AssignmentStatement':
            handle_assignment_statement(state, statement)

        elif statement.__class__.__name__ == 'PrintStatement':
            handle_print_statement(state, statement)

        elif statement.__class__.__name__ == 'CreateClassStatement':
            handle_class_creation(state, statement)

        elif statement.__class__.__name__ == 'CreateObjectStatement':
            handle_object_creation(state, statement)
            
        elif statement.__class__.__name__ == 'AccessClassObject':
            handle_object_access(state, statement)
            
        elif statement.__class__.__name__ == 'CreateFunctionStatement':
            handle_function_creation(state, statement)

        elif statement.__class__.__name__ == 'CallFunction':
            handle_function_call(state, statement)

        elif statement.__class__.__name__ == 'IfStatement':
            result = handle_if_statement(state, statement)
            if result is not None:
                return result

        elif statement.__class__.__name__ == 'ReturnStatement':
            return interpret_expression(state, statement.val)
        
        elif statement.__class__.__name__ == 'WhileStatement':
            handle_while_statement(state, statement)

        elif statement.__class__.__name__ == 'IterateStatement':
            handle_iterate_statement(state, statement)

        elif statement.__class__.__name__ == 'IgnoreStatement':
            pass
                    
def interpret_expression(state, expression):
    if expression.__class__.__name__ == 'VarRef':
        if expression.name in state.variables:
            return state.variables[expression.name]
        else:
            print("Variable '" + expression.name + "' not found")
            quit()
    
    elif expression.__class__.__name__ == 'AccessClassObject':
        return handle_object_access(state, expression) 

    elif expression.__class__.__name__ == 'AttrRef':
        if  expression.name in state.attributes:
            return state.attributes[expression.name]
        else:
            return handle_object_access(state, expression)
    
    elif expression.__class__.__name__ == 'CallFunction':
        return handle_function_call(state, expression)

    elif expression.__class__.__name__ == 'Operation':
        first = interpret_expression(expression.first)
        second = interpret_expression(expression.second)    
        try:
            first = interpret_expression(state, expression.first)
            second = interpret_expression(state, expression.second)
            match expression.op:
                case 'plus':
                    return first + second
                case 'minus':
                    return first - second
                case 'times':
                    return first * second
                case 'divided by':
                    return first / second
                case 'modulo':
                    return first % second
                case 'to the power of':
                    return first ** second
        except TypeError:
            raise Exception("Cannot perform operation on '" + str(first) + "' and '" + str(second) + "'")
    elif expression.__class__.__name__ == 'Comparison':
        try:
            first = interpret_expression(state, expression.first)
            second = interpret_expression(state, expression.second)
            match expression.op:
                case 'is not less than or equal to':
                    return not first <= second
                case 'is not greater than or equal to':
                    return not first >= second
                case 'is not less than':
                    return not first < second
                case 'is not greater than':
                    return not first > second
                case 'is equal to':
                    return first == second
                case 'is not equal to':
                    return first != second
                case 'is less than or equal to':
                    return first <= second
                case 'is greater than or equal to':
                    return first >= second
                case 'is less than':
                    return first < second
                case 'is greater than':
                    return first > second
        except TypeError:
            raise Exception("Cannot compare '" + str(first) + "' to '" + str(second) + "'")
    elif isinstance(expression, str) or isinstance(expression, int) or isinstance(expression, float) or isinstance(expression, bool):
        return expression

def handle_assignment_statement(state, statement):
    value = interpret_expression(state, statement.val)
    variable = None
    if statement.var.__class__.__name__ == 'AccessClassObject':
        print("var is class attribute")
    else:
        variable = statement.var
    state.variables[variable] = value

def handle_print_statement(state, statement):
    for expression in statement.val:
        print(interpret_expression(state, expression))

def function_parser(state, function):
    function_info = {}
    function_info['return_type'] = function.return_type
    function_info['parameters'] = function.parameters.var
    function_info['body'] = function.inner_function_statements
    return function_info

def handle_class_creation(state, statement):
    class_name = statement.name
    class_parameters = statement.parameters.var
    methods = statement.inner_class_statements
    class_methods = {}
    for method in methods:
        method_info = function_parser(state, method)
        class_methods[method.name] = method_info
    new_class = program_class(class_name, class_parameters, class_methods)
    state.classes[class_name] = new_class

def handle_object_creation(state, statement):
    class_name = statement.class_name
    object_name = statement.object_name
    object_args = statement.args.var
    if class_name not in state.classes:
        print("Class '" + class_name + "' not found")
        quit()
    else:
        assciated_class = state.classes[class_name]
        object_info = {}
        object_info['class'] = class_name
        for i in range(len(assciated_class.parameters)):
            object_info[assciated_class.parameters[i]] = object_args[i]
        state.objects[object_name] = object_info

def handle_object_access(state, statement):
    instance_name = statement.instance_name
    if instance_name not in state.objects:
        print("Object '" + statement.instance_name + "' not found")
        quit()
    else:
        object_info = state.objects[instance_name]
        if statement.attribute.__class__.__name__ == 'CallFunction':
            if statement.attribute.name not in state.classes[object_info['class']].methods:
                print("Method '" + statement.attribute.name + "' not found")
                quit()
            else:
                class_parameters = state.classes[object_info['class']].methods[statement.attribute.name]['parameters']
                if len(statement.attribute.args.var) != len(class_parameters):
                    print("Incorrect number of arguments for method '" + statement.attribute.name + "'")
                    quit()
                else:
                    stmts_to_interpret = state.classes[object_info['class']].methods[statement.attribute.name]['body']
                    temp_state = program_state()
                    temp_state.attributes = {key: object_info[key] for key in list(object_info.keys())[1:]}
                    i = 0
                    for parameter in class_parameters:
                        temp_state.variables[parameter] = statement.attribute.args.var[i]
                        i += 1
                    temp_state.functions = state.classes[object_info['class']].methods
                    result = interpret(temp_state, stmts_to_interpret)
                    if result is not None:
                        return result
        else:
            attribute_name = statement.attribute.name
            if attribute_name not in object_info:
                print("Attribute '" + attribute_name + "' not found")
                quit()
            else:
                return object_info[attribute_name]

def handle_function_creation(state, statement):
    function_info = function_parser(state, statement)
    state.functions[statement.name] = function_info
            
def handle_function_call(state, statement):
    if statement.name not in state.functions:
        print("Function '" + statement.name + "' not found")
        quit()
    else:
        function_info = state.functions[statement.name]
        temp_state = program_state()
        temp_state.variables = state.variables
        temp_state.classes = state.classes
        temp_state.functions = state.functions
        temp_state.objects = state.objects
        temp_state.attributes = state.attributes
        for i in range(len(function_info['parameters'])):
            temp_state.variables[function_info['parameters'][i]] = statement.args.var[i]
        result = interpret(temp_state, function_info['body'])
        if result is not None:
            if function_info['return_type'] != 'nothing':
                if (function_info['return_type'] == 'number' and (isinstance(result, int) or isinstance(result, float)) or 
                    function_info['return_type'] == 'string' and isinstance(result, str) or
                    function_info['return_type'] == 'boolean' and isinstance(result, bool)):
                    return result
                else:
                    print("Function '" + statement.name + "' returned incorrect type")
                    quit()
                
def handle_if_statement(state, statement):
    if_block = statement.if_block
    elif_blocks = statement.else_if_blocks
    else_block = statement.else_block
    if interpret_expression(state, if_block.condition):
        result = interpret(state, if_block.inner_if_statements)
        if result is not None:
            return result
    else:
        if elif_blocks is not None:
            finished = False
            for block in elif_blocks:
                if interpret_expression(state, block.condition):
                    result = interpret(state, block.inner_elif_statements)
                    if result is not None:
                        return result
                    finished = True
        if else_block is not None and not finished:
            result = interpret(state, else_block.inner_else_statements)
            if result is not None:
                return result
    
def handle_while_statement(state, statement):
    while interpret_expression(state, statement.condition):
        result = interpret(state, statement.inner_while_statements)
        if result is not None:
            return result

def handle_iterate_statement(state, statement):
    state.variables[statement.var.name] += statement.multiple

def main(debug=False):
    this_folder = dirname(__file__)

    mm = metamodel_from_file(join(this_folder, 'minsym.tx'), debug=False)
    metamodel_export(mm, join(this_folder, 'minsym_meta.dot'))

    # checks syntax of program


    model = mm.model_from_file(join(this_folder, 'testing.minsym'))
    model_export(model, join(this_folder, 'minsym.dot'))

    main_program_state = program_state()
    statements = model.statements
    interpret(main_program_state, statements)

if(__name__ == "__main__"):
    main()