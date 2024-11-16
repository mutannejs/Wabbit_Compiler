from typing import Literal


UnOperators = ['+', '-']
BinOperators = ['+', '-', '/', '*', '<', '>', '&&', '||']
DataTypes = ['int', 'float', 'bool']

OpUnType = Literal[*UnOperators]
OpBinType = Literal[*BinOperators]
DType = Literal[*DataTypes]


class Node:
    pass

class Statement(Node):
    pass

class Expression(Node):
    pass

class BlockStatement(Node):
    '''
    Example: a = 1; a = 2;
    '''
    def __init__(self, statements: list[Statement], tabs: int = 0):
        assert isinstance(statements, list)
        for sttmt in statements:
            assert isinstance(sttmt, Statement)
        assert isinstance(tabs, int)
        self.statements = statements
        self.tabs = tabs

    def __repr__(self):
        return f'BlockStatement({self.statements})'

class Char(Expression):
    '''
    Example: 'h'
    '''
    def __init__(self, value: str):
        assert isinstance(value, str)
        assert len(value) == 1
        self.value = value

    def __repr__(self):
        return f'Char({repr(self.value)})'

class Integer(Expression):
    '''
    Example: 42
    '''
    def __init__(self, value: int):
        assert isinstance(value, int)
        self.value = value

    def __repr__(self):
        return f'Integer({self.value})'

class Float(Expression):
    '''
    Example: 3.4
    '''
    def __init__(self, value: float):
        assert isinstance(value, float)
        self.value = value

    def __repr__(self):
        return f'Float({self.value})'

class Bool(Expression):
    '''
    Example: true
    '''
    def __init__(self, value: bool):
        assert type(value) == bool
        self.value = value

    def __repr__(self):
        return f'{self.value}'

class Print(Statement):
    '''
    Example: print 'h'
    '''
    def __init__(self, expr: Expression):
        assert isinstance(expr, Expression)
        self.expr = expr

    def __repr__(self):
        return f'Print( {self.expr} )'

class UnOp(Expression):
    '''
    Example: -5
    '''
    def __init__(self, op: OpUnType, expr: Expression): # type: ignore
        assert op in UnOperators
        assert isinstance(expr, Expression)
        self.op = op
        self.expr = expr

    def __repr__(self):
        return f'UnOp(\'{self.op}\', {self.expr})'

class BinOp(Expression):
    '''
    Example: 3 + 4
    Example: a < 100.0
    '''
    def __init__(self, op: OpBinType, left: Expression, right: Expression): # type: ignore
        assert op in BinOperators
        assert isinstance(left, Expression)
        assert isinstance(right, Expression)
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f'BinOp(\'{self.op}\', {self.left}, {self.right})'

class Location(Expression):
    '''
    a
    '''
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f'Location(\'{self.name}\')'

class DeclarationVar(Statement):
    '''
    var c bool = true;
    '''
    def __init__(self, location: Location, dtype: DType = None, value: Expression = None): # type: ignore
        assert isinstance(location, Location)
        if dtype: assert dtype in DataTypes
        if value: assert isinstance(value, Expression)
        self.location = location
        self.dtype = dtype
        self.value = value

    def __repr__(self):
        return f'DeclarationVar({self.location}, {self.dtype}, {self.value})'

class DeclarationConst(Statement):
    '''
    const c = true;
    '''
    def __init__(self, location: Location, dtype: DType = None, value: Expression = None): # type: ignore
        assert isinstance(location, Location)
        if dtype: assert dtype in DataTypes
        if value: assert isinstance(value, Expression)
        self.location = location
        self.dtype = dtype
        self.value = value

    def __repr__(self):
        return f'DeclarationConst({self.location}, {self.dtype}, {self.value})'

class Assignment(Statement):
    '''
    Example: r = 2.0;
    '''
    def __init__(self, location: Location, value: Expression):
        assert isinstance(location, Location)
        assert isinstance(value, Expression)
        self.location = location
        self.value = value

    def __repr__(self):
        return f'Assignment({self.location}, {self.value})'

class IfStatement(Statement):
    '''
    Example: if a > 0.0 { print a; } else { print -a; }
    '''
    def __init__(self, cmp: Expression, block_if: BlockStatement, block_else: BlockStatement = None):
        assert isinstance(cmp, Expression)
        assert isinstance(block_if, BlockStatement)
        if block_else:
            assert isinstance(block_else, BlockStatement)
        self.cmp = cmp
        self.block_if = block_if
        self.block_else = block_else

    def __repr__(self):
        if self.block_else:
            return f'IfStatement({self.cmp}, {self.block_if}, {self.block_else})'
        else:
            return f'IfStatement({self.cmp}, {self.block_if})'

class WhileStatement(Statement):
    def __init__(self, cmp: Expression, body: BlockStatement):
        assert isinstance(cmp, Expression)
        assert isinstance(body, BlockStatement)
        self.cmp = cmp
        self.body = body

    def __repr__(self):
        return f'WhileStatement({self.cmp}, {self.body})'

class CompoundExpression(Expression):
    '''
    Example: { var t = y; y = x; t; };
    '''
    def __init__(self, instructions: list[Statement | Expression]):
        assert isinstance(instructions, list)
        for inst in instructions[:-1]:
            assert isinstance(inst, Statement)
        assert isinstance(instructions[-1], Expression)
        self.instructions = instructions

    def __repr__(self):
        return f'CompoundExpression({self.instructions}'


from functools import singledispatch
from typing import Any, List, Dict

from Model.Model import *


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
    print(_getValue(node.expr, env), end='')

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