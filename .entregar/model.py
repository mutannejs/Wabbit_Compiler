from typing import Literal


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
        assert len(value) == 2 if value[0] == "\\" else len(value) == 1
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

BoolType = Literal['true', 'false']

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

OpType = Literal['+', '-', '/', '*', '<', '>', '&&', '||']
Operators = ['+', '-', '/', '*', '<', '>', '&&', '||']

class UnOp(Expression):
    '''
    Example: -5
    '''
    def __init__(self, op: OpType, expr: Expression):
        assert op in Operators
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
    def __init__(self, op: OpType, left: Expression, right: Expression):
        assert op in Operators
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

MutType = Literal['var', 'const']
Dtype = Literal['int', 'float', 'bool']

class Declaration(Statement):
    '''
    var c bool = true;
    '''
    def __init__(self, mut: MutType, location: Location, dtype: Dtype = None, value: Expression = None):
        assert mut in ['var', 'const']
        assert isinstance(location, Location)
        if dtype: assert dtype in ['int', 'float', 'bool']
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


class NodeVisitor:
    def __init__(self):
        pass

    def visit(self, node: Node):
        methname = node.__class__.__name__
        return getattr(self, f'visit_{methname}')(node)

    def visit_BlockStatement(self, node: BlockStatement):
        tabs = ''.rjust(node.tabs * 4, ' ')

        sttmts = ''
        for st in node.statements:
            sttmts += tabs + self.visit(st) + '\n'
        return sttmts

    def visit_Integer(self, node: Integer):
        return node.value

    def visit_Float(self, node: Float):
        return node.value

    def visit_Char(self, node: Char):
        return f'\'{node.value}\''

    def visit_Bool(self, node: Char):
        return f'{node.value}'

    def visit_Print(self, node: Print):
        return f'print {self.visit(node.expr)};'

    def visit_UnOp(self, node: UnOp):
        return f'{node.op}{self.visit(node.expr)}'

    def visit_BinOp(self, node: BinOp):
        return f'{self.visit(node.left)} {node.op} {self.visit(node.right)}'

    def visit_Location(self, node: Location):
        return f'{node.name}'

    def visit_Declaration(self, node: Declaration):
        base = f'{node.mut} {self.visit(node.location)}'
        dtype = f' {node.dtype}' if node.dtype != None else ''
        value = f' = {self.visit(node.value)}' if node.value != None else ''
        return base + dtype + value + ';'

    def visit_Assignment(self, node: Assignment):
        return f'{self.visit(node.location)} = {self.visit(node.value)};'

    def visit_IfStatement(self, node: IfStatement):
        block_if = f'if {self.visit(node.cmp)} {{\n{self.visit(node.block_if)}}}'
        block_else = f' else {{\n{self.visit(node.block_else)}}}' if node.block_else else ''
        return block_if + block_else

    def visit_WhileStatement(self, node: WhileStatement):
        return f'while {self.visit(node.cmp)} {{\n{self.visit(node.body)}}}'

    def visit_CompoundExpression(self, node: CompoundExpression):
        insts = ''
        for inst in node.instructions:
            insts += ' ' + self.visit(inst)
        return f'{{{insts}; }}'


def to_source(node):
    return NodeVisitor().visit(node)