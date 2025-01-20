from functools import singledispatch

from .model import *


class Env:
    def __init__(self):
        self.stack = [{}]

    def newScope(self):
        self.stack.insert(0, {})

    def popScope(self):
        self.stack.pop(0)

    def createRegister(self, name: str, value: Expression):
        self.stack[0][name] = value

    def setRegister(self, name: str, value: Expression):
        for i in range( len(self.stack) ):
            if self.stack[i].get(name):
                self.stack[i][name] = value
                break

    def getRegister(self, name: str, deep: int = -1) -> DType | None:
        length = deep if deep < len(self.stack) and deep > -1 else len(self.stack)
        for i in range( length ):
            reg = self.stack[i].get(name)
            if reg: return reg


class Context:
    def __init__(self):
        self.env = Env()


def transform_program(model):
    ctx = Context()
    return _transform(model, ctx)


@singledispatch
def _transform(node: Node, ctx: Context):
    raise RuntimeError(f"{node} not compile")

rule = _transform.register

@rule(Integer)
@rule(Float)
@rule(Char)
@rule(Bool)
@rule(Unit)
def _transform_literal(node: LiteralT, ctx: Context):
    return node

@rule(BinOp)
def _transform_binop(node: BinOp, ctx: Context):
    left = _transform(node.left, ctx)
    right = _transform(node.right, ctx)

    if not ( node.op in ['&&', '||'] and isinstance(left, Bool) ) and \
        ( not isinstance(left, LiteralT) or not isinstance(right, LiteralT) ):
        return BinOp(node.lineno, node.op, left, right)

    new_value = ''
    match node.op:
        case '+': new_value = f'{repr(left.value)} + {repr(right.value)}'
        case '-': new_value = f'{repr(left.value)} - {repr(right.value)}'
        case '/': new_value = f'{repr(left.value)} / {repr(right.value)}'
        case '*': new_value = f'{repr(left.value)} * {repr(right.value)}'
        case '<': new_value = f'{repr(left.value)} < {repr(right.value)}'
        case '>': new_value = f'{repr(left.value)} > {repr(right.value)}'
        case '<=': new_value = f'{repr(left.value)} <= {repr(right.value)}'
        case '>=': new_value = f'{repr(left.value)} >= {repr(right.value)}'
        case '==': new_value = f'{repr(left.value)} == {repr(right.value)}'
        case '!=': new_value = f'not {repr(left.value)} == {repr(right.value)}'
        case '&&': new_value = 'False' if not left.value else \
            f'{repr(left.value)} and {repr(right.value)}'
        case '||': new_value = 'True' if left.value else \
            f'{repr(left.value)} or {repr(right.value)}'

    if node.op in ['<', '<=', '>', '>=', '==', '!=', '&&', '||']:
        return Bool(node.lineno, eval(new_value))
    if isinstance(left, Integer):
        return Integer(node.lineno, eval(new_value))
    if isinstance(left, Float):
        return Float(node.lineno, eval(new_value))

@rule(UnOp)
def _transform_unop(node: UnOp, ctx: Context):
    expr = _transform(node.expr, ctx)

    if not isinstance(expr, LiteralT):
        return UnOp(node.lineno, node.op, expr)

    if node.op == '-':
        new_value = f'-{expr.value}'
    elif node.op == '!':
        new_value = f'not {repr(expr.value)}'
    else:
        new_value = f'+{expr.value}'

    if isinstance(expr, Integer): return Integer(node.lineno, eval(new_value))
    if isinstance(expr, Float): return Float(node.lineno, eval(new_value))
    if isinstance(expr, Bool): return Bool(node.lineno, eval(new_value))

@rule(PrintStatement)
def _transform_print_statement(node: PrintStatement, ctx: Context):
    return PrintStatement(
        node.lineno,
        _transform(node.expr, ctx)
    )

@rule(Location)
def _transform_location(node: Location, ctx: Context):
    value = ctx.env.getRegister(node.name)
    return value if not value == None else node

@rule(VarDefinition)
@rule(ConstDefinition)
def _interpret_definition(node: VarDefinition | ConstDefinition, ctx: Context):
    if node.value:
        value = _transform(node.value, ctx)
        dtype = node.value.p_type
    else:
        value = None
        dtype = node.dtype

    if isinstance(node, VarDefinition):
        return VarDefinition(node.lineno, node.location, value, dtype)
    else:
        ctx.env.createRegister(node.location.name, value)
        return None

@rule(AssignmentStatement)
def _transform_assignmentstatement(node: AssignmentStatement, ctx: Context):
    value = _transform(node.value, ctx)
    location = _transform_location(node.location, ctx)

    if isinstance(location, Location):
        return AssignmentStatement(node.lineno, node.location, value)
    else:
        ctx.env.setRegister(location, value)
        return None

@rule(IfStatement)
def _transform_ifstatement(node: IfStatement, ctx: Context):
    cmp = _transform(node.cmp, ctx)

    block_if = _transform_blockstatement(node.block_if, ctx)

    if node.block_else:
        block_else = _transform_blockstatement(node.block_else, ctx)
    else:
        block_else = None

    if len(block_if.instructions) == 0:
        block_if = None
    if block_else and len(block_else.instructions) == 0:
        block_else = None

    if isinstance(cmp, Bool):
        if cmp.value and block_if:
            return block_if
        elif not cmp.value and block_else:
            return block_else
        else:
            return None
    else:
        if block_if:
            return IfStatement(node.lineno, cmp, block_if, block_else)
        else:
            return None

@rule(WhileStatement)
def _transform_whilestatement(node: WhileStatement, ctx: Context):
    cmp = _transform(node.cmp, ctx)
    body = _transform(node.body, ctx)

    if isinstance(cmp, Bool) and not cmp.value:
        return None
    else:
        return WhileStatement(node.lineno, cmp, body)

@rule(Break)
@rule(Continue)
def _interpret_breakcontinue(node: Break | Continue, ctx: Context):
    return node

@rule(CompoundExpression)
def _transform_compoundexpression(node: CompoundExpression, ctx: Context):
    ctx.env.newScope()

    insts = []
    for inst in node.instructions[:-1]:
        inst_t = _transform(inst, ctx)
        # if isinstance(inst_t, Statement):
        #     insts.append(inst_t)
        if inst_t:
            insts.append(inst_t)

    inst_t = _transform( node.instructions[-1], ctx )

    ctx.env.popScope()

    # if isinstance(inst_t, LiteralT):
    #     return inst_t
    # elif isinstance(inst_t, Expression):
    if isinstance(inst_t, Expression):
        insts.append(inst_t)
        return CompoundExpression(node.lineno, insts)
    else:
        return None

@rule(BlockStatement)
def _transform_blockstatement(node: BlockStatement, ctx: Context):
    ctx.env.newScope()

    insts = []
    for inst in node.instructions:
        inst_t = _transform(inst, ctx)
        if inst_t == None:
            continue
        elif isinstance(inst_t, BlockStatement):
            insts.extend(inst_t.instructions)
        else:
            insts.append(inst_t)

    ctx.env.popScope()
    if len(insts) == 0:
        return None
    else:
        return BlockStatement(node.lineno, insts)