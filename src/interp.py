from functools import singledispatch

from .model import *

class Env:
    def __init__(self):
        self.stack = [{}]
        self.global_vars = {}
        self.registers = []
        self.functions = {}
        self.returnValue = []

    def newScope(self):
        self.stack.insert(0, {})

    def popScope(self):
        self.stack.pop(0)

    def pushRegister(self):
        self.registers.append( self.stack )
        self.stack = [{}]

    def popRegister(self):
        self.stack = self.registers.pop()

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
        return self.global_vars.get(name)


def interpret_program(model: list[Node]):
    env = Env()

    for s in model:
        _interpret(s, env)

        for key in list(env.stack[0]):
            env.global_vars[key] = env.stack[0].get(key)
        env.stack[0] = {}

    (_, main) = env.functions['main']

    getLiteralFromExpr(main, env)
    resp = env.returnValue.pop().value
    return resp

inf_int = 2147483647
inf_float = 1.7e+308

def getLiteralFromExpr(node: Expression, env):
    return node if isinstance(node, LiteralT) else _interpret(node, env)

def copyLiteral(node: LiteralT):
    return node.__class__(node.lineno, node.value)


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
        case '<': res = Bool(node.lineno, left.value < right.value)
        case '>': res = Bool(node.lineno, left.value > right.value)
        case '<=': res = Bool(node.lineno, left.value <= right.value)
        case '>=': res = Bool(node.lineno, left.value >= right.value)
        case '==': res = Bool(node.lineno, left.value == right.value)
        case '!=': res = Bool(node.lineno, left.value != right.value)
        case '&&': res = Bool(node.lineno, left.value and right.value)
        case '||': res = Bool(node.lineno, left.value or right.value)

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
            case 'int': value = Integer(node.lineno, None)
            case 'float': value = Float(node.lineno, None)
            case 'char': value = Char(node.lineno, None)
            case 'bool': value = Bool(node.lineno, None)
            case 'unit': value = Unit(node.lineno)

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
        if isinstance(resp, Break) or \
                isinstance(resp, Continue) or \
                isinstance(resp, ReturnStatement):
            break

    env.popScope()
    return resp if resp else Unit(node.lineno)

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
        if isinstance(resp, Break) or isinstance(resp, ReturnStatement): break
        if isinstance(resp, Continue): continue
        cmp = getLiteralFromExpr(node.cmp, env)
    return resp if isinstance(resp, ReturnStatement) else None

@rule(CompoundExpression)
def _interpret_compoundexpression(node: CompoundExpression, env: Env):
    env.newScope()

    for inst in node.instructions[:-1]:
        _interpret(inst, env)

    expr = getLiteralFromExpr( node.instructions[-1], env )

    env.popScope()
    return expr

@rule(FunctionParam)
def _interpret_functionparam(node: FunctionParam, env: Env):
    return (node.name, node.dtype)

@rule(FunctionDefinition)
def _interpret_functiondefinition(node: FunctionDefinition, env: Env):
    params = []
    for p in node.params:
        params.append( _interpret_functionparam(p, env) )

    function = node.body
    env.functions[node.name] = (params, function)

@rule(FunctionCall)
def _interpret_functioncall(node: FunctionCall, env: Env):
    (params, function) = env.functions[node.name]
    lin = node.lineno

    args_interp = []
    for i in range( len(params) ):
        (name, dtype) = params[i]
        args_interp.append(
            VarDefinition(
                lin,
                Location(lin, name, dtype),
                getLiteralFromExpr(node.args[i], env),
                dtype
            )
        )

    env.pushRegister()

    args_interp.extend(function.instructions)
    function_body = BlockStatement(lin, args_interp)
    resp = _interpret_blockstatement(function_body, env)

    env.popRegister()

    if isinstance(resp, ReturnStatement):
        resp = env.returnValue.pop()
    else:
        resp = Unit(node.lineno)

    return resp

@rule(ReturnStatement)
def _interpret_ReturnStatement(node: ReturnStatement, env: Env):
    ret_literal = getLiteralFromExpr(node.expr, env)
    env.returnValue.append(ret_literal)
    return node