
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
    