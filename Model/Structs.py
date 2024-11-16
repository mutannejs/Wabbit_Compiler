from typing import Literal


OpUnType = Literal['+', '-']
OperatorsUn = ['+', '-']
OpBinType = Literal['+', '-', '/', '*', '<', '>', '&&', '||']
OperatorsBin = ['+', '-', '/', '*', '<', '>', '&&', '||']
MutType = Literal['var', 'const']
Dtype = int | float | bool
BoolType = Literal['true', 'false']


class Node:
    pass

class Statement(Node):
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

class Expression(Node):
    pass

class Char(Expression):
    '''
    Example: 'h'
    '''
    def __init__(self, value: str):
        assert isinstance(value, str)
        assert len(value) == 1
        self.value = value

    def __repr__(self):
        return f'Char(\'{self.value}\')'

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
    def __init__(self, value: BoolType):
        assert value in ['true', 'false']
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
    def __init__(self, op: OpUnType, expr: Expression):
        assert op in OperatorsUn
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
    def __init__(self, op: OpBinType, left: Expression, right: Expression):
        assert op in OperatorsBin
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

class Declaration(Statement):
    '''
    var c bool = true;
    '''
    def __init__(self, mut: MutType, location: Location, dtype: Dtype = None, value: Expression = None):
        assert mut in ['var', 'const']
        assert isinstance(location, Location)
        if dtype: assert (dtype, Dtype)
        if value: assert isinstance(value, Expression)
        self.mut = mut
        self.location = location
        self.dtype = dtype
        self.value = value

    def __repr__(self):
        return f'Declaration(\'{self.mut}\', {self.location}, {self.dtype}, {self.value})'

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