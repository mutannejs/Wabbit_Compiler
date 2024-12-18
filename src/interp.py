from functools import singledispatch
from typing import Any, List, Dict

from model import *

class EnvDataType():
    def __init__(self, value: Any, changeble: bool, dtype: DType): # type: ignore
        self.value = value
        self.chang = changeble
        self.dtype = dtype

class EnvType:
    def __init__(self):
        self.declarations: Dict[str, Definition] = {}
        self.stack: List[Dict[str, EnvDataType]] = []

    def newScope(self):
        self.stack.append({})

    def popScope(self):
        self.stack.pop()

    def addDefinition(self, definition: Definition):
        self.declarations[definition.name] = definition

    def addData(self, name: str, data: EnvDataType):
        exists = self.stack[-1].get(name)
        assert not exists or exists.chang
        self.stack[-1][name] = data

    def getDefinition(self, name: str):
        return self.declarations.get(name)

    def getData(self, name: str):
        for i in range( len(self.stack) - 1, -1, -1 ):
            if name in self.stack[i].keys():
                return self.stack[i].get(name)

def _getValue(expr: Expression, env: EnvType):
    val = _interpret(expr, env)
    if isinstance(expr, Location):
        val = val.value
    return val

@singledispatch
def _interpret(node: Node, env: EnvType):
    raise RuntimeError(f"Can't interpret {node}")

rule = _interpret.register

@rule(Integer)
@rule(Float)
@rule(Char)
@rule(Bool)
@rule(Unit)
def _interpret_literal(node: Integer | Float | Char | Bool, env: EnvType):
    return node.value

@rule(Break)
@rule(Continue)
def _interpret_breakcontinue(node: Break | Continue, env: EnvType):
    return node

@rule(BlockStatement)
def _interpret_blockstatement(node: BlockStatement, env: EnvType):
    resp = None
    env.newScope()

    for sttmt in node.statements:
        resp = _interpret(sttmt, env)
        if isinstance(sttmt, ReturnStatement) or isinstance(resp, Break) or isinstance(resp, Continue):
            break

    env.popScope()
    return resp if resp else Unit()

@rule(Print)
def _interpret_print(node: Print, env):
    print(_getValue(node.expr, env))

@rule(UnOp)
def _interpret_unop(node: UnOp, env: EnvType):
    exprval = _getValue(node.expr, env)
    if node.op == '+':
        return exprval
    elif node.op == '-':
        return -exprval
    else:
        return not exprval

@rule(BinOp)
def _interpret_binop(node: BinOp, env: EnvType):
    leftval = _getValue(node.left, env)
    rightval = _getValue(node.right, env)

    result = 0
    match node.op:
        case '+': result = leftval + rightval
        case '-': result = leftval - rightval
        case '/': result = leftval / rightval
        case '*': result = leftval * rightval
        case '<': result = leftval < rightval
        case '>': result = leftval > rightval
        case '<=': result = leftval <= rightval
        case '>=': result = leftval >= rightval
        case '==': result = leftval == rightval
        case '!=': result = leftval != rightval
        case '&&': result = leftval and rightval
        case '||': result = leftval or rightval

    return result

@rule(Location)
def _interpret_location(node: Location, env: EnvType):
    return env.getData(node.name)

@rule(DeclarationVar)
@rule(DeclarationConst)
def _interpret_declaration(node: DeclarationVar | DeclarationConst, env: EnvType):
    name = node.location.name
    dtype = value = None

    if node.value:
        value = _getValue(node.value, env)
        dtype = type(value)

    if dtype == None:
        dtype = node.dtype

    changeble = True if isinstance(node, DeclarationVar) else False
    env.addData(name, EnvDataType(value, changeble, dtype))

@rule(Assignment)
def _interpret_assignment(node: Assignment, env: EnvType):
    location = env.getData(node.location.name)
    if location:
        location.value = _getValue(node.value, env)

@rule(IfStatement)
def _interpret_Ifstatement(node: IfStatement, env: EnvType):
    resp = None
    if _interpret(node.cmp, env):
        resp = _interpret_blockstatement(node.block_if, env)
    elif node.block_else:
        resp = _interpret_blockstatement(node.block_else, env)

    if resp: return resp

@rule(WhileStatement)
def _interpret_whilestatement(node: WhileStatement, env: EnvType):
    resp = None
    while _interpret(node.cmp, env):
        resp = _interpret_blockstatement(node.body, env)
        if isinstance(resp, Break): break
        if isinstance(resp, Continue): continue

    if resp: return resp

@rule(CompoundExpression)
def _interpret_compoundexpression(node: CompoundExpression, env: EnvType):
    env.newScope()

    for inst in node.instructions[:-1]:
        _interpret(inst, env)

    expr = _getValue(node.instructions[-1], env)

    env.popScope()
    return expr

@rule(Argument)
def _interpret_argument(node: Argument, env: EnvType) -> DeclarationVar:
    return DeclarationVar(
        Location(node.name),
        dtype = node.dtype
    )

@rule(ReturnStatement)
def _interpret_returnstatement(node: ReturnStatement, env: EnvType):
    return _getValue(node.value, env)

@rule(FunctionDefinition)
def _interpret_functiondefinition(node: FunctionDefinition, env: EnvType):
    env.addDefinition(node)

@rule(FunctionApplication)
def _interpret_functionapplication(node: FunctionApplication, env: EnvType):
    resp = None
    func: FunctionDefinition = env.getDefinition(node.name)

    if func.params:
        for i in range(len(func.params)):
            param = _interpret_argument(func.params[i], env)
            param.value = node.args[i]
            func.statements.statements.insert(0, param)
            print(func.statements.statements[0])

    resp = _interpret_blockstatement(func.statements, env)
    return resp if func.typeReturn != 'unit' else Unit().value

@rule(Program)
def _interpret_program(node: Program, env: EnvType):
    for d in node.declarations:
        _interpret(d, env)
    _interpret_functionapplication(FunctionApplication('main'), env)

def interpret_program(model: Node):
    env = EnvType()

    if not isinstance(model, BlockStatement) and isinstance(model, Statement):
        model = BlockStatement([ model ])

    _interpret(model, env)