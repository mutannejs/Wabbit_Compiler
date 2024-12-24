from functools import singledispatch

from .model import *

class Env:
    def __init__(self):
        self.stack = [{}]

    def newScope(self):
        self.stack.insert(0, {})

    def popScope(self):
        self.stack.pop(0)

    def createRegister(self, name: str, data: Node | None):
        self.stack[0][name] = data

    def setRegister(self, name: str, data: Node):
        for i in range( len(self.stack) ):
            if self.stack[i].get(name):
                self.stack[i][name] = data
                break

    def getRegister(self, name: str) -> Node | None:
        for i in range( len(self.stack) ):
            reg = self.stack[i].get(name)
            if reg: return reg


def interpret_program(model: Node):
    env = Env()

    if not isinstance(model, BlockStatement) and isinstance(model, Statement):
        model = BlockStatement([ model ])

    _interpret(model, env)


inf_int = 2147483647
inf_float = 1.7e+308

def getLiteralFromExpr(node: Expression, env):
    return node if isinstance(node, LiteralT) else _interpret(node, env)

def copyLiteral(node: LiteralT):
    return node.__class__(node.value)


@singledispatch
def _interpret(node: Node, env: Env):
    raise RuntimeError(f"Can't interpret {node}")

rule = _interpret.register

@rule(Integer)
@rule(Float)
@rule(Char)
@rule(Bool)
@rule(Unit)
def _interpret_literal(node: Integer | Float | Char | Bool | Unit, env: Env):
    return node.value

@rule(Break)
@rule(Continue)
def _interpret_breakcontinue(node: Break | Continue, env: Env):
    return node

@rule(PrintStatement)
def _interpret_print(node: PrintStatement, env):
    expr = getLiteralFromExpr( node.expr , env )
    if isinstance(expr, Char):
        print(expr if expr.value != '\\n' else '\n', end='')
    else:
        print( expr )

@rule(UnOp)
def _interpret_unop(node: UnOp, env: Env) -> LiteralT:
    expr = copyLiteral( getLiteralFromExpr(node.expr, env) )

    if node.op == '-':
        expr.value = -1 * expr.value
    elif node.op == '!':
        expr.value = not expr.value

    return expr

@rule(BinOp)
def _interpret_binop(node: BinOp, env: Env):
    left = getLiteralFromExpr(node.left, env)
    right = getLiteralFromExpr(node.right, env)

    res = copyLiteral(left)

    match node.op:
        case '+': res.value = left.value + right.value
        case '-': res.value = left.value - right.value
        case '/':
            if right.value == 0:
                res.value = inf_int if isinstance(right, Integer) else inf_float
            else:
                res.value = left.value / right.value
                if isinstance(left, Integer): res.value = int(res.value)
        case '*': res.value = left.value * right.value
        case '<': res = Bool(left.value < right.value)
        case '>': res = Bool(left.value > right.value)
        case '<=': res = Bool(left.value <= right.value)
        case '>=': res = Bool(left.value >= right.value)
        case '==': res = Bool(left.value == right.value)
        case '!=': res = Bool(left.value != right.value)
        case '&&': res = Bool(left.value and right.value)
        case '||': res = Bool(left.value or right.value)

    return res

@rule(Location)
def _interpret_location(node: Location, env: Env):
    return env.getRegister(node.name)

@rule(VarDefinition)
@rule(ConstDefinition)
def _interpret_definition(node: VarDefinition | ConstDefinition, env: Env):
    name = node.location.name

    if node.value:
        value = getLiteralFromExpr(node.value, env)
    else:
        dtype: DType = node.dtype
        match dtype:
            case 'int': value = Integer(None)
            case 'float': value = Float(None)
            case 'char': value = Char(None)
            case 'bool': value = Bool(None)
            case 'unit': value = Unit()

    env.createRegister(name, value)

@rule(AssignmentStatement)
def _interpret_assignment(node: AssignmentStatement, env: Env):
    nodeval = getLiteralFromExpr(node.value, env)
    env.setRegister( node.location.name, nodeval )

@rule(BlockStatement)
def _interpret_blockstatement(node: BlockStatement, env: Env):
    resp = None
    env.newScope()

    for inst in node.instructions:
        resp = _interpret(inst, env)
        if isinstance(resp, Break) or isinstance(resp, Continue):
            break

    env.popScope()
    return resp

@rule(IfStatement)
def _interpret_Ifstatement(node: IfStatement, env: Env):
    resp = None
    cmp = getLiteralFromExpr(node.cmp, env)
    if _interpret(cmp, env):
        resp = _interpret_blockstatement(node.block_if, env)
    elif node.block_else:
        resp = _interpret_blockstatement(node.block_else, env)

    return resp

@rule(WhileStatement)
def _interpret_whilestatement(node: WhileStatement, env: Env):
    cmp = getLiteralFromExpr(node.cmp, env)
    while _interpret(cmp, env):
        resp = _interpret_blockstatement(node.body, env)
        if isinstance(resp, Break): break
        if isinstance(resp, Continue): continue
        cmp = getLiteralFromExpr(node.cmp, env)

@rule(CompoundExpression)
def _interpret_compoundexpression(node: CompoundExpression, env: Env):
    env.newScope()

    for inst in node.instructions[:-1]:
        _interpret(inst, env)

    expr = getLiteralFromExpr( node.instructions[-1], env )

    env.popScope()
    return expr

# @rule(Argument)
# def _interpret_argument(node: Argument, env: Env) -> DeclarationVar:
#     return DeclarationVar(
#         Location(node.name),
#         dtype = node.dtype
#     )

# @rule(ReturnStatement)
# def _interpret_returnstatement(node: ReturnStatement, env: Env):
#     return _getValue(node.value, env)

# @rule(FunctionDefinition)
# def _interpret_functiondefinition(node: FunctionDefinition, env: Env):
#     env.addDefinition(node)

# @rule(FunctionApplication)
# def _interpret_functionapplication(node: FunctionApplication, env: Env):
#     resp = None
#     func: FunctionDefinition = env.getDefinition(node.name)

#     if func.params:
#         for i in range(len(func.params)):
#             param = _interpret_argument(func.params[i], env)
#             param.value = node.args[i]
#             func.statements.statements.insert(0, param)
#             print(func.statements.statements[0])

#     resp = _interpret_blockstatement(func.statements, env)
#     return resp if func.typeReturn != 'unit' else Unit().value

# @rule(Program)
# def _interpret_program(node: Program, env: Env):
#     for d in node.declarations:
#         _interpret(d, env)
#     _interpret_functionapplication(FunctionApplication('main'), env)