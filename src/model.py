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
        # assert len(value) == 1
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

class Unit(Expression):
    '''
    Example: ()
    '''
    def __init__(self):
        self.value = '()'

    def __repr__(self):
        return 'Unit()'

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

class BlockStatement(Node):
    '''
    Example: a = 1; a = 2;
    '''
    def __init__(self, statements: list[Statement], tabs: int = 0):
        assert isinstance(statements, list)
        # for sttmt in statements:
        #     assert isinstance(sttmt, Statement) or isinstance(sttmt, CompoundExpression)
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


class _NodeVisitor:
    def __init__(self):
        self.tabs = -1

    def visit(self, node: Node):
        methname = node.__class__.__name__
        return getattr(self, f'visit_{methname}')(node)

    def visit_BlockStatement(self, node: BlockStatement):
        # tabs = ''.rjust(node.tabs * 4, ' ')
        self.tabs += 1
        tabs = ''.rjust(self.tabs * 4, ' ')

        sttmts = ''
        for st in node.statements:
            sttmts += tabs + self.visit(st) + '\n'

        self.tabs -= 1
        return sttmts

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

    def visit_Print(self, node: Print):
        return f'print {self.visit(node.expr)};'

    def visit_UnOp(self, node: UnOp):
        return f'{node.op}{self.visit(node.expr)}'

    def visit_BinOp(self, node: BinOp):
        return f'{self.visit(node.left)} {node.op} {self.visit(node.right)}'

    def visit_Location(self, node: Location):
        return f'{node.name}'

    def visit_DeclarationVar(self, node: DeclarationVar):
        base = f'var {self.visit(node.location)}'
        dtype = f' {node.dtype}' if node.dtype != None else ''
        value = f' = {self.visit(node.value)}' if node.value != None else ''
        return base + dtype + value + ';'

    def visit_DeclarationConst(self, node: DeclarationConst):
        base = f'const {self.visit(node.location)}'
        dtype = f' {node.dtype}' if node.dtype != None else ''
        value = f' = {self.visit(node.value)}' if node.value != None else ''
        return base + dtype + value + ';'

    def visit_Assignment(self, node: Assignment):
        return f'{self.visit(node.location)} = {self.visit(node.value)};'

    def visit_IfStatement(self, node: IfStatement):
        # tabs = ''.rjust(node.tabs * 4, ' ')
        tabs = ''.rjust(self.tabs * 4, ' ')
        block_if = f'if {self.visit(node.cmp)} {{\n{self.visit(node.block_if)}{tabs}}}'
        block_else = f' else {{\n{self.visit(node.block_else)}{tabs}}}' if node.block_else else ''
        return block_if + block_else

    def visit_WhileStatement(self, node: WhileStatement):
        # tabs = ''.rjust(node.tabs * 4, ' ')
        tabs = ''.rjust(self.tabs * 4, ' ')
        cmp = self.visit(node.cmp)
        body = self.visit(node.body)
        return f'while {cmp} {{\n{body}{tabs}}}'

    def visit_CompoundExpression(self, node: CompoundExpression):
        insts = ''
        for inst in node.instructions:
            insts += ' ' + self.visit(inst)
        if isinstance(node.instructions[-1], Expression):
            insts += ';'
        return f'{{{insts} }}'

    def visit_Argument(self, node: Argument):
        return f'{node.name} {node.dtype}'

    def visit_ReturnStatement(self, node: ReturnStatement):
        return f'return {self.visit(node.value)};'

    def visit_FunctionDefinition(self, node: FunctionDefinition):
        params = ''
        if node.params:
            for a in node.params[:-1]:
                params += f'{self.visit(a)}, '
            params += f'{self.visit(node.params[-1])}'
        interface = f'func {node.name}({params}) {node.typeReturn+" " if node.typeReturn != "unit" else ""}{{'
        blockSt = f'{self.visit(node.statements)}'
        return f'{interface}\n{blockSt}}}'

    def visit_FunctionApplication(self, node: FunctionApplication):
        args = ''
        for a in node.args[:-1]:
            args += f'{self.visit(a)}, '
        args += f'{self.visit(node.args[-1])}'
        return f'{node.name}({args})'

    def visit_Program(self, node: Program):
        strCode = ''
        for d in node.declarations[:-1]:
            strCode += f'{self.visit(d)}\n\n'
        strCode += f'{self.visit(node.declarations[-1])}'
        return strCode


def to_source(node):
    return _NodeVisitor().visit(node)