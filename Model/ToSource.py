from .Structs import *

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