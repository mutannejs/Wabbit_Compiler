from typing import Literal


UnOperators = ['+', '-', '!']
BinOperators = ['+', '-', '/', '*', '<', '>', '<=', '>=', '==', '!=', '&&', '||']
DataTypes = ['int', 'float', 'bool', 'unit']

OpUnType = Literal['+', '-', '!']
OpBinType = Literal['+', '-', '/', '*', '<', '>', '<=', '>=', '==', '!=', '&&', '||']
DType = Literal['int', 'float', 'bool', 'unit']


class Node:
    pass

class Statement(Node):
    pass

class Expression(Node):
    pass

class Definition(Node):
    def __init__(self, name: str):
        assert type(name) == str
        self.name = name

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
        return 'true' if self.value else 'false'

class Break(Statement):
    '''
    break;
    '''
    def __init__(self):
        pass

    def __repr__(self):
        return 'Break()'

class Continue(Statement):
    '''
    continue;
    '''
    def __init__(self):
        pass

    def __repr__(self):
        return 'Continue()'

class Unit(Expression):
    '''
    Example: ()
    '''
    def __init__(self):
        self.value = '()'

    def __repr__(self):
        return self.value

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
    def __init__(self, location: Location, value: Expression = None, dtype: DType = None): # type: ignore
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
    def __init__(self, location: Location, value: Expression, dtype: DType = None): # type: ignore
        assert isinstance(location, Location)
        if dtype: assert dtype in DataTypes
        assert isinstance(value, Expression)
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
    def __init__(self, cmp: Expression, block_if: BlockStatement, block_else: BlockStatement = None, tabs: int = 0):
        assert isinstance(cmp, Expression)
        assert isinstance(block_if, BlockStatement)
        if block_else:
            assert isinstance(block_else, BlockStatement)
        assert type(tabs) == int
        self.cmp = cmp
        self.block_if = block_if
        self.block_else = block_else
        self.tabs = tabs

    def __repr__(self):
        if self.block_else:
            return f'IfStatement({self.cmp}, {self.block_if}, {self.block_else})'
        else:
            return f'IfStatement({self.cmp}, {self.block_if})'

class WhileStatement(Statement):
    def __init__(self, cmp: Expression, body: BlockStatement, tabs: int = 0):
        assert isinstance(cmp, Expression)
        assert isinstance(body, BlockStatement)
        assert type(tabs) == int
        self.cmp = cmp
        self.body = body
        self.tabs = tabs

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
        assert isinstance(instructions[-1], Expression) or isinstance(instructions[-1], Statement)
        self.instructions = instructions

    def __repr__(self):
        return f'CompoundExpression({self.instructions})'

class Argument(Node):
    '''
    int a
    '''
    def __init__(self, dtype: DType, name: str): # type: ignore
        assert dtype in DataTypes
        assert isinstance(name, str)
        self.dtype = dtype
        self.name = name

    def __repr__(self):
        return f'Argument({self.name}, {self.dtype})'

class ReturnStatement(Statement):
    '''
    return x + y
    '''
    def __init__(self, expr: Expression):
        assert isinstance(expr, Expression)
        self.value = expr

    def __repr__(self):
        return f'ReturnStatement({self.value})'

class FunctionDefinition(Definition):
    '''
    func add(x int, y int) int {
        return x + y;
    }
    '''
    def __init__(self, name: str, statements: BlockStatement, params: list[Argument] = None, typeReturn: DType = 'unit'): # type: ignore
        super().__init__(name)
        if params != None: assert isinstance(params, list)
        if params != None:
            for a in params: assert isinstance(a, Argument)
        assert typeReturn in DataTypes
        assert isinstance(statements, BlockStatement)
        self.statements = statements
        self.params = params
        self.typeReturn = typeReturn

    def __repr__(self):
        return f'FunctionDefinition({self.name}, {self.params}, {self.statements}, {self.typeReturn})'

class FunctionApplication(Expression):
    '''
    mul(n, factorial(add(n, -1)));
    '''
    def __init__(self, name: str, args: list[Expression] = None):
        assert type(name) == str
        if args:
            assert isinstance(args, list)
            for a in args:
                assert isinstance(a, Expression)
        self.name = name
        self.args = args

    def __repr__(self):
        return f'FunctionApplication(\'{self.name}\', {self.args})'

class Program():
    def __init__(self, declarations: list[Definition | DeclarationVar | DeclarationConst]):
        assert isinstance(declarations, list)
        for d in declarations:
            assert isinstance(d, Definition) or isinstance(d, DeclarationConst) or isinstance(d, DeclarationVar)
        self.declarations = declarations

    def __repr__(self):
        return f'Program({self.declarations})'