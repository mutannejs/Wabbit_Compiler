from typing import Literal


UnOperators = ['+', '-', '!']
BinOperators = ['+', '-', '/', '*', '<', '>', '<=', '>=', '==', '!=', '&&', '||']
DataTypes = ['int', 'float', 'bool', 'unit', 'char']

UnOpType = Literal['+', '-', '!']
BinOpType = Literal['+', '-', '/', '*', '<', '>', '<=', '>=', '==', '!=', '&&', '||']
DType = Literal['int', 'float', 'bool', 'unit', 'char']


class Node:
    pass

class Statement(Node):
    pass

class Expression(Node):
    pass

class LiteralT(Expression):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'{self.value}'

class Definition(Node):
    pass

class Char(LiteralT):
    '''
    Example: 'h'
             'x\ff'
             '\n'
    '''
    def __init__(self, value: str):
        super().__init__(value)

    def __repr__(self):
        return f"'{self.value}'"

class Integer(LiteralT):
    '''
    Example: 42
    '''
    def __init__(self, value: int):
        super().__init__(value)

class Float(LiteralT):
    '''
    Example: 3.4
    '''
    def __init__(self, value: float):
        super().__init__(value)

class Bool(LiteralT):
    '''
    Example: true
             false
    '''
    def __init__(self, value: bool):
        assert type(value) == bool
        super().__init__(value)

    def __repr__(self):
        return 'true' if self.value else 'false'

class Unit(LiteralT):
    '''
    Example: ()
    '''
    def __init__(self):
        super().__init__('()')

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

class PrintStatement(Statement):
    '''
    Example: print 'h'
             print 5 + 9
    '''
    def __init__(self, expr: Expression):
        assert isinstance(expr, Expression)
        self.expr = expr

    def __repr__(self):
        return f'PrintStatement({ self.expr })'

class UnOp(Expression):
    '''
    Example: -5
             !expr
    '''
    def __init__(self, op: UnOpType, expr: Expression):
        assert op in UnOperators
        assert isinstance(expr, Expression)
        self.op = op
        self.expr = expr

    def __repr__(self):
        return f'UnOp({self.op}, {self.expr})'

class BinOp(Expression):
    '''
    Example: 3 + 4
             a < 100.0
    '''
    def __init__(self, op: BinOpType, left: Expression, right: Expression):
        assert op in BinOperators
        assert isinstance(left, Expression)
        assert isinstance(right, Expression)
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
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name

class VarDefinition(Statement):
    '''
    var c bool = true;
    '''
    def __init__(self, location: Location, value: Expression = None, dtype: DType = None):
        assert isinstance(location, Location)
        if value: assert isinstance(value, Expression)
        if dtype: assert dtype in DataTypes
        self.location = location
        self.dtype = dtype
        self.value = value

    def __repr__(self):
        return f'VarDefinition({self.location}, {self.dtype}, {self.value})'

class ConstDefinition(Statement):
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
        return f'ConstDefinition({self.location}, {self.dtype}, {self.value})'

class AssignmentStatement(Statement):
    '''
    Example: r = 2.0;
    '''
    def __init__(self, location: Location, value: Expression):
        assert isinstance(location, Location)
        assert isinstance(value, Expression)
        self.location = location
        self.value = value

    def __repr__(self):
        return f'AssignmentStatement({self.location}, {self.value})'

class BlockStatement(Node):
    '''
    Example: a = 1; a = 2;
    '''
    def __init__(self, instructions: list):
        self.instructions = instructions

    def __repr__(self):
        return f'BlockStatement( { self.instructions } )'

class IfStatement(Statement):
    '''
    Example: if a > 0.0 { print a; } else { print -a; }
    '''
    def __init__(self, cmp: Expression, block_if: BlockStatement, block_else: BlockStatement = None):
        assert isinstance(cmp, Expression)
        assert isinstance(block_if, BlockStatement)
        if block_else: assert isinstance(block_else, BlockStatement)
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
    def __init__(self, instructions: list):
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


class _NodeVisitor:
    def __init__(self):
        self.tabs = -1

    def visit(self, node: Node):
        methname = node.__class__.__name__
        return getattr(self, f'visit_{methname}')(node)

    def visit_Integer(self, node: Integer):
        return node.value

    def visit_Float(self, node: Float):
        return node.value

    def visit_Char(self, node: Char):
        return repr(node.value) if node.value[0] != '\\' else f"'{node.value}'"

    def visit_Bool(self, node: Bool):
        return 'true' if node.value else 'false'

    def visit_Unit(self, node: Unit):
        return '()'

    def visit_Break(self, node: Break):
        return 'break;'

    def visit_Continue(self, node: Continue):
        return 'continue;'

    def visit_PrintStatement(self, node: PrintStatement):
        return f'print {self.visit(node.expr)};'

    def visit_UnOp(self, node: UnOp):
        return f'{node.op}{self.visit(node.expr)}'

    def visit_BinOp(self, node: BinOp):
        return f'{self.visit(node.left)} {node.op} {self.visit(node.right)}'

    def visit_Location(self, node: Location):
        return f'{node.name}'

    def visit_VarDefinition(self, node: VarDefinition):
        base = f'var {self.visit(node.location)}'
        dtype = f' {node.dtype}' if node.dtype != None else ''
        value = f' = {self.visit(node.value)}' if node.value != None else ''
        return base + dtype + value + ';'

    def visit_ConstDefinition(self, node: ConstDefinition):
        base = f'const {self.visit(node.location)}'
        dtype = f' {node.dtype}' if node.dtype != None else ''
        value = f' = {self.visit(node.value)}' if node.value != None else ''
        return base + dtype + value + ';'

    def visit_AssignmentStatement(self, node: AssignmentStatement):
        return f'{self.visit(node.location)} = {self.visit(node.value)};'

    def visit_BlockStatement(self, node: BlockStatement):
        self.tabs += 1
        tabs = ''.rjust(self.tabs * 4, ' ')

        insts = ''
        for inst in node.instructions:
            insts += tabs + self.visit(inst) + '\n'

        self.tabs -= 1
        return insts

    def visit_IfStatement(self, node: IfStatement):
        tabs = ''.rjust(self.tabs * 4, ' ')
        block_if = f'if {self.visit(node.cmp)} {{\n{self.visit(node.block_if)}{tabs}}}'
        block_else = f' else {{\n{self.visit(node.block_else)}{tabs}}}' if node.block_else else ''
        return block_if + block_else

    def visit_WhileStatement(self, node: WhileStatement):
        tabs = ''.rjust(self.tabs * 4, ' ')
        cmp = self.visit(node.cmp)
        body = self.visit(node.body)
        return f'while {cmp} {{\n{body}{tabs}}}'

    def visit_CompoundExpression(self, node: CompoundExpression):
        insts = ''

        for inst in node.instructions:
            insts += ' ' + self.visit(inst)
            if isinstance(inst, Expression): insts += ';'

        return f'{{{insts} }}'

    # def visit_Argument(self, node: Argument):
    #     return f'{node.name} {node.dtype}'

    # def visit_ReturnStatement(self, node: ReturnStatement):
    #     return f'return {self.visit(node.value)};'

    # def visit_FunctionDefinition(self, node: FunctionDefinition):
    #     params = ''
    #     if node.params:
    #         for a in node.params[:-1]:
    #             params += f'{self.visit(a)}, '
    #         params += f'{self.visit(node.params[-1])}'
    #     interface = f'func {node.name}({params}) {node.typeReturn+" " if node.typeReturn != "unit" else ""}{{'
    #     blockSt = f'{self.visit(node.statements)}'
    #     return f'{interface}\n{blockSt}}}'

    # def visit_FunctionApplication(self, node: FunctionApplication):
    #     args = ''
    #     for a in node.args[:-1]:
    #         args += f'{self.visit(a)}, '
    #     args += f'{self.visit(node.args[-1])}'
    #     return f'{node.name}({args})'

    # def visit_Program(self, node: Program):
    #     strCode = ''
    #     for d in node.declarations[:-1]:
    #         strCode += f'{self.visit(d)}\n\n'
    #     strCode += f'{self.visit(node.declarations[-1])}'
    #     return strCode


def to_source(node):
    return _NodeVisitor().visit(node)