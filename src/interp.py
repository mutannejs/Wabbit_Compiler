from functools import singledispatch
from typing import Any, List, Dict

from .model import *


class EnvDataType():
    def __init__(self, value: Any, changeble: bool, dtype: DType): # type: ignore
        self.value = value
        self.chang = changeble
        self.dtype = dtype

EnvType = List[Dict[str, EnvDataType]]

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
def _interpret_literal(node: Integer | Float | Char | Bool, env: EnvType):
    return node.value

@rule(BlockStatement)
def _interpret_blockstatement_(node: BlockStatement, env: EnvType):
    env.append({})

    for sttmts in node.statements:
        _interpret(sttmts, env)

    env.pop()

@rule(Print)
def _interpret_print(node: Print, env):
    print(_getValue(node.expr, env))

@rule(UnOp)
def _interpret_unop(node: UnOp, env: EnvType):
    exprval = _getValue(node.expr, env)
    if node.op == '+':
        return exprval
    else:
        return -exprval

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
        case '&&': result = leftval and rightval
        case '||': result = leftval or rightval

    return result

@rule(Location)
def _interpret_location(node: Location, env: EnvType):
    for i in range(len(env) - 1, -1, -1):
        if node.name in env[i].keys():
            return env[i].get(node.name)

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

    changeble = True if isinstance(node, DeclarationConst) else False
    env[-1][name] = EnvDataType(value, changeble, dtype)

@rule(Assignment)
def _interpret_assignment(node: Assignment, env: EnvType):
    for i in range(len(env) - 1, -1, -1):
        if node.location.name in env[i].keys():
            _interpret(node.location, env).value = _getValue(node.value, env)

@rule(IfStatement)
def _interpret_Ifstatement(node: IfStatement, env: EnvType):
    if _interpret(node.cmp, env):
        _interpret(node.block_if, env)
    elif node.block_else:
        _interpret(node.block_else, env)

@rule(WhileStatement)
def _interpret_whilestatement(node: WhileStatement, env: EnvType):
    while _interpret(node.cmp, env):
        _interpret(node.body, env)

@rule(CompoundExpression)
def _interpret_compoundexpression(node: CompoundExpression, env: EnvType):
    env.append({})

    for inst in node.instructions:
        _interpret(inst, env)
    
    expr = _getValue(node.instructions[-1], env)

    env.pop()
    return expr


def interpret_program(model: Node):
    # cadeia de dicionários de tuplas (any, MutType, Dtype)
    env = []

    if not isinstance(model, BlockStatement) and isinstance(model, Statement):
        model = BlockStatement([ model ])

    _interpret(model, env)