from typing import Literal


UnOperators = ['+', '-', '!']
BinOperators = ['+', '-', '/', '*', '<', '>', '<=', '>=', '==', '!=', '&&', '||']
DataTypes = ['int', 'float', 'bool', 'unit', 'char']

UnOpType = Literal['+', '-', '!']
BinOpType = Literal['+', '-', '/', '*', '<', '>', '<=', '>=', '==', '!=', '&&', '||']
DType = Literal['int', 'float', 'bool', 'unit', 'char']


class Node:
    def __init__(self, lineno: int):
        self.lineno = lineno

class Statement(Node):
    pass

class Expression(Node):
    pass

class LiteralT(Expression):
    def __init__(self, lineno: int, value):
        super().__init__(lineno)
        self.value = value

    def __repr__(self):
        return f'{self.value}'

class Integer(LiteralT):
    '''
    Example: 42
    '''
    def __init__(self, lineno: int, value: int | None):
        super().__init__(lineno, value)

class Float(LiteralT):
    '''
    Example: 3.4
    '''
    def __init__(self, lineno: int, value: float | None):
        super().__init__(lineno, value)

class Char(LiteralT):
    '''
    Example: 'h'
             'x\ff'
             '\n'
    '''
    def __init__(self, lineno: int, value: str | None):
        super().__init__(lineno, value)

    def __repr__(self):
        return f"{self.value}"

class Bool(LiteralT):
    '''
    Example: true
             false
    '''
    def __init__(self, lineno: int, value: bool | None):
        super().__init__(lineno, value)

    def __repr__(self):
        return 'true' if self.value else 'false'

class Unit(LiteralT):
    '''
    Example: ()
    '''
    def __init__(self, lineno: int, value = '()'):
        super().__init__(lineno, '()')

class Break(Statement):
    '''
    break;
    '''
    def __init__(self, lineno: int):
        super().__init__(lineno)

    def __repr__(self):
        return 'Break()'

class Continue(Statement):
    '''
    continue;
    '''
    def __init__(self, lineno: int):
        super().__init__(lineno)

    def __repr__(self):
        return 'Continue()'

class PrintStatement(Statement):
    '''
    Example: print 'h'
             print 5 + 9
    '''
    def __init__(self, lineno: int, expr: Expression):
        super().__init__(lineno)
        self.expr = expr

    def __repr__(self):
        return f'PrintStatement({ self.expr })'

class UnOp(Expression):
    '''
    Example: -5
             !expr
    '''
    def __init__(self, lineno: int, op: UnOpType, expr: Expression):
        super().__init__(lineno)
        self.op = op
        self.expr = expr

    def __repr__(self):
        return f'UnOp({self.op}, {self.expr})'

class BinOp(Expression):
    '''
    Example: 3 + 4
             a < 100.0
    '''
    def __init__(self, lineno: int, op: BinOpType, left: Expression, right: Expression):
        super().__init__(lineno)
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f'BinOp({self.op}, {self.left}, {self.right})'

class Location(Expression):
    '''
    Example: a
             loc
    '''
    def __init__(self, lineno: int, name: str):
        super().__init__(lineno)
        self.name = name

    def __repr__(self):
        return self.name

class VarDefinition(Statement):
    '''
    var c bool = true;
    '''
    def __init__(self, lineno: int, location: Location, value: Expression = None, dtype: DType = None):
        super().__init__(lineno)
        self.location = location
        self.dtype = dtype
        self.value = value

    def __repr__(self):
        return f'VarDefinition({self.location}, {self.dtype}, {self.value})'

class ConstDefinition(Statement):
    '''
    const c = true;
    '''
    def __init__(self, lineno: int, location: Location, value: Expression, dtype: DType = None):
        super().__init__(lineno)
        self.location = location
        self.dtype = dtype
        self.value = value

    def __repr__(self):
        return f'ConstDefinition({self.location}, {self.dtype}, {self.value})'

class AssignmentStatement(Statement):
    '''
    Example: r = 2.0;
    '''
    def __init__(self, lineno: int, location: Location, value: Expression):
        super().__init__(lineno)
        self.location = location
        self.value = value

    def __repr__(self):
        return f'AssignmentStatement({self.location}, {self.value})'

class BlockStatement(Node):
    '''
    Example: a = 1; a = 2;
    '''
    def __init__(self, lineno: int, instructions: list):
        super().__init__(lineno)
        self.instructions = instructions

    def __repr__(self):
        return f'BlockStatement( { self.instructions } )'

class IfStatement(Statement):
    '''
    Example: if a > 0.0 { print a; } else { print -a; }
    '''
    def __init__(self, lineno: int, cmp: Expression, block_if: BlockStatement, block_else: BlockStatement = None):
        super().__init__(lineno)
        self.cmp = cmp
        self.block_if = block_if
        self.block_else = block_else

    def __repr__(self):
        if self.block_else:
            return f'IfStatement({self.cmp}, {self.block_if}, {self.block_else})'
        else:
            return f'IfStatement({self.cmp}, {self.block_if})'

class WhileStatement(Statement):
    def __init__(self, lineno: int, cmp: Expression, body: BlockStatement):
        super().__init__(lineno)
        self.cmp = cmp
        self.body = body

    def __repr__(self):
        return f'WhileStatement({self.cmp}, {self.body})'

class CompoundExpression(Expression):
    '''
    Example: { var t = y; y = x; t; };
    '''
    def __init__(self, lineno: int, instructions: list):
        super().__init__(lineno)
        self.instructions = instructions

    def __repr__(self):
        return f'CompoundExpression( {self.instructions} )'

# class Argument(Node):
#     '''
#     int a
#     '''
#     def __init__(self, dtype: DType, name: str): # type: ignore
#         assert dtype in DataTypes
#         assert isinstance(name, str)
#         self.dtype = dtype
#         self.name = name

#     def __repr__(self):
#         return f'Argument({self.name}, {self.dtype})'

# class ReturnStatement(Statement):
#     '''
#     return x + y
#     '''
#     def __init__(self, expr: Expression):
#         assert isinstance(expr, Expression)
#         self.value = expr

#     def __repr__(self):
#         return f'ReturnStatement({self.value})'

# class FunctionDefinition(Definition):
#     '''
#     func add(x int, y int) int {
#         return x + y;
#     }
#     '''
#     def __init__(self, name: str, statements: BlockStatement, params: list[Argument] = None, typeReturn: DType = 'unit'): # type: ignore
#         super().__init__().__init__(name)
#         if params != None: assert isinstance(params, list)
#         if params != None:
#             for a in params: assert isinstance(a, Argument)
#         assert typeReturn in DataTypes
#         assert isinstance(statements, BlockStatement)
#         self.statements = statements
#         self.params = params
#         self.typeReturn = typeReturn

#     def __repr__(self):
#         return f'FunctionDefinition({self.name}, {self.params}, {self.statements}, {self.typeReturn})'

# class FunctionApplication(Expression):
#     '''
#     mul(n, factorial(add(n, -1)));
#     '''
#     def __init__(self, name: str, args: list[Expression] = None):
#         assert type(name) == str
#         if args:
#             assert isinstance(args, list)
#             for a in args:
#                 assert isinstance(a, Expression)
#         self.name = name
#         self.args = args

#     def __repr__(self):
#         return f'FunctionApplication(\'{self.name}\', {self.args})'

# class Program():
#     def __init__(self, definitions: list[Statement]):
#         assert isinstance(definitions, list)
#         for d in definitions:
#             assert isinstance(d, Statement)
#         self.definitions = definitions

#     def __repr__(self):
#         return f'Program( {self.definitions} )'